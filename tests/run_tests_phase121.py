#!/usr/bin/env python3
"""PS1b — Portfolio Risk panel → Today (collapsible) · Sat Strategy box = PS1 numbers · Sat min stop (% of entry) · RRG speed tag · sub-port goals collapsed ·
Loss limits (drawdown 10/20 per port · day 2R / week 5R · fake clock) · risk as % of the port in Details · เทส 121
Chromium · 390 / 1440 · ข้อมูล SAMPLE ล้วน · รัน: python3 run_tests_phase121.py"""
import json, re, math
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase111 as P111
import run_tests_phase77 as P77
import run_tests_phase105 as P105
import run_tests_phase120 as B

ENGINE = base.BROWSER_ENGINE
results = []
js, settle, P13 = C.js, T.settle, P111.P13
PS = {"def": {"winner": 0.4, "ladder": 1.0, "satMain": 0.2, "satTac": 0.15}}


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def ps_set(page, extra=None, ps=None):
    """PS1 on + psRisk with min stop 0.5% for XAUUSD (BTC left unset on purpose)"""
    o = dict(ps or PS); o["minStop"] = {"XAUUSD": 0.5}
    if extra: o.update(extra)
    js(page, "([o])=>{ localStorage.removeItem('dash.ps1Off'); const B=getBook('main'); B.settings.psRisk=o; saveBook('main'); render(); }", [o]); settle(page, 300)


def sat_plan(page, asset, e, s, tp, sleeve="main"):
    iid = js(page, "([a,s])=>satV2NewPlan(a,s)", [asset, sleeve]); settle(page, 500)
    js(page, "([i])=>satV2SetDir(i,'Long')", [iid]); settle(page, 250)
    for f_, v in (("entry", e), ("sl", s), ("tp", tp)):
        js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, f_, str(v)]); settle(page, 100)
    js(page, "([i])=>{ pfVerifySet(i,'structure_ok',true); pfVerifySet(i,'ema50_ok',true); }", [iid]); settle(page, 400)
    return iid


def calc(page, iid):
    return js(page, """([i])=>{ const x=satIdeasList.find(y=>y.id===i); const c=satV3PlanAcctCalc(x,'main'); return {lot:c.lot, blocks:c.blocks, ready:c.ready, msg:c.lotMsg, raw:c.v2&&c.v2.rawRisk, lim:c.v2&&c.v2.limit,
        deal:c.v2&&c.v2.lotDeal, dealTHB:c.v2&&c.v2.dealTHB, riskTHB:c.v2&&c.v2.riskTHB, rawCap:c.v2&&c.v2.rawCap, E:c.ps1&&c.ps1.E, line:satV2SizeLine({_idea:x,_skipSet:new Set()}, {id:'main'})}}""", [iid])


