#!/usr/bin/env python3
"""Bug-hunt crawl (REPORT ONLY) — fixtures only (mock Firebase via P39.launch; every http(s) request not in the suites' stub list is aborted).
Opens each main tab at 390/1024/1440, clicks every visible button that is not save/delete-like (confirm dialogs are DISMISSED),
logs console errors / uncaught exceptions / horizontal overflow / empty panels / clipped text → docs/reports/bughunt-crawl.txt
Run: python3 tests/crawl_all.py"""
import os, re, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
import run_tests_phase38 as P38
import run_tests_phase39 as P39
import run_tests_phase4 as base

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reports", "bughunt-crawl.txt")
TABS = ["today", "flow", "watch", "plan", "journal", "mix"]
VPS = [(390, 844), (1024, 768), (1440, 900)]
MAXCLICK = int(os.environ.get("CRAWL_MAX", "90"))
DANGER = re.compile(r"ลบ|delete|remove|บันทึก|save|reset|รีเซ็ต|restore|กู้|sign ?out|logout|ออกจาก|clear|ล้าง|ยืนยัน|confirm|ปิดแผน|close plan|เปิดแผน|apply|นำเข้า.*บันทึก|import.*save|ส่ง|submit|disconnect|ย้าย|archive|merge", re.I)
issues = {}

def log(vp, tab, kind, detail):
    k = (kind, detail[:160])
    issues.setdefault(k, set()).add(f"{vp}/{tab}")

GATHER = r"""()=>{
  const out=[]; let i=0;
  document.querySelectorAll('button, [role=button], .tabbtn, summary, [onclick]').forEach(b=>{
    const r=b.getBoundingClientRect(); const cs=getComputedStyle(b);
    if(r.width<2||r.height<2||cs.visibility==='hidden'||cs.display==='none'||b.disabled) return;
    if(b.closest('#authBox,#authOverlay')) return;
    const sig=(b.id||'')+'|'+(b.innerText||b.getAttribute('aria-label')||'').trim().slice(0,40)+'|'+(b.getAttribute('onclick')||'').slice(0,60)+'|'+(b.dataset?JSON.stringify(b.dataset).slice(0,60):'');
    b.setAttribute('data-crawl', String(i)); out.push({i, sig, label:(b.innerText||b.getAttribute('aria-label')||b.title||'').trim().slice(0,50), oc:(b.getAttribute('onclick')||'')}); i++;
  });
  return out; }"""

AUDIT = r"""(tabId)=>{
  const res=[]; const de=document.documentElement;
  if(de.scrollWidth-window.innerWidth>1) res.push(['overflow','horizontal overflow +'+(de.scrollWidth-window.innerWidth)+'px']);
  const t=document.getElementById(tabId); if(t && t.style.display!=='none' && (t.innerText||'').trim().length<15) res.push(['empty','panel '+tabId+' is empty']);
  let n=0;
  document.querySelectorAll('body *').forEach(e=>{
    if(n>3) return; const cs=getComputedStyle(e);
    if(cs.display==='none'||cs.visibility==='hidden') return;
    const r=e.getBoundingClientRect(); if(r.width<4||r.height<4) return;
    if((cs.overflowX==='hidden'||cs.overflow==='hidden') && cs.textOverflow!=='ellipsis' && e.scrollWidth>e.clientWidth+2 && e.children.length===0 && (e.innerText||'').trim().length>3 && cs.whiteSpace!=='normal'){
      n++; res.push(['clipped','text clipped (no ellipsis): '+(e.tagName+'.'+(e.className||'').toString().slice(0,30))+' "'+(e.innerText||'').trim().slice(0,30)+'"']); }
    if(r.right>window.innerWidth+2 && r.width<window.innerWidth*1.5 && cs.position!=='fixed' && !e.closest('[style*="overflow"],.scroll,.tblWrap') && n<=3 && e.children.length===0 && (e.innerText||'').trim().length>3){
      n++; res.push(['offscreen','element extends past viewport: '+(e.tagName+'.'+(e.className||'').toString().slice(0,30))+' "'+(e.innerText||'').trim().slice(0,30)+'"']); }
  });
  return res; }"""

def run(pw, w, h, tab):
    vp = str(w)
    doc = P38.doc38(clean=False)
    browser, ctx, page, ce, pe, dlg = P39.launch(pw, w, h, doc=doc, clean=False, extra=None)
    # hard guarantee: nothing leaves the machine (suite stubs fall through, everything else aborted)
    page.route(re.compile(r"^https?://"), lambda r: r.fallback() if re.search(r"gstatic\.com/firebasejs|fonts\.(googleapis|gstatic)|fundflow\.json|er-api|twelvedata", r.request.url) else r.abort())
    page.remove_listener("dialog", page.listeners("dialog")[0]) if hasattr(page, "listeners") else None
    page.on("dialog", lambda d: d.dismiss())
    seen = set(); clicks = 0; ci = 0; pi = 0
    def flush(where):
        nonlocal ci, pi
        for m in ce[ci:]: log(vp, tab, "console-error", f"{m[:140]} @ {where}")
        for m in pe[pi:]: log(vp, tab, "uncaught", f"{m[:140]} @ {where}")
        ci, pi = len(ce), len(pe)
    try:
        page.evaluate(f"()=>switchTab('{tab}')"); page.wait_for_timeout(500); flush("open")
        tid = {"today":"tabToday","flow":"tabFlow","watch":"tabWatch","plan":"tabPlan","journal":"tabJournal","mix":"tabMix"}[tab]
        for rnd in range(4):
            btns = page.evaluate(GATHER)
            todo = [b for b in btns if b["sig"] not in seen and not DANGER.search(b["label"]) and not DANGER.search(b["oc"])]
            if not todo: break
            for b in todo:
                if clicks >= MAXCLICK: break
                seen.add(b["sig"]); clicks += 1
                try:
                    el = page.locator(f'[data-crawl="{b["i"]}"]').first
                    if el.count() == 0: continue
                    el.click(timeout=1500, force=True)
                except Exception as ex:
                    if "Timeout" not in str(ex): log(vp, tab, "click-fail", f'"{b["label"]}" {str(ex)[:80]}')
                page.wait_for_timeout(120)
                flush(f'click "{b["label"]}"')
                for k, d in page.evaluate(AUDIT, tid): log(vp, tab, k, d + f' after "{b["label"]}"')
                # close overlays, return to tab
                page.evaluate("()=>{document.querySelectorAll('.overlay.show,[id$=Overlay].show').forEach(o=>o.classList.remove('show'));}")
                page.keyboard.press("Escape")
            if clicks >= MAXCLICK: break
            page.evaluate(f"()=>switchTab('{tab}')"); page.wait_for_timeout(200)
    except Exception as ex:
        log(vp, tab, "crawl-abort", str(ex)[:140])
    finally:
        flush("end"); browser.close()
    return clicks

if __name__ == "__main__":
    tot = 0; t0 = time.time()
    with sync_playwright() as pw:
        for (w, h) in VPS:
            for tab in TABS:
                n = run(pw, w, h, tab); tot += n
                print(f"{w} {tab}: {n} clicks ({int(time.time()-t0)}s)", flush=True)
    lines = [f"[{kind}] {detail}  (@ {', '.join(sorted(v))})" for (kind, detail), v in sorted(issues.items())]
    open(OUT, "w").write(f"# crawl_all — {tot} clicks, {len(lines)} distinct issue lines\n" + "\n".join(lines) + "\n")
    print(f"done: {tot} clicks, {len(lines)} issues → {OUT}")
