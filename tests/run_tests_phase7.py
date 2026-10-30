#!/usr/bin/env python3
"""7D.6 — จัดวาง Trade Plans: การ์ดกาง + แถวพับ "รอเงื่อนไข" อยู่ grid เดียวกัน · กลุ่มกางก่อน → กลุ่มพับ ·
แต่ละกลุ่มเรียงตามเวลาสร้าง (เก่า→ใหม่) · align-items:start · Activate/เปิด จากแถวพับ → การ์ดขึ้นก่อน + เลื่อนจอไปที่การ์ด ·
แถว plan/open ที่บันทึก order แล้วและ "แผนเดิม" อยู่นอก grid ตำแหน่งเดิม

เป็นเรื่องการจัดวางอย่างเดียว — ไม่เปลี่ยนพฤติกรรมการ์ด (เคส 7D.4/7D.5 เดิมต้องผ่านครบโดยไม่แก้)
ภาพเก็บที่ tests/screenshots/7d6-*.png · รัน: CHROMIUM_PATH=".../Google Chrome" python3 run_tests_phase7.py
"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase6 as p6

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")
os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def rect(page, sel):
    return page.evaluate("""(s)=>{ const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect();
        return {l:r.left+scrollX, t:r.top+scrollY, w:r.width, h:r.height, top:r.top, bottom:r.bottom}; }""", sel)


def grid_order(page):
    """ลำดับลูกของ .ui-pgrid เป็น [('card'|'wait', ideaId)]"""
    return page.evaluate("""() => { const g=document.querySelector('#satV3Panel .ui-pgrid'); if(!g) return [];
        return [...g.children].map(e=> e.classList.contains('ui-wait') ? ['wait', e.dataset.id] : ['card', (e.querySelector('.ui-plan')||{dataset:{}}).dataset.id]); }""")


def make_plan(page, asset, bias, cond_text, tp_from, tp_to, setup=True):
    if setup:
        p6.setup_strategy(page, asset, bias)
    iid = p6.new_plan(page, asset)
    p6.add_cond_typed(page, iid, "Break & Pullback @", cond_text, tp_from, tp_to)
    page.click(f'.ui-plan[data-id="{iid}"] .ui-plan-cta .ui-btn-pri:has-text("บันทึกแผน")')
    page.wait_for_timeout(250)
    return iid


def open_row(page, iid):
    page.click(f'.ui-wait[data-id="{iid}"] .ui-btn:text-is("เปิด")')
    page.wait_for_timeout(250)


def fold_card(page, iid):
    page.click(f'.ui-plan[data-id="{iid}"] .ui-plan-cta .ui-btn:has-text("พับกลับ")')
    page.wait_for_timeout(250)


def run(pw, width, height, label):
    tag = f"[{ENGINE}/{label}]"
    px = label.replace("px", "")
    wide = width > 900
    browser, context, page, console_errors, page_errors = base.launch_page(pw, width, height, base.DEFAULT_INDEX)
    p5.goto_sat(page)

    # สร้าง 3 แผนตามลำดับเวลา: P1 (XAUUSD) → P2 (S50) → P3 (BRENT) — พับทั้งหมดหลังบันทึกแผน
    P1 = make_plan(page, "XAUUSD", "S", "4600", 4550, 4500)
    P2 = make_plan(page, "S50", "S", "1000", 950, 940)
    P3 = make_plan(page, "BRENT", "L", "85", 90, 95)
    ideas = page.evaluate("() => satIdeasList.filter(x=>x.v3).map(x=>x.id)")
    check(f"{tag} เวลาสร้างเรียงตามที่สร้างจริง (P1 < P2 < P3)",
          page.evaluate("([a,b,c])=>{ const g=id=>sat7dIdea(id).created_at; return g(a)<=g(b) && g(b)<=g(c); }", [P1, P2, P3]))

    # ─── (2) พับทั้งหมด: เก่า → ใหม่ ───
    order = grid_order(page)
    check(f"{tag} พับทั้งสาม → อยู่ใน grid เดียว เรียง P1, P2, P3 (เก่า→ใหม่)", order == [["wait", P1], ["wait", P2], ["wait", P3]], json.dumps(order))
    r1, r2, r3 = (rect(page, f'.ui-wait[data-id="{i}"]') for i in (P1, P2, P3))
    if wide:
        check(f"{tag} 1440: แถวพับวางเป็นคอลัมน์ในแถวเดียวกัน — P1 ซ้ายสุด · P2 ถัดไปทางขวา (auto-fill ≥420px)",
              r1["l"] < r2["l"] and abs(r1["t"] - r2["t"]) < 2, json.dumps([r1, r2]))
    else:
        check(f"{tag} 430: 1 คอลัมน์ — P1 บน P2 บน P3 · ซ้ายตรงกัน", r1["t"] < r2["t"] < r3["t"] and abs(r1["l"] - r2["l"]) < 1 and abs(r2["l"] - r3["l"]) < 1, json.dumps([r1, r2, r3]))
        check(f"{tag} 430: 1 คอลัมน์ กว้างเต็มแผง (ไม่ล้น)", r1["w"] <= width, str(r1["w"]))

    # ─── (1)+(3) กาง 1 พับ 1: กางก่อนเสมอ · 1440 กางซ้าย พับขวา · 430 กางบน ───
    # ลดเหลือ 2 แผนเพื่อให้ภาพ/เช็คตรงสเปก: ปิด P3 (ผู้ใช้กด [ปิดแผน] ไม่ได้เพราะยังมีเงื่อนไข → ใช้ ยกเลิก + ปิดแผน จริง)
    page.click(f'.ui-wait[data-id="{P3}"] .ui-wc-cancel')
    page.wait_for_timeout(200)
    page.click(f'.ui-wait[data-id="{P3}"] .ui-wc-close')
    page.wait_for_timeout(250)
    check(f"{tag} เหลือ 2 แผนใน grid (P3 ปิดแผนแล้ว ไม่แสดง)", grid_order(page) == [["wait", P1], ["wait", P2]], json.dumps(grid_order(page)))

    open_row(page, P2)   # กาง P2 (สร้างทีหลัง) — ต้องขึ้นก่อน P1 ที่พับอยู่
    order = grid_order(page)
    check(f"{tag} กาง P2 พับ P1 → กลุ่มกางก่อน: [การ์ด P2, แถว P1]", order == [["card", P2], ["wait", P1]], json.dumps(order))
    rc, rw = rect(page, f'.ui-plan[data-id="{P2}"]'), rect(page, f'.ui-wait[data-id="{P1}"]')
    if wide:
        check(f"{tag} 1440: กางซ้าย พับขวา (การ์ดอยู่ซ้ายของแถวพับ · บรรทัดบนเดียวกัน)", rc["l"] < rw["l"] and abs(rc["t"] - rw["t"]) < 2, json.dumps([rc, rw]))
    else:
        check(f"{tag} 430: กางบน พับล่าง (คอลัมน์เดียว)", rc["t"] < rw["t"] and abs(rc["l"] - rw["l"]) < 1, json.dumps([rc, rw]))
    hw = page.evaluate("(i)=>{ const e=document.querySelector(`.ui-wait[data-id=\"${i}\"]`); return {h:e.getBoundingClientRect().height, sh:e.scrollHeight, as:getComputedStyle(e).alignSelf}; }", P1)
    ai = page.evaluate("() => getComputedStyle(document.querySelector('#satV3Panel .ui-pgrid')).alignItems")
    check(f"{tag} แถวพับข้างการ์ดกาง สูงไม่เกินเนื้อหา (h ≤ scrollHeight+2 และต่ำกว่าการ์ดที่กางมาก) · grid align-items:start",
          hw["h"] <= hw["sh"] + 2 and hw["h"] < rc["h"] - 100 and ai == "start", json.dumps([hw, rc["h"], ai]))
    h_beside = hw["h"]
    page.locator("#satV3Panel .ui-pgrid").screenshot(path=os.path.join(SHOTS, f"7d6-open1-fold1-{px}.png"))

    # ─── (4) พับการ์ด → ย้ายไปกลุ่มพับ · ไม่เลื่อนจอ ───
    y0 = page.evaluate("() => scrollY")
    fold_card(page, P2)
    y1 = page.evaluate("() => scrollY")
    ymax = page.evaluate("() => Math.max(0, document.documentElement.scrollHeight - innerHeight)")   # AC2: การ์ดเตี้ยลง หน้าสั้นลงจนเบราว์เซอร์ clamp scrollY เอง = ไม่ใช่การเลื่อนจอ
    order = grid_order(page)
    check(f"{tag} พับ P2 → พับทั้งคู่: อันสร้างก่อน (P1) อยู่ซ้าย/บน", order == [["wait", P1], ["wait", P2]], json.dumps(order))
    r1, r2 = rect(page, f'.ui-wait[data-id="{P1}"]'), rect(page, f'.ui-wait[data-id="{P2}"]')
    if wide:
        check(f"{tag} 1440: พับทั้งคู่ → P1 ซ้าย · P2 ขวา · บรรทัดเดียวกัน", r1["l"] < r2["l"] and abs(r1["t"] - r2["t"]) < 2, json.dumps([r1, r2]))
    else:
        check(f"{tag} 430: พับทั้งคู่ → P1 บน · P2 ล่าง", r1["t"] < r2["t"], json.dumps([r1, r2]))
    check(f"{tag} พับการ์ดไม่เลื่อนจอ (scrollY เท่าเดิม · ยกเว้นที่ถูก clamp ด้วยความสูงหน้า)", y1 == min(y0, ymax), f"{y0} -> {y1} (max {ymax})")
    check(f"{tag} แถวพับสูงเท่ากันทั้งตอนพับคู่และตอนอยู่ข้างการ์ดกาง (ไม่ยืดตามการ์ด) ต่าง ≤2px", abs(r1["h"] - h_beside) <= 2, json.dumps([r1["h"], h_beside]))
    page.locator("#satV3Panel .ui-pgrid").screenshot(path=os.path.join(SHOTS, f"7d6-fold-both-{px}.png"))

    # ─── (2) กางทั้งคู่: เก่า → ใหม่ · พับ P1 → P2 (กาง) ขึ้นก่อน ───
    open_row(page, P1); open_row(page, P2)
    check(f"{tag} กางทั้งคู่ → การ์ดเรียงเก่า→ใหม่ [P1, P2]", grid_order(page) == [["card", P1], ["card", P2]], json.dumps(grid_order(page)))
    fold_card(page, P1)
    check(f"{tag} พับ P1 (เก่ากว่า) เหลือ P2 กาง → [การ์ด P2, แถว P1]", grid_order(page) == [["card", P2], ["wait", P1]], json.dumps(grid_order(page)))
    fold_card(page, P2)

    # ─── (4) Activate จากแถวพับ → การ์ดขึ้นก่อน + อยู่ในจอ ───
    # ทำให้มีเนื้อหาพอให้ต้องเลื่อน: เปิดแผนที่ 3 อีกครั้ง (BRENT) แล้วเลื่อนจอลงล่างสุด ก่อน Activate ข้อของ P2
    P3b = make_plan(page, "BRENT", "L", "86", 91, 96)   # 7D.6 ค้าง: เปิดขั้นตั้ง Strategy ซ้ำกลับมา (open_editor คลิกชื่อสินค้าแล้ว จึงไม่ toggle พับพลาด)
    check(f"{tag} แผนใหม่ (P3b) อยู่ท้ายกลุ่มพับ: [P1, P2, P3b]", grid_order(page) == [["wait", P1], ["wait", P2], ["wait", P3b]], json.dumps(grid_order(page)))
    page.evaluate("() => scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(150)
    cond_id = page.evaluate("(i)=>sat7dIdea(i).conditions[0].id", P3b)
    page.evaluate("([i,c])=>satV3CondActivate(i,c,true)", [P3b, cond_id])   # Activate (AC1: เรียกตัวทำงานเดิมตรง ๆ) ขณะแถวพับอยู่ล่างสุด
    page.wait_for_timeout(350)
    order = grid_order(page)
    check(f"{tag} Activate จากแถวพับ → การ์ด P3b ย้ายไปกลุ่มกาง ขึ้นก่อนแถวพับทั้งหมด", order[0] == ["card", P3b] and order[1:] == [["wait", P1], ["wait", P2]], json.dumps(order))
    rc = rect(page, f'.ui-plan[data-id="{P3b}"]')
    vh = page.evaluate("() => innerHeight")
    check(f"{tag} Activate แล้วการ์ดอยู่ในจอ (ส่วนบนของการ์ดเห็น: 0 ≤ top < innerHeight−100)", 0 <= rc["top"] < vh - 100, json.dumps([rc, vh]))
    page.locator("#satV3Panel .ui-pgrid").screenshot(path=os.path.join(SHOTS, f"7d6-activate-{px}.png"))
    # [ยกเลิก Activate] แล้วพับ → กลับกลุ่มพับ
    page.evaluate("(i)=>satV3CondActivate(i, satV3ActiveCond(sat7dIdea(i)).id, false)", P3b)   # AC2: ไม่มีปุ่ม [ยกเลิก Activate] — เรียกตัวทำงานเดิมตรง ๆ
    page.wait_for_timeout(200)
    fold_card(page, P3b)
    # [เปิด] จากแถวพับที่อยู่ล่างสุด → การ์ดขึ้นก่อน + อยู่ในจอ
    page.evaluate("() => scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(150)
    open_row(page, P3b)
    rc = rect(page, f'.ui-plan[data-id="{P3b}"]')
    check(f"{tag} [เปิด] จากแถวพับล่างสุด → การ์ดขึ้นก่อนและอยู่ในจอ", grid_order(page)[0] == ["card", P3b] and 0 <= rc["top"] < vh - 100, json.dumps([grid_order(page), rc]))
    fold_card(page, P3b)

    # ─── (5) แถว plan/open ที่บันทึก order แล้ว + "แผนเดิม" อยู่นอก grid ตำแหน่งเดิม ───
    cid1 = page.evaluate("(i)=>sat7dIdea(i).conditions[0].id", P1)
    page.evaluate("([i,c])=>satV3CondActivate(i,c,true)", [P1, cid1])   # AC1
    page.wait_for_timeout(250)
    root = f'.ui-plan[data-id="{P1}"]'
    p5.fill_blur(page, f'{root} input[onchange*="\'entry\'"]', "4600")
    p5.fill_blur(page, f'{root} input[onchange*="\'sl\'"]', "4630")
    page.click(f'{root} .ui-plan-cta .ui-btn-pri:has-text("บันทึก order")')
    page.wait_for_timeout(350)
    pos = page.evaluate("""() => { const p=document.getElementById('satV3Panel'); const g=p.querySelector('.ui-pgrid');
        const btn=[...p.querySelectorAll('button')].find(b=>b.innerText.trim()==='เข้าแล้ว');
        const row = btn && btn.closest('.ui-row');
        const old = [...p.querySelectorAll('*')].find(e=>/แผนเดิม/.test(e.textContent) && e.children.length===0);
        return {rowExists: !!row, rowInGrid: !!(row && g.contains(row)), rowAfterGrid: !!(row && (g.compareDocumentPosition(row) & Node.DOCUMENT_POSITION_FOLLOWING)),
                oldExists: !!old, oldInGrid: !!(old && g.contains(old)), gridRows: g.querySelectorAll('.ui-row').length}; }""")
    check(f"{tag} บันทึก order แล้ว → แถว plan (เข้าแล้ว/ยกเลิก) อยู่นอก grid ต่อท้ายตำแหน่งเดิม (ไม่เข้า grid)",
          pos["rowExists"] and not pos["rowInGrid"] and pos["rowAfterGrid"] and pos["gridRows"] == 0, json.dumps(pos))
    check(f"{tag} 'แผนเดิม' ไม่อยู่ใน grid นี้", not pos["oldInGrid"], json.dumps(pos))
    check(f"{tag} P1 ออกจากกลุ่ม grid (มีไม้แล้ว) → grid เหลือ P2, P3b ตามลำดับเก่า→ใหม่", grid_order(page) == [["wait", P2], ["wait", P3b]], json.dumps(grid_order(page)))

    # ─── ระบบ ───
    for t in ["home", "port", "watch", "journal", "plan"]:
        try: page.evaluate(f"() => switchTab('{t}')")
        except Exception: pass
    page.wait_for_timeout(200)
    p5.goto_sat(page)
    sw = page.evaluate("() => document.documentElement.scrollWidth")
    check(f"{tag} ไม่ล้นแนวนอน (scrollWidth = {width})", sw <= width, str(sw))
    check(f"{tag} console: zero error-level messages", len(console_errors) == 0, "; ".join(console_errors[:8]))
    check(f"{tag} console: zero uncaught page errors", len(page_errors) == 0, "; ".join(page_errors[:8]))
    context.close(); browser.close()


def main():
    with sync_playwright() as pw:
        run(pw, 1440, 900, "1440px")
        run(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok)
    n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 7 / 7D.6) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok:
                print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
