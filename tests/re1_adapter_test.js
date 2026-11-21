// RE-B — adapter unit tests (fixtures: two accounts, partial exits, legacy ladder card, missing costs, date-only exits). Run: node tests/re1_adapter_test.js
const R = require('../risk-engine.js'), A = require('../re1-adapter.js'); let f = 0, n = 0;
const ok = (c, m) => { n++; if (!c) { f++; console.log('FAIL', m); } };
const eq = (a, b, m) => ok(a === b, m + ' got ' + JSON.stringify(a) + ' want ' + JSON.stringify(b));
const near = (a, b, m, e = 1e-6) => ok(typeof a === 'number' && Math.abs(a - b) < e, m + ' got ' + a + ' want ' + b);
const T = s => Date.parse(s + '+07:00'), NOW = T('2026-11-18T10:00:00');
// RM1 fixture: fundflow ratios in the SMA 20/50 shape (state + inputs_asof, adjusted)
const FFR = (eq, cr, asof) => { const it = (st, a, b) => ({ tf: 'D', sma: [20, 50], adj: true, state: st, up: st === 'green' ? true : st === 'red' ? false : null, days_in_state: 5, bar: asof, inputs_asof: { [a]: asof, [b]: asof }, sma20: 1, sma50: 1, ratio: 1 }); return { ACWI_BIL: it(eq, 'ACWI', 'BIL'), HYG_IEI: it(cr, 'HYG', 'IEI') }; };
const iso = s => new Date(T(s)).toISOString();

const tr = (o) => Object.assign({ port: 'core', bias: 'Long', mult: 1, cur: 'THB', status: 'open', date: '2026-11-02', qty: 100, entry: 100, sl: 95, tp: null }, o);
const main = {
  settings: { fx: 35, capital: { core: 1000000, satB: 0 }, psRisk: { minStop: {} } },
  trades: [
    // Momentum AAPL (US, USD): partial exit leg (closedAt known) + remaining open; initial stop in card history
    tr({ id: 'm1', sym: 'AAPL', cur: 'USD', qty: 6, entry: 200, sl: 195, posGroup: 'm1', sl0: 190 }),
    tr({ id: 'm1x', sym: 'AAPL', cur: 'USD', qty: 4, entry: 200, sl: 190, status: 'closed', exitPrice: 210, exitDate: '2026-11-17', closedAt: iso('2026-11-17T11:00:00'), posGroup: 'm1', sl0: 190 }),
    // date-only exit loser this week (no closedAt) Momentum without card, THB .BK
    tr({ id: 'm2', sym: 'PTT.BK', qty: 1000, entry: 36, sl: 35, status: 'closed', exitPrice: 35, exitDate: '2026-11-17' }),
    // exact breakeven-ish gross win under old rounding: P&L +0.3
    tr({ id: 'b1', sym: 'ZZZ.BK', qty: 3, entry: 10, sl: 9, status: 'closed', exitPrice: 10.1, exitDate: '2026-11-10', closedAt: iso('2026-11-10T10:00:00') }),
    // Compounder legacy: 3 base lots + accelerator
    tr({ id: 'l1', sym: 'MSFT', cur: 'USD', qty: 5, entry: 400, sl: 380, posGroup: 'l1', sl0: 380 }),
    tr({ id: 'l1a', sym: 'MSFT', cur: 'USD', qty: 5, entry: 390, sl: 380, posGroup: 'l1', acc: true, accOf: 'l1', sl0: 380 }),
    tr({ id: 'l1b', sym: 'MSFT', cur: 'USD', qty: 5, entry: 380, sl: 380, posGroup: 'l1', sl0: 380 }),
    // Satellite: ordered plan trade + closed loser this week
    tr({ id: 's1', sym: 'XAUUSD', port: 'satB', cur: 'USD', mult: 100, qty: 0.1, entry: 2000, sl: 1990, status: 'plan' }),
    tr({ id: 's0', sym: 'BTCUSD', port: 'satB', cur: 'USD', mult: 1, qty: 0.5, entry: 60000, sl: 59000, status: 'closed', exitPrice: 59000, exitDate: '2026-11-16', closedAt: iso('2026-11-16T12:00:00') }),
    // USD position without fx would be excluded in an account that has no fx: (see fam)
  ]
};
const fam = { settings: { capital: { core: 200000 } }, trades: [tr({ id: 'f1', sym: 'US1', cur: 'USD', qty: 10, entry: 50, sl: 45 }), tr({ id: 'f2', sym: 'PTT.BK', qty: 200, entry: 36, sl: 35 })] };
const cards = [
  { id: 'cA', acct: 'main', ticker: 'AAPL', market: 'US', strategy: 'W', status: 'open', trade_id: 'm1', stopHistory: [{ date: '2026-11-05', from: 190, to: 195 }], lots: [{ n: 1, px: 200, qty: 10 }], plan: { entry: 200, stop: 190 } },
  { id: 'cL', acct: 'main', ticker: 'MSFT', market: 'US', strategy: 'L', status: 'open', trade_id: 'l1', acc_trade_id: 'l1a', stopHistory: [], lots: [{ n: 1, px: 400, qty: 5 }, { n: 2, px: 390, qty: 5, layer: 'acc' }, { n: 3, px: 380, qty: 5 }] },
  { id: 'cP', acct: 'main', ticker: 'NVDA', market: 'US', strategy: 'W', status: 'plan', plan: { entry: 120, stop: 110, ps1: { rows: [{ px: 120, qty: 50 }] } }, ln4: { placedLv: { 0: iso('2026-11-17T09:00:00') } } },
  { id: 'cF', acct: 'fam', ticker: 'US1', market: 'US', strategy: 'W', status: 'open', trade_id: 'f1', stopHistory: [], lots: [{ n: 1, px: 50, qty: 10 }] }
];
const ideas = [{ id: 'iX', asset: 'XAUUSD', bias: 'Long', entry: 2000, sl: 1990, tp: 2020, status: 'active', accts: { main: { trade_id: 's1', lot: 0.1 } }, ln4: { placedAt: iso('2026-11-16T09:00:00') } }];
const specs = { XAUUSD: { contract: 100, lotStep: 0.01, minLot: 0.01, cur: 'USD', sys: 'lot' } };
const src = { now: NOW, accounts: [{ id: 'main', name: 'Main', ports: ['core', 'satB'] }, { id: 'fam', name: 'Family', ports: ['core'] }], books: { main, fam }, cards, ideas, specs,
  ff: { as_of: '2026-11-17', ratios: FFR('green', 'red', '2026-11-16') }, portCur: { core: 'THB', satB: 'USD' }, homework: { AAPL: true, MSFT: true, NVDA: false } };
