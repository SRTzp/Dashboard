#!/usr/bin/env python3
"""SET1 — Settings แบบ Lean + สเปคสินค้า hard-code (Lot / % loss · ไม่มีโบรก) + Copy for AI · เทส 110
Chromium · 300 / 390 / 1280 / 1440 · Sat: fixture P77 (Lean) · Watch: fixture P106/P107 · ข้อมูล SAMPLE ล้วน
ภาพ tests/screenshots/set1-{settings-390,sat-390,products-390,plan-btc-390,plan-xau-390,settings-1440}.png
รัน: SECT='calc plan settings copy' python3 run_tests_phase110.py"""
import json, os, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase39 as P39
import run_tests_phase77 as P77
import run_tests_phase79 as P79
import run_tests_phase107 as T

ENGINE = base.BROWSER_ENGINE
HERE = os.path.dirname(os.path.abspath(__file__))
OLD_INDEX = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-SET1.html"))
SHOTS = os.path.join(HERE, "screenshots")
results = []
js, settle, txt, cnt = T.js, T.settle, T.txt, T.cnt
LOG = {}


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    os.makedirs(SHOTS, exist_ok=True)
    p = os.path.join(SHOTS, name)
    if sel:
        el = page.locator(sel).first
        el.screenshot(path=p)
    else:
        page.screenshot(path=p)
    return p


def sat_launch(pw, w, h, old=False):
    keep = P39.INDEX
    if old: P39.INDEX = OLD_INDEX
    try:
        b, page, ce, pe = P77.launch(pw, w, h)
    finally:
        P39.INDEX = keep
    js(page, "()=>{ localStorage.removeItem('dash.set1Open'); ln1SetMode('lean'); render(); }"); settle(page, 400)
    return b, page, ce, pe


def to_plan(page): js(page, "()=>{ switchTab('plan'); setPlanScope('future'); satV3Render({force:true}); }"); settle(page, 500)
def hover(page): return js(page, "()=>document.documentElement.scrollWidth - document.documentElement.clientWidth")


def card_text(page, iid):
    return js(page, "(i)=>{ const e = document.querySelector('[data-ln1-card=\"'+i+'\"], [data-sat-idea=\"'+i+'\"]') || document.getElementById('satV3Panel'); return e.innerText; }", iid)


def xau_numbers(page):
    iid = P79.idea(page, sleeve="main", entry=4180, sl=4117)
    c = P77.calc(page, iid)
    return c["lot"], c["riskUsd"]


