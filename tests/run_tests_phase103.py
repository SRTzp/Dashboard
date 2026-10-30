#!/usr/bin/env python3
"""PF3 — weeklyImpact/v2 (kind event · status ครบ · previous_period · src_actual · source_refs · label_th) · ป้ายสถานการณ์ · Today Mac ย้ายการ์ดแผน Sat · เทส 103
Chromium · FF_STUB_BASE = Lean · 390 / 300 / 1280 / 1440 · ข้อมูลทดสอบ = SAMPLE ล้วน
ภาพ tests/screenshots/pf3-{wi-event-390,wi-event-1440,today-long-1440,today-short-1440,today-390}.png
รัน: python3 run_tests_phase103.py"""
import copy, json, os
import pf2_retire as RT
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase100 as P100
import run_tests_phase102 as P102

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
WEEK = P100.WEEK
settle = P100.settle
paste, get_doc, panel, go_strategy, go_today = P100.paste, P100.get_doc, P100.panel, P100.go_strategy, P100.go_today


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def legacy_doc():
    """weeklyImpact/v2 แบบเดิม (WM1) — ไม่มี previous_period / src_actual / source_refs / label_th"""
    return P100.sample()


def new_doc(**over):
    """weeklyImpact/v2 แบบใหม่ (รูปเดียวกับที่ skill weekend-macro-update ส่ง)"""
    d = P100.sample()
    d["sources"]["s2"] = {"name": "SAMPLE second source", "url": "https://example.com/two", "checked_at": "2026-09-27T08:40:00+07:00"}
    d["events"] = {
        "e_new": {"title": "SAMPLE Hormuz tension", "label_th": "SAMPLE ความตึงเครียดช่องแคบ", "kind": "event", "metric": "SAMPLE idx", "basis": "MoM", "period": "Sep 2026", "unit": "%",
                  "date_local": "2026-10-01", "time_status": "unknown", "forecast": 2.6, "previous": 2.7, "previous_revised": True, "previous_period": "Sep 2026", "actual": None,
                  "status": "ongoing", "src_schedule": "s1", "src_forecast": None, "src_actual": None, "source_refs": ["s1", "s2"]},
        "e_plain": {"title": "SAMPLE plain release", "kind": "release", "metric": "SAMPLE m", "unit": "pts", "scheduled_at": "2026-10-01T19:30:00+07:00", "time_status": "confirmed",
                    "forecast": 50.0, "previous": 49.5, "status": "scheduled", "previous_period": None, "src_actual": None, "source_refs": []},
    }
    sc = [{"key": "occurs", "text_th": "SAMPLE occurs text"}, {"key": "delayed", "text_th": "SAMPLE delayed text"}, {"key": "escalates", "text_th": "SAMPLE escalates text"},
          {"key": "eases", "text_th": "SAMPLE eases text"}, {"key": "post", "text_th": "SAMPLE post text"},
          {"key": "zz_custom", "label_th": "ป้ายกำหนดเอง SAMPLE", "text_th": "SAMPLE custom text"}, {"key": "xyz_raw_key", "text_th": "SAMPLE unknown text"},
          {"key": "occurs", "label_th": "ป้ายทับ SAMPLE", "text_th": "SAMPLE override text"}]
    d["assets"] = {"XAUUSD": {"impact": "HIGH", "note": "SAMPLE note", "carryover_th": None, "event_refs": ["e_new", "e_plain"],
                              "interp": {"e_new": {"mechanism_th": "SAMPLE mech", "scenarios_th": sc, "watch_th": "SAMPLE watch"}}},
                   "BRENT": {"impact": "LOW", "note": "x", "event_refs": []}}
    d.update(over)
    return d


def sat_assets(d): return {k: v for k, v in d["assets"].items()}


KEYS = ["title", "label_th", "kind", "status", "previous_period", "src_schedule", "src_forecast", "src_previous", "src_actual", "source_refs", "previous", "previous_revised", "forecast", "actual", "metric", "period"]


def pick_fields(ev):
    d = {k: ev.get(k) for k in KEYS}
    d["label_th"] = d["label_th"] or None   # แอปเก็บ label_th ของ event เป็น '' เมื่อไม่มี (พฤติกรรมเดิม)
    return d


