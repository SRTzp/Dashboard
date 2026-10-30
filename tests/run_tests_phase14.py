#!/usr/bin/env python3
"""UI-1b — บล็อกสรุป .sumBlk (token กลางจากแถบ Flow) : (A) Future Strategy · (B) หุ้น Core Port + Heat · (C) จอแคบ/กรอบ · (D) acctDetail
ตัวเลข/ข้อความทุกค่า ก่อน-หลังเท่ากัน (เทียบ index.backup-pre-UI1b.html ในข้อมูลชุดเดียวกัน) — เปลี่ยนแค่การจัดวางและสี
ภาพเก็บที่ tests/screenshots/ui1b-*.png · รัน: python3 run_tests_phase14.py (mock Firestore + fundflow stub)"""
import json, os, re, datetime
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as p11
import run_tests_phase12 as p12
import run_tests_phase13 as p13

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-UI1b.html"))
ENGINE = base.BROWSER_ENGINE
results = []
WARN_RGB = "rgb(242, 184, 75)"       # --sum-warn-val (#F2B84B)
WARN_PILL = "rgb(252, 211, 77)"      # --sum-warn (#FCD34D)
TODAY = datetime.date.today().isoformat()


def retired(name, reason):
    """CL2-a — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่ต้องพิมพ์ไว้ให้ตามรอยได้ (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:1500] + "...(truncated)") if (detail and len(detail) > 1500) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def norm(t): return " ".join((t or "").split())
def fresh(pw, w, h, path=None): return p13.fresh(pw, w, h, path)
def T(*a, **k): return p13.T(*a, **k)
def seed(page, **k): return p13.seed(page, **k)


def shot(page, name, sel=None, **kw):
    # ภาพซีด = .tabSlideIn (fade-in 0.22s ของแท็บ) ถูกสตาร์ตใหม่ตอนแคปองค์ประกอบที่สูงกว่า viewport — ไม่ใช่บั๊กหน้าจริง (ภาพ viewport ปกติ · computed opacity = 1) → ปลดคลาสนี้ก่อนแคป
    try: page.evaluate("() => document.querySelectorAll('.tabSlideIn').forEach(e=>e.classList.remove('tabSlideIn'))"); page.wait_for_timeout(100)
    except Exception: pass
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name), **kw)
        else: page.screenshot(path=os.path.join(SHOTS, name))
    except Exception as e:
        print("shot fail", name, e)


def scope(page, s):
    page.evaluate("(s)=>{ if(planScope!==s) setPlanScope(s); else render(); }", s); page.wait_for_timeout(250)


# ───────────────────────── ชุดข้อมูลกลาง ─────────────────────────
STOCK_MAIN = [T("m1", "core", "open", sym="CCC", entry=100, sl=95, qty=1000), T("m2", "core", "open", sym="CCD", entry=50, sl=48, qty=2000),
              T("m3", "core", "plan", sym="CCE", entry=80, sl=76, qty=1000), T("m4", "core", "open", sym="SSA", entry=100, sl=95, qty=100),   # CL2-a: ไม้ satA เดิมเปลี่ยนเป็น core
              T("m5", "core", "plan", sym="SSB", entry=40, sl=38, qty=100),
              T("m6", "satB", "open", sym="XAUUSD", qty=0.1, mult=100), T("m7", "satB", "plan", sym="S50", qty=2, mult=200, entry=900, sl=890, date=TODAY),
              T("m8", "satB", "plan", sym="S50", qty=2, mult=200, entry=900, sl=890, date=TODAY), T("m9", "satB", "plan", sym="S50", qty=2, mult=200, entry=900, sl=890, date=TODAY)]
STOCK_FAM = [T("f1", "core", "open", sym="ZZZ", entry=100, sl=96, qty=500), T("f2", "satB", "open", sym="XAUUSD", qty=0.05, mult=100, date=TODAY)]


def sat_setup(page):
    """Strategy: XAUUSD Long+Trend▼+Macro▼ (ลด 40%) · BTC Short เต็ม · BRENT ยังไม่ประเมิน (1/2) · S50 งดเทรด"""
    p11.seed_pb(page, [p11.pbver(1, p11.iso(-72), x="down", b="down_flat", r="flat")])
    p11.wk(page, "XAUUSD", "Long", "down", inval=4200)
    p11.wk(page, "BTCUSD", "Short", "down", inval=105000)
    page.evaluate("() => satwWrite('BRENT', {comps:{trend:{v:'up'}}})"); page.wait_for_timeout(120)
    page.evaluate("() => satwWrite('S50', {bias:'None', why:'รอสัญญาณ'})"); page.wait_for_timeout(200)
    page.evaluate("() => { satV3Sel = null; satV3Render(); }"); page.wait_for_timeout(120)


def dark_bg(page, sel):
    return page.evaluate("(s)=>{ const e=document.querySelector(s); return e ? getComputedStyle(e).backgroundColor : null; }", sel)


# ───────────────────────── 0) แถบ Flow หลังย้ายไปใช้ token กลาง ─────────────────────────
FLOW_SELS = ["#ffAction", ".ffActSum", ".ffActFresh", ".ffActFresh i", ".ffActCell[data-ff=regime]", ".ffActCell[data-ff=cap]", ".ffActL", ".ffActRg", ".ffActPill.up", ".ffActPill.dn",
             ".ffActCell[data-ff=cap] .ffActV", ".ffActCell[data-ff=cap] .ffActWhy", ".ffActLead", ".ffActLead small", ".ffActMv", ".ffActMac", ".ffActMac .up", ".ffActTag", ".ffActTag.flip", ".ffActFlip", ".ffActWatch", ".ffActWatch b", ".ffActWatchTx"]
FLOW_PROPS = ["backgroundColor", "color", "fontSize", "fontWeight", "fontFamily", "lineHeight", "borderRadius", "paddingTop", "paddingLeft", "marginBottom", "marginTop", "display", "whiteSpace"]


def flow_setup(page):
    page.evaluate("() => switchTab('flow')"); page.wait_for_timeout(250)
    p11.seed_pb(page, [p12.watch_pb(page, "ดู CPI วันพฤหัส")])
    p12.set_ff(page, {"ACWI_BIL": True, "HYG_IEI": False}, prev={"ACWI_BIL": False, "HYG_IEI": False}, age=1, flip={"ACWI_BIL": 12, "HYG_IEI": 1})
    p12.rrg_rows(page, [p12.row("XLK", "Technology", "lead"), p12.row("XLE", "Energy", "imp", prev="lag")])
    page.wait_for_timeout(150)


def flow_styles(page):
    return page.evaluate("""([sels, props])=>{ const o={}; sels.forEach(s=>{ const e=document.querySelector(s); o[s]= e ? Object.fromEntries(props.map(p=>[p,getComputedStyle(e)[p]])) : null; });
        o['#ffAction cols']=getComputedStyle(document.querySelector('.ffActGrid')).gridTemplateColumns; o['#ffAction cellbg']=getComputedStyle(document.querySelector('.ffActCell')).backgroundColor; return o; }""", [FLOW_SELS, FLOW_PROPS])


def flow_tests(pw, w, h, tag):
    got = {}
    for k, path in (("new", None), ("old", BACKUP)):
        browser, context, page, ce, pe = fresh(pw, w, h, path)
        try:
            flow_setup(page); got[k] = flow_styles(page)
            if k == "new": got["txt"] = norm(page.inner_text("#ffAction")); got["var"] = page.evaluate("() => ['--sum-bg','--sum-cell','--sum-fg','--sum-muted','--sum-pill-up-bg','--sum-pill-dn-bg','--sum-pill-warn-bg','--sum-pill-nt-bg'].map(v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim())")
            else: got["txt_old"] = norm(page.inner_text("#ffAction"))
            if k == "new" and w in (1440, 430): shot(page, f"ui1b-{w}-flow-token.png", "#ffAction")
        finally:
            browser.close()
    diffs = {s: [got["new"][s], got["old"][s]] for s in got["new"] if got["new"][s] != got["old"][s]}
    present = [s for s in FLOW_SELS if got["new"][s] is not None]
    check(f"{tag} แถบ Flow หลังใช้ token กลาง: computed style หลัก (bg · สีตัว · ขนาด/น้ำหนักฟอนต์ · padding · radius) เท่าก่อนย้ายทุกจุด ({len(present)} องค์ประกอบ)", not diffs and len(present) >= 18, json.dumps(diffs, ensure_ascii=False)[:1200])
    check(f"{tag} แถบ Flow: ข้อความเท่าเดิมทุกตัวอักษร", got["txt"] == got["txt_old"], got["txt"][:200] + " || " + got["txt_old"][:200])
    check(f"{tag} token กลางมีครบ (--sum-bg #16191E · --sum-cell #262A31 · --sum-fg · --sum-muted · pill up/dn/warn/nt)", got["var"][:2] == ["#16191E", "#262A31"] and all(got["var"]), json.dumps(got["var"]))


# ───────────────────────── (A) Future — Strategy ─────────────────────────
def strategy_numbers(page):
    return page.evaluate("""() => { const wk = satwViewWeek || wpWeekKey(); const o={};
        SAT_ASSETS.forEach(a=>{ const w=satwWeek(wk,a.key), at=satwAtTime(wk); const m=satV3TileBadgeSub(a.key,w,at); o[a.key]={badge:m.badge, sub:m.sub, sub2:m.sub2||null}; });
        o.tiles = SAT_ASSETS.filter(a=>a.key!=='BRENT').map(a=>{ const e=document.querySelector('.ui-tile[data-key="'+a.key+'"]'); return e ? e.innerText.replace(/[\\s·]+/g,'') : null; });   /* WA1fix: เทียบเฉพาะ 3 ช่องที่เลือก (ไม่นับ Brent) */
        o.meta = sat7dAccts().map(a=>{ const b=sat7dAcctBase(a.id); return [a.name, b.cap, b.heatPct, b.nNew, b.rpt, b.cnt.n, b.cnt.since?1:0]; });
        const strip=document.querySelector('#satV3Panel .ui-acctStrip'); const meta=document.querySelector('#satV3Panel [data-sat-meta]');
        o.stripTxt = [...document.querySelectorAll('#satV3Panel .ui-acctStrip')].map(e=>e.innerText.replace(/[\\s·]+/g,'')).concat([...document.querySelectorAll('#satV3Panel .sumMr')].map(e=>e.innerText.replace(/[\\s·]+/g,'')));
        o.warnOld = [...document.querySelectorAll('#satV3Panel .ui-acctF.ui-warn')].map(e=>e.innerText.replace(/[\\s·]+/g,'')); o.warnNew = [...document.querySelectorAll('#satV3Panel .sumM.warn')].map(e=>e.innerText.replace(/[\\s·]+/g,''));
        o.editor = (document.querySelector('#satV3Panel .ui-editor')||{}).innerHTML || null;
        return o; }""")


def future_data(pw, w, h, path):
    browser, context, page, ce, pe = fresh(pw, w, h, path)
    try:
        page.add_style_tag(content=".ui-acctStrip .ui-acctF.ui-sec{display:inline!important}")
        seed(page, main=STOCK_MAIN, fam=STOCK_FAM); scope(page, "future"); sat_setup(page)
        page.evaluate("() => ['main','fam'].forEach(a=>{ getBook(a).settings.satRisk={rpt:1.25, rptHi:1.5}; })")   # SR1 — fixture: ค่าเดิม 1.25/1.5 เพื่อเทียบกับไฟล์สำรองก่อนแก้
        page.evaluate("() => { const o=sat7dAcctBase; window.sat7dAcctBase=(id)=>{ const b=o(id); return id==='main' ? Object.assign({}, b, {heatPct:9, nNew:3}) : b; }; satV3Sel='XAUUSD'; satV3Render(); }"); page.wait_for_timeout(200)
        return strategy_numbers(page)
    finally:
        browser.close()


def future_tests(pw, w, h, tag):
    new, old = future_data(pw, w, h, None), future_data(pw, w, h, BACKUP)
    keys = ["XAUUSD", "BTCUSD", "S50", "meta"]   # WA1fix: Brent ไม่ได้เลือก (เพดาน 3)
    check(f"{tag} Future: PF3 ตัวเลขแถบ Sat ต่อบัญชี (ถัง·heat·ไม้ใหม่·RPT·ไม้ Sat) เท่าไฟล์ก่อน UI1b ทุกค่า · tile ไม่มี badge Bias (badge ว่าง) และ sub = รับ/ต้านเท่านั้น (ไม่มี Trend Shift)", new["meta"] == old["meta"] and all(new[k]["badge"] == "" and "Trend Shift" not in new[k]["sub"] and "รับ" in new[k]["sub"] and "ต้าน" in new[k]["sub"] for k in ("XAUUSD", "BTCUSD", "S50")), json.dumps({"n": {k: new[k] for k in keys[:3]}, "m": [new["meta"], old["meta"]]}, ensure_ascii=False))
    check(f"{tag} Future: PF3 ข้อความ tile = ชื่อ + [+ แผน] + [＋ วางลิงก์กราฟ] + รับ/ต้าน (ไม่มีไอคอนทิศ/ป้าย Long-Short/ขนาดไม้/Trend Shift) · S50 ยังมี 'รอสัญญาณ'", len(new["tiles"]) == 3 and all(t and "+แผน" in t and "รับ" in t and "ต้าน" in t and "TrendShift" not in t and "ขนาดไม้" not in t and "Long" not in t and "Short" not in t and "▲" not in t and "▼" not in t for t in new["tiles"]) and "รอสัญญาณ" in new["tiles"][2], json.dumps(new["tiles"], ensure_ascii=False))
    check(f"{tag} Future: แถบ Sat ต่อบัญชี — ข้อความเท่าเดิมทุกค่า (ถัง Sat · heat · ไม้ใหม่ · RPT · ไม้ Sat ต่อบัญชี) และค่าเตือนเดิม (ไม้ใหม่เกิน) เป็น warn เหมือนเดิม",
          [x.replace("DD0%ปกติ", "").split("RPT")[0] for x in new["stripTxt"]] == [x.split("RPT")[0] for x in old["stripTxt"]] and all("RPTMain1.25%Tactical2%" in x and "ไม้Sat" not in x for x in new["stripTxt"]) and len(new["stripTxt"]) == 2 and old["warnOld"] == new["warnNew"] and len(new["warnNew"]) == 2,   # PV2c: RPT เดิม + ไม้ Sat n/m → RPT Main x% · Tactical y% (ส่วนก่อน RPT เทียบตรงเท่าเดิม)
          json.dumps({"new": new["stripTxt"], "old": old["stripTxt"], "wo": old["warnOld"], "wn": new["warnNew"]}, ensure_ascii=False))
    import re as _re
    _nb = lambda h: _re.sub(r'\s*<button[^>]*data-bias-neutral[^>]*>Neutral</button>', '', h or '')   # PV2b: เพิ่มปุ่ม Neutral 1 ปุ่ม — นอกจากนั้นเท่าเดิม
    check(f"{tag} Future: PF3 ตัวแก้ Strategy (legacy): ไม่มีปุ่ม Bias/ช่อง Trend Shift · ยังมีแนวรับ/ต้าน (satwSetSupport/Resistance) + บล็อก Macro + ช่องความเห็น", bool(new["editor"]) and "ui-bias-btn" not in new["editor"] and "data-bias-neutral" not in new["editor"] and "Trend Shift" not in new["editor"] and "satwSetSupport" in new["editor"] and "satwSetResistance" in new["editor"] and 'data-macro-block="1"' in new["editor"] and "data-my-opinion" in new["editor"], (new["editor"] or "")[:200])


def future_ui(page, tag, w, h):
    seed(page, main=STOCK_MAIN, fam=STOCK_FAM); scope(page, "future"); sat_setup(page)
    q = lambda js, a=None: page.evaluate(js, a)
    n = q("() => ({blk: document.querySelectorAll('#satV3Panel .sumBlk').length, meta: document.querySelectorAll('#satV3Panel .sumBlk .sumMr').length, tiles: document.querySelectorAll('#satV3Panel .sumBlk .ui-tile.sumCell').length, old: document.querySelectorAll('#satV3Panel .ui-acctStrip, #satV3Panel .ui-tiles:not(.sumGrid)').length, dark: document.querySelectorAll('#satV3Panel .sumBlk').length, head: (document.querySelector('#satV3Panel .sumBlk .sumT')||{}).innerText, rng:(document.querySelector('#satV3Panel .sumBlk .sumR')||{}).innerText, hint:(document.querySelector('#satV3Panel .sumBlk .sumHint')||{}).innerText})")
    check(f"{tag} Future: บล็อกสรุป 1 ก้อน = หัว 'Strategy สัปดาห์นี้'+ช่วงวันที่ · แถบ Sat 2 บัญชี (2 บรรทัด) · 3 tile ที่เลือก (.sumCell · WA1fix) · ไม่มีแถบบัญชีขาว/กริด tile เดิมแยก · 'แตะช่องเพื่อแก้' ใต้หัว",
          n["blk"] == 1 and n["meta"] == 2 and n["tiles"] == 3 and n["old"] == 0 and n["head"] == "Strategy สัปดาห์นี้" and n["rng"] and n["hint"] == "แตะช่องเพื่อแก้", json.dumps(n, ensure_ascii=False))
    bg = dark_bg(page, "#satV3Panel .sumBlk")
    check(f"{tag} Future: พื้นบล็อกเป็นค่าเดิมของแถบ Flow (rgb(22,25,30) ไม่ใช่ดำสนิท) · พื้นช่อง rgb(38,42,49)", bg == "rgb(22, 25, 30)" and dark_bg(page, "#satV3Panel .sumBlk .ui-tile") == "rgb(38, 42, 49)", bg)
    # pill
    q("() => { satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','BRENT']); satV3Render(); }"); page.wait_for_timeout(200)   # WA1fix: Brent ไม่อยู่ใน pick เริ่มต้น (เพดาน 3) → เลือกชั่วคราวเพื่อตรวจ pill ของ Brent แล้วคืน
    q("() => { satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','S50']); satV3Render(); }"); page.wait_for_timeout(200)
    check(f"{tag} Future: PF3 ไม่มีข้อความ pill เดิมบนทั้ง 3 tile (Long · ลด 40% / ขนาดไม้ เต็ม / ยังไม่ประเมิน / งดเทรด) · ไม่มี pill สี warn/dn/nt", q("() => [...document.querySelectorAll('.ui-tile')].every(e=>!/ลด 40%|ขนาดไม้ เต็ม|ยังไม่ประเมิน|งดเทรด/.test(e.innerText))") and q("() => document.querySelectorAll('.ui-tile .ui-pill, .ui-tile .ui-tile-b').length") == 0)
    check(f"{tag} Future: PF3 ไม่มีช่องจาง — ทุก tile opacity = 1 (ไม่มี ui-dim)", q("() => [...document.querySelectorAll('.ui-tile')].every(e=>getComputedStyle(e).opacity==='1' && !e.classList.contains('ui-dim'))"))
    check(f"{tag} Future: PF1 — tile ไม่มี pill Bias (.ui-tile-b) และมีปุ่ม + แผน ทุกช่อง", q("() => document.querySelectorAll('.ui-tile .ui-tile-b').length") == 0 and q("() => document.querySelectorAll('.ui-tile .ui-btn-pri').length") >= 3)
    # แตะ tile → ตัวแก้ต่อใต้บล็อก
    page.click('.ui-tile[data-key="BTCUSD"] .ui-tile-th .ui-tile-a'); page.wait_for_timeout(200)
    ed = q("""() => { const b=document.querySelector('#satV3Panel .sumBlk'), e=document.querySelector('#satV3Panel .ui-editor'); if(!e) return null; const rb=b.getBoundingClientRect(), re=e.getBoundingClientRect(), cs=getComputedStyle(e);
        const sel=document.querySelector('.ui-tile.ui-sel'); return {adj: b.nextElementSibling===e, gap: Math.round(re.top-rb.bottom), bg: cs.backgroundColor, bt: cs.borderTopWidth, bw: cs.borderLeftWidth, bc: cs.borderLeftColor, asset:e.dataset.asset, sel: sel && sel.dataset.key, selShadow: sel && getComputedStyle(sel).boxShadow, hasEd: b.classList.contains('hasEd'), rbr: getComputedStyle(b).borderBottomLeftRadius}; }""")
    check(f"{tag} Future: แตะ tile → ตัวแก้เปิดเป็นแผ่นพื้นขาวต่อใต้บล็อกทันที (ไม่มีช่องว่าง · ขอบบนติดบล็อก · ขอบรอบเข้ม) · tile ที่เลือก = เส้นขอบสว่าง",
          ed and ed["adj"] and ed["gap"] == 0 and ed["bg"] == "rgb(255, 255, 255)" and ed["bt"] == "0px" and ed["bw"] == "2px" and ed["bc"] == "rgb(22, 25, 30)" and ed["asset"] == "BTCUSD" and ed["sel"] == "BTCUSD" and ed["selShadow"] != "none" and ed["rbr"] == "0px", json.dumps(ed))
    check(f"{tag} Future: PF3 ตัวแก้เปิดแล้วมีบล็อก Macro อ่านอย่างเดียว + ช่องความเห็นของฉัน (ส่วนที่ PF1 คงไว้แทนฟอร์ม Bias เดิม)", page.locator(".ui-editor[data-asset=\"BTCUSD\"] [data-macro-block]").count() == 1 and page.locator(".ui-editor[data-asset=\"BTCUSD\"] [data-my-opinion]").count() >= 1)
    check(f"{tag} Future: PF1 — ตัวแก้ legacy ไม่มีปุ่ม Bias/Trend Shift · ยังมีแนวรับ/ต้าน", page.locator(".ui-editor[data-asset=\"BTCUSD\"] .ui-bias-btn").count() == 0 and page.locator(".ui-editor input[onchange*=\"satwSetSupport\"]").count() == 1 and page.locator(".ui-editor input[onchange*=\"satwSetResistance\"]").count() == 1)
    # "+ แผน"
    before = q("() => satIdeasList.filter(x=>x.v3).length")
    page.click('.ui-tile[data-key="XAUUSD"] .ui-btn-pri:has-text("+ แผน")'); page.wait_for_timeout(500)
    after = q("() => satIdeasList.filter(x=>x.v3).length")
    check(f"{tag} Future: '+ แผน' ทำงานเดิม (สร้างร่างแผนใหม่ 1 ใบ) · ไม่เปลี่ยน tile ที่เลือก", after == before + 1, f"{before}->{after}")
    btn = q("""() => { const e=document.querySelector('.ui-tile[data-key="XAUUSD"] .ui-btn-pri'), t=document.querySelector('.ui-tile[data-key="XAUUSD"]'); const r=e.getBoundingClientRect(), rt=t.getBoundingClientRect(), cs=getComputedStyle(e);
        return {h:r.height, w:r.width, right: Math.round(rt.right-r.right), top: Math.round(r.top-rt.top), bg:cs.backgroundColor, fg:cs.color}; }""")
    check(f"{tag} Future: ปุ่ม '+ แผน' พื้นสว่าง ตัวเข้ม อยู่มุมขวาบนของช่อง" + (" · สูง ≥ 36px (มือถือ)" if w <= 700 else ""),
          btn["bg"] == "rgb(244, 245, 247)" and btn["fg"] == "rgb(22, 25, 30)" and btn["right"] <= 12 and btn["top"] <= 16 and (btn["h"] >= 36 or w > 700), json.dumps(btn))
    th = q("() => Math.min(...[...document.querySelectorAll('.sumBlk .ui-tile-th')].map(e=>e.getBoundingClientRect().height))")
    check(f"{tag} Future: เป้าแตะหัว tile ≥ 36px" if w <= 700 else f"{tag} Future: เป้าแตะหัว tile สูงพอ (≥ 30px)", th >= (36 if w <= 700 else 30) - 0.5, str(th))
    ov = q("""() => [...document.querySelectorAll('.sumBlk .ui-tile')].map(t=>{ const a=t.querySelector('.ui-tile-a'), b=t.querySelector('.ui-btn-pri'); if(!b) return {n:a.innerText, btn:false};
        const ra=a.getBoundingClientRect(), rb=b.getBoundingClientRect(); const hit = ra.left < rb.right && rb.left < ra.right && ra.top < rb.bottom && rb.top < ra.bottom;
        return {n:a.innerText, btn:true, hit, pos:getComputedStyle(b).position, fit:a.scrollWidth<=a.clientWidth+1, h:Math.round(rb.height)}; })""")
    check(f"{tag} Future: กรอบปุ่ม '+ แผน' ไม่ซ้อนทับกรอบชื่อ asset (bounding box ไม่ intersect) · ปุ่มไม่ใช่ absolute · ชื่อไม่ถูกตัด · ทุก tile ที่มีปุ่ม" + (" · ปุ่มสูง ≥ 36px" if w <= 700 else ""),
          sum(1 for x in ov if x["btn"]) >= 2 and all((not x["hit"]) and x["pos"] != "absolute" and x["fit"] and (x["h"] >= 36 or w > 700) for x in ov if x["btn"]), json.dumps(ov, ensure_ascii=False))
    names = q("() => [...document.querySelectorAll('.sumBlk .ui-tile-a')].map(e=>[e.innerText, e.scrollWidth<=e.clientWidth+1])")
    check(f"{tag} Future: ชื่อ asset ไม่ถูกตัด (ไม่ขึ้น …) ทั้ง 4 ช่อง", all(x[1] for x in names), json.dumps(names, ensure_ascii=False))
    # grid + สูงเท่ากัน
    g = q("""() => { const t=[...document.querySelectorAll('.sumBlk .ui-tile')].map(e=>{const r=e.getBoundingClientRect(); return {top:Math.round(r.top), h:Math.round(r.height), l:Math.round(r.left)}}); const cols=getComputedStyle(document.querySelector('.sumBlk .ui-tiles')).gridTemplateColumns.split(' ').length; return {t, cols}; }""")
    rows = {}
    for x in g["t"]: rows.setdefault(x["top"], []).append(x["h"])
    check(f"{tag} Future: grid {'4 คอลัมน์ (MacBook)' if w > 700 else '2×2 (≤700px)'} · tile ในแถวเดียวกันสูงเท่ากัน", g["cols"] == (4 if w > 700 else 2) and all(len(set(v)) == 1 for v in rows.values()) and (len(rows) == 1 if w > 700 else len(rows) == 2), json.dumps(g))
    fs = q("""() => { const rem=parseFloat(getComputedStyle(document.documentElement).fontSize); let mn=99, bad=[]; const mono=getComputedStyle(document.documentElement).getPropertyValue('--mono').split(',')[0].replace(/['"]/g,'').trim().toLowerCase();
        document.querySelectorAll('.sumBlk *').forEach(e=>{ if(!e.children.length && e.textContent.trim() && e.offsetParent!==null){ const cs=getComputedStyle(e), f=parseFloat(cs.fontSize); if(f<mn) mn=f; if(cs.fontFamily.toLowerCase().includes(mono) || /monospace/i.test(cs.fontFamily)) bad.push(e.textContent.trim().slice(0,20)); } }); return {mn:mn/rem, bad}; }""")
    check(f"{tag} Future: บล็อกสรุป — ตัวเล็กสุด ≥ 0.72rem · ไม่ใช้ var(--mono)", fs["mn"] >= 0.72 - 0.005 and not fs["bad"], json.dumps(fs))
    sw = q("() => document.documentElement.scrollWidth")
    check(f"{tag} Future: ไม่ล้นแนวนอน (scrollWidth={sw} ≤ {w})", sw <= w + 1)
    sat_tile_overflow = q("() => [...document.querySelectorAll('.sumBlk .ui-tile, .sumBlk .sumMr')].filter(e=>e.scrollWidth>e.clientWidth+1).length")
    check(f"{tag} Future: ไม่มี tile/บรรทัด Sat ล้นกรอบ", sat_tile_overflow == 0, str(sat_tile_overflow))
    if w in (1440, 430):
        page.evaluate("() => { satV3Sel='XAUUSD'; satV3Render(); }"); page.wait_for_timeout(150)
        # ให้เห็น Trade Plans ด้วย: แคปทั้งแผง
        shot(page, f"ui1b-{w}-future-strategy.png", "#satV3Panel")
        page.evaluate("() => { satV3Sel=null; satV3Render(); }"); page.wait_for_timeout(150)
        shot(page, f"ui1b-{w}-future-block.png", "#satV3Panel .sumBlk")
    page.evaluate("() => { satV3Sel=null; satV3Render(); }")


# ───────────────────────── (B) หุ้น — Core Port + Heat ─────────────────────────
def core_numbers(page):
    return page.evaluate("""() => { const T=e=>e?e.innerText.replace(/\\s+/g,' ').trim():null; const o={};
        const oldCore=document.querySelector('#ports .port[data-priv="p-port-core"]');
        const newCore=document.querySelector('#ports .sumSec[data-sum-sec="core"]');
        o.core=T(oldCore)||T(newCore); o.isNew=!!newCore;
        o.kv=[...document.querySelectorAll('#strip .acctDetail')].map(d=>[...d.querySelectorAll('.acctKV b')].map(b=>b.innerText.replace(/\\s+/g,'')));
        o.kvLbl=[...document.querySelectorAll('#strip .acctDetail')].map(d=>[...d.querySelectorAll('.acctKV>span')].map(b=>b.innerText.replace(/\\s+/g,' ').trim()));
        return o; }""")


def parse_port(t, new, sat=False):
    """ดึงตัวเลขออกจากข้อความบล็อกเดิม/ใหม่ให้อยู่รูปเดียวกัน"""
    g = lambda pat: (re.search(pat, t) or [None])
    m = {}
    m["cap"] = g(r"ทุน (.+?) · ([\d.,]+)% ของทุนรวม")
    cap = re.search(r"ทุน ([฿$][^·]*?) · ([\d.,]+)% ของทุนรวม", t)
    out = {"cap": (cap.group(1), cap.group(2)) if cap else None}
    if new:
        # 7E-1: บล็อกใหม่ — ความเสี่ยงค้าง '฿x · ≈ y% ของบัญชี' (ฐานบัญชีเหมือนเดิม) · แผนที่รอ 'เสี่ยง +฿x · z% ของถัง' (% เปลี่ยนฐาน → เทียบเฉพาะ ฿) · ตำแหน่ง 'n ตัว'
        o = re.search(r"(฿[\d,]+) · ≈ ([\d.,]+)% ของบัญชี", t); p = re.search(r"เสี่ยง \+(฿[\d,]+)", t); ps = re.search(r"ตำแหน่ง (\d+) ตัว", t); pc = re.search(r"แผนที่รอ \(Planned\) (\d+) ตัว", t)
        out.update(open=(o.group(1), o.group(2)) if o else None, plan=(p.group(1),) if p else None, pos=(ps.group(1), pc.group(1) if pc else "0") if ps else None)
    else:
        if sat:
            o = re.search(r"Open Risk (\S+) ([\d.,]+)%", t, re.I); p = re.search(r"Planned (\S+) ([\d.,]+)%", t, re.I); ps = re.search(r"Positions (\d+) / (\d+) open / plan", t, re.I)
        else:
            o = re.search(r"Open Risk (\S+) \(([\d.,]+)%\)", t); p = re.search(r"Planned (\S+) \(([\d.,]+)%\)", t); ps = re.search(r"Positions (\d+) open / (\d+) plan", t)
        out.update(open=(o.group(1), o.group(2)) if o else None, plan=(p.group(1),) if p else None, pos=(ps.group(1), ps.group(2)) if ps else None)   # เทียบเฉพาะค่าที่ยังอยู่ (7E-1: plan เทียบ ฿ อย่างเดียว)
    return out


def stock_data(pw, w, h, path, main, fam):
    browser, context, page, ce, pe = fresh(pw, w, h, path)
    try:
        page.add_style_tag(content=".ui-acctStrip .ui-acctF.ui-sec{display:inline!important}")   # เดิมซ่อนช่องรองที่ ≤430 — เปิดให้เทียบค่าครบ
        seed(page, main=main, fam=fam); scope(page, "stock")
        page.evaluate("() => { document.querySelectorAll('#strip .acctCard').forEach(c=>c.classList.add('open')); }")
        return core_numbers(page)
    finally:
        browser.close()


def stock_tests(pw, w, h, tag):
    for label, main, fam in (("ปกติ", STOCK_MAIN, STOCK_FAM), ("เกิน limit", STOCK_MAIN + [T("mx", "core", "plan", sym="BIG", entry=100, sl=50, qty=200000)], STOCK_FAM)):
        new, old = stock_data(pw, w, h, None, main, fam), stock_data(pw, w, h, BACKUP, main, fam)
        pn, po = parse_port(new["core"], True), parse_port(old["core"], False)
        ok = all(pn[k] is not None for k in pn) and pn == po
        check(f"{tag} หุ้น ({label}): Core — ทุน · Open Risk (฿/%) · Planned · Positions ก่อน-หลังเท่ากัน (CL2-d: ตัด Heat 1R · รวม%/limit ออกแล้ว · 7E-1: Open = ฿ + % ของบัญชี · Planned เทียบ ฿ · Positions จากช่อง 'ตำแหน่ง'/'แผนที่รอ')", ok, json.dumps({"new": pn, "old": po}, ensure_ascii=False))
        retired(f"{tag} หุ้น ({label}): satA — ตัวเลขทุกค่าก่อน-หลังเท่ากัน", "CL2-a ลบ Sat.A — ไม่มีบล็อก satA ในแท็บหุ้นแล้ว")
        check(f"{tag} หุ้น ({label}): รายละเอียดแถบบัญชี (acctDetail) ทุกค่าเท่ากัน (CL2-d: ตัดช่อง Heat 1R ออกจากฝั่งเก่าก่อนเทียบ)", new["kv"] == [[v for i, v in enumerate(r) if i != 2] for r in old["kv"]] and new["kv"], json.dumps({"new": new["kv"], "old": old["kv"]}, ensure_ascii=False))
        check(f"{tag} หุ้น ({label}): ป้ายรายละเอียดเดิมเหมือนเดิม ยกเว้น 'Open' (คำอธิบายเดิมย้ายไป tooltip)", [l[0] for l in old["kvLbl"]] == ["ความเสี่ยงค้าง (Open) · % ของทุนรวมบัญชี"] * len(old["kvLbl"]) and [l[0] for l in new["kvLbl"]] == ["Open"] * len(new["kvLbl"]) and [l[1:] for l in new["kvLbl"]] == [[v for i, v in enumerate(l[1:]) if i != 1] for l in old["kvLbl"]], json.dumps([new["kvLbl"], old["kvLbl"]], ensure_ascii=False))


def stock_ui(page, tag, w, h):
    seed(page, main=STOCK_MAIN, fam=STOCK_FAM); scope(page, "stock")
    q = lambda js, a=None: page.evaluate(js, a)
    n = q("() => ({blk: document.querySelectorAll('#ports .sumBlk').length, sec: [...document.querySelectorAll('#ports .sumBlk .sumSec')].map(e=>e.dataset.sumSec), oldCard: document.querySelectorAll('#ports .port, #ports .ui-acctStrip').length, dark: document.querySelectorAll('#ports .sumBlk, #ports [style*=\"16191E\"]').length, head:[...document.querySelectorAll('#ports .sumSec .sumT')].map(e=>e.innerText), cells:[...document.querySelectorAll('#ports .sumSec')].map(s=>[...s.querySelectorAll('.sumCell .sumL')].map(e=>e.innerText))})")
    check(f"{tag} หุ้น: บล็อกสรุป 1 ก้อน (#portsSum) — Core Port (CL2-a: เหลือแถวเดียว — satA ถูกลบ) · ช่อง ความเสี่ยงถึง Stop (ชั้น 2 · จากราคาปิด) / เงินที่ถือ / ตำแหน่ง / แผนที่รอ (7E-1: แทน Open Risk / Planned)",
          n["blk"] == 1 and n["sec"] == ["core"] and n["oldCard"] == 0 and n["head"] == ["Core Port"] and all(c == ["ความเสี่ยงถึง Stop (ชั้น 2 · จากราคาปิด) · % ของถัง Core", "งบ W / L · เงินที่ถือ", "ตำแหน่ง", "ประตูบันได L", "แผนที่รอ (Planned)"] for c in n["cells"]), json.dumps(n, ensure_ascii=False))
    check(f"{tag} หุ้น: พื้นบล็อก rgb(22,25,30) · ช่อง rgb(38,42,49)", dark_bg(page, "#portsSum") == "rgb(22, 25, 30)" and dark_bg(page, "#portsSum .sumCell") == "rgb(38, 42, 49)")
    hd = q("() => { const s=document.querySelector('#ports .sumSec[data-sum-sec=core]'); return {sumR: s.querySelector('.sumR').innerText.replace(/\\s+/g,' '), big: [...s.querySelectorAll('.sumBig')].map(e=>e.innerText.replace(/\\s+/g,' ')), nw:getComputedStyle(s.querySelector('[data-sum=open] .sumBig')).whiteSpace}; }")
    check(f"{tag} หุ้น: หัวขวา 'ทุน ฿x · y% ของทุนรวม' · sumBig ช่องแรก 'x% / 20%' ช่องสอง 'y% ของถัง' · ตัวเลข nowrap (7E-1: ตัด sumMeta 'Positions n open · n plan' — ย้ายเป็นช่อง 'ตำแหน่ง')",
          re.match(r"^ทุน ฿[\d,]+ · [\d.]+% ของทุนรวม", hd["sumR"]) and re.match(r"^ตอนนี้ [\d.]+%$", hd["big"][0]) and re.match(r"^[\d.]+% ของถัง$", hd["big"][1]) and hd["nw"] == "nowrap", json.dumps(hd, ensure_ascii=False))
    ov = q("() => [...document.querySelectorAll('#ports .sumSec')].map(s=>({k:s.dataset.sumSec, warn: s.querySelectorAll('.sumCell.sumLv-warn, .sumCell.sumLv-over').length, over: !!s.querySelector('[data-stop-buy]')}))")
    check(f"{tag} หุ้น: ความเสี่ยงค้าง < เหลืองที่ → ไม่มีช่องเหลือง/แดง · ไม่มีป้าย 'งดซื้อเพิ่ม' (7E-1: แทนป้าย 'เกิน limit')", all(x["warn"] == 0 and not x["over"] for x in ov), json.dumps(ov))
    retired(f"{tag} หุ้น: แถบ heat เดิมปรับเข้ากับพื้นเข้ม (รางสี rgb(58,63,72) ไม่ใช่พื้นขาว)", "CL2-d ลบช่อง Heat 1R (heatbar) ออกจากบล็อกสรุป Core")
    # 👁 ทั้งบล็อกใหม่
    txt0 = q("() => document.querySelector('#ports .sumSec[data-sum-sec=core]').innerText")
    page.click('#ports .sumSec[data-sum-sec=core] .privEye'); page.wait_for_timeout(250)
    hid = q("() => ({core: document.querySelector('#ports .sumSec[data-sum-sec=core]').innerText, eyes: document.querySelectorAll('#ports .privEye').length})")
    check(f"{tag} หุ้น: 👁 ในบล็อกใหม่ซ่อนตัวเลขเงิน (฿…→X) ของ Core และคลิกอีกครั้งคืนค่าเดิม (CL2-a: เหลือ Core แถวเดียว ตาเดียว)",
          re.search(r"฿X", hid["core"]) and not re.search(r"฿\d", hid["core"]) and hid["eyes"] == 1, json.dumps(hid, ensure_ascii=False))
    page.click('#ports .sumSec[data-sum-sec=core] .privEye'); page.wait_for_timeout(250)
    txt1 = q("() => document.querySelector('#ports .sumSec[data-sum-sec=core]').innerText")
    check(f"{tag} หุ้น: 👁 เปิดกลับ = ข้อความเดิมทุกตัวอักษร", txt1 == txt0)
    # acctDetail 👁
    set_open(page, True, True)
    d0 = q("() => document.querySelector('#strip .acctCard .acctDetail').innerText")
    page.click('#strip .acctCard .acctDetail .privEye'); page.wait_for_timeout(250); set_open(page, True, True)
    d1 = q("() => document.querySelector('#strip .acctCard .acctDetail').innerText")
    check(f"{tag} หุ้น: 👁 ในรายละเอียดแถบบัญชี (acctDetail) ยังซ่อน/แสดงตัวเงินได้", "฿X" in d1 and "฿X" not in d0)
    page.click('#strip .acctCard .acctDetail .privEye'); page.wait_for_timeout(250)
    set_open(page, False, False)
    # over
    seed(page, main=STOCK_MAIN + [T("mx", "core", "open", sym="BIG", entry=100, sl=50, qty=200000)], fam=STOCK_FAM); scope(page, "stock")
    ov = q("""() => { const s=document.querySelector('#ports .sumSec[data-sum-sec=core]'); const c=s.querySelector('[data-sum=open]'); return {cell:c.classList.contains('sumLv-over'), big:getComputedStyle(c.querySelector('.sumBig')).color,
        badge: !!s.querySelector('[data-stop-buy]')}; }""")
    check(f"{tag} หุ้น: ความเสี่ยงค้าง ≥ เพดานชั้น 2 → ช่องแดง (สี #FCA5A5) · ป้าย 'งดซื้อเพิ่ม' (7E-1: แทนช่อง Open Risk warn + ป้าย 'เกิน limit' — ทดสอบด้วยไม้ open ที่เสี่ยงเกินเพดาน)", ov["cell"] and ov["big"] == "rgb(252, 165, 165)" and ov["badge"], json.dumps(ov))
    seed(page, main=STOCK_MAIN, fam=STOCK_FAM); scope(page, "stock")
    # กติกา: ช่องในแถวเดียวกันสูงเท่ากัน
    hh = q("() => [...document.querySelectorAll('#ports .sumSec')].map(s=>{ const c=[...s.querySelectorAll('.sumCell')].map(e=>{const r=e.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.height)];}); const rows={}; c.forEach(x=>{ (rows[x[0]]=rows[x[0]]||[]).push(x[1]); }); return Object.values(rows).every(v=>new Set(v).size===1); })")
    check(f"{tag} หุ้น: ช่อง Core ในแถวเดียวกันสูงเท่ากัน", all(hh), json.dumps(hh))
    cols = q("() => getComputedStyle(document.querySelector('#ports .sumG3')).gridTemplateColumns.split(' ').length")
    check(f"{tag} หุ้น: grid ช่อง {'3 คอลัมน์ (desktop)' if w > 700 else '2 คอลัมน์ (≤700px)'} (7E-1: .sumG3 แทน .sumG2)", cols == (3 if w > 700 else 2), str(cols))
    fs = q("""() => { const rem=parseFloat(getComputedStyle(document.documentElement).fontSize); let mn=99, bad=[]; const mono=getComputedStyle(document.documentElement).getPropertyValue('--mono').split(',')[0].replace(/['"]/g,'').trim().toLowerCase();
        document.querySelectorAll('#ports .sumBlk *').forEach(e=>{ if(!e.children.length && e.textContent.trim() && e.offsetParent!==null){ const cs=getComputedStyle(e), f=parseFloat(cs.fontSize); if(f<mn) mn=f; if(cs.fontFamily.toLowerCase().includes(mono)||/monospace/i.test(cs.fontFamily)) bad.push(e.textContent.trim().slice(0,20)); } }); return {mn:mn/rem, bad}; }""")
    check(f"{tag} หุ้น: บล็อกสรุป — ตัวเล็กสุด ≥ 0.72rem · ไม่ใช้ var(--mono)", fs["mn"] >= 0.72 - 0.005 and not fs["bad"], json.dumps(fs))
    ovf = q("() => ({sw: document.documentElement.scrollWidth, over: [...document.querySelectorAll('#ports .sumBlk *')].filter(e=>e.scrollWidth>e.clientWidth+1 && getComputedStyle(e).overflow==='visible' && e.offsetParent!==null && e.children.length===0).length})")
    check(f"{tag} หุ้น: ไม่ล้นแนวนอน (scrollWidth={ovf['sw']} ≤ {w}) · ไม่มีข้อความล้นกรอบ", ovf["sw"] <= w + 1 and ovf["over"] == 0, json.dumps(ovf))
    if w in (1440, 430):
        shot(page, f"ui1b-{w}-stock-block.png", "#portsSum")
        shot(page, f"ui1b-{w}-stock-table.png", "#planSections")
    both = q("() => document.querySelectorAll('.sumBlk').length")
    check(f"{tag} หุ้น: บล็อกสรุป (.sumBlk) ในสโคปหุ้นมี 1 ก้อน (ไม่นับแถบ Flow ที่อยู่คนละแท็บ)", q("() => [...document.querySelectorAll('#tabPlan .sumBlk')].filter(e=>e.offsetParent!==null).length") == 1, str(both))


# ───────────────────────── (C) Regime / แถบบัญชี / การ์ดคู่ ─────────────────────────
def regime_tests(pw, w, h, tag):
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        flow_setup(page)
        r = page.evaluate("""() => { const rows=[...document.querySelectorAll('#ffAction .ffActCell[data-ff=regime] .ffActRg')].map(e=>{const r=e.getBoundingClientRect(); const p=e.querySelector('.ffActPill').getBoundingClientRect(), n=e; return {h:Math.round(r.height), stacked: p.top > r.top + 8, pillL: Math.round(p.left-r.left)}; });
            const cell=document.querySelector('#ffAction .ffActCell[data-ff=regime]'); return {rows, cw: Math.round(cell.getBoundingClientRect().width), pills:[...document.querySelectorAll('#ffAction .ffActRg .ffActPill')].map(e=>e.innerText.trim()), sw:document.documentElement.scrollWidth}; }""")
        same = len(r["rows"]) == 2 and abs(r["rows"][0]["h"] - r["rows"][1]["h"]) <= 1 and r["rows"][0]["stacked"] == r["rows"][1]["stacked"] and r["rows"][0]["pillL"] == r["rows"][1]["pillL"] or (len(r["rows"]) == 2 and r["rows"][0]["stacked"] == r["rows"][1]["stacked"] and abs(r["rows"][0]["h"] - r["rows"][1]["h"]) <= 1)
        check(f"{tag} Regime (ช่องกว้าง {r['cw']}px): 2 แถวสูงเท่ากัน · จัดแบบเดียวกัน ({'ซ้อนลงทั้งคู่' if r['rows'][0]['stacked'] else 'บรรทัดเดียวทั้งคู่'})", same, json.dumps(r, ensure_ascii=False))
        if w <= 700: check(f"{tag} Regime ที่จอแคบ: ทั้งสองแถวซ้อนลง (pill ใต้ชื่อ) เหมือนกัน", r["rows"][0]["stacked"] and r["rows"][1]["stacked"], json.dumps(r))
        if w == 1440: check(f"{tag} Regime ที่จอกว้าง: ทั้งสองแถวบรรทัดเดียว", not r["rows"][0]["stacked"] and not r["rows"][1]["stacked"], json.dumps(r))
        check(f"{tag} แถบ Flow: ไม่ล้นแนวนอน (scrollWidth={r['sw']})", r["sw"] <= w + 1)
        fs = page.evaluate("""() => { const rem=parseFloat(getComputedStyle(document.documentElement).fontSize); let mn=99, bad=[]; const mono=getComputedStyle(document.documentElement).getPropertyValue('--mono').split(',')[0].replace(/['"]/g,'').trim().toLowerCase();
            document.querySelectorAll('#ffAction *').forEach(e=>{ if(!e.children.length && e.textContent.trim() && e.offsetParent!==null){ const cs=getComputedStyle(e), f=parseFloat(cs.fontSize); if(f<mn) mn=f; if(cs.fontFamily.toLowerCase().includes(mono)||/monospace/i.test(cs.fontFamily)) bad.push(e.textContent.trim().slice(0,20)); } }); return {mn:mn/rem, bad}; }""")
        check(f"{tag} แถบ Flow: ตัวเล็กสุด ≥ 0.72rem · ไม่ใช้ var(--mono)", fs["mn"] >= 0.72 - 0.005 and not fs["bad"], json.dumps(fs))
    finally:
        browser.close()


def strip_setup(page, closed_future_b=True):
    ports = {"main": ["core", "satB"], "fam": ["core"] if closed_future_b else ["core", "satB"]}
    seed(page, main=STOCK_MAIN, fam=STOCK_FAM, ports=ports)
    page.evaluate("() => { planStripOpen.clear(); render(); }"); page.wait_for_timeout(200)


def set_open(page, a_open, b_open):
    page.evaluate("""([a,b])=>{ const c=[...document.querySelectorAll('#strip .acctCard')]; [a,b].forEach((o,i)=>{ if(c[i].classList.contains('open')!==o) togglePlanStrip(c[i].querySelector('.acctRow1')); }); }""", [a_open, b_open])
    page.wait_for_timeout(200)


CARD_JS = """() => [...document.querySelectorAll('#strip .acctCard')].map(c=>{ const r=c.getBoundingClientRect(), h=c.querySelector('.acctRow1'), d=c.querySelector('.acctDetail'), nm=c.querySelector('.acctRow1 > b'), cr=c.querySelector('.acctCaret2');
    const nr=nm.getBoundingClientRect(), cc=cr.getBoundingClientRect(); return {top:Math.round(r.top), h:r.height, open:c.classList.contains('open'), detTop: d && d.offsetParent ? Math.round(d.getBoundingClientRect().top) : null, headH: h.getBoundingClientRect().height,
      nameY: nr.top+nr.height/2, caretY: cc.top+cc.height/2, caretX: Math.round(r.right-cc.right), rows:[...c.querySelectorAll('.acctGrp')].map(g=>g.dataset.grp)}; })"""


def strip_layout_tests(page, tag, w):
    strip_setup(page)
    q = lambda js: page.evaluate(js)
    set_open(page, False, False); c = q(CARD_JS)
    check(f"{tag} การ์ดบัญชี: A มีหุ้น+Future · B ปิด Future (มีแต่แถวหุ้น)", c[0]["rows"] == ["stock", "future"] and c[1]["rows"] == ["stock"], json.dumps(c))
    if w >= 900:
        check(f"{tag} การ์ดบัญชี {w}px: พับทั้งคู่ → วางคู่กัน สูงเท่ากัน (±1px)", abs(c[0]["top"] - c[1]["top"]) <= 1 and abs(c[0]["h"] - c[1]["h"]) <= 1, json.dumps(c))
        set_open(page, True, True); c = q(CARD_JS)
        check(f"{tag} การ์ดบัญชี {w}px: กางทั้งคู่ → สูงเท่ากัน (±1px) · acctDetail เริ่มที่ y เดียวกัน", abs(c[0]["h"] - c[1]["h"]) <= 1 and c[0]["detTop"] is not None and abs(c[0]["detTop"] - c[1]["detTop"]) <= 1, json.dumps(c))
        check(f"{tag} การ์ดบัญชี {w}px: ส่วนหัวสูงเท่ากัน (ใบที่ไม่มีแถว Future เว้นที่ว่างเท่าหนึ่งแถว)", abs(c[0]["headH"] - c[1]["headH"]) <= 1, json.dumps([c[0]["headH"], c[1]["headH"]]))
        check(f"{tag} การ์ดบัญชี {w}px: ลูกศรอยู่ y เดียวกับชื่อบัญชี (±3px) · ตำแหน่งมุมขวาเท่ากันทั้งสองใบ (กางทั้งคู่)", all(abs(x["nameY"] - x["caretY"]) <= 3 for x in c) and c[0]["caretX"] == c[1]["caretX"], json.dumps(c))
        shot(page, f"ui1b-{w}-acct-open-both.png", "#strip")
        set_open(page, True, False); c = q(CARD_JS)
        check(f"{tag} การ์ดบัญชี {w}px: กางใบเดียว → อีกใบ (พับ) ไม่ยืดตาม · ลูกศรทั้งสองใบอยู่ตำแหน่งเดียวกัน", c[1]["h"] < c[0]["h"] - 20 and c[1]["h"] <= c[1]["headH"] + 4 and c[0]["caretX"] == c[1]["caretX"] and abs(c[0]["caretY"] - c[1]["caretY"]) <= 1, json.dumps(c))
        shot(page, f"ui1b-{w}-acct-open-one.png", "#strip")
        set_open(page, False, True); c = q(CARD_JS)
        check(f"{tag} การ์ดบัญชี {w}px: กางใบ B ใบเดียว → ใบ A (พับ) ไม่ยืดตาม", c[0]["h"] < c[1]["h"] - 20, json.dumps(c))
        set_open(page, False, False); c = q(CARD_JS)
        check(f"{tag} การ์ดบัญชี {w}px: พับกลับ → สูงเท่ากันอีกครั้ง (±1px) · ลูกศรอยู่ y เดียวกับชื่อ", abs(c[0]["h"] - c[1]["h"]) <= 1 and all(abs(x["nameY"] - x["caretY"]) <= 3 for x in c), json.dumps(c))
        shot(page, f"ui1b-{w}-acct-closed.png", "#strip")
        # พับ: ไม่มีช่องว่างเปล่าระหว่างแถว Future กับลูกศร — ลูกศรอยู่แถวชื่อ (บนสุด) ไม่ใช่แถวล่าง
        check(f"{tag} การ์ดบัญชี: ลูกศรอยู่มุมขวาบน (แถวเดียวกับชื่อ) ตอนพับ", all(x["caretY"] < x["top"] + 40 for x in c), json.dumps(c))
    else:
        check(f"{tag} การ์ดบัญชี {w}px: เรียงลงเป็นคอลัมน์เดียว", c[1]["top"] >= c[0]["top"] + c[0]["h"] - 1, json.dumps(c))
        set_open(page, True, True); c = q(CARD_JS)
        check(f"{tag} การ์ดบัญชี {w}px: ลูกศรอยู่แถวเดียวกับชื่อบัญชี ทั้งพับ/กาง (±3px)", all(abs(x["nameY"] - x["caretY"]) <= 3 for x in c), json.dumps(c))
        if w == 430:
            g = q("""() => [...document.querySelectorAll('#strip .acctCard .acctGrp')].map(g=>{ const l=g.querySelector('.acctGrpLbl').getBoundingClientRect(), b=[...g.querySelectorAll('.acctJump')].map(e=>{const r=e.getBoundingClientRect(); return {l:Math.round(r.left), t:Math.round(r.top), h:Math.round(r.height)}}); return {grp:g.dataset.grp, lblRight: Math.round(l.right), b}; })""")
            wrapped = [x for x in g if len(x["b"]) > 1 and x["b"][1]["t"] > x["b"][0]["t"] + 4]
            check(f"{tag} แถบบัญชี: ปุ่มที่ตัดบรรทัด left ≥ left ของปุ่มแรกในแถว (อยู่ในคอลัมน์ปุ่ม) · ปุ่มทุกตัวอยู่ขวาของป้ายหุ้น/Future",
                  all(all(bb["l"] >= x["b"][0]["l"] - 1 and bb["l"] >= x["lblRight"] for bb in x["b"]) for x in g) and len(wrapped) >= 1, json.dumps({"g": g, "wrapped": len(wrapped)}))
            check(f"{tag} แถบบัญชี: ปุ่ม Hold/Plan สูง ≥ 36px", all(bb["h"] >= 36 for x in g for bb in x["b"]), json.dumps(g))
            set_open(page, False, False)
            shot(page, "ui1b-430-acct-closed.png", "#strip"); set_open(page, True, True); shot(page, "ui1b-430-acct-open.png", "#strip")
    sw = q("() => document.documentElement.scrollWidth")
    check(f"{tag} แถบบัญชี: ไม่ล้นแนวนอน (scrollWidth={sw})", sw <= w + 1)


def detail_tests(page, tag, w):
    strip_setup(page); set_open(page, True, True)
    d = page.evaluate("""() => { const mono=getComputedStyle(document.documentElement).getPropertyValue('--mono').split(',')[0].replace(/['"]/g,'').trim().toLowerCase(); const c=document.querySelector('#strip .acctCard');
        const kv=[...c.querySelectorAll('.acctKV')].map(k=>{ const s=k.querySelector('span'), b=k.querySelector('b'); const sr=s.getBoundingClientRect(), br=b.getBoundingClientRect(); const lh=parseFloat(getComputedStyle(s).lineHeight)||20;
            return {lbl:s.innerText.trim(), title:s.getAttribute('title'), val:b.innerText.replace(/\\s+/g,' ').trim(), sTop:Math.round(sr.top), sH:Math.round(sr.height), bTop:Math.round(br.top), bRight:Math.round(br.right), bLeft:Math.round(br.left), bfw:getComputedStyle(b).fontWeight, bff:getComputedStyle(b).fontFamily, sff:getComputedStyle(s).fontFamily,
            small:(b.querySelector('small')||{}).innerText||null, smallColor:b.querySelector('small')?getComputedStyle(b.querySelector('small')).color:null, bColor:getComputedStyle(b).color, ws:getComputedStyle(b).whiteSpace, lh}; });
        const fam=[...c.querySelectorAll('.acctDetail *')].some(e=>getComputedStyle(e).fontFamily.toLowerCase().includes(mono)||/monospace/i.test(getComputedStyle(e).fontFamily));
        const eye=c.querySelector('.acctKV b[data-priv-anchor] .privEye'); const openB=c.querySelector('.acctKV b[data-priv-anchor]').getBoundingClientRect(); const er=eye?eye.getBoundingClientRect():null;
        return {kv, mono:fam, eye: er ? {gap: Math.round(openB.left-er.right), y: Math.round((er.top+er.bottom)/2-(openB.top+openB.bottom)/2)} : null, cols:getComputedStyle(c.querySelector('.acctDetail')).gridTemplateColumns.split(' ').length}; }""")
    kv = d["kv"]
    check(f"{tag} acctDetail: ไม่มี var(--mono) (ฟอนต์ปกติของแอป) · ตัวเลขตัวหนา ≥ 600", not d["mono"] and all(int(x["bfw"]) >= 600 for x in kv), json.dumps(d)[:600])
    check(f"{tag} acctDetail: ป้ายเป็น 'Open' บรรทัดเดียว · คำอธิบายเดิม 'ความเสี่ยงค้าง (Open) · % ของทุนรวมบัญชี' อยู่ใน tooltip (title)", kv[0]["lbl"] == "Open" and kv[0]["title"] == "ความเสี่ยงค้าง (Open) · % ของทุนรวมบัญชี" and kv[0]["sH"] <= kv[0]["lh"] * 1.3, json.dumps(kv[0]))
    check(f"{tag} acctDetail: ค่า Open = '0.xx% ฿…' บรรทัดเดียว (nowrap) · หน่วย/฿ ตัวรองสีจาง", re.match(r"^[\d.]+%฿[\d,]+( 👁)?$", kv[0]["val"]) and kv[0]["ws"] == "nowrap" and kv[0]["small"] and kv[0]["smallColor"] != kv[0]["bColor"], json.dumps(kv[0]))
    check(f"{tag} acctDetail: ลำดับ Open · Plan · จำนวนไม้ · ไม้ใหม่สัปดาห์นี้ (CL2-d: ตัด Heat 1R)", [x["lbl"] for x in kv] == ["Open", "Plan", "จำนวนไม้", "ไม้ใหม่สัปดาห์นี้"], json.dumps([x["lbl"] for x in kv]))
    if w > 480:
        check(f"{tag} acctDetail: ตาราง 2 คู่ [ป้าย|ค่า] ต่อแถว — แถว 1 = Open · Plan · แถว 2 = จำนวนไม้ · ไม้ใหม่ (CL2-d: ตัด Heat 1R · ไม้ใหม่ไม่เป็น solo แล้ว)",
              d["cols"] == 4 and abs(kv[0]["sTop"] - kv[1]["sTop"]) <= 3 and abs(kv[2]["sTop"] - kv[3]["sTop"]) <= 3 and kv[2]["sTop"] > kv[0]["sTop"] + 10, json.dumps(kv))
        check(f"{tag} acctDetail: ค่าชิดขวาในคอลัมน์ค่า ตรงแนวกันทุกแถว (Open/จำนวนไม้ · Plan/ไม้ใหม่ ขอบขวาเท่ากัน ±1px)", abs(kv[0]["bRight"] - kv[2]["bRight"]) <= 1 and abs(kv[1]["bRight"] - kv[3]["bRight"]) <= 1, json.dumps([[x["lbl"], x["bRight"]] for x in kv]))
    else:
        ys = [x["sTop"] for x in kv]
        check(f"{tag} acctDetail ≤480px: 1 คู่ต่อแถว (4 แถวเรียงลง) · ค่าชิดขวาตรงแนวเดียวกันทุกแถว", all(ys[i + 1] > ys[i] + 10 for i in range(3)) and len({x["bRight"] for x in kv[:4]}) == 1, json.dumps([[x["lbl"], x["sTop"], x["bRight"]] for x in kv]))
    check(f"{tag} acctDetail: 👁 อยู่ติดค่า Open (ซ้ายมือของค่า · กึ่งกลางแนวเดียวกัน) ไม่ดันเลขให้เยื้อง", d["eye"] and 0 <= d["eye"]["gap"] <= 6 and abs(d["eye"]["y"]) <= 4, json.dumps(d["eye"]))
    if w in (1440, 430): shot(page, f"ui1b-{w}-acct-detail.png", "#strip .acctCard")
    fs = page.evaluate("() => { const rem=parseFloat(getComputedStyle(document.documentElement).fontSize); let mn=99; document.querySelectorAll('#strip .acctDetail *').forEach(e=>{ if(!e.children.length && e.textContent.trim() && e.offsetParent!==null){ mn=Math.min(mn, parseFloat(getComputedStyle(e).fontSize)); } }); return mn/rem; }")
    check(f"{tag} acctDetail: ตัวเล็กสุด ≥ 0.72rem", fs >= 0.72 - 0.005, str(fs))


def ui(pw, w, h, tag):
    tag = f"[{ENGINE}/{tag}]"
    flow_tests(pw, w, h, tag)
    regime_tests(pw, w, h, tag)
    future_tests(pw, w, h, tag)
    stock_tests(pw, w, h, tag)
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        future_ui(page, tag, w, h)
        stock_ui(page, tag, w, h)
        strip_layout_tests(page, tag, w)
        detail_tests(page, tag, w)
        check(f"{tag} console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


def main():
    with sync_playwright() as pw:
        ui(pw, 1440, 900, "1440px")
        ui(pw, 430, 932, "430px")
        ui(pw, 932, 430, "932x430")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 14 / UI-1b) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:400])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