# ───────────────────────── 1 สูตร + สเปค ─────────────────────────
def calc_tests(pw):
    tag = f"[{ENGINE}/calc]"
    b, page, ce, pe = sat_launch(pw, 390, 844)
    try:
        r = js(page, """()=>({
          btc: Calc.pctLoss({riskAmount:200, entry:100000, sl:98000, qtyStep:0.0001}),
          eth: Calc.pctLoss({riskAmount:150, entry:3000, sl:2850, qtyStep:0.0001}),
          us: Calc.pctLoss({riskAmount:100, entry:50, sl:48, qtyStep:1}),
          th: Calc.pctLoss({riskAmount:2500, entry:50, sl:48, qtyStep:100}),
          tiny: Calc.pctLoss({riskAmount:1, entry:100000, sl:50000, qtyStep:1}),
          bad: Calc.pctLoss({riskAmount:200, entry:100, sl:100, qtyStep:1}),
          go: Calc.satLot({riskAmount:3000, dist:10, contract:productFor('GO').perPoint, lotStep:1, minLot:1}),
          xau: productCfg('XAUUSD'), s50: productCfg('S50'), go2: productCfg('GO'), btc2: productCfg('BTCUSDT'), eth2: productCfg('ETHUSD'),
          brent: productFor('BRENT'), s50z: productFor('S50Z25').name,
          viaLot: Calc.satLot({riskAmount:200, dist:2000, contract:1, lotStep:0.0001, minLot:0.0001})})""")
        check(f"{tag} BTC $200 · Entry 100,000 · SL 98,000 → สถานะ $10,000 · 0.10 BTC · stop 2%", r["btc"]["pos"] == 10000 and abs(r["btc"]["qty"] - 0.1) < 1e-9 and abs(r["btc"]["stopPct"] - 2) < 1e-9, r["btc"])
        check(f"{tag} ETH: $150 · 3000→2850 (5%) → $3,000 · 1 ETH", abs(r["eth"]["pos"] - 3000) < 1e-6 and abs(r["eth"]["qty"] - 1) < 1e-9, r["eth"])
        check(f"{tag} หุ้น US: เศษหุ้นปัดลงเป็นหุ้นเต็ม (risk $100 · ระยะ 2 → 50 หุ้น)", r["us"]["qty"] == 50 and r["us"]["pos"] == 2500, r["us"])
        check(f"{tag} หุ้น TH: ปัดลงเป็นล็อต 100 (raw 1,250 → 1,200)", r["th"]["qty"] == 1200, r["th"])
        check(f"{tag} ต่ำกว่า qty step → qty=null + ข้อความ · Entry=SL → ไม่คำนวณ (msg ว่าง)", r["tiny"]["qty"] is None and r["tiny"]["msg"] != "" and r["bad"]["qty"] is None and r["bad"]["msg"] == "", [r["tiny"], r["bad"]])
        check(f"{tag} GO ฿300/จุด: เสี่ยง ฿3,000 · 10 จุด → 1 สัญญา", r["go"]["lot"] == 1 and r["go2"]["contract"] == 300 and r["go2"]["cur"] == "THB", [r["go"], r["go2"]])
        check(f"{tag} XAUUSD = $100/pt step 0.01 min 0.01 USD · S50 = ฿200/pt step 1 THB (ค่าเดิมของ XM/Pi)", r["xau"]["contract"] == 100 and r["xau"]["lotStep"] == 0.01 and r["xau"]["minLot"] == 0.01 and r["xau"]["cur"] == "USD" and r["s50"]["contract"] == 200 and r["s50"]["lotStep"] == 1 and r["s50"]["cur"] == "THB", [r["xau"], r["s50"]])
        check(f"{tag} alias BTCUSDT→BTC · ETHUSD→ETH เป็นระบบ % loss · S50Z25→S50 · Brent ยังไม่มีสเปค", r["btc2"]["sys"] == "pct" and r["eth2"]["sys"] == "pct" and r["s50z"] == "S50" and r["brent"] is None, [r["btc2"], r["eth2"], r["s50z"], r["brent"]])
        check(f"{tag} สูตร % loss ≡ satLot(contract=1) ที่แผนใช้ (qty 0.1)", abs(r["viaLot"]["lot"] - 0.1) < 1e-9, r["viaLot"])
        r2 = js(page, """()=>{ const hm = getBook(tdHome()); hm.settings.products = {PTTX:{sys:'pct', qtyStep:100, cur:'THB'}, NVDX:{sys:'pct', qtyStep:1}};
          return {th: productCfg('PTT.BK'), thc: productCfg('PTTX'), us: productCfg('NVDX'), lean: (localStorage.setItem('ln1_plan_view','legacy'), localStorage.removeItem('dash.ln1Legacy'), ln1Mode())}; }""")
        check(f"{tag} หุ้นไทย built-in (.BK): % loss · ล็อต 100 · THB", r2["th"]["sys"] == "pct" and r2["th"]["lotStep"] == 100 and r2["th"]["cur"] == "THB", r2["th"])
        check(f"{tag} สินค้า % loss ที่เพิ่มเอง: เลือกสกุลได้ (THB) · ไม่ระบุ = USD", r2["thc"]["cur"] == "THB" and r2["us"]["cur"] == "USD", [r2["thc"], r2["us"]])
        check(f"{tag} หน้าแผน Sat บังคับ Lean แม้เก็บ 'legacy' ไว้ (ไม่มีแฟลกนักพัฒนา)", r2["lean"] == "lean", r2["lean"])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


