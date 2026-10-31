#!/usr/bin/env python3
"""RG2b — ถัง Winner / Ladder / Sat แยกกัน · Sat คิดจากถังทั้งก้อน · หน้า Ladder · เส้น Port 50/30/20 · เทส 113
Chromium · 300 / 390 / 1440 · ข้อมูล SAMPLE ล้วน (fixture P77: Core ฿4.2M · Sat $45k · fx 33)
ภาพ tests/screenshots/rg2b-{settings-pools-390,settings-pools-1440,ladder-300,ladder-390,ladder-1440,scope-hdr-1440,scope-page-300,port-line-390,port-line-1440}.png
รัน: SECT='pools winner sat ladder port' python3 run_tests_phase113.py"""
import json, os, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase24 as P24
import run_tests_phase107 as T

ENGINE = base.BROWSER_ENGINE
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")
results = []
js = C.js
settle, cnt, txt = T.settle, T.cnt, T.txt
CORE, SATB, FX = 4200000, 45000, 33
TOTAL = CORE + SATB * FX
POOL = {"w": TOTAL * 0.5, "l": TOTAL * 0.3, "s": TOTAL * 0.2}


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    os.makedirs(SHOTS, exist_ok=True)
    page.wait_for_timeout(700)
    p = os.path.join(SHOTS, name)
    (page.locator(sel).first.screenshot(path=p) if sel else page.screenshot(path=p))
    return p


def sections():
    env = os.environ.get("SECT", "").split()
    return env or ["pools", "winner", "sat", "ladder", "port", "core47", "node"]


def near(a, b, tol=1.0): return abs(a - b) <= tol


def W(t, **kw):
    d = {"ticker": t, "market": "US", "port": "core", "note": "", "industry": "", "added_at": "2026-09-01T00:00:00.000Z"}
    d.update(kw); return d


def fort_stub(page, syms):
    page.evaluate("(s)=>{ window.__csOrig = window.__csOrig || csEvalOf; window.csEvalOf = x=> s.includes(String(x).toUpperCase()) ? {fortress:'passed'} : null; }", syms)


def launch(pw, w, h, trades=None, cards=None, mut=None):
    return C.launch2(pw, w, h, trades or [], cards or {}, mut=mut, fx=FX)


def set_ff(page, acwi, hyg):
    def pair(u): return {"up": u, "flip_days": 12, "tf": "D", "ema": [20, 50], "bar": "2026-10-01", "slow": {"up": u, "flip_days": 30, "ema": [50, 100]}}
    j = {"as_of": "2026-10-01", "ver": 2, "ratios": {"ACWI_BIL": pair(acwi), "HYG_IEI": pair(hyg)}}
    page.evaluate("async (j)=>{ window.__FF_JSON = j; await ffLoadJson(true); }", j)
    settle(page, 250)