const before = JSON.stringify(src);
const rp = A.build(src);
eq(JSON.stringify(src), before, 'adapter never mutates its input');
const M = rp.accounts.find(a => a.id === 'main'), F = rp.accounts.find(a => a.id === 'fam');
ok(M && F, 'both accounts reported separately');

// accounts never mix
ok(M.positions.every(p => p.id !== 'c:cF') && F.positions.every(p => !/AAPL|MSFT|XAU/.test(p.sym)), 'positions are not mixed across accounts');
eq(F.counts.tradeRows, 2, 'Family has its own 2 rows'); ok(M.counts.tradeRows >= 8, 'Main has its own rows');
// fam has no fx in settings → USD position excluded + FX missing, never 0
ok(F.excluded.some(x => x.why === 'FX'), 'USD position with no FX is excluded'); ok(F.missing.some(m => m.code === 'FX'), 'FX listed as missing');
ok(F.positions.every(p => p.sym !== 'US1'), 'excluded position not in engine rows');

// partial exit: remaining + exited tranche qty
const aapl = M.positions.find(p => p.sym === 'AAPL');
ok(aapl && aapl.status === 'holding', 'AAPL holding'); eq(aapl.old.qtyHeldNow, 6, 'partial exit leaves 6'); eq(aapl.old.qtyAsEntered, 10, 'original size 10 = 6 open + 4 exited');
eq(aapl.old.initialStop, 190, 'initial stop from sl0'); near(aapl.old.principalRiskAtCurrentStop, 6 * 5 * 35, 'risk at current stop in THB (fx 35)'); near(aapl.old.riskAtInitialStop, 10 * 10 * 35, 'risk at initial stop for the whole idea');
eq(aapl.costUnknown, true, 'costs missing → costUnknown'); eq(aapl.projectedNet, null, 'projected net is Unknown (null), not 0');
// engine size fields
ok(aapl.engine.rptPct === 0.40 && aapl.engine.qty > 0, 'Momentum engine RPT 0.40% and a quantity'); ok(aapl.whyDifferent.includes('EQUITY_PROXY'), 'difference list says equity is a proxy');
eq(M.equity.basisKind.startsWith('PROXY'), true, 'no snapshots → proxy basis flagged'); ok(M.missing.some(m => m.code === 'EQUITY_SNAPSHOT'), 'missing snapshot listed'); eq(M.emergency.state, 'n/a', 'Emergency not evaluable without snapshots');
near(M.equity.proxyEquity, 1000000, 'proxy equity = entered capital');

// missing fields: costs, confirmed stop, date-only, initial stop, exit reason
const codes = new Set(M.missing.map(m => m.code));
['COSTS', 'CONFIRMED_STOP', 'CLOSE_TIME_DATE_ONLY', 'EXIT_REASON', 'EQUITY_SNAPSHOT'].forEach(c => ok(codes.has(c), 'missing list has ' + c));
ok(M.missing.find(m => m.code === 'CLOSE_TIME_DATE_ONLY').count >= 1, 'date-only exits counted');