# ───────────────────────── 2 แผน Sat ─────────────────────────
def plan_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = sat_launch(pw, w, h)
    try:
        to_plan(page)
        # XAU: ตัวเลขเท่ากับก่อนแก้ (เทียบกับ index.backup-pre-SET1.html)
        new = xau_numbers(page)
        bo, po, ceo, peo = sat_launch(pw, w, h, old=True)
        try:
            to_plan(po)
            old = xau_numbers(po)
        finally:
            bo.close()
        LOG["xau_before_after"] = {"old": old, "new": new}
        check(f"{tag} §sizing XAUUSD main 4180/4117: ก่อน = หลัง (lot, risk $)", old == new and new[0] > 0, {"old": old, "new": new})
        iid = P79.idea(page, sleeve="main", entry=4180, sl=4117)
        js(page, "(i)=>{ if(satActiveDraft!==i) ln3ToggleDraft(i); }", iid); settle(page, 400)
        t = js(page, "()=>document.getElementById('satV3Panel').innerText")
        check(f"{tag} แผน XAU แสดง 'lot · N pts' (ไม่มีชื่อโบรก XM/IC)", "pts" in t and " XM" not in t and " IC " not in t, t[:300])
        if shots:
            js(page, "()=>{ const e = document.querySelector('[data-ln1-acct]'); if(e) e.scrollIntoView({block:'center'}); }"); settle(page, 300)
            shot(page, "set1-plan-xau-390.png")
        # BTC % loss
        bt = P79.idea(page, sleeve="main", asset="BTCUSD", entry=100000, sl=98000)
        js(page, "(i)=>{ if(satActiveDraft!==i) ln3ToggleDraft(i); }", bt); settle(page, 500)
        c = js(page, "(i)=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x,'main'); const h = satV2SizeLine({_idea:x,_skipSet:new Set(),_v2:true},{id:'main'}); return {lot:c.lot, deal:c.v2.lotDeal, sys:c.chosen && c.chosen.cfg.sys, risk:c.v2.dealTHB/c.v2.k, msg:c.lotMsg, html:h.replace(/<[^>]+>/g,' ')}; }", bt)
        t = c["html"]
        check(f"{tag} BTC: ระบบ % loss · qty ดีล = เสี่ยง$ ÷ 2,000 · แสดง '$… · stop 2.0%'", c["sys"] == "pct" and c["deal"] and abs(c["deal"] - c["risk"] / 2000) < 1e-3 and "stop 2.0%" in t and "BTC" in t, [c])
        if shots:
            js(page, "()=>{ const e = document.querySelector('[data-ln1-acct]'); if(e) e.scrollIntoView({block:'center'}); }"); settle(page, 300)
            shot(page, "set1-plan-btc-390.png")
            js(page, "()=>{ const e = document.querySelector('.ln1-card, [data-ln1-card]') || document.getElementById('satV3Panel'); e.scrollIntoView({block:'start'}); }"); settle(page, 300)
            shot(page, "set1-sat-390.png")
        # Brent ไม่มีสเปค → Can't size + Set ›
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','BRENT']); }"); settle(page, 500)
        br = P79.idea(page, sleeve="main", asset="BRENT", entry=80, sl=78)
        js(page, "(i)=>{ if(satActiveDraft!==i) ln3ToggleDraft(i); }", br); settle(page, 500)
        t = js(page, "()=>document.getElementById('satV3Panel').innerText")
        check(f"{tag} Brent ไม่มีสเปค → \"Can't size: Brent spec missing\" + ลิงก์ Set ›", "Can't size: Brent spec missing" in t and cnt(page, "[data-cant-size] [data-set-go]") >= 1, t[:300])
        js(page, "()=>document.querySelector('[data-cant-size] [data-set-go]').click()"); settle(page, 500)
        st = js(page, "()=>({ov:document.getElementById('setOverlay').classList.contains('show'), f:document.activeElement && document.activeElement.id, v:document.getElementById('set1PnName').value, open:document.getElementById('set1AddProd').open, card:document.querySelector('[data-set1-card=prod]').open})")
        check(f"{tag} Set › เปิด Settings ที่การ์ด Products + ฟอร์มเพิ่มสินค้า ชื่อ BRENT + focus", st["ov"] and st["f"] == "set1PnName" and st["v"] == "BRENT" and st["open"] and st["card"], st)
        # เพิ่มสินค้า Lot → คำนวณได้
        js(page, "()=>{ document.getElementById('set1PnPer').value='1000'; document.getElementById('set1PnStep').value='0.01'; document.getElementById('set1PnMin').value='0.01'; set1ProdAdd(); }"); settle(page, 700)
        pm = js(page, "()=>getBook(tdHome()).settings.products")
        check(f"{tag} เพิ่ม BRENT (Lot $1000/pt) → เก็บใน settings.products + Setup check ไม่มี Brent", pm and pm.get("BRENT", {}).get("sys") == "lot" and "Brent" not in (txt(page, "#set1Check") or ""), pm)
        js(page, "()=>document.getElementById('setOverlay').classList.remove('show')"); settle(page, 300)
        c = js(page, "(i)=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x,'main'); return {lot:c.lot, msg:c.lotMsg}; }", br)
        check(f"{tag} Brent หลังมีสเปค → คำนวณ lot ได้", c["lot"] and c["lot"] > 0, c)
        # ทุนหาย → Can't size: Sat capital not set (Main)
        js(page, "()=>{ getBook('main').settings.capital.satB = 0; render(); satV3Render({force:true}); }"); settle(page, 500)
        t = js(page, "()=>document.getElementById('satV3Panel').innerText")
        check(f"{tag} ไม่ตั้งทุน Sat → \"Can't size: Sat capital not set (Main)\"", "Can't size: Sat capital not set (Main)" in t, t[:300])
        js(page, "(i)=>satV3PlanEdit(i,'sl','80')", br); settle(page, 500)
        js(page, "()=>{ getBook('main').settings.capital.satB = 45000; satV3Render({force:true}); }"); settle(page, 400)
        t = js(page, "()=>document.getElementById('satV3Panel').innerText")
        check(f"{tag} Entry = SL → \"Can't size: Entry = SL\"", "Can't size: Entry = SL" in t, t[:300])
        check(f"{tag} ไม่ overflow แนวนอน (หน้า plan)", hover(page) <= 1, hover(page))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


