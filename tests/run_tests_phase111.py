#!/usr/bin/env python3
"""CS1 — Core Trade Plan = วางแผนล้วน · ขนาดไม้จาก ★ (กรอกเอง) · ด่านเปิดแผน/ย้ายเข้า Watchlist · Sat: Classify Clear Trend/Unclear + กฎ Tactical/Main · เทส 111
Chromium · 300 / 390 / 1440 · ข้อมูล SAMPLE ล้วน · Core ฿4.2M fx 33 (≈ $127,272.73) · FF เขียว = 100%
ภาพ tests/screenshots/cs1-{plan-390,plan-1440,eval-390,gate-390}.png
รัน: SECT='calc size gate budget legacy sat width' python3 run_tests_phase111.py"""
import json, os, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase24 as P24
import run_tests_phase37 as P37
import run_tests_phase77 as P77
import run_tests_phase78 as P78
import run_tests_phase79 as P79
import run_tests_phase107 as T
import run_tests_phase108 as P108

ENGINE = base.BROWSER_ENGINE
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")
results = []
js = C.js
settle, cnt, txt = T.settle, T.cnt, T.txt
LOG = {}
TANK = 4200000 / 33.0


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    os.makedirs(SHOTS, exist_ok=True)
    page.wait_for_timeout(900)
    p = os.path.join(SHOTS, name)
    (page.locator(sel).first.screenshot(path=p) if sel else page.screenshot(path=p))
    return p


def core(pw, w=390, h=844, trades=None, cards=None):
    return C.launch2(pw, w, h, trades or [], cards or {})


def ev(page, sym, f="untested", p="untested", e="untested", rs=("untested",) * 3, g5=("untested",) * 3, stars=None, date="2026-10-30"):
    js(page, """([s,f,p,e,rs,g5,st,d])=>{ csEvalWrite(s, Calc.evalNorm({fortress:f, proven:p, emerging:e, rs:{sustained:rs[0], b26:rs[1], b52:rs[2]}, gate5:g5, stars:st, date:d})); }""",
       [sym, f, p, e, list(rs), list(g5), stars, date])
    page.wait_for_timeout(120)


def ok_ev(page, sym, stars=3, f="passed", p="passed", e="untested"):
    ev(page, sym, f=f, p=p, e=e, rs=("passed", "untested", "untested"), g5=("passed",) * 3, stars=stars)


def open_form(page, sym, acct="main"):
    if js(page, "()=>activeTab") != "plan" or js(page, "()=>planScope") != "stock": C.go_core(page)
    js(page, "([a,s])=>coreNewOpen(a,{ticker:s})", [acct, sym]); settle(page, 450)


def setpx(page, entry, stop):
    js(page, "([e,s])=>{ document.getElementById('cnEntry').value = e; document.getElementById('cnStop').value = s; coreNewIn(); }", [str(entry), str(stop)]); settle(page, 250)


def banner(page):
    return js(page, "()=>({l1:(document.querySelector('[data-cs-l1]')||{}).innerText||'', l2:(document.querySelector('[data-cs-l2]')||{}).innerText||'', bud:(document.querySelector('[data-cs-budget]')||{}).innerText||'', miss:(document.querySelector('[data-cs-missing]')||{}).innerText||'', hint:(document.querySelector('[data-cs-hint]')||{}).innerText||'', edit:document.querySelectorAll('[data-cs-edit]').length})")


def form(page):
    return js(page, """()=>({qty:(document.querySelector('[data-lf-qty]')||{}).innerText||'', risk:document.getElementById('cnRisk').value, ro:document.getElementById('cnRisk').readOnly,
      save:document.getElementById('cnSave').disabled, tier:document.querySelectorAll('[data-c-tierblock], #cnTierBox, #tiRoic, #cnTierSel, #cnReason').length, err:(document.getElementById('cnErr')||{}).innerText||''})""")


def cards(page): return js(page, "()=>coreCardsList.map(c=>c.id)")


