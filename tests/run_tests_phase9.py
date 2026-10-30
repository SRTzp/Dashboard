#!/usr/bin/env python3
"""F2b — Macro Playbook (schema macroPlaybook/v1) · Calc.pb* (pure) + แผงในแท็บ Flow + ขั้นวาง JSON + ประวัติ
เทส: pbValidate · pbAlign 12 ช่อง · pbStanceText 6 ค่า · pbEffective · pbDiff · หน้าจอ (ท่าทีผสม) · วาง→พรีวิว→บันทึก ·
เปลี่ยนร่างเป็นใช้จริง · ไม่มี update/delete บน macroPlaybook · ไม่แตะ collection 'macro' · ไม่ล้นที่ 1440/430
ภาพเก็บที่ tests/screenshots/f2b-*.png · รัน: python3 run_tests_phase9.py (จำลอง Firestore ด้วย mock-firebase.js)
"""
from pf2_retire import retired as retired2
import copy, json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
UID = "testuid"
COL = ["users", UID, "macroPlaybook"]

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))

def asset(stance="up", **kw):
    if stance == "none":
        return {"stance": "none"}
    d = {"stance": stance, "why": "ตัวอย่าง why", "change_if": "ตัวอย่างเงื่อนไขเปลี่ยนแผน", "drivers": ["P1"]}
    d.update(kw); return d

def pb(quarter="2026Q4", status="active", stances=("up", "flat", "down", "none"), **kw):
    o = {"schema": "macroPlaybook/v1", "quarter": quarter, "status": status, "doc_url": "https://docs.google.com/x",
         "view": {"headline": "หัวข้อตัวอย่าง", "thesis": "ข้อความตัวอย่าง ไม่ใช่มุมมองจริง",
                  "pillars": [{"id": "P1", "title": "เสาหลัก 1", "note": "n1"}, {"id": "P2", "title": "เสาหลัก 2"}],
                  "base": "ฐานตัวอย่าง", "alt": "ทางเลือกตัวอย่าง"},
         "assets": {a: asset(s) for a, s in zip(["XAUUSD", "BTC", "BRENT", "US"], stances)}}
    o.update(kw); return o

def ver(id_, savedAt, no, obj, prev=None):
    d = copy.deepcopy(obj); d.update({"savedAt": savedAt, "versionNo": no, "prevId": prev, "reason": None, "stanceChanges": {}}); d["id"] = id_
    return d

def V(page, obj, now=None):
    return page.evaluate("([o,n])=>Calc.pbValidate(o, n?new Date(n):undefined)", [obj, now])

def seed(page, docs):
    page.evaluate("""(a)=>{ const [col, docs] = a; docs.forEach(d=>{ const id=d.id; const c={...d}; delete c.id; window.firebase.__mockDb.__seedDoc([...col, id], c); });
        pbStop(); pbStart(); }""", [COL, docs])
    page.wait_for_timeout(150)

def fresh(pw, w, h):
    browser, context, page, ce, pe = base.launch_page(pw, w, h, base.DEFAULT_INDEX)
    page.evaluate("() => switchTab('flow')")
    page.evaluate("""() => { window.__pbBad = []; const db = window.firebase.__mockDb; const orig = db.collection.bind(db);
        const wrap = (o, path) => new Proxy(o, {get(t, k){ const v = t[k]; if(typeof v!=='function') return v;
          return (...a)=>{ let p = path; if(k==='collection'||k==='doc') p = path+'/'+a[0];
            if((k==='update'||k==='delete') && /macroPlaybook/.test(path)) window.__pbBad.push(k+' '+path);
            const r = v.apply(t, a); return (r && typeof r==='object' && (k==='collection'||k==='doc')) ? wrap(r, p) : r; }; }});
        db.collection = (n)=>wrap(orig(n), n); }""")
    return browser, context, page, ce, pe

def no_overflow(page, w, tag):
    sw = page.evaluate("() => document.documentElement.scrollWidth")
    check(f"{tag} ไม่ล้นแนวนอน (scrollWidth={sw} ≤ {w})", sw <= w, str(sw))

