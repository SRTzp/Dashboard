"""E2E1 shared harness: real clicks + the 'no dead button' guard (every click must change the DOM / open-close a sheet / show a message within 1.5 s, and raise no console.error / pageerror / console.warn)."""
import os, json
from re1d_common import js, launch, check, results
import hf5_common as H

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")
SHOTS_ON = bool(os.environ.get("E2E1_SHOTS"))
JOURNEYS = []        # (journey, step, width, ok)
DEAD = []            # (where, label)

INSTALL = """()=>{ if(window.__e2){ return; } window.__e2 = {mut:0, warns:[]};
  new MutationObserver(()=>{ window.__e2.mut++; }).observe(document.documentElement, {subtree:true, childList:true, attributes:true, characterData:true});
  const ow = console.warn; console.warn = function(){ try{ window.__e2.warns.push([].map.call(arguments, x=>String(x && x.message || x)).join(' ').slice(0,200)); }catch(e){} return ow.apply(console, arguments); };
  const oe = console.error; console.error = function(){ try{ window.__e2.warns.push('ERROR ' + [].map.call(arguments, x=>String(x && x.message || x)).join(' ').slice(0,200)); }catch(e){} return oe.apply(console, arguments); };
  window.addEventListener('error', e=>{ window.__e2.warns.push('UNCAUGHT ' + e.message); });
  window.addEventListener('unhandledrejection', e=>{ window.__e2.warns.push('REJECT ' + String(e.reason && e.reason.message || e.reason)); }); }"""
STATE = "()=>({mut:window.__e2.mut, warns:window.__e2.warns.length, ov:document.querySelectorAll('#bdPop,.core-sheet,#closePosOverlay.show,.ui-sheet-backdrop').length, toast:(document.getElementById('sdToast')||{}).innerText||''})"


def start(pw, w, h=None):
    h = h or (900 if w >= 900 else 844)
    b, page, ce, pe = launch(pw, w, h, c={})
    js(page, "()=>{ switchTab('today'); todayRefresh(true); }")
    js(page, "()=>satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','S50','BRENT'])")
    js(page, "()=>{ const s = tdSettings(); s.products = Object.assign({}, s.products || {}, {BRENT:{sys:'lot', perPoint:100, lotStep:0.01, minLot:0.01, cur:'USD'}}); }")
    js(page, "()=>{ window.prompt = (m, d)=>String(d); ['main','fam'].forEach(a=>{ const st = ps1Settings(a); st.psRisk = Object.assign({}, st.psRisk || {}, {minStop:{XAUUSD:0.3, BTCUSD:0.5, S50:0.3, BRENT:0.3}}); }); re1Cache = {}; }")   # seed: min stop set in Settings (a prerequisite, not a journey step)
    js(page, INSTALL)
    page.wait_for_timeout(200)
    return b, page, ce, pe


def click(page, loc, label, where="", wait=1500):
    """Click + the guard. Returns (ok, why). A dead click is recorded in DEAD and fails the check."""
    if isinstance(loc, str): loc = page.locator(loc).first
    s0 = js(page, STATE)
    try:
        loc.click(timeout=4000)
    except Exception as e:
        DEAD.append((where, label + " · not clickable: " + " ".join(str(e).split())[-420:])); return False, "not clickable"
    ok = False; st = s0
    for _ in range(int(wait / 100)):
        page.wait_for_timeout(100)
        st = js(page, STATE)
        if st["mut"] != s0["mut"] or st["ov"] != s0["ov"] or (st["toast"] and st["toast"] != s0["toast"]): ok = True; break
    bad = js(page, "(n)=>window.__e2.warns.slice(n)", s0["warns"]) if st["warns"] != s0["warns"] else []
    if not ok: DEAD.append((where, label))
    if bad: DEAD.append((where, label + " · console: " + "; ".join(bad)[:120]))
    return ok and not bad, "dead" if not ok else ("console: " + "; ".join(bad)[:120] if bad else "")


def step(j, w, name, ok, detail=""):
    JOURNEYS.append((j, name, w, bool(ok)))
    check(f"[{j} {w}] {name}", ok, detail)


def sel_text(page, sel):
    return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)