# ───────────────────────── 1 สูตรล้วน ─────────────────────────
def calc_tests(pw):
    tag = f"[{ENGINE}/calc]"
    b, page, ce, pe = core(pw)
    try:
        rows = [
            ("F+P", dict(fortress="passed", proven="passed"), 3, False), ("F+P+E+RS", dict(fortress="passed", proven="passed", emerging="passed", rs="passed"), 3, False),
            ("F only", dict(fortress="passed"), 2, False), ("P only", dict(proven="passed"), 2, False), ("F+E (ไม่บวกดาว)", dict(fortress="passed", emerging="passed"), 2, False),
            ("E only", dict(emerging="passed"), 1, False), ("E+RS", dict(emerging="passed", rs="passed"), 1, False),
            ("RS only", dict(rs="passed"), 1, True), ("F insufficient + RS", dict(fortress="insufficient", rs="passed"), 1, True),
            ("F failed + RS na", dict(fortress="failed", rs="na"), 0, False), ("ทุกอย่าง untested", dict(), 0, False),
            ("F failed P failed E failed RS failed", dict(fortress="failed", proven="failed", emerging="failed", rs="failed"), 0, False),
        ]
        out = js(page, """(rows)=>rows.map(([n,o])=>{ const rs = o.rs || 'untested'; const r = Calc.starsFromEval({fortress:o.fortress, proven:o.proven, emerging:o.emerging, rs:{sustained:rs, b26:'untested', b52:'untested'}}); return [n, r.stars, r.rsOnly, r.baseRisk]; })""", [[r[0], r[1]] for r in rows])
        for (n, o, st, ro), got in zip(rows, out):
            check(f"{tag} starsFromEval · {n} → {'★' * st or 'ไม่มีดาว'}{' · RS only' if ro else ''}", got[1] == st and got[2] == ro and got[3] == ({3: 1, 2: 0.75, 1: 0.5, 0: None}[st]), got)
        d = js(page, "()=>{ const e = Calc.evalNorm(null); const g = Calc.evalNorm({fortress:'weird', gate5:['passed']}); return {def:[e.fortress,e.proven,e.emerging,e.rs.sustained,e.rs.b26,e.rs.b52,...e.gate5,e.stars,e.stars_src], bad:[g.fortress, ...g.gate5]}; }")
        check(f"{tag} ค่าเริ่มต้น = untested ทุกช่อง (ไม่เคยถือว่าผ่าน) · ค่าแปลก → untested · stars_src='manual'", d["def"] == ["untested"] * 9 + [None, "manual"] and d["bad"] == ["untested", "passed", "untested", "untested"], d)
        for rsn in ("sustained", "b26", "b52"):
            r = js(page, "(k)=>Calc.evalRsPassed({rs:{[k]:'passed'}})", rsn)
            check(f"{tag} RS ผ่านเมื่อ {rsn} ผ่านข้อเดียว", r is True, r)
        g = js(page, """()=>[Calc.evalGate({rs:{sustained:'passed'}, gate5:['passed','passed','passed']}, 1), Calc.evalGate({rs:{sustained:'passed'}, gate5:['passed','passed','passed']}, 0),
            Calc.evalGate({rs:{b26:'passed'}, gate5:['passed','passed','untested']}, 2), Calc.evalGate({rs:{b52:'passed'}, gate5:['passed','failed','passed']}, 3), Calc.evalGate(null, 0)]""")
        check(f"{tag} evalGate: ★≥1+RS+Gate5 ครบ = ผ่าน", g[0]["ok"] is True and g[0]["missing"] == [], g[0])
        check(f"{tag} evalGate: ไม่มีดาว → Missing: Stars", g[1]["missing"] == ["Stars"], g[1])
        check(f"{tag} evalGate: Gate 5 ตอบ 2/3 → 'Gate 5 (2/3)'", g[2]["missing"] == ["Gate 5 (2/3)"], g[2])
        check(f"{tag} evalGate: Gate 5 ตอบ 'ใช่' → ติดธง (ไม่ผ่าน)", g[3]["ok"] is False and g[3]["missing"] == ["Gate 5 flagged (1 Yes)"], g[3])
        check(f"{tag} evalGate: ไม่มีอะไรเลย → Stars · RS · Gate 5 (0/3)", g[4]["missing"] == ["Stars", "RS", "Gate 5 (0/3)"], g[4])
        s = js(page, "()=>[Calc.starBudget({stars:2, equity:1000000, f:0.75, dd:1, used:3000}), Calc.starBudget({stars:3, equity:1000000, f:1, dd:0.5, used:99999999}), Calc.starBudget({stars:0, equity:1000}), Calc.starBudget({stars:1, equity:0})]")
        check(f"{tag} starBudget: ★★ 0.75% × 1,000,000 = 7,500 × FF 0.75 (ครั้งเดียว) = 5,625 − ใช้ 3,000 = เหลือ 2,625", abs(s[0]["full"] - 7500) < 1e-6 and abs(s[0]["adj"] - 5625) < 1e-6 and abs(s[0]["left"] - 2625) < 1e-6, s[0])
        check(f"{tag} starBudget: DD ×0.5 · ใช้เกินงบ → เหลือ 0 (ไม่ติดลบ) · ไม่มีดาว/ไม่มี equity → ok:false", abs(s[1]["adj"] - 5000) < 1e-6 and s[1]["left"] == 0 and s[2]["ok"] is False and s[3]["ok"] is False, s)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 2 ขนาดไม้ตาม ★ ─────────────────────────