// date-only exit is attributed to 12:00 Bangkok → inside this week for 2026-11-17, Momentum loser counted
eq(M.momentum.completedLossesThisWeek, 1, 'date-only exit loser (PTT.BK) counted this week'); near(M.momentum.weekGrossLoss, 1000, 'its gross loss is 1,000 THB (costs not recorded)', 1e-6);
// reservations: AAPL holding (stop 195 below entry 200) + NVDA working order + MSFT holding = reserved ideas
ok(M.momentum.reservedIdeas >= 2, 'Momentum reservations counted: ' + M.momentum.reservedIdeas); eq(M.momentum.ammoMax, 4, 'ammo max 4');

// Compounder legacy shape + heat
eq(M.compounder.legacyShapeCards.length, 1, 'one legacy-shape Compounder card'); ok(M.compounder.legacyShapeCards[0].why.includes('ACCELERATOR_LOTS') && M.compounder.legacyShapeCards[0].why.includes('TRANCHES_GT_2'), 'legacy reasons: accelerator + >2 tranches');
ok(M.compounder.heatMoney > 0, 'legacy card lots count to heat at actual remaining risk'); near(M.compounder.heatPctWeekStart, M.compounder.heatMoney / 1000000 * 100, 'heat pct on week-start equity'); ok(M.compounder.heatPctCurrent != null, 'heat also shown vs current equity');
ok(M.positions.find(p => p.sym === 'MSFT').legacyShape, 'position row flagged ⚑ legacy');
near(M.compounder.regimeFactor, 0.8, 'regime one red = 80% (RM1 table 100/80/80/60)'); eq(M.compounder.regimeFresh, true, 'regime fresh (oldest input 1 day old)'); eq(rp.regime.signals.hyg, 'red', 'SMA 20/50 state used');
eq(A.build(Object.assign({}, src, { ff: { as_of: '2026-11-17', ratios: FFR('green', 'red', '2026-11-10') } })).regime.fresh, false, 'as-of 8 days old = stale'); eq(A.build(Object.assign({}, src, { ff: {} })).regime.fresh, false, 'no fundflow = not fresh');

// Satellite from history: ordered XAU in queue, BTC loser this week → Step 2; costs unknown
eq(M.satellite.step, 2, 'Satellite Step 2 after one loss this week'); eq(M.satellite.queue.length, 1, 'queue has the ordered XAUUSD setup'); eq(M.satellite.queue[0].status, 'ordered', 'status ordered');
const xau = M.positions.find(p => p.sym === 'XAUUSD'); ok(xau && xau.status === 'ordered', 'ordered Sat order listed'); eq(xau.engine.variants.length, 2, 'Satellite shows 100% and 65% variants (Condition unknown)'); near(xau.engine.variants[1].rptPct, 0.2 * 0.65, 'Step 2 (fixed 0.20) × 65%');
near(xau.old.workingOrderRisk, 0.1 * 10 * 100 * 35, 'working order risk in THB');

// would-be-blocked: NVDA planned/ordered momentum order evaluated; Sat none blocked unless limits
ok(Array.isArray(M.wouldBeBlocked), 'blocked list present'); ok(M.wouldBeBlocked.every(b => b.reasons.length > 0), 'every blocked row has reason codes');

// strict sign badges: 0.3 gross win was BE under old rounding
ok(M.journalBadges.changed >= 1 && M.journalBadges.list.some(b => b.id === 'b1' && b.old === 'be' && b.strict === 'win'), 'journal badge changes: 0.3 profit was BE, now win');
eq(F.journalBadges.changed, 0, 'Family badges unaffected (own trades)');

// markdown + json
const md = A.toMarkdown(rp), js = A.toJson(rp); ok(/Read-only/.test(md) && /Account: Main/.test(md) && /Account: Family/.test(md), 'markdown has both accounts'); ok(/Unknown/.test(md), 'markdown shows Unknown'); ok(!/NaN|Infinity|undefined/.test(md), 'markdown has no NaN / Infinity / undefined');
ok(JSON.parse(js).accounts.length === 2, 'json parses'); ok(!/NaN|Infinity/.test(js), 'json has no NaN');

// real snapshots win over the proxy
const withSnap = JSON.parse(JSON.stringify(src)); withSnap.books.main.settings.equitySnapshots = [{ at: T('2026-11-16T08:00:00'), equity: 2000000, confirmed: true }];
const r2 = A.build(withSnap).accounts[0]; eq(r2.equity.basisKind, 'confirmed snapshots', 'confirmed snapshots used when present'); near(r2.equity.weekEquity, 2000000, 'week equity from snapshot');
// stale snapshot blocks
const stale = JSON.parse(JSON.stringify(src)); stale.books.main.settings.equitySnapshots = [{ at: T('2026-10-01T08:00:00'), equity: 2000000, confirmed: true }];
const r3 = A.build(stale).accounts[0]; ok(r3.equity.reasons.includes('SNAPSHOT_STALE'), 'stale snapshot reported'); ok(r3.wouldBeBlocked.every(b => b.reasons.includes('SNAPSHOT_STALE')), 'everything is blocked with the stale reason');

console.log((f ? 'FAIL ' : 'PASS ') + (n - f) + '/' + n + ' adapter assertions'); process.exit(f ? 1 : 0);
