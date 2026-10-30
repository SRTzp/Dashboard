#!/usr/bin/env python3
"""F2c — ต่อ Macro Playbook เข้า Sat: Strategy (Macro อ่านอย่างเดียว) · การ์ดแผนขั้นหน้างาน (Trend override · Trend Shift · Driver · ขนาดไม้)
· บันทึก order (11 field) · แท็บ Flow (แถบดำ Macro · ชื่อ asset ในแถวพับ · บล็อก "อะไรเปลี่ยนสัปดาห์นี้")
เทส: Calc.sizeRule ครบทุกคู่ · satMacroOf · Strategy · การ์ด · Driver · บันทึก order (ค่า ณ ตอนกด) · Flow · ไม่เขียน macroPlaybook/ไม่แตะ 'macro'
ภาพเก็บที่ tests/screenshots/f2c-*.png · รัน: python3 run_tests_phase11.py (จำลอง Firestore ด้วย mock-firebase.js + fundflow stub)
"""
from pf2_retire import retired as retired2
import copy, json, os
from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
PBCOL = ["users", "testuid", "macroPlaybook"]



def f2c_line(page, t):
    return page.evaluate("(t)=>{ const d=document.createElement('div'); d.innerHTML=satV3F2cTradeLine(t); return d.innerText||d.textContent; }", t) or ""

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def iso(delta_h=0):
    return (datetime.now(timezone.utc) + timedelta(hours=delta_h)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def cell(stance, **kw):
    if stance == "none":
        return {"stance": "none"}
    d = {"stance": stance, "why": f"why {stance}", "change_if": f"change_if {stance}", "drivers": ["P1", "P2"]}
    d.update(kw); return d


def pbver(no, savedAt, quarter="2026Q4", status="active", x="up", b="none", r="none", u="none", **kw):
    """เวอร์ชัน Playbook 1 ตัว · x/b/r/u = stance ของ XAUUSD/BTC/BRENT/US (kw = override ช่องของ asset เช่น xa={'drivers':['P2']})"""
    a = {"XAUUSD": cell(x, **kw.get("xa", {})), "BTC": cell(b, **kw.get("ba", {})), "BRENT": cell(r, **kw.get("ra", {})), "US": cell(u)}
    return {"id": f"{quarter}-v{no:03d}", "schema": "macroPlaybook/v1", "quarter": quarter, "status": status,
            "view": {"headline": "หัวข้อ", "thesis": "ข้อความ", "pillars": [{"id": "P1", "title": "เสาหลัก 1"}, {"id": "P2", "title": "เสาหลัก 2"}]},
            "assets": a, "savedAt": savedAt, "versionNo": no, "prevId": None, "reason": None, "stanceChanges": {}}


def seed_pb(page, docs):
    """ล้างเวอร์ชันเดิม แล้ว seed ชุดใหม่ (เขียนตรงเข้า mock db · ไม่ผ่านตัวดักเขียนของแอป)"""
    page.evaluate("""(a)=>{ const [col, docs] = a; const db = window.firebase.__mockDb;
        (window.__pbSeeded||[]).forEach(id=>{ try{ window.__rawCol('users').doc('testuid').collection('macroPlaybook').doc(id).delete(); }catch(e){} });
        window.__pbSeeded = [];
        docs.forEach(d=>{ const id=d.id; const c={...d}; delete c.id; db.__seedDoc([...col, id], c); window.__pbSeeded.push(id); });
        pbStop(); pbStart(); }""", [PBCOL, docs])
    page.wait_for_timeout(200)


def wk(page, asset, bias="Long", trend="up", inval=None, macro_v=None, note=None):
    """ตั้ง Strategy สัปดาห์นี้ของ asset (เขียน satWeek ตรง ๆ แบบที่แอปเขียน)"""
    comps = {"trend": {"v": trend}}
    if macro_v is not None or note is not None:
        comps["macro"] = {}
        if macro_v is not None: comps["macro"]["v"] = macro_v
        if note is not None: comps["macro"]["note"] = note
    patch = {"bias": bias, "comps": comps}
    if inval is not None: patch["invalidation"] = inval
    page.evaluate("([a,p])=>satwWrite(a,p)", [asset, patch])
    page.wait_for_timeout(150)


def reset_ideas(page):
    page.evaluate("() => satIdeasList.map(x=>x.id).forEach(i=>satV3IdeaDelete(i))")
    page.wait_for_timeout(200)


def mkidea(page, iid, asset="XAUUSD", bias="Long", entry=4600, sl=4599.5, **extra):
    d = {"v3": True, "asset": asset, "bias": bias, "created_at": iso(), "entry": entry, "sl": sl, "tp": None, "cancel_level": None,
         "conditions": [{"id": "c1", "text": "Break & Pullback @ 4600", "tp_from": 4700, "tp_to": 4750, "inval": None, "active": True, "saved": True}],
         "planned": True, "setups": [], "status": "active", "accts": {}}
    d.update(extra)
    if "tp" not in extra and entry and sl and entry != sl:   # ST1: ต้องมี TP แรกให้ R:R ≥ 1.5 ถึงบันทึก order ได้ — fixture ใส่ R:R 3 (เดิม tp None)
        d["tp"] = round(entry + 3 * (entry - sl), 4)
    page.evaluate("([i,d])=>{ d.week = wpWeekKey(); sat7dWrite('satIdeas', i, d); }", [iid, d])
    page.wait_for_timeout(250)


def idea(page, iid):
    return page.evaluate("(i)=>sat7dIdea(i)", iid)


def norm(t):
    return " ".join((t or "").split())


def txt(page, sel):
    return norm(page.evaluate("(s)=>{ const e=document.querySelector(s); return e ? e.innerText : ''; }", sel))


def no_overflow(page, w, tag):
    sw = page.evaluate("() => document.documentElement.scrollWidth")
    check(f"{tag} ไม่ล้นแนวนอน (scrollWidth={sw} ≤ {w})", sw <= w, str(sw))


def shot(page, name, sel=None):
    try:
        if sel and page.locator(sel).count():
            page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else:
            page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e:
        print("shot fail", name, e)


def fresh(pw, w, h):
    browser, context, page, ce, pe = base.launch_page(pw, w, h, base.DEFAULT_INDEX)
    page.evaluate("""() => { window.__pbW = []; window.__macroTouch = []; const db = window.firebase.__mockDb; const orig = db.collection.bind(db); window.__rawCol = orig;
        const wrap = (o, path) => new Proxy(o, {get(t, k){ const v = t[k]; if(typeof v!=='function') return v;
          return (...a)=>{ let p = path; if(k==='collection'||k==='doc') p = path+'/'+a[0];
            if(['set','add','update','delete'].includes(k) && /macroPlaybook/.test(path)) window.__pbW.push(k+' '+path);
            if(/^macro(\\/|$)/.test(path) || /\\/macro(\\/|$)/.test(path)) window.__macroTouch.push(k+' '+path);
            const r = v.apply(t, a); return (r && typeof r==='object' && (k==='collection'||k==='doc')) ? wrap(r, p) : r; }; }});
        db.collection = (n)=>wrap(orig(n), n); }""")
    return browser, context, page, ce, pe


# ─────────────────────────────────────────────────────────────
def calc_tests(page, tag):
    # ── Calc.sizeRule ครบทุกคู่ (4 × 3 × 2 = 24) ──
    bad = []
    for align in ["with", "neutral", "against", "none"]:
        for trend in ["up", "flat", "down"]:
            for side in ["Long", "Short"]:
                r = page.evaluate("([a,t,s])=>Calc.sizeRule({macroAlign:a, trendState:t, side:s})", [align, trend, side])
                mac = align == "against"
                trd = (side == "Long" and trend == "down") or (side == "Short" and trend == "up")
                exp = {"factor": 0.6 if mac else 1, "kind": "against" if mac else ("with" if align == "with" else "neutral"), "against": {"macro": mac, "trend": trd}}   # WA1: ตัวคูณตาม Macro อย่างเดียว (Trend ไม่อยู่ในกติกา)
                if r != exp: bad.append(f"{align}/{trend}/{side}={json.dumps(r)}")
    check(f"{tag} Calc.sizeRule: ครบ 24 คู่ (macroAlign 4 × trend 3 × side 2)", not bad, "; ".join(bad[:4]))
    check(f"{tag} Calc.sizeRule: ค่า 0.6 มาจาก SAT_MACRO_CUT ที่เดียว", page.evaluate("() => SAT_MACRO_CUT") == 0.6 and page.evaluate("() => Calc.sizeRule({macroAlign:'against',trendState:'down',side:'long'}).factor === SAT_MACRO_CUT"))
    r = page.evaluate("() => Calc.sizeRule({macroAlign:'against', trendState:null, side:'long'})")
    check(f"{tag} Calc.sizeRule: trend ไม่มีค่า (null) = ไม่สวน (WA1: Macro สวนอย่างเดียว ×0.6)", r["factor"] == 0.6 and r["against"]["trend"] is False and r["against"]["macro"] is True)
    m = page.evaluate("() => SAT_PB_ASSET")
    check(f"{tag} SAT_PB_ASSET: XAUUSD→XAUUSD · BTC→BTC · Brent→BRENT · S50→null",
          m["XAUUSD"] == "XAUUSD" and m["BTCUSD"] == "BTC" and m["BTC"] == "BTC" and m["BRENT"] == "BRENT" and m["Brent"] == "BRENT" and m["S50"] is None, json.dumps(m))

    # ── satMacroOf ──
    none = page.evaluate("() => satMacroOf('XAUUSD', Date.now(), [])")
    check(f"{tag} satMacroOf: ไม่มี Playbook → state none · versionId null · drivers []", none["state"] == "none" and none["versionId"] is None and none["drivers"] == [], json.dumps(none))
    draft = pbver(1, iso(-48), status="draft", x="up")
    r = page.evaluate("([l])=>satMacroOf('XAUUSD', Date.now(), l)", [[draft]])
    check(f"{tag} satMacroOf: มีแต่ร่าง → none (ร่างไม่มีผล)", r["state"] == "none" and r["versionId"] is None, json.dumps(r))
    act = pbver(2, iso(-48), x="up", b="down_flat", ba={"posture": "downside อาจจำกัด", "drivers": ["P2"]})
    r = page.evaluate("([l])=>satMacroOf('XAUUSD', Date.now(), l)", [[draft, act]])
    check(f"{tag} satMacroOf: active → state · versionId · why · change_if · quarter",
          r["state"] == "up" and r["versionId"] == "2026Q4-v002" and r["why"] == "why up" and r["change_if"] == "change_if up" and r["quarter"] == "2026Q4" and r["stale"] is False, json.dumps(r, ensure_ascii=False))
    check(f"{tag} satMacroOf: drivers = [{{id, title จาก view.pillars}}]", r["drivers"] == [{"id": "P1", "title": "เสาหลัก 1"}, {"id": "P2", "title": "เสาหลัก 2"}], json.dumps(r["drivers"], ensure_ascii=False))
    rb = page.evaluate("([l])=>satMacroOf('BTCUSD', Date.now(), l)", [[act]])
    check(f"{tag} satMacroOf: ท่าทีผสมคืน posture (BTCUSD → key BTC)", rb["state"] == "down_flat" and rb["posture"] == "downside อาจจำกัด" and rb["drivers"] == [{"id": "P2", "title": "เสาหลัก 2"}], json.dumps(rb, ensure_ascii=False))
    rs = page.evaluate("([l])=>satMacroOf('S50', Date.now(), l)", [[act]])
    check(f"{tag} satMacroOf: S50 → none · drivers [] แม้มี Playbook", rs["state"] == "none" and rs["drivers"] == [] and rs["versionId"] is None, json.dumps(rs))
    rbr = page.evaluate("([l])=>[satMacroOf('BRENT', Date.now(), l).state, satMacroOf('Brent', Date.now(), l).state]", [[pbver(3, iso(-2), r="down")]])
    check(f"{tag} satMacroOf: BRENT / Brent → key BRENT", rbr == ["down", "down"], json.dumps(rbr))
    old = pbver(4, iso(-24 * 200), quarter="2026Q2", x="up")
    r = page.evaluate("([l])=>satMacroOf('XAUUSD', Date.now(), l)", [[old]])
    check(f"{tag} satMacroOf: quarter เก่ากว่าไตรมาสปัจจุบัน → stale true", r["stale"] is True and r["state"] == "up", json.dumps(r))
    rn = page.evaluate("([l])=>satMacroOf('BTCUSD', Date.now(), l)", [[pbver(5, iso(-2), x="up")]])
    check(f"{tag} satMacroOf: asset stance none → state none · drivers [] (versionId ยังมี)", rn["state"] == "none" and rn["drivers"] == [] and rn["versionId"] == "2026Q4-v005", json.dumps(rn))
    # แปลง up/flat/down
    conv = page.evaluate("() => ['up','up_flat','flat','down_flat','down','none'].map(satMacroTrendOf)")
    check(f"{tag} แปลงท่าที → up/flat/down: up·up_flat→up · down·down_flat→down · flat→flat · none→ไม่นับ", conv == ["up", "up", "flat", "down", "down", None], json.dumps(conv))


def strategy_tests(page, tag, w):
    p5.goto_sat(page)
    reset_ideas(page)
    seed_pb(page, [pbver(1, iso(-72), x="up", b="down_flat", ba={"posture": "ระยะสั้นยังผันผวน"}, r="flat")])
    # comps.macro.v เดิม (ค่าเก่า 'down') ต้องอยู่ในข้อมูล แต่ไม่ถูกอ่าน/แสดง
    wk(page, "XAUUSD", "Long", "up", inval=4650, macro_v="down", note=None)
    p5.open_editor(page, "XAUUSD")
    ed = page.evaluate("() => document.querySelector('.ui-editor[data-asset=\"XAUUSD\"]').innerText")
    blk = txt(page, '.ui-editor[data-asset="XAUUSD"] [data-macro-block]')
    check(f"{tag} Strategy: Macro แสดงจาก Playbook อ่านอย่างเดียว = '▲ ขึ้น' + why + 'เปลี่ยนเมื่อ: …'", "▲ ขึ้น" in blk and "why up" in blk and "เปลี่ยนเมื่อ: change_if up" in blk, blk)
    check(f"{tag} Strategy: ป้าย 'ใส่เอง · จะเชื่อม Playbook…' ถูกลบ", "ใส่เอง" not in ed and "จะเชื่อม Playbook" not in ed)
    ro = page.evaluate("() => { const f=[...document.querySelectorAll('.ui-editor[data-asset=\"XAUUSD\"] .ui-factor')].find(x=>x.innerText.includes('Macro')); return f && f.classList.contains('ui-f-ro') && !f.getAttribute('onclick') && !f.querySelector('.ui-f-pen'); }")
    check(f"{tag} Strategy: ช่อง Macro ไม่มี onclick/✎ (อ่านอย่างเดียว) และมีช่องกรอก 'My opinion'", ro and page.locator('.ui-editor[data-asset="XAUUSD"] input[data-my-opinion]').count() == 1)
    # PV2b: หัว Strategy ยาวขึ้น → แถบแท็บล่าง (fixed) ทับจุดกลางของช่อง Macro ที่จอแคบ แล้ว force-click พลาดไปโดนแถบ · ใช้ element.click() (เหตุการณ์ click บนช่อง Macro เหมือนเดิม)
    page.evaluate("() => [...document.querySelectorAll('.ui-editor[data-asset=\"XAUUSD\"] .ui-factor')].find(x=>x.innerText.includes('Macro')).click()"); page.wait_for_timeout(150)
    mc = page.evaluate("() => satwWeek(wpWeekKey(),'XAUUSD').comps.macro")
    check(f"{tag} Strategy: แตะช่อง Macro ไม่เขียนอะไร · comps.macro.v เดิม ('down') ยังอยู่ ไม่ถูกลบ/แก้", mc.get("v") == "down", json.dumps(mc))
    tally = page.evaluate("() => satwTally(satwWeek(wpWeekKey(),'XAUUSD'), 'XAUUSD')")
    check(f"{tag} Strategy: คะแนนนับ Macro จาก Playbook (▲) ไม่ใช่ comps.macro.v เดิม (▼) → up 2 down 0", tally == {"up": 2, "flat": 0, "down": 0, "n": 2}, json.dumps(tally))
    check(f"{tag} Strategy: ตัวแก้ไม่โชว์ ▼ จาก comps.macro.v เดิม (แถวสรุป 'รวม ▲2 ▬0 ▼0')", "รวม ▲2 ▬0 ▼0" in ed, ed[:200])
    # My opinion → comps.macro.note
    p5.fill_blur(page, '.ui-editor[data-asset="XAUUSD"] input[data-my-opinion]', "ผมคิดว่า dovish")
    mc = page.evaluate("() => satwWeek(wpWeekKey(),'XAUUSD').comps.macro")
    check(f"{tag} Strategy: My opinion บันทึกที่ comps.macro.note เดิม (v เดิมไม่หาย)", mc.get("note") == "ผมคิดว่า dovish" and mc.get("v") == "down", json.dumps(mc, ensure_ascii=False))
    n_before = page.evaluate("() => JSON.stringify(satwTally(satwWeek(wpWeekKey(),'XAUUSD'),'XAUUSD'))")
    check(f"{tag} Strategy: My opinion ไม่มีผลกับคะแนน · ป้าย 'My opinion' มี", n_before == json.dumps({"up": 2, "flat": 0, "down": 0, "n": 2}, separators=(",", ":")) and "My opinion" in page.inner_text('.ui-editor[data-asset="XAUUSD"]'))
    # ป้าย ขนาดไม้ บน tile
    tile = txt(page, '.ui-tile[data-key="XAUUSD"]')
    check(f"{tag} PF3 tile (Macro ▲ + Trend ▲): ไม่โชว์ 'Long · ขนาดไม้ เต็ม' / x/2 (ป้ายถอดแล้ว) · กฎขนาดไม้ตาม Macro ยังอยู่ในการ์ดแผน", "Long" not in tile and "ขนาดไม้" not in tile and "x/2" not in tile, tile)
    wk(page, "XAUUSD", "Long", "down")
    seed_pb(page, [pbver(1, iso(-72), x="down", b="down_flat", ba={"posture": "ระยะสั้นยังผันผวน"}, r="flat")])
    tile = txt(page, '.ui-tile[data-key="XAUUSD"]')
    check(f"{tag} PF3 tile (Macro ▼ + Trend ▼): ไม่โชว์ 'Long · ลด 40%' (ป้ายถอดแล้ว)", "ลด 40%" not in tile and "Long" not in tile, tile)
    wk(page, "XAUUSD", "Short", "down")
    tile = txt(page, '.ui-tile[data-key="XAUUSD"]')
    check(f"{tag} PF3 tile (Short + Macro ▼): ไม่โชว์ 'Short · ขนาดไม้ เต็ม' (ป้ายถอดแล้ว)", "Short" not in tile and "ขนาดไม้" not in tile, tile)
    check(f"{tag} tile: แถบ 2 ขีด (Trend · Macro) คงไว้", page.locator('.ui-tile[data-key="XAUUSD"] .ui-tile-dot').count() == 2)
    # tally 4 สถานะ
    tl = page.evaluate("""() => { const w = {comps:{trend:{v:'flat'}}}; const out = {};
        [['up_flat','x'],['down_flat','x'],['flat','x'],['none','x']].forEach(([st])=>{
          const l = [{id:'2026Q4-v009', status:'active', quarter:'2026Q4', savedAt:new Date().toISOString(), versionNo:9, assets:{XAUUSD:{stance:st}}}];
          const m = satMacroOf('XAUUSD', Date.now(), l); out[st] = satMacroTrendOf(m.state); });
        return out; }""")
    check(f"{tag} tally: up_flat→up · down_flat→down · flat→flat · none→ไม่นับ", tl == {"up_flat": "up", "down_flat": "down", "flat": "flat", "none": None}, json.dumps(tl))
    # ท่าทีผสมในตัวแก้ (BTC down_flat)
    wk(page, "BTCUSD", "Long", "up", inval=60000)
    p5.open_editor(page, "BTCUSD")
    mix = txt(page, '.ui-editor[data-asset="BTCUSD"] .ui-mac .pbMix')
    check(f"{tag} Strategy: ท่าทีผสม → บรรทัดจาง '▼▬ ลง/ผสม · ระยะสั้นยังผันผวน' (.pbMix ไม่ใช่คำเตือน)", mix == "▼▬ ลง/ผสม · ระยะสั้นยังผันผวน" and page.locator('.ui-editor[data-asset="BTCUSD"] .ui-editor-hint:has-text("ผสม")').count() == 0, mix)
    # Brent flat: ไม่มี mix line
    wk(page, "BRENT", "Long", "up", inval=70)
    p5.open_editor(page, "BRENT")
    check(f"{tag} Strategy: ท่าที flat (ไม่ใช่ up_flat/down_flat) → ไม่มีบรรทัดท่าทีผสม", page.locator('.ui-editor[data-asset="BRENT"] .ui-mac .pbMix').count() == 0)
    # S50
    wk(page, "S50", "Long", "up", inval=900)
    p5.open_editor(page, "S50")
    s50 = txt(page, '.ui-editor[data-asset="S50"] [data-macro-block]')
    check(f"{tag} Strategy: S50 → '— S50 ไม่อยู่ใน Playbook' ตัวจาง ไม่มีคำเตือนส้ม", "— S50 ไม่อยู่ใน Playbook" in s50 and page.locator('.ui-editor[data-asset="S50"] [data-mac-warn]').count() == 0, s50)
    check(f"{tag} Strategy: S50 ยังกรอก My opinion ได้", page.locator('.ui-editor[data-asset="S50"] input[data-my-opinion]:not([disabled])').count() == 1)
    # ไม่มี Playbook ใช้จริง
    seed_pb(page, [])
    p5.open_editor(page, "XAUUSD")
    nb = txt(page, '.ui-editor[data-asset="XAUUSD"] [data-macro-block]')
    check(f"{tag} Strategy: ไม่มี Playbook → '—' + คำเตือนส้ม 'ยังไม่มี Playbook ใช้จริง'", nb.startswith("—") and "ยังไม่มี Playbook ใช้จริง" in nb and page.locator('.ui-editor[data-asset="XAUUSD"] [data-mac-warn="nopb"]').count() == 1, nb)
    check(f"{tag} Strategy: ไม่มี Playbook ยังกรอก My opinion ได้ (แก้ได้เสมอ)", page.locator('.ui-editor[data-asset="XAUUSD"] input[data-my-opinion]:not([disabled])').count() == 1)
    # stale
    seed_pb(page, [pbver(1, iso(-24 * 200), quarter="2026Q2", x="up")])
    p5.open_editor(page, "XAUUSD")
    st = txt(page, '.ui-editor[data-asset="XAUUSD"] [data-macro-block]')
    check(f"{tag} Strategy: stale → เตือน 'Playbook เป็นของ 2026Q2'", "Playbook เป็นของ 2026Q2" in st and page.locator('.ui-editor[data-asset="XAUUSD"] [data-mac-warn="stale"]').count() == 1, st)
    seed_pb(page, [pbver(1, iso(-72), x="up", b="down_flat", ba={"posture": "ระยะสั้นยังผันผวน"}, r="flat")])
    check(f"{tag} Strategy: SATW_COMPS_SCORED ยัง = ['trend','macro']", page.evaluate("() => JSON.stringify(SATW_COMPS_SCORED)") == '["trend","macro"]')
    p5.open_editor(page, "XAUUSD")
    no_overflow(page, w, f"{tag} Strategy")
    if w < 500:
        wk(page, "XAUUSD", "Long", "down", inval=4650)
        seed_pb(page, [pbver(1, iso(-72), x="down", b="down_flat", ba={"posture": "ระยะสั้นยังผันผวน"}, r="flat")])
        p5.open_editor(page, "XAUUSD")
        page.evaluate("() => document.querySelector('.ui-tile[data-key=\"XAUUSD\"]').scrollIntoView({block:'start'})")
        page.wait_for_timeout(100)
        shot(page, "f2c-430-strategy.png", "#satV3Panel .ui-tiles")
        shot(page, "f2c-430-strategy-editor.png", '.ui-editor[data-asset="XAUUSD"]')


def card_tests(page, tag, w):
    p5.goto_sat(page)
    reset_ideas(page)
    seed_pb(page, [pbver(1, iso(-72), x="down", b="down_flat", ba={"posture": "ระยะสั้นยังผันผวน", "drivers": ["P2"]}, r="flat", xa={"drivers": ["P1", "P2"]})])
    wk(page, "XAUUSD", "Long", "down", inval=4650)
    mkidea(page, "iA", "XAUUSD", "Long", 4700, 4699.5)     # Long + Trend ▼ + Macro ▼ = สวนทั้งคู่ · Entry 4700 > 4650 ไม่ผ่าน Trend Shift
    C = '.ui-plan[data-id="iA"]'
    check(f"{tag} การ์ด: มีบรรทัด Trend/Macro/Driver/ขนาดไม้ (data-f2c)", page.locator(f"{C} [data-f2c]").count() == 1, page.evaluate("() => document.querySelectorAll('.ui-plan').length+''"))
    check(f"{tag} PF3 การ์ดแผนไม่มีแถว Trend (Strategy จ.) และไม่มีปุ่ม [เปลี่ยน] แล้ว", page.locator(f"{C} [data-f2c-row=\"trend\"]").count() == 0 and "Strategy จ." not in (txt(page, f"{C} [data-f2c]") or "") and page.locator(f"{C} button:has-text(\"เปลี่ยน\")").count() == 0, txt(page, f"{C} [data-f2c]"))
    check(f"{tag} การ์ด: Macro = pbStanceText '▼ ลง' + v001", "Macro: ▼ ลง" in txt(page, f'{C} [data-f2c-row="macro"]') and "v001" in txt(page, f'{C} [data-f2c-row="macro"]'), txt(page, f'{C} [data-f2c-row="macro"]'))
    check(f"{tag} การ์ด: ยังไม่กดเปลี่ยน → ไม่มีปุ่ม [ขึ้น][ผสม][ลง]", page.locator(f"{C} [data-trend]").count() == 0)
    # PF1 — ตัวเปลี่ยน Trend ต่อแผน (trend_override · [ขึ้น][ผสม][ลง] · ใช้ค่า Strategy) ถอดแล้ว (A1/A8): เคสด้านล่างเลิกใช้
    check(f"{tag} PF3 ไม่มีตัวเปลี่ยน Trend ต่อแผนเลย ([data-trend] = 0 · ไม่มีปุ่ม ขึ้น/ผสม/ลง)", page.locator(f"{C} [data-trend]").count() == 0 and page.locator(f"{C} button:has-text(\"ผสม\")").count() == 0)
    check(f"{tag} PF3 แผนไม่มี trend_override (ตัวเปลี่ยนถอดแล้ว ไม่มีอะไรเขียนฟิลด์นี้)", not idea(page, "iA").get("trend_override"))
    check(f"{tag} PF3 satWeek ของ Strategy ไม่ถูกแตะ (comps.trend.v เดิม 'down' ยังอยู่ในข้อมูล)", page.evaluate("() => satwWeek(wpWeekKey(),'XAUUSD').comps.trend.v") == "down")
    check(f"{tag} PF3 ไม่มีข้อความ 'เปลี่ยนจาก' / 'ยกเลิก override' ในการ์ดแผน", not any(x in (txt(page, C) or "") for x in ("เปลี่ยนจาก", "ยกเลิก override", "Trend ▲ (")), txt(page, C))
    check(f"{tag} PF3 ขนาดไม้ตาม Macro อย่างเดียว: Macro ▼ → 'ขนาดไม้: ลด 40% (สวน Macro)' + มีสวิตช์ [ใช้ไม้เต็ม] โดยไม่ขึ้นกับ Trend", "ลด 40% (สวน Macro)" in (txt(page, f"{C} [data-f2c-row=\"size\"]") or "") and page.locator(f"{C} [data-size-switch]").count() == 1)
    check(f"{tag} PF3 trend_override = null/ไม่มี (ไม่มีการ override Trend ต่อแผน)", idea(page, "iA").get("trend_override") in (None, False, ""))
    # ขนาดไม้ 40% + lot
    check(f"{tag} การ์ด: 'ขนาดไม้: ลด 40% (สวน Macro)'", "ขนาดไม้: ลด 40% (สวน Macro)" in txt(page, f'{C} [data-f2c-row="size"]'), txt(page, f'{C} [data-f2c-row="size"]'))
    lot_cut = page.evaluate("() => satV3PlanAcctCalc(sat7dIdea('iA'), 'main')")
    exp = page.evaluate("""() => { const c = satV3PlanAcctCalc(sat7dIdea('iA'), 'main'); const cfg = c.chosen.cfg;
        return {expCut: Calc.satLot({riskAmount:c.riskCur*SAT_MACRO_CUT, dist:0.5, contract:cfg.contract, lotStep:cfg.lotStep, minLot:cfg.minLot}).lot,
                full: Calc.satLot({riskAmount:c.riskCur, dist:0.5, contract:cfg.contract, lotStep:cfg.lotStep, minLot:cfg.minLot}).lot, factor:c.factor, lot:c.lot}; }""")
    check(f"{tag} lot: ลดเหลือ ~60% (riskAmount × 0.6 ผ่าน Calc.satLot เดิม) — ตัด {exp['lot']} vs เต็ม {exp['full']}",
          exp["factor"] == 0.6 and abs(exp["lot"] - exp["expCut"]) < 1e-9 and 0.55 <= exp["lot"] / exp["full"] <= 0.65, json.dumps(exp))
    heat_cut = page.evaluate("() => satV3PlanAcctCalc(sat7dIdea('iA'), 'main').heatPct")
    # สวิตช์ไม่ตามกฎ
    page.click(f'{C} [data-size-switch]'); page.wait_for_timeout(250)
    check(f"{tag} สวิตช์: 'ใช้ไม้เต็ม (ไม่ตามกฎ)' → idea.size_full_override = true · ป้ายส้ม 'ไม่ตามกฎ' · 'ขนาดไม้: เต็ม'",
          idea(page, "iA").get("size_full_override") is True and page.locator(f"{C} [data-off-rule]").count() == 1 and "ขนาดไม้: เต็ม" in txt(page, f'{C} [data-f2c-row="size"]'), txt(page, f'{C} [data-f2c-row="size"]'))
    full = page.evaluate("() => satV3PlanAcctCalc(sat7dIdea('iA'), 'main')")
    check(f"{tag} lot: ใช้ไม้เต็ม → lot เท่าเต็ม ({full['lot']}) · heat คิดจาก lot ใหม่ (สูงกว่าตอนลด)", full["factor"] == 1 and full["lot"] == exp["full"] and (full["heatPct"] or 0) > (heat_cut or 0), f"{full['lot']} heat {full['heatPct']} vs {heat_cut}")
    page.click(f'{C} [data-size-switch]'); page.wait_for_timeout(250)
    check(f"{tag} สวิตช์: กดอีกครั้ง = กลับตามกฎ (override=false · ป้ายหาย · ลด 40%)", idea(page, "iA").get("size_full_override") is False and page.locator(f"{C} [data-off-rule]").count() == 0 and "ลด 40%" in txt(page, f'{C} [data-f2c-row="size"]'))
    # ใต้ minLot = ข้อความเดิมของ satLot
    mkidea(page, "iA", "XAUUSD", "Long", 4700, 4000)
    msg = page.evaluate("() => satV3PlanAcctCalc(sat7dIdea('iA'), 'main').lotMsg")
    check(f"{tag} lot: ต่ำกว่า minLot → ข้อความเดิมของ satLot ('SL กว้างเกินขนาดขั้นต่ำ')", msg == "SL กว้างเกินขนาดขั้นต่ำ", msg)
    mkidea(page, "iA", "XAUUSD", "Long", 4700, 4699.5)
    # ไม่ตามกฎ → กฎ = เต็ม ไม่มีสวิตช์ (Short ตาม Macro ▼ + Trend ▼)
    reset_ideas(page)
    mkidea(page, "iS", "XAUUSD", "Short", 4600, 4600.5)
    CS = '.ui-plan[data-id="iS"]'
    check(f"{tag} การ์ด: กฎ = เต็ม → 'ขนาดไม้: เต็ม' ไม่มีสวิตช์ ไม่มีป้ายไม่ตามกฎ", "ขนาดไม้: เต็ม" in txt(page, f'{CS} [data-f2c-row="size"]') and page.locator(f"{CS} [data-size-switch]").count() == 0 and page.locator(f"{CS} [data-off-rule]").count() == 0)

    # ── Trend Shift ──
    def shift(bias, entry, inval=4650):
        reset_ideas(page)
        wk(page, "XAUUSD", bias, "down" if bias == "Long" else "up", inval=inval)
        mkidea(page, "iT", "XAUUSD", bias, entry, (entry - 0.5) if bias == "Long" else (entry + 0.5))
        return page.locator('.ui-plan[data-id="iT"] [data-trend-shift]').count() == 1, page.locator('.ui-plan[data-id="iT"] [data-trend]').count()
    s, b = shift("Long", 4600)
    check(f"{tag} PF3 Trend Shift: Long และ Entry 4600 < 4650 → ไม่มีเตือน Trend Shift / ไม่มีปุ่ม [ขึ้น][ผสม][ลง] (ถอดแล้ว)", (not s) and b == 0, [s, b])
    warn = txt(page, '.ui-plan[data-id="iT"] [data-trend-shift]')
    check(f"{tag} PF3 Trend Shift: ไม่มีข้อความ 'ราคาผ่าน Trend Shift' / 'แค่ Sweep แล้วกลับ' ในการ์ดแผน", not warn and not any(x in (txt(page, '.ui-plan[data-id="iT"]') or "") for x in ("ราคาผ่าน Trend Shift", "แค่ Sweep แล้วกลับ", "Trend อาจเปลี่ยนแล้ว")), json.dumps([warn, txt(page, '.ui-plan[data-id="iT"]')], ensure_ascii=False))
    tr = page.evaluate("() => satwWeek(wpWeekKey(),'XAUUSD').comps.trend.v")
    check(f"{tag} Trend Shift: ไม่เปลี่ยน Trend ให้เอง (Strategy ยัง ▼) · ไม่บล็อก (ยังบันทึกได้)", tr == "down" and not idea(page, "iT").get("trend_override"))
    if w < 500:
        page.evaluate("() => document.querySelector('.ui-plan[data-id=\"iT\"]').scrollIntoView({block:'start'})"); page.wait_for_timeout(100)
        shot(page, "f2c-430-trend-shift.png", '.ui-plan[data-id="iT"]')
    no_overflow(page, w, f"{tag} การ์ด Trend Shift")
    s, _ = shift("Long", 4700)
    check(f"{tag} Trend Shift: Long และ Entry 4700 > 4650 → ไม่เตือน", not s)
    s, b = shift("Short", 4700)
    check(f"{tag} PF3 Trend Shift: Short และ Entry 4700 > 4650 → ไม่มีเตือน/ไม่มีปุ่มเปิด (ถอดแล้ว)", (not s) and b == 0, [s, b])
    s, _ = shift("Short", 4600)
    check(f"{tag} Trend Shift: Short และ Entry 4600 < 4650 → ไม่เตือน", not s)
    reset_ideas(page)
    wk(page, "XAUUSD", "Long", "down")
    page.evaluate("() => satwWrite('XAUUSD', {invalidation: null})"); page.wait_for_timeout(150)
    mkidea(page, "iT", "XAUUSD", "Long", 100, 99.5)
    check(f"{tag} Trend Shift: ไม่มีระดับ (invalidation ว่าง) → ไม่เตือน", page.locator('.ui-plan[data-id="iT"] [data-trend-shift]').count() == 0 and page.locator('.ui-plan[data-id="iT"] [data-f2c]').count() == 1)
    wk(page, "XAUUSD", "Long", "down", inval=4650)
    mkidea(page, "iT", "XAUUSD", "Long", None, None)
    check(f"{tag} Trend Shift: ไม่มี Entry → ไม่เตือน", page.locator('.ui-plan[data-id="iT"] [data-trend-shift]').count() == 0)

    # ── Driver ──
    reset_ideas(page)
    wk(page, "XAUUSD", "Long", "down", inval=4650)
    mkidea(page, "iD", "XAUUSD", "Long", 4700, 4699.5)
    D = '.ui-plan[data-id="iD"]'
    chips = txt(page, f'{D} [data-f2c-row="driver"]')
    check(f"{tag} Driver: ชิป 'P1 · เสาหลัก 1' 'P2 · เสาหลัก 2' · ค่าเริ่มต้น = ตัวแรก (ui-on ที่ P1)", "P1 · เสาหลัก 1" in chips and "P2 · เสาหลัก 2" in chips and page.locator(f'{D} [data-driver="P1"].ui-on').count() == 1 and page.locator(f'{D} [data-driver="P2"].ui-on').count() == 0, chips)
    check(f"{tag} Driver: ยังไม่แตะ = ไม่เก็บ idea.driver", not idea(page, "iD").get("driver"))
    page.click(f'{D} [data-driver="P2"]'); page.wait_for_timeout(250)
    check(f"{tag} Driver: แตะ P2 → เก็บ idea.driver='P2' (เลือกได้ 1 ตัว)", idea(page, "iD").get("driver") == "P2" and page.locator(f'{D} [data-driver="P2"].ui-on').count() == 1 and page.locator(f'{D} .ui-chip.ui-on[data-driver]').count() == 1)
    page.evaluate("() => sat7dWrite('satIdeas','iD',{driver:'P9'})"); page.wait_for_timeout(250)
    check(f"{tag} Driver: ค่าเก่าที่ไม่อยู่ในรายการ Playbook (P9) → กลับเป็นตัวแรก (P1)", page.locator(f'{D} [data-driver="P1"].ui-on').count() == 1)
    seed_pb(page, [])
    page.evaluate("() => satV3Render()"); page.wait_for_timeout(150)
    check(f"{tag} Driver: ไม่มี Playbook → 'Driver —' ตัวจาง ไม่เตือน · Macro 'ไม่มี Playbook'", "Driver —" in txt(page, f'{D} [data-f2c-row="driver"]') and page.locator(f"{D} [data-driver]").count() == 0 and "ไม่มี Playbook" in txt(page, f'{D} [data-f2c-row="macro"]') and page.locator(f"{D} .ui-cond-warn").count() == 0)
    check(f"{tag} การ์ด: ไม่มี Playbook → 'ขนาดไม้: เต็ม' (macro none ไม่สวน)", "ขนาดไม้: เต็ม" in txt(page, f'{D} [data-f2c-row="size"]'))
    # S50 / asset ไม่ผูก pillar
    seed_pb(page, [pbver(1, iso(-72), x="down", b="down", ba={"drivers": []}, r="flat")])
    reset_ideas(page)
    wk(page, "S50", "Long", "up", inval=900)
    mkidea(page, "iS50", "S50", "Long", 1000, 990)
    check(f"{tag} Driver: S50 → 'Driver —' ไม่บล็อก ไม่เตือน", "Driver —" in txt(page, '.ui-plan[data-id="iS50"] [data-f2c-row="driver"]') and "Macro: ไม่มี Playbook" in txt(page, '.ui-plan[data-id="iS50"] [data-f2c-row="macro"]'))
    reset_ideas(page)
    wk(page, "BTCUSD", "Short", "down", inval=70000)
    mkidea(page, "iB", "BTCUSD", "Short", 60000, 60100)
    check(f"{tag} Driver: asset ที่ไม่ได้ผูก pillar (drivers ว่าง) → 'Driver —'", "Driver —" in txt(page, '.ui-plan[data-id="iB"] [data-f2c-row="driver"]'))
    # ท่าทีผสมบนการ์ด
    seed_pb(page, [pbver(1, iso(-72), x="down", b="down_flat", ba={"posture": "ระยะสั้นยังผันผวน", "drivers": ["P2"]}, r="flat")])
    page.evaluate("() => satV3Render()"); page.wait_for_timeout(150)
    check(f"{tag} การ์ด: ท่าทีผสม → บรรทัดจาง '▼▬ ลง/ผสม · ระยะสั้นยังผันผวน' ใต้ Macro", txt(page, '.ui-plan[data-id="iB"] .ui-f2c .pbMix') == "▼▬ ลง/ผสม · ระยะสั้นยังผันผวน", txt(page, '.ui-plan[data-id="iB"] .ui-f2c'))
    # เพิ่งเปลี่ยน
    seed_pb(page, [pbver(1, iso(-72), x="up"), pbver(2, iso(-2), x="down", b="down_flat", ba={"posture": "p", "drivers": ["P2"]})])
    reset_ideas(page)
    wk(page, "XAUUSD", "Long", "down", inval=4650)
    mkidea(page, "iR", "XAUUSD", "Long", 4700, 4699.5)
    check(f"{tag} Playbook เพิ่งเปลี่ยนท่าที (≤24 ชม.) → ป้ายจาง 'Playbook เพิ่งเปลี่ยน …' (ข้อมูล ไม่ใช่คำเตือน)", page.locator('.ui-plan[data-id="iR"] [data-f2c-recent]').count() == 1 and page.locator('.ui-plan[data-id="iR"] .ui-cond-warn').count() == 0, txt(page, '.ui-plan[data-id="iR"] .ui-f2c'))
    seed_pb(page, [pbver(1, iso(-72), x="up"), pbver(2, iso(-48), x="down")])
    page.evaluate("() => satV3Render()"); page.wait_for_timeout(150)
    check(f"{tag} Playbook เปลี่ยนเกิน 24 ชม. → ไม่มีป้าย 'เพิ่งเปลี่ยน'", page.locator('.ui-plan[data-id="iR"] [data-f2c-recent]').count() == 0)
    seed_pb(page, [pbver(1, iso(-72), x="down"), pbver(2, iso(-2), x="down")])
    page.evaluate("() => satV3Render()"); page.wait_for_timeout(150)
    check(f"{tag} v002 ท่าทีเดิมกับ v001 (ไม่เปลี่ยนท่าที) → ไม่มีป้าย 'เพิ่งเปลี่ยน' (นับตามท่าที ไม่ใช่เวอร์ชัน)", page.locator('.ui-plan[data-id="iR"] [data-f2c-recent]').count() == 0)
    no_overflow(page, w, f"{tag} การ์ด")
    if w < 500:
        seed_pb(page, [pbver(1, iso(-72), x="up"), pbver(2, iso(-2), x="down", b="down_flat", ba={"posture": "p", "drivers": ["P2"]}, xa={"drivers": ["P1", "P2"]})])
        reset_ideas(page)
        wk(page, "XAUUSD", "Long", "down", inval=4650)
        mkidea(page, "iShot", "XAUUSD", "Long", 4700, 4699.5, driver="P2")
        page.evaluate("() => document.querySelector('.ui-plan[data-id=\"iShot\"]').scrollIntoView({block:'start'})"); page.wait_for_timeout(120)
        shot(page, "f2c-430-card-cut40.png", '.ui-plan[data-id="iShot"]')


def saved_trade(page, iid):
    return page.evaluate("(i)=>{ const a = ((sat7dIdea(i)||{}).accts||{}).main || {}; return a.trade_id ? (getBook('main').trades.find(x=>x.id===a.trade_id) || null) : null; }", iid)


def save_tests(page, tag, w):
    p5.goto_sat(page)
    reset_ideas(page)
    base_pb = pbver(1, iso(-72), x="down", xa={"drivers": ["P1", "P2"]})
    seed_pb(page, [base_pb])
    wk(page, "XAUUSD", "Long", "up", inval=4650, note="ความเห็นของฉัน")
    mkidea(page, "iO", "XAUUSD", "Long", 4700, 4699.5)
    O = '.ui-plan[data-id="iO"]'
    # Strategy Trend ▲ + Macro ▼ (against) → override Trend ▼ → สวนทั้งคู่ · เลือก Driver P2
    page.click(f'{O} [data-driver="P2"]'); page.wait_for_timeout(250)
    check(f"{tag} ก่อนบันทึก: ลด 40% (Macro ▼ สวน Long + Trend ▼ สวน)", "ลด 40%" in txt(page, f'{O} [data-f2c-row="size"]'))
    # เปลี่ยน Playbook หลัง Activate ก่อนกดบันทึก (v002: XAUUSD ▲▬ posture) → ไม้ต้องใช้ค่าใหม่
    seed_pb(page, [base_pb, pbver(2, iso(0), x="up_flat", xa={"posture": "upside จำกัด", "drivers": ["P1", "P2"]})])
    # ค่าที่การ์ดเห็นตอน Activate = สวน · ตอนกดบันทึก = up_flat (with) → factor 1
    btn = page.locator(f'{O} .ui-btn:has-text("บันทึก order ทุกบัญชีที่พร้อม")')
    btn.scroll_into_view_if_needed(); btn.click(); page.wait_for_timeout(400)
    t = saved_trade(page, "iO")
    check(f"{tag} บันทึก order: สร้างไม้ satB 1 ไม้", t is not None)
    keys = ["trend_state", "trend_changed", "macro_state", "macro_stance", "playbook_version", "driver", "size_rule", "off_rule", "macro_note", "macro_recent", "sizeFactor"]
    check(f"{tag} บันทึก order: ครบ 11 field ตามข้อ D (sizeFactor + 10 field ใหม่)", t is not None and all(k in t for k in keys), json.dumps([k for k in keys if t and k not in t]))
    exp = {"trend_state": None, "trend_changed": None, "macro_state": "with", "macro_stance": "up_flat", "playbook_version": "2026Q4-v002",
           "driver": "P2", "size_rule": 1, "off_rule": False, "macro_note": "ความเห็นของฉัน", "macro_recent": True, "sizeFactor": None}
    got = {k: (t or {}).get(k) for k in keys}
    check(f"{tag} บันทึก order: ค่า ณ ตอนกด — เปลี่ยน Playbook หลัง Activate ก่อนบันทึก → ไม้ใช้ค่าใหม่ (v002 ▲▬ ตาม Long → เต็ม · macro_recent true)", got == exp, json.dumps(got, ensure_ascii=False))
    line = f2c_line(page, t)
    check(f"{tag} รายละเอียดไม้: 1 บรรทัดอ่านอย่างเดียว 'Macro ตาม (▲▬ v002) · Trend สวน · Driver P2 · เต็ม' + ป้าย Trend เปลี่ยน / Playbook เพิ่งเปลี่ยน",
          line.startswith("Macro ตาม (▲▬ v002) · Trend — · Driver P2 · เต็ม") and "Trend เปลี่ยน" not in line and "Playbook เพิ่งเปลี่ยน" in line and "ไม่ตามกฎ" not in line, line)
    # ล็อกแล้วไม่เปลี่ยนแม้ Playbook/Trend เปลี่ยนภายหลัง
    seed_pb(page, [base_pb, pbver(2, iso(0), x="up_flat"), pbver(3, iso(1), x="down")])
    page.evaluate("() => satwWrite('XAUUSD', {comps:{trend:{v:'flat'}}})"); page.wait_for_timeout(200)
    t2 = saved_trade(page, "iO")
    check(f"{tag} บันทึก order: ล็อกแล้ว — Playbook/Trend เปลี่ยนภายหลัง ค่าในไม้ไม่เปลี่ยน", {k: t2.get(k) for k in keys} == exp)

    # ── สวนทั้งคู่ตอนกด · ลด 40% · sizeFactor 0.6 ──
    def save_case(iid, bias, docs, trend_wk, override_full=False, driver=None, note=None, reason=None):
        reset_ideas(page)
        seed_pb(page, docs)
        wk(page, "XAUUSD", bias, trend_wk, inval=4650, note=note)
        extra = {}
        if override_full: extra["size_full_override"] = True
        if driver: extra["driver"] = driver
        if reason: extra["macro_note"] = reason   # WA1: สวน/นอก Macro ต้องมีเหตุผลก่อนบันทึก order
        mkidea(page, iid, "XAUUSD", bias, 4700, 4699.5 if bias == "Long" else 4700.5, **extra)
        page.evaluate("([i])=>satV3SaveSlot(i,'main')", [iid]); page.wait_for_timeout(350)
        return saved_trade(page, iid)
    t = save_case("iCut", "Long", [pbver(1, iso(-72), x="down")], "down", driver="P2", note=None, reason="เหตุผลทดสอบ")
    got = {k: t.get(k) for k in keys}
    check(f"{tag} บันทึก order (สวนทั้งคู่): size_rule 0.6 · off_rule false · sizeFactor 0.6 · macro_state against · macro_note = สำเนา My opinion ของสัปดาห์ · macro_recent false",
          got["size_rule"] == 0.6 and got["off_rule"] is False and got["sizeFactor"] == 0.6 and got["macro_state"] == "against" and got["macro_stance"] == "down"
          and got["macro_note"] == "เหตุผลทดสอบ" and got["macro_recent"] is False and got["trend_state"] is None and got["trend_changed"] is None and got["driver"] == "P2", json.dumps(got, ensure_ascii=False))
    lot_full = page.evaluate("() => { const c = satV3PlanAcctCalc(sat7dIdea('iCut'),'main',Object.assign({}, satV3F2c(sat7dIdea('iCut')), {off:true})); return c.lot; }")
    check(f"{tag} บันทึก order (สวนทั้งคู่): qty = lot ที่ลด ~60% ({t['qty']} vs เต็ม {lot_full})", 0.55 <= t["qty"] / lot_full <= 0.65, f"{t['qty']} {lot_full}")
    line = f2c_line(page, t)
    check(f"{tag} รายละเอียดไม้: 'Macro สวน (▼ v001) · Trend ตาม? …' — Long + Trend ▼ = 'Trend สวน' · Driver P2 · ลด 40% (ไม่มีป้าย)", line.startswith("Macro สวน (▼ v001) · Trend — · Driver P2 · ลด 40%") and "ไม่ตามกฎ" not in line, line)
    t = save_case("iOff", "Long", [pbver(1, iso(-72), x="down")], "down", override_full=True, reason="เหตุผลทดสอบ")
    check(f"{tag} บันทึก order (ใช้ไม้เต็มทั้งที่กฎ 0.6): off_rule true · size_rule 0.6 · sizeFactor null", t["off_rule"] is True and t["size_rule"] == 0.6 and t["sizeFactor"] is None, json.dumps({k: t.get(k) for k in keys}, ensure_ascii=False))
    line = f2c_line(page, t)
    check(f"{tag} รายละเอียดไม้: มีป้าย 'ไม่ตามกฎ' เมื่อ off_rule", "ไม่ตามกฎ" in line and "· เต็ม" in line, line)
    # ไม่มี Playbook
    t = save_case("iNone", "Long", [], "up")
    got = {k: t.get(k) for k in keys}
    check(f"{tag} บันทึก order (ไม่มี Playbook): macro_state none · macro_stance none · playbook_version null · driver null · size_rule 1 · off_rule false · sizeFactor null",
          got["macro_state"] == "none" and got["macro_stance"] == "none" and got["playbook_version"] is None and got["driver"] is None and got["size_rule"] == 1 and got["off_rule"] is False and got["sizeFactor"] is None and got["macro_recent"] is False, json.dumps(got))
    # driver ที่เลือกไม่อยู่ในเวอร์ชันที่ใช้ → null? (เก็บ P9 ไว้ในไอเดียแต่ Playbook ไม่มี → ตกเป็นตัวแรก ไม่ใช่ P9)
    t = save_case("iDrv", "Long", [pbver(1, iso(-72), x="down", xa={"drivers": ["P1"]})], "up", driver="P2", reason="เหตุผลทดสอบ")
    check(f"{tag} บันทึก order: driver ที่ไม่อยู่ใน drivers ของเวอร์ชันที่ใช้ (P2) → ไม่เก็บ P2 (ใช้ตัวแรก P1) · ไม่หลุดรายการ", t["driver"] == "P1", str(t["driver"]))
    t = save_case("iDrv2", "Long", [pbver(1, iso(-72), x="down", xa={"drivers": []})], "up", reason="เหตุผลทดสอบ")
    check(f"{tag} บันทึก order: เวอร์ชันที่ใช้ไม่มี drivers → driver null", t["driver"] is None, str(t["driver"]))
    # ไม้เก่า: ไม่มี field ใหม่ · ยังแสดง/แก้ได้
    old = page.evaluate("""() => { const t = makeTradeObject({id:'told', date:'2026-09-01', sym:'XAUUSD', port:'satB', bias:'Long', entry:4600, sl:4590, tp:null, qty:0.1, mult:100, cur:'USD', status:'plan', prevTrade:null});
        const ed = makeTradeObject({id:'told', date:'2026-09-01', sym:'XAUUSD', port:'satB', bias:'Long', entry:4601, sl:4590, tp:null, qty:0.1, mult:100, cur:'USD', status:'plan', prevTrade:t});
        return {keys: Object.keys(t), editKeys: Object.keys(ed), line: satV3F2cTradeLine(t), entry: ed.entry}; }""")
    newk = {"trend_state", "trend_changed", "macro_state", "macro_stance", "playbook_version", "driver", "size_rule", "off_rule", "macro_note", "macro_recent"}
    check(f"{tag} ไม้เก่า: makeTradeObject ไม่ส่ง = ไม่มี field ใหม่ (แก้ไม้ก็ไม่เพิ่ม) · ไม่มีบรรทัดรายละเอียด · แก้ราคาได้", not (newk & set(old["keys"])) and not (newk & set(old["editKeys"])) and old["line"] == "" and old["entry"] == 4601, json.dumps(old))
    keep = page.evaluate("""() => { const t = getBook('main').trades.find(x=>x.sym==='XAUUSD' && x.port==='satB' && x.macro_state!==undefined); const ed = makeTradeObject({id:t.id, date:t.date, sym:t.sym, port:'satB', bias:t.bias, entry:t.entry+1, sl:t.sl, tp:null, qty:t.qty, mult:t.mult, cur:t.cur, status:'plan', prevTrade:t});
        return {a: ed.macro_state, b: t.macro_state, c: ed.size_rule, d: t.size_rule}; }""")
    check(f"{tag} ไม้ใหม่: แก้ไม้ภายหลังผ่าน makeTradeObject คงค่าเดิมของ prevTrade (ไม่คำนวณใหม่)", keep["a"] == keep["b"] and keep["c"] == keep["d"], json.dumps(keep))
    check(f"{tag} บันทึก order ไม่เขียน macroPlaybook / ไม่แตะ collection 'macro'", page.evaluate("() => window.__pbW.length === 0 && window.__macroTouch.length === 0"), page.evaluate("() => JSON.stringify([window.__pbW, window.__macroTouch])"))
    no_overflow(page, w, f"{tag} หลังบันทึก")


def flow_tests(page, tag, w):
    page.evaluate("() => switchTab('flow')"); page.wait_for_timeout(250)
    seed_pb(page, [])
    bar = txt(page, '#ffAction [data-ff="macro"]')
    check(f"{tag} แถบดำ: ไม่มี Playbook ใช้จริง → '—' + ป้าย 'ยังไม่มี Playbook ใช้จริง'", bar.startswith("Macro —") and "ยังไม่มี Playbook ใช้จริง" in bar and "รอ Playbook" not in bar, bar)
    v1 = pbver(1, iso(-72), x="up", b="up_flat", r="down", u="none")
    v2 = pbver(2, iso(-48), x="up", b="up_flat", r="down", u="none")
    seed_pb(page, [pbver(1, iso(-72), status="draft", x="down"), v1, v2])
    bar = txt(page, '#ffAction [data-ff="macro"]')
    check(f"{tag} แถบดำ: ค่า 'XAU ▲ · BTC ▲▬ · BR ▼ · US —' (active ล่าสุด · ร่างไม่นับ) + ป้าย '2026Q4 v002'", "XAU ▲ · BTC ▲▬ · BR ▼ · US —" in bar and "2026Q4 v002" in bar, bar)
    page.evaluate("() => { window.__scr = 0; document.getElementById('pbPanel').scrollIntoView = function(){ window.__scr++; }; }")
    page.click('#ffAction [data-ff="macro"]'); page.wait_for_timeout(80)
    check(f"{tag} แถบดำ: แตะช่อง Macro = เลื่อนไป #pbPanel", page.evaluate("() => window.__scr") == 1)
    head = txt(page, "#pbPanel .pbHead .pbIcos")
    check(f"{tag} #pbPanel แถวพับ: ไอคอนมีชื่อ asset 'XAU ▲ · BR ▼ · BTC ▲▬ · US —' (MF1 เรียงตามท่าที)", head == "XAU ▲ BR ▼ BTC ▲▬ US —", head)   # MF1: เรียง ▲▼ เต็ม → ▲▬ → ▬ → none
    no_overflow(page, w, f"{tag} Flow (แถวพับ)")

    # [F2d แก้เคสเดิม] บล็อก #ffChanges ('อะไรเปลี่ยนสัปดาห์นี้') ถูกลบ — ข้อมูลเดียวกันย้ายเข้าช่องในแถบดำ · เคสเทียบสัปดาห์ก่อนอยู่ใน run_tests_phase12.py

    # rrgCompute prevQuad: = quad ณ แท่ง last-1 (W) / last-5 (D)
    res = page.evaluate("""() => { let s = 12345; const rnd = () => (s = (s*1103515245 + 12345) % 2147483648) / 2147483648;
        const n = 420; const c = [], b = []; let p = 100, q = 100;
        for(let i=0;i<n;i++){ p *= 1 + (rnd()-0.48)*0.03; q *= 1 + (rnd()-0.5)*0.01; c.push(p); b.push(q); }
        const out = {};
        ['D','W'].forEach(tf=>{ const back = tf==='W' ? 1 : 5;
          const full = rrgCompute(c, c, b, tf), cut = rrgCompute(c.slice(0,n-back), c.slice(0,n-back), b.slice(0,n-back), tf);
          out[tf] = {prevQuad: full.prevQuad, cutQuad: cut.quad, quad: full.quad}; });
        const short = rrgCompute(c.slice(0,120), c.slice(0,120), b.slice(0,120), 'D');
        out.shortErr = !!short.err;
        return out; }""")
    check(f"{tag} rrgCompute: prevQuad (TF D) = quad ณ แท่ง last-5", res["D"]["prevQuad"] == res["D"]["cutQuad"] and res["D"]["prevQuad"] in ("lead", "weak", "imp", "lag"), json.dumps(res["D"]))
    check(f"{tag} rrgCompute: prevQuad (TF W) = quad ณ แท่ง last-1", res["W"]["prevQuad"] == res["W"]["cutQuad"] and res["W"]["prevQuad"] in ("lead", "weak", "imp", "lag"), json.dumps(res["W"]))
    check(f"{tag} RRG_BUILD เพิ่มแล้ว (แคชเก่าที่ไม่มี prevQuad ถูกดึงใหม่)", page.evaluate("() => RRG_BUILD") >= 6)


def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    page.evaluate("()=>{ ['main','fam'].forEach(a=>{ const B = getBook(a); if(B){ if(!B.settings) B.settings = {}; B.settings.satPyrSplit = [100,0,0]; saveBook(a); } }); }")   # PY2: สัดส่วนแบ่งไม้ 100/0/0 = ไม้ 1 เข้าเต็ม RPT เหมือนก่อน PY2 (เคสเดิมไม่ได้ทดสอบการแบ่งไม้)
    try:
        if w > 900: calc_tests(page, tag)
        strategy_tests(page, tag, w)
        card_tests(page, tag, w)
        save_tests(page, tag, w)
        flow_tests(page, tag, w)
        check(f"{tag} ไม่มีการเขียน macroPlaybook (set/add/update/delete) · ไม่แตะ collection 'macro' ตลอดการทดสอบ", page.evaluate("() => window.__pbW.length === 0 && window.__macroTouch.length === 0"), page.evaluate("() => JSON.stringify([window.__pbW, window.__macroTouch])"))
        check(f"{tag} satwMacroFF ไม่มีแล้ว (ไม่มีจุดเรียกเหลือใน source)", page.evaluate("() => typeof satwMacroFF === 'undefined'") and "satwMacroFF" not in open(base.DEFAULT_INDEX, encoding="utf-8").read())
    finally:
        check(f"{tag} console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
        browser.close()


def main():
    with sync_playwright() as pw:
        ui_tests(pw, 1440, 900, "1440px")
        ui_tests(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 11 / F2c) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