def calc_tests(page, tag):
    # ── pbValidate ──
    r = V(page, pb(), "2026-09-28")
    check(f"{tag} pbValidate: JSON ครบ → errors ว่าง warnings ว่าง", r["errors"] == [] and r["warnings"] == [], json.dumps(r, ensure_ascii=False))
    for st in ["up", "up_flat", "flat", "down_flat", "down", "none"]:
        o = pb(); o["assets"]["XAUUSD"] = asset(st, posture="สมมติฐาน") if st != "none" else {"stance": "none"}
        check(f"{tag} pbValidate: stance '{st}' ผ่าน", V(page, o, "2026-09-28")["errors"] == [])
    r = V(page, "{ไม่ใช่ json")
    check(f"{tag} pbValidate: JSON ผิดรูป → error ขึ้นต้น 'JSON ผิดรูป'", len(r["errors"]) == 1 and r["errors"][0].startswith("JSON ผิดรูป"))
    check(f"{tag} pbValidate: string ว่าง → error", len(V(page, "  ")["errors"]) == 1)
    check(f"{tag} pbValidate: ไม่ใช่ object (array) → error", len(V(page, [1])["errors"]) == 1)
    def drop(path):
        o = pb(); t = o
        for k in path[:-1]: t = t[k]
        del t[path[-1]]; return o
    for label, path, key in [("schema", ["schema"], "schema"), ("quarter", ["quarter"], "quarter"), ("status", ["status"], "status"),
                             ("view", ["view"], "view"), ("view.headline", ["view", "headline"], "view.headline"),
                             ("view.thesis", ["view", "thesis"], "view.thesis"), ("view.pillars", ["view", "pillars"], "view.pillars"),
                             ("assets", ["assets"], "assets"), ("assets.BTC", ["assets", "BTC"], "assets.BTC"),
                             ("assets.XAUUSD.why", ["assets", "XAUUSD", "why"], "assets.XAUUSD.why"),
                             ("assets.XAUUSD.change_if", ["assets", "XAUUSD", "change_if"], "assets.XAUUSD.change_if"),
                             ("assets.XAUUSD.stance", ["assets", "XAUUSD", "stance"], "assets.XAUUSD.stance")]:
        r = V(page, drop(path), "2026-09-28")
        check(f"{tag} pbValidate: ขาด {label} → error ระบุช่อง", any(key in e for e in r["errors"]), json.dumps(r["errors"], ensure_ascii=False))
    o = pb(); o["assets"]["BTC"] = {"stance": "none"}
    check(f"{tag} pbValidate: stance none ไม่ต้องมี why/change_if", V(page, o, "2026-09-28")["errors"] == [])
    o = pb(quarter="2026-Q4"); check(f"{tag} pbValidate: quarter ผิดรูป → error", any("quarter" in e for e in V(page, o)["errors"]))
    o = pb(status="live"); check(f"{tag} pbValidate: status นอกชุด → error", any("status" in e for e in V(page, o)["errors"]))
    o = pb(); o["assets"]["BTC"]["stance"] = "sideways"
    check(f"{tag} pbValidate: stance ผิด → error", any("assets.BTC.stance" in e for e in V(page, o)["errors"]))
    o = pb(); o["assets"]["BTC"]["confidence"] = "very"
    check(f"{tag} pbValidate: confidence ผิด → error", any("assets.BTC.confidence" in e for e in V(page, o)["errors"]))
    for c in ["low", "mid", "high"]:
        o = pb(); o["assets"]["BTC"]["confidence"] = c
        check(f"{tag} pbValidate: confidence '{c}' ผ่าน", V(page, o, "2026-09-28")["errors"] == [])
    o = pb(); o["assets"]["BTC"]["drivers"] = ["P1", "P9"]
    check(f"{tag} pbValidate: driver อ้าง pillar ที่ไม่มี → error", any("P9" in e for e in V(page, o)["errors"]))
    o = pb(); o["view"]["pillars"].append({"id": "P1", "title": "ซ้ำ"})
    check(f"{tag} pbValidate: pillar id ซ้ำ → error", any("ซ้ำ" in e for e in V(page, o)["errors"]))
    o = pb(); o["view"]["pillars"] = []
    check(f"{tag} pbValidate: pillars ว่าง → error", any("pillars" in e for e in V(page, o)["errors"]))
    o = pb(); del o["doc_url"]
    r = V(page, o, "2026-09-28")
    check(f"{tag} pbValidate: ไม่มี doc_url → warning 'ยังไม่มีลิงก์รายงานเต็ม' (ไม่ error)", r["errors"] == [] and any("ยังไม่มีลิงก์รายงานเต็ม" in w for w in r["warnings"]))
    o = pb(); o["mystery"] = 1; o["assets"]["XAUUSD"]["extra"] = 2; o["assets"]["GOLD"] = {}
    r = V(page, o, "2026-09-28")
    check(f"{tag} pbValidate: key แปลก (บนสุด/ใน asset/asset แปลก) → warning ทั้ง 3 · ไม่ error", r["errors"] == [] and sum("key แปลก" in w for w in r["warnings"]) == 3, json.dumps(r, ensure_ascii=False))
    r = V(page, pb(quarter="2026Q2"), "2026-09-28")
    check(f"{tag} pbValidate: quarter เก่ากว่าไตรมาสปัจจุบัน → warning", r["errors"] == [] and any("เก่ากว่า" in w for w in r["warnings"]))
    for st in ["up_flat", "down_flat"]:
        o = pb(); o["assets"]["BTC"] = asset(st)
        r = V(page, o, "2026-09-28")
        check(f"{tag} pbValidate: {st} ไม่มี posture → warning ท่าทีผสมควรมีวิธีวางตัว (ไม่ error)", r["errors"] == [] and any("ท่าทีผสม" in w for w in r["warnings"]))
        o["assets"]["BTC"]["posture"] = "มีสมมติฐาน"
        check(f"{tag} pbValidate: {st} มี posture → ไม่มี warning ท่าทีผสม", not any("ท่าทีผสม" in w for w in V(page, o, "2026-09-28")["warnings"]))
    o = pb(); o["assets"]["BTC"]["if_alt"] = "ถ้า alt"; o["assets"]["BTC"]["posture"] = "x"
    check(f"{tag} pbValidate: if_alt/posture ผ่านโดยไม่ error", V(page, o, "2026-09-28")["errors"] == [])
    # ── pbAlign 12 ช่อง ──
    table = {"up": ("with", "against"), "up_flat": ("with", "against"), "flat": ("neutral", "neutral"),
             "down_flat": ("against", "with"), "down": ("against", "with"), "none": ("none", "none")}
    bad = []
    for st, (l, s) in table.items():
        gl, gs = page.evaluate("([s])=>[Calc.pbAlign(s,'long'), Calc.pbAlign(s,'short')]", [st])
        if gl != l: bad.append(f"{st}/long={gl}")
        if gs != s: bad.append(f"{st}/short={gs}")
    check(f"{tag} pbAlign: ครบ 12 ช่องตามตาราง", not bad, ", ".join(bad))
    txt = page.evaluate("() => ['up','up_flat','flat','down_flat','down','none'].map(Calc.pbStanceText)")
    check(f"{tag} pbStanceText: ครบ 6 ค่า", txt == ["▲ ขึ้น", "▲▬ ขึ้น/ผสม", "▬ ผสม", "▼▬ ลง/ผสม", "▼ ลง", "— ยังไม่มี"], json.dumps(txt, ensure_ascii=False))
    # ── pbDiff ──
    d = page.evaluate("([a,b])=>Calc.pbDiff(a,b)", [pb(stances=("up", "flat", "down", "none")), pb(stances=("down_flat", "flat", "down", "up"))])
    check(f"{tag} pbDiff: เฉพาะตัวที่เปลี่ยน", d == {"XAUUSD": {"from": "up", "to": "down_flat"}, "US": {"from": "none", "to": "up"}}, json.dumps(d))
    d = page.evaluate("([b])=>Calc.pbDiff(null,b)", [pb(stances=("up", "none", "none", "none"))])
    check(f"{tag} pbDiff: ไม่มีเวอร์ชันก่อน → เทียบกับ none", d == {"XAUUSD": {"from": "none", "to": "up"}}, json.dumps(d))
    # ── pbEffective ──
    def eff(vs, a="XAUUSD", at="2026-10-15T00:00:00Z"):
        return page.evaluate("([v,a,t])=>Calc.pbEffective(v,a,t)", [vs, a, at])
    r = eff([])
    check(f"{tag} pbEffective: ไม่มีเอกสาร → none/null/stale false", r == {"state": "none", "versionId": None, "changedAt": None, "stale": False, "posture": None}, json.dumps(r))
    r = eff([ver("2026Q4-v001", "2026-10-01T00:00:00Z", 1, pb(status="draft"))])
    check(f"{tag} pbEffective: มีแต่ร่าง → none (ร่างไม่มีผล)", r["state"] == "none" and r["versionId"] is None)
    a1 = ver("2026Q4-v001", "2026-10-01T00:00:00Z", 1, pb(stances=("up", "flat", "down", "none")))
    d2 = ver("2026Q4-v002", "2026-10-05T00:00:00Z", 2, pb(status="draft", stances=("down", "flat", "down", "none")), "2026Q4-v001")
    r = eff([a1, d2])
    check(f"{tag} pbEffective: active แล้วมีร่างใหม่กว่า → ใช้ active", r["state"] == "up" and r["versionId"] == "2026Q4-v001", json.dumps(r))
    r = eff([a1], "US")
    check(f"{tag} pbEffective: stance none → state none (versionId ยังคืน)", r["state"] == "none" and r["versionId"] == "2026Q4-v001")
    r = eff([a1], at="2026-09-30T00:00:00Z")
    check(f"{tag} pbEffective: atTime ก่อน savedAt → ยังไม่มีผล (none)", r["state"] == "none" and r["versionId"] is None)
    a2 = ver("2026Q4-v002", "2026-10-05T00:00:00Z", 2, pb(stances=("up", "up", "down", "none")), "2026Q4-v001")
    a3 = ver("2026Q4-v003", "2026-10-09T00:00:00Z", 3, pb(stances=("up", "down", "down", "none")), "2026Q4-v002")
    r = eff([a3, a1, a2])
    check(f"{tag} pbEffective: ท่าทีไม่เปลี่ยนข้าม 3 เวอร์ชัน → changedAt = เวอร์ชันแรก (v001) · ส่งลำดับสลับก็ได้", r["state"] == "up" and r["changedAt"] == "2026-10-01T00:00:00Z" and r["versionId"] == "2026Q4-v003", json.dumps(r))
    r = eff([a1, a2, a3], "BTC")
    check(f"{tag} pbEffective: BTC flat→up→down → changedAt = v003", r["state"] == "down" and r["changedAt"] == "2026-10-09T00:00:00Z", json.dumps(r))
    b1 = ver("2026Q4-v001", "2026-10-01T00:00:00Z", 1, pb(stances=("down", "flat", "down", "none")))
    b2 = ver("2026Q4-v002", "2026-10-05T00:00:00Z", 2, pb(stances=("down_flat", "flat", "down", "none")), "2026Q4-v001")
    r = eff([b1, b2])
    check(f"{tag} pbEffective: down → down_flat นับเป็นเปลี่ยน (changedAt = v002)", r["state"] == "down_flat" and r["changedAt"] == "2026-10-05T00:00:00Z", json.dumps(r))
    r = eff([a1], at="2027-01-05T00:00:00Z")
    check(f"{tag} pbEffective: quarter เก่ากว่า atTime → stale true · state ไม่เปลี่ยน", r["stale"] is True and r["state"] == "up", json.dumps(r))
    check(f"{tag} pbEffective: quarter เดียวกัน → stale false", eff([a1])["stale"] is False)
    p1 = pb(stances=("up_flat", "flat", "down", "none")); p1["assets"]["XAUUSD"]["posture"] = "downside อาจจำกัด"
    r = eff([ver("2026Q4-v001", "2026-10-01T00:00:00Z", 1, p1)])
    check(f"{tag} pbEffective: posture คืนค่า · asset ที่ไม่มี posture = null", r["posture"] == "downside อาจจำกัด" and eff([a1])["posture"] is None, json.dumps(r, ensure_ascii=False))
    n = page.evaluate("()=>[Calc.pbNextId([{quarter:'2026Q4',versionNo:2},{quarter:'2026Q3',versionNo:9}],'2026Q4'), Calc.pbNextId([],'2026Q4')]")
    check(f"{tag} pbNextId: นับต่อจากสูงสุดของไตรมาสนั้น · ไตรมาสใหม่เริ่ม v001", n[0] == {"versionNo": 3, "id": "2026Q4-v003"} and n[1]["id"] == "2026Q4-v001", json.dumps(n))