def validate(page, doc_or_text):
    t = doc_or_text if isinstance(doc_or_text, str) else json.dumps(doc_or_text, ensure_ascii=False)
    return js(page, "(t)=>{ const r = Calc.wiValidate(t, wiAssetCtx()); return {errors: r.errors, warnings: r.warnings, doc: r.doc}; }", t)


def reload_docs(page):
    """โหลดใหม่จาก DB จำลอง: ล้าง wiDocs แล้วเริ่ม listener ใหม่ (เหมือนเปิดแอปใหม่)"""
    js(page, "()=>{ wiDocs = {}; wiStop(); wiStart(); }"); settle(page, 700)
    return js(page, "()=>JSON.parse(JSON.stringify(wiDocs))")


def parser_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = P100.launch(pw, 390, 844)
    try:
        go_strategy(page)
        # ── enum ──
        r = js(page, "()=>({kinds: Calc.wiKinds, status: Calc.wiStatus})")
        check(f"{tag} 1 enum kind = release/decision/speech/event/carryover · status = scheduled/released/ongoing/postponed/cancelled",
              sorted(r["kinds"]) == sorted(["release", "decision", "speech", "event", "carryover"]) and sorted(r["status"]) == sorted(["scheduled", "released", "ongoing", "postponed", "cancelled"]), r)
        for k in ["release", "decision", "speech", "event", "carryover"]:
            d = new_doc(); d["events"]["e_new"]["kind"] = k
            v = validate(page, d)
            check(f"{tag} 1 kind={k} ผ่าน", not v["errors"] and v["doc"]["events"]["e_new"]["kind"] == k, v["errors"])
        for st in ["scheduled", "released", "ongoing", "postponed", "cancelled"]:
            d = new_doc(); d["events"]["e_new"]["status"] = st
            v = validate(page, d)
            check(f"{tag} 1 status={st} ผ่าน", not v["errors"] and v["doc"]["events"]["e_new"]["status"] == st, v["errors"])
        d = new_doc(); d["events"]["e_new"]["kind"] = "rumor"
        v = validate(page, d); check(f"{tag} 1 kind ผิด (rumor) → error บอกค่าที่ใช้ได้ · ไม่มี doc", v["errors"] and "event" in v["errors"][0] and v["doc"] is None, v["errors"])
        d = new_doc(); d["events"]["e_new"]["status"] = "done"
        v = validate(page, d); check(f"{tag} 1 status ผิด (done) → error · ไม่มี doc", v["errors"] and "ongoing" in v["errors"][0] and v["doc"] is None, v["errors"])
        # ── normalise legacy ──
        v = validate(page, legacy_doc())
        e0 = v["doc"]["events"]["e_pce"] if v["doc"] else {}
        check(f"{tag} 1 v2 เดิม (ไม่มีฟิลด์ใหม่) ผ่าน · normalise previous_period=null · src_actual=null · source_refs=[]",
              not v["errors"] and e0.get("previous_period") is None and "previous_period" in e0 and e0.get("src_actual") is None and "src_actual" in e0 and e0.get("source_refs") == [], [v["errors"], e0])
        # ── ref ตรวจ ──
        for label, mut in [("source_refs มี id ที่ไม่มี", lambda d: d["events"]["e_new"].__setitem__("source_refs", ["s1", "nope"])),
                           ("src_actual อ้าง id ที่ไม่มี", lambda d: d["events"]["e_new"].__setitem__("src_actual", "nope")),
                           ("src_schedule อ้าง id ที่ไม่มี", lambda d: d["events"]["e_new"].__setitem__("src_schedule", "nope")),
                           ("src_forecast อ้าง id ที่ไม่มี", lambda d: d["events"]["e_new"].__setitem__("src_forecast", "nope")),
                           ("source_refs ไม่ใช่ array", lambda d: d["events"]["e_new"].__setitem__("source_refs", "s1")),
                           ("source_refs มีตัวที่ไม่ใช่ข้อความ", lambda d: d["events"]["e_new"].__setitem__("source_refs", [1]))]:
            d = new_doc(); mut(d)
            v = validate(page, d)
            check(f"{tag} 1 {label} → error สั้น ๆ · ไม่มี doc", len(v["errors"]) >= 1 and v["doc"] is None and all(len(x) < 140 for x in v["errors"]), v["errors"])
        d = new_doc(); d["events"]["e_new"]["src_actual"] = "nope"
        paste(page, d)
        n0 = js(page, "()=>[Object.keys(wiDocs).length, !!document.querySelector('[data-wi-save]'), (document.querySelector('[data-wi-errs]')||{}).innerText||null]")
        check(f"{tag} 1 src_actual ผิด ผ่านหน้า Paste → แสดง error · ไม่มีปุ่มบันทึก · ไม่มีอะไรถูกเขียน", n0[0] == 0 and n0[1] is False and n0[2] and get_doc(page, WEEK) is None, n0)
        js(page, "()=>wiPasteClose()")
        d = new_doc()
        for k in ("src_schedule", "src_forecast", "src_actual"): d["events"]["e_new"][k] = None
        d["events"]["e_new"]["source_refs"] = []
        v = validate(page, d)
        check(f"{tag} 1 src_schedule/src_forecast/src_actual = null + source_refs [] → ผ่าน", not v["errors"], v["errors"])
        d = new_doc(); d["events"]["e_new"]["previous_period"] = "x" * 41
        v = validate(page, d); check(f"{tag} 1 previous_period ยาวเกิน 40 → error", v["errors"] and "previous_period" in v["errors"][0], v["errors"])
        d = new_doc(); d["assets"]["XAUUSD"]["interp"]["e_new"]["scenarios_th"][0]["label_th"] = "  "
        v = validate(page, d); sc = v["doc"]["assets"]["XAUUSD"]["interp"]["e_new"]["scenarios_th"] if v["doc"] else []
        check(f"{tag} 1 label_th เป็นช่องว่างล้วน → ไม่เก็บ (ใช้ป้ายในตัวแทน)", sc and "label_th" not in sc[0], sc[:1])
        # ── import → save → reload : legacy ──
        ld = legacy_doc()
        paste(page, ld, save=True)
        saved = get_doc(page, WEEK)
        want = {k: pick_fields(v) for k, v in ld["events"].items()}
        for k in want: want[k].update({"previous_period": None, "src_actual": ld["events"][k].get("src_actual"), "source_refs": []})
        got = {k: pick_fields(v) for k, v in saved["events"].items()}
        for k in want:
            for f in ("src_previous",): want[k][f] = want[k][f] if want[k][f] is not None else None
        check(f"{tag} 2 legacy v2: นำเข้า → บันทึก → ฟิลด์ใหม่ normalise (null/null/[]) ในเอกสารที่เขียน · ฟิลด์เดิมไม่เปลี่ยน", got == want, [got.get("e_pce"), want.get("e_pce")])
        back = reload_docs(page)[WEEK]
        check(f"{tag} 2 legacy v2: โหลดใหม่แล้วเท่ากับที่บันทึกทุก event (deep-equal ฟิลด์ที่ตรวจ)", {k: pick_fields(v) for k, v in back["events"].items()} == got, back["events"].get("e_pce"))
        check(f"{tag} 2 legacy v2: scenarios_th เดิม (key/text_th) รอดหลังโหลดใหม่ · ไม่มี label_th ปลอม",
              [dict(key=s["key"], text_th=s["text_th"]) for s in back["assets"]["XAUUSD"]["interp"]["e_pce"]["scenarios_th"]] == [dict(key=s["key"], text_th=s["text_th"]) for s in ld["assets"]["XAUUSD"]["interp"]["e_pce"]["scenarios_th"]]
              and all("label_th" not in s for s in back["assets"]["XAUUSD"]["interp"]["e_pce"]["scenarios_th"]), back["assets"]["XAUUSD"]["interp"]["e_pce"]["scenarios_th"])
        # ── import → save → reload : new ──
        js(page, "()=>{ sat7dCol('weeklyImpact').doc('2026-09-28').delete(); }"); settle(page, 500)
        reload_docs(page)
        nd = new_doc()
        paste(page, nd, save=True)
        saved = get_doc(page, WEEK)
        want = {k: pick_fields(v) for k, v in nd["events"].items()}
        got = {k: pick_fields(v) for k, v in saved["events"].items()}
        check(f"{tag} 2 v2 ใหม่: บันทึกแล้ว previous_period · src_actual · source_refs · kind=event · status=ongoing ครบ (deep-equal)", got == want, [got.get("e_new"), want.get("e_new")])
        back = reload_docs(page)[WEEK]
        rb = {k: pick_fields(v) for k, v in back["events"].items()}
        check(f"{tag} 2 v2 ใหม่: โหลดใหม่ → ฟิลด์ใหม่เท่าเดิม (previous_period='Sep 2026' · src_actual=null · source_refs=[s1,s2])",
              rb == want and rb["e_new"]["previous_period"] == "Sep 2026" and rb["e_new"]["src_actual"] is None and rb["e_new"]["source_refs"] == ["s1", "s2"], rb.get("e_new"))
        sc_back = back["assets"]["XAUUSD"]["interp"]["e_new"]["scenarios_th"]
        sc_want = nd["assets"]["XAUUSD"]["interp"]["e_new"]["scenarios_th"]
        check(f"{tag} 2 v2 ใหม่: scenarios_th เก็บ label_th (ตัวที่มี) · ตัวที่ไม่มี = ไม่มี key นี้ · deep-equal หลังโหลดใหม่", sc_back == sc_want, [sc_back, sc_want])
        check(f"{tag} 2 carryover_th = null รอด (ไม่กลายเป็นข้อความว่างที่โชว์)", back["assets"]["XAUUSD"].get("carryover_th") in ("", None), back["assets"]["XAUUSD"].get("carryover_th"))
        # reimport ซ้ำ: ฟิลด์ใหม่ยังอยู่
        paste(page, nd, save=True)
        again = reload_docs(page)[WEEK]
        check(f"{tag} 2 นำเข้าซ้ำสัปดาห์เดิม → ฟิลด์ใหม่ยังเท่าเดิม", {k: pick_fields(v) for k, v in again["events"].items()} == want)
        check(f"{tag} 2 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


UI_JS = """()=>{
  const det = document.querySelector('[data-wi-det]'); if(!det) return null;
  const evs = [...det.querySelectorAll('[data-wi-ev]')].map(e=>({id:e.dataset.wiEv, fp: (e.querySelector('.wiFp')||{innerText:null}).innerText, txt: e.innerText.replace(/\\s+/g,' ').trim(),
    sc: [...e.querySelectorAll('[data-wi-sc]')].map(s=>({key:s.dataset.wiSc, label:(s.querySelector('b')||{}).textContent, text:(s.querySelector('div')||{}).textContent}))}));
  return {evs, all: det.innerText.replace(/\\s+/g,' ').trim(), ow: document.documentElement.scrollWidth - innerWidth};
}"""


def ui_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = P100.launch(pw, w, h)
    try:
        go_strategy(page)
        nd = new_doc()
        P100.seed(page, nd)
        go_strategy(page)
        page.locator('[data-wi-name="XAUUSD"]').click(); settle(page, 400)
        # เปิด 'อีก n ข่าว' ถ้ามี (e_new แรก · e_plain ที่สอง = เห็นทั้งคู่)
        u = js(page, UI_JS)
        e_new = next((e for e in u["evs"] if e["id"] == "e_new"), None); e_plain = next((e for e in u["evs"] if e["id"] == "e_plain"), None)
        check(f"{tag} 3 e_new แสดง 'ครั้งก่อน (Sep 2026)' คู่กับค่า · ไม่ลืมค่าตลาดคาด", e_new and "ครั้งก่อน (Sep 2026)" in (e_new["fp"] or "") and "ตลาดคาด 2.6%" in e_new["fp"] and "แก้ไขแล้ว" in e_new["fp"], e_new and e_new["fp"])
        check(f"{tag} 3 ไม่มี previous_period → 'ครั้งก่อน' เปล่า ไม่มีวงเล็บ", e_plain and "ครั้งก่อน 49.5" in (e_plain["fp"] or "") and "ครั้งก่อน (" not in e_plain["fp"], e_plain and e_plain["fp"])
        labs = {(s["key"], s["text"]): s["label"] for s in (e_new["sc"] if e_new else [])}
        want = {("occurs", "SAMPLE occurs text"): "เกิดขึ้น", ("delayed", "SAMPLE delayed text"): "เลื่อนออกไป", ("escalates", "SAMPLE escalates text"): "ตึงเครียดขึ้น",
                ("eases", "SAMPLE eases text"): "คลี่คลายลง", ("post", "SAMPLE post text"): "หลังประกาศผล", ("zz_custom", "SAMPLE custom text"): "ป้ายกำหนดเอง SAMPLE",
                ("xyz_raw_key", "SAMPLE unknown text"): "กรณีอื่น", ("occurs", "SAMPLE override text"): "ป้ายทับ SAMPLE"}
        check(f"{tag} 3 ป้ายสถานการณ์: label_th ชนะ · occurs=เกิดขึ้น · delayed/escalates/eases/post แมปไทย · key แปลกไม่มี label = 'กรณีอื่น'", labs == want, str(labs))
        check(f"{tag} 3 'เกิดขึ้นตามคาด' ไม่ปรากฏที่ไหนใน UI · key ดิบ (xyz_raw_key / zz_custom / escalates) ไม่โผล่เป็นป้ายใน DOM",
              "เกิดขึ้นตามคาด" not in u["all"] and not any(k in s["label"] for e in u["evs"] for s in e["sc"] for k in ("xyz_raw_key", "zz_custom", "escalates", "occurs", "delayed")), u["all"][:200])
        check(f"{tag} 3 ไม่ล้นแนวนอน", u["ow"] <= 0, u["ow"])
        page_all = js(page, "()=>document.body.innerText")
        check(f"{tag} 3 ทั้งหน้าไม่มีข้อความ 'เกิดขึ้นตามคาด'", "เกิดขึ้นตามคาด" not in page_all)
        # helper โดยตรง (ลำดับ fallback)
        r = js(page, """()=>[wiScLabel({key:'occurs'}), wiScLabel({key:'occurs', label_th:'  '}), wiScLabel({key:'occurs', label_th:' ป้าย '}), wiScLabel({key:'toString'}), wiScLabel({key:'__proto__'}), wiScLabel({key:'above'}), wiScLabel({key:'below'}), wiScLabel({key:'inline'}), wiScLabel(null), wiScLabel({key:'q'})]""")
        check(f"{tag} 3 wiScLabel: ลำดับ label_th → ตาราง → 'กรณีอื่น' · key ชนชื่อ prototype (toString/__proto__) ไม่หลุดเป็นป้าย",
              r == ["เกิดขึ้น", "เกิดขึ้น", "ป้าย", "กรณีอื่น", "กรณีอื่น", "ถ้าสูงกว่าคาด", "ถ้าต่ำกว่าคาด", "ถ้าใกล้เคียงคาด", "กรณีอื่น", "กรณีอื่น"], r)
        st = js(page, "()=>[...document.querySelectorAll('[data-wi-det] [data-wi-ev]')].map(e=>(e.querySelector('.wiBdg')||{}).textContent||null)")
        check(f"{tag} 3 status=ongoing แสดง 'ต่อเนื่อง'", st and st[0] == "ต่อเนื่อง", st)
        if shots:
            page.add_style_tag(content=".tabs, .topbar{ display:none !important }")   # ซ่อนแถบ fixed ไม่ให้ทับภาพ (เฉพาะตอนถ่าย)
            js(page, "()=>document.querySelector('[data-wi-panel]').scrollIntoView()"); settle(page, 1200)
            C.shot(page, f"pf3-wi-event-{w}.png", "[data-wi-panel]")
        check(f"{tag} 3 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── Today ─────────────────────────
BAL = """()=>{
  const c1 = document.querySelector('[data-td-col="1"]'), c2 = document.querySelector('[data-td-col="2"]'), sat = document.querySelector('[data-ln3-satbox]');
  const kind = e => e.matches('[data-wi-today]') ? 'news' : e.matches('[data-ln3-tasks]') ? 'tasks' : e.matches('[data-td-routine],[data-td-off]') ? 'slots' : e.matches('[data-ln3-satbox]') ? 'sat' : e.matches('[data-gl-goal]') ? 'goal' : e.matches('[data-ln3-hw]') ? 'hw' : e.matches('[data-stk-card]') ? 'stk' : e.matches('[data-ln3-recheck]') ? 'recheck' : e.classList.contains('ln3-tdok') ? 'ok' : '?';
  const b1 = c1 ? c1.getBoundingClientRect().bottom : null, b2 = c2 ? c2.getBoundingClientRect().bottom : null;
  return {c1: c1 ? [...c1.children].map(kind) : null, c2: c2 ? [...c2.children].map(kind) : null, b1, b2, r: b1 != null ? Math.abs(b1-b2)/Math.max(b1,b2) : null, satIn: sat ? (c1 && c1.contains(sat) ? 1 : c2 && c2.contains(sat) ? 2 : 0) : null,
          satH: sat ? Math.round(sat.getBoundingClientRect().height) : null, ow: document.documentElement.scrollWidth - innerWidth,
          dom: [...document.querySelectorAll('#tabToday [data-ln3-tdhead],#tabToday [data-td-goaltop],#tabToday [data-wi-today],#tabToday [data-ln3-tasks],#tabToday [data-td-routine],#tabToday [data-td-off],#tabToday [data-ln3-satbox],#tabToday [data-ln3-hw],#tabToday [data-stk-card],#tabToday .ln3-tdok')].map(kind).filter((x,i,a)=>i===0||x!==a[i-1])};
}"""
FOUR = ["XAUUSD", "BTCUSD", "BRENT", "S50"]


def set_sat(page, picks, plans):
    """ตั้ง Asset ที่เลือก + แผนใช้งาน (เฉพาะ plans) · การ์ดแผน Sat สูงเมื่อมี Asset ที่ยังไม่มีแผนหลายตัว (รายการ 'ยังไม่มีแผนใช้งาน n ตัว')"""
    js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", picks); settle(page, 500)
    if plans:
        js(page, """(ks)=>{ ks.forEach(k=>{ sat7dWrite('satIdeas', 'pf3'+k, {v3:true, v2:true, sleeve:'main', asset:k, bias:'', week: wpWeekKey(), status:'active', accts:{}, setups:[], created_at:new Date().toISOString()}); }); }""", plans); settle(page, 800)


# long = 4 Asset ไม่มีแผน (การ์ดแผน Sat สูงสุด ~316px) + ข่าววันนี้ · short = 1 Asset มีแผน ไม่มีข่าว + Re-check Macro ถึงกำหนด (ขวายาวขึ้น) · shortnews = 1 Asset มีแผน + ข่าววันนี้
VARIANTS = {"long": dict(picks=FOUR, plans=[], news=True, recheck=False), "short": dict(picks=["XAUUSD"], plans=["XAUUSD"], news=False, recheck=True),
            "shortnews": dict(picks=["XAUUSD"], plans=["XAUUSD"], news=True, recheck=False)}


def today_tests(pw, w, h, label, variant, shots=False):
    tag = f"[{ENGINE}/{label}/{variant}]"
    mac = w >= 1000; V = VARIANTS[variant]
    b, page, ce, pe = P102.launch(pw, w, h)
    try:
        if V["news"]: P102.seed_wi(page)
        P102.seed(page, P102.stock_doc())
        set_sat(page, V["picks"], V["plans"])
        if V["recheck"]: js(page, "()=>{ window.pbStaleInfo = ()=>({days:32,last:Date.now()-32*86400000,due:true}); }")
        go_today(page)
        RT.retired_td3a(f"{tag} 4 tdBalance/2 คอลัมน์ (ย้ายการ์ดแผน Sat · ก้นต่าง ≤ 15% · debounce · แท็บซ่อน · ลำดับ DOM เดิม) — ดู TD3a_retired.md")
        o = js(page, RT.PANELS_JS)
        check(f"{tag} 4 TD3a: 3 panels ชิดบนเท่ากัน (Mac) · ไม่ล้นแนวนอน", RT.panels_ok(o), o)
        if mac and shots and variant != "shortnews": C.shot(page, f"pf3-today-{variant}-{w}.png", full=True)
        if (not mac) and shots: C.shot(page, "pf3-today-390.png", full=True)
        check(f"{tag} 4 ไม่ล้นแนวนอน · ไม่มี console error", o["ow"] <= 0 and not ce and not pe, [o["ow"], ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        parser_tests(pw)
        ui_tests(pw, 390, 844, "390px", shots=True)
        ui_tests(pw, 1440, 900, "1440px", shots=True)
        ui_tests(pw, 300, 700, "300px")
        for w, h, lab, sh in ((1280, 800, "1280px", False), (1440, 900, "1440px", True)):
            for v in ("long", "short", "shortnews"):
                today_tests(pw, w, h, lab, v, shots=sh)
        today_tests(pw, 390, 844, "390px", "long", shots=True)
        today_tests(pw, 300, 700, "300px", "long")
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
