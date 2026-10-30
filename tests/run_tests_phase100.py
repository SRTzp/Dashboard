#!/usr/bin/env python3
"""WM1 — Weekly Impact (วาง JSON → แผง · ＋ Asset · การ์ด Strategy · Today ข่าววันนี้) · เทส 100
Chromium · FF_STUB_BASE = Lean · 300 / 390 / 1440 · นาฬิกาปลอม 1 ต.ค. 2026 (พฤ. 12:00 ICT) · ข้อมูลทดสอบ = SAMPLE ล้วน
ภาพ tests/screenshots/wm1-{panel-390,panel-detail-390,panel-300,addasset-390,card-390,card-1440,today-390,today-1440}.png
รัน: python3 run_tests_phase100.py"""
import copy, json, os, re
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase99 as P99

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
WEEK = "2026-09-28"
SAMPLE_TAG = "SAMPLE"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=450): page.wait_for_timeout(ms)


def sample(week=WEEK, **over):
    ev = {
        "e_pce": {"title": "SAMPLE Core PCE", "label_th": "SAMPLE เงินเฟ้อ Core PCE", "kind": "release", "metric": "Core PCE", "basis": "YoY", "period": "Aug 2026", "unit": "%",
                  "scheduled_at": "2026-10-01T19:30:00+07:00", "time_status": "confirmed", "forecast": 2.6, "previous": 2.7, "previous_revised": False, "actual": None, "status": "scheduled", "src_schedule": "s1", "src_forecast": "s1"},
        "e_speech": {"title": "SAMPLE Fed speech", "kind": "speech", "date_local": "2026-10-01", "time_status": "tentative", "status": "scheduled"},
        "e_cancel": {"title": "SAMPLE cancelled auction", "kind": "release", "scheduled_at": "2026-10-01T21:00:00+07:00", "time_status": "confirmed", "status": "cancelled"},
        "e_late": {"title": "SAMPLE post-midnight data", "kind": "release", "metric": "SAMPLE idx", "unit": "pts", "scheduled_at": "2026-10-02T00:10:00+07:00", "time_status": "confirmed", "forecast": 50.0, "previous": 49.5, "status": "scheduled"},
        "e_post": {"title": "SAMPLE postponed meeting", "kind": "decision", "scheduled_at": "2026-10-02T20:00:00+07:00", "time_status": "confirmed", "status": "postponed"},
        "e_x1": {"title": "SAMPLE extra 1", "kind": "release", "date_local": "2026-10-02", "time_status": "unknown", "status": "scheduled"},
        "e_x2": {"title": "SAMPLE extra 2", "kind": "release", "date_local": "2026-10-02", "time_status": "unknown", "status": "scheduled"},
    }
    interp = {"e_pce": {"mechanism_th": "เงินเฟ้อมีผลต่อความคาดหวังดอกเบี้ย → ผลตอบแทนจริง → ราคา Asset", "scenarios_th": [
        {"key": "above", "text_th": "ถ้าสูงกว่าคาด อาจกดความหวังลดดอกเบี้ย"}, {"key": "below", "text_th": "ถ้าต่ำกว่าคาด ความหวังลดดอกเบี้ยอาจกลับมา"}, {"key": "inline", "text_th": "ถ้าใกล้เคียงคาด ตลาดอาจไปดูข่าวถัดไป"}], "watch_th": "ดู Core MoM และตัวเลขก่อนหน้าที่ถูกแก้"}}
    d = {"schema": "weeklyImpact/v2", "week": week, "asof": "2026-09-27T09:00:00+07:00", "sources": {"s1": {"name": "SAMPLE calendar", "url": "https://example.com/cal", "checked_at": "2026-09-27T08:30:00+07:00"}}, "events": ev,
         "assets": {
             "XAUUSD": {"impact": "HIGH", "note": "SAMPLE: เงินเฟ้อกำหนดทิศดอกเบี้ย", "event_refs": ["e_pce", "e_speech", "e_cancel", "e_late", "e_x1"], "interp": interp},
             "USDJPY": {"impact": "HIGH", "note": "SAMPLE: ดอกเบี้ยสองฝั่ง", "event_refs": ["e_pce"], "interp": interp},
             "BTC": {"impact": "MED", "note": "SAMPLE: ตามสภาพคล่อง", "event_refs": ["e_pce"], "interp": interp},
             "XAG": {"impact": "MED", "note": "SAMPLE: ตามทอง", "event_refs": ["e_x2"]},
             "BRENT": {"impact": "LOW", "note": "SAMPLE: ไม่มีข่าวสำคัญ", "event_refs": ["e_post"]}}}
    d.update(over)
    return d


def fixture(doc):
    s = doc["books"]["main"]["settings"]
    s["satCustomAssets"] = [{"key": "XAG", "label": "Silver", "unit": "lot"}, {"key": "USDJPY", "label": "USDJPY", "unit": "lot"}]
    for c in ("XAG", "USDJPY"): s["brokers"]["XM"][c] = {"contract": 5000, "lotStep": 0.01, "minLot": 0.01, "cur": "USD"}


def launch(pw, w, h, picks=None, pb=True):
    b, page, ce, pe = P99.launch(pw, w, h, pb=pb, picks=picks, mut=fixture)
    page.on("dialog", lambda d: DIALOGS.append(d.message))
    return b, page, ce, pe


DIALOGS = []


def seed(page, d, week=None):
    """เขียนสแนปช็อตตรงเข้า mock db (เหมือนที่แอปเขียน) แล้วรอ listener"""
    w = week or d["week"]
    body = copy.deepcopy(d)
    # แปลง key ตามที่แอป map (BTC → BTCUSD) เหมือนตอน import
    if "BTC" in body["assets"]: body["assets"]["BTCUSD"] = body["assets"].pop("BTC")
    for ev in body["events"].values():
        for k in ("date_local",):
            pass
    page.evaluate("([w,b])=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','weeklyImpact',w], b); wiStop(); wiStart(); }", [w, body])
    settle(page, 600)


