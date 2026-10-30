#!/usr/bin/env python3
"""PY1 — เติมไม้ Future (Pyramid) 1 ครั้ง · 50% ของ lot ไม้แรก · เทส 36
mock Firestore · Chromium 1440 + 430 · Bias สัปดาห์ XAUUSD = Long · XM contract 100 / lotStep 0.01 / minLot 0.01 · fx 33
ไม้ 1 ตั้งต้น: Long entry 2400 · SL 2390 · qty 0.40 (main)
ภาพเก็บที่ tests/screenshots/py1-*.png
รัน: python3 run_tests_phase36.py"""
import json, math, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
from run_tests_phase11 import seed_pb, iso, fresh, reset_ideas
from run_tests_phase27 import js, setup_week, push_trade

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []


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


def today(page): return js(page, "()=>thaiToday()")


def clean(page, bias="Long"):
    js(page, "()=>{ closeTradeEdit && closeTradeEdit(); satPyrClose(); }")
    reset_ideas(page)
    js(page, "()=>{ const B=getBook('main'); B.trades=[]; saveBook('main'); }")
    setup_week(page, bias=bias, support=(2400,), resistance=(2520,))


def mk_first(page, tid="t1", bias="Long", entry=2400, sl=2390, qty=0.40, port="satB", status="open", idea=True, **extra):
    """ไม้ 1 + ไอเดีย Sat ที่ผูก (accts.main.trade_id) — แถว Sat แสดงจากไอเดียนี้"""
    kw = dict(id=tid, date=today(page), bias=bias, entry=entry, sl=sl, tp=2460 if bias == "Long" else 2340, qty=qty, port=port, status=status)
    kw.update(extra)
    push_trade(page, **kw)
    if idea:
        page.evaluate("""([tid, bias, entry, sl])=>{ sat7dWrite('satIdeas', 'i_'+tid, {v3:true, asset:'XAUUSD', bias, week:wpWeekKey(), created_at:new Date().toISOString(),
            entry, sl, tp:null, cancel_level:null, conditions:[], planned:true, setups:[], status:'active',
            accts:{main:{trade_id:tid, broker:'XM', lot:0.4, placed:false}}}); }""", [tid, bias, entry, sl])
        page.wait_for_timeout(300)
    js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); page.wait_for_timeout(300)


def tr(page, tid): return js(page, "(i)=>{ const t=getBook('main').trades.find(x=>x.id===i); return t ? JSON.parse(JSON.stringify(t)) : null; }", tid)
def trades_n(page): return js(page, "()=>getBook('main').trades.length")
def set_sl(page, tid, sl): js(page, "([i,s])=>{ const t=getBook('main').trades.find(x=>x.id===i); t.sl=s; saveBook('main'); render(); }", [tid, sl]); page.wait_for_timeout(250)


def btn(page, tid=None):
    return js(page, """()=>{ const b=document.querySelector('[data-pyr-btn]'); if(!b) return null;
        const w=document.querySelector('[data-pyr-why]'); return {disabled:b.disabled, title:b.title||'', label:b.innerText, why: w ? w.innerText : ''}; }""")


def open_sheet(page, tid="t1"):
    js(page, "(i)=>satPyrOpen(i,'main')", tid); page.wait_for_timeout(250)


def fill(page, broke=True, e2=None, sj=None):
    if broke and not page.is_checked("#pyrBreak"): page.check("#pyrBreak")
    if (not broke) and page.is_checked("#pyrBreak"): page.uncheck("#pyrBreak")
    if e2 is not None: page.fill("#pyrEntry", str(e2))
    if sj is not None: page.fill("#pyrSL", str(sj))
    page.wait_for_timeout(120)


def sheet(page):
    return js(page, """()=>{ const g=id=>{ const e=document.getElementById(id); return e ? e.innerText : null; };
        return {lot:g('pyrLot'), r2:g('pyrRisk2'), r1:g('pyrRisk1'), heat:g('pyrHeat'), err:g('pyrErr'), save: (document.getElementById('pyrSave')||{}).disabled, sl: (document.getElementById('pyrSL')||{}).value}; }""")


