#!/usr/bin/env python3
"""SR1 — ค่าตั้งความเสี่ยง Sat ต่อบัญชี (เสี่ยงต่อไม้ 1.5/2% · heat · ไม้ใหม่/สัปดาห์) + ปิด MR + ห้ามเทรดสวน Bias สัปดาห์ · เทส 34
mock Firestore · Chromium 1440 + 430 · seed 2 บัญชีเปิด Sat (main: ทุน Sat มีค่า · XM XAUUSD · fam: IC XAUUSD) · แผน Sat XAUUSD Entry/SL ตายตัว
ภาพเก็บที่ tests/screenshots/sr1-*.png
รัน: python3 run_tests_phase34.py"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase27 as p27
from run_tests_phase11 import wk, reset_ideas, fresh
from run_tests_phase27 import js, mk, setup_week, push_trade, set_idea

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []

ENTRY, SL, DIST = 2650, 2680, 30      # แผน Short ตายตัว (Bias Short · dist 30)


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:600] + "...(truncated)") if (detail and len(detail) > 600) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(300)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def txt(page, sel):
    return page.evaluate("(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)


def set_risk(page, acct, obj):
    js(page, "([a,o])=>{ const s=getBook(a).settings; if(o===null) delete s.satRisk; else s.satRisk=o; }", [acct, obj])


def set_heat(page, acct, v):
    js(page, "([a,v])=>{ const s=getBook(a).settings; s.limits=s.limits||{}; s.limits.port=Object.assign({core:20}, s.limits.port||{}, {satB:v}); }", [acct, v])


def calc(page, iid, acct="main"):
    return js(page, """([i,a])=>{ const c=satV3PlanAcctCalc(sat7dIdea(i), a);
        return {ready:c.ready, warns:c.warns, lot:c.lot, rpt:c.base.rpt, heatMax:c.base.heatMax, newMax:c.base.newMax, riskCur:c.riskCur, factor:c.factor, cfg:c.chosen?c.chosen.cfg:null, offBias:c.offBias}; }""", [iid, acct])


def exp_lot(page, c, mult=1):
    return js(page, "([cfg,r,d,f])=>Calc.satLot({riskAmount:r*f, dist:d, contract:cfg.contract, lotStep:cfg.lotStep, minLot:cfg.minLot}).lot", [c["cfg"], c["riskCur"], DIST, c["factor"]])


def lot_for(page, pct, acct="main", f=1):
    """lot ที่คาดหวังจาก Calc.satLot ตรง ๆ — riskAmount = ทุน Sat (USD) × pct%"""
    return js(page, """([a,p,d,f])=>{ const b=sat7dAcctBase(a); const opts=sat7dBrokerOpts(b.B,'XAUUSD'); const cfg=opts[0].cfg;
        const risk = (b.cap*p/100)/b.fx; return Calc.satLot({riskAmount:risk*f, dist:d, contract:cfg.contract, lotStep:cfg.lotStep, minLot:cfg.minLot}).lot; }""", [acct, pct, DIST, f])


def clean(page):
    reset_ideas(page)
    js(page, "()=>{ ['main','fam'].forEach(a=>{ const B=getBook(a); B.trades=[]; delete B.settings.satRisk; if(B.settings.limits&&B.settings.limits.port) B.settings.limits.port.satB=6; }); saveBook('main'); saveBook('fam'); }")
    setup_week(page, "Short")


def plan(page, iid="iS", bias="Short", entry=ENTRY, sl=SL, tp=2380):
    mk(page, iid, bias=bias, entry=entry, sl=sl, tp=None, active="c1", extra_conds=[
        {"id": "c1", "text": "Break & Pullback @ 2400", "tp_from": tp, "tp_to": tp - 30 if bias == "Short" else tp + 30, "inval": None, "active": True, "saved": True}])
    set_idea(page, iid, {"tp": tp})


def strip(page, acct="main"):
    return txt(page, f'.sumMr[data-acct="{acct}"]')


def overflow(page, sels):
    return page.evaluate("""(sels)=>{ const W = window.innerWidth, bad = [];
      sels.forEach(s=>{ const e = document.querySelector(s); if(!e){ bad.push(s+':missing'); return; }
        const r = e.getBoundingClientRect(); if(r.right > W + 1 || r.left < -1 || e.scrollWidth > e.clientWidth + 1) bad.push(s+':'+Math.round(r.left)+'-'+Math.round(r.right)+'/'+e.scrollWidth+'>'+e.clientWidth); });
      if(document.documentElement.scrollWidth > W + 1) bad.push('page:'+document.documentElement.scrollWidth+'>'+W); return bad; }""", sels)


def open_set(page):
    js(page, "()=>{ openSettings(); }"); page.wait_for_timeout(250)
    js(page, "()=>{ document.querySelectorAll('#satRiskSec').forEach(d=>d.open=true); }")


def err(page, id_):
    return txt(page, f'[data-err-for="{id_}"]') or ""


def save_disabled(page):
    return js(page, "()=>document.getElementById('setSaveBtn').disabled")


def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    page.evaluate("()=>{ ['main','fam'].forEach(a=>{ const B = getBook(a); if(B){ if(!B.settings) B.settings = {}; B.settings.satPyrSplit = [100,0,0]; saveBook(a); } }); }")   # PY2: สัดส่วนแบ่งไม้ 100/0/0 = ไม้ 1 เข้าเต็ม RPT เหมือนก่อน PY2 (เคสเดิมไม่ได้ทดสอบการแบ่งไม้)
    try:
        page.evaluate("() => switchTab('flow')")
        p5.goto_sat(page); clean(page)
        plan(page, "iS")
        # ── 1 ค่าเริ่มต้น
        cfgd = js(page, "()=>[satRiskCfg('main'), satRiskCfg('fam')]")
        check(f"{tag} 1 ไม่มี satRisk → ค่าเริ่มต้น rpt 1.5 · rptHi 2 · heat 6 · ใหม่ 2 (ทั้ง 2 บัญชี)",
              all(c == {"rpt": 1.5, "rptHi": 2, "heatMax": 6, "newMax": 2, "macroNeutral": 1, "macroAgainst": 0.6, "pyrSplit": [100, 0, 0], "ddReduce": 12.5, "ddPause": 20, "ddPauseWeeks": 1, "ddRecoverR": 2} for c in cfgd), json.dumps(cfgd))
        c = calc(page, "iS")
        check(f"{tag} 1 lot ค่าเริ่มต้น (RPT 1.5%) = Calc.satLot ตรง ๆ · rpt=1.5", c["rpt"] == 1.5 and c["lot"] == exp_lot(page, c) == lot_for(page, 1.5), json.dumps(c))
        js(page, "()=>render()"); p5.goto_sat(page)
        s = strip(page) or ""
        check(f"{tag} 1 แถบบัญชี Sat: RPT 1.5% · heat ลงท้าย /6% · ไม้ใหม่ /2", f"RPT Main {js(page, '()=>satV2Cfg(\'main\').rptMain')}% · Tactical {js(page, '()=>satV2Cfg(\'main\').rptTac')}%" in s and "/6%" in s and "0/2" in s, s)
        shot(page, f"sr1-sat-strip-{label}.png", "[data-sat-meta]")
        check(f"{tag} 1 STRIP_FIELDS.sat สร้างจากค่าตั้ง (heat /6% · ใหม่ /2)", js(page, "()=>[STRIP_FIELDS.sat[0].suffix, STRIP_FIELDS.sat[1].suffix]") == ["/6%", "/2"])
        # เดิม 1.25 → lot เท่ากับของก่อนแก้ (0.13 ที่ dist 30 · คำนวณตรง)
        set_risk(page, "main", {"rpt": 1.25, "rptHi": 1.5}); c = calc(page, "iS")
        check(f"{tag} 1 seed satRisk {{rpt:1.25, rptHi:1.5}} → lot เท่าค่าเดิมก่อนแก้ (0.13) · = Calc.satLot ตรง", c["rpt"] == 1.25 and c["lot"] == 0.13 == lot_for(page, 1.25), json.dumps(c))
        # ── 2 ต่อบัญชี
        set_risk(page, "main", {"rpt": 1.0, "rptHi": 2, "newMax": 2}); c = calc(page, "iS"); cf = calc(page, "iS", "fam")
        check(f"{tag} 2 main rpt 1.0 → lot ลดตามสัดส่วน = Calc.satLot ตรง", c["rpt"] == 1.0 and c["lot"] == lot_for(page, 1.0) and c["lot"] < lot_for(page, 1.5), json.dumps(c))
        check(f"{tag} 2 fam ยังเป็นค่าเริ่มต้น 1.5 (แยกต่อบัญชี) · lot = Calc.satLot ตรง", cf["rpt"] == 1.5 and cf["lot"] == lot_for(page, 1.5, "fam"), json.dumps(cf))
        js(page, "()=>render()"); p5.goto_sat(page)
        check(f"{tag} 2 แถบ main RPT 1% · fam RPT 1.5%", "RPT Main 1% ·" in (strip(page, "main") or "") and f"RPT Main {js(page, '()=>satV2Cfg(\'fam\').rptMain')}% ·" in (strip(page, "fam") or "") and js(page, "()=>satV2Cfg('main').rptMain") == 1, f"{strip(page,'main')} || {strip(page,'fam')}")   # PV2c: แถบอ่านค่า RPT Main จากตั้งค่า Sat v2 ของแต่ละบัญชี
        # ── 3 พิสูจน์ผ่าน
        set_risk(page, "main", None)
        js(page, """()=>{ const B=getBook('main'); B.sat_since='2026-01-01'; for(let i=0;i<50;i++){ B.trades.push(makeTradeObject({id:'pv'+i, date:'2026-02-01', openedAt:'2026-02-01', exitDate:'2026-02-02', sym:'XAUUSD', port:'satB', bias:'Long', entry:100, sl:90, qty:1, mult:1, cur:'USD', status:'closed', exitPrice:110})); } saveBook('main'); }""")
        hi = js(page, "()=>[sat7dCounter(getBook('main')).hi, sat7dCounter(getBook('fam')).hi]")
        c = calc(page, "iS"); cf = calc(page, "iS", "fam")
        check(f"{tag} 3 ตัวนับพิสูจน์ผ่าน (main) → ใช้ rptHi 2% ค่าเริ่มต้น · lot = Calc.satLot ตรง · fam ยัง 1.5", hi == [True, False] and c["rpt"] == 2 and c["lot"] == lot_for(page, 2) and cf["rpt"] == 1.5, json.dumps([hi, c, cf]))
        set_risk(page, "main", {"rpt": 1.5, "rptHi": 1.8}); c = calc(page, "iS")
        check(f"{tag} 3 ตั้ง rptHi 1.8 → main ผ่านพิสูจน์ใช้ 1.8", c["rpt"] == 1.8 and c["lot"] == lot_for(page, 1.8), json.dumps(c))
        js(page, "()=>{ const B=getBook('main'); B.trades=[]; delete B.settings.satRisk; saveBook('main'); }")
        # ── 4 heat = limits.port.satB
        set_heat(page, "main", 4)
        push_trade(page, id="h1", date=js(page, "()=>thaiToday()"), bias="Short", entry=ENTRY, sl=SL, tp=2600, qty=0.28, status="open")
        c = calc(page, "iS")
        js(page, "()=>render()"); p5.goto_sat(page); s = strip(page) or ""
        check(f"{tag} 4 limits.port.satB=4 → heatMax 4 · แถบ heat ลงท้าย /4% (ไม่ใช่ /6%)", c["heatMax"] == 4 and "/4%" in s and "/6%" not in s, f"{c['heatMax']} {s}")
        check(f"{tag} 4 ไม้ที่ทำให้ heat > 4% → ไม่ ready (heat เกิน)", c["ready"] is False and "heat เกิน" in c["warns"], json.dumps(c["warns"], ensure_ascii=False))
        set_heat(page, "main", 6); c = calc(page, "iS")
        check(f"{tag} 4 คืน heat 6 → ready (6% เดิมกลับมาใช้เมื่อตั้งเอง)", c["heatMax"] == 6 and c["ready"] is True, json.dumps(c["warns"], ensure_ascii=False))
        set_heat(page, "main", 4)
        check(f"{tag} 4 ไม่ใช้ SAT7D_HEAT_MAX ตายตัวอีก (บัญชี fam ที่ยัง 6 ไม่เปลี่ยน)", calc(page, "iS", "fam")["heatMax"] == 6)
        set_heat(page, "main", 6)
        # ── 5 newMax
        js(page, "()=>{ const B=getBook('main'); B.trades=[]; saveBook('main'); }")
        set_risk(page, "main", {"rpt": 1.5, "rptHi": 2, "newMax": 3})
        today = js(page, "()=>thaiToday()")
        for i in range(2): push_trade(page, id=f"n{i}", date=today, bias="Short", entry=ENTRY, sl=SL, tp=2600, qty=0.01, status="open")
        c = calc(page, "iS")
        check(f"{tag} 5 newMax 3 · มีไม้ใหม่ 2 → ไม้ที่ 3 ยัง ready", c["newMax"] == 3 and c["ready"] is True, json.dumps(c["warns"], ensure_ascii=False))
        push_trade(page, id="n2", date=today, bias="Short", entry=ENTRY, sl=SL, tp=2600, qty=0.01, status="open")
        c = calc(page, "iS"); js(page, "()=>render()"); p5.goto_sat(page)
        check(f"{tag} 5 มีไม้ใหม่ 3 → ไม้ที่ 4 = โควตาเต็ม · แถบ 3/3", c["ready"] is False and "โควตาเต็ม" in c["warns"] and "3/3" in (strip(page) or ""), f"{c['warns']} {strip(page)}")
        js(page, "()=>{ const B=getBook('main'); B.trades=[]; saveBook('main'); }")
        # ── 6 หน้าตั้งค่า
        set_risk(page, "main", None); open_set(page)
        vals = page.evaluate("()=>['sSatRpt','sSatRptHi','sSatNewMax'].map(i=>document.getElementById(i).value)")
        check(f"{tag} 6 ส่วน 'ความเสี่ยง SAT — % ของถัง Sat' มี 3 ช่อง · ค่าเริ่มต้น 1.5 / 2 / 2", vals == ["1.5", "2", "2"] and "per-trade risk" in (txt(page, "#satRiskSec summary") or "").lower(), json.dumps(vals))
        check(f"{tag} 6 หน่วย: '% ของถัง Sat' · ป้ายผ่านเกณฑ์พิสูจน์ 50 ไม้ · avg R ≥ 0.25", "% of Sat bucket" in (txt(page, "#satRiskSec .f label") or "") and "50 ไม้ · avg R ≥ 0.25" in (txt(page, "#satRiskSec") or ""), txt(page, "#satRiskSec") or "")
        check(f"{tag} 6 บรรทัดเล็ก heat: 'ตั้งที่ช่อง Sat — % ของถัง Sat (ตอนนี้ 6%)' · ไม่มีช่อง heat ซ้ำ", "ตอนนี้ 6%" in (txt(page, "#satHeatHint") or "") and js(page, "()=>document.querySelectorAll('#satRiskSec input').length") == 8, txt(page, "#satHeatHint") or "")   # PV2c: ช่องแบ่งไม้ 3 ช่องย้ายไป Sat v2 (12 → 9)
        check(f"{tag} 6 ไม่มีหมายเหตุ 'ค่าคงที่ 6%' เดิมที่ช่อง heat", not js(page, "()=>{ const n=document.getElementById('satHeatNote'); return n && n.style.display!=='none'; }"))
        shot_el = lambda n: (page.evaluate("()=>document.getElementById('satRiskSec').scrollIntoView({block:'center'})"), shot(page, n))
        shot_el(f"sr1-settings-sat-{label}.png")
        page.fill("#sSatRptHi", "1"); page.wait_for_timeout(80)
        check(f"{tag} 6 rptHi < rpt → ข้อความแดง + ปุ่มบันทึกปิด", err(page, "sSatRptHi") != "" and save_disabled(page) is True, err(page, "sSatRptHi"))
        page.fill("#sSatRptHi", "2")
        bad = {}
        for fld, vals_ in {"sSatNewMax": ["0", "2.5", "11"], "sSatRpt": ["0", "6"]}.items():
            for v in vals_:
                page.fill("#" + fld, v); page.wait_for_timeout(60)
                bad[f"{fld}={v}"] = (err(page, fld) != "" and save_disabled(page) is True)
            page.fill("#" + fld, "2" if fld == "sSatNewMax" else "1.5")
        check(f"{tag} 6 newMax 0 / 2.5 / 11 · rpt 0 / 6 → แดงทุกค่า + ปุ่มบันทึกปิด", all(bad.values()), json.dumps(bad))
        page.wait_for_timeout(60)
        check(f"{tag} 6 แก้กลับเป็นค่าถูก → ข้อความแดงหาย · ปุ่มบันทึกเปิด", all(err(page, i) == "" for i in ("sSatRpt", "sSatRptHi", "sSatNewMax")) and save_disabled(page) is False)
        # ── 7 บันทึก
        page.fill("#sSatRpt", "1"); page.fill("#sSatRptHi", "1.8"); page.fill("#sSatNewMax", "3"); page.wait_for_timeout(60)
        js(page, "()=>saveSettings()"); page.wait_for_timeout(300)
        saved = js(page, "()=>[getBook('main').settings.satRisk, getBook('fam').settings.satRisk || null]")
        check(f"{tag} 7 บันทึก → settings.satRisk ของบัญชีที่เปิด = {{rpt:1, rptHi:1.8, newMax:3}} · fam ไม่เปลี่ยน", saved[0] == {"rpt": 1, "rptHi": 1.8, "newMax": 3, "macroNeutral": 1, "macroAgainst": 0.6, "ddReduce": 12.5, "ddPause": 20, "ddPauseWeeks": 1, "ddRecoverR": 2} and saved[1] is None, json.dumps(saved))
        js(page, "(a)=>acctSwitch(a)", "fam"); page.wait_for_timeout(400)
        open_set(page); v_fam = page.evaluate("()=>['sSatRpt','sSatRptHi','sSatNewMax'].map(i=>document.getElementById(i).value)")
        check(f"{tag} 7 สลับไป fam → ช่องแสดงค่าเริ่มต้น 1.5 / 2 / 2", v_fam == ["1.5", "2", "2"], json.dumps(v_fam))
        page.fill("#sSatRpt", "1.2"); js(page, "()=>saveSettings()"); page.wait_for_timeout(300)
        js(page, "(a)=>acctSwitch(a)", "main"); page.wait_for_timeout(400)
        both = js(page, "()=>[getBook('main').settings.satRisk, getBook('fam').settings.satRisk]")
        check(f"{tag} 7 สลับกลับ main → ค่าของ main ไม่เปลี่ยน · fam เก็บ rpt 1.2 แยกกัน", both[0]["rpt"] == 1 and both[0]["newMax"] == 3 and both[1]["rpt"] == 1.2, json.dumps(both))
        open_set(page); v_main = page.evaluate("()=>['sSatRpt','sSatRptHi','sSatNewMax'].map(i=>document.getElementById(i).value)")
        check(f"{tag} 7 เปิดค่าตั้ง main → เห็น 1 / 1.8 / 3", v_main == ["1", "1.8", "3"], json.dumps(v_main))
        js(page, "()=>document.getElementById('setOverlay').classList.remove('show')")
        # ── 8 ไม้ที่บันทึกแล้วไม่คำนวณใหม่
        clean(page); plan(page, "iK")
        js(page, "()=>satV3SaveSlot('iK','main')"); page.wait_for_timeout(350)
        t = js(page, "()=>{ const s=(sat7dIdea('iK').accts||{}).main||{}; const t=getBook('main').trades.find(x=>x.id===s.trade_id); return t?{id:t.id,qty:t.qty,sl:t.sl,entry:t.entry}:null; }")
        set_risk(page, "main", {"rpt": 1.0, "rptHi": 1.5, "newMax": 2}); js(page, "()=>render()"); page.wait_for_timeout(200)
        t2 = js(page, "(id)=>{ const t=getBook('main').trades.find(x=>x.id===id); return t?{id:t.id,qty:t.qty,sl:t.sl,entry:t.entry}:null; }", t["id"] if t else "")
        check(f"{tag} 8 ไม้ Sat ที่บันทึกก่อนแก้ค่า (lot {t and t['qty']}) → qty/entry/SL เดิมไม่เปลี่ยน", t and t == t2 and t["qty"] == lot_for(page, 1.5) or (t and t == t2), json.dumps([t, t2]))
        # ── 9 บัญชีที่ไม่เปิด Sat
        js(page, "()=>{ window.__pp = acctList.find(a=>a.id==='main').ports.slice(); acctList.find(a=>a.id==='main').ports = ['core','satA']; }")
        open_set(page); hidden = js(page, "()=>getComputedStyle(document.getElementById('satRiskSec')).display")
        check(f"{tag} 9 บัญชีไม่เปิด port Sat → ไม่มีส่วน 'ความเสี่ยง SAT'", hidden == "none", hidden)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); acctList.find(a=>a.id==='main').ports = window.__pp; }")
        js(page, "()=>{ ['main','fam'].forEach(a=>delete getBook(a).settings.satRisk); }")
        # ── 10 MR ปิด
        clean(page); p5.goto_sat(page)
        mk(page, "iM", bias="Short", entry=None, sl=None, tp=None, active="none")   # แผนบันทึกแล้ว ยังไม่ Activate ข้อไหน = หน้าที่มีปุ่มเพิ่มเงื่อนไข (เงื่อนไข MR เดิม c2 ติดมากับ fixture)
        js(page, "()=>{ satV3Open.add('iM'); satV3Render(); }"); page.wait_for_timeout(300)
        n_btn = js(page, "()=>document.querySelectorAll('[data-mr-add]').length")
        n0 = js(page, "()=>sat7dIdea('iM').conditions.length")
        js(page, "()=>satV3MrAdd('iM')"); page.wait_for_timeout(300)
        n1 = js(page, "()=>sat7dIdea('iM').conditions.length")
        check(f"{tag} 10 MR ปิด: SAT_MR_ENABLED false · แผน Sat ไม่มีปุ่ม '＋ MR สวน Bias' · satV3MrAdd ตรง ๆ ไม่เพิ่มเงื่อนไข",
              js(page, "()=>[SAT_MR_ENABLED, satMrOn()]") == [False, False] and n_btn == 0 and n0 == n1, f"{n_btn} {n0} {n1}")
        js(page, "()=>satV3Render()")
        plan_txt = txt(page, '.ui-plan[data-id="iM"]') or ""
        # เงื่อนไข MR เดิม (c2) + ไม้ MR เดิม → ยังแสดง
        check(f"{tag} 10 เงื่อนไข MR เดิมในแผน (ข้อมูลเก่า) ยังแสดง ไม่ถูกซ่อน", js(page, "()=>document.querySelectorAll('.ui-plan[data-id=\"iM\"] [data-cond-kind=\"mr\"], .ui-plan[data-id=\"iM\"] [data-mr-tag]').length") > 0 or "MR" in plan_txt, plan_txt[:300])
        shot(page, f"sr1-plan-no-mr-{label}.png", '.ui-plan[data-id="iM"]')
        push_trade(page, id="mr1", date=js(page, "()=>thaiToday()"), bias="Long", entry=2410, sl=2390, tp=2450, qty=0.01, status="open", mr=True, mr_level=2400)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(300)
        pv = page.evaluate("(s)=>{ const o={}; document.querySelectorAll(s).forEach(r=>o[r.dataset.pos]=r.innerText.replace(/\\s+/g,' ')); return o; }", "tr[data-pos]" if w > 900 else ".tcard[data-pos]")
        check(f"{tag} 10 ไม้ MR เดิมที่เปิดอยู่ → Positions ยังมีป้าย 'MR · สวน Bias'", "MR · สวน Bias" in pv.get("mr1", ""), pv.get("mr1", ""))
        js(page, "()=>{ const t=getBook('main').trades.find(x=>x.id==='mr1'); t.status='closed'; t.exitPrice=2440; t.exitDate=thaiToday(); saveBook('main'); render(); switchTab('journal'); setJFilter('all'); }"); page.wait_for_timeout(350)
        jt = page.evaluate("()=>{ const e=document.querySelector('#jContent_closed'); return e ? e.innerText.replace(/\\s+/g,' ') : ''; }")
        check(f"{tag} 10 Journal ยังแสดงป้าย MR ของไม้ MR เดิม", "MR · สวน Bias" in jt, jt[:200])
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }")
        js(page, "()=>{ window.SAT_MR_ENABLED = true; satV3Render(); }"); page.wait_for_timeout(300)
        n_btn2 = js(page, "()=>document.querySelectorAll('[data-mr-add]').length")
        js(page, "()=>satV3MrAdd('iM')"); page.wait_for_timeout(300)
        n2 = js(page, "()=>sat7dIdea('iM').conditions.length")
        check(f"{tag} 10 window.SAT_MR_ENABLED = true → ปุ่ม MR กลับมา · satV3MrAdd เพิ่มเงื่อนไข", n_btn2 >= 1 and n2 == n1 + 1, f"{n_btn2} {n1} {n2}")
        js(page, "()=>{ window.SAT_MR_ENABLED = false; }")
        # ── 11 สวน Bias
        clean(page); p5.goto_sat(page)
        setup_week(page, "Long", support=(2400,), resistance=(2520,))
        plan(page, "iL", bias="Long", entry=2410, sl=2390, tp=2450)
        push_trade(page, id="ob0", date=js(page, "()=>thaiToday()"), bias="Long", entry=2410, sl=2390, tp=2450, qty=0.01, status="open")
        js(page, "()=>{ satV3Open.add('iL'); satV3Render(); }"); page.wait_for_timeout(300)
        cm, cf = calc(page, "iL"), calc(page, "iL", "fam")
        check(f"{tag} 11 แผน Long + Bias สัปดาห์ Long → ready ทั้ง 2 บัญชี · ไม่ถูกบล็อก", cm["ready"] and cf["ready"] and not cm["offBias"], json.dumps([cm["warns"], cf["warns"]], ensure_ascii=False))
        wk(page, "XAUUSD", "Short", "down", inval=2600); js(page, "()=>satV3Render()"); page.wait_for_timeout(300)
        cm, cf = calc(page, "iL"), calc(page, "iL", "fam")
        msg = "สวน Bias สัปดาห์ (ตอนนี้ Short) — ยกเลิกแผนนี้ หรือรอ Bias กลับ"
        check(f"{tag} 11 PF1 — Strategy bias เก่าสลับเป็น Short (แผน Long): ยัง ready ทั้ง 2 บัญชี · ไม่มีเหตุผล สวน Bias · ไม่ลดไม้", cm["ready"] and cf["ready"] and not cm["offBias"] and not any("สวน Bias" in x for x in cm["warns"] + cf["warns"]), json.dumps([cm["warns"], cf["warns"]], ensure_ascii=False))
        card = txt(page, '.ui-plan[data-id="iL"]') or ""
        check(f"{tag} 11 PF1 — การ์ดแผนไม่มีข้อความ สวน Bias สัปดาห์", "สวน Bias" not in card, card[:400])
        nt0 = js(page, "()=>[getBook('main').trades.length, getBook('fam').trades.length]")
        js(page, "()=>{ satV3SaveOffplanAccount('iL','main'); satV3SaveOffplanAccount('iL','fam'); satV3SaveSlot('iL','main'); satV3SaveSlot('iL','fam'); satV3SaveSlot('iL','main', true); satV3SaveReadyAccounts('iL'); }"); page.wait_for_timeout(350)
        nt1 = js(page, "()=>[getBook('main').trades.length, getBook('fam').trades.length]")
        check(f"{tag} 11 PF3 เรียก satV3SaveOffplanAccount / satV3SaveSlot / SaveReady ตรง ๆ → ไม่ถูกบล็อกด้วย สวน Bias แล้ว: ทั้ง 2 บัญชีสร้างไม้ได้ (main {nt0[0]}→{nt1[0]} · fam {nt0[1]}→{nt1[1]})", nt1[0] > nt0[0] and nt1[1] > nt0[1], json.dumps([nt0, nt1]))
        # ไม้ที่เปิดอยู่ก่อนสลับ → ป้าย + ไม่ปิด
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(300)
        pv = page.evaluate("(s)=>{ const o={}; document.querySelectorAll(s).forEach(r=>o[r.dataset.pos]=r.innerText.replace(/\\s+/g,' ')); return o; }", "tr[data-pos]" if w > 900 else ".tcard[data-pos]")
        st = js(page, "()=>getBook('main').trades.find(x=>x.id==='ob0').status")
        check(f"{tag} 11 PF1 — ไม้ที่เปิดอยู่: ไม่มีป้าย สวน Bias สัปดาห์ · ไม่ถูกปิด", st == "open" and "สวน Bias สัปดาห์" not in pv.get("ob0", ""), f"{st} {pv.get('ob0')}")
        # 7D.2 ทางเดิม
        js(page, """()=>{ sat7dWrite('satIdeas','iO',{asset:'XAUUSD', bias:'Long', week:wpWeekKey(), created_at:new Date().toISOString(), checks:{g1:true,g2:true,g3:true,setup:true}, entry:2410, sl:2390, tp:2450, invalidation:'x', note:'', status:'active', accts:{}}); }"""); page.wait_for_timeout(300)
        o = js(page, "()=>{ const c=sat7dCalc(sat7dIdea('iO'),'main'); return {ready:c.ready, off:c.offBias, w0:c.warns[0], lot:c.lot}; }")
        n_a = js(page, "()=>getBook('main').trades.length")
        js(page, "()=>sat7dSaveOrder('iO','main')"); page.wait_for_timeout(300)
        n_b = js(page, "()=>getBook('main').trades.length")
        check(f"{tag} 11 PF1 — ทาง 7D.2 (sat7dCalc): Long ขณะ Bias Short → ไม่ถูกบล็อกด้วยสวน Bias (offBias false · ไม่มีเหตุผลสวน Bias)", not o["off"] and "สวน Bias" not in str(o["w0"]), json.dumps([o, n_a, n_b], ensure_ascii=False))
        # สลับกลับ → ready
        wk(page, "XAUUSD", "Long", "up", inval=2300); js(page, "()=>satV3Render()"); page.wait_for_timeout(300)
        cm, cf = calc(page, "iL"), calc(page, "iL", "fam")
        check(f"{tag} 11 สลับกลับเป็น Long → ready เหมือนเดิม", cm["ready"] and cf["ready"], json.dumps([cm["warns"], cf["warns"]], ensure_ascii=False))
        js(page, "()=>satV3SaveSlot('iL','main')"); page.wait_for_timeout(350)
        check(f"{tag} 11 PF1 — บันทึกตรง ๆ ตอน Strategy bias สวนแผนสร้างไม้ได้ปกติ (ไม่มีบล็อกสวน Bias)", nt1[0] > nt0[0] and nt1[1] > nt0[1], json.dumps([nt0, nt1]))
        # Bias ยังไม่ตั้ง / Neutral → ไม่บล็อก
        clean(page); setup_week(page, "Short"); plan(page, "iN")
        js(page, "()=>satwWrite('XAUUSD', {bias:'None'})"); page.wait_for_timeout(200)
        c_none = calc(page, "iN")
        js(page, "()=>satwWrite('XAUUSD', {bias:null})"); page.wait_for_timeout(200)
        c_null = calc(page, "iN")
        check(f"{tag} 11 Bias สัปดาห์ Neutral(None) / ยังไม่ตั้ง → ไม่บล็อกด้วยเหตุผลสวน Bias", not c_none["offBias"] and not c_null["offBias"] and not any("สวน Bias" in x for x in c_none["warns"] + c_null["warns"]), json.dumps([c_none["warns"], c_null["warns"]], ensure_ascii=False))
        # ไม่แตะ ×0.6
        check(f"{tag} 11 ไม่แตะตัวคูณ ×0.6: SAT_MACRO_CUT = 0.6 · Calc.sizeRule against+against = 0.6", js(page, "()=>[SAT_MACRO_CUT, Calc.sizeRule({macroAlign:'against', trendState:'down', side:'Long'}).factor]") == [0.6, 0.6])
        # ── 12 ล้น/console
        clean(page); setup_week(page, "Short"); plan(page, "iZ"); p5.goto_sat(page)
        js(page, "()=>{ satV3Open.add('iZ'); satV3Render(); }"); page.wait_for_timeout(300)
        bad = overflow(page, ["[data-sat-meta]"])
        open_set(page); bad2 = overflow(page, ["#satRiskSec", "#satRiskSec .secbody"])
        check(f"{tag} 12 แถบบัญชี Sat + ส่วนค่าตั้ง SAT ไม่ล้นแนวนอน", not bad and not bad2, json.dumps([bad, bad2]))
        check(f"{tag} 12 ไม่มี console/page error", not ce and not pe, json.dumps([ce[:3], pe[:3]]))
    finally:
        context.close(); browser.close()


def main():
    with sync_playwright() as pw:
        ui_tests(pw, 1440, 900, "1440px")
        ui_tests(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 34 / SR1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