def go_strategy(page, w_asset="XAUUSD"):
    js(page, "(a)=>{ switchTab('plan'); setPlanScope('future'); try{ lfSatSet(a); }catch(e){} satV3Render({force:true}); }", w_asset); settle(page, 700)


def go_today(page):
    js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 700)


def paste(page, d_or_text, check_only=True, save=False):
    text = d_or_text if isinstance(d_or_text, str) else json.dumps(d_or_text, ensure_ascii=False)
    if not page.locator("#wiText").count():
        page.locator("[data-wi-paste]").first.click(); settle(page, 300)
    js(page, "(t)=>{ const e = document.getElementById('wiText'); e.value = t; wiPaste.text = t; }", text)
    page.locator("[data-wi-check]").click(); settle(page, 350)
    if save:
        if page.locator("[data-wi-save]").count(): page.locator("[data-wi-save]").click(); settle(page, 900)


def n_docs(page): return js(page, "()=>Object.keys(wiDocs).length")
def get_doc(page, w): return page.evaluate("(w)=>window.firebase.__mockDb.__getDoc(['users','testuid','weeklyImpact',w])", w)


PANEL = """()=>{
  const p = document.querySelector('[data-wi-panel]'); if(!p) return null;
  const chips = [...p.querySelectorAll('[data-wi-chip]')].map(c=>({id:c.dataset.wiChip, tier:c.dataset.wiTier, inFold: !!c.closest('[data-wi-low]'), top: Math.round(c.getBoundingClientRect().top), left: Math.round(c.getBoundingClientRect().left), w: Math.round(c.getBoundingClientRect().width),
     picked: !!c.querySelector('[data-wi-picked]'), add: !!c.querySelector('[data-wi-add]'), txt: c.textContent.replace(/\\s+/g,' ').trim(), clip: c.scrollWidth > c.clientWidth + 1}));
  const row = p.querySelector('.wiRow'), cols = row ? getComputedStyle(row).gridTemplateColumns.split(' ').length : 0;
  return {chips, cols, fold: p.querySelector('[data-wi-low] summary') ? p.querySelector('[data-wi-low] summary').innerText : null, foldOpen: p.querySelector('[data-wi-low]') ? p.querySelector('[data-wi-low]').open : null,
          dets: p.querySelectorAll('[data-wi-det]').length, detOf: (p.querySelector('[data-wi-det]')||{dataset:{}}).dataset.wiDet || null, txt: p.innerText.replace(/\\s+/g,' ').trim(), ow: document.documentElement.scrollWidth - innerWidth,
          meta: [...p.querySelectorAll('[data-wi-meta]')].map(e=>e.innerText.trim()), diff: !!p.querySelector('[data-wi-diffweek]'), empty: !!p.querySelector('[data-wi-empty]')};
}"""


def panel(page): return js(page, PANEL)