def size_tests(pw, w=390, h=844):
    tag = f"[{ENGINE}/size/{w}]"
    b, page, ce, pe = core(pw, w, h)
    try:
        for stars, pct, qty in ((3, 1.0, 127), (2, 0.75, 95), (1, 0.5, 63)):
            sym = "S%d" % stars
            ok_ev(page, sym, stars=stars, f="passed" if stars > 1 else "untested", p="passed" if stars == 3 else "untested", e="passed" if stars == 1 else "untested")
            open_form(page, sym); setpx(page, 100, 90)
            bn, fm = banner(page), form(page)
            exp_l1 = "★" * stars + " · Base risk %.2f%% · Manual" % pct
            check(f"{tag} {'★' * stars}: แบนเนอร์ '{exp_l1}' · ไม้แรก {qty} หุ้น (Risk {pct}% × Core equity ${TANK:,.0f} ÷ 10, ปัดลง) · Risk % อ่านอย่างเดียว",
                  bn["l1"] == exp_l1 and fm["qty"].replace(",", "") == str(qty) and abs(float(fm["risk"]) - pct) < 1e-3 and fm["ro"] is True and fm["save"] is False, [bn, fm])
        ok_ev(page, "S3", stars=3)
        open_form(page, "S3"); setpx(page, 100, 90)
        bn = banner(page)
        check(f"{tag} บรรทัดที่ 2 = 'Fortress + Proven · RS Passed · Gate 5 clear' · งบ: Risk budget · used · this tranche (FF 100%)", bn["l2"] == "Fortress + Proven · RS Passed · Gate 5 clear" and bn["bud"].startswith("Risk budget $1,273 · used $0 · this tranche ≤ $1,273 (FF 100%)"), bn)
        check(f"{tag} ฟอร์มแผนไม่มี UI ประเมิน (Tier A/B · override · Fortress/Proven/Emerging · Gate 5 · ช่องตัวเลข fundamentals)", form(page)["tier"] == 0 and cnt(page, "#tiRoic, #tiNd, #tiFcf, [data-g5], [data-tk], #cnTierSel, #cnReason, #cnTierOnly") == 0, form(page))
        check(f"{tag} ฟอร์มยังมี: บัญชี · Ticker · กลยุทธ์ · Entry · Stop · ขนาดไม้ · ปุ่มบันทึก", cnt(page, "#cnAcctBox, #cnTicker, #cnStratBox, #cnEntry, #cnStop, #cnRes, #cnSave") == 7, "")
        fx = js(page, "()=>document.getElementById('cnAcct') ? [...document.querySelectorAll('#cnAcct option')].map(o=>o.textContent) : [document.getElementById('cnAcctBox').innerText]")
        check(f"{tag} แถวบัญชีในฟอร์มแผนแสดง 'Main' (ไม่ใช่ 'บัญชีหลัก')", all("บัญชีหลัก" not in x for x in fx) and any(x.startswith("Main") for x in fx), fx)
        # บันทึก → snapshot
        js(page, "()=>coreNewSave()"); settle(page, 900)
        c = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='S3'); return c ? JSON.parse(JSON.stringify(c)) : null; }")
        cs = (c or {}).get("cs") or {}
        check(f"{tag} บันทึกแผน → การ์ดมี snapshot cs (eval · วันที่ · ★3 · stars_src · Base 1% · riskAmt · ตัวปรับ FF/DD) และไม่เขียน tier*", c and cs.get("stars") == 3 and cs.get("baseRiskPct") == 1 and cs.get("stars_src") == "manual" and cs.get("eval", {}).get("fortress") == "passed" and cs.get("riskAmt") == 1270 and "adj" in cs and "tier" not in c and "tierInputs" not in c and abs(c["plan"]["risk"] - 1.0) < 1e-3, c)
        js(page, "()=>coreBuy1Open(coreCardsList.find(x=>x.ticker==='S3').id)"); settle(page, 400)
        dq = js(page, "()=>+document.getElementById('cbQty').value")
        js(page, "()=>document.getElementById('cbSave').click()"); settle(page, 900)
        lt = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='S3'); return [c.status, c.lots[0]]; }")
        check(f"{tag} ซื้อไม้ 1 จากแผน ★: จำนวนเริ่มต้น 127 · lots[0] risk 1 (Base ★★★) · การ์ดเป็น open", dq == 127 and lt[0] == "open" and lt[1]["qty"] == 127 and lt[1]["risk"] == 1, [dq, lt])
        # ไม่มีดาว
        n0 = len(cards(page))
        open_form(page, "NOSTAR"); setpx(page, 100, 90)
        bn, fm = banner(page), form(page)
        check(f"{tag} ไม่มีดาว/ยังไม่ประเมิน → 'No stars · Unassigned' + Missing: Stars · RS · Gate 5 (0/3) + ปุ่ม Edit Stock Evaluation · บันทึกไม่ได้", bn["l1"] == "No stars · Unassigned" and bn["miss"] == "Missing: Stars · RS · Gate 5 (0/3)" and bn["edit"] == 1 and fm["save"] is True, [bn, fm])
        js(page, "()=>coreNewSave()"); settle(page, 400)
        check(f"{tag} เรียก coreNewSave ตรง ๆ ขณะไม่ผ่านด่าน → ไม่สร้างการ์ด (กันทางลัด)", len(cards(page)) == n0, [n0, len(cards(page))])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 3 ด่านทุกเส้นทาง ─────────────────────────
