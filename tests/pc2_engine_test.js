/* PC2 — engine selftest: planned rows after a fill (first build) · homework factor per strategy · add-on rules · numeric texts · saved data untouched. Run: node tests/pc2_engine_test.js */
const R = require('../risk-engine.js'), A = require('../re1-adapter.js');
let pass = 0, fail = 0;
function ok(name, cond, d) { if (cond) pass++; else { fail++; console.log('FAIL - ' + name + (d !== undefined ? ' :: ' + JSON.stringify(d).slice(0, 400) : '')); } }
const near = (a, b, e) => Math.abs(a - b) <= (e || 1e-6);
const NOW = Date.parse('2026-11-16T10:00:00+07:00');   // Monday
const bk = d => Date.parse(d + 'T00:00:00+07:00');
// RM1 fixture: fundflow ratios in the SMA 20/50 shape (state + inputs_asof, adjusted)
const FFR = (eq, cr, asof) => { const it = (st, a, b) => ({ tf: 'D', sma: [20, 50], adj: true, state: st, up: st === 'green' ? true : st === 'red' ? false : null, days_in_state: 5, bar: asof, inputs_asof: { [a]: asof, [b]: asof }, sma20: 1, sma50: 1, ratio: 1 }); return { ACWI_BIL: it(eq, 'ACWI', 'BIL'), HYG_IEI: it(cr, 'HYG', 'IEI') }; };
const FF = { as_of: '2026-11-17', ratios: FFR('green', 'red', '2026-11-13') };   // one red → 80% (RM1)
function tr(o) { return Object.assign({ port: 'core', bias: 'Long', mult: 1, cur: 'USD', status: 'open', date: '2026-11-10', qty: 10, entry: 100, sl: 95 }, o); }
function src(over) {
  const snap = { id: 's1', bkkDate: '2026-11-16', equity: 5000000, confirmed: true, kind: 'weekly' };
  const S = (e) => Object.assign({ fx: 35, equitySnapshots: [snap], costSettings: { winner: { perUnit: 0.005, min: 1 }, ladder: { perUnit: 0.005, min: 1 }, sat: { perUnit: 7, swapDay: 3 } }, capital: { core: 5000000, satB: 0 } }, e || {});
  const o = { costsOn: true, now: NOW, accounts: [{ id: 'main', name: 'Main', ports: ['core', 'satB'] }, { id: 'fam', name: 'Family', ports: ['core', 'satB'] }],
    books: { main: { settings: S(), trades: [] }, fam: { settings: S({ equitySnapshots: [{ id: 'f1', bkkDate: '2026-11-09', equity: 10000000, confirmed: true }] }), trades: [] } },
    cards: [], ideas: [], ff: FF, specs: {}, portCur: { core: 'THB', satB: 'USD' }, homework: {}, starterOn: false };
  return Object.assign(o, over || {});
}

