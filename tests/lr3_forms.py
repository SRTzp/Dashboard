"""LR3 part C — plan forms (Core new / edit, Satellite): English UI (no Thai outside user content), field order, footer handlers, sticky footer on phone."""
import os, re
from re1d_common import js, check, launch
import pv1_common as PV

SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
def sp(t): return re.sub(r"\s+", " ", t or "").strip()

# Thai letters only — the baht sign (U+0E3F) is a currency symbol, not Thai text
SCAN = """(sel)=>{ const root=document.querySelector(sel); if(!root) return null; const th=/[\\u0E00-\\u0E3E\\u0E40-\\u0E7F]/, out=[];
  const user = e=>!!(e.closest && e.closest('[data-user-content],textarea,datalist,option[data-user]'));
  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT); let n; while(n=w.nextNode()){ const p=n.parentElement; if(th.test(n.nodeValue) && p && !['SCRIPT','STYLE'].includes(p.tagName) && !user(p)) out.push(p.tagName+'#'+(p.id||'')+'.'+(p.className||'')+': '+n.nodeValue.trim().slice(0,70)); }
  root.querySelectorAll('*').forEach(e=>['placeholder','title','aria-label'].forEach(a=>{ const v=e.getAttribute(a); if(v && th.test(v)) out.push(a+' '+e.tagName+'#'+(e.id||'')+': '+v.slice(0,70)); }));
  return out; }"""

CORE_STATES = [
    ("Momentum new", "()=>{ planScope='stock'; coreNewOpen('main'); }"),
    ("Compounder new", "()=>{ planScope='ladder'; coreNewOpen('main'); }"),
    ("Momentum edit", "()=>{ planScope='stock'; coreNewOpen('main',{id:'mN',mode:'editw'}); }"),
]


def thai(page, sel): return js(page, SCAN, sel) or []


def partC(page, tag, w):
    js(page, "()=>{ serverConfirmed = true; stateFromServer = true; if(acctActive !== 'main') acctSwitch('main'); switchTab('plan'); bdRender(); }"); page.wait_for_timeout(300)
    for name, code in CORE_STATES:
        js(page, "()=>{ try{ coreSheetClose(); }catch(e){} }"); js(page, code); page.wait_for_timeout(500)
        # drive the validation states too: type a ticker / bad numbers so every error line is rendered
        js(page, "()=>{ const t=document.getElementById('cnTicker'); if(t && !t.readOnly){ t.value='AAPL'; } const e=document.getElementById('cnEntry'); if(e && !e.value){ e.value='90'; } const s=document.getElementById('cnStop'); if(s && !s.value){ s.value='95'; } coreNewIn(); }"); page.wait_for_timeout(300)
        th = thai(page, ".core-sheet")
        check(f"{tag} C: Core form '{name}' has no Thai UI strings", not th, th[:8])
    # validation / market-mismatch states (error lines, 'Show other accounts')
    for name, body in (("TH ticker on Main", "t.value='BBB.BK'"), ("empty entry / stop", "t.value='AAPL'; document.getElementById('cnEntry').value=''; document.getElementById('cnStop').value=''"), ("entry below stop", "t.value='AAPL'; document.getElementById('cnEntry').value='80'; document.getElementById('cnStop').value='90'"), ("existing ticker", "t.value='NVDA'")):
        js(page, "()=>{ try{ coreSheetClose(); }catch(e){} planScope='stock'; coreNewOpen('main'); }"); page.wait_for_timeout(400)
        js(page, "()=>{ const t=document.getElementById('cnTicker'); %s; coreNewIn(); try{ lrTickerMkt(); }catch(e){} coreNewIn(); }" % body); page.wait_for_timeout(300)
        th = thai(page, ".core-sheet")
        check(f"{tag} C: Core form '{name}' state has no Thai UI strings", not th, th[:8])
    js(page, "()=>{ try{ coreSheetClose(); }catch(e){} planScope='stock'; coreNewOpen('main'); }"); page.wait_for_timeout(500)
    r = js(page, """()=>{ const q = s=>document.querySelector('.core-sheet '+s), t = e=>e ? e.getBoundingClientRect().top : null;
      const sv = q('[data-cn-save]'), dr = q('[data-cn-draft]'), ca = q('[data-lf-cancel]');
      return {order: ['#cnAcctBox','#cnTicker','#cnEntry','#cnStop','[data-pv-tgt]','[data-ps1-details]'].map(s=>t(q(s))), save: sv && [sv.innerText, sv.getAttribute('onclick')], draft: dr && [dr.innerText, dr.getAttribute('onclick')], cancel: ca && [ca.innerText, ca.getAttribute('onclick')],
        pos: [ca, dr, sv].map(e=>e ? Math.round(e.getBoundingClientRect().left) : null), lbl: [...document.querySelectorAll('.core-sheet .ps1Ht, .core-sheet .ccF>label')].slice(0,4).map(e=>e.innerText)}; }""")
    ord_ = r["order"]
    check(f"{tag} C: Core field order: Account · Ticker · Entry · SL · Targets · Details", all(x is not None for x in ord_) and ord_ == sorted(ord_), ord_)
    check(f"{tag} C: footer Cancel · Save draft · Save plan keep their handlers", r["cancel"] and r["cancel"][0] == "Cancel" and "coreSheetClose" in r["cancel"][1] and r["draft"] and r["draft"][0] == "Save draft" and "bdDraftSave" in r["draft"][1] and r["save"] and r["save"][0] == "Save plan" and "coreNewSave" in r["save"][1] and r["pos"] == sorted(r["pos"]), r)
    if w < 600:
        s = js(page, """()=>{ const f = document.querySelector('.core-sheet .lf-btnrow'), b = document.querySelector('.core-sheet [data-cn-save]'); const r = b.getBoundingClientRect(); return {pos: getComputedStyle(f).position, h: Math.round(r.height), vis: r.bottom <= innerHeight + 1 && r.top >= 0}; }""")
        check(f"{tag} C: Core form 390 — sticky footer, Save plan visible, buttons ≥ 44 px", s["pos"] == "sticky" and s["vis"] and s["h"] >= 44, s)
        page.screenshot(path=os.path.join(SHOTS, "lr3-form-core-390.png"))
    ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
    check(f"{tag} C: Core form no overflow", ov <= 0, ov)
    # labels above inputs (not beside)
    lb = js(page, "()=>{ const l = document.querySelector('.core-sheet #cnAcctBox').closest('.ccF').querySelector('label'), i = document.querySelector('.core-sheet #cnTicker'); return [l.getBoundingClientRect().bottom <= i.getBoundingClientRect().top + 2]; }")
    check(f"{tag} C: labels sit above inputs", lb[0], lb)
    js(page, "()=>{ try{ coreSheetClose(); }catch(e){} }")