def gate_tests(pw, w=390, h=844, shots=False):
    tag = f"[{ENGINE}/gate/{w}]"
    b, page, ce, pe = core(pw, w, h)
    try:
        ev(page, "GATE1", rs=("passed", "untested", "untested"), g5=("passed", "passed", "untested"), stars=3)
        open_form(page, "GATE1"); setpx(page, 50, 45)
        bn = banner(page)
        check(f"{tag} ข้อมูลไม่ครบ: แสดงสิ่งที่ขาด 'Missing: Gate 5 (2/3)' + ปุ่ม Edit Stock Evaluation · บันทึกไม่ได้", bn["miss"] == "Missing: Gate 5 (2/3)" and bn["edit"] == 1 and form(page)["save"] is True, [bn, form(page)])
        if shots: shot(page, "cs1-gate-390.png", ".ccSh")
        page.locator("[data-cs-edit]").first.click(); settle(page, 400)
        check(f"{tag} กด Edit Stock Evaluation › → เปิดฟอร์มประเมิน (ของ GATE1) · Gate 5 ข้อ 3 ยังเป็น Untested", cnt(page, "[data-cs-sheet]") == 1 and js(page, "()=>document.querySelector('[data-cs-sheet]').dataset.sym") == "GATE1" and js(page, "()=>document.querySelector('[data-cs-in=\"g5.2\"]').value") == "untested", "")
        if shots: shot(page, "cs1-eval-390.png", "[data-cs-sheet]")
        sel = js(page, "()=>[...document.querySelectorAll('[data-cs-in=\"g5.2\"] option')].map(o=>o.value+':'+o.textContent)")
        check(f"{tag} Gate 5 ตอบได้ Untested / No / Yes / Insufficient data (No = ผ่าน)", sel == ["untested:Untested", "passed:No", "failed:Yes", "insufficient:Insufficient data"], sel)
        page.select_option('[data-cs-in="g5.2"]', "failed"); settle(page, 150)
        sm = txt(page, "[data-cs-sum]")
        check(f"{tag} ตอบ 'Yes' → ติดธง ไม่ผ่าน ('Gate 5 flagged (1 Yes)')", "Gate 5 flagged (1 Yes)" in sm, sm)
        page.select_option('[data-cs-in="g5.2"]', "passed"); settle(page, 150)
        check(f"{tag} ตอบ 'No' ครบ 3 ข้อ → สรุป Ready", txt(page, "[data-cs-sum]").startswith("Ready"), txt(page, "[data-cs-sum]"))
        page.locator("[data-cs-save]").click(); settle(page, 500)
        bn, fm = banner(page), form(page)
        check(f"{tag} บันทึกการประเมินแล้วฟอร์มแผนคำนวณใหม่ทันที: ผ่านด่าน · บันทึกแผนได้ · ไม่มี Missing", cnt(page, "[data-cs-sheet]") == 0 and bn["miss"] == "" and fm["save"] is False and bn["l1"].startswith("★★★"), [bn, fm])
        # พิมพ์ ticker เอง
        js(page, "()=>{ const e = document.getElementById('cnTicker'); e.value = 'TYPED9'; coreNewIn(); }"); settle(page, 250)
        bn = banner(page)
        check(f"{tag} พิมพ์ ticker เอง (ไม่มีการประเมิน) → ติดด่านเหมือนกัน (ไม่มีทางลัด) · ไม่เหลือ ★/Risk ของหุ้นตัวก่อน", bn["l1"] == "No stars · Unassigned" and form(page)["save"] is True and form(page)["risk"] == "" and bn["bud"] == "", [bn, form(page)])
        # เส้นทาง Watch
        ev(page, "GATE2")
        js(page, "()=>{ coreSheetClose(); wlOpenCorePlan('GATE2'); }"); settle(page, 700)
        bn = banner(page)
        check(f"{tag} Watch › เปิดแผน Core → ฟอร์มพร้อม ticker · ติดด่านเดียวกัน (Missing …)", js(page, "()=>document.getElementById('cnTicker').value") == "GATE2" and bn["miss"].startswith("Missing:") and form(page)["save"] is True, bn)
        # Watch add / import ไม่สร้างตัวใหม่
        n0 = js(page, "()=>wlItems.length")
        r = js(page, "()=>{ try{ wlOpenAdd('BRANDNEW'); }catch(e){} const ov = document.getElementById('wlAddOverlay'); return [td4MayAdd('BRANDNEW'), ov && ov.classList.contains('show')]; }")
        check(f"{tag} Watch add ตัวใหม่ → ไม่เปิดฟอร์มเพิ่ม (ต้องเป็น Candidate + ผ่านด่านก่อน) · ไม่มีเอกสาร Watchlist ใหม่", r == [False, False] and js(page, "()=>wlItems.length") == n0, [r, n0])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def today_gate_tests(pw, w=390, h=844):
    tag = f"[{ENGINE}/today/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        P108.seed_cands(page); T.go_today(page)
        page.locator('[data-td3-cand="NEW1"] [data-td4-promote]').click(); settle(page, 300)
        f = js(page, "()=>({tier:document.querySelectorAll('[data-td4-pro-tier], [data-td4-pro-rs], [data-td3-tier], [data-td3-rs]').length, need:document.querySelector('[data-td4-need]').innerText, go:document.querySelector('[data-td4-pro-go]').disabled, line:document.querySelector('[data-cs-line]').innerText, edit:document.querySelectorAll('[data-td4-pro] [data-cs-edit]').length})")
        check(f"{tag} ฟอร์ม Cand → WL: ไม่มีช่องติ๊ก 'Tier passed' / 'RS Leader' แล้ว · มีบรรทัดสรุปการประเมิน + ปุ่ม Edit Stock Evaluation · Need: Stars · RS · Gate 5 (0/3)", f["tier"] == 0 and f["edit"] == 1 and f["go"] is True and f["need"] == "Need: Stars · RS · Gate 5 (0/3)" and f["line"].startswith("No stars"), f)
        page.fill("[data-td4-pro-note]", "why it passed"); page.locator('[data-td4-star="2"]').click(); settle(page, 200)
        need = txt(page, "[data-td4-need]")
        check(f"{tag} กด ★★ ที่ฟอร์ม → เขียนลงเรคคอร์ดประเมิน (แหล่งเดียว) · Need เหลือ RS · Gate 5", need == "Need: RS · Gate 5 (0/3)" and js(page, "()=>csStarsOf('NEW1')") == 2, need)
        page.locator("[data-td4-pro] [data-cs-edit]").click(); settle(page, 350)
        page.select_option('[data-cs-in="rs.b26"]', "passed")
        for i in range(3): page.select_option(f'[data-cs-in="g5.{i}"]', "passed")
        page.locator("[data-cs-save]").click(); settle(page, 500)
        st = js(page, "()=>({need:document.querySelector('[data-td4-need]').innerText, go:document.querySelector('[data-td4-pro-go]').disabled, stars:document.querySelectorAll('[data-td4-star].on').length, ev:csEvalOf('NEW1')})")
        check(f"{tag} ประเมินครบในชีตแล้วกลับมา → Ready · ★★ ยังอยู่ · Move to Watchlist กดได้", st["need"] == "Ready" and st["go"] is False and st["stars"] == 2 and st["ev"]["rs"]["b26"] == "passed", st)
        page.locator("[data-td4-pro-go]").click(); settle(page, 700)
        wl = js(page, "()=>{ const w = wlItems.find(x=>x.ticker==='NEW1'); return w ? {stars:w.stars, by:w.promoted_by} : null; }")
        check(f"{tag} ย้ายเข้า Watchlist: เอกสารมี ★2 · promoted_by=['rs'] · การประเมินยังอยู่ (ย้ายแล้วไม่หาย)", wl == {"stars": 2, "by": ["rs"]} and js(page, "()=>csEvalOf('NEW1').gate5.every(x=>x==='passed')"), wl)
        # หลังย้าย: แผนจาก Watch ผ่านด่านทันที
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); coreNewOpen(null, {ticker:'NEW1'}); }"); settle(page, 600)
        bn = banner(page)
        check(f"{tag} Candidate → Watchlist ไม่ต้องประเมินซ้ำ: เปิดแผน NEW1 ผ่านด่าน (★★ · Base risk 0.75%)", bn["l1"].startswith("★★ · Base risk 0.75%") and bn["miss"] == "", bn)
        # Pending Review (ไม่ลบ/ไม่ย้าย)
        n0 = js(page, "()=>wlItems.length")
        ev(page, "NEW1", rs=("failed", "failed", "failed"), g5=("passed",) * 3, stars=2)
        js(page, "()=>{ coreSheetClose(); switchTab('watch'); wlSetView('wl'); renderWatchlist(); }"); settle(page, 500)
        pend = js(page, "()=>({chip:document.querySelectorAll('[data-cs-pending]').length, still:wlItems.some(x=>x.ticker==='NEW1'), n:wlItems.length})")
        check(f"{tag} Watchlist เดิมที่ประเมินใหม่แล้วไม่ผ่าน → ติดป้าย 'Pending Review' ไม่ลบ ไม่ย้าย", pend["chip"] >= 1 and pend["still"] and pend["n"] == n0, pend)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 4 แชร์งบ + ไม่เก็บค่าข้ามหุ้น ─────────────────────────