# ───────────────────────── 3 Settings ─────────────────────────
def settings_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = sat_launch(pw, w, h)
    try:
        js(page, "()=>openSettings()"); settle(page, 500)
        cards = js(page, "()=>[...document.querySelectorAll('#setOverlay [data-set1-card]')].map(e=>e.dataset.set1Card + ':' + e.querySelector('summary').childNodes[0].textContent.trim())")
        check(f"{tag} Settings = 5 การ์ด: Accounts & Capital · Core rules · Sat rules · Products · App", cards == ["acct:Accounts & Capital", "core:Core rules", "sat:Sat rules", "prod:Products", "app:App"], cards)
        ck = txt(page, "#set1Check") or ""
        check(f"{tag} Setup check: fixture ครบ → '✓ All set' บรรทัดเดียว", "All set" in ck, ck)
        # ไม่มี UI ของค่าที่ตายตัว
        vis = js(page, "()=>['sizeWl','sizePlan','sizeClosed','tabsOffset','ln1ModeLean','ln1ModeLegacy','sV2TfMain','sV2TfTac','sV2SetupsMain','sV2SetupsTac','ideaGroupMinIn'].filter(id=>{ const e = document.getElementById(id); return e && e.offsetParent !== null; })")
        check(f"{tag} ไม่มี UI แก้: ขนาดตัวอักษร · แถบแท็บ · Lean/แบบเดิม · TF · Setup list · Ideas min group", vis == [], vis)
        check(f"{tag} ไม่มี UI โบรก XM/IC/Pi ใน Settings", "XM" not in js(page, "()=>document.getElementById('setOverlay').innerText") and cnt(page, "#setOverlay [data-bk-row]") == 0, "")
        # Advanced พับอยู่ · เปิดแล้วเห็นช่อง
        adv = js(page, "()=>[...document.querySelectorAll('#setOverlay .set1adv')].map(d=>d.open)")
        check(f"{tag} 'Advanced ▸' ของ Core / Sat พับอยู่ตอนเปิด", adv == [False, False], adv)
        # Sat basics + live hint
        live = js(page, "()=>document.getElementById('set1RptLive').textContent")
        check(f"{tag} Sat basics: RPT Main/Tactical + บรรทัดสด '= $… per Main trade'", "per Main trade" in live and "per Tactical" in live and "$" in live, live)
        # เพดาน L2 รวมเป็นช่องเดียว (ช่องซ้ำถูกซ่อน)
        check(f"{tag} Core: Max open risk = เพดานชั้น 2 ช่องเดียว (sCrL2Cap ซ่อน)", js(page, "()=>document.getElementById('sCrL2Cap').offsetParent === null && document.getElementById('sPortCore').closest('.set1adv') === null"), "")
        # บันทึกแล้ว settings อื่นไม่เปลี่ยน
        before = js(page, "()=>JSON.stringify(Object.assign({}, state.settings, {_k:0}))")
        js(page, "()=>{ document.querySelector('[data-set1-adv=core]').open = true; saveSettings(); }"); settle(page, 500)
        after = js(page, "()=>JSON.stringify(Object.assign({}, state.settings, {_k:0}))")
        bo, ao = json.loads(before), json.loads(after)
        OWN = {"capital", "fx", "fxAuto", "strategicCash", "limits", "coreRisk", "satRisk", "satV2", "tdKey"}   # ฟิลด์ที่ Settings เป็นเจ้าของ (บันทึกเติมค่าเริ่มต้นได้)
        diff = [k for k in set(bo) | set(ao) if k not in OWN and bo.get(k) != ao.get(k)]
        lost = [k for k in OWN if k in bo and k not in ao]
        sub = all(all(ao[k].get(kk) == vv for kk, vv in bo[k].items()) for k in ("satV2", "satRisk", "coreRisk") if isinstance(bo.get(k), dict) and isinstance(ao.get(k), dict))
        check(f"{tag} กดบันทึกโดยไม่แก้ → key นอกเจ้าของเหมือนเดิม · ค่าเดิมของ Core/Sat ไม่เปลี่ยน (เติมได้แค่ค่าเริ่มต้น)", diff == [] and lost == [] and sub, [diff, lost, sub])
        # Setup check เตือน + Fix › โฟกัสช่องที่ถูกต้อง
        js(page, "()=>{ getBook('main').settings.capital.satB = 0; state.settings.capital.satB = 0; openSettings(); }"); settle(page, 500)
        ck = txt(page, "#set1Check") or ""
        check(f"{tag} Setup check ⚠ ทุน Sat หาย → 'Sat capital not set (Main)' + Fix ›", "Sat capital not set (Main)" in ck and "Fix" in ck, ck)
        js(page, "()=>document.querySelector('#set1Check [data-set-go]').click()"); settle(page, 600)
        f = js(page, "()=>document.activeElement && document.activeElement.id")
        check(f"{tag} Fix › โฟกัสช่อง Sat ($) ของบัญชีนั้น", f == "sSatB", f)
        if shots:
            js(page, "()=>{ state.settings.capital.satB = 45000; getBook('main').settings.capital.satB = 45000; openSettings(); document.querySelector('[data-set1-card=sat]').open = true; document.querySelector('[data-set1-card=acct]').open = false; document.getElementById('setOverlay').scrollTop = 0; }"); settle(page, 500)
            shot(page, "set1-settings-%d.png" % w if w in (390, 1440) else "set1-x.png", "#setOverlay .modal") if w in (390, 1440) else None
            js(page, "()=>{ document.querySelector('[data-set1-card=sat]').open = false; document.querySelector('[data-set1-card=prod]').open = true; document.getElementById('set1AddProd').open = true; }"); settle(page, 400)
            if w == 390:
                shot(page, "set1-products-390.png", "#setOverlay .modal")
        # Products: ฟอร์ม Lot กับ % แยกกัน
        js(page, "()=>{ openSettings(); document.querySelector('[data-set1-card=prod]').open = true; document.getElementById('set1AddProd').open = true; }"); settle(page, 400)
        lotf = cnt(page, "[data-set1-lotf]"); pctf = cnt(page, "[data-set1-pctf]")
        js(page, "()=>{ const s = document.getElementById('set1PnType'); s.value='pct'; s.dispatchEvent(new Event('change')); }"); settle(page, 300)
        lotf2 = cnt(page, "[data-set1-lotf]"); pctf2 = cnt(page, "[data-set1-pctf]")
        names = js(page, "()=>[...document.querySelectorAll('#set1AddProd .f label')].map(l=>l.textContent.trim().split(' ')[0])")
        check(f"{tag} ฟอร์มเพิ่มสินค้า: Lot = 4 ช่อง (ค่าต่อจุด/step/min/สกุล) · % loss = ช่องเดียว (qty step) · ไม่ใช้ร่วมกัน", lotf == 4 and pctf == 0 and lotf2 == 0 and pctf2 == 2, [lotf, pctf, lotf2, pctf2, names])
        # ชื่อซ้ำ
        def add(name, per=None):
            js(page, "([n,p])=>{ document.getElementById('set1PnName').value = n; if(p!=null && document.getElementById('set1PnPer')) document.getElementById('set1PnPer').value = p; set1ProdAdd(); }", [name, per]); settle(page, 400)
            return js(page, "()=>(document.getElementById('set1PnMsg')||{}).textContent || ''")
        m1 = add("XAUUSD")
        m2 = add("btc")
        check(f"{tag} ชื่อซ้ำกับสินค้าในตัว (XAUUSD / BTC) ถูกปฏิเสธ", "built-in" in m1 and "built-in" in m2, [m1, m2])
        add("SOL")   # % loss, qty step default 1
        js(page, "()=>{ const s = document.getElementById('set1PnType'); }")
        m3 = add("SOL")
        pm = js(page, "()=>getBook(tdHome()).settings.products")
        check(f"{tag} เพิ่ม % loss 'SOL' ได้ครั้งเดียว · ชื่อซ้ำ (custom) ถูกปฏิเสธ · เก็บ {{sys,qtyStep,cur}} เท่านั้น", pm and pm.get("SOL") == {"sys": "pct", "qtyStep": 1, "cur": "USD"} and "already exists" in m3, [pm, m3])
        # คงอยู่หลังโหลดใหม่ (อ่านจากเอกสารเดียวกัน)
        js(page, "()=>{ openSettings(); }"); settle(page, 300)
        check(f"{tag} สินค้าที่เพิ่มเองแสดงในรายการหลังเปิด Settings ใหม่", cnt(page, "[data-set1-pr='SOL']") == 1, "")
        check(f"{tag} ไม่ overflow แนวนอน (Settings) · modal ไม่ล้นจอ", hover(page) <= 1 and js(page, "()=>document.querySelector('#setOverlay .modal').scrollWidth <= document.querySelector('#setOverlay .modal').clientWidth + 1"), hover(page))
        # หน้า Sat assets (เดิม = โบรก) ไม่มีโบรกแล้ว
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); sat7dBrokerOpen(); }"); settle(page, 500)
        ov = js(page, "()=>document.getElementById('sat7dBrokerOverlay').innerText")
        check(f"{tag} หน้า Sat assets: ไม่มีส่วนโบรก/สัญญา (ไม่มี XM·IC·Pi, ไม่มี contract/step/min)", cnt(page, "#sat7dBrokerOverlay [data-bk-row]") == 0 and cnt(page, "#sat7dBrokerOverlay .s7BRow") == 0 and "โบรก" not in ov.replace("ไม่มีโบรก", ""), ov[:200])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def broker_data_tests(pw):
    tag = f"[{ENGINE}/broker]"
    b, page, ce, pe = sat_launch(pw, 390, 844)
    try:
        # ข้อมูลโบรกเดิมค้างอยู่ (ซ่อน) + ไม้เก่ามีฟิลด์ broker → แสดงผลได้ ไม่ error
        js(page, """()=>{ const B = getBook('main'); B.settings.brokers = {XM:{XAUUSD:{contract:100,lotStep:0.01,minLot:0.01,cur:'USD'}}};
          B.trades.push({id:'tOldBroker', port:'satB', sym:'XAUUSD', bias:'Long', entry:4000, sl:3950, qty:0.1, mult:100, cur:'USD', status:'closed', exitPrice:4050, exitDate:'2026-09-20', date:'2026-09-10', broker:'XM'}); saveBook('main'); render(); }""")
        settle(page, 500)
        js(page, "()=>{ switchTab('journal'); renderJournal(); }"); settle(page, 500)
        js(page, "()=>{ openSettings(); saveSettings(); }"); settle(page, 500)
        keep = js(page, "()=>JSON.stringify(getBook('main').settings.brokers)")
        check(f"{tag} ข้อมูลโบรกเก่าไม่ถูกแตะหลังเปิด/บันทึก Settings (ซ่อนไว้)", keep and "XM" in keep, keep)
        t = js(page, "()=>getBook('main').trades.find(t=>t.id==='tOldBroker')")
        check(f"{tag} ไม้เก่าที่มี broker='XM' ยังอยู่ครบ + Journal เรนเดอร์ได้", t and t["broker"] == "XM" and not pe, [t, pe[:2]])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