def new_sat_plan(page, w, j, asset_idx, buy, acct, entry, sl, tp, ema=True, st=True):
    """＋ New plan → Satellite → asset → fill → Save plan, all real clicks. Returns steps ok."""
    ok = True
    ok &= click(page, "#hdrPlanBtn", "＋ New plan", j)[0]
    ok &= click(page, "#bdPop [onclick=\"bdNewPick('F')\"]", "pick Satellite", j)[0]
    ok &= click(page, f"#bdPop [onclick=\"pb2Pick({asset_idx})\"]", "pick asset", j)[0]
    ok &= click(page, f"[data-pb2-dir=\"{'Buy' if buy else 'Sell'}\"]", "Buy/Sell", j)[0]
    ok &= click(page, f"[data-pb2-acct=\"{acct}\"]", "acct", j)[0]
    for k, v in (("entry", entry), ("sl", sl), ("tp", tp)):
        page.locator(f"[data-pb2-in=\"{k}\"]").fill(str(v))
    page.wait_for_timeout(150)
    ok &= click(page, f"[data-pb2-tg=\"ema\"][data-v=\"{1 if ema else 0}\"]", "EMA50", j)[0]
    ok &= click(page, f"[data-pb2-tg=\"str\"][data-v=\"{1 if st else 0}\"]", "Structure", j)[0]
    return ok


def shot(page, name):
    if not SHOTS_ON: return
    os.makedirs(SHOTS, exist_ok=True)
    js(page, "()=>{ const s=document.createElement('style'); s.id='e2shot'; s.textContent='@media (max-width:600px){#tabsMain{display:none!important}}'; document.head.appendChild(s); }")
    page.wait_for_timeout(300)
    page.screenshot(path=os.path.join(SHOTS, "e2e1-%s.png" % name), full_page=False)
    js(page, "()=>{ const s=document.getElementById('e2shot'); if(s) s.remove(); }")


# ---------- Sat real-click steps ----------
def enter_btn(page, sym, grp="enter"):
    return page.locator(f'[data-re2-row="{sym}"][data-re2-grp="{grp}"] button').first


def place_from_today(page, sym, j):
    """Today Enter row → Place › → Confirm. Returns (ok, blockline)."""
    ok = click(page, enter_btn(page, sym), f"{sym} Enter row · Place", j)[0]
    page.wait_for_timeout(250)
    blk = sel_text(page, "[data-hf3-block]")
    dis = js(page, "()=>{ const y=document.querySelector('[data-pb2-yes]'); return y ? y.disabled : null; }")
    if blk or dis:
        return False, blk or "Confirm disabled"
    ok &= click(page, "[data-pb2-yes]", f"{sym} Confirm", j)[0]
    page.wait_for_timeout(300)
    return ok, None


def filled_from_today(page, sym, j):
    ok = click(page, enter_btn(page, sym, "check"), f"{sym} Check row · Filled", j)[0]
    page.wait_for_timeout(300)
    return ok


def manage_row(page, sym):
    return page.locator(f'[data-hf5-row="{sym}"]').first


def set_price(page, sym, px, j):
    ok = click(page, manage_row(page, sym).locator('[data-hf5-btn="price"]'), f"{sym} Price ›", j)[0]
    page.locator("#hf5Px").fill(str(px)); page.wait_for_timeout(150)
    ok &= click(page, "#csSave", f"{sym} Price Save", j)[0]
    return ok


def move_stop_ui(page, sym, v, j):
    ok = click(page, manage_row(page, sym).locator('[data-hf5-btn="stop"]'), f"{sym} Move stop ›", j)[0]
    page.locator("#csStop").fill(str(v)); page.wait_for_timeout(200)
    err = js(page, "()=>{ const e=document.getElementById('csErr'); return e && e.style.display!=='none' ? e.textContent : ''; }")
    dis = js(page, "()=>{ const b=document.getElementById('csSave'); return b ? b.disabled : null; }")
    if err or dis:
        click(page, ".core-sheet button:has-text('Cancel')", "stop Cancel", j); return False, err
    ok &= click(page, "#csSave", f"{sym} Stop Save", j)[0]
    page.wait_for_timeout(300)
    return ok, ""


def close_ui(page, sym, exit_px, j, frac=None):
    ok = click(page, manage_row(page, sym).locator(".l1"), f"{sym} Manage row", j)[0]
    ok &= click(page, "[data-bd-close]", f"{sym} Close trade", j)[0]
    if frac: ok &= click(page, f'#closePosOverlay [onclick="cpSetFraction({frac})"]', f"close {frac}", j)[0]
    page.locator("#cpExitPrice").fill(str(exit_px)); page.wait_for_timeout(150)
    ok &= click(page, "#cpConfirmBtn", f"{sym} Confirm close", j)[0]
    page.wait_for_timeout(500)
    # drawer may still be open after a close: close it
    if js(page, "()=>!!document.querySelector('[data-bd-close]')"):
        js(page, "()=>{ try{ bdDrawerClose(); }catch(e){} }")
    return ok


def goto(page, tab, j):
    return click(page, f'#tabsMain [onclick="switchTab(\'{tab}\')"], [onclick="switchTab(\'{tab}\')"]', f"tab {tab}", j)[0]