def budget_tests(pw, w=390, h=844):
    tag = f"[{ENGINE}/budget/{w}]"
    tr = [P13.T("tB1", "core", "open", sym="AAPL", entry=100, sl=90, qty=60, cur="USD", date="2026-10-20")]   # เสี่ยง $600
    b, page, ce, pe = core(pw, w, h, tr)
    try:
        ok_ev(page, "AAPL", stars=3); ok_ev(page, "MSFT", stars=2)
        used = js(page, "()=>csUsedOther('main','AAPL',null)")
        check(f"{tag} ใช้ไปแล้ว: ตำแหน่ง AAPL ที่ถือ (60 × (100−90) = $600) นับเป็น used", abs(used - 600) < 1e-6, used)
        open_form(page, "AAPL"); setpx(page, 100, 90)
        bn, fm = banner(page), form(page)
        check(f"{tag} แผนใหม่ AAPL ★★★: งบ $1,273 − ใช้ $600 → tranche ≤ $673 → 67 หุ้น (ไม่แจกงบใหม่ซ้ำ)", bn["bud"].startswith("Risk budget $1,273 · used $600 · this tranche ≤ $673") and fm["qty"] == "67" and abs(float(fm["risk"]) - 0.5285) < 0.002, [bn, fm])
        # ใช้งบหมด
        js(page, "()=>{ const B=getBook('main'); B.trades[0].qty = 200; saveBook('main'); render(); }"); settle(page, 300)
        js(page, "()=>coreNewOpen('main',{ticker:'AAPL'})"); settle(page, 400); setpx(page, 100, 90)
        fm = form(page)
        check(f"{tag} ใช้งบเกิน/หมดแล้ว → บันทึกแผนใหม่ไม่ได้ ('Risk budget used up')", fm["save"] is True and "Risk budget used up" in fm["err"], fm)
        js(page, "()=>{ const B=getBook('main'); B.trades[0].qty = 60; saveBook('main'); render(); }"); settle(page, 300)
        # สลับหุ้น: ไม่ค้างค่า
        open_form(page, "AAPL"); setpx(page, 100, 90)
        js(page, "()=>{ document.getElementById('cnTicker').value = 'MSFT'; coreNewIn(); }"); settle(page, 300)
        bn, fm = banner(page), form(page)
        check(f"{tag} สลับ AAPL → MSFT: ★/Risk คำนวณใหม่ทั้งหมด (★★ · 0.75% · used $0 · ไม่ค้าง $600/★★★ ของ AAPL)", bn["l1"].startswith("★★ · Base risk 0.75%") and "used $0" in bn["bud"] and abs(float(fm["risk"]) - 0.75) < 1e-3, [bn, fm])
        js(page, "()=>{ document.getElementById('cnTicker').value = 'ZZZ'; coreNewIn(); }"); settle(page, 300)
        bn, fm = banner(page), form(page)
        check(f"{tag} สลับไปหุ้นที่ไม่มีดาว → ล้างหมด (No stars · Risk ว่าง · ไม่มีงบ)", bn["l1"] == "No stars · Unassigned" and fm["risk"] == "" and bn["bud"] == "", [bn, fm])
        # reload keeps eval
        js(page, "()=>{ snStop(); snMap = {}; snStart(); }"); settle(page, 800)
        e = js(page, "()=>csEvalOf('AAPL')")
        check(f"{tag} โหลดซ้ำ (ฟังข้อมูลใหม่จากเซิร์ฟเวอร์) → การประเมินของ AAPL ยังอยู่ครบ", e and e["fortress"] == "passed" and e["stars"] == 3 and e["gate5"] == ["passed"] * 3 and e["date"] == "2026-10-30", e)
        # การ์ดที่บันทึกแล้ว + เติมไม้ใช้งบร่วม + snapshot ไม่เปลี่ยน
        card = {"acct": "main", "ticker": "AAPL", "market": "US", "strategy": "W", "plan": {"entry": 100, "stop": 90, "risk": 1.0}, "stop": 90, "stopHistory": [], "px": 100, "pxDate": "2026-10-29", "emaW": 95,
                "lots": [{"n": 1, "date": "2026-10-20", "px": 100, "qty": 60, "f": 1, "stop": 90}], "trade_id": "tB1", "acc_trade_id": None, "status": "open", "created_at": "2026-10-20T00:00:00Z",
                "cs": {"eval": None, "date": "2026-10-20", "evalDate": "", "stars": 3, "stars_src": "manual", "baseRiskPct": 1.0, "riskAmt": 600, "equity": TANK, "used": 0, "budget": TANK * 0.01, "adj": {"ff": 1, "dd": 1}, "capKey": "A"}}
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", ["ccAA", card]); js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 800)
        r = js(page, "()=>{ const c = coreCardsList.find(x=>x.id==='ccAA'); const k = lfAddCalc(c, {acc:false, px:100, sl:90, risk:NaN, riskEdited:false}); return {max:k.maxRiskPct, tank:coreCtx('main').tankTHB/33, blocked:k.blocked, used:csUsedOther('main','AAPL','ccAA')}; }")
        exp = 1.0 - 600 / TANK * 100        # Base 1% − carry (60 × (100−90)) ของถัง
        check(f"{tag} เติมไม้ (ไม้ 2) ใช้งบก้อนเดียวกับไม้แรก: Risk ที่เติมได้ = 1% − เสี่ยงค้าง 600 = {exp:.4f}% ของถัง (ไม่ได้งบใหม่)", abs(r["max"] - exp) < 0.01 and r["used"] == 0, r)
        before = js(page, "()=>JSON.stringify(coreCardsList.find(x=>x.id==='ccAA').cs)")
        ok_ev(page, "AAPL", stars=1, f="untested", p="untested")      # แก้การประเมินทีหลัง
        after = js(page, "()=>JSON.stringify(coreCardsList.find(x=>x.id==='ccAA').cs)")
        r2 = js(page, "()=>{ const c = coreCardsList.find(x=>x.id==='ccAA'); const k = lfAddCalc(c, {acc:false, px:100, sl:90, risk:NaN, riskEdited:false}); return k.maxRiskPct; }")
        check(f"{tag} แก้ ★ ของ AAPL เป็น ★ ภายหลัง → snapshot ในแผนที่บันทึกไว้ไม่เปลี่ยน · ไม้เติมยังใช้ Base 1% เดิม", before == after and abs(r2 - exp) < 0.01, [before == after, r2])
        # แก้แผน: ไม่นับตัวเองซ้ำ
        used_ex = js(page, "()=>csUsedOther('main','AAPL','ccAA')"); used_in = js(page, "()=>csUsedOther('main','AAPL',null)")
        check(f"{tag} เสี่ยงของการ์ดที่กำลังแก้ไม่ถูกนับซ้ำ (ไม่รวมตัวเอง: used = 0 · รวมตัวเอง = $600)", used_ex == 0 and abs(used_in - 600) < 1e-6, [used_ex, used_in])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 5 แผน/ไม้เดิม (legacy) ─────────────────────────
