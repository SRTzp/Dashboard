#!/usr/bin/env python3
"""Hotfix acctSwitch — สลับบัญชีตอนมีงานค้าง (persistTimer / pendingLocalWrite) ต้องไม่ทำให้การแก้ของบัญชีเดิมหาย
เคส: 1) แก้ A → สลับ B ภายใน 350ms → server มีของ A และ B ไม่เสีย
     2) เขียนล้มเหลว (pendingLocalWrite=true) → สลับ → retry → A ขึ้น server
     3) สลับโดยไม่มีงานค้าง → dirtyBooks ไม่ถูกเพิ่ม · ไม่เขียนบัญชีเดิม
รัน: python3 run_tests_phase10.py (จำลอง Firestore ด้วย mock-firebase.js)
"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base

ENGINE = base.BROWSER_ENGINE
results = []
DOC = ["users", "testuid"]


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def server_book(page, id_):
    return page.evaluate("([p,i])=>{ const d=window.firebase.__mockDb.__getDoc(p); return d && d.books ? (d.books[i]||null) : null; }", [DOC, id_])


def fresh(pw, w, h):
    browser, context, page, ce, pe = base.launch_page(pw, w, h, base.DEFAULT_INDEX)
    page.wait_for_function("() => serverConfirmed && stateFromServer", timeout=5000)
    page.wait_for_timeout(900)   # ให้งานเขียนอัตโนมัติตอนโหลดจบก่อน
    page.evaluate("() => { dirtyBooks.clear(); }")
    return browser, context, page, ce, pe


def run(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    # ── เคส 1 ──
    browser, context, page, ce, pe = fresh(pw, w, h)
    act = page.evaluate("() => acctActive")
    other = page.evaluate("(a)=>acctList.find(x=>x.id!==a).id", act)
    fam_before = server_book(page, other)
    page.evaluate("([o])=>{ state._hotfixMark = 'A-edit'; schedulePersist(); acctSwitch(o); }", [other])   # ภายใน 350ms
    check(f"{tag} เคส1: สลับสำเร็จ (acctActive เปลี่ยน)", page.evaluate("() => acctActive") == other)
    check(f"{tag} เคส1: บัญชีเดิมอยู่ใน dirtyBooks ทันทีหลังสลับ", page.evaluate("(a)=>dirtyBooks.has(a)", act))
    page.wait_for_timeout(1200)
    sb = server_book(page, act)
    check(f"{tag} เคส1: server มีการแก้ของบัญชีเดิม (A)", bool(sb) and sb.get("_hotfixMark") == "A-edit", json.dumps(sb)[:200] if sb else "None")
    fb = server_book(page, other)
    check(f"{tag} เคส1: บัญชีปลายทาง (B) ไม่เสีย (ยังมีอยู่ · brokers/capital เท่าเดิม · ไม่มี mark ของ A)",
          bool(fb) and (fb.get("settings") or {}).get("brokers") == ((fam_before or {}).get("settings") or {}).get("brokers") and (fb.get("settings") or {}).get("capital") == ((fam_before or {}).get("settings") or {}).get("capital") and "_hotfixMark" not in fb, json.dumps(fb)[:200] if fb else "None")
    check(f"{tag} เคส1: dirtyBooks ว่างหลัง persist", page.evaluate("() => dirtyBooks.size") == 0)
    context.close(); browser.close()

    # ── เคส 2 ──
    browser, context, page, ce, pe = fresh(pw, w, h)
    act = page.evaluate("() => acctActive")
    other = page.evaluate("(a)=>acctList.find(x=>x.id!==a).id", act)
    page.evaluate("(p)=>window.firebase.__mockDb.__denyPath(p)", DOC)
    page.evaluate("() => { state._hotfixMark = 'A-fail'; schedulePersist(); }")
    page.wait_for_timeout(900)   # timer ยิง → set ถูกปฏิเสธ
    st = page.evaluate("() => ({pw: pendingLocalWrite, t: !!persistTimer})")
    check(f"{tag} เคส2: เขียนล้มเหลว → pendingLocalWrite=true · ไม่มี timer ค้าง", st["pw"] is True and st["t"] is False, json.dumps(st))
    page.evaluate("(o)=>acctSwitch(o)", other)
    check(f"{tag} เคส2: สลับแล้ว บัญชีเดิมอยู่ใน dirtyBooks", page.evaluate("(a)=>dirtyBooks.has(a)", act))
    page.evaluate("(p)=>window.firebase.__mockDb.__allowPath(p)", DOC)
    page.wait_for_timeout(1200)   # timer จาก acctSwitch → doPersist (retry)
    sb = server_book(page, act)
    check(f"{tag} เคส2: retry แล้ว A ขึ้น server", bool(sb) and sb.get("_hotfixMark") == "A-fail", json.dumps(sb)[:200] if sb else "None")
    context.close(); browser.close()

    # ── เคส 3 ──
    browser, context, page, ce, pe = fresh(pw, w, h)
    act = page.evaluate("() => acctActive")
    other = page.evaluate("(a)=>acctList.find(x=>x.id!==a).id", act)
    idle = page.evaluate("() => ({pw: pendingLocalWrite, t: !!persistTimer})")
    check(f"{tag} เคส3: ก่อนสลับไม่มีงานค้าง", idle == {"pw": False, "t": False}, json.dumps(idle))
    page.evaluate("""() => { window.__setCalls = []; const db = window.firebase.__mockDb; const orig = db.collection.bind(db);
        db.collection = (n)=>{ const c = orig(n); const od = c.doc.bind(c);
          c.doc = (id)=>{ const d = od(id); const os = d.set.bind(d); d.set = (data, o)=>{ window.__setCalls.push(o && o.mergeFields || []); return os(data, o); }; return d; };
          return c; }; }""")
    page.evaluate("(o)=>acctSwitch(o)", other)
    check(f"{tag} เคส3: สลับโดยไม่มีงานค้าง → dirtyBooks ไม่ถูกเพิ่ม", page.evaluate("() => dirtyBooks.size") == 0)
    page.wait_for_timeout(1000)
    calls = page.evaluate("() => window.__setCalls")
    wrote_old = any(("books." + act) in mf for mf in calls)
    check(f"{tag} เคส3: ไม่มีการเขียน books.<บัญชีเดิม> โดยไม่จำเป็น", not wrote_old, json.dumps(calls))
    context.close(); browser.close()


def main():
    with sync_playwright() as pw:
        run(pw, 1440, 900, "1440px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 10 / acctSwitch hotfix) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
