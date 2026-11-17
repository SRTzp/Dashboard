#!/usr/bin/env node
// RV1 A — run the APP's own RRG code (extracted from index.html, not re-typed) on a cases file.
//   node tools/rrg_app_run.js cases.json > app.json
// cases: [{id, sym, ref, etf:[{datetime,close,high?}…newest first], bench:[…]}]  (Twelve Data time_series shape)
// Uses: rrgWeekKey … rrgCompute (one block), rrgSeries, rrgBuildRows — exactly the functions the browser runs.
const fs = require('fs'), vm = require('vm'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
function block(from, to) { const a = src.indexOf(from), b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error('marker not found: ' + from); return src.slice(a, b); }
function fn(name) {   // whole top-level function by brace matching
  const a = src.indexOf('\nfunction ' + name + '(') + 1; if (a < 1) throw new Error('no function ' + name);
  let i = src.indexOf('{', a), d = 0;
  for (; i < src.length; i++) { if (src[i] === '{') d++; else if (src[i] === '}' && --d === 0) break; }
  return src.slice(a, i + 1);
}
const code = block('const RRG_BUILD', '/* ---------- ดึงราคาจาก Twelve Data') + '\n' + fn('rrgSeries') + '\n' + fn('rrgBuildRows') + '\nlet REF = null; function rrgToday(){ return REF; }\n';
const ctx = vm.createContext({ Math, Date, Map, Array, Object, console });
vm.runInContext(code + '\nthis.__api = {RRG_SYMS, RRG_BENCH, RRG_CFG, RRG_K, RRG_HYST, RRG_MODEL, rrgSeries, rrgBuildRows, rrgCompute, rrgToWeekly, setRef:(r)=>{REF=r;}};', ctx);
const A = ctx.__api;
if (require.main === module) {
  const cases = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')), out = {};
  for (const c of cases) {
    A.setRef(c.ref);
    const r = A.rrgBuildRows({ s: c.sym, n: c.sym }, { [c.sym]: c.etf }, A.rrgSeries(c.bench));
    out[c.id] = JSON.parse(JSON.stringify(r));
  }
  process.stdout.write(JSON.stringify({ meta: { K: A.RRG_K, hyst: A.RRG_HYST, model: A.RRG_MODEL, fast: A.RRG_CFG.fast, slow: A.RRG_CFG.slow, syms: A.RRG_SYMS.map(x => x.s) }, rows: out }));
}
module.exports = A;