def legacy_tests(pw, w=390, h=844):
    tag = f"[{ENGINE}/legacy/{w}]"
    cd = C.core_cards(False)
    b, page, ce, pe = C.launch(pw, w, h, cards=cd)
    try:
        C.go_core(page)
        r = js(page, """()=>{ const c = coreCardsList.find(x=>x.id==='ccNV'); const cx = coreCtx('main'); const v = coreView(c, cx); const k = lfAddCalc(c, {acc:false, px:130, sl:120, risk:NaN, riskEdited:false});
            return {cs:!!c.cs, tier:csTier(c), fort:coreIsFortress(c), max:k.maxRiskPct, html:coreCardHtml(v, cx).slice(0,4000)}; }""")
        check(f"{tag} การ์ด/ไม้เดิม (Tier A · ไม่มี cs) เปิดและเติมไม้ได้โดยไม่ต้องประเมินใหม่ · ยังเป็น Tier A · Fortress", r["cs"] is False and r["tier"] == "A" and r["fort"] is True and r["max"] > 0 and "Tier A" in r["html"] or "A · Winners" in r["html"], {k: r[k] for k in ("cs", "tier", "fort", "max")})
        r = js(page, """()=>{ const c = coreCardsList.find(x=>x.id==='ccAV'); const cx = coreCtx('main'); const v = coreView(c, cx); return {tier:csTier(c), first:coreFirstRisk(c, cx, 'B'), html:coreCardHtml(v, cx).length}; }""")
        check(f"{tag} แผนเดิม Tier B (ไม่มี cs) ยังคำนวณเดิม (ไม่ถูกแตะ)", r["tier"] == "B" and r["html"] > 100, r)
        js(page, "()=>coreNewOpen('main',{id:'ccNV', mode:'edit'})"); settle(page, 400)
        check(f"{tag} แก้แผนบันไดของการ์ดเดิมไม่ต้องประเมินใหม่: ไม่มีแบนเนอร์ประเมินในโหมดแก้ไข", js(page, "()=>document.getElementById('cnStarBox').style.display") == "none", "")
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 6 Sat ─────────────────────────
def sat_launch(pw, w, h):
    b, page, ce, pe = P77.launch(pw, w, h)
    js(page, "()=>{ ln1SetMode('lean'); render(); }"); settle(page, 400)
    return b, page, ce, pe