def run_sat(pw, w, h, tag):
    b, page, ce, pe = launch(pw, w, h, d=PV.doc_sat(), c=PV.cards_pv())
    try:
        js(page, PV.SAT_JS); js(page, PV.SAT_PLANS_JS); page.wait_for_timeout(700)
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','XAGUSD']); switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
        for name, code in (("new", "()=>pb2OpenAsset('XAGUSD')"), ("edit", "()=>pb2OpenEdit('xp')")):
            js(page, "()=>{ if(bdPopOpen()) bdPopClose(); }"); js(page, code); page.wait_for_timeout(500)
            th = js(page, SCAN, "#bdPop") or []
            check(f"{tag} C: Satellite form ({name}) has no Thai UI strings", not th, th[:8])
        r = js(page, """()=>{ const q=s=>document.querySelector('#pb2Body '+s); return {draft: q('[data-pb2-draft]') && [q('[data-pb2-draft]').innerText, q('[data-pb2-draft]').getAttribute('onclick')], save: q('[data-pb2-save]') && [q('[data-pb2-save]').innerText, q('[data-pb2-save]').getAttribute('onclick')], ema: !!q('[data-pb2-tg="ema"]'), str: !!q('[data-pb2-tg="str"]') || !!q('[data-pb2-tg]'), prices: !!q('[data-pb2-prices]')}; }""")
        check(f"{tag} C: Satellite footer Save draft / Save plan keep their handlers; prices + EMA50/Structure toggles stay", r["draft"] and r["draft"][0] == "Save draft" and "pb2Save(true)" in r["draft"][1] and r["save"] and r["save"][0] == "Save plan" and "pb2Save(false)" in r["save"][1] and r["ema"] and r["prices"], r)
        if w < 600:
            s = js(page, """()=>{ const f = document.querySelector('#pb2Body .pb2-ft'), b = document.querySelector('#pb2Body [data-pb2-save]'), r = b.getBoundingClientRect(); return {pos: getComputedStyle(f).position, h: Math.round(r.height), vis: r.bottom <= innerHeight + 1 && r.top >= 0}; }""")
            check(f"{tag} C: Satellite form 390 — sticky footer, Save plan visible, buttons ≥ 44 px", s["pos"] == "sticky" and s["vis"] and s["h"] >= 44, s)
        if w == 1440: page.screenshot(path=os.path.join(SHOTS, "lr3-form-sat-1440.png"))
        ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} C: Satellite form no overflow", ov <= 0, ov)
    finally:
        b.close()