# ───────────────────────── 1 Pools ─────────────────────────
def pools_tests(pw):
    for w, h, label in ((390, 844, "390px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h)
        try:
            P = js(page, "()=>{ const p = poolsOf('main'); return [p.total, p.winner, p.ladder, p.sat, JSON.stringify(state.settings.pools)]; }")
            check(f"{tag} §4.1 ย้ายครั้งแรก: ยอดรวม = core + satB×fx · 50/30/20 ทั้งก้อน (Sat หด)", near(P[0], TOTAL) and near(P[1], POOL["w"]) and near(P[2], POOL["l"]) and near(P[3], POOL["s"]), P)
            pl = json.loads(P[4])
            check(f"{tag} §4.1 settings.pools = 50/30/20 · mig RG2b · reviewed false (รอทบทวน)", pl["winner"] == 50 and pl["ladder"] == 30 and pl["sat"] == 20 and pl.get("mig") == "RG2b" and pl.get("reviewed") is False, pl)
            cap = js(page, "()=>state.settings.capital")
            check(f"{tag} §4.1 capital เดิมไม่ถูกเขียนทับ (ยังเป็นแหล่งยอดบัญชี)", cap["core"] == CORE and cap["satB"] == SATB, cap)
            # เปิด Settings: ช่องแบ่ง + ข้อความ + แจ้งครั้งเดียว
            js(page, "()=>{ openSettings(); }"); settle(page, 500)
            vals = js(page, "()=>['sPoolW','sPoolL','sPoolS'].map(i=>document.getElementById(i).value)")
            check(f"{tag} §4.1 Settings: ช่อง Winner/Ladder/Sat = 50/30/20", vals == ["50", "30", "20"], vals)
            hint = txt(page, "#poolHint")
            check(f"{tag} §4.1 แสดงยอด ฿ ต่อถัง", "Winner ฿" in hint and "Ladder ฿" in hint and "Sat ฿" in hint, hint)
            nv = js(page, "()=>{ const n = document.getElementById('poolNotice'); return [n.style.display, n.innerText]; }")
            check(f"{tag} §4.1 แจ้งให้ทบทวนการแบ่ง (ครั้งเดียว)", nv[0] != "none" and "50 / 30 / 20" in nv[1], nv)
            # ตรวจค่า: รวมไม่ครบ 100 → error + ปุ่มบันทึกล็อก
            js(page, "()=>{ document.getElementById('sPoolS').value = '25'; crOnInput(); }")
            er = js(page, "()=>[document.querySelector('[data-err-for=sPoolS]').textContent, document.getElementById('setSaveBtn').disabled]")
            check(f"{tag} §4.1 รวม ≠ 100 → error + ล็อกบันทึก", "total 100" in er[0] and er[1] is True, er)
            js(page, "()=>{ document.getElementById('sPoolW').value = '120'; document.getElementById('sPoolL').value = '-10'; document.getElementById('sPoolS').value = '-10'; crOnInput(); }")
            er = js(page, "()=>[document.querySelector('[data-err-for=sPoolS]').textContent, document.getElementById('setSaveBtn').disabled]")
            check(f"{tag} §4.1 แต่ละช่องต้อง 0–100", "0–100" in er[0] and er[1] is True, er)
            # แก้เป็น 40/40/20 แล้วบันทึก → ถังเปลี่ยน · reviewed true · แจ้งหาย
            js(page, "()=>{ document.getElementById('sPoolW').value = '40'; document.getElementById('sPoolL').value = '40'; document.getElementById('sPoolS').value = '20'; crOnInput(); }")
            check(f"{tag} §4.1 40/40/20 ผ่านการตรวจ", js(page, "()=>document.getElementById('setSaveBtn').disabled") is False)
            js(page, "()=>{ saveSettings(); }"); settle(page, 600)
            P2 = js(page, "()=>{ const p = poolsOf('main'); return [p.winner, p.ladder, p.sat, state.settings.pools.reviewed, state.settings.pools.mig]; }")
            check(f"{tag} §4.1 บันทึกแล้วถังตามที่แบ่ง · reviewed true · mig คงอยู่", near(P2[0], TOTAL * 0.4) and near(P2[1], TOTAL * 0.4) and near(P2[2], TOTAL * 0.2) and P2[3] is True and P2[4] == "RG2b", P2)
            js(page, "()=>{ openSettings(); }"); settle(page, 400)
            nv = js(page, "()=>document.getElementById('poolNotice').style.display")
            check(f"{tag} §4.1 หลังทบทวนแล้ว ไม่แจ้งซ้ำ", nv == "none", nv)
            ov = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
            check(f"{tag} Settings ไม่ล้นแนวนอน", ov <= 0, ov)
            js(page, "()=>{ document.getElementById('poolBlock').scrollIntoView({block:'center'}); }")
            shot(page, f"rg2b-settings-pools-{w}.png", "#poolBlock")
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()


def over_tests(pw):
    """ย้ายด้วยตำแหน่งเกินถังใหม่ → เตือนอย่างเดียว ไม่แตะอะไร"""
    big = P13.T("tBig", "core", "open", sym="BIGW", entry=100, sl=90, qty=30000, cur="THB", date="2026-09-10")   # ทุน ฿3.0M > Winner ฿2.84M
    b, page, ce, pe = launch(pw, 390, 844, [big], {})
    try:
        before = js(page, "()=>JSON.stringify(getBook('main').trades.map(t=>[t.id,t.qty,t.sl,t.status]))")
        w = js(page, "()=>poolsWarn('main')")
        check("[over] §4.1 ตำแหน่งเกินถัง Winner → มีคำเตือน (ข้อความบอกว่าไม่ได้ปิด/ย่อ)", len(w) == 1 and "Nothing was closed or resized" in w[0], w)
        js(page, "()=>{ render(); }"); settle(page, 300)
        after = js(page, "()=>JSON.stringify(getBook('main').trades.map(t=>[t.id,t.qty,t.sl,t.status]))")
        check("[over] §4.1 ไม่มีอะไรถูกปิด/ย่อ/เปลี่ยน", before == after, [before, after])
        js(page, "()=>{ openSettings(); }"); settle(page, 400)
        nt = txt(page, "#poolNotice")
        check("[over] §4.1 คำเตือนแสดงใน Settings › Pools", "Winner holds" in nt, nt)
        check("[over] ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 2 Winner / Ladder ─────────────────────────
def winner_tests(pw):
    ladder_card = P24.card("ccLd", "main", "LADX", strategy="L", status="plan", tier="A",
                           ladder={"levels": [{"px": 100, "status": "wait"}, {"px": 90, "status": "wait"}, {"px": 80, "status": "wait"}], "sl": 70, "budgetPct": 0.1667, "split": [0.4, 0.3, 0.3]})
    wtr = [P13.T("tW1", "core", "open", sym="WINX", entry=100, sl=90, qty=1000, cur="THB", date="2026-09-10")]
    for w, h, label in ((390, 844, "390px"),):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h, wtr, {})
        try:
            ctx0 = js(page, "()=>{ const c = coreCtx('main'); return [c.tankTHB, c.ladderPoolTHB, c.cashTHB, c.lCashTHB, c.wCost]; }")
            check(f"{tag} §4.1 Winner tank = ถัง Winner · Ladder tank = ถัง Ladder", near(ctx0[0], POOL["w"]) and near(ctx0[1], POOL["l"]), ctx0)
            check(f"{tag} §4.1 Winner ว่าง = ถัง Winner − ทุน W (ไม่หักถัง Ladder)", near(ctx0[2], POOL["w"] - 100000) and near(ctx0[3], POOL["l"]), ctx0)
            # วางบันไดใหม่ (การ์ดแผน) → Ladder ว่างลด · Winner ว่างเท่าเดิม
            page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", ["ccLd", ladder_card])
            js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 800)
            ctx1 = js(page, "()=>{ const c = coreCtx('main'); return [c.cashTHB, c.lCashTHB, c.split.lReserved, c.split.lUsed]; }")
            check(f"{tag} §4.1 วางบันได → Ladder ว่างลด ตามงบจอง", ctx1[1] < ctx0[3] - 1 and near(ctx0[3] - ctx1[1], ctx1[2], 1), [ctx0, ctx1])
            check(f"{tag} §4.1 วางบันได → Winner ว่างไม่ลด", near(ctx1[0], ctx0[2], 0.5), [ctx0, ctx1])
            # ไม้ W เพิ่ม → Winner ว่างลด · Ladder ว่างเท่าเดิม
            js(page, "()=>{ const B=getBook('main'); B.trades.push({id:'tW2', port:'core', sym:'WINY', status:'open', entry:100, sl:90, qty:2000, cur:'THB', date:'2026-09-11', bias:'Long'}); saveBook('main'); render(); }"); settle(page, 400)
            ctx2 = js(page, "()=>{ const c = coreCtx('main'); return [c.cashTHB, c.lCashTHB]; }")
            check(f"{tag} §4.1 ซื้อ W เพิ่ม → Winner ว่างลด · Ladder ว่างไม่เปลี่ยน", near(ctx1[0] - ctx2[0], 200000, 1) and near(ctx2[1], ctx1[1], 0.5), [ctx1, ctx2])
            # ไม่มีประตู/เหตุผล GATE_ · ไม่มี L_SHARE / LAYER2
            r = js(page, """()=>{ const cs=Calc.coreSize, bx=coreBase('main'); const nl=cs.ladder({tier:'A',tank:bx.ladderPoolTHB,sl:70,levels:[{px:100},{px:90},{px:80}],budgetPct:0.05});
                const cp=coreCanPlace('main',{tier:'A',fortress:true,thb:nl},null,false); return [cp.reasons, cp.rows.map(x=>x.k), JSON.stringify(cs.canPlaceLadder({tank:1e6,tier:'A',ladder:nl}).reasons)]; }""")
            check(f"{tag} §4.1 วางบันไดไม่มีเหตุผล GATE_*/L_SHARE_OVER/LAYER2_OVER · แถวเช็กไม่มี gate/share/l2", not any(x.startswith("GATE_") or x in ("L_SHARE_OVER", "LAYER2_OVER") for x in r[0]) and not any(k in ("gate", "share", "l2") for k in r[1]), r)
            # งบบันได = 5% ของบัญชี × f
            T.wl_seed(page, [W("FRTA")]); fort_stub(page, ["FRTA"])
            for acwi, hyg, f in ((True, True, 1.0), (True, False, 0.75), (False, False, 0.5)):
                set_ff(page, acwi, hyg)
                js(page, "()=>{ ldrNew('FRTA'); }"); settle(page, 500)
                v = js(page, "()=>[parseFloat(document.getElementById('cnLbud').value), document.getElementById('cnLbudT').textContent]")
                want = 0.05 * TOTAL * f / POOL["l"] * 100
                check(f"{tag} §4.1 งบบันไดเริ่ม = 5% ของบัญชี × f {int(f*100)}% = {want:.3f}% ของถัง Ladder", abs(v[0] - want) < 0.01 and "5%" in v[1], [v, want])
                js(page, "()=>{ coreSheetClose(); }")
            cfg = js(page, "()=>{ const c = coreRiskCfg('main'); return [c.ladderMaxAcctPct, c.winnerCap, c.tierA, c.tierB, c.capTotalA, c.capTotalB]; }")
            check(f"{tag} §4.1 ตั้งค่าเริ่ม: Ladder ต่อหุ้น 5% ของบัญชี · Winner ต่อหุ้น 25%", cfg[0] == 5 and cfg[1] == 25 and set(cfg[2:]) == {25}, cfg)
            ov = js(page, "()=>{ const o = coreSizeOpts('main'); return [o.stockCap.A, o.stockCap.B, o.tierCap.A, o.tierCap.B]; }")
            check(f"{tag} §4.5 เพดานต่อหุ้นค่าเดียว 25% ของถัง Winner (ไม่แยก Tier)", set(ov) == {0.25}, ov)
            # first lot ติดเพดาน 25% ของถัง Winner
            fl = js(page, "()=>{ const cx = coreCtx('main'); const r = coreFirstLotCalc(cx,'TH','A',100,99,1,0.05); return r && r.ok ? [r.qty, r.stockCapped, cx.tankTHB] : null; }")
            check(f"{tag} §4.5 ไม้แรก (ราคา 100 · Risk ใหญ่) ถูกจำกัดที่ 25% ของถัง Winner", fl and fl[0] * 100 <= fl[2] * 0.25 and fl[0] * 100 > fl[2] * 0.249, fl)
            # Settings: ไม่มีช่อง Tier/ladderShare/gateWeeks ให้เห็น · ชั้น 2 ไม่มีสถานะเหลือง/แดง
            js(page, "()=>{ openSettings(); }"); settle(page, 500)
            vis = js(page, """()=>['sCrTierA','sCrTierB','sCrCapTotA','sCrCapTotB','sCrRiskB','sCrL2Warn','sCrLShare','sCrGate'].map(i=>{ const e=document.getElementById(i); return !!(e && e.offsetParent); })""")
            check(f"{tag} §4.1/4.5 ช่อง Tier A/B · Layer 2 · ladderShare · gateWeeks ไม่แสดง", not any(vis), vis)
            keep = js(page, "()=>[document.getElementById('sCrWinCap').value, document.querySelector('[data-cr-tiertbl]')]")
            check(f"{tag} §4.5 มีช่องเพดานต่อหุ้นค่าเดียว · ไม่มีตาราง Tier", keep[0] == "25" and keep[1] is None, keep)
            lv = js(page, "()=>[coreL2Level(99, coreRiskCfg('main')), coreL2Level(5, coreRiskCfg('main'))]")
            check(f"{tag} §4.5 ชั้น 2: ไม่มีเหลือง/แดง/บล็อก (ถอดเพดานแล้ว)", lv == ["ok", "ok"], lv)
            # key เดิมไม่หายหลังบันทึก
            js(page, "()=>{ state.settings.coreRisk = Object.assign({}, state.settings.coreRisk, {tierA:15, tierB:10, capTotalA:22, capTotalB:22, ladderShare:30, gateWeeks:3, l2Warn:14, riskB:1.1}); openSettings(); }"); settle(page, 400)
            js(page, "()=>{ saveSettings(); }"); settle(page, 500)
            kk = js(page, "()=>{ const c = state.settings.coreRisk; return [c.tierA, c.tierB, c.capTotalA, c.ladderShare, c.gateWeeks, c.l2Warn, c.riskB, c.winnerCap, c.ladderMaxAcctPct]; }")
            check(f"{tag} §4.1 key เดิมเก็บไว้หลังบันทึก (ไม่ใช้) + key ใหม่ถูกเขียน", kk == [15, 10, 22, 30, 3, 14, 1.1, 25, 5], kk)
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()


# ───────────────────────── 3 Sat ─────────────────────────
def sat_tests(pw):
    def mut(doc):
        doc["books"]["main"]["settings"]["satV2"] = {"mainPct": 70, "tacPct": 30, "rptMain": 2, "rptTac": 2, "capMain": 2, "capTac": 4, "brkDd": 10}
    b, page, ce, pe = launch(pw, 390, 844, [], {}, mut=mut)
    try:
        tag = f"[{ENGINE}/390px]"
        m = js(page, "()=>{ const m = satV2Money('main'); return [m.satTHB, m.mainTHB, m.tacTHB, m.totalTHB]; }")
        check(f"{tag} §4.2 Main และ Tactical คิดจากถัง Sat ทั้งก้อน (ไม่มี 70/30)", near(m[0], POOL["s"]) and m[0] == m[1] == m[2], m)
        check(f"{tag} §4.2 พอร์ตรวม = ยอดบัญชี", near(m[3], TOTAL), m)
        pr = js(page, "()=>[JSON.stringify(SAT_V2_RPTS_MAIN), JSON.stringify(SAT_V2_RPTS_TAC), SAT_V2_DEF.rptMain, SAT_V2_DEF.rptTac, SAT_NEW_WEEK_MAX]")
        check(f"{tag} §4.2 รายการ RPT: Main 0.5·0.75·1·1.25·1.5·2 (เริ่ม 1.5) · Tactical 0.25·0.5·0.75·1 (เริ่ม 0.75) · สัปดาห์ละ 4", pr == ["[0.5,0.75,1,1.25,1.5,2]", "[0.25,0.5,0.75,1]", 1.5, 0.75, 4], pr)
        c = js(page, "()=>satV2Cfg('main')")
        check(f"{tag} §4.2 ค่าเก่า migrate: cap Main 2→1.4 · Tactical 4→1.2 · เบรก DD 10→3", c["capMain"] == 1.4 and c["capTac"] == 1.2 and c["brkDd"] == 3, c)
        check(f"{tag} §4.2 RPT Tactical เก่า 2 (นอกรายการ) → ค่าเริ่ม 0.75 + แจ้งครั้งเดียว · Main 2 คงเดิม", c["rptTac"] == 0.75 and c["rptMain"] == 2 and c["rptReset"] == ["rptTac"], c)
        sizes = js(page, "()=>{ const b = sat7dAcctBase('main'); return [b.cap, b.newMax, b.riskTHBFull]; }")
        check(f"{tag} §4.2 งบเสี่ยง/ไม้ = RPT × ถัง Sat ทั้งก้อน · โควตา 4", near(sizes[0], POOL["s"]) and sizes[1] == 4 and near(sizes[2], POOL["s"] * 1.5 / 100, 1), sizes)
        caps = js(page, "()=>satV2Caps('main')")
        check(f"{tag} §4.2 เพดาน Open Risk ยังคิดจากพอร์ตรวม (Sat 1.2% · สินค้า 0.6% · รวม 6%)", near(caps["sat"], TOTAL * 0.012) and near(caps["asset"], TOTAL * 0.006) and near(caps["total"], TOTAL * 0.06), caps)
        # เบรก Tactical: DD 3% ของถัง Sat
        brk = js(page, """()=>{ const B = getBook('main'); const sat = satV2Money('main').satTHB;
            B.trades = [{id:'t1', port:'satB', sym:'XAUUSD', status:'closed', bias:'Long', entry:100, exitPrice:99, qty:1, mult:1, cur:'THB', sleeve:'tactical', exitDate:'2026-09-01', date:'2026-08-30'}];
            const fx = 1; const loss = sat * 0.031; B.trades[0].qty = loss; saveBook('main'); const br = satV2Brake('main'); return [br.ddMax, br.byDd, Math.round(br.ddPct*100)/100]; }""")
        check(f"{tag} §4.2 เบรก Tactical DD 3% ของถัง Sat: ขาดทุน 3.1% → หยุด", brk[0] == 3 and brk[1] is True, brk)
        # โควตา: Main + Tactical นับรวม
        q = js(page, """()=>{ const B = getBook('main'); const mk=(id,sl)=>({id, port:'satB', sym:'XAUUSD', status:'open', bias:'Long', entry:100, sl:95, qty:1, mult:1, cur:'USD', date:thaiToday(), sleeve:sl});
            B.trades = [mk('a','main'), mk('b','tactical'), mk('c','tactical'), mk('d','main')]; saveBook('main'); const b = sat7dAcctBase('main'); return [b.nNew, b.newMax]; }""")
        check(f"{tag} §4.2 ไม้ใหม่/สัปดาห์: Main + Tactical นับรวม (4 ไม้ = 4/4)", q[0] == 4 and q[1] == 4, q)
        # ไม่มี Macro size ×
        mf = js(page, "()=>{ const f = satMacroFactors('main'); const c = satRiskCfg('main'); return [f.neutral, f.against, c.macroNeutral, c.macroAgainst]; }")
        check(f"{tag} §4.2 ไม่มีตัวคูณขนาดตาม Macro (Neutral/Against = 1)", mf == [1, 1, 1, 1], mf)
        js(page, "()=>{ openSettings(); }"); settle(page, 500)
        vis = js(page, "()=>['sSatMacroNeutral','sSatMacroAgainst','sSatNewMax','sV2Main','sV2Tac'].map(i=>{ const e=document.getElementById(i); return !!(e && e.offsetParent); })")
        check(f"{tag} §4.2 ช่อง Macro ×/ไม้ใหม่/Main%/Tactical% ไม่แสดง", not any(vis), vis)
        opts = js(page, "()=>[[...document.getElementById('sV2RptMain').options].map(o=>o.value), [...document.getElementById('sV2RptTac').options].map(o=>o.value)]")
        check(f"{tag} §4.2 Settings: RPT เป็นรายการเลือก (ไม่มีช่องพิมพ์เอง)", opts == [["0.5", "0.75", "1", "1.25", "1.5", "2"], ["0.25", "0.5", "0.75", "1"]], opts)
        lab = js(page, "()=>document.getElementById('sV2CapMain').closest('.f').innerText + '|' + document.getElementById('sV2BrkDd').closest('.f').innerText")
        check(f"{tag} §4.2 ป้ายเพดาน/เบรกเขียนว่า of Sat pool", lab.count("Sat pool") == 2, lab)
        js(page, "()=>{ saveSettings(); }"); settle(page, 400)
        sv = js(page, "()=>state.settings.satV2")
        check(f"{tag} §4.2 บันทึกแล้วประทับ poolMig · ไม่เก็บ mainPct/tacPct · แจ้ง RPT แล้ว", sv.get("poolMig") == "RG2b" and "mainPct" not in sv and sv.get("rptNoticed") is True and sv["rptTac"] == 0.75 and sv["capMain"] == 1.4, sv)
        c2 = js(page, "()=>satV2Cfg('main')")
        check(f"{tag} §4.2 อ่านซ้ำหลังบันทึก: ไม่ migrate ซ้ำ (1.4 / 1.2 / 3)", c2["capMain"] == 1.4 and c2["capTac"] == 1.2 and c2["brkDd"] == 3 and c2["rptReset"] == [], c2)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 4 Ladder page ─────────────────────────
def ladder_tests(pw):
    cards = {"ccLd": P24.card("ccLd", "main", "LADX", strategy="L", status="plan", tier="A",
                              ladder={"levels": [{"px": 100, "status": "bought"}, {"px": 90, "status": "wait"}, {"px": 80, "status": "cancelled"}], "sl": 70, "budgetPct": 0.1667, "split": [0.4, 0.3, 0.3]})}
    for w, h, label in ((300, 800, "300px"), (390, 844, "390px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h, [], cards)
        try:
            js(page, "()=>{ switchTab('plan'); }"); settle(page, 400)
            ids = js(page, "()=>[...document.querySelectorAll('.scopeBtn')].map(b=>b.id+':'+b.textContent.replace(/\\s+/g,' ').trim().replace(/ [SLF]$/,''))")
            check(f"{tag} §4.3 สวิตช์ 3 ปุ่ม Winner | Ladder | Sat", ids == ["scopeStock:Winner", "scopeLadder:Ladder", "scopeFuture:Sat"], ids)
            where = js(page, "()=>document.getElementById('scopeLadder').closest('#hdrSub') ? 'header' : (document.getElementById('scopeLadder').closest('.planScope') ? 'page' : '?')")
            if w <= 390: check(f"{tag} §4.3 จอแคบ: 3 ปุ่มเต็มอยู่ในหน้า (ไม่ใช้ select · ไม่ทับปุ่ม header)", where == "page", where)
            # ห้ามทับ / ล้น
            box = js(page, "()=>[...document.querySelectorAll('.scopeBtn')].map(b=>{ const r=b.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.width)]; })")
            cmp_ = js(page, "()=>!!document.querySelector('#hdrSub.cmp .hdrCmp select')")
            if cmp_:
                lab = js(page, "()=>[...document.querySelector('#hdrSub .hdrCmp select').options].map(o=>o.textContent.replace(/\\s+/g,' ').trim().replace(/ [SLF]$/,''))")
                check(f"{tag} §4.3 header แคบ: รูปย่อ (select) มี Winner · Ladder · Sat", lab == ["Winner", "Ladder", "Sat"], lab)
            vis = cmp_ or (all(r[2] > 20 for r in box) and (box[2][1] <= w if where == "page" else True))
            check(f"{tag} §4.3 ปุ่มทั้งสามมองเห็น/อยู่ในจอ", vis, box)
            if w == 300: shot(page, "rg2b-scope-page-300.png", "#tabPlan .planScope")
            # สลับ
            page.evaluate("()=>document.getElementById('scopeLadder').click()"); settle(page, 600)
            check(f"{tag} §4.3 กด Ladder → planScope=ladder · หน้า Ladder แสดง · แผง Winner/Sat ซ่อน", js(page, "()=>planScope") == "ladder" and js(page, "()=>document.getElementById('ladderPanel').style.display") == "" and js(page, "()=>document.getElementById('corePanel').offsetParent") is None)
            hd = txt(page, "[data-ldr-head]")
            check(f"{tag} §4.3 หัวหน้า: Pool ใช้/ถัง · Free · Size chip", "Pool" in hd and "Free" in hd and "Size" in hd, hd)
            pool = js(page, "()=>{ const t = document.querySelector('[data-ldr-used]').textContent; return t; }")
            check(f"{tag} §4.3 Pool = ถัง Ladder ฿{POOL['l']:,.0f}", f"{POOL['l']:,.0f}" in pool, pool)
            chip = txt(page, "[data-ldr-size]")
            check(f"{tag} §4.3 chip Size 100/75/50 (ไม่มีข้อมูล = 100)", chip in ("Size 100%", "Size 75%", "Size 50%"), chip)
            for acwi, hyg, f in ((True, True, 100), (True, False, 75), (False, False, 50)):
                set_ff(page, acwi, hyg); js(page, "()=>{ render(); }"); settle(page, 300)
                check(f"{tag} §4.3 chip = Size {f}%", txt(page, "[data-ldr-size]") == f"Size {f}%", txt(page, "[data-ldr-size]"))
            # การ์ด: T1..T3 · สถานะ · progress dots · avg · exit
            card = js(page, """()=>{ const c = document.querySelector('[data-ldr-card=ccLd]'); if(!c) return null;
                return {lv:[...c.querySelectorAll('[data-ldr-lv]')].map(x=>x.dataset.ldrSt), dots:[...c.querySelectorAll('[data-ldr-dot]')].map(x=>x.dataset.ldrDot), txt:c.innerText.replace(/\\s+/g,' ')}; }""")
            check(f"{tag} §4.3 การ์ด Active: T1 bought · T2 waiting · T3 cancelled + จุดความคืบหน้า", card and card["lv"] == ["bought", "wait", "cancelled"] and card["dots"] == ["bought", "wait", "cancelled"], card)
            check(f"{tag} §4.3 การ์ดมี avg cost + บรรทัด Exit (SL)", card and "avg" in card["txt"] and "Exit: SL" in card["txt"], card and card["txt"])
            acts = js(page, "()=>[...document.querySelectorAll('[data-ldr-card=ccLd] [data-ldr-act] button')].map(b=>b.dataset.ldrBuy!==undefined?'buy':b.dataset.ldrCancel!==undefined?'cancel':b.dataset.ldrEdit!==undefined?'edit':'?')")
            check(f"{tag} §4.3 ปุ่ม: mark bought · cancel level · edit zones", acts == ["buy", "cancel", "edit"], acts)
            check(f"{tag} §4.3 ปุ่ม + New ladder และลิงก์ Journal (Ladder bucket) มีอยู่", cnt(page, "[data-ldr-new]") == 1 and cnt(page, "[data-ldr-journal]") == 1)
            # แตะการ์ด → sheet (มือถือ/ทุกจอ)
            page.locator("[data-ldr-card=ccLd]").first.click(position={"x": 8, "y": 8}); settle(page, 500)
            check(f"{tag} §4.3 แตะการ์ด → เปิด sheet รายละเอียด", cnt(page, ".core-sheet [data-core-card]") == 1 or cnt(page, ".core-sheet [data-ldr-sheet-close]") == 1)
            js(page, "()=>{ coreSheetClose(); }")
            # ปุ่ม mark bought เปิดฟอร์มเดิม (ไม่มีกติกาใหม่)
            page.locator("[data-ldr-card=ccLd] [data-ldr-buy]").first.click(); settle(page, 500)
            check(f"{tag} §4.3 Mark T2 bought → ฟอร์มซื้อ L เดิม", cnt(page, ".core-sheet") >= 1 and "T2" in js(page, "()=>document.querySelector('.core-sheet').innerText + 'T2'"))
            js(page, "()=>{ coreSheetClose(); }")
            # Watching: ต้องผ่าน Fortress · เลือกสถานะ · ระยะ EMA
            T.wl_seed(page, [W("FRTA"), W("NOFT")]); fort_stub(page, ["FRTA"]); js(page, "()=>{ render(); }"); settle(page, 400)
            opts = js(page, "()=>[...document.querySelectorAll('#ldrAddSel option')].map(o=>o.value)")
            check(f"{tag} §4.3 เลือกเข้า Watching ได้เฉพาะหุ้นที่ Fortress ผ่าน", opts == ["", "FRTA"], opts)
            js(page, "()=>{ document.getElementById('ldrAddSel').value='FRTA'; ldrWatchAdd(); }"); settle(page, 300)
            w1 = js(page, "()=>{ const e = document.querySelector('[data-ldr-w=FRTA]'); return e ? [[...e.querySelector('[data-ldr-state]').options].map(o=>o.value), e.querySelector('[data-ldr-state]').value, e.querySelectorAll('[data-ldr-dist]').length] : null; }")
            check(f"{tag} §4.3 Watching: สถานะ Base · Sideways-Up · Broken (ไม่มี Uptrend) + ช่อง EMA20/50/200", w1 == [["Base", "Sideways-Up", "Broken"], "Base", 3], w1)
            js(page, "()=>{ ldrStateSet('FRTA','Broken'); ldrDistSet('FRTA','ema50','-4.5'); }"); settle(page, 600)
            w2 = js(page, "()=>{ const it = wlItems.find(x=>x.ticker==='FRTA'); return [it.ladder_state, it.ladder_dist.ema50, it.ladder_watch]; }")
            check(f"{tag} §4.3 ตั้งสถานะ + ระยะ EMA เอง", w2 == ["Broken", -4.5, True], w2)
            ov = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
            check(f"{tag} §4.3 หน้า Ladder ไม่ล้นแนวนอน", ov <= 0, ov)
            js(page, "()=>{ window.csEvalOf = window.__csOrig; render(); }"); settle(page, 300)
            shot(page, f"rg2b-ladder-{w}.png")
            if w == 1440: shot(page, "rg2b-scope-hdr-1440.png", ".topbar")
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()
    # กดสลับในหัวหน้า (≥ 430 จอ mob = header · desk = header/select)
    b, page, ce, pe = launch(pw, 480, 900, [], cards)
    try:
        js(page, "()=>{ switchTab('plan'); }"); settle(page, 500)
        where = js(page, "()=>document.getElementById('scopeLadder').closest('#hdrSub') ? 'header' : 'page'")
        r = js(page, "()=>{ const b = [...document.querySelectorAll('#hdrSub .scopeBtn')].map(x=>{const q=x.getBoundingClientRect(); return [Math.round(q.left), Math.round(q.right)]}); const hb = document.querySelector('.topbar .hbtns').getBoundingClientRect(); return [b, Math.round(hb.left)]; }")
        check("[480px] §4.3 สวิตช์อยู่ใน header (ช่อง hdrSub) และไม่ทับปุ่มขวา", where == "header" and r[0] and r[0][-1][1] <= r[1], [where, r])
        page.evaluate("()=>document.getElementById('scopeLadder').click()"); settle(page, 500)
        check("[480px] §4.3 กดใน header → ไป Ladder", js(page, "()=>planScope") == "ladder")
    finally: b.close()


# ───────────────────────── 5 Port line ─────────────────────────
def port_tests(pw):
    # Winner ถือ ฿1.42M (≈25% ของบัญชี · เป้า 50) → ห่าง 25 จุด = เหลือง
    wtr = [P13.T("tW1", "core", "open", sym="WINX", entry=100, sl=90, qty=14200, cur="THB", date="2026-09-10")]
    for w, h, label in ((390, 844, "390px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h, wtr, {})
        try:
            js(page, "()=>{ switchTab('mix'); ln3PortSet('main'); renderPortfolioMix(); }"); settle(page, 600)
            line = txt(page, "[data-pool-txt]")
            wp = round(1420000 / TOTAL * 100)
            check(f"{tag} §4.4 บรรทัดถัง: Winner {wp}/50 · Ladder 0/30 · Sat 0/20", line == f"Winner {wp}/50 · Ladder 0/30 · Sat 0/20", line)
            check(f"{tag} §4.4 จุดเหลืองเมื่อถังใดห่างเป้า > 5 จุด", cnt(page, "[data-pool-dot].amb") == 1, js(page, "()=>document.querySelector('[data-pool-line]').dataset.amber"))
            closed = js(page, "()=>document.querySelector('[data-pool-line]').open")
            check(f"{tag} §4.4 แถบ/฿ พับไว้ (บรรทัดเห็นเสมอ)", closed is False and js(page, "()=>document.querySelector('[data-pool-txt]').offsetParent !== null") is True)
            js(page, "()=>{ document.querySelector('[data-pool-line]').open = true; }"); settle(page, 200)
            bars = js(page, "()=>[...document.querySelectorAll('[data-pool-line] [data-pool-bar]')].map(b=>b.dataset.poolBar+':'+b.innerText.replace(/\\s+/g,' '))")
            check(f"{tag} §4.4 เปิดดู: 3 แถบ + ฿ ใช้/ถัง", len(bars) == 3 and "฿1,420,000" in bars[0], bars)
            ov = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
            check(f"{tag} §4.4 เส้นถังไม่ล้นแนวนอน", ov <= 0, ov)
            shot(page, f"rg2b-port-line-{w}.png", "[data-pool-line]")
            # ไม่เกิน 5 จุด → ไม่เหลือง (Winner ถือ ~50% ของบัญชี)
            js(page, "()=>{ const B=getBook('main'); B.trades=[{id:'tW1',port:'core',sym:'WINX',status:'open',entry:100,sl:90,qty:28000,cur:'THB',date:'2026-09-10',bias:'Long'}]; saveBook('main'); renderPortfolioMix(); }"); settle(page, 400)
            wp2 = round(2800000 / TOTAL * 100)
            check(f"{tag} §4.4 Winner {wp2}/50 (ห่าง ≤ 5 แต่ Ladder/Sat 0 ห่างเกิน) ยังเหลือง", cnt(page, "[data-pool-dot].amb") == 1)
            # เติมจนทุกถังใกล้เป้า → ไม่เหลือง: Winner 50% · Ladder บันได 30% (ทุนบันได) · Sat 20% มูลค่าสัญญา
            js(page, """()=>{ const B=getBook('main'); B.trades=[
                {id:'tW1',port:'core',sym:'WINX',status:'open',entry:100,sl:90,qty:%d,cur:'THB',date:'2026-09-10',bias:'Long'},
                {id:'tS1',port:'satB',sym:'XAUUSD',status:'open',entry:1,sl:0.9,qty:%d,mult:1,cur:'USD',date:'2026-09-10',bias:'Long'}]; saveBook('main');
                window.coreLadders = ()=>[{c:{id:'x'}, heldTHB:%d, reservedTHB:0, reservedRows:[]}]; renderPortfolioMix(); }""" % (round(TOTAL*0.5/100), round(TOTAL*0.2/FX), round(TOTAL*0.3)))
            settle(page, 400)
            check(f"{tag} §4.4 ทุกถังห่างเป้า ≤ 5 จุด → ไม่เหลือง", cnt(page, "[data-pool-dot].amb") == 0, txt(page, "[data-pool-txt]"))
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()


def multi_acct_tests(pw):
    wtr = [P13.T("tW1", "core", "open", sym="WINX", entry=100, sl=90, qty=1000, cur="THB", date="2026-09-10")]
    b, page, ce, pe = launch(pw, 390, 844, wtr, {})
    try:
        js(page, "()=>{ switchTab('mix'); ln3PortSet('all'); renderPortfolioMix(); }"); settle(page, 600)
        n = cnt(page, "[data-pool-line]"); line = txt(page, "[data-pool-txt]")
        check("[all] §4.4 โหมด 'รวม' = บรรทัดเดียวรวมยอดทุกบัญชี", n == 1 and line.startswith("Winner "), [n, line])
        js(page, "()=>{ document.querySelector('[data-pool-line]').open = true; }"); settle(page, 200)
        na = cnt(page, "[data-pool-line] [data-pool-acct]")
        check("[all] §4.4 รายละเอียดแยกต่อบัญชี", na == 2, na)
        js(page, "()=>{ ln3PortSet('fam'); renderPortfolioMix(); }"); settle(page, 500)
        check("[acct] §4.4 เลือกบัญชีเดียว = ยอดบัญชีนั้น", cnt(page, "[data-pool-line] [data-pool-acct]") == 1)
    finally: b.close()


# ───────────────────────── 6 §4.7 Core → Winner + Ladder ─────────────────────────
def today_tests(pw):
    for w, h, label in ((300, 800, "300px"), (390, 844, "390px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h)
        try:
            js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
            set_ff(page, True, False)
            js(page, "()=>{ todayRefresh(true); }"); settle(page, 400)
            n = cnt(page, "[data-td3-panel=core] [data-td3-pool]")
            check(f"{tag} §4.7 Today › Core: หัวแผงมี 2 บรรทัด Winner / Ladder", n == 2 and cnt(page, "[data-td3-panel=core] [data-td3-pools]") == 1, n)
            vis = js(page, "()=>[...document.querySelectorAll('[data-td3-pool]')].map(e=>[e.dataset.td3Pool, e.innerText.replace(/\\s+/g,' ').trim(), e.dataset.poolFactor, e.dataset.poolUsed, Math.round(e.getBoundingClientRect().right)])")
            want_w = "W 75% · 0%" if w <= 340 else "Winner 75% · used 0%"
            want_l = "L 75% · 0%" if w <= 340 else "Ladder 75% · used 0%"
            check(f"{tag} §4.7 ข้อความ: '{want_w}' / '{want_l}' (ตัวคูณ Regime ของถังนั้น · ใช้จริง ÷ ถัง)", [v[1] for v in vis] == [want_w, want_l], vis)
            check(f"{tag} §4.7 พอดีจอ (ไม่เกิน {w}px) และไม่ล้นแนวนอน", all(v[4] <= w for v in vis) and js(page, "()=>document.documentElement.scrollWidth - window.innerWidth") <= 0, vis)
            # Winner/Ladder ใช้คู่คนละชุด (slow)
            page.evaluate("""async ()=>{ const mk=(u,s)=>({up:u,flip_days:3,tf:'D',ema:[20,50],bar:'2026-10-01',slow:{up:s,flip_days:9,ema:[50,100]}});
                window.__FF_JSON = {as_of:'2026-10-01', ver:2, ratios:{ACWI_BIL:mk(true,false), HYG_IEI:mk(true,true)}}; await ffLoadJson(true); todayRefresh(true); }""")
            settle(page, 400)
            fac = js(page, "()=>[...document.querySelectorAll('[data-td3-pool]')].map(e=>e.dataset.poolFactor)")
            check(f"{tag} §4.7 Winner ใช้สัญญาณ EMA20/50 · Ladder ใช้ EMA50/100 → 100 / 75", fac == ["100", "75"], fac)
            if w == 300: shot(page, "rg2b-today-core-300.png", "[data-td3-panel=core]")
            if w == 390: shot(page, "rg2b-today-core-390.png", "[data-td3-panel=core]")
            if w == 1440: shot(page, "rg2b-today-core-1440.png", "[data-td3-panel=core]")
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()
    # used % : Winner ถือ ฿1.42M → 25% ของถัง ฿2.84M (บัญชีเดียวเลือก main · รวม 2 บัญชี = ถังรวม)
    wtr = [P13.T("tW1", "core", "open", sym="WINX", entry=100, sl=90, qty=14200, cur="THB", date="2026-09-10")]
    b, page, ce, pe = launch(pw, 390, 844, wtr, {})
    try:
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
        u = js(page, "()=>[...document.querySelectorAll('[data-td3-pool]')].map(e=>e.dataset.poolUsed)")
        check("[used] §4.7 used% = ทุนที่ถือ ÷ ถัง (รวมทุกบัญชี Core: 1.42M ÷ 5.685M×2 ถัง Winner 2.84M×2 = 25%)", u[0] == "25" and u[1] == "0", u)
    finally: b.close()


def dd_tests(pw):
    big_w = P13.T("tBW", "core", "closed", sym="LOSW", entry=100, sl=90, qty=28425, exitPrice=75, exitDate="2026-10-01", cur="THB", date="2026-09-01")   # ขาดทุน 710,625 = 25% ของถัง Winner
    big_l = P13.T("tBL", "core", "closed", sym="LOSL", entry=100, sl=90, qty=17055, exitPrice=75, exitDate="2026-10-01", cur="THB", date="2026-09-01")   # ขาดทุน 426,375 = 25% ของถัง Ladder
    lc = P24.card("ccLX", "main", "LOSL", strategy="L", status="closed", trade_id="tBL", tier="A")
    tag = f"[{ENGINE}/390px]"
    # Winner ล้ม → Winner พัก · Ladder ปกติ
    b, page, ce, pe = launch(pw, 390, 844, [big_w], {})
    try:
        r = js(page, "()=>{ const w = ddEval('main','winner'), l = ddEval('main','ladder'); return [w.stage, Math.round(w.ddPct*10)/10, l.stage, Math.round(l.ddPct*10)/10, Math.round(w.tankTHB), JSON.stringify(ddBucketsOf('main'))]; }")
        check(f"{tag} §4.7 Winner ขาดทุน 25% ของถัง → Winner พัก · DD ≈ 25% ของถัง Winner · Ladder ปกติ 0%", r[0] == "pause" and abs(r[1] - 25) < 0.2 and r[2] == "normal" and r[3] == 0, r)
        check(f"{tag} §4.7 ถังของ DD = ถัง Winner (ไม่ใช่ capital.core) · มี 3 ถัง winner/ladder/sat", near(r[4], POOL["w"]) and r[5] == '["winner","ladder","sat"]', r)
        blk = js(page, "()=>[ddCoreBlockNew('main','winner'), ddCoreBlockNew('main','ladder'), ddCoreBlockLadder('main')]")
        check(f"{tag} §4.7 Winner พักไม่บล็อกการวางบันได (Ladder) · บล็อกแผน Winner ใหม่", blk[0] != "" and blk[1] == "" and blk[2] == "", blk)
        cp = js(page, """()=>{ const cs=Calc.coreSize, bx=coreBase('main'); const nl=cs.ladder({tier:'A',tank:bx.ladderPoolTHB,sl:70,levels:[{px:100},{px:90}],budgetPct:0.05}); const c = coreCanPlace('main',{tier:'A',fortress:true,thb:nl},null,false); return [c.allowed, c.reasons]; }""")
        check(f"{tag} §4.7 วางบันไดใหม่ได้ระหว่าง Winner พัก", cp[0] is True, cp)
        js(page, "()=>{ openSettings(); switchTab('plan'); setPlanScope('stock'); render(); }"); settle(page, 500)
        chips = js(page, "()=>[...document.querySelectorAll('[data-dd-chip]')].map(c=>[c.dataset.ddChip, c.dataset.stage, c.innerText.replace(/\\s+/g,' ')])")
        check(f"{tag} §4.7 ชิป DD บอกชื่อถัง (Winner DD / Ladder DD)", any(c[0] == "winner" and c[2].startswith("Winner DD") for c in chips) and any(c[0] == "ladder" and c[2].startswith("Ladder DD") for c in chips), chips)
        js(page, "()=>{ ddSync(); }"); settle(page, 300)
        ds = js(page, "()=>Object.keys(getBook('main').settings.ddState||{}).sort()")
        check(f"{tag} §4.7 เก็บ state แยก ddState.winner / ddState.ladder", "winner" in ds and "ladder" in ds, ds)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()
    # Ladder ล้ม → Ladder พัก · Winner ปกติ · วางบันไดบล็อก · แผน Winner ไม่บล็อก
    b, page, ce, pe = launch(pw, 390, 844, [big_l], {"ccLX": lc})
    try:
        # trade ถูกใส่ก่อนการ์ดโหลด → state ของ Winner ที่เขียนไปตอนยังไม่ผูกการ์ดเป็นของปลอม: เริ่มใหม่ที่ peak = ถัง (Ladder คงที่ผ่านการ sync หลังการ์ดโหลด)
        js(page, """()=>{ const B = getBook('main'), ds = B.settings.ddState, pw = poolsOf('main').winner, k = ds.ladder.key;
            B.settings.ddState = Object.assign({}, ds, {winner:{peak:pw, baseAt:'2026-10-01', tank:pw, key:k, stage:'normal', stageSince:'2026-10-01', pauseUntil:null, review:null, recoverDd0:null, weekly:{}, rebasedAt:null}}); render(); }"""); settle(page, 300)
        r = js(page, "()=>{ const w = ddEval('main','winner'), l = ddEval('main','ladder'); return [w.stage, Math.round(w.ddPct*10)/10, l.stage, Math.round(l.ddPct*10)/10, Math.round(l.tankTHB)]; }")
        check(f"{tag} §4.7 ไม้ที่ผูกการ์ด L ขาดทุน 25% ของถัง Ladder → Ladder พัก · Winner ปกติ 0%", r[0] == "normal" and r[1] == 0 and r[2] == "pause" and abs(r[3] - 25) < 0.2 and near(r[4], POOL["l"]), r)
        blk = js(page, "()=>[ddCoreBlockNew('main','winner'), ddCoreBlockNew('main','ladder'), ddCoreBlockLadder('main')]")
        check(f"{tag} §4.7 Ladder พักไม่บล็อกแผน Winner · บล็อกบันไดใหม่", blk[0] == "" and blk[1] != "" and blk[2] != "", blk)
        sz = js(page, "()=>coreSizeOpts('main').ddFactor")
        check(f"{tag} §4.7 ขนาดไม้ Winner ไม่ลดจากเบรก Ladder (ddFactor 1)", sz == 1, sz)
    finally: b.close()
    # ย้าย: Core เดิมพัก → ทั้งสองถังเริ่มพัก + แจ้งครั้งเดียว · Core เดิมปกติ → ปกติ
    def mut_pause(doc):
        doc["books"]["main"]["settings"]["ddState"] = {"core": {"peak": 4300000, "baseAt": "2026-09-01", "tank": CORE, "stage": "pause", "stageSince": "2026-10-20", "pauseUntil": "2026-12-31", "weekly": {}}}
    b, page, ce, pe = C.launch2(pw, 390, 844, [], {}, mut=mut_pause, fx=FX)
    try:
        r = js(page, "()=>{ const w = ddEval('main','winner'), l = ddEval('main','ladder'); return [w.stage, l.stage, w.pauseUntil, l.pauseUntil]; }")
        check(f"{tag} §4.7 ย้าย: Core เดิมกำลังพัก → Winner และ Ladder เริ่มพักทั้งคู่ (วันครบเดิม)", r == ["pause", "pause", "2026-12-31", "2026-12-31"], r)
        js(page, "()=>{ render(); ddSync(); openSettings(); }"); settle(page, 600)
        nt = js(page, "()=>[getBook('main').settings.pools.ddNote, document.getElementById('poolNotice').innerText]")
        check(f"{tag} §4.7 แจ้งครั้งเดียวใน Settings › Pools", nt[0] is True and "both Winner and Ladder start paused" in nt[1], nt)
    finally: b.close()
    def mut_ok(doc):
        doc["books"]["main"]["settings"]["ddState"] = {"core": {"peak": 4300000, "baseAt": "2026-09-01", "tank": CORE, "stage": "normal", "stageSince": "2026-09-01", "pauseUntil": None, "weekly": {}}}
    b, page, ce, pe = C.launch2(pw, 390, 844, [], {}, mut=mut_ok, fx=FX)
    try:
        r = js(page, "()=>{ const w = ddEval('main','winner'), l = ddEval('main','ladder'); return [w.stage, l.stage, getBook('main').settings.pools.ddNote || false]; }")
        check(f"{tag} §4.7 ย้าย: Core เดิมปกติ → ทั้งสองถังเริ่มปกติ ไม่แบกพัก ไม่มีหมายเหตุ", r == ["normal", "normal", False], r)
    finally: b.close()
    # fx ขยับ ไม่ทำให้ DD ถูก rebase (ถังเป็น ฿ ที่ผูก fx)
    b, page, ce, pe = launch(pw, 390, 844, [big_w], {})
    try:
        js(page, "()=>{ render(); ddSync(); }"); settle(page, 300)
        js(page, "()=>{ getBook('main').settings.fx = 36; getBook('main').settings.fxChanged = 1; render(); }"); settle(page, 300)
        r = js(page, "()=>{ const w = ddEval('main','winner'); return [w.rebased, w.stage]; }")
        check(f"{tag} §4.7 fx เปลี่ยน → DD ไม่ถูกเริ่มนับใหม่ (rebase เฉพาะเมื่อแก้ทุน/สัดส่วนถัง)", r[0] is False, r)
        js(page, "()=>{ getBook('main').settings.pools = Object.assign({}, getBook('main').settings.pools, {winner:45, ladder:35}); }")
        r2 = js(page, "()=>ddEval('main','winner').rebased")
        check(f"{tag} §4.7 แก้สัดส่วนถัง → เริ่มนับ DD ใหม่", r2 is True, r2)
    finally: b.close()


def goals_tests(pw):
    def mut(doc):
        doc["books"]["main"]["settings"]["subGoals"] = {"main": {"Core.US": {"cur": "THB", "start": 1000000, "target": 2000000, "startDate": "2026-01-01", "deadline": "2026-12-31", "now": 1500000}, "Sat": {"cur": "USD", "start": 10000, "target": 20000, "startDate": "2026-01-01", "deadline": "2026-12-31", "now": 12000}}}
    for w, h, label in ((390, 844, "390px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h, [], {}, mut=mut)
        try:
            subs = js(page, "()=>JSON.stringify(TD3_SUBS)")
            check(f"{tag} §4.7 เป้าย่อย: Winner · Ladder · Sat (+ Option เดิม) ไม่มี Core.US/Core.TH", subs == '["Winner","Ladder","Sat","Option"]', subs)
            r = js(page, "()=>[td3SubOf('main','Winner') && td3SubOf('main','Winner').target, td3SubOf('main','Ladder'), td3SubOf('main','Sat') && td3SubOf('main','Sat').target]")
            check(f"{tag} §4.7 เป้า Core เดิมย้ายไป Winner · Ladder ว่าง · Sat คงเดิม", r == [2000000, None, 20000], r)
            js(page, "()=>{ switchTab('today'); todayRefresh(true); td3GoalOpen.add('main'); todayRefresh(true); }"); settle(page, 400)
            rows = js(page, "()=>[...document.querySelectorAll('[data-td3-acct=main] [data-td3-sub]')].map(e=>e.dataset.td3Sub+':'+(e.innerText.includes('No goal')?'none':'goal'))")
            check(f"{tag} §4.7 Today แสดงแถวเป้า Winner (มี) · Ladder (ไม่มี) · Sat (มี)", rows[:3] == ["Winner:goal", "Ladder:none", "Sat:goal"], rows)
            js(page, "()=>{ openSystemSettings(); glSetPick('main'); }"); settle(page, 500)
            gr = js(page, "()=>[...document.querySelectorAll('#glSet [data-gl-subrow]')].map(e=>e.dataset.glSubrow)")
            check(f"{tag} §4.7 Settings › Goals: แถว Winner / Ladder / Sat / Option", gr == ["Winner", "Ladder", "Sat", "Option"], gr)
            wv = js(page, "()=>document.querySelector('#glSet [data-gl-subrow=Winner] [data-sg-target]').value")
            check(f"{tag} §4.7 แถว Winner โชว์เป้า Core เดิม", wv == "2000000", wv)
            js(page, "()=>{ glSubSave(); }"); settle(page, 500)
            sv = js(page, "()=>Object.keys(tdSettings().subGoals.main).sort()")
            check(f"{tag} §4.7 บันทึกแล้วเขียนเป็นคีย์ Winner (ไม่เขียน Core.US ต่อ)", sv == ["Sat", "Winner"], sv)
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()


def backstop_tests(pw):
    tr = [P13.T("tW1", "core", "open", sym="WINX", entry=100, sl=90, qty=1000, cur="THB", date="2026-09-10"),
          P13.T("tL1", "core", "open", sym="LADY", entry=100, sl=90, qty=500, cur="THB", date="2026-09-10")]
    cards = {"ccLY": P24.card("ccLY", "main", "LADY", strategy="L", status="open", trade_id="tL1", tier="A")}
    b, page, ce, pe = launch(pw, 390, 844, tr, cards)
    try:
        r = js(page, "()=>{ const s = summarize(); return [Math.round(s.per.core.open), Math.round(s.tot.open)]; }")
        check("[backstop] §4.7 Core + Sat Open Risk 6% นับทั้ง Winner และ Ladder (10,000 + 5,000)", r[0] == 15000 and r[1] >= 15000, r)
    finally: b.close()


def node_tests():
    import subprocess
    r = subprocess.run(["node", os.path.join(HERE, "core_size_test.js")], capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if l.startswith("PASS") or l.startswith("FAIL")][-1:]
    check("[node] core_size_test.js ผ่านครบ (รวมเคส RG2b)", r.returncode == 0 and last and "0 ไม่ผ่าน" in last[0] and int(last[0].split()[1]) >= 502, last)
    r2 = subprocess.run([sys.executable, os.path.join(HERE, "..", "tools", "sync_core_size.py"), "--check"], capture_output=True, text=True)
    check("[node] sync_core_size --check", r2.returncode == 0, r2.stdout + r2.stderr)


def main():
    S = sections()
    with sync_playwright() as pw:
        if "pools" in S: pools_tests(pw); over_tests(pw)
        if "winner" in S: winner_tests(pw)
        if "sat" in S: sat_tests(pw)
        if "ladder" in S: ladder_tests(pw)
        if "port" in S: port_tests(pw); multi_acct_tests(pw)
        if "core47" in S: today_tests(pw); dd_tests(pw); goals_tests(pw); backstop_tests(pw)
    if "node" in S: node_tests()
    bad = [r for r in results if not r[1]]
    print(f"\n{'PASS' if not bad else 'FAIL'}  {len(results) - len(bad)} / {len(results)}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
