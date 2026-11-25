"""HF5 shared helpers: build Sat setups (XAUUSD / BTCUSD / S50 / BRENT), place + fill them, move stops (the same code the buttons call)."""
import os
from re1d_common import js, launch, check, results
import run_tests_lrf as LF

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")

# asset → (entry, long stop, long tp, short stop, short tp)
LV = {"XAUUSD": (2643, 2620, 2700, 2660, 2600), "BTCUSD": (90000, 88500, 94000, 91500, 86000), "S50": (800, 790, 830, 810, 770), "BRENT": (80, 78, 85, 82, 75)}

MK = """(o)=>{ sat7dWrite('satIdeas',o.id,Object.assign({v3:true,v2:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],ema50_ok:true,structure_ok:true,ready:true,readyAt:new Date().toISOString()}, o));
  (satIdeasList||[]).forEach(i=>{ if(i && i.id===o.id) Object.assign(i,o); }); re1Cache = {}; re2GrpAll = {enter:true, check:true, manage:true}; window.ps1MinStopMsg = ()=>''; try{ bdRender(); }catch(e){} todayRefresh(true); }"""


def start(pw, w=1440, h=900):
    b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
    js(page, "()=>{ window.prompt = (m, d)=>String(d); }")   # the fill price prompt: the planned entry
    LF.today(page)
    js(page, "()=>{ const s = tdSettings(); s.products = Object.assign({}, s.products || {}, {BRENT:{sys:'lot', perPoint:100, lotStep:0.01, minLot:0.01, cur:'USD'}}); }")   # BRENT needs a spec to be sized
    js(page, "()=>satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','S50','BRENT'])")
    return b, page, ce, pe


def mk(page, id, asset, bias="Short", **kw):
    e, ls, lt, ss, st = LV[asset]
    o = {"id": id, "asset": asset, "pb_acct": "main", "pb2": True, "bias": bias, "entry": e, "sl": ls if bias == "Long" else ss, "tp": lt if bias == "Long" else st}
    o.update(kw)
    js(page, MK, o); page.wait_for_timeout(250)


def place(page, id):
    """Place order the way the sheet does. Returns the sheet state (block line or None)."""
    js(page, "(id)=>{ window.__pb = null; pb2PlaceOpen(id); }", id); page.wait_for_timeout(300)
    st = js(page, "()=>{ const l = document.querySelector('[data-hf3-block]'); const y = document.querySelector('[data-pb2-yes]'); return {open: !!document.getElementById('bdPop'), line: l ? l.innerText.replace(/\\s+/g,' ').trim() : null, dis: y ? y.disabled : null}; }")
    if st["open"] and not st["line"]:
        js(page, "()=>pb2PlaceYes()"); page.wait_for_timeout(500)
        st["placed"] = js(page, "(id)=>!!(sat7dIdea(id).ln4 && sat7dIdea(id).ln4.placedAt)", id)
    return st


def fill(page, id):
    js(page, "(id)=>{ pb2Filled(id); }", id); page.wait_for_timeout(500)
    return js(page, "(id)=>{ const i=sat7dIdea(id); const a=pb2AcctOf(i); const t=(getBook(a).trades||[]).filter(x=>x.id===((i.accts||{})[a]||{}).trade_id)[0]; return t?{status:t.status,sl:t.sl,sl0:t.sl0,qty:t.qty,entry:t.entry}:null; }", id)


def move_stop(page, id, ns):
    """Move stop exactly like the sheet: open it, type, Save."""
    js(page, "(id)=>re1SatStopOpen(id)", id); page.wait_for_timeout(250)
    js(page, "(v)=>{ const el=document.getElementById('csStop'); el.value=String(v); re1SatStopIn(); }", ns); page.wait_for_timeout(150)
    err = js(page, "()=>{ const e=document.getElementById('csErr'); return e && e.style.display!=='none' ? e.textContent : ''; }")
    if err:
        js(page, "()=>coreSheetClose()"); return err
    js(page, "()=>re1SatStopSave()"); page.wait_for_timeout(400)
    return ""


def queue(page, id):
    """The engine queue verdict for a (planned) idea: reasons + message."""
    return js(page, "(id)=>{ const i=sat7dIdea(id), c=pb2Calc(i,pb2AcctOf(i)); const m=c.c&&c.c.re1; return {reasons:(m&&m.reasons||[]).filter(x=>/QUEUE/.test(x)), text:(m&&m.reasonTexts||[]).filter(x=>/open with|working|setups open/.test(x))[0]||null}; }", id)


def shot(page, name):
    os.makedirs(SHOTS, exist_ok=True)
    page.screenshot(path=os.path.join(SHOTS, "hf5-%s.png" % name))