const spec = { mult: 1, fx: 35, lotStep: 1, minLot: 1 };
const NVDA = (qty, stop) => { const s = src(); s.books.main.trades = [tr({ id: 'n1', sym: 'NVDA', qty: qty, entry: 100, sl: stop, posGroup: 'n1', sl0: stop })]; s.cards = [{ id: 'cN', acct: 'main', ticker: 'NVDA', market: 'US', strategy: 'L', status: 'open', trade_id: 'n1', lots: [{ n: 1, px: 100, qty: qty }] }]; return s; };
const sNo = JSON.stringify;
// fixture: one regime signal red → Momentum 80%, Compounder 100% (CP1)
{
  const s = NVDA(10, 95), before = sNo(s), L = A.live(s, 'main'), id = L.ideas[0].id;
  // §1 planned row after the first fill: no ADDON_THESIS, sized by plan % × homework (comp 100%) × regime
  const p = A.sizeComp(L, Object.assign({ kind: 'plan', ideaId: id, thesisDone: false, riskPct: 1.0, side: 'long', entry: 90, stop: 85 }, spec));
  ok('planned ② after ① fill, homework NOT done → no ADDON_THESIS', p.reasons.indexOf('ADDON_THESIS') < 0 && !p.blocked, p.reasons);
  ok('planned ② budget = plan 1.00% × homework 100% × regime 100% (CP1: one red = full) = 1.00%', near(p.budget.capPct, 1.0) && /^1% × homework 100% × risk-on 100%$/.test(p.budget.text), p.budget);
  ok('planned ② fits: total = ①'+" at stop + ②"+' ≤ 1.00% (qty cut by room)', p.fit.totalPct <= 1.0 + 1e-9 && p.qty > 0, p.fit);
  // row added after the fill = add-on → thesis required as before
  const a = A.sizeComp(L, Object.assign({ kind: 'addon', ideaId: id, thesisDone: false, riskPct: 1.0, side: 'long', entry: 110, stop: 104 }, spec));
  ok('row added after the fill (add-on) → ADDON_THESIS', a.reasons.indexOf('ADDON_THESIS') >= 0 && a.blocked, a.reasons);
  const a2 = A.sizeComp(L, Object.assign({ kind: 'addon', ideaId: id, thesisDone: true, riskPct: 1.0, side: 'long', entry: 110, stop: 104 }, spec));
  ok('add-on with homework done and stop at 95 (risk of ① 0.07%): fits the plan budget', !a2.blocked && a2.qty > 0 && a2.fit.totalPct <= 1.0 + 1e-9, [a2.reasons, a2.fit]);
  ok('engine run does not touch saved data', sNo(s) === before);
  // over-limit text with numbers
  const big = NVDA(70, 90), LB = A.live(big, 'main'), ib = LB.ideas[0].id;
  const pb = A.sizeComp(LB, Object.assign({ kind: 'plan', ideaId: ib, riskPct: 1.0, side: 'long', entry: 90, stop: 80, thesisDone: false }, spec));
  ok('held ① already 0.49% + row at stop 80 → qty cut to what fits, limited by total risk 1%', pb.limit && pb.limit.code === 'total_risk' && /risk 1%/.test(pb.limit.text), [pb.limit, pb.qty]);
  const huge = NVDA(100, 80), LH = A.live(huge, 'main'), ih = LH.ideas[0].id;
  const ph = A.sizeComp(LH, Object.assign({ kind: 'plan', ideaId: ih, riskPct: 1.0, side: 'long', entry: 90, stop: 80, thesisDone: false }, spec));
  ok('①alone over the limit → block text with numbers', ph.reasons.indexOf('PLAN_TOTAL_RISK') >= 0 && /^Risk \d+(\.\d+)?% is over the limit for this plan 1% \(1% × homework 100% × risk-on 100%\)$/.test(ph.reasonTexts[0]), [ph.reasons, ph.reasonTexts]);
  // add-on risk rule: stop must come up first
  const ad = A.sizeComp(LH, Object.assign({ kind: 'addon', ideaId: ih, thesisDone: true, riskPct: 1.0, side: 'long', entry: 110, stop: 104 }, spec));
  ok('add-on blocked while total risk with the new row is over budget (named numbers)', ad.reasons.indexOf('ADDON_TOTAL_RISK') >= 0 && /^Risk \d+(\.\d+)?% is over the [\d.]+% limit for this stock \(all lots at their current stop\)$/.test(ad.reasonTexts.join()), [ad.reasons, ad.reasonTexts]);
  const up = NVDA(100, 99), LU = A.live(up, 'main'), iu = LU.ideas[0].id;
  const ad2 = A.sizeComp(LU, Object.assign({ kind: 'addon', ideaId: iu, thesisDone: true, riskPct: 1.0, side: 'long', entry: 110, stop: 104 }, spec));
  ok('after the stop moves up (99) the same add-on no longer breaks the total-risk rule', ad2.reasons.indexOf('ADDON_TOTAL_RISK') < 0 && ad2.qty > 0, [ad2.reasons, ad2.fit]);
  // 2d risk per plan
  const r1 = A.sizeComp(L, Object.assign({ kind: 'plan', riskPct: 1.0, side: 'long', entry: 100, stop: 80, thesisDone: true }, spec)), r15 = A.sizeComp(L, Object.assign({ kind: 'plan', riskPct: 1.5, side: 'long', entry: 100, stop: 80, thesisDone: true }, spec));
  ok('plan risk 1.5% sizes ×1.5 vs 1.0%', near(r15.effPct / r1.effPct, 1.5) && r15.qty >= Math.floor(r1.qty * 1.5) - 1, [r1.qty, r15.qty]);
  const vc = A.sizeComp(L, Object.assign({ kind: 'plan', riskPct: 2.0, side: 'long', entry: 100, stop: 99.5, thesisDone: true }, spec));
  ok('value cap 12.5% still limits a tight stop', vc.limit && vc.limit.code === 'value_cap', vc.limit);
  const old = A.sizeComp(L, Object.assign({ kind: 'pilot', side: 'long', entry: 100, stop: 95 }, spec));
  ok('legacy pilot kind unchanged (0.50% × regime; one red = 100% for Compounder, CP1)', near(old.effPct, 0.5));
}
// 2e Momentum
{
  const L = A.live(src(), 'main');
  const n = A.sizeMomentum(L, Object.assign({ homeworkDone: false, side: 'long', entry: 100, stop: 90 }, spec)), d = A.sizeMomentum(L, Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 90 }, spec));
  ok('Momentum not done = 70% of done', near(n.effPct / d.effPct, 0.7) && /homework 70%/.test(n.formula) && n.factors.indexOf('HOMEWORK_70') >= 0, [n.effPct, d.effPct, n.formula]);
  ok('POLICY.hwFactor comp 1.00 / mom 0.70', R.POLICY.hwFactor.comp === 1 && R.POLICY.hwFactor.mom === 0.7);
  const mid = src(); mid.books.main.trades = [tr({ id: 'm1', sym: 'PLTR', qty: 20, entry: 100, sl: 90, posGroup: 'm1', sl0: 90 })]; mid.cards = [{ id: 'cP', acct: 'main', ticker: 'PLTR', market: 'US', strategy: 'M', status: 'open', trade_id: 'm1', lots: [{ n: 1, px: 100, qty: 20 }] }];
  const LM = A.live(mid, 'main'), im = LM.ideas[0].id;
  const add0 = A.sizeMomentum(LM, Object.assign({ homeworkDone: false, isAddition: true, isFirstEntry: false, ideaId: im, side: 'long', entry: 110, stop: 100 }, spec));
  ok('Momentum add-on without homework → ADDON_THESIS', add0.reasons.indexOf('ADDON_THESIS') >= 0 && add0.allowedQty === 0, add0.reasons);
  const add1 = A.sizeMomentum(LM, Object.assign({ homeworkDone: true, isAddition: true, isFirstEntry: false, ideaId: im, side: 'long', entry: 110, stop: 100 }, spec));
  ok('Momentum add-on with homework: total-risk rule (held ① at its stop + new ≤ budget)', add1.fit && add1.fit.totalPct <= add1.fit.capPct + 1e-9 || add1.reasons.indexOf('ADDON_TOTAL_RISK') >= 0, [add1.fit, add1.reasons]);
  const tu = A.sizeMomentum(LM, Object.assign({ homeworkDone: true, topUp: true, isAddition: false, isFirstEntry: false, ideaId: im, side: 'long', entry: 100, stop: 90 }, spec));
  ok('top-up = first build: no ADDON_THESIS, no stop rule, total ≤ full budget', tu.reasons.indexOf('ADDON_THESIS') < 0 && tu.fit && tu.fit.totalPct <= tu.fit.capPct + 1e-9 && tu.fit.capPct > n.effPct, [tu.reasons, tu.fit]);
}
console.log((fail ? 'FAIL ' : 'PASS ') + pass + '/' + (pass + fail) + ' PC2 engine assertions'); process.exit(fail ? 1 : 0);
