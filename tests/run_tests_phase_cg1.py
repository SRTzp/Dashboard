#!/usr/bin/env python3
"""CG1 — showGuideToast (timing · hover pause · replace · ✕/tap close · reduced motion · 390/1440 light+dark shots)
+ mode prefix 'idea-scout <mode>:' line 1 + Export JSON pick/update · เทส CG1"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase107 as T
import ln3fix_common as C

ENGINE = base.BROWSER_ENGINE
results = []
js, settle = C.js, T.settle
SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cg1_shots")


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + detail[:700]) if (detail and not ok) else ""))


def toast_tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        ms = js(page, "()=>[cgToastMs(['x'.repeat(40)]), cgToastMs(['x'.repeat(200)]), cgToastMs(['x'.repeat(120)]), cgToastMs(['x'.repeat(60),'y'.repeat(60)])]")
        check(f"{tag} timing 40→5s · 200→10s (cap) · 120→9.7s · ผลรวมหลายบรรทัด", ms == [5000, 10000, 9700, 9700], ms)
        js(page, "()=>showGuideToast(CG_GUIDE.scanNew)"); settle(page, 250)
        st = js(page, """()=>{ const t=document.getElementById('cgToast'); const r=t.getBoundingClientRect(); return {role:t.getAttribute('role'), live:t.getAttribute('aria-live'), shown:t.classList.contains('show'),
            lines:t.querySelectorAll('.cgL').length, x:t.querySelectorAll('[data-cg-x]').length, w:r.width, fits:r.left>=0&&r.right<=innerWidth, ctr:Math.abs((r.left+r.right)/2-innerWidth/2)<2, n:document.querySelectorAll('#cgToast').length}; }""")
        check(f"{tag} role=status · aria-live=polite · 3 บรรทัด · ✕ เดียว · กึ่งกลาง · ไม่ล้นจอ", st["role"] == "status" and st["live"] == "polite" and st["shown"] and st["lines"] == 3 and st["x"] == 1 and st["fits"] and st["ctr"] and st["n"] == 1, st)
        if w <= 430: check(f"{tag} กว้าง = viewport − 32px", abs(st["w"] - (w - 32)) <= 1, st["w"])
        fit = js(page, """()=>{ const o={}; for(const k of Object.keys(CG_GUIDE)){ showGuideToast(CG_GUIDE[k]); const t=document.getElementById('cgToast'); o[k]=[...t.querySelectorAll('.cgL')].map(e=>Math.round(e.getBoundingClientRect().height/parseFloat(getComputedStyle(e).lineHeight))).reduce((a,b)=>a+b,0); } return o; }""")
        check(f"{tag} ทุก guide toast ไม่เกิน 3 บรรทัดที่มองเห็น", all(v <= 3 for v in fit.values()), fit)
        js(page, "()=>document.getElementById('cgToast').dispatchEvent(new Event('mouseenter'))"); settle(page, 150)
        paused = js(page, "()=>cgToastT === 0 && document.getElementById('cgToast').classList.contains('show')")
        js(page, "()=>document.getElementById('cgToast').dispatchEvent(new Event('mouseleave'))"); settle(page, 100)
        check(f"{tag} hover หยุดนับ · ออกแล้วนับต่อ", paused and js(page, "()=>cgToastT !== 0"), paused)
        js(page, "()=>showGuideToast(CG_GUIDE.update)"); settle(page, 150)
        r = js(page, "()=>({n:document.querySelectorAll('#cgToast').length, l:[...document.querySelectorAll('#cgToast .cgL')].map(e=>e.textContent)})")
        check(f"{tag} อันใหม่แทนอันเก่า (ครั้งละอัน)", r["n"] == 1 and r["l"] == CG_UPDATE, r)
        js(page, "()=>document.querySelector('[data-cg-x]').click()"); settle(page, 150)
        check(f"{tag} ✕ ปิด", js(page, "()=>!document.getElementById('cgToast').classList.contains('show')"))
        js(page, "()=>showGuideToast(CG_GUIDE.match)"); settle(page, 100)
        js(page, "()=>document.querySelector('#cgToast .cgL').click()"); settle(page, 150)
        check(f"{tag} แตะที่ toast = ปิด", js(page, "()=>!document.getElementById('cgToast').classList.contains('show')"))
        js(page, "()=>showGuideToast(['a','b','c','d'])")
        check(f"{tag} สูงสุด 3 บรรทัด", js(page, "()=>document.querySelectorAll('#cgToast .cgL').length") == 3)
        js(page, "()=>cgCopyFailToast()")
        check(f"{tag} copy failed toast = 'Copy failed — select and copy manually' (ไม่มี guide)", js(page, "()=>[...document.querySelectorAll('#cgToast .cgL')].map(e=>e.textContent)") == ["Copy failed — select and copy manually"])
        # click-through: toast ไม่บล็อกที่อื่นเมื่อซ่อนแล้ว
        js(page, "()=>cgToastHide()"); settle(page, 300)
        check(f"{tag} ซ่อนแล้ว pointer-events:none (ไม่บล็อกคลิก)", js(page, "()=>getComputedStyle(document.getElementById('cgToast')).pointerEvents") == "none")
        # prefix
        pre = js(page, """()=>({ask:sdAskPrompt({sym:'XLK',name:'Tech',quad:'lead',lastObs:'2026-11-06',dMom:0}, 'D').split('\\n')[0].slice(0,18)})""")
        check(f"{tag} Ask why line 1 = 'idea-scout scan:'", pre["ask"] == "idea-scout scan: X", pre)
        # Export pick vs update (inject a minimal idea into ideaList)
        mode = js(page, """()=>{ const out={}; const mk=(c)=>({id:'cg1-'+c, idea:{schema:'idea@1', id:'cg1-'+c, name:'t', candidates:c?[{sym:'AAA',rank:1,state:'study'}]:[], chain:{segments:[]}, gaps:[]}, log:[]});
            const saved=ideaList.slice(); let got=null; window.__cpx=[];
            Object.defineProperty(navigator,'clipboard',{value:{writeText:t=>{window.__cpx.push(t);return Promise.resolve();}},configurable:true});
            ideaList.length=0; ideaList.push(mk(0), mk(1)); try{ ideaExport('cg1-0'); ideaExport('cg1-1'); }catch(e){ out.err=String(e); }
            out.saved=saved.length; return out; }""")
        settle(page, 400)
        cp = js(page, "()=>window.__cpx")
        ok = len(cp) == 2 and cp[0].startswith("idea-scout pick:\n\n{") and cp[1].startswith("idea-scout update:\n\n{")
        parse = ok and all(json.loads(c.split("\n\n", 1)[1]) for c in cp)
        check(f"{tag} Export: ไม่มีบริษัท → 'idea-scout pick:' · มี → 'update:' · บรรทัดว่าง · JSON หลังบรรทัดที่ 2 parse ได้", ok and parse, [mode, [c[:40] for c in cp]])
        imp = js(page, "(t)=>{ const f = x=>{ const r = ideaParse(x); return r.err || 'ok'; }; return [f(t), f(t.split('\\n\\n').slice(1).join('\\n\\n'))]; }", cp[1]) if ok else None
        check(f"{tag} Import: ข้อความ export ทั้งก้อน = JSON ล้วน (ข้ามบรรทัด idea-scout …:)", imp and imp[0] == imp[1] and "อ่าน JSON" not in imp[0], imp)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


CG_UPDATE = ["Goal: refresh evidence/status.", "Paste → idea-scout update → import."]


def reduced_motion(pw):
    b = pw.chromium.launch(); ctx = b.new_context(reduced_motion="reduce", viewport={"width": 1440, "height": 900}); page = ctx.new_page()
    try:
        import pathlib
        page.goto(pathlib.Path(base.INDEX_HTML).resolve().as_uri() if hasattr(base, "INDEX_HTML") else "file://" + os.path.abspath("../index.html"))
        page.wait_for_timeout(500)
        css = page.evaluate("""()=>{ showGuideToast(['x']); const t=document.getElementById('cgToast'); const a=getComputedStyle(t).transform; t.classList.remove('show'); const b=getComputedStyle(t).transform; return [a,b,getComputedStyle(t).transitionProperty]; }""")
        check("reduced-motion: ไม่มี transform animation (fade เท่านั้น)", css[0] == css[1] and "translate" not in css[2], css)
    finally:
        b.close()


def shots(pw):
    os.makedirs(SHOTS, exist_ok=True)
    for w, h in ((390, 800), (1440, 900)):
        for theme in ("light", "dark"):
            b, page, ce, pe = T.launch(pw, w, h)
            try:
                js(page, "(t)=>{ document.documentElement.setAttribute('data-theme', t); showGuideToast(CG_GUIDE.ask); }", theme); settle(page, 400)
                page.screenshot(path=os.path.join(SHOTS, f"cg1_{w}_{theme}.png"))
            finally:
                b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 800)): toast_tests(pw, w, h)
        reduced_motion(pw); shots(pw)
    bad = [r for r in results if not r[1]]
    print(f"\nCG1: {len(results) - len(bad)}/{len(results)} PASS")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