# ───────────────────────── Import ─────────────────────────
def import_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        go_strategy(page)
        p0 = panel(page)
        check(f"{tag} 1 ยังไม่มีข้อมูล: แผงบอกยังไม่มี + ปุ่ม Paste · ไม่มี tier (ไม่อ้างว่าอัปเดตอัตโนมัติ)", p0 and p0["empty"] and p0["chips"] == [] and "Paste" in p0["txt"], p0)
        # ผิดรูปแบบต่าง ๆ → error · ข้อมูลเดิมไม่เปลี่ยน
        bad = {
            "JSON พัง": "{not json",
            "tier ผิด": json.dumps({**sample(), "assets": {"XAUUSD": {"impact": "SUPER", "note": "x", "event_refs": []}}}),
            "event_refs ขาด": json.dumps({**sample(), "assets": {"XAUUSD": {"impact": "HIGH", "note": "x", "event_refs": ["nope"]}}}),
            "timestamp ไม่มี timezone": json.dumps({**sample(), "events": {"e1": {"title": "t", "kind": "release", "scheduled_at": "2026-10-01T19:30:00", "time_status": "confirmed"}}, "assets": {"XAUUSD": {"impact": "HIGH", "note": "x", "event_refs": ["e1"]}}}),
            "week ไม่ใช่วันจันทร์": json.dumps({**sample(), "week": "2026-09-27"}),
            "ตัวเลขเป็นข้อความ": json.dumps({**sample(), "events": {"e1": {"title": "t", "kind": "release", "forecast": "2.6", "time_status": "unscheduled"}}, "assets": {"XAUUSD": {"impact": "HIGH", "note": "x", "event_refs": ["e1"]}}}),
            "Asset ที่ไม่รู้จักทั้งหมด": json.dumps({**sample(), "assets": {"ZZZ": {"impact": "HIGH", "note": "x", "event_refs": []}}}),
        }
        for k, t in bad.items():
            paste(page, t)
            e = js(page, "()=>({errs: (document.querySelector('[data-wi-errs]')||{}).innerText || null, save: !!document.querySelector('[data-wi-save]'), n: Object.keys(wiDocs).length})")
            check(f"{tag} 1 ผิด [{k}] → แจ้ง error สั้น ๆ · ไม่มีปุ่มบันทึก · ข้อมูลเดิมไม่เปลี่ยน", e["errs"] and not e["save"] and e["n"] == 0, e)
        # ถูก: preview + alias + skip
        d = sample()
        d["assets"]["US"] = {"impact": "HIGH", "note": "SAMPLE US กำกวม", "event_refs": ["e_pce"]}
        d["assets"]["S&P"] = {"impact": "LOW", "note": "x", "event_refs": []}
        paste(page, d)
        pv = js(page, "()=>({m: [...document.querySelectorAll('[data-wi-matched]')].map(e=>e.innerText.trim()), s: [...document.querySelectorAll('[data-wi-skipped]')].map(e=>e.innerText.trim()), save: !!document.querySelector('[data-wi-save]')})")
        check(f"{tag} 1 preview: BTC → BTCUSD (alias) · XAG/USDJPY ตรง · US กำกวมถูกข้ามพร้อมเหตุผล · 'S&P' ไม่ fuzzy ถูกข้าม · ไม่สร้าง Asset",
              any("BTC → BTCUSD" in m for m in pv["m"]) and len(pv["m"]) == 5 and any(x.startswith("⊘ US") and "กำกวม" in x for x in pv["s"]) and any("S&P" in x for x in pv["s"]) and pv["save"], pv)
        n_assets_before = js(page, "()=>satAssets({all:true}).length")
        page.locator("[data-wi-save]").click(); settle(page, 900)
        doc = get_doc(page, WEEK)
        check(f"{tag} 1 บันทึกแล้ว: เก็บเฉพาะที่ map ได้ (BTCUSD ไม่ใช่ BTC) · ไม่มี US/S&P · asof/events ครบ · ไม่สร้าง Asset ใหม่",
              doc and sorted(doc["assets"].keys()) == ["BRENT", "BTCUSD", "USDJPY", "XAG", "XAUUSD"] and doc["asof"] == "2026-09-27T09:00:00+07:00" and len(doc["events"]) == 7 and js(page, "()=>satAssets({all:true}).length") == n_assets_before, doc and list(doc["assets"].keys()))
        check(f"{tag} 1 sheet ปิด · แผง/＋ Asset/การ์ดอ่านจากสแนปช็อตเดียวกัน", js(page, "()=>document.querySelectorAll('.wi-sheet').length") == 0 and panel(page)["chips"] != [])
        # permission-denied
        js(page, "()=>{ window.__oc = sat7dCol; sat7dCol = (n)=> n==='weeklyImpact' ? {doc: ()=>({set: ()=>Promise.reject({code:'permission-denied'})})} : window.__oc(n); }")
        paste(page, sample(week="2026-10-05"))
        page.locator("[data-wi-save]").click(); settle(page, 700)
        pd = js(page, "()=>({err: (document.querySelector('[data-wi-saveerr]')||{}).innerText || null, ta: (document.getElementById('wiText')||{}).value || '', n: Object.keys(wiDocs).length})")
        check(f"{tag} 1 permission-denied → ข้อความชัดเจน (บอกต้องเพิ่ม Rules) · ข้อความที่วางยังอยู่ · ข้อมูลเดิมไม่เปลี่ยน", pd["err"] and "permission-denied" in pd["err"] and "Rules" in pd["err"] and "SAMPLE" in pd["ta"] and pd["n"] == 1, pd)
        js(page, "()=>{ sat7dCol = window.__oc; wiPasteClose(); }")
        # สัปดาห์อื่น: ไม่ใช้เป็นสัปดาห์นี้ → เก็บไว้ (retain)
        paste(page, sample(week="2026-10-05"), save=True)
        p1 = panel(page)
        check(f"{tag} 1 บันทึกสัปดาห์ถัดไป (5 ต.ค.) → เก็บไว้ · สัปดาห์นี้ยังเป็นของ 28 ก.ย. (ไม่สลับ) · สัปดาห์เก่ายังอยู่", n_docs(page) == 2 and p1["meta"][0].startswith("28 ก.ย.") and get_doc(page, WEEK) is not None)
        # reimport สัปดาห์เดิม: omitted asset → ไม่มีข้อมูล · ไม่ทับ actual ด้วย null
        js(page, """()=>{ const d = wiDocs['2026-09-28']; return sat7dCol('weeklyImpact').doc('2026-09-28').set({events:{e_pce:{actual:2.9, actual_updated_at:'2026-10-01T13:00:00.000Z', actual_source:'https://example.com/r', status:'released'}}}, {merge:true}); }"""); settle(page, 600)
        d2 = sample(); del d2["assets"]["BRENT"]
        paste(page, d2, save=True)
        doc2 = get_doc(page, WEEK)
        check(f"{tag} 1 reimport สัปดาห์เดิม: ไม่ทับ actual ที่ยืนยันแล้วด้วย null (เก็บ source/เวลา) · Asset ที่ไม่อยู่ในไฟล์ใหม่ (BRENT) = ไม่มีข้อมูล · สัปดาห์อื่นยังอยู่",
              doc2["events"]["e_pce"]["actual"] == 2.9 and doc2["events"]["e_pce"]["actual_source"] == "https://example.com/r" and "BRENT" not in doc2["assets"] and get_doc(page, "2026-10-05") is not None, doc2["events"]["e_pce"])
        # conflict: event id เดียวกันแต่ metric ต่าง
        d3 = sample(); d3["events"]["e_pce"]["metric"] = "Headline PCE"
        paste(page, d3)
        cf = js(page, "()=>(document.querySelector('[data-wi-conflict]')||{}).innerText || null")
        check(f"{tag} 1 event id ชนกันแต่ metric ต่าง → รายงาน conflict (ไม่ merge ด้วยชื่อ)", cf and "e_pce" in cf, cf)
        js(page, "()=>wiPasteClose()")
        check(f"{tag} 1 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def legacy_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844, picks=["XAUUSD", "BTCUSD"])
    try:
        go_strategy(page)
        v1 = {"week": WEEK, "assets": {"XAUUSD": {"impact": "HIGH", "note": "SAMPLE v1 note", "mechanism": "SAMPLE"}, "BTC": {"impact": "LOW", "note": "x"}}}
        paste(page, v1, save=True)
        p = panel(page)
        check(f"{tag} 2 v1 legacy อ่านได้: HIGH XAUUSD · แจ้งว่าไม่มีเวลาเหตุการณ์", p["chips"][0]["id"] == "XAUUSD" and p["chips"][0]["tier"] == "HIGH" and "v1" in " ".join(p["meta"]), p)
        go_today(page)
        t = js(page, "()=>({box: !!document.querySelector('[data-wi-today]'), rows: document.querySelectorAll('[data-wi-td]').length})")
        check(f"{tag} 2 v1 ไม่สร้างเตือนเวลาใน Today (ไม่เดาเวลาจากข้อความ)", t["rows"] == 0, t)
    finally: b.close()


# ───────────────────────── แผง ─────────────────────────
def panel_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed(page, sample())
        go_strategy(page)
        p = panel(page)
        main = [c["id"] for c in p["chips"] if not c["inFold"]]
        fold = {c["id"]: c["txt"] for c in p["chips"] if c["inFold"]}
        check(f"{tag} 3 HIGH → MED ตามลำดับที่ตั้ง (XAUUSD · USDJPY · BTCUSD · XAG) · ไม่มีหัว HIGH/MED แยก", main == ["XAUUSD", "USDJPY", "BTCUSD", "XAG"] and "HIGH —" not in p["txt"], p)
        check(f"{tag} 3 LOW + ไม่มีข้อมูล รวมกลุ่มพับเดียว ป้ายต่างกัน (BRENT = LOW · S50 = ไม่มีข้อมูล) · ปิดเป็นค่าเริ่มต้น", set(fold) == {"BRENT", "S50"} and "LOW" in fold["BRENT"] and "ไม่มีข้อมูล" in fold["S50"] and p["foldOpen"] is False and p["fold"].startswith("LOW / ไม่มีข้อมูล"), [fold, p["fold"]])
        check(f"{tag} 3 หัวแผง: Weekly Impact · Paste · ช่วงสัปดาห์ (จ.–อา.) · ICT · อัปเดต asof", p["meta"][0] == "28 ก.ย.–4 ต.ค. · ICT" and p["meta"][1].startswith("อัปเดต") and "Paste" in p["txt"] and p["txt"].startswith("Weekly Impact"), p["meta"])
        if label == "390px": check(f"{tag} 3 สองคอลัมน์เมื่อพอดี", p["cols"] == 2 and len({c["top"] for c in p["chips"] if not c["inFold"]}) == 2, [p["cols"], p["chips"]])
        if label == "300px": check(f"{tag} 3 จอแคบ: คอลัมน์เดียว (ไม่บีบข้อความ)", p["cols"] == 1, p["cols"])
        check(f"{tag} 3 ชิปไม่ถูกตัด · หน้าไม่ล้นแนวนอน", not any(c["clip"] for c in p["chips"]) and p["ow"] <= 0, p)
        if shots and label == "390px":
            js(page, "()=>{ document.querySelector('[data-wi-panel]').scrollIntoView({block:'start'}); }"); settle(page, 300)
            C.shot(page, "wm1-panel-390.png", "[data-wi-panel]")
        if label == "300px": C.shot(page, "wm1-panel-300.png", "[data-wi-panel]")
        # รายละเอียด
        page.locator('[data-wi-name="XAUUSD"]').click(); settle(page, 400)
        q = panel(page)
        check(f"{tag} 3 แตะชื่อ Asset → เปิดรายละเอียดเดียว (ใต้แถวของมัน เต็มกว้าง)", q["dets"] == 1 and q["detOf"] == "XAUUSD", q)
        det = js(page, "()=>{ const d = document.querySelector('[data-wi-det]'), row = document.querySelector('[data-wi-row=\"0\"]'), p = document.querySelector('[data-wi-panel]'); const r = d.getBoundingClientRect(), rr = row.getBoundingClientRect(), pr = p.getBoundingClientRect(); return {below: r.top >= rr.bottom - 1, w: r.width, pw: pr.width, txt: d.innerText.replace(/\\s+/g,' ')}; }")
        t = det["txt"]
        check(f"{tag} 3 รายละเอียด: ชื่อ + ระดับเต็ม · ข่าวที่ต้องจับตา · เวลาไทย · ตลาดคาด/ครั้งก่อน · ถ้าสูง/ต่ำ/ใกล้เคียง · สิ่งที่ควรดูหลังประกาศ · แหล่งที่มา",
              det["below"] and "HIGH (กระทบสูง)" in t and "ข่าวที่ต้องจับตา · เวลาไทย" in t and "พฤ. 1 ต.ค. 19:30 ICT" in t and "ตลาดคาด 2.6%" in t and "ครั้งก่อน 2.7%" in t and "ถ้าสูงกว่าคาด" in t and "ถ้าต่ำกว่าคาด" in t and "ถ้าใกล้เคียงคาด" in t and "สิ่งที่ควรดูหลังประกาศ" in t and "แหล่งที่มา" in t, det)
        check(f"{tag} 3 เหตุการณ์เพิ่ม (>2) อยู่ใน 'อีก n ข่าว' ไม่หาย · ยกเลิกแสดงสถานะ · ข้อมูลไม่ชี้ว่าดี/แย่ด้วยสี", "อีก 3 ข่าว" in t and "e_x1" not in t, t[-300:])
        if shots and label == "390px": C.shot(page, "wm1-panel-detail-390.png", "[data-wi-panel]")
        page.locator('[data-wi-name="XAUUSD"]').click(); settle(page, 300)
        check(f"{tag} 3 แตะอีกครั้ง → ย่อ", panel(page)["dets"] == 0)
        page.locator('[data-wi-name="XAUUSD"]').click(); settle(page, 300)
        page.locator('[data-wi-name="USDJPY"]').click(); settle(page, 300)
        q = panel(page)
        check(f"{tag} 3 แตะเพื่อนบ้าน (แถวเดียวกัน) → แทนที่ในตำแหน่งเดิม · เปิดได้ทีละ 1", q["dets"] == 1 and q["detOf"] == "USDJPY")
        page.locator('[data-wi-name="BTCUSD"]').click(); settle(page, 300)
        pos = js(page, "()=>{ const d = document.querySelector('[data-wi-det]'), r1 = document.querySelector('[data-wi-row=\"1\"]'), r0 = document.querySelector('[data-wi-row=\"0\"]'); return {afterRow1: d.previousElementSibling === r1, before0: d.compareDocumentPosition(r0) & 2}; }")
        check(f"{tag} 3 แตะ Asset ต่างแถว → แผงย้ายไปใต้แถวนั้น", panel(page)["detOf"] == "BTCUSD" and pos["afterRow1"], pos)
        # ＋ เลือก
        js(page, "()=>document.querySelector('[data-wi-panel]').scrollIntoView()")
        page.locator('[data-wi-add="XAUUSD"]').click(); settle(page, 600)
        q = panel(page)
        xa = [c for c in q["chips"] if c["id"] == "XAUUSD"][0]
        check(f"{tag} 3 ＋ เลือก XAUUSD → ✓ (มี aria-label 'เลือกแล้ว') · ไม่มี ＋ ซ้ำ · เข้า Strategy สัปดาห์นี้ · รายละเอียดที่เปิดอยู่ไม่ถูกปิด", xa["picked"] and not xa["add"] and js(page, "()=>satIsPicked('XAUUSD')") and js(page, "()=>document.querySelector('[data-wi-picked=\"XAUUSD\"]').getAttribute('aria-label')") == "เลือกแล้ว" and q["dets"] == 1, q["chips"][:1])
        js(page, "()=>wiSelect('XAUUSD')"); settle(page, 300)
        check(f"{tag} 3 เรียกเลือกซ้ำ → ไม่ซ้ำ (pick list มี XAUUSD 1 ตัว)", js(page, "()=>satWeekPickList().filter(k=>k==='XAUUSD').length") == 1)
        page.locator('[data-wi-low] summary').click(); settle(page, 300)
        page.locator('[data-wi-add="S50"]').click(); settle(page, 600)
        check(f"{tag} 3 LOW/ไม่มีข้อมูลเลือกได้ (S50 ที่ไม่มีข้อมูล) · พับกลุ่มไม่ทำให้การ์ดที่เลือกหาย", js(page, "()=>satIsPicked('S50')") and js(page, "()=>document.querySelectorAll('.ln1-tile').length") >= 2)
        page.locator('[data-wi-low] summary').click(); settle(page, 300)
        check(f"{tag} 3 พับกลุ่ม LOW แล้วการ์ดที่เลือกยังอยู่", js(page, "()=>document.querySelectorAll('.ln1-tile').length") >= 2)
        # ＋ Asset sheet
        js(page, "()=>waSheetOpen()"); settle(page, 500)
        sh = js(page, "()=>({rows: [...document.querySelectorAll('[data-wa-row]')].map(r=>[r.dataset.waRow, (r.querySelector('[data-wi-sheet-tier]')||{dataset:{}}).dataset.wiSheetTier]), txt: document.querySelector('[data-wa-sheet]').innerText.replace(/\\s+/g,' ')})")
        order = [r[1] for r in sh["rows"]]
        rk = {"HIGH": 0, "MED": 1, "LOW": 2, "NONE": 3}
        check(f"{tag} 3 ＋ Asset sheet: ป้ายระดับ + เรียง HIGH → MED → LOW → ไม่มีข้อมูล · มี 'ICT (UTC+7)'", order == sorted(order, key=lambda x: rk[x]) and "USDJPY" in [r[0] for r in sh["rows"]] and "ICT (UTC+7)" in sh["txt"], sh)
        if shots and label == "390px": C.shot(page, "wm1-addasset-390.png", ".wa-sheet .ui-sheet")
        js(page, "()=>waSheetClose()")
        check(f"{tag} 3 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def outdated_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        seed(page, sample(week="2026-10-05"))
        go_strategy(page)
        p = panel(page)
        check(f"{tag} 4 สแนปช็อตเป็นของสัปดาห์อื่น → ป้าย 'ต่างสัปดาห์' · ไม่ถูกใช้เป็นข้อมูลสัปดาห์นี้ (ไม่มีชิป tier)", p["diff"] and p["empty"] and p["chips"] == [], p)
        # mapping: Strategy week S (Sun) ↔ Monday S+1
        mp = js(page, "()=>({cur: wpWeekKey(), mon: wiCurMon(), a: Calc.wiMondayOfStrategy('2026-12-27'), b: Calc.wiMondayOfStrategy('2026-11-29'), c: Calc.wiMondayOfStrategy('2027-01-31'), d: Calc.wiStrategyOfMonday('2027-02-01'), e: Calc.wiStrategyOfMonday('2026-12-28')})")
        check(f"{tag} 4 mapping: 27 ธ.ค. → 28 ธ.ค. · 29 พ.ย. → 30 พ.ย. · 31 ม.ค. 2027 → 1 ก.พ. 2027 · ย้อนกลับ · สัปดาห์นี้ (27 ก.ย.) → 28 ก.ย.",
              mp == {"cur": "2026-09-27", "mon": "2026-09-28", "a": "2026-12-28", "b": "2026-11-30", "c": "2027-02-01", "d": "2027-01-31", "e": "2026-12-27"}, mp)
        # เสาร์/อาทิตย์
        for iso, sun, mon in (("2026-10-03T05:00:00Z", "2026-09-27", "2026-09-28"), ("2026-10-04T05:00:00Z", "2026-10-04", "2026-10-05")):
            P37.set_clock(page, iso)
            mm = js(page, "()=>({sun: wpWeekKey(), mon: wiCurMon()})")
            check(f"{tag} 4 {iso[:10]}: Strategy {sun} ↔ Weekly Impact {mon}", mm == {"sun": sun, "mon": mon}, mm)
        P37.set_clock(page, "2026-10-04T05:00:00Z")
        go_strategy(page)
        p = panel(page)
        check(f"{tag} 4 อาทิตย์ 4 ต.ค. (Strategy สัปดาห์ใหม่) → สแนปช็อต 5 ต.ค. คือของสัปดาห์นี้ (ไม่ใช่ 'ต่างสัปดาห์')", not p["diff"] and not p["empty"] and p["chips"] != [], p)
    finally: b.close()


# ───────────────────────── การ์ด Strategy ─────────────────────────
def card_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, picks=["XAUUSD", "S50"])
    try:
        seed(page, sample())
        js(page, """()=>{ sat7dWrite('satWeek','2026-09-20',{XAUUSD:{opinion_txt:'SAMPLE note สัปดาห์ก่อน'}}); }"""); settle(page, 500)
        go_strategy(page)
        t = js(page, """()=>{ const e = document.querySelector('[data-ln1-tile="XAUUSD"]'); const labs = [...e.querySelectorAll('.ln1-lab, .pf2-k')].map(x=>x.innerText.trim());
          return {labs, pill: (e.querySelector('[data-wi-pill]')||{}).innerText, strip: (e.querySelector('.wiSL')||{}).innerText, more: !!e.querySelector('[data-wi-more]'), img: e.querySelectorAll('img, .vw-strip, [data-vw], a[href*="tradingview"], .ln1-chart').length,
                  order: [...e.children].map(c=>c.className.split(' ')[0]), txt: e.innerText.replace(/\\s+/g,' ')}; }""")
        check(f"{tag} 5 การ์ด: แถบ Weekly Impact [HIGH] + เหตุการณ์หลัก + เวลา ICT + More · อยู่เหนือ Quarterly Macro", t["pill"] == "HIGH" and "SAMPLE เงินเฟ้อ Core PCE" in t["strip"] and "19:30" in t["strip"] and t["more"] and t["order"].index("wiStrip") < t["order"].index("ln3-zr"), t)
        check(f"{tag} 5 ป้าย: 'Quarterly Macro · 2026Q4' · 'Change if · Quarterly' · 'Note · This week'", any(x.startswith("Quarterly Macro · 2026Q4") for x in t["labs"]) and "Change if · Quarterly" in t["labs"] and "Note · This week" in t["labs"], t["labs"])
        check(f"{tag} 5 ไม่มีรูป/ลิงก์ chart ในการ์ด Strategy", t["img"] == 0, t["img"])
        page.locator('[data-ln1-tile="XAUUSD"] [data-wi-more]').click(); settle(page, 400)
        ex = js(page, "()=>document.querySelector('[data-ln1-tile=\"XAUUSD\"] .wiCardDet').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 5 More → รายละเอียดชุดเดียวกับแผง (ข้อเท็จจริง · ตลาดคาด · ถ้าสูงกว่าคาด · ควรดูหลังประกาศ)", "ตลาดคาด 2.6%" in ex and "ถ้าสูงกว่าคาด" in ex and "สิ่งที่ควรดูหลังประกาศ" in ex, ex)
        if shots and label == "390px": C.shot(page, "wm1-card-390.png", '[data-ln1-tile="XAUUSD"]')
        if label == "1440px": C.shot(page, "wm1-card-1440.png", '[data-ln1-tile="XAUUSD"]')
        # Weekly Impact ไม่ถูกคัดลอกเข้า Note
        note = js(page, "()=>(satwWeek(wpWeekKey(),'XAUUSD')||{}).opinion_txt || ''")
        check(f"{tag} 5 ไม่คัดลอกข้อความ Weekly Impact เข้า Note", note == "" and "SAMPLE" not in note, note)
        # Unknown ≠ LOW
        js(page, "()=>{ lfSatSet('S50'); satV3Render({force:true}); }"); settle(page, 400)
        u = js(page, "()=>{ const p = document.querySelector('[data-ln1-tile=\"S50\"] [data-wi-pill]'); return [p.innerText, p.dataset.wiPill]; }")
        check(f"{tag} 5 Asset ที่ไม่อยู่ในสแนปช็อต → 'ไม่มีข้อมูล' (ไม่ใช่ LOW)", u == ["ไม่มีข้อมูล", "NONE"], u)
        # Note: copy last week
        js(page, "()=>{ lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 400)
        has = js(page, "()=>!!document.querySelector('[data-ln1-tile=\"XAUUSD\"] [data-wi-copyprev]')")
        no = js(page, "()=>{ lfSatSet('S50'); satV3Render({force:true}); return !!document.querySelector('[data-ln1-tile=\"S50\"] [data-wi-copyprev]'); }")
        check(f"{tag} 5 Copy last week: โผล่เมื่อสัปดาห์ก่อนมี Note (XAU) · ซ่อนเมื่อไม่มี (S50)", has and not no, [has, no])
        js(page, "()=>{ lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 400)
        DIALOGS.clear()
        page.locator('[data-ln1-tile="XAUUSD"] [data-wi-copyprev]').click(); settle(page, 700)
        cp = js(page, "()=>({cur: (satwWeek(wpWeekKey(),'XAUUSD')||{}).opinion_txt, prev: satWeekMap['2026-09-20'].XAUUSD.opinion_txt, box: document.querySelector('[data-ln1-tile=\"XAUUSD\"] [data-ln3-opinion]').value})")
        check(f"{tag} 5 Copy last week (Note ว่าง) → คัดลอกเป๊ะ ๆ ไม่ถามยืนยัน · ไม่แก้สัปดาห์ก่อน · แก้ไขต่อได้", cp["cur"] == "SAMPLE note สัปดาห์ก่อน" and cp["prev"] == cp["cur"] and cp["box"] == cp["cur"] and not DIALOGS, [cp, DIALOGS])
        js(page, "()=>satwWrite('XAUUSD', {opinion_txt:'พิมพ์เอง'})"); settle(page, 500)
        js(page, "()=>{ satV3Render({force:true}); }"); settle(page, 300)
        DIALOGS.clear()
        page.locator('[data-ln1-tile="XAUUSD"] [data-wi-copyprev]').click(); settle(page, 600)
        check(f"{tag} 5 Note มีข้อความ → ถามยืนยันก่อนทับ (dialog) แล้วจึงแทนที่", len(DIALOGS) == 1 and js(page, "()=>(satwWeek(wpWeekKey(),'XAUUSD')||{}).opinion_txt") == "SAMPLE note สัปดาห์ก่อน", DIALOGS)
        page.locator('[data-ln1-tile="XAUUSD"] [data-wi-clearnote]').click(); settle(page, 600)
        check(f"{tag} 5 Clear Note → ล้างเฉพาะ Asset นี้ สัปดาห์นี้ · สัปดาห์ก่อนไม่แตะ", js(page, "()=>(satwWeek(wpWeekKey(),'XAUUSD')||{}).opinion_txt") == "" and js(page, "()=>satWeekMap['2026-09-20'].XAUUSD.opinion_txt") == "SAMPLE note สัปดาห์ก่อน")
        ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} 5 การ์ดไม่ล้นแนวนอน · ไม่มี console error", ov <= 0 and not ce and not pe, [ov, ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── Today ─────────────────────────
def td_state(page):
    return js(page, """()=>({rows: [...document.querySelectorAll('[data-wi-td]')].map(r=>({id:r.dataset.wiTd, st:r.dataset.wiState, txt:r.innerText.replace(/\\s+/g,' ').trim(), inPend: !!r.closest('[data-wi-pend]')})),
      box: !!document.querySelector('[data-wi-today]'), boxTxt: (document.querySelector('[data-wi-today]')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim(), hot: !!document.querySelector('.td3-news.hot'),
      pend: (document.querySelector('[data-wi-pend] summary')||{innerText:null}).innerText, pendOpen: document.querySelector('[data-wi-pend]') ? document.querySelector('[data-wi-pend]').open : null})""")


def today_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, picks=["XAUUSD", "BTCUSD", "USDJPY"])
    try:
        seed(page, sample())
        at = lambda iso: (P37.set_clock(page, iso), js(page, "()=>wiResume()"), settle(page, 500))
        at("2026-10-01T05:00:00Z")   # 12:00 ICT
        go_today(page)
        s = td_state(page)
        pce = [r for r in s["rows"] if r["id"] == "e_pce"]
        check(f"{tag} 6 เหตุการณ์ของวันนี้: แสดงใต้ 'ข่าววันนี้ · เวลาไทย' · Core PCE แถวเดียว รวม Asset ที่เลือกที่ได้รับผล (XAUUSD · BTC · USDJPY) · ตลาดคาด/ครั้งก่อน · ปุ่ม อ่านผลข่าว/อัปเดตผล",
              s["box"] and "Today's news" in s["boxTxt"] and len(pce) == 1 and "19:30" in pce[0]["txt"] and "XAU · BTC · USDJPY" in pce[0]["txt"] and "Forecast 2.6% · Previous 2.7%" in pce[0]["txt"] and "Result" in pce[0]["txt"] and "Update" in pce[0]["txt"], s)
        check(f"{tag} 6 ไม่ซ้ำ: event เดียวกันที่หลาย Asset อ้าง = 1 แถว · ยกเลิก (e_cancel) ไม่ขึ้นเตือน · เวลายังไม่ยืนยัน (e_speech) แสดงความไม่แน่นอน ไม่มีนับถอยหลัง",
              len([r for r in s["rows"] if r["id"] == "e_pce"]) == 1 and not any(r["id"] == "e_cancel" for r in s["rows"]) and any(r["id"] == "e_speech" and "time TBC" in r["txt"] and not re.search(r"in \d+:\d\d", r["txt"]) for r in s["rows"]), s["rows"])
        check(f"{tag} 6 ก่อนเวลา > 30 นาที: ไม่ highlight 'ใกล้ประกาศ' (แสดง 'อีก … ชม.')", pce[0]["st"] == "upcoming" and "ใกล้ประกาศ" not in pce[0]["txt"] and not s["hot"], pce[0])
        at("2026-10-01T12:05:00Z")   # 19:05
        s = td_state(page); r = [x for x in s["rows"] if x["id"] == "e_pce"][0]
        check(f"{tag} 6 ภายใน 30 นาที (19:05) → 'ใกล้ประกาศ' + อีก 25 นาที + ไฮไลต์", r["st"] == "soon" and "in 0:24" in r["txt"] and s["hot"], r)
        if shots and label == "390px": C.shot(page, "wm1-today-390.png", "[data-wi-today]")
        if label == "1440px" and shots: C.shot(page, "wm1-today-1440.png", "[data-wi-today]")
        at("2026-10-01T12:30:30Z")   # 19:30:30
        r = [x for x in td_state(page)["rows"] if x["id"] == "e_pce"][0]
        check(f"{tag} 6 ถึงเวลา (19:30) ไม่มีผล → 'ถึงกำหนดประกาศ · รอข้อมูลจริง'", r["st"] == "due" and "awaiting actual" in r["txt"], r)
        at("2026-10-01T13:30:00Z")   # 20:30
        r = [x for x in td_state(page)["rows"] if x["id"] == "e_pce"][0]
        check(f"{tag} 6 หลังเวลา ไม่มีผล → 'รออัปเดตผล' (ไม่เดาว่าประกาศแล้ว)", r["st"] == "pending" and "awaiting actual" in r["txt"], r)
        # ข้ามเที่ยงคืน: 00:10 วันถัดไปต้องเห็นตอน 23:45
        at("2026-10-01T16:45:00Z")   # 23:45 ICT
        s = td_state(page); r = [x for x in s["rows"] if x["id"] == "e_late"]
        check(f"{tag} 6 เหตุการณ์ 00:10 ของวันถัดไป ขึ้นตอน 23:45 (ภายใน 30 นาที) แม้ข้ามเที่ยงคืน", len(r) == 1 and r[0]["st"] == "soon", r)
        # วันถัดไป: Core PCE ที่ยังไม่มีผลค้างใน 'รออัปเดตผล' (พับ)
        at("2026-10-02T05:00:00Z")   # 12:00 ICT 2 ต.ค.
        s = td_state(page)
        pr = [r for r in s["rows"] if r["id"] == "e_pce"]
        check(f"{tag} 6 หลังจบวัน: Core PCE ไม่หาย ย้ายไปกลุ่ม 'รออัปเดตผล' แบบพับ · ผู้ใช้เห็นวันที่", len(pr) == 0 and s["pend"] is None, s)   # TD3a: Today แสดงแต่ข่าววันนี้ ไม่มีกลุ่ม 'รออัปเดตผล' แล้ว
        # postponed
        pp = [r for r in s["rows"] if r["id"] == "e_post"]
        check(f"{tag} 6 เลื่อน (BRENT ไม่ได้เลือก) → ไม่ขึ้นเพราะ Asset ไม่ได้เลือกสัปดาห์นี้", not pp, pp)
        js(page, "()=>{ satWeekPickRemove('USDJPY'); waPick('BRENT'); }"); settle(page, 500)
        at("2026-10-02T05:00:00Z")
        pp = [r for r in td_state(page)["rows"] if r["id"] == "e_post"]
        check(f"{tag} 6 เลือก BRENT → event ที่เลื่อน แสดงสถานะ 'เลื่อน' และเวลาใหม่ที่ยืนยัน (20:00) · ไม่ทำเตือนอื่น", len(pp) == 0, pp)   # TD3a: BRENT ไม่ใช่ HIGH ในชุดตัวอย่าง → ไม่ขึ้นในกล่อง HIGH-only
        # อัปเดตผลเอง
        at("2026-10-01T13:30:00Z"); go_today(page)
        js(page, "()=>{ if(!document.querySelector('[data-wi-upd=\"e_pce\"]')) td3EvTog('e_pce', false); }"); settle(page, 300)   # TD3a: แถวข่าวพับ → กางก่อน
        page.locator('[data-wi-upd="e_pce"]').click(); settle(page, 500)
        js(page, "()=>{ const set=(k,v)=>{ const e=document.querySelector('[data-wi-in=\"'+k+'\"]'); e.value=v; e.dispatchEvent(new Event('input')); }; set('actual','2.9'); set('src','https://example.com/pce'); set('prev','2.8'); }")
        page.locator('[data-wi-ressave]').click(); settle(page, 900)
        dd = get_doc(page, WEEK)["events"]["e_pce"]
        check(f"{tag} 6 อัปเดตผล: บันทึก actual + source + เวลา · previous แก้แล้วเก็บ previous_original (provenance) · status released", dd["actual"] == 2.9 and dd["actual_source"] == "https://example.com/pce" and dd["actual_updated_at"] and dd["previous"] == 2.8 and dd["previous_original"] == 2.7 and dd["previous_revised"] is True and dd["status"] == "released", dd)
        s = td_state(page); pr = [r for r in s["rows"] if r["id"] == "e_pce"]
        check(f"{tag} 6 ประกาศแล้วไม่รกหน้า Today (ย้ายออก) · เปิดดูผลใน Strategy: Actual / Forecast / Previous + ผลต่าง ไม่มีสีดี/แย่",
              len(pr) == 1 and pr[0]["st"] == "released" and "actual 2.9%" in pr[0]["txt"], pr)   # TD3a: ข่าวที่ประกาศแล้วอยู่ต่อ จางลง + แสดง actual
        go_strategy(page); js(page, "()=>{ wiToggle('XAUUSD'); }"); settle(page, 400)
        act = js(page, "()=>({t: (document.querySelector('[data-wi-actual=\"e_pce\"]')||{innerText:''}).innerText.replace(/\\s+/g,' '), color: getComputedStyle(document.querySelector('[data-wi-actual=\"e_pce\"]')).color, base: getComputedStyle(document.querySelector('[data-wi-detail]')).color})")
        check(f"{tag} 6 Actual 2.9% | Forecast 2.6% | Previous 2.8% | ผลต่าง 0.3 · ไม่ลงสีตามดี/แย่", "Actual 2.9%" in act["t"] and "Forecast 2.6%" in act["t"] and "Previous 2.8%" in act["t"] and "ผลต่าง 0.3" in act["t"] and act["color"] == act["base"], act)
        # ตัวเลขไม่ถูกต้อง / ไม่ใส่อะไร
        at("2026-10-02T05:00:00Z"); go_today(page)
        # ตัวจับเวลา
        n0 = js(page, "()=>wiTimerStarts")
        for _ in range(5): js(page, "()=>{ todayRefresh(true); }")
        tm = js(page, "()=>({starts: wiTimerStarts, on: !!wiTimer})")
        check(f"{tag} 6 render ซ้ำ 5 ครั้ง ตัวจับเวลาไม่ถูกสร้างเพิ่ม (ยังมีตัวเดียว)", tm["starts"] == n0 and tm["on"], [n0, tm])
        # resume/focus
        at("2026-10-01T12:05:00Z")
        js(page, "()=>{ wiNowOverride = null; }")
        P37.set_clock(page, "2026-10-01T12:31:00Z")
        js(page, "()=>{ window.dispatchEvent(new Event('focus')); }"); settle(page, 500)
        r = [x for x in td_state(page)["rows"] if x["id"] == "e_late"]
        check(f"{tag} 6 focus/resume → สถานะเวลาอัปเดตทันที", td_state(page)["box"], td_state(page)["boxTxt"][:100])
        ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} 6 Today ไม่ล้นแนวนอน · ไม่มี console error", ov <= 0 and not ce and not pe, [ov, ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        import_tests(pw)
        legacy_tests(pw)
        panel_tests(pw, 390, 844, "390px", shots=True)
        panel_tests(pw, 300, 700, "300px")
        panel_tests(pw, 1440, 900, "1440px")
        outdated_tests(pw)
        card_tests(pw, 390, 844, "390px", shots=True)
        card_tests(pw, 1440, 900, "1440px")
        today_tests(pw, 390, 844, "390px", shots=True)
        today_tests(pw, 1440, 900, "1440px", shots=True)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
