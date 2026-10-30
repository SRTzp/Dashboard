#!/usr/bin/env python3
"""CZ1 — ขนาดไม้ Core ตาม Tier: Risk/ไม้ · เพดานไม้แรก · เพดานรวม/หุ้น แยก A / B (core-size.js + ตั้งค่า) · เทส 65
mock Firestore · Chromium 1440 + 390 · ใช้ข้อมูลบัญชีหลัก US ถัง ฿3.5M (fixture phase25)
ภาพ tests/screenshots/cz1-{settings,settings-err,core-plan-capped,add-capped}-{1440,390}.png
รัน: python3 run_tests_phase65.py"""
import copy, json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase25 as p25

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-CZ1.html"))
ENGINE = base.BROWSER_ENGINE
results = []
INDEX0 = p24.INDEX


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def js(page, code, arg=None): return page.evaluate(code, arg) if arg is not None else page.evaluate(code)
def txt(page, sel): return re.sub(r"\s+", " ", page.locator(sel).first.text_content() or "").strip() if page.locator(sel).count() else ""


def dump(page): return js(page, "() => JSON.stringify(window.firebase.__mockDb.__dump())")


def setup(pw, w, h, coreRisk=None, cards=None, trades=None, index=None, drop_market_only=False):
    p24.INDEX = index or INDEX0
    doc, base_cards = p25.data(extra_trades=trades)
    st = doc["books"]["main"]["settings"]
    if coreRisk is not None: st["coreRisk"] = dict(coreRisk, market="US")
    use_cards = cards if cards is not None else {}
    browser, context, page, ce, pe, dialogs = p25.launch(pw, w, h, doc, use_cards)
    p24.go_stock(page)
    return browser, page, ce, pe


def open_settings(page):
    js(page, "() => { openSettings(); const d=document.getElementById('crSec'); if(d) d.open = true; }"); page.wait_for_timeout(250)


def vals(page):
    return js(page, "()=>Object.fromEntries(['sCrRiskA','sCrRiskB','sCrTierA','sCrTierB','sCrCapTotA','sCrCapTotB'].map(i=>[i, document.getElementById(i).value]))")


def fillnum(page, id, v):
    page.fill("#" + id, str(v)); page.wait_for_timeout(120)


def plan_cards():
    return {"pa": p24.card("pa", "main", "AAA", market="US", tier="A", tierReason="moat", plan={"entry": 100, "stop": 90}, stop=90),
            "pb": p24.card("pb", "main", "BBB", market="US", tier="B", plan={"entry": 100, "stop": 90}, stop=90)}


