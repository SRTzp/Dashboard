#!/usr/bin/env python3
"""SU — "Setup ไม่ครบ" แยกจาก "นอกแผน" (แผน Sat ทุกแบบ) · เทส 30
ธง trade.setup_incomplete (ใหม่) · Setup ไม่ถึง 65% → unplanned:false + setup_incomplete:true · นอกแผนจริง (บัญชีไม่ ready → "รวมด้วย") ยังเป็น unplanned:true
mock Firestore · Chromium 1440 + 430 · ภาพเก็บที่ tests/screenshots/su-*.png
รัน: python3 run_tests_phase30.py"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase27 as p27
from run_tests_phase11 import pbver, seed_pb, iso, fresh, wk, reset_ideas
from run_tests_phase27 import js, mk, setup_week, push_trade, set_idea

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


def trade_of(page, iid, acct="main"):
    return js(page, """([i,a])=>{ const s=((sat7dIdea(i)||{}).accts||{})[a]||{}; return s.trade_id ? getBook(a).trades.find(x=>x.id===s.trade_id) : null; }""", [iid, acct])


def set_setups(page, iid, n):
    ids = js(page, "(i)=>satV3SetupsFor(sat7dIdea(i).asset).map(s=>s.id)", iid)
    set_idea(page, iid, {"setups": ids[:n]})
    return len(ids)


def clean(page):
    reset_ideas(page)
    js(page, "()=>{ const B=getBook('main'); B.trades=[]; saveBook('main'); }")
    setup_week(page)


def open_it(page, tid):
    """Positions แสดงเฉพาะไม้ open — เปลี่ยนไม้ plan ที่เพิ่งบันทึกเป็น open (ไม่แตะธงอื่น)"""
    js(page, "(id)=>{ const B=getBook('main'); const t=B.trades.find(x=>x.id===id); t.status='open'; t.openedAt=thaiToday(); saveBook('main'); render(); }", tid)


def pos_view(page, w):
    js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(300)
    sel = "tr[data-pos]" if w > 900 else ".tcard[data-pos]"
    return page.evaluate("(s)=>{ const o={}; document.querySelectorAll(s).forEach(r=>o[r.dataset.pos]=r.innerText.replace(/\\s+/g,' ')); return o; }", sel)


def j_view(page, w):
    """ข้อความต่อ trade id ใน Journal Closed ทั้งหมดที่เห็น (ตาราง/การ์ด) — คืน dict sym→ข้อความ"""
    return page.evaluate("""()=>{ const o=[]; document.querySelectorAll('#jContent_closed tr, #jContent_closed .tcard').forEach(e=>o.push(e.innerText.replace(/\\s+/g,' '))); return o.join(' | '); }""")


def jfilter(page, f):
    js(page, "(f)=>{ switchTab('journal'); setJFilter(f); }", f); page.wait_for_timeout(350)
    return j_view(page, 0)


def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        page.evaluate("() => switchTab('flow')")
        p5.goto_sat(page); clean(page)
        # ── 1 แผนปกติ Setup 0/3 · บัญชี ready
        mk(page, "iA", entry=2650, sl=2680, tp=None, active="c1"); set_idea(page, "iA", {"tp": 2380})
        total = set_setups(page, "iA", 0)
        a = js(page, "()=>satV3PlanAcctCalc(sat7dIdea('iA'),'main').ready")
        check(f"{tag} 0 เตรียม: บัญชี ready · Setup มี {total} ข้อ", a is True and total >= 2, f"{a} {total}")
        js(page, "()=>satV3SaveSlot('iA','main')"); page.wait_for_timeout(350)
        t1 = trade_of(page, "iA")
        check(f"{tag} 1 Setup 0/3 + ready → unplanned:false · setup_incomplete:true", t1 and t1["unplanned"] is False and t1["setup_incomplete"] is True, json.dumps({k: (t1 or {}).get(k) for k in ("unplanned", "setup_incomplete")}))
        open_it(page, t1["id"]); pv = pos_view(page, w)
        check(f"{tag} 1 Positions: ไม้มีชิป 'Setup ไม่ครบ' · ไม่มี 'นอกแผน'", t1 and "Setup ไม่ครบ" in pv.get(t1["id"], "") and "นอกแผน" not in pv.get(t1["id"], ""), pv.get(t1["id"] if t1 else "", ""))
        shot(page, f"su-positions-chips-{label}.png")
        # ── 5 ข้อความหน้างาน + การ์ดไม้ที่เปิด
        clean(page)
        mk(page, "iB", entry=2650, sl=2680, tp=None, active="c1"); set_idea(page, "iB", {"tp": 2380}); set_setups(page, "iB", 0)
        js(page, "()=>{ satV3Open.add('iB'); satV3Render(); }"); page.wait_for_timeout(300)
        card = page.evaluate("()=>{ const e=document.querySelector('.ui-plan[data-id=\"iB\"]'); return e ? e.innerText.replace(/\\s+/g,' ') : ''; }")
        lbl = page.evaluate("()=>satV3SetupLabel(satV3SetupsReady(sat7dIdea('iB')))")
        check(f"{tag} 5 ข้อความ = 'Setup 0/{total} · ต่ำกว่า 65% = Setup ไม่ครบ' (AC2: ตัดบรรทัดออกจากการ์ด · ข้อความจากฟังก์ชันยังเท่าเดิม)", f"Setup 0/{total} · ต่ำกว่า 65% = Setup ไม่ครบ" == lbl and "ต่ำกว่า 65%" not in card, lbl + " | " + card[:200])
        check(f"{tag} 5 ไม่มีคำ '= นอกแผน' ในการ์ด Sat", "= นอกแผน" not in card)
        shot(page, f"su-sat-active-label-{label}.png", '.ui-plan[data-id="iB"]')
        # ── 2 Setup ≥ 65%
        clean(page)
        mk(page, "iC", entry=2650, sl=2680, tp=None, active="c1"); set_idea(page, "iC", {"tp": 2380}); set_setups(page, "iC", total)
        js(page, "()=>satV3SaveSlot('iC','main')"); page.wait_for_timeout(350)
        t2 = trade_of(page, "iC")
        check(f"{tag} 2 Setup {total}/{total} (≥ 65%) → ทั้งสองธง false", t2 and t2["unplanned"] is False and t2["setup_incomplete"] is False, json.dumps({k: (t2 or {}).get(k) for k in ("unplanned", "setup_incomplete")}))
        open_it(page, t2["id"]); pv = pos_view(page, w)
        check(f"{tag} 2 ไม่มีชิป Setup ไม่ครบ/นอกแผน", t2 and "Setup ไม่ครบ" not in pv.get(t2["id"], "") and "นอกแผน" not in pv.get(t2["id"], ""), pv.get(t2["id"] if t2 else "", ""))
        # ── 3 MR Setup 0/3
        clean(page)
        js(page, "()=>{ window.SAT_MR_ENABLED = true; }")   # SR1 — MR ปิดเป็นค่าเริ่มต้น · เคสนี้ทดสอบไม้ MR เดิม จึงเปิดคืนเฉพาะเคสนี้
        mk(page, "iM", entry=2410, sl=2390, tp=2450); set_setups(page, "iM", 0)
        js(page, "()=>satV3SaveSlot('iM','main')"); page.wait_for_timeout(350)
        t3 = trade_of(page, "iM")
        check(f"{tag} 3 MR Setup 0/3 → setup_incomplete:true · unplanned:false · mr:true", t3 and t3["setup_incomplete"] is True and t3["unplanned"] is False and t3.get("mr") is True, json.dumps(t3))
        open_it(page, t3["id"]); pv = pos_view(page, w); tx = pv.get(t3["id"], "") if t3 else ""
        check(f"{tag} 3 ชิป 'MR · สวน Bias' + 'Setup ไม่ครบ' · ไม่มี 'นอกแผน'", "MR · สวน Bias" in tx and "Setup ไม่ครบ" in tx and "นอกแผน" not in tx, tx)
        js(page, "()=>{ window.SAT_MR_ENABLED = false; }")
        # ── 4 บัญชีไม่ ready (โควตาเต็ม) + รวมด้วย
        clean(page)
        nmax = js(page, "()=>SAT7D_NEW_MAX")
        for i in range(nmax):
            push_trade(page, id=f"q{i}", date=js(page, "()=>thaiToday()"), bias="Short", entry=2650, sl=2680, tp=2600, qty=0.01, status="open")
        mk(page, "iD", entry=2650, sl=2680, tp=None, active="c1"); set_idea(page, "iD", {"tp": 2380}); set_setups(page, "iD", 0)
        c = js(page, "()=>{ const c=satV3PlanAcctCalc(sat7dIdea('iD'),'main'); return {ready:c.ready, lot:c.lot}; }")
        check(f"{tag} 4 เตรียม: โควตาเต็ม → ไม่ ready แต่คำนวณ lot ได้", c["ready"] is False and c["lot"] is not None, json.dumps(c))
        js(page, "()=>satV3SaveOffplanAccount('iD','main')"); page.wait_for_timeout(350)
        t4 = trade_of(page, "iD")
        check(f"{tag} 4 'รวมด้วย (นอกแผน)' + Setup 0/3 → unplanned:true + setup_incomplete:true", t4 and t4["unplanned"] is True and t4["setup_incomplete"] is True, json.dumps({k: (t4 or {}).get(k) for k in ("unplanned", "setup_incomplete")}))
        open_it(page, t4["id"]); pv = pos_view(page, w); tx = pv.get(t4["id"], "") if t4 else ""
        check(f"{tag} 4 เห็นทั้งสองชิป", "นอกแผน" in tx and "Setup ไม่ครบ" in tx, tx)
        # ── 6 Journal (ปิดไม้ข้อ 1/3/4 + ไม้ย้อนหลัง)
        today = js(page, "()=>thaiToday()")
        js(page, "()=>{ const B=getBook('main'); B.trades=B.trades.filter(x=>!/^q/.test(x.id)); saveBook('main'); }")
        def mkc(id, sym, **kw):
            o = {"id": id, "date": today, "exitDate": today, "sym": sym, "port": "satB", "bias": "Long", "entry": 100, "sl": 90, "qty": 1, "mult": 1, "cur": "USD", "status": "closed", "exitPrice": 110}
            o.update(kw)
            js(page, "(o)=>{ const t=makeTradeObject(o); const B=getBook('main'); B.trades.push(t); saveBook('main'); }", o)
        mkc("c1", "SUINC", setupIncomplete=True)                                  # ข้อ 1
        mkc("c3", "SUMR", setupIncomplete=True, mr=True, mr_level=95)             # ข้อ 3
        mkc("c4", "SUBOTH", setupIncomplete=True, offplanOverride=True)           # ข้อ 4
        mkc("c9", "SUOLD", unplannedMode=True)                                    # ไม้ย้อนหลัง/นอกแผนล้วน
        mkc("c8", "SUPLAIN")                                                      # ปกติ
        mkc("cC", "SUCORE", port="core", bias="Long", fromCard=True)                             # Core
        c9_flag = js(page, "()=>getBook('main').trades.find(x=>x.id==='c9').setup_incomplete")
        js(page, "()=>{ render(); }")
        s_ = jfilter(page, "setupinc")
        got = [s for s in ("SUINC", "SUMR", "SUBOTH", "SUOLD", "SUPLAIN", "SUCORE") if s in s_]
        check(f"{tag} 6 ตัวกรอง 'Setup ไม่ครบ' เห็นเฉพาะข้อ 1/3/4", got == ["SUINC", "SUMR", "SUBOTH"], str(got))
        chip = page.evaluate("()=>[...document.querySelectorAll('#jFilters .chip')].map(e=>e.textContent.trim())")
        check(f"{tag} 6 ชิปตัวกรอง 'Setup ไม่ครบ' อยู่ต่อจาก 'นอกแผน'", "นอกแผน" in chip and chip.index("Setup ไม่ครบ") == chip.index("นอกแผน") + 1, str(chip))
        o_ = jfilter(page, "offplan")
        got = [s for s in ("SUINC", "SUMR", "SUBOTH", "SUOLD", "SUPLAIN", "SUCORE") if s in o_]
        check(f"{tag} 6 ตัวกรอง 'นอกแผน' เห็นเฉพาะข้อ 4 (+ไม้ย้อนหลัง)", got == ["SUBOTH", "SUOLD"], str(got))
        ov = js(page, "()=>{ const o=journalStats().overall; return {n:o.nOffPlan, si:o.nSetupInc}; }")
        check(f"{tag} 6 nOffPlan ไม่นับข้อ 1/3 (=2: ข้อ 4 + ย้อนหลัง) · nSetupInc = 3", ov["n"] == 2 and ov["si"] == 3, json.dumps(ov))
        jfilter(page, "all")
        al = j_view(page, w)
        check(f"{tag} 6 Journal Closed: แถว/การ์ดข้อ 1 มีชิป 'Setup ไม่ครบ' · ไม่มี 'นอกแผน' ในแถวเดียวกัน",
              page.evaluate("""()=>[...document.querySelectorAll('#jContent_closed tr, #jContent_closed .tcard')].filter(e=>e.textContent.indexOf('SUINC')>=0).every(e=>/Setup ไม่ครบ/.test(e.textContent) && !/นอกแผน/.test(e.textContent))"""))
        check(f"{tag} 6 ข้อ 4 แสดงทั้งสองชิป", page.evaluate("""()=>[...document.querySelectorAll('#jContent_closed tr, #jContent_closed .tcard')].filter(e=>e.textContent.indexOf('SUBOTH')>=0).every(e=>/Setup ไม่ครบ/.test(e.textContent) && /นอกแผน/.test(e.textContent))"""))
        sumtx = page.evaluate("()=>document.getElementById('jSum').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 6 บรรทัดสรุปยังเป็นนอกแผน (สำคัญกว่า) เมื่อมีทั้งสอง", "ไม้นอกแผน 2 ไม้" in sumtx, sumtx[:300])
        js(page, "()=>{ const B=getBook('main'); B.trades=B.trades.filter(x=>!['c4','c9'].includes(x.id)); saveBook('main'); render(); }")
        page.wait_for_timeout(300)
        sumtx = page.evaluate("()=>document.getElementById('jSum').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 6 เหลือแต่ Setup ไม่ครบ → บรรทัดสรุป 'Setup ไม่ครบ 2 ไม้ · P&L ฿…'", "Setup ไม่ครบ 2 ไม้" in sumtx and "ไม้นอกแผน" not in sumtx, sumtx[:300])
        jfilter(page, "setupinc")
        shot(page, f"su-journal-filter-{label}.png")
        # ── 7 แก้ไม้
        js(page, "()=>{ const B=getBook('main'); const t=B.trades.find(x=>x.id==='c1'); const n=makeTradeObject({id:t.id,date:t.date,exitDate:t.exitDate,sym:t.sym,port:t.port,bias:t.bias,entry:t.entry,sl:t.sl,qty:t.qty,mult:t.mult,cur:t.cur,status:'closed',exitPrice:120,prevTrade:t}); Object.assign(t,n); saveBook('main'); }")
        t7 = js(page, "()=>getBook('main').trades.find(x=>x.id==='c1')")
        check(f"{tag} 7 แก้ไม้ผ่าน makeTradeObject(prevTrade) (ไม่ส่ง setupIncomplete) → setup_incomplete ยัง true", t7["setup_incomplete"] is True and t7["exitPrice"] == 120, json.dumps(t7.get("setup_incomplete")))
        # 7b ผ่านหน้าต่างแก้ไม้จริง
        js(page, "()=>{ switchTab('journal'); setJFilter('all'); }"); page.wait_for_timeout(300)
        opened = False
        try:
            js(page, "()=>openTradeEdit('c1','main')"); page.wait_for_timeout(500)
            for sel in ("#teSaveBtn",):
                if page.locator(sel).count():
                    page.locator(sel).first.click(); opened = True; break
            page.wait_for_timeout(500)
        except Exception as e: pass
        t7b = js(page, "()=>getBook('main').trades.find(x=>x.id==='c1')")
        check(f"{tag} 7 openTradeEdit แล้วกดบันทึก (ถ้ามีปุ่ม) → setup_incomplete ยัง true", t7b["setup_incomplete"] is True, f"opened={opened}")
        # ── 8 Core / ไม้ย้อนหลัง / ไม้เก่า
        t8 = js(page, "()=>{ const B=getBook('main'); return {core:B.trades.find(x=>x.id==='cC'), plain:B.trades.find(x=>x.id==='c8'), mk:makeTradeObject({id:'z',date:'2026-10-01',sym:'ABC',port:'core',bias:'Long',entry:1,sl:1,qty:1,status:'open'}).setup_incomplete}; }")
        check(f"{tag} 8 ไม้ Core/ไม้ปกติ/ไม้ที่ไม่ส่งธง → setup_incomplete:false", t8["core"]["setup_incomplete"] is False and t8["plain"]["setup_incomplete"] is False and t8["mk"] is False, json.dumps(t8["mk"]))
        check(f"{tag} 8 ไม้ย้อนหลัง (unplannedMode · ไม่ส่งธง) → setup_incomplete:false", c9_flag is False, str(c9_flag))
        # ── 9 มือถือไม่ล้น + ชิปไม่ทับ
        clean(page)
        mk(page, "iE", entry=2650, sl=2680, tp=None, active="c1"); set_idea(page, "iE", {"tp": 2380}); set_setups(page, "iE", 0)
        js(page, "()=>satV3SaveOffplanAccount('iE','main')"); page.wait_for_timeout(300)
        te = trade_of(page, "iE")
        if te:
            js(page, "(id)=>{ getBook('main').trades.find(x=>x.id===id).unplanned=true; }", te["id"])   # ให้มีสองชิปในแถวเดียว (ข้อ 4 จริงครอบด้วยเคส 4)
            open_it(page, te["id"])
        pv = pos_view(page, w)
        ov_ = page.evaluate("()=>document.documentElement.scrollWidth <= window.innerWidth + 1")
        check(f"{tag} 9 ไม่ล้นแนวนอน", ov_)
        rect = page.evaluate("""()=>{ const e=document.querySelector('${SEL}'); if(!e) return null; const c=[...e.querySelectorAll('.posTag')].map(x=>x.getBoundingClientRect()); return c.map(r=>[r.left,r.right,r.top,r.bottom]); }""".replace("${SEL}", "tr[data-pos]" if w > 900 else ".tcard[data-pos]"))
        ok = rect is not None and len(rect) >= 2 and all(not (a[0] < b[1] - 0.5 and b[0] < a[1] - 0.5 and a[2] < b[3] - 0.5 and b[2] < a[3] - 0.5) for i, a in enumerate(rect) for b in rect[i + 1:])
        check(f"{tag} 9 ชิปสองตัวในแถว Positions ไม่ทับกัน", ok, json.dumps(rect))
        shot(page, f"su-positions-two-chips-{label}.png")
    finally:
        check(f"{tag} console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
        browser.close()


def main():
    with sync_playwright() as pw:
        ui_tests(pw, 1440, 900, "1440px")
        ui_tests(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 30 / SU) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
