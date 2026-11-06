"""RRG1 — legacy-shaped test rows (quad/ratio/mom/dMom/rsTrend only) -> model-2 rows (adds model, eps, delta, rawChg, rel, momUp).
rel/sign follow the quad key; lets older fixtures keep their intent under the new state model."""
MODELIZE_JS = """(rows)=>(rows||[]).map(x=>{ if(!x || x.err || x.model===2) return x; const o = Object.assign({}, x);
  const pos = (x.quad==='lead'||x.quad==='weak'), up = (x.quad==='lead'||x.quad==='imp');
  o.model = 2; o.eps = 0.02; o.delta = 0.01;
  o.rsTrend = x.quad==='flat' ? 0 : (pos ? Math.abs(x.rsTrend||0.5)+0.1 : -(Math.abs(x.rsTrend||0.5)+0.1));
  o.rawChg = x.rawChg!=null ? x.rawChg : (up ? 0.05 : -0.05);
  o.rel = x.quad==='flat' ? 'neu' : (pos ? 'pos' : 'neg'); o.momUp = up; o.lag = 5; o.bars = o.bars||300; o.close = o.close||100; o.benchClose = o.benchClose||100;
  o.lastObs = o.lastObs || x.date; return o; })"""
