#!/usr/bin/env python3
"""PV2c — Polish โครงพอร์ต v2: แบ่งไม้ตั้งค่าได้ต่อส่วน · ไม้เติมผ่านเพดาน Open Risk · การ์ด Asset 390 · หัว Strategy · ช่องฟอร์ม v2 · ตัดบล็อก Trend ในแผน v2 · เทส 79
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย · Satellite $45,000 (พอร์ตรวม $150,000 → เพดาน Sat $1,800 · ต่อสินค้า $900 · รวม $9,000)
ภาพ tests/screenshots/pv2c-{settings-split,asset-390,header,form-v2,pyramid-block}-{1440,390}.png
รัน: python3 run_tests_phase79.py   (วันอาทิตย์เวลาไทย: p3/p2 ล้มหลอก — ไม่เกี่ยวกับชุดนี้)"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase39 as P39
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase63 as P63
import run_tests_phase76 as P76
import run_tests_phase77 as P77
import run_tests_phase78 as P78

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
OLD_INDEX = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-PV2c.html"))
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, overflow = P54.txt, P54.overflow
launch, idea, calc = P77.launch, P77.idea, P77.calc
sat_t, put, setcfg, note, trades, save, cnt = P78.sat_t, P78.put, P78.setcfg, P78.note, P78.trades, P78.save, P78.cnt


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(900)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def edit(page, iid, f, v):
    js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, f, str(v)]); page.wait_for_timeout(200)


def make(page, sleeve, entry, sl, d=None):
    iid = idea(page, sleeve=sleeve, entry=entry, sl=sl)
    if d: js(page, "([i,d])=>satV2SetDir(i,d)", [iid, d]); page.wait_for_timeout(300)
    note(page, iid)
    return iid


def pyr_calc(page, tid, e2, sj, acct="main"):
    return js(page, """([t,a,e,s])=>{ const th = getBook(a).trades.find(x=>x.id===t); const c = satPyrCalc(th, a, {broke:true, entry2:e, slj:s});
        return {errs:c.errs, qty:c.qty, k:c.k, N:c.N, pct:c.pct, cum:c.cum, risk2:c.risk2THB, exist:c.existTHB, budget:c.budgetTHB}; }""", [tid, acct, e2, sj])


def pyr_save(page, tid, e2, sj, acct="main"):
    js(page, "([i,a])=>satPyrOpen(i,a)", [tid, acct]); page.wait_for_timeout(300)
    page.check("#pyrBreak"); page.fill("#pyrEntry", str(e2)); page.fill("#pyrSL", str(sj)); page.wait_for_timeout(200)
    ok = not js(page, "()=>document.getElementById('pyrSave').disabled")
    if ok: page.click("#pyrSave"); page.wait_for_timeout(500)
    return ok


def openall(page, acct="main"):
    """ไม้ที่เพิ่งบันทึก (plan) → open (เข้าแล้ว)"""
    js(page, "(a)=>{ getBook(a).trades.filter(t=>t.status==='plan').forEach(t=>{ t.status='open'; t.openedAt = thaiToday(); }); saveBook(a); render(); }", acct); page.wait_for_timeout(500)


def risk_usd(page, tids, acct="main"):
    return js(page, "([ids,a])=>{ const B=getBook(a); return B.trades.filter(t=>ids.includes(t.id)).reduce((s,t)=>s+posOpenRisk(t, sat7dAcctBase(a).fx).thb, 0) / sat7dAcctBase(a).fx; }", [tids, acct])


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ── 1 ตั้งค่า
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ openSettings(); document.getElementById('satV2Sec').open = true; }"); page.wait_for_timeout(400)
        v = js(page, "()=>[document.getElementById('sV2SplitMain').value, document.getElementById('sV2SplitTac').value]")
        hint = lambda i: txt(page, f'[data-v2-splith="{i}"]')
        check(f"{tag} 1 ค่าเริ่ม: แบ่งไม้ Main = 50/30/20 · Tactical = 100 · ข้างช่อง '= 3 ไม้' / '= ไม้เดียว'", v == ["50/30/20", "100"] and hint("sV2SplitMain") == "= 3 ไม้" and hint("sV2SplitTac") == "= ไม้เดียว", [v, hint("sV2SplitMain"), hint("sV2SplitTac")])
        dis = lambda: js(page, "()=>document.getElementById('setSaveBtn').disabled")
        err = lambda i: txt(page, f'[data-err-for="{i}"]') or ""
        page.fill("#sV2SplitTac", "60/40"); page.wait_for_timeout(150)
        check(f"{tag} 1 แก้ Tactical 60/40 → ไม่มี error · '= 2 ไม้' · ปุ่มบันทึกใช้ได้", not err("sV2SplitTac") and hint("sV2SplitTac") == "= 2 ไม้" and dis() is False, [err("sV2SplitTac"), hint("sV2SplitTac")])
        shot(page, f"pv2c-settings-split-{sfx}.png", "#satV2Sec")
        bad = {}
        for fid in ("sV2SplitMain", "sV2SplitTac"):
            keep = page.input_value("#" + fid)
            for val in ("60/30", "0/100", "20/20/20/20/20", "abc", "", "50/50/", "60.5/39.5"):
                page.fill("#" + fid, val); page.wait_for_timeout(80)
                bad[f"{fid}={val!r}"] = bool(err(fid)) and dis() is True
            page.fill("#" + fid, keep); page.wait_for_timeout(80)
        check(f"{tag} 1 ค่าผิด (60/30 · 0/100 · 20/20/20/20/20 · abc · ว่าง · 50/50/ · ทศนิยม) ทั้งสองช่อง → error + ปุ่มบันทึกถูกล็อก", all(bad.values()), bad)
        page.fill("#sV2SplitMain", "40 / 40 / 20"); page.wait_for_timeout(100)
        js(page, "()=>saveSettings()"); page.wait_for_timeout(400)
        s = js(page, "()=>{ const v = getBook('main').settings.satV2; return [v.splitMain, v.splitTac, satV2Split('main','main'), satV2Split('main','tactical'), satV2Split('fam','main'), satV2Split('fam','tactical')]; }")
        check(f"{tag} 1 บันทึกแล้ว: main = 40/40/20 + 60/40 (ตัดช่องว่าง) · Family ไม่เปลี่ยน (50/30/20 + 100) = ตั้งต่อบัญชี", s == ["40/40/20", "60/40", [40, 40, 20], [60, 40], [50, 30, 20], [100]], s)
        js(page, "()=>{ getBook('fam').settings.satV2 = Object.assign({}, satV2Cfg('fam'), {splitTac:'70/30', splitMain:'100'}); saveBook('fam'); }")
        s = js(page, "()=>[satV2Split('fam','main'), satV2Split('fam','tactical'), satV2Split('main','tactical')]")
        check(f"{tag} 1 Family ตั้งต่างจาก main ได้ (100 / 70-30) โดย main ไม่กระทบ", s == [[100], [70, 30], [60, 40]], s)
        js(page, "()=>{ const B = getBook('main'); delete B.settings.satV2; B.settings.satPyrSplit = [40,30,30]; saveBook('main'); openSettings(); document.getElementById('satV2Sec').open = true; }"); page.wait_for_timeout(400)
        v = js(page, "()=>[document.getElementById('sV2SplitMain').value, document.getElementById('sV2SplitTac').value, satRiskCfg('main').pyrSplit]")
        check(f"{tag} 1 ผู้ใช้เคยตั้ง pyrSplit เดิม 40/30/30 (PY2) → แบ่งไม้ Main = 40/30/30 · Tactical = 100", v == ["40/30/30", "100", [40, 30, 30]], v)
        check(f"{tag} 1 ช่องแบ่งไม้เดิม 3 ช่อง (แบ่งไม้ที่ 1/2/3) ถูกแทนด้วยช่องเดียว · ไม่ล้นแนวนอน · {label} ไม่มี console error", cnt(page, "#sSatPyr1, #sSatPyr2, #sSatPyr3") == 0 and overflow(page) <= 1 and not ce and not pe, [ce[:2], pe[:2], overflow(page)])
    finally: b.close()

    # ── 2 Tactical 60/40
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        setcfg(page, splitTac="60/40")
        iid = make(page, "tactical", 4180, 4157.5)
        c = calc(page, iid)
        card = txt(page, ".ui-plan") or ""
        check(f"{tag} 2 Tactical 60/40: ดีล 0.12 → ไม้ 1 = 0.07 (ปัดลงตาม lot step) · การ์ดบอก 'ไม้ 1 · 60% ของดีล'", c["deal"] == 0.12 and c["lot"] == 0.07 and c["split1"] == 0.6 and c["ready"] and "ไม้ 1 · 60% ของดีล" in card, [c, card[-260:]])
        save(page, iid)
        ts = trades(page)
        check(f"{tag} 2 บันทึก: ไม้ Tactical qty 0.07 · deal_lot 0.12 · tp1/tp2 คิดจาก Entry ไม้ 1 (2R/3R)", len(ts) == 1 and ts[0]["sleeve"] == "tactical" and ts[0]["qty"] == 0.07 and ts[0]["deal_lot"] == 0.12 and ts[0]["tp"] == 4225 and ts[0]["tp2"] == 4247.5, ts)
        openall(page)
        t1 = js(page, "()=>getBook('main').trades.find(t=>t.port==='satB').id")
        check(f"{tag} 2 ไม้ Tactical ที่เปิดแล้วมีปุ่ม 'เติมไม้ 2' · ป้าย 'ไม้ 1/2'", cnt(page, "[data-pyr-btn]") == 1 and "เติมไม้ 2" in (txt(page, "[data-pyr-btn]") or "") and (txt(page, "[data-pyr-tag]") or "") == "ไม้ 1/2", [cnt(page, "[data-pyr-btn]"), txt(page, "[data-pyr-btn]"), txt(page, "[data-pyr-tag]")])
        pc = pyr_calc(page, t1, 4200, 4170)
        check(f"{tag} 2 sheet เติมไม้ 2: ไม้ 2 ใช้ 40% (งบสะสม 100%) · ไม่มี error · lot > 0", not pc["errs"] and pc["k"] == 2 and pc["N"] == 2 and pc["pct"] == 40 and pc["cum"] == 100 and pc["qty"] and pc["qty"] > 0, pc)
        ok = pyr_save(page, t1, 4200, 4170)
        ts = [t for t in trades(page) if t["status"] == "open"]
        rk = risk_usd(page, [t["id"] for t in ts])
        check(f"{tag} 2 เติมไม้ 2 ได้: 2 ไม้ · sleeve = tactical ทั้งคู่ · SL ร่วม 4170 · Risk รวมสองไม้ ${rk:.1f} ≤ Risk ต่อดีล $270",
              ok and len(ts) == 2 and all(t["sleeve"] == "tactical" for t in ts) and all(t["sl"] == 4170 for t in ts) and rk <= 270 + 1e-6 and any(t.get("pyr_no") == 2 for t in ts), [ok, [(t["id"], t["qty"], t["sl"], t.get("sleeve")) for t in ts], rk])
        check(f"{tag} 2 เติมครบ 2/2 แล้ว → ไม่มีปุ่มเติมไม้อีก", cnt(page, "[data-pyr-btn]") == 0)
        # Tactical = 100 → ไม้เดียว
        put(page, [])
        setcfg(page, splitTac="100")
        iid2 = make(page, "tactical", 4180, 4157.5)
        c2 = calc(page, iid2); card2 = txt(page, ".ui-plan") or ""
        save(page, iid2); js(page, "([i])=>satV3RowMarkOpenAll(i)", [iid2]); page.wait_for_timeout(500)
        check(f"{tag} 2 Tactical 100 → ไม้ 1 = ดีลเต็ม 0.12 · ไม่มีบรรทัด 'ไม้ 1 ·' · ไม่มีปุ่มเติมไม้ · ไม่มีป้าย ไม้ n/m", c2["lot"] == 0.12 and "ไม้ 1 ·" not in card2 and cnt(page, "[data-pyr-btn]") == 0 and cnt(page, "[data-pyr-tag]") == 0, [c2["lot"], cnt(page, "[data-pyr-btn]")])
        check(f"{tag} 2 {label} ไม่มี console error", not ce and not pe, [ce[:3], pe[:3]])
    finally: b.close()

    # ── 3 Main 100
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        setcfg(page, splitMain="100")
        iid = make(page, "main", 4180, 4117)
        c = calc(page, iid); card = js(page, "()=>document.querySelector('.ui-plan .ui-row').innerText.replace(/\\s+/g,' ')")   # แถวบัญชี main
        check(f"{tag} 3 Main 100 (ไม้เดียว): ไม้ 1 = ดีลเต็ม ({c['lot']} = {c['deal']}) · ไม่มีบรรทัด 'ไม้ 1 · x%'", c["lot"] == c["deal"] == 0.10 and c["split1"] == 1 and "ไม้ 1 ·" not in card, [c["lot"], c["deal"], card[-200:]])
        setcfg(page, splitMain="50/30/20")
        c = calc(page, iid); card = js(page, "()=>document.querySelector('.ui-plan .ui-row').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 3 กลับ 50/30/20 → ไม้ 1 = 0.05 · การ์ดบอก 'ไม้ 1 · 50% ของดีล'", c["lot"] == 0.05 and c["deal"] == 0.10 and "ไม้ 1 · 50% ของดีล" in card, [c["lot"], card[-200:]])
    finally: b.close()

    # ── 4 ไม้เติมผ่านเพดาน Open Risk
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        m1 = sat_t("m1", qty=0.05, entry=4180, sl=4117)                    # Main XAUUSD เสี่ยง $315
        def scene(tac_qty=0.0, btc=0):
            ts = [m1]
            if tac_qty: ts.append(sat_t("x1", qty=tac_qty, sleeve="tactical", entry=4180, sl=4150))        # Tactical XAUUSD (ไม่ใช่ห่วงโซ่เดียวกัน)
            if btc: ts.append(sat_t("b1", sym="BTCUSD", qty=btc, entry=70000, sl=69000, sleeve="main"))   # Main BTC เสี่ยง $1,000 ต่อ 1 หน่วย
            put(page, ts)
        scene(0.10)                                                         # XAUUSD = 315 + 300 = 615
        pc = pyr_calc(page, "m1", 4200, 4117)
        check(f"{tag} 4 เติมไม้ Main ที่ไม่ทำให้เกินเพดาน (ต่อสินค้า ${615 + (pc['risk2'] or 0) / 40:.0f} < $900) → เติมได้ ไม่มี error", not pc["errs"] and pc["qty"] == 0.02, pc)
        ok = pyr_save(page, "m1", 4200, 4117)
        check(f"{tag} 4 กดบันทึกเติมไม้ได้จริง (มีไม้ Main 2 ไม้)", ok and len([t for t in trades(page) if t["sleeve"] == "main" and t["status"] == "open"]) == 2)
        scene(0.17)                                                         # XAUUSD = 315 + 510 = 825 → +166 > 900
        pc = pyr_calc(page, "m1", 4200, 4117)
        msg = " | ".join(pc["errs"])
        check(f"{tag} 4 ต่อสินค้าเกิน 0.6% → บล็อก + ตัวเลข 'Risk XAUUSD จะเป็น $… > $900 (0.6%)'", any(e.startswith("Risk XAUUSD จะเป็น $") and "> $900 (0.6%)" in e for e in pc["errs"]) and pc["qty"] is not None, msg)
        js(page, "()=>satPyrOpen('m1','main')"); page.wait_for_timeout(300)
        page.check("#pyrBreak"); page.fill("#pyrEntry", "4200"); page.fill("#pyrSL", "4117"); page.wait_for_timeout(250)
        er = txt(page, "#pyrErr") or ""
        check(f"{tag} 4 sheet: ปุ่มบันทึกปิด + เหตุผลใต้ปุ่ม (ตัวเลข $900 / 0.6%) · กดบันทึกโดยตรงก็ไม่สร้างไม้", js(page, "()=>document.getElementById('pyrSave').disabled") is True and "> $900 (0.6%)" in er and js(page, "()=>satPyrSave()") is False and len([t for t in trades(page) if t["status"] == "open"]) == 2, er)
        shot(page, f"pv2c-pyramid-block-{sfx}.png", ".pyrSh")
        js(page, "()=>satPyrClose()")
        scene(0.0, 1.4)                                                     # Satellite = 315 + 1,400 = 1,715 → +166 > 1,800
        pc = pyr_calc(page, "m1", 4200, 4117)
        check(f"{tag} 4 Satellite เกิน 1.2% → บล็อก 'Satellite Open Risk จะเป็น $… > $1,800 (1.2%)' (ต่อสินค้ายังไม่เกิน)", any(e.startswith("Satellite Open Risk จะเป็น $") and "> $1,800 (1.2%)" in e for e in pc["errs"]) and not any(e.startswith("Risk XAUUSD") for e in pc["errs"]), pc["errs"])
        # Core + Satellite
        setcfg(page, orTot=1.8)                                             # เพดานรวม $2,700
        put(page, [m1, sat_t("c1", sym="AAPL", qty=50, entry=100, sl=50, sleeve=None)])
        js(page, "()=>{ const t = getBook('main').trades.find(x=>x.id==='c1'); t.port = 'core'; t.mult = 1; saveBook('main'); render(); }")
        pc = pyr_calc(page, "m1", 4200, 4117)
        check(f"{tag} 4 Core + Satellite เกินเพดานรวม → บล็อก 'Core + Satellite จะเป็น $… > $2,700 (1.8%)' (Satellite/ต่อสินค้ายังไม่เกิน)", any(e.startswith("Core + Satellite จะเป็น $") and "> $2,700 (1.8%)" in e for e in pc["errs"]) and len([e for e in pc["errs"] if "Open Risk" in e or e.startswith("Risk ")]) == 0, pc["errs"])
        setcfg(page, orTot=6)
        # Tactical: เบรก + Max DD
        setcfg(page, splitTac="60/40", orTot=6)
        put(page, [sat_t("q1", qty=0.07, sleeve="tactical", entry=4180, sl=4157.5)] + [sat_t(f"l{i}", qty=0.01, sleeve="tactical", status="closed", entry=4180, sl=4157.5, exitPrice=4150, exitDate=f"2026-09-2{i}") for i in range(1, 6)])
        ck = js(page, "()=>{ const t = getBook('main').trades.find(x=>x.id==='q1'); const c = satPyrCheck(t, 'main'); return {ok:c.ok, reasons:c.reasons}; }")
        check(f"{tag} 4 Tactical: เบรกทำงาน (เสียติด 5 ไม้) → เติมไม้ถูกบล็อก + ข้อความเบรก Tactical", (not ck["ok"]) and any("เบรก Tactical" in r for r in ck["reasons"]) and cnt(page, "[data-pyr-btn][disabled]") >= 0, ck)
        check(f"{tag} 4 {label} ไม่มี console error", not ce and not pe, [ce[:3], pe[:3]])
    finally: b.close()

    # ── 5 การ์ด Asset ที่จอแคบ
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        put(page, [sat_t("m1", qty=0.05), sat_t("x1", qty=0.07, sleeve="tactical", entry=4180, sl=4157.5)])
        info = js(page, """()=>{
          const tiles = [...document.querySelectorAll('.ui-tile[data-key]')];
          const x = document.querySelector('.ui-tile[data-key=XAUUSD]'), o = tiles.find(t=>t.dataset.key!=='XAUUSD' && !t.querySelector('.pv2tile'));
          const grid = x.parentElement.getBoundingClientRect(), xr = x.getBoundingClientRect();
          const broken = []; const wk = document.createTreeWalker(x.querySelector('.pv2tile'), NodeFilter.SHOW_TEXT);
          while(wk.nextNode()){ const n = wk.currentNode, i = n.data.indexOf('XAUUSD'); if(i<0) continue; const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i+6); const rc = [...r.getClientRects()]; if(rc.length>1 && new Set(rc.map(q=>Math.round(q.top))).size>1) broken.push(n.data); }
          return {w:xr.width, gridW:grid.width, ow:o ? o.getBoundingClientRect().width : null, broken, wide:x.classList.contains('ui-wide'), over: xr.right - grid.right};
        }""")
        if w <= 600:
            check(f"{tag} 5 390: การ์ด XAUUSD ที่มีไม้ค้าง กินเต็มแถว (กว้าง {info['w']:.0f}/{info['gridW']:.0f}) · ชื่อสินค้าไม่ตัดกลางคำ · ไม่ล้นแนวนอน", info["w"] >= info["gridW"] - 1 and not info["broken"] and overflow(page) <= 1 and info["over"] <= 1, info)
        else:
            check(f"{tag} 5 1440 คงเดิม: การ์ด XAUUSD กว้างเท่าการ์ดอื่น ({info['w']:.0f} vs {info['ow']:.0f}) ไม่ขยาย", info["ow"] is not None and abs(info["w"] - info["ow"]) <= 1 and not info["broken"], info)
        check(f"{tag} 5 แถว Main/Tactical + แถบ Risk รวมยังอยู่ครบ ({cnt(page, '.pv2pos')} แถว)", cnt(page, ".pv2tile .pv2pos") == 2 and cnt(page, ".pv2tile [data-pv2-asset-risk]") == 1)
        shot(page, f"pv2c-asset-390-{sfx}.png", ".ui-tile[data-key=XAUUSD]")
    finally: b.close()

    # ── 6 หัว Strategy
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        t = txt(page, "[data-sat-meta]") or ""
        ht = js(page, "()=>document.querySelector('[data-sat-meta]').offsetHeight")
        b2, p2, ce2, pe2 = launch_old(pw, w, h)
        try:
            ht0 = js(p2, "()=>document.querySelector('[data-sat-meta]').offsetHeight"); t0 = txt(p2, "[data-sat-meta]") or ""
        finally: b2.close()
        check(f"{tag} 6 หัว Strategy: มี 'RPT Main 2% · Tactical 2%' · ไม่มี RPT เดิม/ไม้ Sat n/m · ส่วนอื่น (ถัง Sat · DD · heat · ไม้ใหม่) ยังอยู่", "RPT Main 2% · Tactical 2%" in t and "ไม้ Sat" not in t and not __import__("re").search(r"RPT \d", t) and all(k in t for k in ("ถัง Sat", "DD", "heat", "ไม้ใหม่")), t)
        check(f"{tag} 6 ความสูงหัวไม่เกินก่อนแก้ ({ht} ≤ {ht0})", ht <= ht0, [ht, ht0, t0])
        shot(page, f"pv2c-header-{sfx}.png", "[data-sat-meta]")
    finally: b.close()

    # ── 7 ฟอร์ม v2
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        iid = idea(page, sleeve="main", entry=4180, sl=4117)
        info = js(page, """()=>{
          const f = document.querySelector('[data-v2-card]'), pr = f.getBoundingClientRect();
          const q = s => document.querySelector('[data-v2-card] '+s);
          const els = {tf:q('[data-v2-tf]'), note:q('[data-v2-note]'), entry:q('[data-v2-entry]'), sl:q('[data-v2-sl]'), tp:q('input[data-v2-tp]')};
          const out = {};
          for(const [k, e] of Object.entries(els)){ const r = e.getBoundingClientRect(), cs = getComputedStyle(e); out[k] = {h:Math.round(r.height), w:Math.round(r.width), top:Math.round(r.top), right:Math.round(r.right), radius:cs.borderTopLeftRadius, border:cs.borderTopWidth, fs:cs.fontSize}; }
          out.cardRight = Math.round(pr.right);
          return out;
        }""")
        five = ("tf", "note", "entry", "sl", "tp")
        check(f"{tag} 7 ฟอร์ม v2: ช่องทั้ง 5 (TF · เสริม · Entry · SL · TP) สูง ≥ 36px · มุมโค้ง · มีขอบ · ฟอนต์ ≥ 16px", all(info[k]["h"] >= 36 and info[k]["radius"] != "0px" and info[k]["border"] != "0px" and float(info[k]["fs"][:-2]) >= 16 for k in five), info)
        check(f"{tag} 7 Entry/SL วางคู่กัน (บรรทัดเดียวกัน) · ไม่ล้นการ์ด · ไม่ล้นแนวนอน", abs(info["entry"]["top"] - info["sl"]["top"]) <= 2 and all(info[k]["right"] <= info["cardRight"] + 1 for k in five) and overflow(page) <= 1, [info["entry"], info["sl"], info["cardRight"], overflow(page)])
        hint_below = js(page, "()=>{ const h = document.querySelector('[data-v2-card] [data-v2-entry]').closest('.ui-f2c-r'); const hs = h.querySelector('.ui-hint'); const sl = h.querySelector('[data-v2-sl]'); return hs ? hs.getBoundingClientRect().left >= sl.getBoundingClientRect().right - 1 || hs.getBoundingClientRect().top >= sl.getBoundingClientRect().bottom - 1 : null; }")
        check(f"{tag} 7 ป้าย '$ระยะ' อยู่ท้ายแถว (ถัดจาก SL)", hint_below is True, hint_below)
        shot(page, f"pv2c-form-v2-{sfx}.png", "[data-v2-card]")
        check(f"{tag} 7 {label} ไม่มี console error", not ce and not pe, [ce[:3], pe[:3]])
    finally: b.close()

    # ── 8 บล็อก Trend ในการ์ดแผน v2
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        iid = make(page, "main", 4180, 4117)
        js(page, "()=>{ satV3Render({force:true}); }"); page.wait_for_timeout(300)   # PF1 — satV3TrendPick ถอดแล้ว
        card = txt(page, ".ui-plan") or ""
        check(f"{tag} 8 การ์ดแผน v2: ไม่มีปุ่ม ขึ้น/ผสม/ลง · ไม่มี [เปลี่ยน] · ไม่มีแถว Trend · ไม่มีคำเตือน Trend Shift",
              cnt(page, ".ui-plan [data-trend]") == 0 and cnt(page, ".ui-plan .ui-f2c-chg") == 0 and cnt(page, ".ui-plan [data-f2c-row=trend]") == 0 and cnt(page, ".ui-plan [data-trend-shift]") == 0 and cnt(page, ".ui-plan [data-trend-clear]") == 0,
              [cnt(page, ".ui-plan [data-trend]"), cnt(page, ".ui-plan .ui-f2c-chg")])
        check(f"{tag} 8 ยังมีบรรทัด 'Macro: …' + 'ขนาดไม้: เต็ม/ลด x%' (ตัวคูณ Macro ยังทำงาน)", cnt(page, ".ui-plan [data-f2c-row=macro]") == 1 and cnt(page, ".ui-plan [data-f2c-row=size]") == 1 and "Macro:" in card and "ขนาดไม้:" in card, card[-260:])
    finally: b.close()
    import run_tests_phase11 as P11
    b, page, ce, pe = launch(pw, w, h, bias="Short")
    try:
        P11.seed_pb(page, [P11.pbver(1, "2026-09-27T10:00:00.000Z", x="up")])
        P11.wk(page, "XAUUSD", "Short", "down"); page.wait_for_timeout(300)
        iid2 = idea(page, sleeve="main", entry=4180, sl=4240)
        c = calc(page, iid2)
        check(f"{tag} 8 สวน Macro: ขนาดไม้ลด x{c['factor']} (ตัวคูณยังทำงาน) + ข้อความบังคับเขียนเหตุผลยังอยู่ ('เขียนเหตุผลที่เข้าสวน/นอก Macro') · ไม่มีแถว Trend", c["factor"] < 1 and cnt(page, "[data-macro-note]") >= 1 and cnt(page, "[data-note-warn]") >= 1 and cnt(page, "[data-f2c-row=trend]") == 0 and any("เขียนเหตุผล" in x for x in c["warns"]), [c["factor"], c["warns"], cnt(page, "[data-macro-note]"), cnt(page, "[data-note-warn]")])
    finally: b.close()
    b, page, ce, pe = P63.sat_page(pw, w, h)
    try:
        P63.fresh(page, P63.bp_idea([P63.cond()]))
        P63.full_ready(page)
        check(f"{tag} 8 PF3 แผนเดิม (kind bp): ไม่มีแถว Trend (Strategy จ.) · ไม่มีปุ่ม [เปลี่ยน]", "Strategy จ." not in (js(page, "()=>[...document.querySelectorAll('.ui-plan')].map(e=>e.innerText).join(' ')") or "") and js(page, "()=>[...document.querySelectorAll('.ui-plan button')].filter(b=>b.innerText.trim()==='เปลี่ยน').length") == 0)
        check(f"{tag} 8 PF3 แผนเดิม: ไม่มีตัวเปลี่ยน Trend ต่อแผน — ไม่มีปุ่ม ขึ้น/ผสม/ลง ([data-trend] = 0)", js(page, "()=>document.querySelectorAll('.ui-plan [data-trend]').length") == 0)
    finally: b.close()

    # ── 9 ภาพไม่โหลดซ้ำ (RR2) + console
    kw = {"mut": P77.fixture(), "pick": ["XAUUSD", "BTCUSD"]}
    import run_tests_phase59 as P59
    b, c_, page, ce, pe, dl, env = P59.launch(pw, w, h, **kw)
    try:
        js(page, "(c)=>{ satwWrite('XAUUSD', {bias:'Long', support:[3920], resistance:[4080], invalidation:3840, chart:c}); satwWrite('BTCUSD', {bias:'Long'}); }", P76.CHART); page.wait_for_timeout(400)
        P37.go_sat(page); page.wait_for_timeout(300)
        js(page, "()=>satV2NewPlan('XAUUSD','main')"); page.wait_for_timeout(600)
        ok0 = js(page, P76.WATCH)
        for sel in ("[data-sleeve=tactical]", "[data-dir=Short]", "[data-dir=Long]", "[data-v2-setup]", "[data-sleeve=main]"):
            page.locator(sel).first.click(); page.wait_for_timeout(450)
        page.locator("[data-v2-entry]").first.fill("4180"); page.locator("[data-v2-entry]").first.press("Tab"); page.wait_for_timeout(450)
        st = js(page, P76.STATE)
        check(f"{tag} 9 กดปุ่มส่วน/ทิศ/Setup + กรอก Entry ในการ์ดแผน → ภาพกราฟไม่โหลดซ้ำ (RR2)", ok0 and st["loads"] == 0 and st["same"] and st["complete"], [ok0, st])
        check(f"{tag} 9 {label} ไม่มี console error", not ce and not pe, [ce[:3], pe[:3]])
    finally: b.close()


def launch_old(pw, w, h):
    """ไฟล์ก่อนแก้ (index.backup-pre-PV2c.html) ในสถานการณ์เดียวกัน — ไว้เทียบความสูงหัว"""
    old = P39.INDEX
    P39.INDEX = OLD_INDEX
    try: return launch(pw, w, h, bias="Long")
    finally: P39.INDEX = old


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
