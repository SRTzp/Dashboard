#!/usr/bin/env python3
"""LR4 — shared fixture for the Flow tab: Weekly Impact (5 events Mon–Fri · 4 assets) + RRG rows with 5-bar tails (mockup positions) + regime red/red + no playbook."""
import re, os, json
import net_stub
import re1d_common as K
from re1d_common import js, launch

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, "..", "docs", "briefs", "lr")


def mock_sectors():
    """Read the 16 sector tails out of Flow.dc.html (SVG pixel space 560×380) → ratio / mom rows (centre 240,237 = 100/100, ±3)."""
    h = open(os.path.join(MOCK, "Flow.dc.html"), encoding="utf-8").read()
    polys = re.findall(r'<polyline points="([^"]+)" fill="none" stroke="(#[0-9A-Fa-f]{6})"', h)
    names = ["XLC", "ITA", "XLI", "XLU", "XLV", "XLY", "XLP", "XLF", "XRT", "SMH", "XLE", "IGV", "HACK", "ROBO", "ARKX", "XLK"]
    quad = {"#12805C": "lead", "#B7791F": "weak", "#2F5BD3": "imp", "#C2362F": "lag"}
    spd = {"XLC": 0.8, "SMH": 0.8, "XLK": -0.8, "IGV": -0.8, "XLE": 0.2}
    days = {"XLC": 3, "ITA": 11, "XLI": 11, "SMH": 4, "XLE": 1, "XLK": 12, "IGV": 10}
    rows = []
    for n, (pts, col) in zip(names, polys):
        p = [tuple(map(float, a.split(","))) for a in pts.split()]
        tail = [[100 + (x - 240) / 240 * 3, 100 - (y - 237) / 237 * 3] for x, y in p]
        rows.append({"sym": n, "name": n, "quad": quad[col], "ratio": tail[-1][0], "mom": tail[-1][1], "tail": tail, "dMom": spd.get(n, 0.1 if quad[col] != "lag" else -0.1),
                     "days": days.get(n, 5), "prevDays": 3, "err": None})
    return rows


FIX_JS = """([rows])=>{
  serverConfirmed = true; stateFromServer = true;
  const mon = wiCurMon(), D = n=>Calc.wiAddDays(mon, n), at = (n, hm)=>D(n) + 'T' + hm + ':00+07:00';
  const ev = (title, n, hm, kind)=>({title, label_th:title, scheduled_at: at(n, hm), time_status:'confirmed', status:'scheduled', kind:kind || 'other'});
  const doc = {id: mon, week: mon, events:{eia:ev('EIA crude', 2, '21:30'), cpi:ev('US CPI', 3, '20:30', 'cpi'), jc:ev('Jobless claims', 3, '20:30'), fed:ev('Fed speaker', 4, '02:00'), rs:ev('Retail sales', 4, '20:30')},
    assets:{XAUUSD:{impact:'HIGH', event_refs:['cpi','fed'], note:'Real yields + dollar drive gold · CPI Thu'}, BTCUSD:{impact:'MED', event_refs:['cpi'], note:'ETF flows mixed · credit risk-off'}, S50:{impact:'LOW', event_refs:['rs','jc']}, GO:{impact:'MED', event_refs:['eia'], note:'Crude inventories Wed'}}};
  try{ wiStop(); }catch(e){}   /* keep the fixture: no snapshot listener refills wiDocs */
  wiDocs = {}; wiDocs[mon] = doc; wiLoaded = true; wiErr = '';
  if(!window.__bdBias){ window.__bdBias = bdBias; window.__pk = satWeekPickList; }
  satWeekPickList = ()=>['XAUUSD','BTCUSD','S50','GO'];
  bdBias = k=>k === 'XAUUSD' || k === 'GO' ? {k:'bull', t:'Bull'} : k === 'BTCUSD' ? {k:'bear', t:'Bear'} : {k:'neu', t:'Neutral'};
  const mk = r=>Object.assign({model:RRG_MODEL}, r);
  const f = ffState(); f.rrg = {rowsD: rows.map(mk), rowsW: rows.map(mk), build:RRG_BUILD, model:RRG_MODEL, lastBar:rrgToday(), day:rrgToday()};
  const d = new Date().toISOString().slice(0, 10), st = (s, n)=>({tf:'D', sma:[20,50], adj:true, state:s, up:s==='green', days_in_state:n, inputs_asof:{a:d, b:d}, sma20:1.2, sma50:1.1});
  ffJson = {as_of: d, ratios:{ACWI_BIL: st('red', 32), HYG_IEI: st('red', 24)}}; re1Cache = {};
  try{ pbLoaded = true; pbErr = ''; pbList = []; pbRender(); }catch(e){}
  switchTab('flow'); bdFlowTopRender();
}"""


def seed(page, rows=None):
    js(page, FIX_JS, [rows if rows is not None else mock_sectors()])
    page.wait_for_timeout(500)


CLK25 = "2025-11-19T12:00:00+07:00"   # Wed 19 Nov 2025 noon (ICT) = the mockup week 17–21 Nov


def open_flow(pw, w, h, rows=None, iso=CLK25):
    import lib_phase39 as P39, re1c_common as R1
    b, ctx, page, ce, pe, dl = P39.launch(pw, w, h, doc=R1.doc_c(), cards=R1.cards(), clean=True, iso=iso)
    page.add_style_tag(content=K.NOANIM); page.wait_for_timeout(400)
    seed(page, rows)
    return b, page, pe