# ───────────────────────── 4 Copy for AI ─────────────────────────
ROWS = [
    {"sym": "XLU", "name": "Utilities", "quad": "lead", "ratio": 104, "mom": 101, "days": 5, "off52": -2, "date": "2026-10-29", "dRatio": 1, "dMom": 1, "rsTrend": 1},
    {"sym": "XRT", "name": "Retail", "quad": "lead", "ratio": 103, "mom": 100.5, "days": 3, "off52": -3, "date": "2026-10-29", "dRatio": 1, "dMom": 1, "rsTrend": 1},
    {"sym": "SMH", "name": "Semiconductors", "quad": "imp", "ratio": 99, "mom": 101, "days": 2, "off52": -6, "date": "2026-10-29", "dRatio": 1, "dMom": 1, "rsTrend": 1},
    {"sym": "KBE", "name": "Banks", "quad": "imp", "ratio": 98, "mom": 100.2, "days": 2, "off52": -7, "date": "2026-10-29", "dRatio": 1, "dMom": 1, "rsTrend": 1},
    {"sym": "IGV", "name": "Software", "quad": "weak", "ratio": 102, "mom": 99, "days": 4, "off52": -9, "date": "2026-10-29", "dRatio": 1, "dMom": 1, "rsTrend": 1},
    {"sym": "XLF", "name": "Financials", "err": "no data"},
]