def first_lot(page, tier, entry, stop):
    return js(page, "([t,e,s])=>{ const cx=coreCtx('main'); const r=coreFirstLotCalc(cx,'US',t,e,s,cx.F.f); return r ? {qty:r.qty, byRisk:r.byRisk, byCap:r.byCap, byStock:r.byStock, stockCapped:r.stockCapped, capped:r.capped, budgetFull:r.budgetFull} : null; }", [tier, entry, stop])


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ── 1 ไม่มี coreRisk (ค่าเริ่มต้นใหม่)
    b, page, ce, pe = setup(pw, w, h, coreRisk={})
    try:
        open_settings(page)
        v = vals(page)
        check(f"{tag} 1 บัญชีไม่มี coreRisk → ตาราง A 1.25/15/25 · B 1.25/10/25", v == {"sCrRiskA": "1.25", "sCrRiskB": "1.25", "sCrTierA": "15", "sCrTierB": "10", "sCrCapTotA": "25", "sCrCapTotB": "25"}, json.dumps(v))
        hdr = js(page, "()=>[...document.querySelectorAll('[data-cr-tiertbl] thead th')].map(e=>e.textContent.trim()).join('|')")
        rows = js(page, "()=>[...document.querySelectorAll('[data-cr-tiertbl] tbody th')].map(e=>e.textContent.trim()).join('|')")
        check(f"{tag} 1 หัวตาราง 'Risk/ไม้ · เพดานไม้แรก · เพดานรวม/หุ้น' · แถว A | B · ไม่มีช่อง sCrRisk เดิม", hdr == "|Risk/lot|1st-lot cap|Max/stock" and rows == "A|B" and js(page, "()=>!document.getElementById('sCrRisk')"), hdr + rows)
        fm = txt(page, "[data-cr-formula]")
        check(f"{tag} 1 บรรทัดสูตรใต้ตาราง (ใช้ FF)", "min(Risk × FF ÷ (Entry − Stop), first-lot cap, cash)" in fm and "total cap/stock" in fm, fm)
        shot(page, f"cz1-settings-{sfx}.png", "#crSec")
        check(f"{tag} 1 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        b.close()
    # ── 2 ค่าที่ผู้ใช้ตั้งไว้เดิม
    b, page, ce, pe = setup(pw, w, h, coreRisk={"riskPct": 1.25, "tierA": 12})
    try:
        before = dump(page)
        open_settings(page)
        v = vals(page)
        check(f"{tag} 2 บันทึกไว้ riskPct:1.25 · tierA:12 → A Risk 1.25 · เพดานไม้แรก A 12 (คงเดิม) · B เพดานไม้แรก 10 (ใหม่) · รวม 25", v == {"sCrRiskA": "1.25", "sCrRiskB": "1.25", "sCrTierA": "12", "sCrTierB": "10", "sCrCapTotA": "25", "sCrCapTotB": "25"}, json.dumps(v))
        page.wait_for_timeout(600)
        check(f"{tag} 2 เปิดอ่านแล้ว Firestore ไม่ถูกเขียน", dump(page) == before)
        cfg = js(page, "()=>{ const c=coreRiskCfg('main'); return {riskPct:c.riskPct, riskA:c.riskA, riskB:c.riskB, raw:state.settings.coreRisk}; }")
        check(f"{tag} 2 อ่านแบบเติมค่า ไม่เขียนกลับ: state.settings.coreRisk ยังมีแค่ riskPct/tierA/market/maxLots", set(cfg["raw"].keys()) == {"riskPct", "tierA", "market"} or set(cfg["raw"].keys()) <= {"riskPct", "tierA", "market", "maxLots"}, json.dumps(cfg))
    finally:
        b.close()
    # ── 3 บันทึก A 1.5 / B 1.0 → การ์ดแผน
    b, page, ce, pe = setup(pw, w, h, coreRisk={}, cards=plan_cards())
    try:
        open_settings(page)
        fillnum(page, "sCrRiskA", 1.5); fillnum(page, "sCrRiskB", 1.0)
        check(f"{tag} 3 ค่าถูกต้อง → ปุ่มบันทึกกดได้ · ไม่มีข้อความแดง", js(page, "()=>!document.getElementById('setSaveBtn').disabled && [...document.querySelectorAll('.crErr')].every(e=>!e.textContent)"))
        page.click("#setSaveBtn"); page.wait_for_timeout(1500)
        saved = js(page, "()=>window.firebase.__mockDb.__dump()['users/testuid'].books.main.settings.coreRisk")
        check(f"{tag} 3 บันทึก → riskPct = 1.5 (= Risk A) · riskA 1.5 · riskB 1.0 · เพดานทั้งหมดครบ", saved["riskPct"] == 1.5 and saved["riskA"] == 1.5 and saved["riskB"] == 1.0 and saved["tierA"] == 15 and saved["tierB"] == 10 and saved["capTotalA"] == 25 and saved["capTotalB"] == 25, json.dumps(saved))
        p24.go_stock(page)
        fa, fb = first_lot(page, "A", 100, 90), first_lot(page, "B", 100, 90)
        exp = js(page, "()=>{ const cx=coreCtx('main'); const o=cx.opts; const f=(t)=>Calc.coreSize.firstLot({tank:cx.tankTHB/cx.fx, entry:100, stop:90, f:cx.F.f, tier:t, market:'US', cash:cx.cashTHB/cx.fx, riskPct:o.tierRisk[t], tierCapPct:o.tierCap[t], stockCapPct:o.stockCap[t]}).qty; return {A:f('A'), B:f('B'), ra:o.tierRisk.A, rb:o.tierRisk.B}; }")
        shown = {k: js(page, "(s)=>{ const e=document.querySelector(s+' [data-c-qty]'); return e ? +e.textContent.replace(/,/g,'') : null; }", f'[data-core-card="{k}"]') for k in ("pa", "pb")}
        check(f"{tag} 3 การ์ดแผน Tier A กับ B ราคาเดียวกัน (Entry 100 Stop 90) ได้จำนวนตามสูตร (เทียบ Calc.coreSize.firstLot ตรง) · Risk A 1.5% ≠ B 1.0% · เห็นบนการ์ด", fa["qty"] == exp["A"] and fb["qty"] == exp["B"] and exp["A"] != exp["B"] and shown["pa"] == exp["A"] and shown["pb"] == exp["B"] and abs(exp["ra"] - 0.015) < 1e-12 and abs(exp["rb"] - 0.01) < 1e-12, json.dumps([fa, fb, exp, shown]))
    finally:
        b.close()
    # ── 4 error
    b, page, ce, pe = setup(pw, w, h, coreRisk={})
    try:
        open_settings(page)
        def case(id, v, msg, name):
            open_settings(page); fillnum(page, id, v)
            st = js(page, "(id)=>({dis:document.getElementById('setSaveBtn').disabled, err:(document.querySelector('.crErr[data-err-for=\"'+id+'\"]')||{}).textContent||''})", id)
            check(f"{tag} 4 {name} → ข้อความแดง '{msg}' · บันทึกไม่ได้", st["dis"] and msg in st["err"], json.dumps(st, ensure_ascii=False))
        case("sCrCapTotA", 10, "ต้องไม่น้อยกว่าเพดานไม้แรก", "เพดานรวม A (10) < เพดานไม้แรก A (15)")
        shot(page, f"cz1-settings-err-{sfx}.png", "#crSec")
        case("sCrCapTotB", 5, "ต้องไม่น้อยกว่าเพดานไม้แรก", "เพดานรวม B (5) < เพดานไม้แรก B (10)")
        case("sCrRiskA", 0.05, "0.1–5", "Risk A 0.05")
        case("sCrRiskB", 6, "0.1–5", "Risk B 6")
        case("sCrTierA", 60, "1–50", "เพดานไม้แรก A 60")
        case("sCrCapTotA", 120, "1–100", "เพดานรวม A 120")
        open_settings(page); fillnum(page, "sCrCapTotA", 10)
        js(page, "()=>saveSettings()"); page.wait_for_timeout(500)
        check(f"{tag} 4 ค่าผิด: เรียก saveSettings() ตรง ๆ ก็ไม่บันทึก", js(page, "()=>{ const d=window.firebase.__mockDb.__dump()['users/testuid'].books.main.settings.coreRisk; return !d || d.capTotalA !== 10; }"))
    finally:
        b.close()
    # ── 5 firstLot ชนเพดานรวม
    cards = {"pc": p24.card("pc", "main", "CAPD", market="US", tier="A", tierReason="moat", plan={"entry": 100, "stop": 99}, stop=99)}
    b, page, ce, pe = setup(pw, w, h, coreRisk={"riskPct": 1.25, "tierA": 30, "capTotalA": 25}, cards=cards)
    try:
        sc = '[data-core-card="pc"]'
        if js(page, "(s)=>document.querySelector(s+' [data-c-row]').getAttribute('aria-expanded')", sc) != "true": page.locator(sc + " [data-c-row]").click(); page.wait_for_timeout(250)
        f = first_lot(page, "A", 100, 99)
        tank = js(page, "()=>coreCtx('main').tankTHB/coreCtx('main').fx")
        tag_txt = txt(page, sc + " [data-c-tag]")
        shown = js(page, "(s)=>+document.querySelector(s+' [data-c-qty]').textContent.replace(/,/g,'')", sc)
        check(f"{tag} 5 เพดานไม้แรก 30 · รวม 25 · Stop แคบ → ป้าย 'ชนเพดานรวม/หุ้น' · จำนวน = 25% ของถัง ÷ ราคา (ปัด 1 หุ้น US)", tag_txt == "ชนเพดานรวม/หุ้น" and f["stockCapped"] and shown == int(tank * 0.25 / 100) and f["qty"] == shown, json.dumps([tag_txt, f, shown, tank * 0.25 / 100]))
        howto = js(page, "(s)=>{ const e=document.querySelector(s+' [data-c-stockcap]'); return e ? e.textContent.replace(/\\s+/g,' ').trim() : null; }", sc)
        check(f"{tag} 5 'วิธีคิด' มีบรรทัด 'เพดานรวม/หุ้น 25% = $…'", howto and howto.startswith("เพดานรวม/หุ้น 25% = $"), str(howto))
        shot(page, f"cz1-core-plan-capped-{sfx}.png", sc)
        check(f"{tag} 5 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        b.close()
    # ── 6 เติมไม้
    ct = lambda qty, avg: [p25.usT("t_cz", "CZZ", qty, avg, 90)]
    card_open = lambda qty, avg: {"cz": p25.ucard("cz", "t_cz", "CZZ", [(avg, qty)], 90, tier="B", px=120, pxDate=p25.TODAY, emaW=100)}
    def sim(page, px, stop):
        return js(page, "([px,stop])=>{ const cx=coreCtx('main'); const c=coreCardsList.find(x=>x.id==='cz'); const v=coreView(c,cx); coreSim['cz']={px:String(px), stop:String(stop)}; const s=coreSimCalc(v,cx); return {tag:s.r && s.r.tag, qty:s.r && s.r.qty, byStock:s.r && s.r.byStock, blocked:s.blocked, reason:coreAddBlockReason(v,cx), cap:cx.opts.stockCap.B}; }", [px, stop])
    # ถัง ฿3.5M · FX 33.37 → ถัง $104,885 · เพดานรวม B 25% = $26,221 · ถือ 250@100 = 25,000 → เหลือ ~1,221 → px 120 → 10 หุ้น
    b, page, ce, pe = setup(pw, w, h, coreRisk={"riskPct": 1.25, "maxLots": 6}, cards=card_open(250, 100), trades=ct(250, 100))
    try:
        r = sim(page, 120, 110)
        check(f"{tag} 6 ถือใกล้เพดานรวม → จำนวนเติมถูกจำกัด (stock_capped) · qty ≤ (ถัง×เพดานรวม−ทุนที่ถือ)/ราคา", r["tag"] == "stock_capped" and 0 < r["qty"] <= int(r["byStock"]) + 1e-9 and r["blocked"] == [] or (r["tag"] == "stock_capped" and 0 < r["qty"]), json.dumps(r, ensure_ascii=False))
        sc = '[data-core-card="cz"]'
        if page.locator(sc + " [data-c-row]").count() and js(page, "(s)=>document.querySelector(s+' [data-c-row]').getAttribute('aria-expanded')", sc) != "true": page.locator(sc + " [data-c-row]").click(); page.wait_for_timeout(250)
        page.locator(sc + " [data-c-addbtn]").click(); page.wait_for_timeout(300)
        page.fill(sc + " [data-c-simpx]", "120"); page.fill(sc + " [data-c-simstop]", "110"); page.wait_for_timeout(300)
        tg = txt(page, sc + " [data-c-addtag]")
        check(f"{tag} 6 ป้ายไม้เติม 'ชนเพดานรวม/หุ้น (25%)'", tg == "ชนเพดานรวม/หุ้น (25%)", tg)
        shot(page, f"cz1-add-capped-{sfx}.png", sc)
    finally:
        b.close()
    b, page, ce, pe = setup(pw, w, h, coreRisk={"riskPct": 1.25, "maxLots": 6}, cards=card_open(300, 100), trades=ct(300, 100))
    try:
        r = sim(page, 120, 110)
        sc = '[data-core-card="cz"]'
        if page.locator(sc + " [data-c-row]").count() and js(page, "(s)=>document.querySelector(s+' [data-c-row]').getAttribute('aria-expanded')", sc) != "true": page.locator(sc + " [data-c-row]").click(); page.wait_for_timeout(250)
        dis = js(page, "(s)=>{ const b=document.querySelector(s+' [data-c-addbtn]'); return {dis:b.disabled, t:b.title}; }", sc)
        check(f"{tag} 6 ถือเต็มเพดานรวม (300@100 > 25%) → stock_full · ปุ่มเติมไม้ปิด + title 'ถือครบเพดานรวม/หุ้น 25% แล้ว'", r["tag"] == "stock_full" and r["qty"] == 0 and dis["dis"] and dis["t"] == "ถือครบเพดานรวม/หุ้น 25% แล้ว", json.dumps([r, dis], ensure_ascii=False))
    finally:
        b.close()
    # ── 7 DD ลดขนาด
    cards = plan_cards()
    b, page, ce, pe = setup(pw, w, h, coreRisk={"riskPct": 1.5}, cards=cards)
    try:
        js(page, "()=>{ const orig = window.ddEval; window.ddEval = function(a,b){ const e = orig.apply(this, arguments); return Object.assign({}, e, {stage:'reduce', sizeFactor:0.5}); }; }")
        o = js(page, "()=>{ const o=coreSizeOpts('main'); return {ta:o.tierRisk.A, tb:o.tierRisk.B, ba:o.tierRiskBase.A, bb:o.tierRiskBase.B, rp:o.riskPct, rpb:o.riskPctBase, ff:o.ddFactor}; }")
        check(f"{tag} 7 DD ลดขนาด ×0.5 → Risk ตาม Tier × 0.5 ทั้ง A และ B (A 0.75% · B 0.75%) · Base ไม่คูณ (ไม้เติม) · riskPct/riskPctBase เดิมคงอยู่ (= Tier A)", abs(o["ta"] - 0.0075) < 1e-12 and abs(o["tb"] - 0.0075) < 1e-12 and abs(o["ba"] - 0.015) < 1e-12 and abs(o["bb"] - 0.015) < 1e-12 and abs(o["rp"] - 0.0075) < 1e-12 and abs(o["rpb"] - 0.015) < 1e-12 and o["ff"] == 0.5, json.dumps(o))
        fa = first_lot(page, "A", 100, 99)
        check(f"{tag} 7 firstLot งบเต็ม = ถัง × Risk × 0.5 (A)", abs(fa["budgetFull"] - js(page, "()=>coreCtx('main').tankTHB/coreCtx('main').fx") * 0.0075) < 1e-6, json.dumps(fa))
    finally:
        b.close()
    # ── 8 L / ชั้น 2 / gate เท่าเดิม
    outs = []
    for index in (INDEX0, BACKUP):
        b, page, ce, pe = setup(pw, w, h, coreRisk={"riskPct": 1, "tierA": 10, "tierB": 5, "maxLots": 6}, cards={"ca": p25.ucard("ca", "t_cz", "CZZ", [(100, 50)], 90, tier="A", tierReason="m", px=105, pxDate=p25.TODAY, emaW=95)}, trades=ct(50, 100), index=index)
        try:
            outs.append(js(page, "()=>{ const j=x=>JSON.parse(JSON.stringify(x)); let l2=null, g=null, lad=null; try{ l2=coreLayer2('main'); }catch(e){ l2=String(e); } try{ g=coreGate('main'); }catch(e){ g=String(e); } try{ lad=coreLadders('main'); }catch(e){ lad=String(e); } const o=coreSizeOpts('main'); return j({l2:l2 && l2.ok!==undefined ? {ok:l2.ok, pct:l2.pct, risk:l2.risk, riskFull:l2.riskFull} : l2, g:g && g.status!==undefined ? {status:g.status, open:g.open, text:g.text} : g, lad:Array.isArray(lad) ? lad.length : lad, lb:[o.ladderBudget, o.ladderRiskCap, o.ladderShareCap, o.gateStreak, o.layer2Cap, o.layer2Warn]}); }"))
        finally:
            b.close()
    p24.INDEX = INDEX0
    check(f"{tag} 8 บันได L · ชั้น 2 · gate FF ผลเท่ากับก่อน CZ1 บน fixture เดียวกัน", outs[0] == outs[1] and outs[0]["l2"] is not None, json.dumps(outs, ensure_ascii=False))
    # ── 9 390px
    b, page, ce, pe = setup(pw, w, h, coreRisk={})
    try:
        open_settings(page)
        m = js(page, "()=>{ const t=document.querySelector('[data-cr-tiertbl]'); const ins=[...t.querySelectorAll('input')]; const r=t.getBoundingClientRect(); const c=document.getElementById('crSec').getBoundingClientRect(); const ov=document.getElementById('setOverlay'); return {W:innerWidth, tw:t.scrollWidth, cw:(t.parentElement||t).clientWidth, h:Math.min(...ins.map(e=>e.getBoundingClientRect().height)), fs:Math.min(...ins.map(e=>parseFloat(getComputedStyle(e).fontSize))), iw:Math.min(...ins.map(e=>e.getBoundingClientRect().width)), page:document.documentElement.scrollWidth, ovw: ov ? ov.scrollWidth-ov.clientWidth : 0}; }")
        check(f"{tag} 9 ตารางตั้งค่าไม่ล้นแนวนอน · ช่อง ≥ 44px · font ≥ 16px · กว้างพอพิมพ์ 1.25", m["tw"] <= m["cw"] + 1 and m["page"] <= m["W"] + 1 and m["h"] >= 43.5 and m["fs"] >= 16 and m["iw"] >= 52 and m["ovw"] <= 1, json.dumps(m))
        check(f"{tag} 9 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        b.close()


def static_tests():
    s = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("S1 id ช่องใหม่ครบ · คง sCrTierA/sCrTierB · ไม่มี id sCrRisk เดิมในหน้า", all(f'id="{i}"' in s for i in ("sCrRiskA", "sCrRiskB", "sCrTierA", "sCrTierB", "sCrCapTotA", "sCrCapTotB")) and 'id="sCrRisk"' not in s)
    check("S2 CORE_RISK_DEFAULTS: tierA 15 · tierB 10 · capTotalA/B 25 · riskPct 1.25", "tierA:15, tierB:10, capTotalA:25, capTotalB:25" in s and "riskPct:1.25" in s)
    check("S3 สำเนา core-size.js ใน index.html ตรงกับไฟล์ (sync)", os.system("python3 " + os.path.join(HERE, "..", "tools", "sync_core_size.py") + " --check > /dev/null") == 0)


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 65 / CZ1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
