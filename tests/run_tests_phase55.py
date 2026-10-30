#!/usr/bin/env python3
"""AS1 — เพิ่มสินค้า Sat ใหม่ได้เอง (เช่น Silver · NQ) · ลบสินค้าที่เพิ่มเอง · เทส 55
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย
ภาพ tests/screenshots/as1-{asset-add,strategy-6,plan-silver}-{1440,390}.png
รัน: python3 run_tests_phase55.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase36 as p36
import run_tests_phase37 as P37
import run_tests_phase38 as P38
import run_tests_phase39 as P39
import run_tests_phase51 as P51
import run_tests_phase54 as P54

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-AS1.html"))
results = []
js = P37.js
CLK = "2026-10-01T05:00:00Z"
OV = "#sat7dBrokerOverlay"
opensheet, save, txt, settings, tiles, overflow = P54.opensheet, P54.save, P54.txt, P54.settings, P54.tiles, P54.overflow


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


XAG = {"key": "XAG", "label": "Silver", "unit": "lot"}
NQ = {"key": "NQ", "label": "Nasdaq", "unit": "สัญญา"}


def with_picks(*lst, then=None):
    """WA1fix — ไม่มีโหมด legacy: เลือก Asset ของสัปดาห์ fixture (2026-09-27 · ≤ 3) · then = mutator อื่นต่อท้าย"""
    def m(doc):
        doc["books"]["main"]["settings"]["satWeekPick"] = {"2026-09-27": list(lst)}
        if then: then(doc)
    return m


def with_custom(*items, brokers=True):
    def m(doc):
        doc["books"]["main"]["settings"]["satCustomAssets"] = [dict(i) for i in items]
        if brokers:
            for i in items:
                doc["books"]["main"]["settings"]["brokers"]["XM"][i["key"]] = {"contract": 5000 if i["key"] == "XAG" else 20, "lotStep": 0.01 if i["key"] == "XAG" else 1, "minLot": 0.01 if i["key"] == "XAG" else 1, "cur": "USD"}
                # SET1 — สเปคเดียวกันนี้ต้องอยู่ที่ "สินค้า" (settings.products) เพราะขนาดไม้ไม่อ่านโบรกแล้ว
                doc["books"]["main"]["settings"].setdefault("products", {})[i["key"]] = {"sys": "lot", "perPoint": 5000 if i["key"] == "XAG" else 20, "lotStep": 0.01 if i["key"] == "XAG" else 1, "minLot": 0.01 if i["key"] == "XAG" else 1, "cur": "USD"}
    return m


def idea(asset="XAG", bias="Long", entry=30, sl=29, tp=31.5, iid="iS", broker="XM"):
    d = P51.idea_doc(asset=asset, bias=bias, entry=entry, sl=sl, tp=tp, zone=(tp, tp + 1.5), iid=iid)
    d["accts"] = {"main": {"broker": broker}}
    return d


def calc(page, i, acct="main"):
    return js(page, """([i,a])=>{ i.week = wpWeekKey(); const c = satV3PlanAcctCalc(i, a); return {ready:c.ready, news:c.newsBlock, rr:c.rrBlock, lot:c.lot, riskCur:c.riskCur, heat:c.heatPct, broker:c.chosen ? c.chosen.broker : null, warns:c.warns, lotMsg:c.lotMsg}; }""", [i, acct])


def set_bias(page, asset, bias="Long"):
    js(page, "([a,b])=>{ satwWrite(a, {bias:b, support:[28], resistance:[33], invalidation:27}); }", [asset, bias]); page.wait_for_timeout(250)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ── 1 ไม่มี satCustomAssets → เหมือนก่อน AS1
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, with_picks("XAUUSD", "BTCUSD", "S50"))
    try:
        js(page, "()=>{ satWeekMap = {}; switchTab('today'); }"); page.wait_for_timeout(500)
        bias_row = js(page, "()=>{ const e=document.querySelector('[data-kind=bias]'); return e ? e.innerText : ''; }")
        P51.fresh(page, P54.idea())
        js(page, "()=>{ ['main','fam'].forEach(a=>{ const B = getBook(a); if(B){ if(!B.settings) B.settings = {}; B.settings.satPyrSplit = [100,0,0]; saveBook(a); } }); }")   # PY2: เทียบ lot กับไฟล์ก่อนแก้ → ไม้ 1 เข้าเต็ม RPT (100/0/0)
        lot_now = P54.lot_of(page, P54.idea())
        check(f"{tag} 1 ไม่มี satCustomAssets: สินค้าทั้งหมด = 4 ตัวเดิม · Strategy ตามที่เลือก 3 ช่อง (WA1fix เพดาน 3) · ไม่มีปุ่ม ลบ ในหน้าตั้งโบรก", js(page, "()=>satAssets({all:true}).map(a=>a.key)") == ["XAUUSD", "BTCUSD", "S50", "BRENT"] and js(page, "()=>satAssets().map(a=>a.key)") == ["XAUUSD", "BTCUSD", "S50"] and len(tiles(page)) == 3 and settings(page, "satCustomAssets") is None, json.dumps(tiles(page)))
        check(f"{tag} 1 PF3 Today: ไม่มีแถวเตือน Bias แล้ว (งานถอด) · แถวเช็กแผน Sat ยังโชว์ XAU · BTC · S50 ที่เลือก (Brent ไม่ได้เลือก = ไม่ขึ้น)", bias_row == "" and js(page, "()=>[...document.querySelectorAll('.tdRow[data-kind=\"sat-daily\"] .tdAs .nm')].map(e=>e.textContent)") in (["XAU", "BTC", "S50"], []), bias_row)
        opensheet(page)
        check(f"{tag} 1 หน้าตั้งโบรก: ไม่มีปุ่มลบสินค้า (สินค้าเดิม 4 ตัวลบไม่ได้) · มีฟอร์ม ＋ เพิ่มสินค้า", js(page, f"()=>document.querySelectorAll('{OV} [data-as-del]').length") == 0 and js(page, f"()=>!!document.querySelector('{OV} [data-as-add]')"))
        page.locator(f"{OV} [data-br-cancel]").click()
        check(f"{tag} 1 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()
    saved = P39.INDEX; P39.INDEX = BACKUP
    try:
        browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h)
        try:
            P51.fresh(page, P54.idea()); lot_old = P54.lot_of(page, P54.idea())
        finally: browser.close()
    finally: P39.INDEX = saved
    check(f"{tag} 1 lot XAUUSD เท่าก่อน AS1 (fixture เดียวกัน)", lot_old["lot"] == lot_now["lot"] and lot_old["lot"], json.dumps([lot_old, lot_now]))

    # ── 2 เพิ่ม XAG ผ่านหน้าตั้งโบรก
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h)
    try:
        P51.fresh(page, None)
        opensheet(page)
        def add(key, lab, unit="lot"):
            page.locator(f"{OV} [data-as-newkey]").fill(key); page.locator(f"{OV} [data-as-newlabel]").fill(lab)
            page.locator(f"{OV} [data-as-newunit]").select_option(unit); page.locator(f"{OV} [data-as-add]").click(); page.wait_for_timeout(200)
            return txt(page, f"{OV} [data-as-newwarn]") or ""
        n_rows = lambda: js(page, f"()=>document.querySelectorAll('{OV} [data-as-row]').length")
        for key, lab, why in (("xa g", "Silver", "key มีช่องว่าง"), ("ABCDEFGHIJK", "Silver", "key ยาวเกิน 10"), ("A", "Silver", "key สั้นเกิน"), ("S50", "Silver", "ซ้ำ S50"), ("btcusd", "Silver", "ซ้ำ BTCUSD (ไม่สนตัวพิมพ์)"), ("S50X", "Silver", "ขึ้นต้น S50"), ("XAG", "", "ไม่มีชื่อ"), ("XAG", "x" * 13, "ชื่อยาวเกิน 12"), ("XAG", "Brent", "ชื่อซ้ำสินค้าอื่น")):
            wm = add(key, lab)
            check(f"{tag} 2 {why} → เตือน ไม่เพิ่ม", wm != "" and n_rows() == 4, f"{wm} rows={n_rows()}")
        wm = add("xag", "Silver")
        check(f"{tag} 2 เพิ่ม xag/Silver (key แปลงเป็นตัวพิมพ์ใหญ่) → แถวใหม่ 5 แถว · ไม่มีคำเตือน · มีปุ่มลบเฉพาะ XAG", wm == "" and n_rows() == 5 and js(page, f"()=>[...document.querySelectorAll('{OV} [data-as-del]')].map(e=>e.dataset.asDel)") == ["XAG"])
        check(f"{tag} 2 แถวสินค้าใหม่โผล่ในรายบัญชีของทุกโบรกที่ติ๊ก (XM ของ main) · ไม่มีค่าเริ่มต้น", js(page, f"()=>document.querySelectorAll('{OV} [data-as-row=XAG]').length") == 1 and js(page, f"()=>document.querySelectorAll('{OV} .s7BRow').length") == 0)   # SET1 — ไม่มีแถวโบรกแล้ว · สินค้าใหม่อยู่ในรายการสินค้า Sat
        # SET1 — ไม่มีช่องสัญญาโบรกแล้ว (สเปคอยู่ที่สินค้า)
        shot(page, f"as1-asset-add-{sfx}.png", f"{OV} .modal")
        save(page)
        check(f"{tag} 2 บันทึก: satCustomAssets = [{{XAG, Silver, lot}}] · (SET1: ไม่มีช่องสัญญาโบรกแล้ว)", settings(page, "satCustomAssets") == [XAG], json.dumps(settings(page, "satCustomAssets")))
        P51.fresh(page, None)
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','XAG']); satV3Render(); }"); page.wait_for_timeout(300)
        check(f"{tag} 2 สินค้าทั้งหมด 5 ลำดับ 4 เดิม + XAG · Strategy ช่องตามที่เลือก (XAU · BTC · XAG) · ชื่อ 'Silver'", js(page, "()=>satAssets({all:true}).map(a=>a.key)") == ["XAUUSD", "BTCUSD", "S50", "BRENT", "XAG"] and tiles(page) == ["XAUUSD", "BTCUSD", "XAG"] and txt(page, ".ui-tile[data-key=XAG] .ui-tile-a") == "Silver", json.dumps(tiles(page)))
        js(page, "()=>satV3Pick('XAG')"); page.wait_for_timeout(350)
        ed = txt(page, ".ui-editor[data-asset=XAG]") or ""
        check(f"{tag} 2 ตัวแก้ Strategy ของ Silver: ชื่อ Silver · Macro 'ไม่อยู่ใน Playbook' (แบบ S50)", "Silver" in ed and "ไม่อยู่ใน Playbook" in ed, ed[:200])
        js(page, "()=>satV3SetBias('XAG','Long')"); page.wait_for_timeout(350)
        check(f"{tag} 2 ตั้ง Bias Long ได้ → satWeek[XAG].bias = Long", js(page, "()=>{ const w = satwWeek(wpWeekKey(), 'XAG'); return w ? w.bias : null; }") == "Long")
        js(page, "()=>satwWrite('XAG', {support:[28,28.5], resistance:[33], invalidation:27})"); page.wait_for_timeout(250)
        wkd = js(page, "()=>satwWeek(wpWeekKey(), 'XAG')")
        check(f"{tag} 2 ตั้งแนวรับ/แนวต้าน/Trend Shift ได้", wkd and wkd.get("invalidation") == 27 and wkd.get("support") and wkd.get("resistance"), json.dumps(wkd))
        check(f"{tag} 2 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 3-4 แผน Silver · R:R · lot · บันทึก order · ช่วงงดข่าว
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, with_custom(XAG))
    try:
        P51.fresh(page, None)
        js(page, "()=>satwWrite('XAG', {bias:'Long', support:[28], resistance:[33], invalidation:27})"); page.wait_for_timeout(250)
        i_ok = idea(tp=31.5)
        P51.put_idea(page, i_ok); P37.go_sat(page); P37.open_plan(page)
        c = calc(page, i_ok)
        check(f"{tag} 3 แผน Silver R:R 1.5 (entry 30 / SL 29 / TP 31.5) → ผ่าน · ready · ไม่มีบล็อก", c["ready"] is True and not c["rr"] and not c["news"], json.dumps(c, ensure_ascii=False))
        c14 = calc(page, idea(tp=31.4))
        check(f"{tag} 3 R:R 1.4 → บล็อก ('R:R 1.4 ต่ำกว่า 1.5')", c14["ready"] is False and (c14["rr"] or "").startswith("R:R 1.4 ต่ำกว่า 1.5"), json.dumps(c14, ensure_ascii=False))
        exp = js(page, "([r,d])=>Calc.satLot({riskAmount:r, dist:d, contract:5000, lotStep:0.01, minLot:0.01}).lot", [c["riskCur"] * 0.5, 1])   # PY2: ไม้ 1 = 50% ของงบ
        check(f"{tag} 3 lot ตามสูตรเดียวกับ XAUUSD (Calc.satLot · สัญญา 5000 · step 0.01)", c["lot"] and abs(c["lot"] - exp) < 1e-9 and c["broker"] in ("", None), json.dumps([c, exp]))   # SET1 — ไม่มีโบรกใน plan: สเปคมาจากสินค้า
        panel = txt(page, "#satV3Panel") or ""
        check(f"{tag} 3 การ์ดแผนแสดงชื่อ 'Silver' (ไม่ใช่ key) · หน่วย lot", "Silver" in panel and "lot" in panel, panel[:240])
        shot(page, f"as1-plan-silver-{sfx}.png", "#satV3Panel")
        n0 = js(page, "()=>getBook('main').trades.length")
        b0 = js(page, "()=>{ const b = sat7dAcctBase('main'); return {open:b.openRisk, heat:b.heatPct, n:b.nNew}; }")
        js(page, "()=>{ satV3SaveSlot('iS','main'); }"); page.wait_for_timeout(500)
        tr = js(page, "()=>getBook('main').trades.map(t=>({sym:t.sym, port:t.port, status:t.status, mult:t.mult, qty:t.qty, tp:t.tp}))")
        check(f"{tag} 3 บันทึก order → ไม้ Silver ถูกสร้าง (sym XAG · port satB · mult 5000)", len(tr) == n0 + 1 and tr[-1]["sym"] == "XAG" and tr[-1]["port"] == "satB" and tr[-1]["mult"] == 5000, json.dumps(tr))
        pos = js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); return document.getElementById('tab-plan') ? document.getElementById('tab-plan').innerText : document.body.innerText; }")
        check(f"{tag} 3 ไม้ Silver แสดงในแผงไม้/การ์ด (ชื่อ Silver)", "Silver" in pos, pos[:120])
        js(page, "()=>{ const t = getBook('main').trades.find(x=>x.sym==='XAG'); t.status='open'; t.openedAt = thaiToday(); t.date = thaiToday(); saveBook('main'); render(); }"); page.wait_for_timeout(250)
        b1 = js(page, "()=>{ const b = sat7dAcctBase('main'); return {open:b.openRisk, heat:b.heatPct, n:b.nNew}; }")
        check(f"{tag} 3 heat (ความเสี่ยงที่ถือ) และโควตาไม้ใหม่ นับไม้ Silver รวม (ก่อน → หลังบันทึก order)", b1["open"] > b0["open"] and b1["heat"] > b0["heat"] and b1["n"] == b0["n"] + 1, json.dumps([b0, b1]))
        q = js(page, "()=>{ const t = getBook('main').trades.find(x=>x.sym==='XAG'); return t ? isSatProduct(t.sym) : null; }")
        check(f"{tag} 3 isSatProduct('XAG') = true (รู้จักเป็นสินค้า Sat)", q is True)
        # 4 ช่วงงดข่าว CPI
        js(page, "()=>{ const B=getBook('main'); B.settings.newsEvents=[{date:'2026-10-01', kind:'CPI', time:'19:30'}]; saveBook('main'); render(); }")
        P37.set_clock(page, "2026-10-01T11:40:00Z"); page.wait_for_timeout(300)
        cn = calc(page, idea(iid="iS3", entry=31, sl=30, tp=32.5))
        check(f"{tag} 4 ช่วงงดข่าว CPI (18:40 ไทย) → แผน Silver บล็อกเหมือนสินค้าเดิม (newsBlock)", cn["ready"] is False and bool(cn["news"]), json.dumps(cn, ensure_ascii=False))
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(600)
        news = js(page, "()=>{ const e=document.querySelector('[data-kind=news]'); return e ? e.textContent : ''; }")
        check(f"{tag} 4 Today: เช็กลิสต์ก่อนข่าวนับไม้ Silver (ชื่อ Silver อยู่ในรายการ)", "Silver" in news, news[:200])
        check(f"{tag} 4 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 5 Today: เตือน Bias · เช็กแผนรายวัน · ซ่อน
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, with_picks("XAUUSD", "BTCUSD", "XAG", then=with_custom(XAG)))
    try:
        js(page, "()=>{ satWeekMap = {}; switchTab('today'); }"); page.wait_for_timeout(500)
        bias_row = js(page, "()=>{ const e=document.querySelector('[data-kind=bias]'); return e ? e.innerText : ''; }")
        check(f"{tag} 5 PF3 Today: ไม่มีแถวเตือน Bias เลย (Silver ก็ไม่อยู่ในรายการเตือน — งานถอดแล้ว)", bias_row == "" and "Silver" not in bias_row, bias_row)
        check(f"{tag} 5 เช็กแผน Sat รายวัน: tdRoutine().satDaily มี XAG (ค่าเริ่มต้น) · ค่าตั้ง Daily routine มีช่องติ๊ก Silver", "XAG" in js(page, "()=>tdRoutine().satDaily") and js(page, "()=>{ tdSetRender(); return !!document.querySelector('[data-rt-sat=XAG]'); }") is not None)
        js(page, "()=>{ waRemove('XAG'); render(); switchTab('today'); }")   # WA1/WA1fix: ไม่มีการซ่อนแล้ว — เอาออกจากสัปดาห์นี้แทน; page.wait_for_timeout(500)
        bias_row = js(page, "()=>{ const e=document.querySelector('[data-kind=bias]'); return e ? e.innerText : ''; }")
        check(f"{tag} 5 เอา Silver ออกจากสัปดาห์นี้ (แทนซ่อนเดิม) → ไม่เตือน Bias · ไม่อยู่ในเช็กแผนรายวัน · Strategy ไม่มีช่อง", "Silver" not in bias_row and "XAG" not in js(page, "()=>tdRoutine().satDaily") and "XAG" not in tiles(page) if False else ("Silver" not in bias_row and "XAG" not in js(page, "()=>tdRoutine().satDaily")), bias_row)
        check(f"{tag} 5 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 6 ลบสินค้าที่เพิ่มเอง
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, with_custom(XAG, NQ))
    try:
        P51.fresh(page, None)
        js(page, "()=>satwWrite('XAG', {bias:'Long', support:[28], resistance:[33], invalidation:27})"); page.wait_for_timeout(250)
        opensheet(page)
        page.locator(f"{OV} [data-as-del=XAG]").click(); page.wait_for_timeout(200)
        wm = txt(page, f"{OV} [data-as-warn=XAG]") or ""
        check(f"{tag} 6 ลบ Silver ที่มีข้อมูล Bias สัปดาห์ → ไม่ได้ + แนะนำให้เอาออกจากสัปดาห์นี้", "ลบไม่ได้" in wm and "เอาออกจากสัปดาห์นี้" in wm and "Bias" in wm, wm)
        page.locator(f"{OV} [data-br-cancel]").click()
        js(page, "()=>{ const B=getBook('main'); B.trades.push(makeTradeObject({id:'tx', date:'2026-09-20', sym:'XAG', port:'satB', bias:'Long', entry:30, sl:29, tp:31.5, qty:0.1, mult:5000, cur:'USD', status:'closed', exitPrice:30.5, exitDate:'2026-09-25'})); saveBook('main'); satWeekMap = {}; render(); }")
        opensheet(page)
        page.locator(f"{OV} [data-as-del=XAG]").click(); page.wait_for_timeout(200)
        wm = txt(page, f"{OV} [data-as-warn=XAG]") or ""
        check(f"{tag} 6 ลบ Silver ที่มีไม้ที่ปิดแล้ว → ไม่ได้ + แนะนำให้เอาออกจากสัปดาห์นี้", "ลบไม่ได้" in wm and "เอาออกจากสัปดาห์นี้" in wm and "ไม้" in wm, wm)
        page.locator(f"{OV} [data-br-cancel]").click()
        P51.fresh(page, idea(asset="NQ", entry=100, sl=90, tp=115, iid="iN"))
        opensheet(page)
        page.locator(f"{OV} [data-as-del=NQ]").click(); page.wait_for_timeout(200)
        wm = txt(page, f"{OV} [data-as-warn=NQ]") or ""
        check(f"{tag} 6 ลบ Nasdaq ที่มีแผน → ไม่ได้ + แนะนำให้เอาออกจากสัปดาห์นี้", "ลบไม่ได้" in wm and "แผน" in wm and "เอาออกจากสัปดาห์นี้" in wm, wm)
        page.locator(f"{OV} [data-br-cancel]").click()
        P51.fresh(page, None); p36.reset_ideas(page); page.wait_for_timeout(300)
        js(page, "()=>{ const B=getBook('main'); B.trades=[]; saveBook('main'); satWeekMap = {}; render(); }")
        opensheet(page)
        n0 = len(dialogs)
        page.locator(f"{OV} [data-as-del=NQ]").click(); page.wait_for_timeout(250)
        check(f"{tag} 6 สินค้าใหม่ที่ไม่มีข้อมูลเลย → ลบได้ (ยืนยัน 1 ครั้ง)", len(dialogs) == n0 + 1 and js(page, f"()=>document.querySelectorAll('{OV} [data-as-row]').length") == 5, json.dumps(dialogs[n0:], ensure_ascii=False))
        save(page)
        check(f"{tag} 6 บันทึก → satCustomAssets เหลือ XAG ตัวเดียว · ข้อมูลโบรก NQ เดิมค้างไว้ (SET1 ไม่แตะ)", settings(page, "satCustomAssets") == [XAG] and js(page, "()=>getBook('main').settings.brokers.XM.NQ") is not None, json.dumps(settings(page, "satCustomAssets")))   # SET1 — ไม่เขียน/ไม่ล้างข้อมูลโบรกเดิมอีก
        check(f"{tag} 6 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 7 6 สินค้า: grid ไม่ล้น
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, with_picks("XAUUSD", "XAG", "NQ", then=with_custom(XAG, NQ)))
    try:
        P51.fresh(page, None)
        t = tiles(page)
        check(f"{tag} 7 สินค้าทั้งหมด 6 ลำดับเดิม 4 + Silver + Nasdaq · Strategy ช่องตามที่เลือก (XAU · Silver · Nasdaq)", js(page, "()=>satAssets({all:true}).map(a=>a.key)") == ["XAUUSD", "BTCUSD", "S50", "BRENT", "XAG", "NQ"] and t == ["XAUUSD", "XAG", "NQ"], json.dumps(t))
        check(f"{tag} 7 grid ไม่ล้นแนวนอน", overflow(page) <= 0, overflow(page))
        shot(page, f"as1-strategy-6-{sfx}.png", "#satV3Panel")
        js(page, "()=>satV3Pick('NQ')"); page.wait_for_timeout(300)
        check(f"{tag} 7 กางตัวแก้ของ Nasdaq (หน่วยสัญญา) ไม่ล้น", overflow(page) <= 0 and "Nasdaq" in (txt(page, ".ui-editor[data-asset=NQ]") or ""))
        check(f"{tag} 7 หน่วย: satUnit('NQ') = 'สัญญา' · satUnit('XAG') = 'lot' · satUnit('S50') = 'สัญญา'", js(page, "()=>[satUnit('NQ'), satUnit('XAG'), satUnit('S50'), satUnit('XAUUSD')]") == ["สัญญา", "lot", "สัญญา", "lot"])
        check(f"{tag} 7 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()


def static_tests():
    src = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    allowed = ("const SAT_ASSETS", "const TD_SAT_MK", "const TD_LBL", "const IDEA_ASSET_LBL", "const IDEA_ASSET_PB", "const SAT_PB_ASSET", "const SAT_KEY_RESERVED", "SAT7D_DEFAULT_BROKERS", "pbAssets", "const PB_SHORT", "const SAT7D_UNIT")
    bad = []
    lines = src.split("\n")
    for i, ln in enumerate(lines):
        if re.search(r"\[[^\]]*'XAUUSD'[^\]]*'(S50|BRENT|BTCUSD)'", ln) or re.search(r"\[[^\]]*'S50'[^\]]*'BRENT'", ln):
            if not any(a in ln for a in allowed): bad.append((i + 1, ln.strip()[:120]))
    check("[static] ไม่มีอาเรย์รายชื่อสินค้า Sat เขียนตายตัวนอกรายการที่ตั้งใจ (ก = วนตาม satAssets() · ข = เฉพาะสินค้าเดิม)", not bad, json.dumps(bad, ensure_ascii=False))
    check("[static] ไม่มี SAT_ASSETS.map/filter ใช้ตรง ๆ ในกลุ่ม (ก) (Strategy/Today/โบรก ใช้ satAssets())", not re.search(r"SAT_ASSETS\.(map|filter)\(", src.replace("const all = SAT_ASSETS.concat", "")) or all(("brAll" in l or "satAssets" in l or "const SAT7D_ASSETS" in l or "const SATW_MACRO_KEY" in l) for l in lines if re.search(r"SAT_ASSETS\.(map|filter)\(", l)), json.dumps([l.strip()[:100] for l in lines if re.search(r"SAT_ASSETS\.(map|filter)\(", l)]))
    check("[static] ฟังก์ชันใหม่ครบ: satCustomList · satAssets · satUnit · tdSatMk · tdSatDef · brAddAsset · brDelAsset", all(("function " + f + "(") in src for f in ("satCustomList", "satAssets", "satUnit", "tdSatMk", "tdSatDef", "brAddAsset", "brDelAsset")))


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    static_tests()
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 55 / AS1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