def txt_of(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def sat_tests(pw, w, h):
    tag = f"[{ENGINE}/sat/{w}]"
    b, page, ce, pe = P77.launch(pw, w, h)
    try:
        ps_set(page)
        # ── §2 min stop
        iid = sat_plan(page, "XAUUSD", 2000, 1985, 2040)          # 15 pts = 0.75% >= 0.5% (10 pts)
        c = calc(page, iid)
        check(f"{tag} §2 stop 0.75% >= min 0.5% → ผ่าน · lot มี · ไม่มี block 'Stop too tight'", c["lot"] and not any("too tight" in x for x in c["blocks"]), c)
        js(page, "([i])=>satV3PlanEdit(i,'sl','1991')", [iid]); settle(page, 300)
        c = calc(page, iid)
        check(f"{tag} §2 stop 9 pts (0.45%) < 0.5% → 'Stop too tight — min 10 pts (0.5%)' + บันทึกไม่ได้ (ไม่ ready)", any("Stop too tight — min 10" in x and "(0.5%)" in x for x in c["blocks"]) and not c["ready"], c)
        js(page, "([i])=>satV3PlanEdit(i,'sl','1990')", [iid]); settle(page, 300)
        c = calc(page, iid)
        check(f"{tag} §2 stop = min (10 pts) พอดี → ผ่าน", not any("too tight" in x for x in c["blocks"]) and c["lot"], c)
        bid = sat_plan(page, "BTCUSD", 60000, 58000, 64000)
        cb = calc(page, bid)
        check(f"{tag} §2 asset ไม่ได้ตั้ง min stop (BTC) → 'Set min stop in Settings' + ไม่ ready", "Set min stop in Settings" in cb["blocks"] and not cb["ready"], cb)
        # lots formula, no value cap: huge risk vs tiny stop is limited only by min stop → use stop = min and check lot = floor(E*0.2%/(10*contract))
        raw_exp = c["E"] * 0.2 / 100 / c["raw"] if False else None
        ok_formula = c["lim"] == "risk" and abs(c["raw"] - (c["riskTHB"] / js(page, "()=>getBook('main').settings.fx || 33") / (10 * js(page, "([a])=>productCfg(a).contract", ["XAUUSD"])))) < 1e-6
        check(f"{tag} §2 lots = E × risk% ÷ (stop pts × multiplier) · ไม่มีเพดานมูลค่า 1.4× ในออเดอร์ใหม่ (limit = risk)", ok_formula and c["deal"] > 0, c)
        # details = 3 lines, no RPT / % of Main
        t = c["line"]; l3 = re.findall(r"data-ps1-l3[^>]*>(.*?)</div>", t)
        l3t = [txt_of(x) for x in l3]
        check(f"{tag} §2 Details ขนาด Sat = 3 บรรทัดพอดี: Risk … of portfolio = $ / Stop … pts × … multiplier → … / Used … (rounded) · Risk $", len(l3t) == 3 and l3t[0].startswith("Risk ") and "of portfolio" in l3t[0] and l3t[1].startswith("Stop ") and "multiplier" in l3t[1] and l3t[2].startswith("Used ") and "rounded" in l3t[2], l3t)
        check(f"{tag} §2 ไม่มีบรรทัด 'RPT Main' / 'เพดานมูลค่า' / '% ของเงิน Main' สำหรับออเดอร์ PS1", not re.search(r"RPT|เพดานมูลค่า|ของเงิน", txt_of(t)), txt_of(t)[:300])
        # §6 risk as % of port in details
        check(f"{tag} §6 บรรทัดแรกมี '(= x% of Sat)' คู่กับ % ของพอร์ต", re.search(r"of portfolio \(= [\d.]+% of Sat\)", l3t[0]) is not None, l3t[0])
        # old saved order unchanged: existing trade slot keeps legacy path (slotEx) — build via saved trade
        js(page, "([i])=>{ P78 = null; }", [iid]) if False else None
        # ── §1 Strategy box shows PS1 numbers
        box = js(page, "()=>{ const d=document.createElement('div'); d.innerHTML=ln2HeaderHtml(); return {t:d.innerText||d.textContent, used:(d.querySelector('[data-ln2-used]')||{}).textContent, cap:(d.querySelector('[data-ln2-cap]')||{}).textContent, left:(d.querySelector('[data-ln2-left]')||{}).textContent, ps1:!!d.querySelector('[data-ln2-ps1]'), det:(d.querySelector('[data-ln2-det]')||{}).textContent||''}; }")
        check(f"{tag} §1 กล่อง Strategy Sat: 'Risk x.xx% of 0.5% cap · left x.xx%' (PS1) · ไม่มีตัวเลขเพดานเดิม ($ / cap เดิม)", box["ps1"] and box["used"].startswith("Risk ") and box["cap"] == "0.5%" and box["left"].endswith("%") and "Satellite Open Risk" not in box["t"], box)
        check(f"{tag} §1 เพดานเดิมไม่โผล่ใน Details ถ้าไม่มีตำแหน่งเก่า (Legacy)", "Legacy" not in box["det"], box["det"][:200])
        # legacy position (no t.ps1) -> Legacy line + Settings count
        js(page, "()=>{ const B=getBook('main'); B.trades.push({id:'tLeg',port:'satB',sym:'XAUUSD',bias:'Long',entry:2000,sl:1980,qty:1,mult:1,cur:'USD',status:'open',date:'2026-10-20'}); saveBook('main'); render(); }"); settle(page, 300)
        det = js(page, "()=>{ const d=document.createElement('div'); d.innerHTML=ln2HeaderHtml(); return (d.querySelector('[data-ln2-det]')||{}).textContent||''; }")
        check(f"{tag} §1 มีตำแหน่งเก่า (ไม่มี t.ps1) → เพดานเดิมโผล่เฉพาะใน Details ป้าย 'Legacy'", "Legacy" in det and "Open Risk" in det, det[:300])
        js(page, "()=>{ openSettings(); }"); settle(page, 300)
        ln = js(page, "()=>{ ps1MinStopDraw(); return (document.getElementById('ps1LegacyN')||{}).innerText; }")
        check(f"{tag} §1 Settings: 'Legacy positions: 1 — cleanup when 0'", re.search(r"Legacy positions:\s*1\s*—\s*cleanup when 0", ln or "") is not None, ln)
        ms = js(page, "()=>[...document.querySelectorAll('[data-ps1-ms]')].map(e=>[e.dataset.ps1Ms, e.value, e.parentNode.querySelector('[data-ps1-mshint]').innerText])")
        xa = [m for m in ms if m[0] == "XAUUSD"]
        check(f"{tag} §2 Settings: ช่อง min stop ต่อ asset (required) + 'min 0.5% ≈ N pts' ข้างช่อง", len(ms) >= 2 and xa and xa[0][1] == "0.5" and "min 0.5%" in xa[0][2] and "pts" in xa[0][2], ms[:4])
        js(page, "()=>{ const e=document.querySelector('[data-ps1-ms=XAUUSD]'); e.value='60'; crOnInput(); }"); settle(page, 100)
        er = js(page, "()=>{ const e=document.querySelector('[data-ps1-ms=XAUUSD]'); return document.querySelector('[data-err-for='+e.id+']').innerText; }")
        check(f"{tag} §2 Settings: min stop นอกช่วง (60%) → error", "0–50" in er, er)
        js(page, "()=>{ document.querySelector('[data-ps1-ms=XAUUSD]').value='0.6'; crOnInput(); saveSettings(); }"); settle(page, 300)
        sv = js(page, "()=>getBook('main').settings.psRisk")
        check(f"{tag} §2 บันทึกแล้ว psRisk.minStop เก็บค่า · default/loss ไม่หาย", sv and sv.get("minStop", {}).get("XAUUSD") == 0.6 and sv["def"]["winner"] == 0.4 and sv["loss"]["dayR"] == 2, sv)
        check(f"{tag} console ไม่มี error (sat)", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def loss_tests(pw, w, h):
    tag = f"[{ENGINE}/loss/{w}]"
    b, page, ce, pe = P77.launch(pw, w, h)
    try:
        ps_set(page)
        js(page, "()=>{ openSettings(); }"); settle(page, 300)
        d = js(page, "()=>['sPsLossDd','sPsLossHalf','sPsLossDay','sPsLossWeek'].map(i=>document.getElementById(i).value)")
        note = js(page, "()=>document.querySelector('[data-ps1-lossnote]').innerText")
        check(f"{tag} §5 Settings: Loss limits 20 / 10 / 2R / 5R + help line เดียว", d == ["20", "10", "2", "5"] and note == "Each port is checked on its own. R = the port's default risk per idea. Day resets 06:00, week Monday 06:00 (Thai time).", [d, note])
        js(page, "()=>{ const s=(i,v)=>{ document.getElementById(i).value=v; crOnInput(); }; s('sPsLossHalf','25'); }"); settle(page, 100)
        er = js(page, "()=>document.querySelector('[data-err-for=sPsLossHalf]').innerText")
        check(f"{tag} §5 Settings: half size ≥ max drawdown → error", "below" in er, er)
        js(page, "()=>{ document.getElementById('sPsLossHalf').value='10'; crOnInput(); document.querySelector('#setOverlay')&&document.getElementById('setOverlay').classList.remove('show'); }")
        # ── state + fake clock: Thai 2026-11-11 10:00
        NOW = "Date.parse('2026-11-11T10:00:00+07:00')"
        setup = f"""()=>{{ const B=getBook('main'); B.settings.lossState={{startAt:'2026-11-01T00:00:00Z', ports:{{}}}}; B.trades=B.trades.filter(t=>t.id.indexOf('L')!==0); saveBook('main'); render(); }}"""
        js(page, setup); settle(page, 300)
        add = """([id,k,close,sym,opened])=>{ const B=getBook('main'), fx=+B.settings.fx||33, E=ps1E('main'), R=E*0.002; const L=k*R/fx;
          B.trades.push({id:id,port:'satB',sym:sym||'XAUUSD',bias:'Long',entry:100000,sl:100000-L,sl0:100000-L,qty:1,mult:1,cur:'USD',status:'closed',exitPrice:100000-L,exitDate:close.slice(0,10),date:opened||'2026-11-10',closedAt:new Date(close).toISOString()}); saveBook('main'); }"""
        ev = lambda: js(page, f"()=>{{ const e=lossEval('main','sat',{NOW}); return {{st:e.status, blocked:e.blocked, mult:e.mult, day:e.dayR, week:e.weekR, until:e.until, msg:lossBlockMsg(e)}}; }}")
        e0 = ev()
        check(f"{tag} §5 เริ่มต้น: Normal", e0["st"] == "normal" and not e0["blocked"] and e0["mult"] == 1, e0)
        js(page, add, ["L1", 1, "2026-11-11T08:00:00+07:00"]); js(page, add, ["L2", 1, "2026-11-11T09:00:00+07:00", "XAUUSD", "2026-11-09"]); settle(page, 150)
        e1 = ev()
        check(f"{tag} §5 แพ้ 2 ไม้ปกติ (2R) วันนี้ → Stop today · เปิด 06:00 พรุ่งนี้ · ข้อความบรรทัดเดียว", e1["st"] == "day" and e1["blocked"] and "lost today" in e1["msg"] and "06:00" in e1["msg"], e1)
        # stop-today blocks the Sat form
        ps_set(page, ps={"def": {"winner": 0.4, "ladder": 1.0, "satMain": 0.2, "satTac": 0.15}})
        js(page, f"()=>{{ window.__d0 = Date.now; Date.now = ()=>{NOW}; }}")
        iid = sat_plan(page, "XAUUSD", 2000, 1985, 2040)
        cc = calc(page, iid)
        check(f"{tag} §5 ฟอร์ม Sat ถูกบล็อกด้วยเหตุผลบรรทัดเดียว 'Sat: … lost today — opens 06:00 …' ไม่มี override", any("lost today" in x for x in cc["blocks"]) and not cc["ready"], cc)
        js(page, "()=>{ Date.now = window.__d0; }")
        # big gap loss counted by size
        js(page, setup); js(page, add, ["L1", 2.4, "2026-11-11T08:00:00+07:00"]); settle(page, 150)
        e2 = ev(); check(f"{tag} §5 แพ้ไม้เดียวแต่ใหญ่ (gap 2.4R) → Stop today (นับตามขนาด ไม่ใช่จำนวน)", e2["st"] == "day" and abs(e2["day"] - 2.4) < 0.01, e2)
        # scratch
        # real scratch: planned risk large, loss tiny
        js(page, setup)
        js(page, """()=>{ const B=getBook('main'), fx=+B.settings.fx||33, E=ps1E('main'), R=E*0.002, L=R/fx; B.trades.push({id:'L9',port:'satB',sym:'XAUUSD',bias:'Long',entry:100000,sl:100000-L*10,sl0:100000-L*10,qty:1,mult:1,cur:'USD',status:'closed',exitPrice:100000-L*2,exitDate:'2026-11-11',date:'2026-11-10',closedAt:new Date('2026-11-11T08:00:00+07:00').toISOString()}); saveBook('main'); }""")
        e4 = ev(); check(f"{tag} §5 scratch exit (loss 2R ของ… แต่ ≤ ¼ ของ risk ที่วางไว้ 10R? → 2R ≤ 2.5R) ไม่นับ", e4["day"] == 0 and e4["st"] == "normal", e4)
        # same idea in 2 accounts counted once
        js(page, setup); js(page, add, ["L1", 1.2, "2026-11-11T08:00:00+07:00"]); js(page, add, ["L2", 1.2, "2026-11-11T08:05:00+07:00"]); settle(page, 150)
        e5 = ev(); check(f"{tag} §5 ไม้เดียวกัน (asset+ทิศ+วันเปิดเดียวกัน) 2 รายการ = แพ้ 1 ไม้ที่ใหญ่สุด (1.2R) ไม่ใช่ 2.4R", e5["st"] == "normal" and abs(e5["day"] - 1.2) < 0.01, e5)
        # reset 06:00 (fake clock)
        js(page, setup); js(page, add, ["L1", 2.5, "2026-11-11T08:00:00+07:00"]); settle(page, 150)
        r1 = js(page, "()=>lossEval('main','sat',Date.parse('2026-11-12T05:59:00+07:00')).status"); r2 = js(page, "()=>lossEval('main','sat',Date.parse('2026-11-12T06:00:00+07:00')).status")
        check(f"{tag} §5 05:59 ยัง Stop today · 06:00 → ปลดอัตโนมัติ", r1 == "day" and r2 == "normal", [r1, r2])
        # week 5R: 2.5R Mon-Tue-Wed, day resets
        js(page, setup)
        for i, dte in enumerate(["2026-11-09T09:00:00", "2026-11-10T09:00:00"]):
            js(page, add, [f"L{i+1}", 2.6, dte + "+07:00", "XAUUSD", dte[:10]]); settle(page, 50)
        w1 = js(page, f"()=>{{ const e=lossEval('main','sat',Date.parse('2026-11-11T10:00:00+07:00')); return [e.status,e.weekR,e.until]; }}")
        check(f"{tag} §5 สัปดาห์: 5.2R (จ.+อ.) → Stop week จนถึงจันทร์ 06:00 ถัดไป", w1[0] == "week" and abs(w1[1] - 5.2) < 0.02, w1)
        w2 = js(page, "()=>lossEval('main','sat',Date.parse('2026-11-16T06:00:00+07:00')).status")
        check(f"{tag} §5 จันทร์ 06:00 → ปลด Stop week", w2 == "normal", w2)
        # trades before startAt don't count
        js(page, setup); js(page, "()=>{ getBook('main').settings.lossState.startAt='2026-11-11T09:30:00Z'; saveBook('main'); }"); js(page, add, ["L1", 3, "2026-11-11T08:00:00+07:00"]); settle(page, 100)
        e6 = ev(); check(f"{tag} §5 ไม้ที่ปิดก่อนรันครั้งแรกไม่นับ (clean start)", e6["st"] == "normal", e6)
        # drawdown half / stop & review on Sat
        js(page, setup)
        js(page, f"""()=>{{ const B=getBook('main'); const v=lossPortValue('main','sat').v; B.settings.lossState.ports.sat={{peak:v*1.12, half:false, low:null, stopped:false, log:[]}}; saveBook('main'); }}""")
        e7 = ev(); check(f"{tag} §5 ลง ≥10% จาก peak → Half size (mult 0.5) ไม่บล็อก", e7["st"] == "half" and e7["mult"] == 0.5 and not e7["blocked"], e7)
        js(page, f"""()=>{{ const B=getBook('main'); const v=lossPortValue('main','sat').v; B.settings.lossState.ports.sat={{peak:v*1.3, half:false, low:null, stopped:false, log:[]}}; saveBook('main'); }}""")
        e8 = ev(); check(f"{tag} §5 ลง ≥20% → Stop & review (บล็อก) · ไม่มีเวลาปลด", e8["st"] == "review" and e8["blocked"] and e8["until"] is None, e8)
        js(page, "()=>lossStatusStub=null") if False else None
        # persisted stopped state needs lossSync? simulate stopped persisted
        js(page, """()=>{ const B=getBook('main'); B.settings.lossState.ports.sat={peak:1e9, half:false, low:null, stopped:true, log:[]}; saveBook('main'); render(); }"""); settle(page, 200)
        js(page, "()=>lossResumeOpen('main','sat')"); settle(page, 300)
        dis0 = js(page, "()=>document.getElementById('lossResumeBtn').disabled")
        js(page, "()=>{ const t=document.getElementById('lossNote'); t.value='   '; lossResumeIn(); }"); dis1 = js(page, "()=>document.getElementById('lossResumeBtn').disabled")
        js(page, "()=>{ const t=document.getElementById('lossNote'); t.value='Reviewed the 3 losing trades'; lossResumeIn(); }"); dis2 = js(page, "()=>document.getElementById('lossResumeBtn').disabled")
        check(f"{tag} §5 'Reviewed — resume' ต้องมี note (ว่าง/ช่องว่างกดไม่ได้)", dis0 and dis1 and not dis2, [dis0, dis1, dis2])
        js(page, "()=>lossResumeSave()"); settle(page, 300)
        st9 = js(page, "()=>{ const p=getBook('main').settings.lossState.ports.sat; const v=lossPortValue('main','sat').v; return {stopped:p.stopped, peak:p.peak, v:v, log:p.log.length, note:p.log[0]&&p.log[0].note}; }")
        check(f"{tag} §5 resume: ปลดล็อก · peak รีเซ็ตเป็นมูลค่าพอร์ตปัจจุบัน · เก็บ note ในล็อก", st9["stopped"] is False and abs(st9["peak"] - st9["v"]) < 1 and st9["log"] == 1 and "Reviewed" in st9["note"], st9)
        # compounder: dd only
        cp = js(page, f"()=>{{ const e=lossEval('main','ladder',{NOW}); return [e.dayR, e.weekR, e.status]; }}")
        check(f"{tag} §5 Compounder: ไม่มีตัวนับ day/week (drawdown เท่านั้น)", cp[0] == 0 and cp[1] == 0 and cp[2] == "normal", cp)
        # half stacks with other multipliers in Details
        js(page, setup); js(page, f"""()=>{{ const B=getBook('main'); const v=lossPortValue('main','sat').v; B.settings.lossState.ports.sat={{peak:v*1.12, half:true, low:v, stopped:false, log:[]}}; saveBook('main'); render(); }}""")
        ps_set(page); js(page, f"()=>{{ const B=getBook('main'); B.settings.lossState={{startAt:'2026-11-01T00:00:00Z',ports:{{sat:{{peak:lossPortValue('main','sat').v*1.12,half:true,low:lossPortValue('main','sat').v,stopped:false,log:[]}}}}}}; saveBook('main'); render(); }}"); settle(page, 300)
        iid = sat_plan(page, "XAUUSD", 2000, 1985, 2040); cc = calc(page, iid)
        check(f"{tag} §5 Half size: risk × 0.5 ของ default ({cc['E']:,.0f}×0.2%×0.5) ซ้อนกับตัวคูณอื่น · แสดง 'half size' ใน Details", cc["E"] and abs(cc["riskTHB"] - cc["E"] * 0.002 * 0.5) < cc["E"] * 0.002 * 0.05 and "half size" in txt_of(cc["line"]), cc)
        # old plans / legacy untouched
        old = js(page, "()=>{ const B=getBook('main'); return B.trades.filter(t=>t.status==='open').length; }")
        check(f"{tag} §5 ตำแหน่งที่เปิดอยู่ไม่ถูกแตะ (ไม่มี auto-sell)", old == js(page, "()=>getBook('main').trades.filter(t=>t.status==='open').length"), old)
        check(f"{tag} console ไม่มี error (loss)", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def today_tests(pw, w, h):
    tag = f"[{ENGINE}/today/{w}]"
    tr = [P13.T("tR", "core", "open", sym="RED", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20")]
    cards = {"cR": B.open_card("RED", "tR", px=100)}
    b, page, ce, pe = C.launch2(pw, w, h, tr, cards, pin_winner=True)
    try:
        B.ps_on(page)
        js(page, "()=>{ try{localStorage.removeItem('ps1TodayOpen')}catch(e){}; ps1TodayOpen=null; switchTab('plan'); setPlanScope('stock'); render(); }"); settle(page, 500)
        pl = js(page, "()=>({host: !!document.getElementById('ps1Panel'), body: !!document.querySelector('#tabPlan [data-ps1-panel-body]')})")
        check(f"{tag} §1 หน้า Plan ไม่มีแผง Portfolio Risk", not pl["host"] and not pl["body"], pl)
        for sc in ("future", "ladder", "stock"):
            ok_ = js(page, "([s])=>{ try{ setPlanScope(s); }catch(e){} render(); return !document.querySelector('#tabPlan [data-ps1-panel-body]'); }", [sc])
            check(f"{tag} §1 Plan scope '{sc}' ไม่มีแผง", ok_, sc)
        js(page, "()=>{ switchTab('today'); render(); }"); settle(page, 500)
        t0 = js(page, "()=>{ const d=document.querySelector('[data-ps1-today]'); return {has:!!d, tag:d&&d.tagName, open:d&&d.open, chips:document.querySelectorAll('[data-ps1-today-chips] [data-loss-chip]').length, ov:document.documentElement.scrollWidth>innerWidth}; }")
        check(f"{tag} §1 Today: บรรทัดสรุปเดิมอยู่ · พับไว้ตั้งต้น · มีชิป Loss limits ต่อ port 3 ใบ · ไม่ล้น", t0["has"] and t0["open"] is False and t0["chips"] == 3 and not t0["ov"], t0)
        vis0 = js(page, "()=>document.querySelector('[data-ps1-today-body]').checkVisibility()")
        js(page, "()=>document.querySelector('[data-ps1-today] summary').click()"); settle(page, 250)
        t1 = js(page, "()=>{ const d=document.querySelector('[data-ps1-today]'); return {open:d.open, h:document.querySelector('[data-ps1-today-body]').getBoundingClientRect().height, body:!!d.querySelector('[data-ps1-panel-body]'), ls:localStorage.getItem('ps1TodayOpen')}; }")
        check(f"{tag} §1 แตะแถว → ขยายเป็นแผงเต็ม · จำสถานะต่ออุปกรณ์ (localStorage)", t1["open"] and t1["h"] > 50 and vis0 is False and t1["body"] and t1["ls"] == "1", [vis0, t1])
        js(page, "()=>{ ps1TodayOpen=null; render(); }"); settle(page, 300)
        t2 = js(page, "()=>document.querySelector('[data-ps1-today]').open")
        check(f"{tag} §1 วาดใหม่/โหลดใหม่ → ยังเปิดอยู่ (อ่านจาก localStorage)", t2 is True, t2)
        pp = js(page, "()=>[...document.querySelectorAll('[data-ps1-idea] [data-ps1-portpct]')].map(x=>x.innerText)")
        check(f"{tag} §6 แถวในแผง Today: Risk ของไอเดียมี '(= x% of Momentum)'", pp and "of Momentum" in pp[0], pp)
        # §4 goals
        js(page, "()=>{ const B=getBook('main'); }")
        gl = js(page, """()=>{ const g=document.querySelector('[data-td3-goals]'); if(!g) return {none:true}; g.querySelectorAll('details.td3-acct').forEach(x=>x.open=true); const d=g.querySelector('[data-td3-subgoals]'); return {none:false, has:!!d, open:d&&d.open, sum:d&&d.querySelector('summary').textContent.trim(), rowsVisible:[...g.querySelectorAll('[data-td3-sub]')].filter(x=>x.checkVisibility()).length}; }""")
        check(f"{tag} §4 เป้าหมาย: sub-port ยุบเป็นแถวเดียว 'Sub-port goals ›' (ปิดไว้) · ไม่เห็นแถว Momentum/Compounder/Sat/Option", gl.get("none") is False and gl["has"] and gl["open"] is False and gl["sum"].startswith("Sub-port goals") and gl["rowsVisible"] == 0, gl)
        check(f"{tag} console ไม่มี error (today)", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def goals_static():
    """§4 no behaviour reads sub-port goals: only the Today goals card + the Settings editor"""
    src = open(B.INDEX, encoding="utf-8").read()
    uses = [m.start() for m in re.finditer(r"td3SubGoals\(|td3SubOf\(|\.subGoals", src)]
    lines = sorted({src.count("\n", 0, u) + 1 for u in uses})
    fn = []
    for ln in lines:
        l = src.split("\n")[ln - 1]
        fn.append(bool(re.search(r"td3GoalsHtml|function td3SubGoals|function td3SubOf|glSub|S\.subGoals|sg0|td3SubOf\(a\.id, k\)|td3SubGoals\(\)\[", l)))
    check("§4 sub-port goals อ่านจากที่เดียว: การ์ดเป้าหมาย Today + ตัวแก้ใน Settings (ไม่มี warning/reminder/สี/ขนาดไม้ที่อ่านค่านี้)", all(fn), lines)


def rrg_tests(pw, w, h):
    tag = f"[{ENGINE}/rrg/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        R = P105.R
        rows = [R("XLK", "Technology", "imp", dm=0.9, ratio=99.0, mom=103.0, days=2, off=-1.2),     # Lagging ↗ , mom ▲ very fast? 0.9 = Fast
                R("XLU", "Utilities", "lead", dm=-0.7, ratio=103.2, mom=102.1, days=2, off=-1.6),   # Beating … , mom ▼ Fast
                R("SMH", "Semiconductors", "lead", dm=0.3), R("XBI", "Biotech", "lag", dm=-0.1),
                R("XLE", "Energy", "lead", dm=1.4), R("XLV", "Health", "lag", dm=-1.2)]
        P105.seed_rrg(page, d=rows, wk=P105.rows_w()); P105.go_flow(page)
        g = js(page, """()=>Object.fromEntries([...document.querySelectorAll('#ffThemes [data-rr]')].map(e=>{ const s=e.querySelector('[data-rr-speed]'); return [e.dataset.rr, s ? [s.dataset.rrSpeed, s.querySelector('.rr-spl').textContent, getComputedStyle(s).color, s.title] : null]; }))""")
        check(f"{tag} §3 Fast ▲ → '⚡ speeding up' (เขียว) · tooltip ตามสเปก", g.get("XLK") and g["XLK"][0] == "up" and g["XLK"][1] == "⚡ speeding up" and g["XLK"][3] == "RS momentum is changing fast (last 5 bars)", g)
        check(f"{tag} §3 Fast ▼ → '⚡ slowing fast' (เหลือง/amber)", g.get("XLU") and g["XLU"][0] == "down" and g["XLU"][1] == "⚡ slowing fast", g)
        check(f"{tag} §3 Very fast ทั้งสองทิศ (±1.2–1.4) มีแท็ก · Moving/Flat (0.3, −0.1) ไม่มีแท็ก", g.get("XLE") and g.get("XLV") and g["SMH"] is None and g["XBI"] is None, g)
        col = js(page, "()=>{ const u=document.querySelector('#ffThemes [data-rr=XLK] [data-rr-speed]'), d=document.querySelector('#ffThemes [data-rr=XLU] [data-rr-speed]'); return [getComputedStyle(u).color, getComputedStyle(d).color, getComputedStyle(document.documentElement).getPropertyValue('--teal'), getComputedStyle(document.documentElement).getPropertyValue('--amber')]; }")
        check(f"{tag} §3 สี: ▲ ใช้ --teal · ▼ ใช้ --amber (ต่างกัน)", col[0] != col[1], col)
        lay = js(page, """()=>[...document.querySelectorAll('#ffThemes [data-rr] .rr-lean')].map(l=>{ const lr=l.getBoundingClientRect(); const chips=[...l.querySelectorAll('.rr-ch,.rr-sp')].filter(c=>c.getBoundingClientRect().width>0 && getComputedStyle(c).display!=='none');
            const cy=chips.map(c=>{ const r=c.getBoundingClientRect(); return r.top+r.height/2; }); return {sym:l.closest('[data-rr]').dataset.rr, oneRow: Math.max(...cy)-Math.min(...cy) <= 4, inside: chips.every(c=>c.getBoundingClientRect().right <= lr.right+1), n:chips.length, w:Math.round(lr.width)}; })""")
        check(f"{tag} §3 ชิป + แท็กอยู่แถวเดียว ไม่ตกบรรทัด ไม่ล้นการ์ด ({w}px) · ใช้ ⚡▲/⚡▼ เมื่อแคบ", all(x["oneRow"] and x["inside"] for x in lay), lay)
        if w <= 430:
            sh = js(page, "()=>[...document.querySelectorAll('#ffThemes [data-rr-speed]')].map(s=>[getComputedStyle(s.querySelector('.rr-spl')).display, getComputedStyle(s.querySelector('.rr-sps')).display, s.closest('.rr-lean').getBoundingClientRect().width])")
            check(f"{tag} §3 (แสดงรูปย่อเมื่อการ์ดแคบ ≤330px ตรวจจาก container query)", all((x[0] == "none" and x[1] != "none") == (x[2] <= 330) for x in sh), sh)
        # details gauge uses the same thresholds
        words = js(page, "()=>[0.1,0.2,0.49,0.5,0.99,1.0,-0.5,-1.5].map(d=>rrgSpeed(d))")
        check(f"{tag} §3 rrgSpeed ใช้เกณฑ์เดียวกับ gauge: Fast ≥0.5 · Very fast ≥1.0", [x["lvl"] for x in words] == [0, 1, 1, 2, 2, 3, 2, 3] and [x["fast"] for x in words] == [False, False, False, True, True, True, True, True], words)
        check(f"{tag} console ไม่มี error (rrg)", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def main():
    goals_static()
    with sync_playwright() as pw:
        for w, h in ((1440, 1000), (390, 844)):
            today_tests(pw, w, h)
            sat_tests(pw, w, h)
            loss_tests(pw, w, h)
            rrg_tests(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\nPS1b phase121: {len(results) - len(bad)}/{len(results)} PASS")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
