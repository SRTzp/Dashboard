#!/usr/bin/env python3
"""UI2a — จัดหน้าแผง Macro ไตรมาสตอนกาง (.pbBody 2 คอลัมน์ · กล่อง .pbWatch · แถว asset · ท่าทีผสม)
การ์ดเดียวกันใช้ทั้งแผงจริง · พรีวิววาง JSON · ดูประวัติ · ภาพเก็บที่ tests/screenshots/ui2a-*.png
รัน: python3 run_tests_phase17.py (mock Firestore + fundflow stub)"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase11 as p11
from run_tests_phase11 import pbver, seed_pb, iso, txt, no_overflow, shot, fresh

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = base.BROWSER_ENGINE
results = []
LONG = "เหตุผลยาวมากเพื่อทดสอบการตัดสองบรรทัด " * 8


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def mkver(watch="ดู CPI วันพฤหัส", doc="https://docs.example.com/d/abc", no=1):
    v = pbver(no, iso(-24), x="up", b="up_flat", r="down_flat", u="none",
              ba={"posture": "ระยะสั้นยังผันผวน", "confidence": "high", "why": LONG},
              ra={"confidence": "mid"})
    v["assets"]["XAUUSD"]["why"] = "สั้น ๆ"
    v["view"]["base"] = "Base ตัวอย่าง"; v["view"]["alt"] = "Alt ตัวอย่าง"
    if watch is not None: v["view"]["watch"] = watch
    if doc: v["doc_url"] = doc
    return v


def q(page, sel, prop):
    return page.evaluate("([s,p])=>{ const e=document.querySelector(s); return e ? getComputedStyle(e)[p] : null; }", [sel, prop])


def px(page, sel, prop="fontSize"):
    v = q(page, sel, prop); return float(v[:-2]) if v else None


def open_panel(page):
    page.evaluate("() => { switchTab('flow'); pbOpen = true; pbRender(); }"); page.wait_for_timeout(120)


def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        page.evaluate("() => switchTab('flow')"); page.wait_for_timeout(150)
        seed_pb(page, [mkver()]); open_panel(page)
        # ── watch ──
        check(f"{tag} .pbWatch: หัว 'ข้อควรติดตาม' แยก element + เนื้อความแยก", txt(page, "#pbPanel .pbWatchK") == "ข้อควรติดตาม" and txt(page, "#pbPanel .pbWatchV") == "ดู CPI วันพฤหัส")
        fw, ft = px(page, "#pbPanel .pbWatch"), px(page, "#pbPanel .pbThesis")
        check(f"{tag} .pbWatch font-size ({fw}) ≤ .pbThesis ({ft})", fw <= ft)
        check(f"{tag} หัวกล่อง 11.5px สี --mute · พื้น --soft", px(page, "#pbPanel .pbWatchK") == 11.5 and q(page, "#pbPanel .pbWatchK", "color") == page.evaluate("()=>{const d=document.createElement('i');d.style.color='var(--mute)';document.body.appendChild(d);const c=getComputedStyle(d).color;d.remove();return c}") and q(page, "#pbPanel .pbWatch", "backgroundColor") == page.evaluate("()=>{const d=document.createElement('i');d.style.color='var(--soft)';document.body.appendChild(d);const c=getComputedStyle(d).color;d.remove();return c}"))
        a = page.locator("#pbPanel .pbWatchLink")
        check(f"{tag} มี doc_url → ลิงก์ 'ดู scenario ↗' = doc_url#events · แท็บใหม่", a.count() == 1 and a.get_attribute("href") == "https://docs.example.com/d/abc#events" and a.get_attribute("target") == "_blank" and "ดู scenario" in a.inner_text())
        seed_pb(page, [mkver(doc=None)]); open_panel(page)
        check(f"{tag} ไม่มี doc_url → ไม่มีลิงก์ scenario", page.locator("#pbPanel .pbWatch").count() == 1 and page.locator("#pbPanel .pbWatchLink").count() == 0)
        seed_pb(page, [mkver(doc="javascript:alert(1)")]); open_panel(page)
        check(f"{tag} doc_url ไม่ใช่ http(s) → ไม่มีลิงก์ (pbSafeUrl)", page.locator("#pbPanel .pbWatchLink").count() == 0)
        seed_pb(page, [mkver(watch=None)]); open_panel(page)
        check(f"{tag} ไม่มี watch → ไม่มีกล่อง", page.locator("#pbPanel .pbWatch").count() == 0)
        seed_pb(page, [mkver()]); open_panel(page)
        # ── layout ──
        pos = page.evaluate("""() => { const r = s => document.querySelector(s).getBoundingClientRect();
            const b=r('#pbPanel .pbBody'), l=r('#pbPanel .pbColL'), rows=r('#pbPanel .pbRows');
            return {cols:getComputedStyle(document.querySelector('#pbPanel .pbBody')).gridTemplateColumns.split(' ').length, lx:l.left, rx:rows.left, ly:l.top, ry:rows.top, lb:l.bottom, rw:rows.width, lw:l.width}; }""")
        if w > 900:
            check(f"{tag} กาง: 2 คอลัมน์ · asset อยู่ขวา (สัดส่วน ~5:6)", pos["cols"] == 2 and pos["rx"] > pos["lx"] + pos["lw"] - 1 and abs(pos["ry"] - pos["ly"]) < 4 and pos["rw"] > pos["lw"], json.dumps(pos))
        else:
            check(f"{tag} กาง: คอลัมน์เดียว (asset อยู่ใต้ base/alt)", pos["cols"] == 1 and pos["ry"] >= pos["lb"] - 1 and abs(pos["rx"] - pos["lx"]) < 2, json.dumps(pos))
        order = page.evaluate("() => [...document.querySelectorAll('#pbPanel .pbBody .pbThesis, #pbPanel .pbBody .pbWatch, #pbPanel .pbBody .pbPill, #pbPanel .pbBody .pbScn, #pbPanel .pbBody .pbRowW')].map(e=>(e.classList.contains('pbPill')?'pbPill':e.className.split(' ')[0])).join(',')")
        check(f"{tag} ลำดับ DOM: thesis → watch → pillars → base/alt → asset", order == "pbThesis,pbWatch,pbPill,pbScn,pbScn,pbRowW,pbRowW,pbRowW,pbRowW", order)
        check(f"{tag} thesis/base/alt/why: max-width 70ch · line-height 1.55", all(q(page, s, "maxWidth") not in (None, "none") and abs(float(q(page, s, "lineHeight")[:-2]) / px(page, s) - 1.55) < .02 for s in ("#pbPanel .pbThesis", "#pbPanel .pbScn", "#pbPanel .pbWhy")))
        # ── แถว asset ──
        check(f"{tag} บรรทัดบน: ไอคอน · ชื่อ · ความมั่นใจ อยู่แถวเดียว (BTC)", page.evaluate("""() => { const r=[...document.querySelectorAll('#pbPanel .pbRowW')][1].querySelector('.pbRow'); const t=[...r.children].map(e=>{const b=e.getBoundingClientRect(); return b.top+b.height/2;}); return r.children.length===3 && Math.max(...t)-Math.min(...t)<3; }"""))
        why = "#pbPanel .pbRowW:has-text('BTC') .pbWhy"
        lc = page.evaluate("(s)=>{ const e=document.querySelector(s), c=getComputedStyle(e); return [c.webkitLineClamp, c.whiteSpace, e.scrollHeight>e.clientHeight, e.clientHeight/parseFloat(c.lineHeight)]; }", "#pbPanel .pbRowW:nth-child(2) .pbWhy")
        check(f"{tag} why: บรรทัดเดียว nowrap + ellipsis (MF1 แทน line-clamp 2) · ข้อความยาวถูกตัดด้วย …", lc[1] == "nowrap" and lc[3] < 1.1 and page.evaluate("(s)=>{ const e=document.querySelector(s); return getComputedStyle(e).textOverflow==='ellipsis' && e.scrollWidth>e.clientWidth; }", "#pbPanel .pbRowW:nth-child(2) .pbWhy"), json.dumps(lc))
        check(f"{tag} why 13px · เล็กสุดในกาง ≥ 11.5px", px(page, "#pbPanel .pbWhy") == 13 and page.evaluate("() => [...document.querySelectorAll('#pbPanel .pbBody *')].every(e=>!e.childNodes.length || ![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()) || parseFloat(getComputedStyle(e).fontSize)>=11.5)"))
        gap = page.evaluate("() => { const r=[...document.querySelectorAll('#pbPanel .pbRowW')].map(e=>getComputedStyle(e)); return [r[1].paddingTop, r[1].paddingBottom, r[1].borderTopWidth]; }")
        check(f"{tag} ช่องไฟแถว 8px · เส้นคั่นเดิม 1px", gap == ["8px", "8px", "1px"], json.dumps(gap))
        # ── ท่าทีผสม ──
        mixes = page.evaluate("() => [...document.querySelectorAll('#pbPanel .pbRowW')].map(r=>{const m=r.querySelector('.pbMix'); return m ? m.innerText.trim() : null;})")
        check(f"{tag} .pbMix ในการ์ด: BTC = posture ล้วน · BRENT (ไม่มี posture) = 'ท่าทีผสม' · เต็ม/none ไม่มี", mixes == [None, "ระยะสั้นยังผันผวน", "ท่าทีผสม", None], json.dumps(mixes, ensure_ascii=False))
        check(f"{tag} .pbMix ในการ์ด ไม่มีไอคอน ▲/▼/▬ ซ้ำ", not any(c in m for m in mixes if m for c in "▲▼▬"))
        # ── sheet asset + พับ/กาง ──
        page.click("#pbPanel .pbRowW:has-text('BTC')"); page.wait_for_timeout(80)
        check(f"{tag} แตะแถว asset → เปิด sheet เดิม (why · วิธีวางตัว)", "ระยะสั้นยังผันผวน" in page.inner_text(".pb-sheet") and "วิธีวางตัว" in page.inner_text(".pb-sheet"))
        page.click(".pb-sheet button:has-text('ปิด')")
        page.click("#pbPanel .pbHead"); page.wait_for_timeout(60)
        check(f"{tag} แตะหัว → พับ (ไม่มี .pbBody · หัวคงเดิม)", page.locator("#pbPanel .pbBody").count() == 0 and page.locator("#pbPanel .pbIcos .pbIco").count() == 4)
        page.click("#pbPanel .pbHead"); page.wait_for_timeout(60)
        check(f"{tag} แตะหัวอีกครั้ง → กาง", page.locator("#pbPanel .pbBody").count() == 1)
        no_overflow(page, w, tag)
        page.locator("#pbPanel").screenshot(path=os.path.join(p11.SHOTS, f"ui2a-panel-{label}.png"))
        mono = page.evaluate("() => [...document.querySelectorAll('#pbPanel, #pbPanel *')].filter(e=>/mono|courier/i.test(getComputedStyle(e).fontFamily)).length")
        check(f"{tag} ไม่มี font-family mono ใน .pbPanel", mono == 0, str(mono))
        # ── พรีวิววาง JSON (sheet แคบ → คอลัมน์เดียว ไม่ล้น) ──
        obj = mkver(); obj.pop("id"); [obj.pop(k, None) for k in ("savedAt", "versionNo", "prevId", "reason", "stanceChanges")]
        obj["quarter"] = "2026Q4"; obj["status"] = "draft"
        page.click("#pbPanel button:has-text('วาง JSON')")
        page.fill("#pbText", json.dumps(obj, ensure_ascii=False))
        page.click(".pb-sheet button:has-text('ตรวจ')"); page.wait_for_timeout(120)
        check(f"{tag} พรีวิววาง JSON: การ์ดกางมี watch + 4 แถว · คอลัมน์เดียว (sheet แคบ)", page.locator(".pb-sheet .pbCard .pbWatch").count() == 1 and page.locator(".pb-sheet .pbRowW").count() == 4 and q(page, ".pb-sheet .pbBody", "display") != "grid", q(page, ".pb-sheet .pbBody", "display"))
        ov = page.evaluate("() => { const s=document.querySelector('.pb-sheet .pbCard'); return s.scrollWidth <= s.clientWidth+1 && document.querySelector('.pb-sheet .pbSh').scrollWidth <= document.querySelector('.pb-sheet .pbSh').clientWidth+1; }")
        check(f"{tag} พรีวิววาง JSON ไม่ล้น", ov)
        no_overflow(page, w, tag)
        page.locator(".pb-sheet .pbCard").screenshot(path=os.path.join(p11.SHOTS, f"ui2a-preview-{label}.png"))
        page.click(".pb-sheet button:has-text('ปิด')"); page.wait_for_timeout(60)
        # ── ประวัติ ──
        page.click("#pbPanel button:has-text('ประวัติ')"); page.wait_for_timeout(80)
        page.click(".pb-sheet .pbHist"); page.wait_for_timeout(80)
        check(f"{tag} ดูประวัติ: การ์ดแสดงได้ ไม่ล้น", page.locator(".pb-sheet .pbCard .pbBody .pbRowW").count() == 4 and page.evaluate("() => { const s=document.querySelector('.pb-sheet .pbCard'); return s.scrollWidth <= s.clientWidth+1; }"))
        no_overflow(page, w, tag)
        page.evaluate("() => document.querySelectorAll('.pb-sheet').forEach(e=>e.remove())")
        # ── F2c .pbMix ไม่เปลี่ยน ──
        seed_pb(page, [pbver(1, iso(-72), x="up", b="down_flat", ba={"posture": "ระยะสั้นยังผันผวน"}, r="flat")])
        p5.goto_sat(page)
        p11.reset_ideas(page)
        p11.wk(page, "BTCUSD", "Long", "up", inval=60000)
        p5.open_editor(page, "BTCUSD")
        sel = '.ui-editor[data-asset="BTCUSD"] .ui-mac .pbMix'
        m = txt(page, sel)
        mg = q(page, sel, "marginTop"), q(page, sel, "marginLeft")
        check(f"{tag} F2c Strategy .pbMix ยังเป็น '▼▬ ลง/ผสม · ระยะสั้นยังผันผวน' · margin เดิม (ซ้าย 0)", m == "▼▬ ลง/ผสม · ระยะสั้นยังผันผวน" and mg[1] == "0px", f"{m} {mg}")
        shot(page, f"ui2a-strategy-{label}.png", '.ui-editor[data-asset="BTCUSD"]')
    finally:
        check(f"{tag} console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
        browser.close()


def main():
    with sync_playwright() as pw:
        ui_tests(pw, 1440, 900, "1440px")
        ui_tests(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 17 / UI2a) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
