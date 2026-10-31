#!/usr/bin/env python3
"""CX1 — Core การ์ดตำแหน่ง: ตัดชิปที่ซ้ำแผงสรุป · ตัวเลขชิปไม่ใช้ mono · ช่องกรอกวันข่าวมีสไตล์ · เทส 53
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-05 ไทย
ภาพ tests/screenshots/cx1-{core-head-normal,core-head-warn,core-head-more-open,settings-news}-{1440,390}.png
รัน: python3 run_tests_phase53.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase38 as P
import run_tests_phase39 as P39
import run_tests_phase43 as P43

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-CX1.html"))
results = []
js, txt = P.js, P43.txt
HEAD = '[data-core-head="main"]'
MORE = ["data-c-cashfree", "data-c-l2", "data-c-lshare", "data-c-missing"]


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(400)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")


def launch(pw, w, h, cards=None, meta=None, prices=None):
    r = P43.launch(pw, w, h, prices=prices, meta=meta, cards=cards if cards is not None else {"cw": P43.w_card()})
    return r


def launch_px(pw, w, h):
    return launch(pw, w, h, meta=P43.meta_doc("2026-10-04T06:31:00Z"), prices={"AAA": P43.px_doc("AAA", 100, ema=95)})


def patch(page, l2=None, missing=None, lpct=None):
    js(page, """([l2,missing,lpct])=>{
      if(!window.__o){ window.__o = {risk: coreAcctRisk, ctx: coreCtx}; }
      coreAcctRisk = (A)=>{ const r = window.__o.risk(A); if(!r) return r; const o = Object.assign({}, r); if(A==='main'){ if(l2) o.levelFull = l2; if(missing!=null) o.missing = missing; } return o; };
      coreCtx = (A)=>{ const c = window.__o.ctx(A); if(A==='main' && lpct!=null && c.split) return Object.assign({}, c, {split: Object.assign({}, c.split, {lPct: lpct})}); return c; };
      render();
    }""", [l2, missing, lpct])
    js(page, "()=>0"); page.wait_for_timeout(300)


def unpatch(page):
    js(page, "()=>{ if(window.__o){ coreAcctRisk = window.__o.risk; coreCtx = window.__o.ctx; window.__o = null; } render(); }"); page.wait_for_timeout(300)


def inside_more(page, attr, acct="main"):
    return js(page, f"()=>{{ const e=document.querySelector('[data-core-head=\"{acct}\"] [{attr}]'); return e ? !!e.closest('details[data-c-more]') : null; }}")


def visible(page, attr, acct="main"):
    loc = page.locator(f'[data-core-head="{acct}"] [{attr}]')
    return loc.first.is_visible() if loc.count() else None


def chip_texts(page, acct):
    return js(page, f"""()=>{{ const o={{}}; document.querySelectorAll('[data-core-head="{acct}"] .ccStat[data-c-tank],[data-core-head="{acct}"] [data-c-cashfree],[data-core-head="{acct}"] [data-c-l2],[data-core-head="{acct}"] [data-c-lshare],[data-core-head="{acct}"] [data-c-gate],[data-core-head="{acct}"] [data-c-f],[data-core-head="{acct}"] [data-c-missing]').forEach(e=>{{ const k=[...e.attributes].map(a=>a.name).find(n=>n.startsWith('data-c-')); o[k]=e.textContent.replace(/\\s+/g,' ').trim(); }}); return o; }}""")


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    sfx = label.replace("px", "")
    browser, context, page, ce, pe, dialogs = launch_px(pw, w, h)
    try:
        # ── 1 ปกติ
        head_stats = js(page, f"()=>[...document.querySelectorAll('{HEAD} .ccStat')].filter(e=>!e.closest('details')).map(e=>[...e.attributes].map(a=>a.name).find(n=>n.startsWith('data-c-'))||'?')")
        check(f"{tag} 1 active ปกติ: หัวบัญชีเห็นแค่ ถัง · f (DD ถ้ามี) — ไม่มี cashfree/l2/lshare/gate/missing บนหัว", all(k not in head_stats for k in MORE) and "data-c-tank" in head_stats and "data-c-f" in head_stats, json.dumps(head_stats))
        check(f"{tag} 1 ป้ายตลาด (.ccChip) ยังแสดง", js(page, f"()=>!!document.querySelector('{HEAD} .ccChip')"))
        check(f"{tag} 1 ทั้ง 4 ชิปอยู่ใน details[data-c-more] (มีใน DOM)", all(inside_more(page, a) is True for a in MORE), json.dumps({a: inside_more(page, a) for a in MORE}))
        check(f"{tag} 1 ปิด details → มองไม่เห็น", all(visible(page, a) is False for a in MORE), json.dumps({a: visible(page, a) for a in MORE}))
        shot(page, f"cx1-core-head-normal-{sfx}.png", HEAD)
        page.click(f"{HEAD} details[data-c-more] > summary"); page.wait_for_timeout(200)
        check(f"{tag} 1 กดเปิด → เห็นครบ 4 ชิป (RG2b ถอดชิปประตู)", all(visible(page, a) is True for a in MORE), json.dumps({a: visible(page, a) for a in MORE}))
        check(f"{tag} 1 summary เขียน 'รายละเอียด'", txt(page, f"{HEAD} details[data-c-more] > summary") == "รายละเอียด")
        shot(page, f"cx1-core-head-more-open-{sfx}.png", HEAD)
        # ── 5 ตัวเลขเท่าเดิม (เทียบกับไฟล์ก่อน CX1 · fixture เดียวกัน)
        now = chip_texts(page, "main"); now_fam = chip_texts(page, "fam")
        # ── 7 มือถือ
        hh = js(page, f"()=>document.querySelector('{HEAD}').getBoundingClientRect().height")
        if w < 500:
            page.click(f"{HEAD} details[data-c-more] > summary"); page.wait_for_timeout(200)
            rows = js(page, f"""()=>{{ const ys=[]; document.querySelectorAll('{HEAD} > *').forEach(e=>{{ const r=e.getBoundingClientRect(); ys.push([e.className||e.tagName, Math.round(r.top), Math.round(r.height)]); }}); return ys; }}""")
            print("ROWS", rows); tops = sorted(r[1] for r in rows); bands = []
            for t in tops:
                if not bands or t - bands[-1] > 14: bands.append(t)
            rows = len(bands)
            check(f"{tag} 7 หัวบัญชี active ปกติ (พับ) ≤ 4 แถว (ชิป ≤ 2 + แถวลิงก์ + บรรทัดราคา)", rows <= 4, f"rows={rows} h={hh}")
            check(f"{tag} 7 ไม่ล้นแนวนอน", overflow(page) <= 0, overflow(page))
        # ── 5 ฟอนต์ตัวเลข
        ff = js(page, f"()=>{{ const b=document.querySelector('{HEAD} .ccStat b'); const s=getComputedStyle(b); return {{f:s.fontFamily, n:s.fontVariantNumeric, body:getComputedStyle(document.body).fontFamily}}; }}")
        mono = js(page, "()=>getComputedStyle(document.documentElement).getPropertyValue('--mono')")
        check(f"{tag} 5 .ccStat b ไม่ใช้ mono · tabular-nums", ff["f"].strip() != mono.strip() and "tabular-nums" in ff["n"], json.dumps([ff, mono], ensure_ascii=False))
        # ── 6 ราคาอัตโนมัติ
        # ── 4 ปุ่มขยาย/ยุบ
        check(f"{tag} 4 มีการ์ด → มี ขยายทั้งหมด/ยุบทั้งหมด", js(page, f"()=>!!document.querySelector('{HEAD} [data-c-expandall]') && !!document.querySelector('{HEAD} [data-c-collapseall]')"))
        # ── 3 ดูรวม 2 บัญชี (fam ไม่ active)
        fam_inline = js(page, """()=>{ const o={}; ['data-c-cashfree','data-c-l2','data-c-lshare','data-c-missing'].forEach(a=>{ const e=document.querySelector('[data-core-head="fam"] ['+a+']'); o[a]= e ? !e.closest('details[data-c-more]') : null; }); return o; }""")
        check(f"{tag} 3 บัญชีที่ไม่ active (fam): เงินสดว่าง/ชั้น 2/L/บันไดใหม่ บนหัวครบ · ขาดราคา 0 อยู่ใน details", fam_inline["data-c-cashfree"] is True and fam_inline["data-c-l2"] is True and fam_inline["data-c-lshare"] is True and fam_inline["data-c-missing"] is False, json.dumps(fam_inline))
        check(f"{tag} 4 fam ไม่มีการ์ด → ไม่มีลิงก์ ขยาย/ยุบ", js(page, "()=>!document.querySelector('[data-core-head=\"fam\"] [data-c-expandall]') && !document.querySelector('[data-core-head=\"fam\"] [data-c-collapseall]')"))
        # ── 2 ผิดปกติ
        for lv in ("warn", "over"):
            patch(page, l2=lv)
            ok = inside_more(page, "data-c-l2") is False and js(page, f"()=>document.querySelector('{HEAD} [data-c-l2]').dataset.level") == lv and js(page, f"()=>document.querySelector('{HEAD} [data-c-l2]').classList.contains('lv-{lv}')")
            check(f"{tag} 2 ชั้น 2 level {lv} → ขึ้นบนหัว สีตามเดิม (lv-{lv})", ok)
            if lv == "warn": shot(page, f"cx1-core-head-warn-{sfx}.png", HEAD)
            unpatch(page)
        patch(page, lpct=1.2)
        check(f"{tag} 2 Ladder เกินถัง (ใช้ 120%) → [data-c-lshare] บนหัว (lv-over)", inside_more(page, "data-c-lshare") is False and js(page, f"()=>document.querySelector('{HEAD} [data-c-lshare]').classList.contains('lv-over')"))
        unpatch(page)
        patch(page, missing=2)
        check(f"{tag} 2 ขาดราคา 2 → [data-c-missing] บนหัว (warn)", inside_more(page, "data-c-missing") is False and js(page, f"()=>document.querySelector('{HEAD} [data-c-missing]').classList.contains('warn')") and "2" in (txt(page, f"{HEAD} [data-c-missing]") or ""))
        unpatch(page)
        check(f"{tag} 2 หลัง unpatch กลับเป็นพับ", all(inside_more(page, a) is True for a in MORE))
        # ── 6 สถานะราคาอัตโนมัติ
        # ── 9 console
        check(f"{tag} 9 ไม่มี console error (Core)", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
        # เก็บไว้เทียบ
        tests.now = (now, now_fam)
    finally:
        browser.close()

    # ราคาอัตโนมัติ: ปกติ / err / stale
    meta_ok = P43.meta_doc("2026-10-04T06:31:00Z", ok=("AAA",))
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, meta=meta_ok, prices={"AAA": P43.px_doc("AAA", 100, ema=95)})
    try:
        el = js(page, "()=>{ const e=document.querySelector('[data-core-head=\"main\"] [data-px-status]'); return e ? {cls:e.className, st:e.dataset.pxStatus, inMore:!!e.closest('details'), txt:e.textContent.trim()} : null; }")
        check(f"{tag} 6 ปกติ = บรรทัดเล็ก ไม่ใช่ .ccStat · ข้อความเดิม · อยู่นอก details", el and "ccStat" not in el["cls"] and el["st"] == "ok" and not el["inMore"] and "ราคาอัตโนมัติ: อัปเดต" in el["txt"] and "1/1 ตัว" in el["txt"], json.dumps(el, ensure_ascii=False))
        shot(page, f"cx1-px-line-{sfx}.png", HEAD)
    finally: browser.close()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, meta=P43.meta_doc("2026-09-20T06:31:00Z"), prices={"AAA": P43.px_doc("AAA", 100, ema=95)})
    try:
        el = js(page, "()=>{ const e=document.querySelector('[data-core-head=\"main\"] [data-px-status]'); return e ? {cls:e.className, st:e.dataset.pxStatus} : null; }")
        check(f"{tag} 6 stale → .ccStat.warn บนหัว", el and el["st"] == "stale" and "ccStat" in el["cls"] and "warn" in el["cls"], json.dumps(el))
    finally: browser.close()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, meta=P43.meta_doc("2026-10-04T06:31:00Z", ok=("AAA",), failed=("XYZ",)), prices={"AAA": P43.px_doc("AAA", 100, ema=95)})
    try:
        el = js(page, "()=>{ const e=document.querySelector('[data-core-head=\"main\"] [data-px-status]'); return e ? {cls:e.className, st:e.dataset.pxStatus} : null; }")
        check(f"{tag} 6 failed → .ccStat.warn เหมือนเดิม", el and el["st"] == "failed" and "ccStat" in el["cls"] and "warn" in el["cls"], json.dumps(el))
    finally: browser.close()
    # ไม่มีการ์ดเลย
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, cards={}, doc=None) if False else launch_nocard(pw, w, h)
    try:
        check(f"{tag} 4 ไม่มีการ์ดเลย (main) → ไม่มีลิงก์ ขยายทั้งหมด/ยุบทั้งหมด", js(page, f"()=>!!document.querySelector('{HEAD}') && !document.querySelector('{HEAD} [data-c-expandall]') && !document.querySelector('{HEAD} [data-c-collapseall]')"))
    finally: browser.close()

    # ── 8 ตั้งค่าวันข่าว
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        js(page, "()=>{ openSystemSettings(); }"); page.wait_for_timeout(500)
        js(page, "()=>{ const d=document.getElementById('newsSetSec'); if(d){ d.open=true; d.scrollIntoView(); } newsSetRender(); }"); page.wait_for_timeout(300)
        m = js(page, """()=>{ const g=s=>{ const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect(), c=getComputedStyle(e); return {h:r.height, w:r.width, fs:parseFloat(c.fontSize), br:c.borderRadius, bg:c.backgroundColor, x1:r.right}; };
          const ref = (()=>{ const e=document.querySelector('.f input'); if(!e) return null; const c=getComputedStyle(e); return {br:c.borderRadius, bg:c.backgroundColor, fs:parseFloat(c.fontSize)}; })();
          return {date:g('[data-news-new-date]'), time:g('[data-news-new-time]'), kind:g('[data-news-new-kind]'), add:g('[data-news-add]'), ref, vw:innerWidth, over:document.documentElement.scrollWidth-innerWidth}; }""")
        check(f"{tag} 8 ช่องวันที่/เวลา/ประเภท สูง ≥ 40 · font ≥ 16", all(m[k] and m[k]["h"] >= 39.5 and m[k]["fs"] >= 16 for k in ("date", "time", "kind")), json.dumps(m))
        check(f"{tag} 8 ช่องกรอกสไตล์เดียวกับ .f input (มุมโค้ง · สีพื้น)", (m["ref"] is None) or (m["date"]["br"] == m["ref"]["br"] and m["date"]["bg"] == m["ref"]["bg"]), json.dumps([m["date"], m["ref"]]))
        check(f"{tag} 8 ปุ่ม ＋ เพิ่ม สูง ≥ 40", m["add"] and m["add"]["h"] >= 39.5, json.dumps(m["add"]))
        if w < 500:
            check(f"{tag} 8 390px: แถวใหม่ไม่ล้น · ปุ่มเพิ่มลงบรรทัดล่างเต็มกว้าง", m["over"] <= 0 and m["add"]["x1"] <= m["vw"] and m["add"]["w"] > m["date"]["w"], json.dumps(m))
        # เพิ่มวันข่าว + เวลาอัตโนมัติ (ของ ST1) + แถวที่บันทึกแล้ว
        js(page, "()=>{ const d=document.querySelector('[data-news-new-date]'); d.value='2026-10-14'; newsIn('date','2026-10-14'); }")
        t = js(page, "()=>document.querySelector('[data-news-new-time]').value")
        check(f"{tag} 8 เติมเวลาอัตโนมัติ (ST1) ยังทำงาน · CPI 2026-10-14 → 19:30 (ออมแสงสหรัฐ)", bool(re.match(r"^\d\d:\d\d$", t or "")), t)
        js(page, "()=>newsAdd()"); page.wait_for_timeout(300)
        js(page, "()=>{ const d=document.querySelector('[data-news-new-date]'); d.value='2026-10-14'; newsIn('date','2026-10-14'); newsAdd(); }"); page.wait_for_timeout(200)
        msg = txt(page, "[data-news-msg]") or ""
        check(f"{tag} 8 ซ้ำ = เตือน (ST1 เดิม)", "อยู่แล้ว" in msg, msg)
        rm = js(page, """()=>{ const r=document.querySelector('[data-news-row]'); if(!r) return null; const t=r.querySelector('[data-news-time]'), b=r.querySelector('[data-news-del]'), tr=t.getBoundingClientRect(), br=b.getBoundingClientRect(); return {th:tr.height, tfs:parseFloat(getComputedStyle(t).fontSize), bh:br.height, bw:br.width, nd:getComputedStyle(r.querySelector('.nd')).fontWeight, over:document.documentElement.scrollWidth-innerWidth}; }""")
        check(f"{tag} 8 แถวที่บันทึกแล้ว: ช่องเวลา สูง ≥ 40 font ≥ 16 · ปุ่ม × ≥ 36×36 · ไม่ล้น", rm and rm["th"] >= 39.5 and rm["tfs"] >= 16 and rm["bh"] >= 35.5 and rm["bw"] >= 35.5 and rm["over"] <= 0, json.dumps(rm))
        # แก้เวลา → บันทึกแล้ว → พิมพ์แถวใหม่ → หาย
        js(page, "()=>{ const i=document.querySelector('[data-news-time]'); i.value='20:00'; i.dispatchEvent(new Event('change',{bubbles:true})); }"); page.wait_for_timeout(300)
        check(f"{tag} 8 แก้เวลาแล้ว → 'บันทึกแล้ว'", (txt(page, "[data-news-msg]") or "") == "บันทึกแล้ว", txt(page, "[data-news-msg]"))
        shot(page, f"cx1-settings-news-{sfx}.png", "#newsSetSec")
        page.fill("[data-news-new-date]", "2026-11-04") if False else js(page, "()=>{ const t=document.querySelector('[data-news-new-time]'); t.value='1'; t.dispatchEvent(new Event('input',{bubbles:true})); }")
        check(f"{tag} 8 เริ่มพิมพ์แถวใหม่ → ข้อความ 'บันทึกแล้ว' หาย", (txt(page, "[data-news-msg]") or "") == "", txt(page, "[data-news-msg]"))
        check(f"{tag} 9 ไม่มี console error (ตั้งค่า)", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def launch_nocard(pw, w, h):
    doc = P43.base_doc(); doc["books"]["main"]["trades"] = []
    r = P43.launch(pw, w, h, cards={}, doc=doc)
    return r


def baseline_compare(pw, w, h, label):
    """เทียบ chip text ก่อน/หลัง CX1 — fixture เดียวกัน (ไฟล์ index.backup-pre-CX1.html)"""
    tag = f"[{ENGINE}/{label}]"
    cur = tests.now
    saved = P39.INDEX
    P39.INDEX = BACKUP
    try:
        browser, context, page, ce, pe, dialogs = launch_px(pw, w, h)
        try:
            old = (chip_texts(page, "main"), chip_texts(page, "fam"))
        finally: browser.close()
    finally: P39.INDEX = saved
    # UX2: ชิป data-c-f เปลี่ยนคำ f → FF (ที่เหลือเหมือนเดิมทุกตัวอักษร) — ปรับข้อความฝั่งไฟล์เก่าก่อนเทียบ
    old = tuple({k: (re.sub(r"^f ", "FF ", v) if k == "data-c-f" else v) for k, v in d.items()} for d in old)
    check(f"{tag} 5 ข้อความ/ตัวเลขทุกชิป (main + fam) เหมือนก่อน CX1 ทุกตัวอักษร (ยกเว้น f→FF · UX2)", old == cur and len(old[0]) >= 6, json.dumps([old, cur], ensure_ascii=False))


def static_tests():
    src = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("[static] .ccStat b ไม่มี var(--mono)", re.search(r"\.ccStat b\{[^}]*var\(--mono\)", src) is None)
    check("[static] data-c-* เดิมครบ", all(("data-c-" + k) in src for k in ("tank", "cashfree", "l2", "lshare", "gate", "f", "missing", "overcommit", "ffwarn", "expandall", "collapseall", "more")))


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
            baseline_compare(pw, w, h, label)
    static_tests()
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 53 / CX1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