def go_flow(page, rows):
    js(page, "(rows)=>{ switchTab('flow'); const f = ffState(); f.rrg = {rowsD:rows, rowsW:[], day:'2026-10-29', at:'', loading:false, err:''}; f.themesCol = false; f.themesColUser = true; ffRenderThemes(); }", rows)
    settle(page, 600)


def copy_tests(pw):
    tag = f"[{ENGINE}/copy]"
    b, page, ce, pe = T.launch(pw, 390, 844)
    try:
        js(page, "()=>{ window.__clip = null; navigator.clipboard.writeText = t => { window.__clip = t; return Promise.resolve(); }; }")
        go_flow(page, ROWS)
        js(page, "()=>{ const h = tdHome(); const B = getBook(h); B.settings.sectorNotes = {XRT:{follow:true}}; ffRenderThemes(); }"); settle(page, 300)
        js(page, "()=>document.querySelector('[data-rrg-copy]').click()"); settle(page, 400)
        got = js(page, "()=>window.__clip")
        order = js(page, "()=>[...document.querySelectorAll('[data-rr]')].map(e=>e.dataset.rr)")   # ลำดับแถวจริงบนจอ (rrgSortRows)
        nm = {r["sym"]: r["name"] for r in ROWS if "name" in r}
        pick = lambda q: [s for s in order if next((r for r in ROWS if r["sym"] == s), {}).get("quad") == q]
        fm = lambda s: ("★" if s == "XRT" else "") + s + " (" + nm[s] + ")"
        line = lambda lab, q: lab + ": " + (", ".join(fm(s) for s in pick(q)) or "—")
        exp = "\n".join(["RRG Daily · as of 2026-10-29 · vs SPY", line("Leading", "lead"), line("Improving", "imp"), line("Weakening", "weak"), line("Lagging", "lag"), "No data: XLF"])
        check(f"{tag} Copy by phase: ข้อความตรงเป๊ะ (★ ติดตาม · Lagging ว่าง = — · No data ท้ายสุด)", got == exp, got)
        check(f"{tag} Toast 'Copied'", (txt(page, "#sdToast") or "").strip() == "Copied", txt(page, "#sdToast"))
        # ความสูงแถวหัว: ไม่เพิ่มบรรทัดเทียบก่อนแก้ (วัดที่ 3 ความกว้างในส่วน layout)
        # Watchlist / Candidates
        T.wl_seed(page, [T.W("AAA"), T.W("BBB"), T.W("PTT.BK", "TH"), T.W("CCC")])
        T.go_watch(page, "wl")
        shown = T.rows(page)
        js(page, "()=>{ window.__clip = null; ltMenuToggle('__list'); }"); settle(page, 300)
        has_exp = cnt(page, "[data-wl-export]")
        js(page, "()=>document.querySelector('.ltMenu [data-wl-copylist]').click()"); settle(page, 400)
        got = js(page, "()=>window.__clip")
        check(f"{tag} Copy list (Watchlist): ตามลำดับที่แสดง 'AAA, BBB, …' · PTT.BK คงเดิม · ไม่มี prefix ตลาด", got == ", ".join(shown) and "PTT.BK" in got and "SET:" not in got, [got, shown])
        check(f"{tag} Toast 'Copied N tickers' · ไม่มี Export .txt ในเมนู/แถบ", (txt(page, "#sdToast") or "").strip() == f"Copied {len(shown)} tickers" and has_exp == 0 and cnt(page, "[data-wl-export]") == 0, [txt(page, "#sdToast"), has_exp])
        # ตามตัวกรอง (US)
        js(page, "()=>{ wlSetPort('US'); window.__clip = null; ltMenuToggle('__list'); }"); settle(page, 300)
        js(page, "()=>document.querySelector('.ltMenu [data-wl-copylist]').click()"); settle(page, 400)
        got = js(page, "()=>window.__clip"); shown = T.rows(page)
        check(f"{tag} Copy list ตามตัวกรองปัจจุบัน (US เท่านั้น)", got == ", ".join(shown) and "PTT.BK" not in got, [got, shown])
        # Candidates
        T.go_watch(page, "cand")
        cand = js(page, "()=>wlRowsView().rows.map(r=>wlNormTicker(r.sym))")
        js(page, "()=>{ window.__clip = null; if(!document.querySelector('.ltMenu')) ltMenuToggle('__list'); }"); settle(page, 300)
        ok_btn = cnt(page, ".ltMenu [data-wl-copylist]")
        if ok_btn: js(page, "()=>document.querySelector('.ltMenu [data-wl-copylist]').click()"); settle(page, 400)
        got = js(page, "()=>window.__clip")
        check(f"{tag} Copy list ใน Candidates (เมนู ⋯ เดียวกัน) = ตัวกรองปัจจุบันตามลำดับ", ok_btn == 1 and (got or "") == ", ".join(cand), [got, cand])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def layout_tests(pw, w, h):
    """แถวหัว Leadership + แถวกรอง Watchlist: ความสูง/จำนวนบรรทัดเท่าเดิม (เทียบ index ก่อนแก้) · ไม่ overflow"""
    tag = f"[{ENGINE}/layout-{w}]"
    out = {}
    for old in (True, False):
        keep = P39.INDEX
        if old: P39.INDEX = OLD_INDEX
        try:
            b, page, ce, pe = T.launch(pw, w, h)
        finally:
            P39.INDEX = keep
        try:
            go_flow(page, ROWS)
            m = js(page, """()=>{ const bar = document.querySelector('#ffRrgBar > div'); const r = bar.getBoundingClientRect(); const tops = new Set([...bar.children].map(c=>{ const q = c.getBoundingClientRect(); return Math.round((q.top + q.height/2)/20); })); return {h:Math.round(r.height), lines:tops.size, ov:document.documentElement.scrollWidth - document.documentElement.clientWidth}; }""")
            T.wl_seed(page, [T.W("AAA"), T.W("BBB")])
            T.go_watch(page, "wl")
            f = js(page, """()=>{ const e = document.querySelector('.ln3-wl2'); return {h:Math.round(e.getBoundingClientRect().height), ov:document.documentElement.scrollWidth - document.documentElement.clientWidth}; }""")
            out["old" if old else "new"] = {"leadership": m, "filter": f}
        finally:
            b.close()
    LOG["layout_%d" % w] = out
    check(f"{tag} แถวหัว Leadership: ความสูง/จำนวนบรรทัดเท่าเดิม และไม่ overflow", out["old"]["leadership"]["h"] == out["new"]["leadership"]["h"] and out["old"]["leadership"]["lines"] == out["new"]["leadership"]["lines"] and out["new"]["leadership"]["ov"] <= 1, out)
    check(f"{tag} แถวกรอง Watchlist (All|US|TH|Add on candidate|⋯): ความสูงเท่าเดิม · ไม่ overflow", out["old"]["filter"]["h"] == out["new"]["filter"]["h"] and out["new"]["filter"]["ov"] <= 1, out)


if __name__ == "__main__":
    sect = os.environ.get("SECT", "calc plan settings broker copy layout").split()
    with sync_playwright() as pw:
        if "calc" in sect: calc_tests(pw)
        if "plan" in sect:
            for w, h, lb in ((300, 700, "300px"), (390, 844, "390px"), (1280, 800, "1280px"), (1440, 900, "1440px")):
                plan_tests(pw, w, h, lb, shots=(w == 390))
        if "settings" in sect:
            for w, h, lb in ((300, 700, "300px"), (390, 844, "390px"), (1280, 800, "1280px"), (1440, 900, "1440px")):
                settings_tests(pw, w, h, lb, shots=(w in (390, 1440)))
        if "broker" in sect: broker_data_tests(pw)
        if "copy" in sect: copy_tests(pw)
        if "layout" in sect:
            for w, h in ((300, 700), (390, 844), (1440, 900)): layout_tests(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\nสรุป phase110: {len(results) - len(bad)}/{len(results)} ผ่าน")
    print("LOG", json.dumps(LOG, ensure_ascii=False)[:1500])
    sys.exit(1 if bad else 0)