def sat_tests(pw, w=390, h=844):
    tag = f"[{ENGINE}/sat/{w}]"
    b, page, ce, pe = sat_launch(pw, w, h)
    try:
        iid = js(page, "()=>satV2NewPlan('XAUUSD','main')"); settle(page, 500)
        opts = js(page, "()=>[...document.querySelectorAll('[data-pf-classify-sel] option')].map(o=>o.value+':'+o.textContent)")
        check(f"{tag} Classify เหลือแค่ Clear Trend / Unclear", opts == [":— เลือก —", "clear:Clear Trend", "unclear:Unclear"], opts)
        m = js(page, """()=>({a:pfClsKey('strong'), b:pfClsKey('normal'), c:pfClsKey('uncertain'), d:pfClsKey('clear'), e:pfClsKey('unclear'), f:pfClsKey(''), g:pfClsKey('x')})""")
        check(f"{tag} ค่าเก่า strong/normal → clear · uncertain → unclear (แมปตอนอ่าน)", m == {"a": "clear", "b": "clear", "c": "unclear", "d": "clear", "e": "unclear", "f": "", "g": ""}, m)
        t = js(page, """([i])=>{ const o = {}; ['strong','normal','uncertain','clear','unclear'].forEach(k=>{ satV3IdeaWrite(i,{classify:k}); }); return null; }""", [iid])
        outs = []
        for k in ("strong", "normal", "uncertain"):
            js(page, "([i,k])=>{ satV3IdeaWrite(i,{classify:k}); satV3Render({force:true}); }", [iid, k]); settle(page, 350)
            outs.append([k, js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); return [pfClassifyHtml(x).replace(/<[^>]+>/g,''), (document.querySelector('[data-pf-classify-sel]')||{}).value, x.classify]; }", [iid])])
        check(f"{tag} ข้อมูลเก่าแสดงชื่อใหม่ (Strong/Normal → Clear Trend · Uncertain → Unclear) และเลือกค่าในช่อง; ยังไม่เขียนทับจนกว่าจะบันทึกใหม่", [o[1][0] for o in outs] == ["Clear Trend", "Clear Trend", "Unclear"] and [o[1][1] for o in outs] == ["clear", "clear", "unclear"] and [o[1][2] for o in outs] == ["strong", "normal", "uncertain"], outs)
        js(page, "([i])=>{ satV3IdeaWrite(i,{classify:''}); }", [iid]); settle(page, 300)
        # Tactical ต้อง Clear Trend (ไม่มี Main)
        tid = js(page, "()=>satV2NewPlan('XAUUSD','tactical')"); settle(page, 500)
        js(page, "([i])=>{ satV2SetDir(i,'Long'); }", [tid]); settle(page, 300)
        def tfield(): return js(page, "([i])=>{ const f = document.querySelector('[data-v2-card=\"tactical\"]'); if(!f) return null; return {entry:f.querySelector('[data-v2-entry]').disabled, sl:f.querySelector('[data-v2-sl]').disabled, tp:f.querySelector('[data-pf-tp]').disabled, setups:[...f.querySelectorAll('[data-pf-setup]')].map(e=>e.disabled), hint:!!document.querySelector('[data-cs-tac-hint]'), cls:f.querySelector('[data-pf-classify-sel]').disabled}; }", [tid])
        f0 = tfield()
        check(f"{tag} Tactical + Classify ยังไม่เป็น Clear Trend (ไม่มี Main): Setup 3 ข้อ + Entry/SL/TP ปิด · มี hint 'Tactical needs Clear Trend' · ช่อง Classify ยังเลือกได้", f0 and f0["entry"] and f0["sl"] and f0["tp"] and all(f0["setups"]) and len(f0["setups"]) == 3 and f0["hint"] and not f0["cls"], f0)
        txtHint = txt(page, "[data-cs-tac-hint]")
        check(f"{tag} ข้อความ hint = 'Tactical needs Clear Trend'", txtHint == "Tactical needs Clear Trend", txtHint)
        js(page, "([i])=>{ satV3IdeaWrite(i,{classify:'unclear', entry:4180, sl:4117, tp:4306}); satV3Render({force:true}); }", [tid]); settle(page, 400)
        c = js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x,'main'); return {blocks:c.blocks, ready:c.ready}; }", [tid])
        n0 = len(P78.trades(page))
        P78.save(page, tid)
        check(f"{tag} Unclear → บล็อก 'Tactical needs Clear Trend' · ready=false · บันทึกไม่ได้ (ไม่สร้างไม้)", "Tactical needs Clear Trend" in c["blocks"] and c["ready"] is False and len(P78.trades(page)) == n0, [c, n0])
        ps = js(page, "([i])=>td3PlanStatus(satIdeasList.find(y=>y.id===i))", [tid])
        check(f"{tag} Today Sat: สถานะ Pending 'Needs Clear Trend'", ps and ps["k"] == "pending" and ps["list"] == ["Needs Clear Trend"], ps)
        js(page, "([i])=>{ satV3IdeaWrite(i,{classify:'clear'}); satV3Render({force:true}); }", [tid]); settle(page, 400)
        f1 = tfield()
        c = js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x,'main'); return {blocks:c.blocks, ready:c.ready, lot:c.lot}; }", [tid])
        check(f"{tag} Clear Trend → ปลดล็อก: ช่อง/Setup เปิด · ไม่มีบล็อก Clear Trend · คำนวณไม้ได้", f1 and not f1["entry"] and not any(f1["setups"]) and not f1["hint"] and "Tactical needs Clear Trend" not in c["blocks"] and c["lot"] is not None, [f1, c])
        # ตัวเดียวกัน: มี Main อยู่แล้ว (เปิด Tactical ได้ แต่ต้อง Clear Trend ก่อน)
        P78.put(page, [P78.sat_t("tm1", "open", sleeve="main")])
        js(page, "([i])=>{ satV3IdeaWrite(i,{classify:''}); satV3Render({force:true}); }", [tid]); settle(page, 400)
        f2 = tfield(); c = js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x,'main'); return {blocks:c.blocks, ready:c.ready}; }", [tid])
        check(f"{tag} มี Main อยู่แล้ว → Tactical ก็ยังต้อง Clear Trend ก่อนวางแผน (ช่อง/Setup ปิด · บล็อก)", f2 and f2["entry"] and all(f2["setups"]) and "Tactical needs Clear Trend" in c["blocks"], [f2, c])
        # Tactical เข้าแล้ว + ไม่มี Main → Main ใหม่สร้างไม่ได้
        P78.put(page, [P78.sat_t("tt1", "open", sleeve="tactical", qty=0.05)])
        n0 = js(page, "()=>satIdeasList.length")
        r = js(page, "()=>[satV2NewPlan('XAUUSD','main'), satMainBlockedFor('XAUUSD'), satMainBlockMsg('XAUUSD')]")
        check(f"{tag} Tactical เข้าแล้ว + ไม่มี Main → สร้างแผน Main ไม่ได้ (+ แผน) · ข้อความ 'Close the Tactical (XAU) first'", r[0] is None and r[1] is True and r[2] == "Close the Tactical (XAU) first", r)
        nm = lambda: js(page, "()=>satIdeasList.filter(x=>x.v2 && x.asset==='XAUUSD' && x.sleeve!=='tactical' && x.status!=='closed').length")
        m0 = nm(); js(page, "()=>{ td3SatCreate('XAUUSD','main'); }"); settle(page, 400)
        check(f"{tag} Today › Create plan › ก็บล็อกเหมือนกัน (ไม่เกิดแผน Main ใหม่)", nm() == m0, [m0, nm()])
        mid = js(page, "()=>{ const o = satIdeasList.find(x=>x.v2 && x.asset==='XAUUSD' && x.sleeve==='tactical'); return o && o.id; }")
        js(page, "([i])=>{ sat7dWrite('satIdeas', 'i999', {v3:true, v2:true, sleeve:'main', asset:'XAUUSD', bias:'Long', week:wpWeekKey(), entry:4180, sl:4117, tp:4306, tf:'D', setups:[], status:'active', accts:{}, created_at:new Date().toISOString()}); }", [mid]); settle(page, 600)
        c = js(page, "()=>{ const x = satIdeasList.find(y=>y.id==='i999'); const c = satV3PlanAcctCalc(x,'main'); return {blocks:c.blocks, ready:c.ready}; }")
        check(f"{tag} แผน Main ที่หลุดเข้ามา (เช่น import) ก็บันทึกไม่ได้: บล็อก 'Close the Tactical (XAU) first'", "Close the Tactical (XAU) first" in c["blocks"] and c["ready"] is False, c)
        # ปุ่ม Main disabled ในฟอร์ม
        js(page, "()=>{ lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 500)
        dis = js(page, "()=>{ const b = document.querySelector('#satV3Panel [data-sleeve=\"main\"]'); return b ? [b.disabled, !!document.querySelector('[data-cs-main-block]')] : null; }")
        check(f"{tag} ฟอร์มแผน: ปุ่ม Main disabled + hint 'Close the Tactical (XAU) first'", dis == [True, True], dis)
        # ลำดับ: มี Main อยู่ → ไม่บล็อก
        P78.put(page, [P78.sat_t("tm2", "open", sleeve="main", qty=0.04), P78.sat_t("tt2", "open", sleeve="tactical", qty=0.05)])
        r = js(page, "()=>satMainBlockedFor('XAUUSD')")
        pc = P79.pyr_calc(page, "tm2", 4200, 4130)
        check(f"{tag} มี Main อยู่แล้ว → ไม่บล็อก · เติมไม้ Main เดิม (pyramid) ยังทำได้ (ไม่มี error)", r is False and not pc["errs"], [r, pc])
        P78.put(page, [P78.sat_t("tt3", "plan", sleeve="tactical", qty=0.05)])
        r = js(page, "()=>satMainBlockedFor('XAUUSD')")
        check(f"{tag} Tactical ที่ยังไม่เข้า (แผนเฉย ๆ) ไม่บล็อก Main", r is False, r)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 7 กว้าง + ภาพ ─────────────────────────
def width_tests(pw):
    for w, h in ((300, 800), (390, 844), (1440, 900)):
        tag = f"[{ENGINE}/width/{w}]"
        b, page, ce, pe = core(pw, w, h)
        try:
            ok_ev(page, "VIS1", stars=3)
            ev(page, "VIS2", rs=("passed", "untested", "untested"), g5=("passed", "passed", "untested"), stars=2)
            for sym in ("VIS1", "VIS2"):
                js(page, "()=>coreSheetClose()")
                js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); }"); settle(page, 300)
                open_form(page, sym); setpx(page, 100, 90)
                o = C.overflow(page)
                inner = js(page, "()=>{ const s = document.querySelector('.ccSh'); return s ? s.scrollWidth - s.clientWidth : 0; }")
                check(f"{tag} ฟอร์มแผน ({sym}) ไม่ล้นแนวนอน", not o and inner <= 1, [o, inner])
                if w == 390 and sym == "VIS1": shot(page, "cs1-plan-390.png", ".ccSh")
                if w == 1440 and sym == "VIS1": shot(page, "cs1-plan-1440.png")
            js(page, "()=>csEvalOpen('VIS2')"); settle(page, 400)
            o = C.overflow(page); inner = js(page, "()=>{ const s = document.querySelector('.csSh'); return s ? s.scrollWidth - s.clientWidth : -1; }")
            check(f"{tag} ชีต Edit Stock Evaluation ไม่ล้นแนวนอน", not o and inner <= 1, [o, inner])
            if w == 390: shot(page, "cs1-eval-390.png", ".csSh")
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()
    # gate ภาพ
    b, page, ce, pe = core(pw, 390, 844)
    try:
        ev(page, "GATE1", rs=("passed", "untested", "untested"), g5=("passed", "passed", "untested"), stars=3)
        open_form(page, "GATE1"); setpx(page, 50, 45); shot(page, "cs1-gate-390.png", ".ccSh")
    finally: b.close()


SECTIONS = {
    "calc": calc_tests,
    "size": lambda pw: [size_tests(pw, 390), size_tests(pw, 1440, 900)],
    "gate": lambda pw: [gate_tests(pw, 390), gate_tests(pw, 1440, 900), today_gate_tests(pw, 390)],
    "budget": lambda pw: budget_tests(pw, 390),
    "legacy": lambda pw: legacy_tests(pw, 390),
    "sat": lambda pw: [sat_tests(pw, 390), sat_tests(pw, 1440, 900)],
    "width": width_tests,
}


def main():
    want = os.environ.get("SECT", " ".join(SECTIONS)).split()
    with sync_playwright() as pw:
        for k in want: SECTIONS[k](pw)
    print("LOG " + json.dumps(LOG, ensure_ascii=False))
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