def overflow_bad(page, root_sel):
    return page.evaluate("""(s)=>{ const bad=[]; document.querySelectorAll(s+', '+s+' *').forEach(e=>{ const r=e.getBoundingClientRect();
        if(r.width && (r.right > window.innerWidth + 1 || r.left < -1)) bad.push((e.id||e.className||e.tagName)+':'+Math.round(r.right)); }); return bad.slice(0,5); }""", root_sel)


def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        page.evaluate("() => switchTab('flow')")
        p5.goto_sat(page); clean(page)
        info = js(page, "()=>({fx:state.settings.fx, riskTHB: sat7dAcctBase('main').riskTHB, cap: sat7dAcctBase('main').cap, heatMax: sat7dAcctBase('main').heatMax, newMax: sat7dAcctBase('main').newMax})")
        check(f"{tag} 0 PY2: ค่าเริ่มสัดส่วน SAT_PYR_SPLIT_DEF = [50,30,20] · satPyrSplitOf('main') ตรงกัน (แทน SAT_PYR_MAX/RATIO ของ PY1)", js(page, "()=>JSON.stringify(SAT_PYR_SPLIT_DEF)==='[50,30,20]' && JSON.stringify(satPyrSplitOf('main'))==='[50,30,20]'"))
        riskusd = info["riskTHB"] / info["fx"]
        lot_for = lambda pct, dist: round(math.floor(riskusd * pct / 100 / (dist * 100) / 0.01 + 1e-9) * 0.01, 8)

        # ── 1 SL ไม้ 1 = 2390 (ยังเสี่ยงอยู่) — PY2: ปุ่ม 'เติมไม้ 2' กดได้ (ไม่บังคับ SL ที่ทุนแล้ว) แต่ sheet บันทึกไม่ได้จนเสี่ยงรวมไม่เกินงบสะสม
        mk_first(page)
        b = btn(page)
        check(f"{tag} 1 ปุ่ม 'เติมไม้ 2' แสดง · กดได้ · ไม่มีบรรทัดเหตุผล (PY2 ไม่บังคับ SL ที่ทุน)",
              b and b["disabled"] is False and "เติมไม้ 2" in b["label"] and b["why"] == "", json.dumps(b, ensure_ascii=False))
        shot(page, f"py1-btn-locked-{label}.png", ".ui-row")
        n0 = trades_n(page)
        js(page, "()=>satPyrOpen('t1','main')"); page.wait_for_timeout(200)
        fill(page, e2=2412, sj=2390); s0 = sheet(page)
        check(f"{tag} 1 เปิด sheet ตอน SL ไม้ 1 ยัง 2390 (เสี่ยงค้าง $400 > งบสะสม 80%) → บันทึกปิด + 'เลื่อน SL ไม้ก่อนหน้าก่อน'", page.locator(".pyr-sheet").count() == 1 and s0["save"] is True and "เลื่อน SL ไม้ก่อนหน้าก่อน" in s0["err"] and trades_n(page) == n0, json.dumps(s0, ensure_ascii=False))
        js(page, "()=>satPyrClose()")

        # ── 2 แก้ SL ไม้ 1 เป็น 2400 ผ่านฟอร์มแก้ไม้ → ปุ่มกดได้ → sheet
        js(page, "()=>openTradeEdit('t1','main')"); page.wait_for_timeout(250)
        page.fill("#tSL", "2400"); page.wait_for_timeout(100)
        err = js(page, "()=>document.getElementById('teErr').innerText")
        check(f"{tag} 2 ฟอร์มแก้ไม้ Sat ที่เปิดอยู่: SL = ทุน (2400) ไม่ถูกบล็อก", err.strip() == "" and not js(page, "()=>document.getElementById('teSaveBtn').disabled"), err)
        check(f"{tag} 2 ไม้ 1 ยังไม่มีไม้เติม → ไม่มีติ๊ก 'ใช้ SL นี้กับทั้ง 2 ไม้'", not page.is_visible("#teJointBox"))
        page.click("#teSaveBtn"); page.wait_for_timeout(300)
        b = btn(page)
        check(f"{tag} 2 SL = 2400 → ปุ่มเติมกดได้ · ไม่มีบรรทัดเหตุผล", b and b["disabled"] is False and b["why"] == "", json.dumps(b, ensure_ascii=False))
        page.click("[data-pyr-btn]"); page.wait_for_timeout(300)
        s = sheet(page)
        fill(page, broke=True, e2=2412, sj=2400); s = sheet(page); q2 = lot_for(30, 12)
        check(f"{tag} 2 sheet: lot ไม้ 2 = 30% ของงบ ({q2}) · SL ร่วมเริ่มต้น = 2400", s["lot"] is not None and abs(float(s["lot"]) - q2) < 1e-9 and s["sl"] == "2400", json.dumps(s, ensure_ascii=False))
        check(f"{tag} 2 sheet: หัวชื่อ 'เติมไม้ · XAUUSD · …' + ช่อง lot แก้ไม่ได้", js(page, "()=>{ const s=document.querySelector('[data-pyr-sheet]'); return !!s && /เติมไม้/.test(s.innerText) && !document.querySelector('#pyrLot input'); }"))

        # ── 3 Break out บังคับ · ตัวเลขความเสี่ยง
        fill(page, broke=False, e2=2412, sj=2400)
        s = sheet(page)
        check(f"{tag} 3 ไม่ติ๊ก Break โครงสร้าง → บันทึกปิด + ข้อความ", s["save"] is True and "Break โครงสร้างใหม่" in s["err"], json.dumps(s, ensure_ascii=False))
        fill(page, broke=True, e2=2412, sj=2400)
        s = sheet(page)
        exp_r2 = q2 * 12 * 100 * info["fx"]
        exp_txt = js(page, "(v)=>fmt0(Math.round(v))", exp_r2)
        exp_rm = js(page, "(v)=>fmt2(v)", exp_r2 / info["riskTHB"])
        check(f"{tag} 3 ความเสี่ยงไม้เติม = {q2} × 12 × 100 × fx = ฿{exp_txt} ({exp_rm}R)", f"฿{exp_txt}" in (s["r2"] or "") and f"{exp_rm}R" in (s["r2"] or ""), json.dumps(s, ensure_ascii=False))
        check(f"{tag} 3 ไม้ 1 หลังย้าย SL ร่วม เสี่ยง 0 (ล็อกกำไร) · ไม่มี error · บันทึกได้", "฿0" in (s["r1"] or "") and s["err"].strip() == "" and s["save"] is False, json.dumps(s, ensure_ascii=False))
        exp_heat = js(page, "(v)=>fmt2(Math.round(v)/1)", exp_r2 / info["cap"] * 100 * 100 / 100)
        heat_exp = js(page, "(v)=>fmt2(Math.round(v*100)/100)", exp_r2 / info["cap"] * 100)
        check(f"{tag} 3 heat หลังเติม = {heat_exp}/{info['heatMax']}%", f"{heat_exp}/{info['heatMax']}%" in (s["heat"] or ""), json.dumps(s, ensure_ascii=False))
        page.evaluate("()=>{ const e=document.querySelector('#pyrSave'); e.scrollIntoView({block:'end'}); }")
        shot(page, f"py1-sheet-{label}.png", ".pyr-sheet .ui-sheet")
        sheet_bad = overflow_bad(page, ".pyr-sheet")

        # ── 4 SL ร่วมไม่ผ่าน
        fill(page, e2=2412, sj=2398); s = sheet(page)
        cum = js(page, "()=>document.getElementById('pyrCum').innerText")
        check(f"{tag} 4 SL ร่วม 2398 (ต่ำกว่าทุนไม้ 1) → PY2 ไม่บังคับ SL ที่ทุน: ไม่มี error 'ทุนไม้ 1' · แสดง 'เสี่ยงค้าง x% … / งบสะสม 80%' แทน", "ทุนไม้ 1" not in s["err"] and "เสี่ยงค้าง" in cum and "งบสะสม 80%" in cum, json.dumps([s, cum], ensure_ascii=False))
        fill(page, e2=2412, sj=2413); s = sheet(page)
        check(f"{tag} 4 SL ร่วม 2413 (เหนือ entry ไม้เติม) → ข้อความ + บันทึกปิด", s["save"] is True and "ราคาเข้าไม้เติม" in s["err"], json.dumps(s, ensure_ascii=False))
        red = js(page, "()=>getComputedStyle(document.getElementById('pyrErr')).color")
        check(f"{tag} 4 ข้อความ error เป็นสีแดง", red.startswith("rgb(") and (lambda c: c[0] > 150 and c[1] < 100 and c[2] < 100)([int(x) for x in red[4:-1].split(",")[:3]]), red)

        # ── 5 บันทึก
        fill(page, e2=2412, sj=2400)
        n_new_before = js(page, "()=>sat7dAcctBase('main').nNew")
        heat_before = js(page, "()=>sat7dAcctBase('main').heatPct")
        meta_before = js(page, "()=>document.querySelector('.sumMr[data-acct=\"main\"]').innerText.replace(/\\s+/g,' ')")
        page.click("#pyrSave"); page.wait_for_timeout(400)
        t1, ts = tr(page, "t1"), js(page, "()=>getBook('main').trades.filter(x=>x.pyr_parent)")
        t2 = ts[0] if len(ts) == 1 else None
        check(f"{tag} 5 สร้างไม้ใหม่ 1 ไม้: open · pyr_parent=t1 · pyr_no=2 · qty {q2} · sl 2400 · entry 2412 · tp = TP ไม้ 1",
              t2 and t2["status"] == "open" and t2["pyr_parent"] == "t1" and t2["pyr_no"] == 2 and abs(t2["qty"] - q2) < 1e-9 and t2["sl"] == 2400 and t2["entry"] == 2412 and t2["tp"] == t1["tp"], json.dumps(t2, ensure_ascii=False))
        check(f"{tag} 5 ไม้เติมโครงเดียวกับไม้ Sat: port satB · XAUUSD · Long · openedAt วันนี้ · mult 100", t2 and t2["port"] == "satB" and t2["sym"] == "XAUUSD" and t2["bias"] == "Long" and t2["openedAt"] == today(page) and t2["mult"] == 100, json.dumps(t2, ensure_ascii=False))
        check(f"{tag} 5 ไม้ 1: sl = 2400 · pyr_child = ไม้เติม", t1["sl"] == 2400 and t2 and t1["pyr_child"] == t2["id"], json.dumps(t1, ensure_ascii=False))
        slot = js(page, "()=>sat7dIdea('i_t1').accts.main")
        check(f"{tag} 5 idea.accts.main.trade_id ยังชี้ไม้ 1 · เก็บ pyr_trade_id (+ pyr_trade_ids) เพิ่ม", slot["trade_id"] == "t1" and t2 and slot["pyr_trade_id"] == t2["id"] and slot["pyr_trade_ids"] == [t2["id"]], json.dumps(slot))
        rows = js(page, "()=>[...document.querySelectorAll('.ui-row')].map(r=>r.innerText.replace(/\\s+/g,' '))")
        check(f"{tag} 5 แถวไม้เติมต่อจากไม้ 1 + ป้าย 'ไม้ 1/3' · 'ไม้ 2/3' (data-pyr-tag) + ปุ่มปิดไม้", len(rows) == 2 and "ไม้ 2/3" in rows[1] and "ปิดไม้" in rows[1] and "ไม้ 1/3" in rows[0] and page.locator("[data-pyr-tag]").count() >= 2, json.dumps(rows, ensure_ascii=False))
        check(f"{tag} 5 ปุ่มเติมย้ายไปที่ไม้ 2 (ล่าสุด) เป็น 'เติมไม้ 3' · ไม้ 1 ไม่มีปุ่ม", js(page, "()=>[...document.querySelectorAll('[data-pyr-btn]')].map(e=>e.innerText.trim())") == ["เติมไม้ 3"])
        shot(page, f"py1-after-rows-{label}.png", "#satV3Panel")

        # ── 6 โควตา + heat
        n_new_after = js(page, "()=>sat7dAcctBase('main').nNew")
        heat_after = js(page, "()=>sat7dAcctBase('main').heatPct")
        meta_after = js(page, "()=>document.querySelector('.sumMr[data-acct=\"main\"]').innerText.replace(/\\s+/g,' ')")
        import re
        nn = lambda m: (re.search(r"ไม้ใหม่\s*(\d+)/(\d+)", m) or [None, None, None])[1]
        check(f"{tag} 6 Calc.newCount ผ่าน sat7dAcctBase: ก่อน {n_new_before} → หลัง {n_new_after} (เท่าเดิม)", n_new_before == n_new_after, f"{n_new_before} {n_new_after}")
        check(f"{tag} 6 แถบบัญชี 'ไม้ใหม่ x/{info['newMax']}' ไม่ขยับ", nn(meta_before) is not None and nn(meta_before) == nn(meta_after), f"{meta_before} || {meta_after}")
        check(f"{tag} 6 heat ขยับตามความเสี่ยงไม้เติม (+{exp_r2/info['cap']*100:.3f}%)", abs((heat_after - heat_before) - exp_r2 / info["cap"] * 100) < 1e-6, f"{heat_before} {heat_after}")
        wk_cnt = js(page, "()=>{ const b=planAcctBundle ? null : null; return null; }")
        pos_new = js(page, """()=>{ const A='main'; return withAccount(A, ()=>{ const wk=wpWeekKey(), seen=new Set(); state.trades.forEach(t=>{ if(t.pyr_parent) return; if((t.status==='open'||t.status==='closed') && wpOpenedKey(t)===wk) seen.add(t.posGroup||t.id); }); return seen.size; }); }""")
        bundle_new = js(page, "()=>{ const o=withAccount('main', ()=>planAcctBundle('main')); return o.nNew!==undefined ? o.nNew : (o.newCount!==undefined ? o.newCount : null); }")
        check(f"{tag} 6 ไม้ใหม่ในแถบ Positions (planAcctBundle) ไม่นับไม้เติม", bundle_new in (None, 1) and pos_new == 1, f"{bundle_new} {pos_new}")

        # ── 12 SL ร่วม (ฟอร์มแก้ไม้)
        js(page, "(i)=>openTradeEdit(i,'main')", t2["id"]); page.wait_for_timeout(250)
        vis = page.is_visible("#teJointBox"); chk = page.is_checked("#tJointSL")
        check(f"{tag} 12 แก้ไม้เติม → มีติ๊ก 'ใช้ SL นี้กับทั้ง 2 ไม้' ค่าเริ่มต้น = ติ๊ก", vis and chk, f"{vis} {chk}")
        page.fill("#tSL", "2405"); page.click("#teSaveBtn"); page.wait_for_timeout(300)
        a, b2 = tr(page, "t1"), tr(page, t2["id"])
        check(f"{tag} 12 ติ๊ก 'ใช้กับทั้ง 2 ไม้' → ทั้งคู่ SL 2405", a["sl"] == 2405 and b2["sl"] == 2405, f"{a['sl']} {b2['sl']}")
        js(page, "(i)=>openTradeEdit(i,'main')", t2["id"]); page.wait_for_timeout(250)
        page.fill("#tSL", "2406"); page.uncheck("#tJointSL"); page.click("#teSaveBtn"); page.wait_for_timeout(300)
        a, b2 = tr(page, "t1"), tr(page, t2["id"])
        check(f"{tag} 12 ไม่ติ๊ก → เปลี่ยนเฉพาะไม้เติม (ไม้ 1 ยัง 2405 · ไม้เติม 2406)", a["sl"] == 2405 and b2["sl"] == 2406, f"{a['sl']} {b2['sl']}")
        js(page, "(i)=>openTradeEdit(i,'main')", "t1"); page.wait_for_timeout(250)
        check(f"{tag} 12 แก้ไม้ 1 (โหมดเปิด) ก็มีติ๊กเหมือนกัน", page.is_visible("#teJointBox") and page.is_checked("#tJointSL"))
        js(page, "()=>closeTradeEdit()")
        js(page, "()=>{ const B=getBook('main'); B.trades.find(x=>x.pyr_parent).sl=2400; saveBook('main'); render(); }")

        # ── 13 ปิดไม้ 1 → ไม้เติมยังเปิด · ปุ่มไม่กลับ · Journal
        td = today(page)
        js(page, "([d])=>{ const B=getBook('main'); const t=B.trades.find(x=>x.id==='t1'); t.status='closed'; t.exitPrice=2420; t.exitDate=d; saveBook('main'); render(); }", [td])
        page.wait_for_timeout(300)
        rows = js(page, "()=>[...document.querySelectorAll('.ui-row')].map(r=>r.innerText.replace(/\\s+/g,' '))")
        check(f"{tag} 13 ปิดไม้ 1 → ไม้เติมยังเปิด (แถวยังอยู่ + ป้าย 'ไม้ 2/3') · ปุ่มเติมไม้ 3 อยู่ที่ไม้ 2", len(rows) == 1 and "ไม้ 2/3" in rows[0] and js(page, "()=>[...document.querySelectorAll('[data-pyr-btn]')].map(e=>e.innerText.trim())") == ["เติมไม้ 3"], json.dumps(rows, ensure_ascii=False))
        js(page, "([d])=>{ const B=getBook('main'); const t=B.trades.find(x=>x.pyr_parent); t.status='closed'; t.exitPrice=2430; t.exitDate=d; saveBook('main'); render(); }", [td])
        page.wait_for_timeout(200)
        r2 = js(page, "()=>realizedROf(getBook('main').trades.find(x=>x.pyr_parent))")
        exp_r = (2430 - 2412) / (2412 - 2400)   # R ของไม้เติมคิดจากความเสี่ยงของตัวเอง (ไม่เปลี่ยนตาม PY2)
        js(page, "()=>{ switchTab('journal'); setJFilter('closed'); }"); page.wait_for_timeout(350)
        jt = js(page, "()=>{ const o=[]; document.querySelectorAll('#jContent_closed tr, #jContent_closed .tcard').forEach(e=>o.push(e.innerText.replace(/\\s+/g,' '))); return o; }")
        tagged = [x for x in jt if "เติม" in x]
        check(f"{tag} 13 Journal: ไม้เติมมีป้าย 'เติม' (ตารางและการ์ด · ไม้ 1 ไม่มี)", len(tagged) >= 1 and all("2,412" in x for x in tagged) and not any("2,400 2,420" in x and "เติม" in x for x in jt) and js(page, "()=>document.querySelectorAll('#jContent_closed [data-pyr-tag]').length") >= 1, json.dumps(jt, ensure_ascii=False)[:400])
        check(f"{tag} 13 R ไม้เติม = (2430−2412)/(2412−2400) = {exp_r} (คิดจากความเสี่ยงของตัวเอง)", r2 is not None and abs(r2 - exp_r) < 1e-9, str(r2))
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }")

        # ── 7 heat เต็ม
        clean(page)
        mk_first(page, sl=2400)
        push_trade(page, id="big", date=today(page), entry=2410, sl=2390, qty=0.9, tp=2450)   # ความเสี่ยง 0.9×20×100×33 = 59,400 ฿ ของ heatMax 62,400
        open_sheet(page); fill(page, e2=2412, sj=2400); s = sheet(page)
        check(f"{tag} 7 heat หลังเติมเกิน heatMax → 'heat เกิน' · บันทึกปิด", "heat เกิน" in s["err"] and s["save"] is True, json.dumps(s, ensure_ascii=False))
        n0 = trades_n(page)
        ok = js(page, "()=>satPyrSave()")
        check(f"{tag} 7 เรียกบันทึกตรง ๆ ตอน heat เกิน → ไม่สร้างไม้", ok is False and trades_n(page) == n0)
        js(page, "()=>satPyrClose()")
        # โควตาไม้ใหม่เต็ม (≥ newMax) ก็ยังเติมได้ — เติมไม่เช็กโควตา
        clean(page); mk_first(page, sl=2400)
        for i in range(info["newMax"]):
            push_trade(page, id=f"q{i}", date=today(page), bias="Short", entry=2650, sl=2680, tp=2600, qty=0.01)
        full = js(page, "()=>{ const b=sat7dAcctBase('main'); return b.nNew >= b.newMax; }")
        open_sheet(page); fill(page, e2=2412, sj=2400); s = sheet(page)
        check(f"{tag} 7 โควตาไม้ใหม่เต็มแล้ว ({full}) → เติมยังได้ (ไม่มี 'โควตาเต็ม')", full and s["err"].strip() == "" and s["save"] is False, json.dumps(s, ensure_ascii=False))
        js(page, "()=>satPyrClose()")

        # ── 8 สวน Bias
        clean(page); mk_first(page, sl=2400)
        open_sheet(page); fill(page, e2=2412, sj=2400)
        setup_week(page, bias="Short", support=(2400,), resistance=(2520,)); page.wait_for_timeout(300)
        js(page, "()=>render()"); page.wait_for_timeout(250)
        b = btn(page)
        check(f"{tag} 8 PF1 — Strategy bias เก่าสลับเป็น Short: ปุ่มเติมยังกดได้ · ไม่มีข้อความ สวน Bias", b and b["disabled"] is False and "สวน Bias" not in b["why"], json.dumps(b, ensure_ascii=False))
        n0 = trades_n(page)
        ok = js(page, "()=>satPyrSave()")
        check(f"{tag} 8 PF3 เรียกฟังก์ชันบันทึกเติมตรง ๆ ตอน Strategy bias เก่าเป็น Short → ไม่ถูกบล็อกแล้ว: บันทึกสำเร็จ · สร้างไม้เติม 1 ไม้ ({n0}→{trades_n(page)})", ok is True and trades_n(page) == n0 + 1, json.dumps([ok, n0, trades_n(page)]))
        js(page, "()=>satPyrClose()")

        # ── 9 Short
        clean(page, bias="Short")
        mk_first(page, bias="Short", entry=2400, sl=2410)
        b = btn(page)
        check(f"{tag} 9 Short: SL 2410 (> ทุน) → PY2 ปุ่ม 'เติมไม้ 2' กดได้ (เสี่ยงรวมตรวจที่ sheet)", b and b["disabled"] is False and "เติมไม้ 2" in b["label"], json.dumps(b, ensure_ascii=False))
        set_sl(page, "t1", 2400)
        b = btn(page)
        open_sheet(page); fill(page, e2=2388, sj=2400); s = sheet(page)
        check(f"{tag} 9 Short: SL 2400 → ปุ่มกดได้ · entry 2388 SL ร่วม 2400 ผ่าน (error ว่าง · บันทึกได้)", b and b["disabled"] is False and s["err"].strip() == "" and s["save"] is False, json.dumps([b, s], ensure_ascii=False))
        fill(page, e2=2388, sj=2387); s = sheet(page)
        check(f"{tag} 9 Short: SL ร่วม 2387 (ต่ำกว่า entry ไม้เติม) → บล็อก", s["save"] is True and s["err"].strip() != "", json.dumps(s, ensure_ascii=False))
        fill(page, e2=2388, sj=2401); s = sheet(page)
        check(f"{tag} 9 Short: SL ร่วม 2401 (สูงกว่าทุนไม้ 1) → ไม่มีข้อห้าม 'ทุนไม้ 1' (PY2) · เสี่ยงค้างอยู่ในงบสะสม → บันทึกได้", "ทุนไม้ 1" not in s["err"] and s["save"] is False, json.dumps(s, ensure_ascii=False))
        js(page, "()=>satPyrClose()")

        # ── 10 minLot
        clean(page); mk_first(page, sl=2400, qty=0.01)
        b = btn(page)
        check(f"{tag} 10 qty ไม้ 1 = minLot (0.01) → ปุ่มกดไม่ได้ + 'ไม้ 1 เล็กเกินจะแบ่ง 30% (ขั้นต่ำ 0.01)' (PY2: สัดส่วนไม้ 2)", b and b["disabled"] and "ไม้ 1 เล็กเกินจะแบ่ง 30% (ขั้นต่ำ 0.01)" in b["title"], json.dumps(b, ensure_ascii=False))

        # ── 11 ไม้ 1 ลดขนาด ×0.6
        clean(page); mk_first(page, sl=2400, qty=0.24, sizeFactor=0.6, size_rule=0.6, macro_state="against", trend_state="down", macro_stance="bear", driver="D1", off_rule=False)
        open_sheet(page)
        lot = sheet(page)["lot"]
        fill(page, e2=2412, sj=2400); lot = sheet(page)["lot"]
        q11 = round(math.floor(riskusd * 0.6 * 0.3 / (12 * 100) / 0.01 + 1e-9) * 0.01, 8)   # งบ = RPT × sizeFactor ของไม้ 1 (0.6) · ไม้ 2 = 30% (ไม่คูณ 0.6 ซ้ำ)
        check(f"{tag} 11 ไม้ 1 ลดขนาด (sizeFactor 0.6) → lot ไม้ 2 = 30% ของงบที่ลดแล้ว = {q11}", lot is not None and abs(float(lot) - q11) < 1e-9, str(lot))
        page.click("#pyrSave"); page.wait_for_timeout(400)
        t2 = (js(page, "()=>getBook('main').trades.filter(x=>x.pyr_parent)") or [None])[0]
        keep = t2 and all(t2.get(k) == v for k, v in {"size_rule": 0.6, "macro_state": "against", "trend_state": "down", "driver": "D1", "sizeFactor": 0.6}.items())
        check(f"{tag} 11 ไม้เติมคัดลอก F2c field (size_rule · macro_state · trend_state · driver · sizeFactor) จากไม้ 1", keep and abs(t2["qty"] - q11) < 1e-9, json.dumps(t2, ensure_ascii=False))

        # ── 14 plan / Core
        clean(page)
        mk_first(page, tid="tp", status="plan", sl=2400)
        check(f"{tag} 14 ไม้ plan → ไม่มีปุ่มเติม", js(page, "()=>document.querySelectorAll('[data-pyr-btn]').length") == 0 and js(page, "()=>satPyrEligible(getBook('main').trades.find(x=>x.id==='tp'))") is False)
        clean(page)
        push_trade(page, id="tc", date=today(page), port="core", sym="AAPL", entry=100, sl=100, qty=10, mult=1, tp=130, cur="USD")
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }")
        check(f"{tag} 14 ไม้ Core → ไม่มีปุ่มเติม · satPyrEligible=false", js(page, "()=>document.querySelectorAll('[data-pyr-btn]').length") == 0 and js(page, "()=>satPyrEligible(getBook('main').trades.find(x=>x.id==='tc'))") is False)

        # ── 15 ไม่ล้น + console
        clean(page); mk_first(page, sl=2390)
        bad_row = overflow_bad(page, "#satV3Panel .ui-row")
        mk_first(page, tid="t9", sl=2400, idea=False) if False else None
        set_sl(page, "t1", 2400)
        open_sheet(page); fill(page, e2=2412, sj=2400)
        bad_sheet = overflow_bad(page, ".pyr-sheet")
        scroll_ok = page.evaluate("()=>document.documentElement.scrollWidth <= window.innerWidth + 1")
        check(f"{tag} 15 แถว + ปุ่ม + sheet ไม่ล้นแนวนอน (เช็กราย element)", not bad_row and not bad_sheet and not sheet_bad and scroll_ok, json.dumps([bad_row, bad_sheet, sheet_bad, scroll_ok]))
        js(page, "()=>satPyrClose()")
    finally:
        check(f"{tag} 15 console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} 15 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
        browser.close()


def main():
    with sync_playwright() as pw:
        ui_tests(pw, 1440, 900, "1440px")
        ui_tests(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 36 / PY1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