def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    if w > 900: calc_tests(page, tag)
    page.evaluate("() => switchTab('flow')"); page.wait_for_timeout(150)
    check(f"{tag} ไม่มีเอกสาร → 'ยังไม่มี Playbook' + ปุ่มวาง JSON", "ยังไม่มี Playbook" in page.inner_text("#pbPanel") and page.locator("#pbPanel button:has-text('วาง JSON')").count() == 1)
    # [F2d แก้เคสเดิม] #ffChanges ถูกลบ (F2c เคยแทรกคั่นกลาง) → กลับเป็น ffAction → pbPanel ติดกัน
    check(f"{tag} panel อยู่ใต้แถบดำ (#ffAction) ติดกัน ไม่มี #ffChanges แล้ว", page.evaluate("() => { const a=document.getElementById('ffAction'); return a.nextElementSibling.id==='pbPanel' && !document.getElementById('ffChanges'); }"))
    # ── วาง → พรีวิว → บันทึก (เวอร์ชันแรก ไม่ต้องมีเหตุผล) ──
    first = pb(stances=("up", "up_flat", "down", "none")); first["assets"]["BTC"]["posture"] = "ระยะสั้นยังผันผวน"
    page.click("#pbPanel button:has-text('วาง JSON')")
    page.fill("#pbText", json.dumps(first, ensure_ascii=False))
    page.click(".pb-sheet button:has-text('ตรวจ')"); page.wait_for_timeout(100)
    check(f"{tag} พรีวิวใช้ชิ้นส่วนการ์ดเดียวกัน (.pbCard) + บอก id ที่จะบันทึก 2026Q4-v001 + ท่าทีเปลี่ยน", page.locator(".pb-sheet .pbCard").count() == 1 and "2026Q4-v001" in page.inner_text(".pb-sheet .pbPrev") and "XAUUSD —→▲" in page.inner_text(".pb-sheet .pbChg"), page.inner_text(".pb-sheet .pbChg"))
    check(f"{tag} เวอร์ชันแรก: ไม่มีช่องเหตุผล · ปุ่มบันทึกกดได้", page.locator("#pbReasonText").count() == 0 and page.locator("#pbSaveBtn").is_enabled())
    page.screenshot(path=os.path.join(SHOTS, f"f2b-preview-{label}.png"))
    page.click("#pbSaveBtn"); page.wait_for_timeout(300)
    d1 = page.evaluate("(p)=>window.firebase.__mockDb.__getDoc(p)", COL + ["2026Q4-v001"])
    check(f"{tag} บันทึกครั้งแรก: id 2026Q4-v001 · versionNo 1 · prevId null · reason null · stanceChanges ถูก · มี savedAt",
          d1 and d1["versionNo"] == 1 and d1["prevId"] is None and d1["reason"] is None and d1["savedAt"] and d1["stanceChanges"] == {"XAUUSD": {"from": "none", "to": "up"}, "BTC": {"from": "none", "to": "up_flat"}, "BRENT": {"from": "none", "to": "down"}}, json.dumps(d1, ensure_ascii=False)[:300])
    check(f"{tag} เอกสารเก็บ JSON ที่วางครบ (schema/view/assets)", d1 and d1["schema"] == "macroPlaybook/v1" and d1["view"]["headline"] == "หัวข้อตัวอย่าง" and d1["assets"]["BTC"]["posture"] == "ระยะสั้นยังผันผวน")
    check(f"{tag} บันทึกแล้ว sheet ปิด · แผงโชว์การ์ด", page.locator(".pb-sheet").count() == 0 and page.locator("#pbPanel .pbCard").count() == 1)
    # ── พับ = 1 บรรทัด ──
    head = page.inner_text("#pbPanel .pbHead")
    check(f"{tag} พับ: บรรทัดเดียว มี quarter · headline · ใช้จริง · ไอคอนท่าที 4 ตัว", "2026Q4" in head and "หัวข้อตัวอย่าง" in head and "ใช้จริง" in head and page.locator("#pbPanel .pbIcos .pbIco").count() == 4 and page.locator("#pbPanel .pbBody").count() == 0, head)
    hh = page.evaluate("() => document.querySelector('#pbPanel .pbHead').getBoundingClientRect().height")
    check(f"{tag} พับ: สูง ≤ 48px (1 บรรทัด) = {hh:.0f} (PF2: เปลี่ยนเป็น หัว → headline → ชิป · สูงได้ถึง 140px แทน)", hh <= 140)
    retired2(f"{tag} พับ: สูง ≤ 48px (1 บรรทัด)", "PF2 — การ์ดพับเป็นแถว1 + headline + แถวชิป")
    no_overflow(page, w, tag)
    page.screenshot(path=os.path.join(SHOTS, f"f2b-folded-{label}.png"))
    page.click("#pbPanel .pbHead"); page.wait_for_timeout(80)
    check(f"{tag} แตะหัว 1 ครั้ง → กาง: Thesis · Pillar ชิป · Base/Alt · 4 แถว asset", page.locator("#pbPanel .pbThesis").count() == 1 and page.locator("#pbPanel .pbPill .ui-chip").count() == 2 and page.locator("#pbPanel .pbScn").count() == 2 and page.locator("#pbPanel .pbRowW").count() == 4)
    check(f"{tag} [UI2a แก้] ท่าทีผสม (BTC ▲▬): บรรทัดจางแสดงแค่ posture (ไอคอนท่าทีอยู่บรรทัดบนแล้ว)", page.locator("#pbPanel .pbMix").count() == 1 and page.inner_text("#pbPanel .pbMix") == "ระยะสั้นยังผันผวน", page.inner_text("#pbPanel .pbMix") if page.locator("#pbPanel .pbMix").count() else "none")
    mixcol = page.evaluate("() => getComputedStyle(document.querySelector('#pbPanel .pbMix')).color")
    check(f"{tag} บรรทัดผสม = สีจาง (var(--mute)) ไม่ใช่สีเตือน", mixcol != page.evaluate("() => getComputedStyle(document.documentElement).getPropertyValue('--warn')") and page.evaluate("() => !document.querySelector('#pbPanel .pbMix').className.includes('warn')"))
    check(f"{tag} ท่าทีเต็ม (XAUUSD ▲/BRENT ▼) ไม่มีบรรทัดผสม · ช่องไม่มีค่า (confidence) ไม่แสดง", page.locator("#pbPanel .pbRowW:has-text('XAUUSD') .pbMix").count() == 0 and page.locator("#pbPanel .pbRowW:has-text('BRENT') .pbMix").count() == 0 and page.locator("#pbPanel .pbConf").count() == 0)
    check(f"{tag} asset none → ไอคอน '—'", page.inner_text("#pbPanel .pbRowW:has(.pbAsset:text-is('US')) .pbIco").strip() == "—")
    # ท่าทีผสมไม่มี posture → แสดงแค่ไอคอน+คำ
    no_overflow(page, w, tag)
    page.screenshot(path=os.path.join(SHOTS, f"f2b-expanded-{label}.png"), full_page=False)
    # ── sheet asset ──
    page.click("#pbPanel .pbRowW:has-text('BTC')"); page.wait_for_timeout(80)
    st = page.inner_text(".pb-sheet")
    check(f"{tag} แตะแถว asset → sheet: why · วิธีวางตัว · change_if · drivers · อ่านเต็ม(doc_url ของไตรมาส)", "ตัวอย่าง why" in st and "ระยะสั้นยังผันผวน" in st and "ตัวอย่างเงื่อนไขเปลี่ยนแผน" in st and "P1" in st and page.locator(".pb-sheet a:has-text('อ่านเต็ม')").get_attribute("href") == "https://docs.google.com/x", st[:200])
    check(f"{tag} sheet asset: ไม่มีหัวข้อ 'ถ้า Alternative เกิด' เมื่อไม่มี if_alt", "ถ้า Alternative เกิด" not in st)
    no_overflow(page, w, tag)
    page.screenshot(path=os.path.join(SHOTS, f"f2b-asset-sheet-{label}.png"))
    page.click(".pb-sheet button:has-text('ปิด')")
    # ── เวอร์ชันสอง: ขาดเหตุผล = บันทึกไม่ได้ ──
    second = pb(stances=("down_flat", "up_flat", "down", "none")); second["assets"]["XAUUSD"]["posture"] = "downside อาจจำกัด"; second["assets"]["BTC"]["posture"] = "ยังผสม"
    page.click("#pbPanel button:has-text('วาง JSON')"); page.fill("#pbText", json.dumps(second, ensure_ascii=False))
    page.click(".pb-sheet button:has-text('ตรวจ')"); page.wait_for_timeout(100)
    check(f"{tag} เวอร์ชันสอง: พรีวิวบอกท่าทีเปลี่ยน 'XAUUSD ▲→▼▬' · id v002", "XAUUSD ▲→▼▬" in page.inner_text(".pb-sheet .pbChg") and "2026Q4-v002" in page.inner_text(".pb-sheet .pbPrev"), page.inner_text(".pb-sheet .pbChg"))
    check(f"{tag} เวอร์ชันสอง: ยังไม่เลือกเหตุผล → ปุ่มบันทึกกดไม่ได้", page.locator("#pbSaveBtn").is_disabled())
    page.click(".pb-sheet .ui-chip:has-text('ทบทวนตามรอบ')"); page.wait_for_timeout(50)
    check(f"{tag} เลือกชนิดแต่ไม่มีข้อความ → ยังบันทึกไม่ได้", page.locator("#pbSaveBtn").is_disabled())
    page.click(".pb-sheet .ui-chip:has-text('แก้คำผิด/ข้อมูล')"); page.fill("#pbReasonText", "แก้คำผิด")
    check(f"{tag} type fix แต่ท่าทีเปลี่ยน → เตือน 'แก้คำผิดแต่ท่าทีเปลี่ยน' (ไม่บล็อก · ปุ่มกดได้)", "แก้คำผิดแต่ท่าทีเปลี่ยน" in page.inner_text("#pbFixWarn") and page.locator("#pbSaveBtn").is_enabled())
    page.click(".pb-sheet .ui-chip:has-text('เงื่อนไขเปลี่ยนแผนเกิดแล้ว')"); page.fill("#pbReasonText", "ราคาหลุดแนวรับ")
    check(f"{tag} ชนิดอื่น → คำเตือน fix หาย", page.inner_text("#pbFixWarn").strip() == "")
    # บันทึกไม่สำเร็จ → ข้อความผิดพลาด · ข้อความในช่องไม่หาย
    page.evaluate("(p)=>window.firebase.__mockDb.__denyPath(p)", COL)
    page.click("#pbSaveBtn"); page.wait_for_timeout(250)
    check(f"{tag} บันทึกไม่สำเร็จ → มีข้อความผิดพลาด · JSON และเหตุผลในช่องไม่หาย · sheet ยังเปิด", "บันทึกไม่สำเร็จ" in page.inner_text(".pb-sheet") and json.loads(page.input_value("#pbText"))["quarter"] == "2026Q4" and page.input_value("#pbReasonText") == "ราคาหลุดแนวรับ")
    page.evaluate("(p)=>window.firebase.__mockDb.__allowPath(p)", COL)
    page.click("#pbSaveBtn"); page.wait_for_timeout(300)
    d2 = page.evaluate("(p)=>window.firebase.__mockDb.__getDoc(p)", COL + ["2026Q4-v002"])
    check(f"{tag} บันทึกสำเร็จหลังแก้: v002 · versionNo 2 · prevId v001 · reason {{trigger,text}} · stanceChanges XAUUSD up→down_flat + BTC up_flat→up_flat ไม่มี",
          d2 and d2["versionNo"] == 2 and d2["prevId"] == "2026Q4-v001" and d2["reason"] == {"type": "trigger", "text": "ราคาหลุดแนวรับ"} and d2["stanceChanges"] == {"XAUUSD": {"from": "up", "to": "down_flat"}}, json.dumps(d2 and d2.get("stanceChanges")))
    check(f"{tag} v001 ยังอยู่ไม่ถูกแก้", page.evaluate("(p)=>window.firebase.__mockDb.__getDoc(p).versionNo", COL + ["2026Q4-v001"]) == 1)
    # ── ร่าง + แถบ "มีร่าง" + เปลี่ยนเป็นใช้จริง ──
    draft = pb(status="draft", stances=("down", "up_flat", "down", "none")); draft["assets"]["BTC"]["posture"] = "ร่าง"
    page.click("#pbPanel button:has-text('วาง JSON')"); page.fill("#pbText", json.dumps(draft, ensure_ascii=False))
    page.click(".pb-sheet button:has-text('ตรวจ')"); page.click(".pb-sheet .ui-chip:has-text('หลักฐานใหม่')"); page.fill("#pbReasonText", "มีข้อมูลใหม่")
    page.click("#pbSaveBtn"); page.wait_for_timeout(300)
    d3 = page.evaluate("(p)=>window.firebase.__mockDb.__getDoc(p)", COL + ["2026Q4-v003"])
    check(f"{tag} บันทึกร่าง: v003 status draft · prevId v002 · stanceChanges เทียบกับ active (v002)", d3 and d3["status"] == "draft" and d3["prevId"] == "2026Q4-v002" and d3["stanceChanges"] == {"XAUUSD": {"from": "down_flat", "to": "down"}}, json.dumps(d3 and d3.get("stanceChanges")))
    check(f"{tag} มีร่างใหม่กว่า active: แผงยังแสดง active (ท่าที XAUUSD ▼▬) + แถบ 'มีร่าง v3'", "มีร่าง v3" in page.inner_text("#pbPanel .pbDraftBar") and "ใช้จริง" in page.inner_text("#pbPanel .pbHead") and page.evaluate("()=>pbMain().assets.XAUUSD.stance") == "down_flat", page.inner_text("#pbPanel .pbHead"))   # PF2: กางแล้วไม่มีแถวชิป → ตรวจท่าทีจากข้อมูล
    check(f"{tag} Calc.pbEffective บนข้อมูลจริง: ร่างไม่มีผล (XAUUSD = down_flat จาก v002)", page.evaluate("() => { const e=Calc.pbEffective(pbList,'XAUUSD',Date.now()); return e.state==='down_flat' && e.versionId==='2026Q4-v002' && e.posture==='downside อาจจำกัด'; }"))
    page.click("#pbPanel .pbDraftBar"); page.wait_for_timeout(80)
    check(f"{tag} แตะแถบ 'มีร่าง' → ดูการ์ดร่าง (อ่านอย่างเดียว) + ปุ่มเปลี่ยนเป็นใช้จริง", page.locator(".pb-sheet .pbCard").count() == 1 and page.locator(".pb-sheet button:has-text('เปลี่ยนเป็นใช้จริง')").count() == 1 and "ร่าง" in page.inner_text(".pb-sheet .pbBadge"))
    page.click(".pb-sheet button:has-text('เปลี่ยนเป็นใช้จริง')"); page.wait_for_timeout(100)
    check(f"{tag} เปลี่ยนเป็นใช้จริง: พรีวิว v004 · ต้องกรอกเหตุผล (ปุ่มบันทึกกดไม่ได้)", "2026Q4-v004" in page.inner_text(".pb-sheet .pbPrev") and page.locator("#pbSaveBtn").is_disabled() and page.locator("#pbText").count() == 0)
    page.click(".pb-sheet .ui-chip:has-text('ทบทวนตามรอบ')"); page.fill("#pbReasonText", "ยืนยันใช้ร่าง")
    page.click("#pbSaveBtn"); page.wait_for_timeout(300)
    d4 = page.evaluate("(p)=>window.firebase.__mockDb.__getDoc(p)", COL + ["2026Q4-v004"])
    d3b = page.evaluate("(p)=>window.firebase.__mockDb.__getDoc(p)", COL + ["2026Q4-v003"])
    check(f"{tag} เปลี่ยนร่างเป็นใช้จริง = เอกสารใหม่ v004 (active · prevId v003 · เนื้อหาเดิม) · ร่าง v003 ยังอยู่เป็นร่าง",
          d4 and d4["status"] == "active" and d4["prevId"] == "2026Q4-v003" and d4["view"]["headline"] == d3["view"]["headline"] and d4["assets"]["XAUUSD"]["stance"] == "down" and d3b and d3b["status"] == "draft" and d4["reason"]["type"] == "review")
    check(f"{tag} หลังเปลี่ยน: ไม่มีแถบ 'มีร่าง' อีก (active ใหม่กว่าร่าง)", page.locator("#pbPanel .pbDraftBar").count() == 0)
    # ── ประวัติ ──
    page.click("#pbPanel button:has-text('ประวัติ')"); page.wait_for_timeout(80)
    ids = page.eval_on_selector_all(".pb-sheet .pbHist b", "els=>els.map(e=>e.textContent)")
    check(f"{tag} ประวัติ: ใหม่→เก่า 4 เวอร์ชัน", ids == ["2026Q4-v004", "2026Q4-v003", "2026Q4-v002", "2026Q4-v001"], json.dumps(ids))
    ht = page.inner_text(".pb-sheet")
    check(f"{tag} ประวัติ: มีวันเวลา · สถานะ · เหตุผล · ท่าทีที่เปลี่ยน · ไม่มีปุ่มลบ", "/" in ht and "ร่าง" in ht and "เงื่อนไขเปลี่ยนแผนเกิดแล้ว — ราคาหลุดแนวรับ" in ht and "XAUUSD ▲→▼▬" in ht and "ลบ" not in ht, ht[:200])
    no_overflow(page, w, tag)
    page.click(".pb-sheet .pbHist:has-text('2026Q4-v002')"); page.wait_for_timeout(80)
    check(f"{tag} ประวัติ: แตะ = ดูการ์ดของเวอร์ชันนั้น (อ่านอย่างเดียว · ไม่มีปุ่มเปลี่ยนเป็นใช้จริงสำหรับ active)", page.locator(".pb-sheet").count() == 2 and page.locator(".pb-sheet:last-of-type .pbCard").count() == 1 and page.locator(".pb-sheet:last-of-type button:has-text('เปลี่ยนเป็นใช้จริง')").count() == 0)
    page.evaluate("() => document.querySelectorAll('.pb-sheet').forEach(e=>e.remove())")
    # ── validate errors บล็อก ──
    bad = pb(); del bad["view"]["thesis"]
    page.click("#pbPanel button:has-text('วาง JSON')"); page.fill("#pbText", json.dumps(bad, ensure_ascii=False)); page.click(".pb-sheet button:has-text('ตรวจ')")
    check(f"{tag} JSON มี error → บอกช่องที่ขาด · ไม่มีปุ่มบันทึก · ไม่มีพรีวิว", "view.thesis" in page.inner_text(".pb-sheet .pbErrs") and page.locator("#pbSaveBtn").count() == 0 and page.locator(".pb-sheet .pbCard").count() == 0)
    warn = pb(); del warn["doc_url"]
    page.fill("#pbText", json.dumps(warn, ensure_ascii=False)); page.click(".pb-sheet button:has-text('ตรวจ')")
    check(f"{tag} JSON มีแต่ warning → แสดงคำเตือน · ยังมีพรีวิว", "ยังไม่มีลิงก์รายงานเต็ม" in page.inner_text(".pb-sheet .pbWarns") and page.locator(".pb-sheet .pbCard").count() == 1)
    no_overflow(page, w, tag)
    page.evaluate("() => { pbPaste=null; document.querySelectorAll('.pb-sheet').forEach(e=>e.remove()); }")
    # ── ความปลอดภัยของข้อมูล ──
    acc = page.evaluate("() => window.__fsAccess || []")
    check(f"{tag} ไม่มีการอ่าน/เขียน collection 'macro' เดิม", not any(p.split('/')[-1] == 'macro' or '/macro/' in p or p.endswith('/macro') for p in acc), json.dumps([p for p in acc if 'macro' in p and 'macroPlaybook' not in p]))
    check(f"{tag} ไม่มีการเรียก update/delete บน macroPlaybook (ตรวจขณะรันจริง)", page.evaluate("() => window.__pbBad") == [], json.dumps(page.evaluate("() => window.__pbBad")))
    src = open(base.DEFAULT_INDEX, encoding="utf-8").read()
    a, b = src.index("F2b — Macro Playbook (แท็บ Flow"), src.index("F1 — การ์ดปฏิทินข่าว")
    blk = src[a:b]
    check(f"{tag} ซอร์สส่วน Playbook: ไม่มี .update( / .delete( / collection('macro')", ".update(" not in blk and ".delete(" not in blk and "'macro'" not in blk)
    # ── อ่านไม่ได้ / stale ──
    page.evaluate("(p)=>{ window.firebase.__mockDb.__denyPath(p); pbStop(); pbStart(); }", COL); page.wait_for_timeout(200)
    check(f"{tag} อ่าน Firestore ไม่ได้ → 'อ่าน Playbook ไม่ได้' + เตือน · ไม่ error", "อ่าน Playbook ไม่ได้" in page.inner_text("#pbPanel") and page.locator("#pbPanel .pbWarn").count() == 1)
    page.evaluate("(p)=>window.firebase.__mockDb.__allowPath(p)", COL)
    page.evaluate("(v)=>{ pbErr=null; pbLoaded=true; pbList=[v]; pbRender(); }", ver("2026Q2-v001", "2026-04-01T00:00:00Z", 1, pb(quarter="2026Q2")))
    check(f"{tag} stale: Playbook เป็นของไตรมาสก่อน → เตือน 'Playbook เป็นของ 2026Q2 — ยังไม่มีของไตรมาสนี้'" if page.evaluate("() => Calc.pbQuarterOf(new Date())") != "2026Q2" else f"{tag} stale (ข้าม: ไตรมาสจริงบนเครื่องคือ 2026Q2)",
          True if page.evaluate("() => Calc.pbQuarterOf(new Date())") == "2026Q2" else "ยังไม่มีของไตรมาสนี้" in page.inner_text("#pbPanel"), page.inner_text("#pbPanel")[:200])
    no_overflow(page, w, tag)
    check(f"{tag} console: zero error-level messages", len(ce) == 0, "; ".join(ce[:8]))
    check(f"{tag} console: zero uncaught page errors", len(pe) == 0, "; ".join(pe[:8]))
    context.close(); browser.close()

def main():
    with sync_playwright() as pw:
        ui_tests(pw, 1440, 900, "1440px")
        ui_tests(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 9 / F2b) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)

if __name__ == "__main__":
    main()
