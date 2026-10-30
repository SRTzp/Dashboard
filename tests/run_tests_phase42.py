#!/usr/bin/env python3
"""NUM1 — เก็บกวาดตัวเลข 7 จุด (การ์ดแผน Sat USD · BE/WIN · ฿-0 · 0 ตัวรอสร้าง Thesis · ตัวที่อ่อนสุด 0 ตัว · คำ f · ตาราง Thesis 390px) · เทส 42
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอมแบบชุดก่อน (P37 = 2026-10-01 · P41 = 2026-10-03) · fixture tests/fixtures/avgo_thesis_v3.json
ภาพ tests/screenshots/num1-{sat-plan-usd,journal-be,thesis-table}-{1440,390}.png
รัน: python3 run_tests_phase42.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase24 as p24
import run_tests_phase27 as p27
import run_tests_phase37 as P37
import run_tests_phase41 as P41
from run_tests_phase11 import fresh, reset_ideas, idea

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js, T = P37.js, P37.T
P40 = P41.P40


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


def txt(page, sel):
    return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)


def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")


NEG0 = re.compile(r"฿\s*[-−]\s*0(?![\d.,])")


# ───────────────────────── 1 · การ์ดแผน Sat USD / THB ─────────────────────────
def sat_plan_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, context, page, ce, pe = fresh(pw, w, h)
    page.evaluate("()=>{ ['main','fam'].forEach(a=>{ const B = getBook(a); if(B){ if(!B.settings) B.settings = {}; B.settings.satPyrSplit = [100,0,0]; saveBook(a); } }); }")   # PY2: เคสนี้ตรวจรูปแบบ $/฿ ไม่ใช่การแบ่งไม้ → 100/0/0 (ไม้ 1 เต็ม RPT)
    context.add_init_script("window.SAT_MR_ENABLED = true;"); page.evaluate("() => { window.SAT_MR_ENABLED = true; }")
    try:
        page.evaluate("() => switchTab('flow')")
        p5.goto_sat(page)
        # ── การ์ดจริง: XM = USD · MR → factor 0.6 (SAT_MACRO_CUT)
        reset_ideas(page); p27.setup_week(page)
        p27.mk(page, "iM", active=None)
        js(page, "()=>satV3CondActivate('iM','c2',true)"); page.wait_for_timeout(350)
        js(page, "()=>{ satV3Open.add('iM'); satV3Render(); }"); page.wait_for_timeout(250)
        C = '.ui-plan[data-id="iM"]'
        page.fill(f'{C} .ui-plan-nums div:nth-child(1) input', "2410"); page.keyboard.press("Tab")
        page.fill(f'{C} .ui-plan-nums div:nth-child(2) input', "2390"); page.keyboard.press("Tab")
        page.evaluate("()=>{ if(document.activeElement && document.activeElement.blur) document.activeElement.blur(); }"); page.wait_for_timeout(350)
        a = p27.acct(page)
        row = txt(page, f"{C} .ui-plan-accts") or ""
        usd_full = a["riskCur"]
        thb_full = js(page, "()=>satV3PlanAcctCalc(sat7dIdea('iM'),'main').base.riskTHB")
        exp_usd = f"${round(usd_full * a['factor']):,}"; exp_thb = f"≈฿{round(thb_full * a['factor']):,}"
        check(f"{tag} 1 บัญชี USD (XM) → '$x · ≈฿y' · ตัวหลัก $ = riskCur×factor ({exp_usd}) · ตัวเล็ก {exp_thb}", exp_usd in row and exp_thb in row, row)
        check(f"{tag} 1 ไม่มี ฿ หน้าเลข USD (ไม่มี '฿{round(usd_full * a['factor']):,}' ที่ไม่ใช่ ≈฿)", not re.search(r"(?<!≈)฿" + re.escape(f"{round(usd_full * a['factor']):,}") + r"(?![\d,])", row) or exp_usd.replace("$", "฿") == exp_thb.replace("≈", ""), row)
        check(f"{tag} 1 ป้าย 'ลด 40%' เหมือนเดิม (factor 0.6)", "ลด 40%" in row, row)
        shot(page, f"num1-sat-plan-usd-{sfx}.png", C)
        # ── adapter ตรง ๆ: THB · USD factor 1 / 0.5 (ค่า factor ในระบบจริงมีแค่ 1 กับ 0.6 → ใช้ stub ตรวจสัดส่วน 0.5)
        res = js(page, """()=>{
          const idea = {asset:'XAUUSD'}, orig = satV3PlanAcctCalc, out = {};
          const mkc = (cur, factor) => ({lot:0.19, chosen:{broker:'XM', cfg:{cur}}, riskCur: cur==='USD'?325:11050, base:{riskTHB:11050}, factor});
          const run = (cur, factor) => { satV3PlanAcctCalc = ()=>mkc(cur, factor); try{ return satV3PlanAdapter.sizeLine({_idea:idea, _skipSet:new Set()}, {id:'main'}); } finally { satV3PlanAcctCalc = orig; } };
          out.usd1 = run('USD',1); out.usd5 = run('USD',0.5); out.thb1 = run('THB',1); out.thb5 = run('THB',0.5);
          // privacy: เอาผลเข้า container data-priv แล้วใช้ privMaskIn ตัวจริง
          const host = document.createElement('div'); host.innerHTML = out.usd1; privMaskIn(host); out.maskUsd = host.innerText;
          const h2 = document.createElement('div'); h2.innerHTML = out.thb1; privMaskIn(h2); out.maskThb = h2.innerText;
          return out; }""")
        plain = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))
        u1, u5, t1, t5 = plain(res["usd1"]), plain(res["usd5"]), plain(res["thb1"]), plain(res["thb5"])
        check(f"{tag} 1 USD factor 1 → '$325 · ≈฿11,050'", "$325 · ≈฿11,050" in u1, u1)
        check(f"{tag} 1 USD factor 0.5 → ทั้งสองตัวครึ่งหนึ่ง '$163 · ≈฿5,525' + ลด 50%", "$163 · ≈฿5,525" in u5 and "ลด 50%" in u5, u5)
        check(f"{tag} 1 บัญชี THB → '฿11,050' ตัวเดียว (ไม่มี $ · ไม่มี ≈) · factor 0.5 → ฿5,525", "฿11,050" in t1 and "$" not in t1 and "≈" not in t1 and "฿5,525" in t5 and "$" not in t5, t1 + " | " + t5)
        check(f"{tag} 1 privacy: USD → '$XXX · ≈฿XX,XXX' · THB → '฿XX,XXX' (ซ่อนทั้ง $ และ ฿)", "$XXX · ≈฿XX,XXX" in res["maskUsd"] and "฿XX,XXX" in res["maskThb"] and not re.search(r"\d", re.sub(r"0\.19", "", res["maskUsd"] + res["maskThb"]).replace("XM", "")), json.dumps([res["maskUsd"], res["maskThb"]], ensure_ascii=False))
        check(f"{tag} 1 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()


# ───────────────────────── 2–3 · BE/WIN · ฿-0 ─────────────────────────
def pnl_trade(i, pnl, port="core", **kw):
    """P&L (บาท) = pnl · core THB: entry 100 qty 1 exit 100+pnl"""
    return T(f"p{i}", port, "closed", sym=f"S{i}", entry=100, sl=90, qty=1, exitPrice=round(100 + pnl, 4), exitDate="2026-09-25", cur="THB",
             date="2026-09-10", openedAt="2026-09-10", **kw)


def journal_text(page): return txt(page, "#tab-journal") or js(page, "()=>document.body.innerText.replace(/\\s+/g,' ')")


def rows_syms(page):
    return js(page, "()=>[...document.querySelectorAll('#jContent_closed tr[data-trade], #jContent_closed .tcard')].map(e=>e.innerText.replace(/\\s+/g,' ').trim().split(' ')[0])")


def journal_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, context, page, ce, pe, dialogs = P37.launch(pw, w, h, P37.doc37(), cards={})
    try:
        # ───── 2 · BE/WIN ─────
        P37.put_trades(page, "main", [pnl_trade(1, 0.4), pnl_trade(2, -0.4), pnl_trade(3, 0), pnl_trade(4, 1), pnl_trade(5, -1)])
        js(page, "()=>{ switchTab('journal'); setJFilter('all'); }"); page.wait_for_timeout(350)
        view = lambda: js(page, "()=>{ const o=[]; document.querySelectorAll('#jContent_closed tr, #jContent_closed .tcard').forEach(e=>o.push(e.innerText.replace(/\\s+/g,' ').trim())); return o; }")
        tags = {}
        for r in view():
            m = re.match(r"^(?:\S+ )?.*?\b(S[1-5])\b.*?\b(WIN|LOSS|BE)\b", r)
            if m: tags[m.group(1)] = m.group(2)
        check(f"{tag} 2 ป้าย +0.4/−0.4/0/+1/−1 = BE BE BE WIN LOSS", [tags.get(f"S{i}") for i in range(1, 6)] == ["BE", "BE", "BE", "WIN", "LOSS"], json.dumps(tags))
        outc = js(page, "()=>state.trades.filter(t=>t.status==='closed').sort((a,b)=>a.id.localeCompare(b.id)).map(t=>pnlOutcome(t))")
        check(f"{tag} 2 pnlOutcome(t) ตรงกับป้ายทุกไม้", outc == ["be", "be", "be", "win", "loss"], json.dumps(outc))

        def filt(f):
            js(page, "(f)=>setJFilter(f)", f); page.wait_for_timeout(300)
            return sorted(set(re.findall(r"\bS[1-5]\b", " ".join(view()))))
        check(f"{tag} 2 ตัวกรอง Win = มีแค่ +1 (S4) · ไม่มีแถว BE", filt("win") == ["S4"], json.dumps(filt("win")))
        check(f"{tag} 2 ตัวกรอง Loss = มีแค่ −1 (S5)", filt("loss") == ["S5"], json.dumps(filt("loss")))
        js(page, "()=>setJFilter('all')"); page.wait_for_timeout(300)
        wr = txt(page, '[data-sum="win"]') or ""
        st = js(page, "()=>{ const s=journalStats().overall; return {n:s.n, wins:s.wins, wr:s.winRate}; }")
        check(f"{tag} 2 Win Rate = 1/5 = 20% (บล็อกสรุป + journalStats · BE อยู่ในตัวหาร)", st == {"n": 5, "wins": 1, "wr": 20} and "20%" in wr, json.dumps([st, wr]))
        g = js(page, "()=>jSetupGroups(journalStats().closed).map(g=>({label:g.label, n:g.n, wr:g.winRate}))")
        check(f"{tag} 2 สถิติตาม setup ตรงกัน (ทุกกลุ่มที่นับ 5 ไม้ → Win% = 20)", g and all(x["n"] == 5 and x["wr"] == 20 for x in g), json.dumps(g, ensure_ascii=False))
        shot(page, f"num1-journal-be-{sfx}.png")
        check(f"{tag} 2 ไม่มี console error (Journal BE)", not ce and not pe, json.dumps([ce, pe]))

        # ───── 3 · ฿-0 ─────
        # (ก) รวม −0.3 · นอกแผน (unplanned) → ข้อความ 'ไม้นอกแผน … P&L ฿0'
        P37.put_trades(page, "main", [pnl_trade(1, -0.3, unplanned=True)])
        js(page, "()=>{ switchTab('journal'); setJFilter('all'); }"); page.wait_for_timeout(400)
        full = js(page, "()=>document.getElementById('tab-journal') ? document.getElementById('tab-journal').innerText.replace(/\\s+/g,' ') : document.body.innerText.replace(/\\s+/g,' ')")
        pnl_cell = txt(page, '[data-sum="pnl"]') or ""
        check(f"{tag} 3 รวม −0.3 → บล็อกสรุป P&L = '฿0' ไม่มี -0 · ไม่มีป้ายขาดทุน", "฿0" in pnl_cell and "-0" not in pnl_cell and "ขาดทุน" not in pnl_cell and "กำไร" not in pnl_cell, pnl_cell)
        dec = txt(page, '[data-jsum="decision"]') or ""
        check(f"{tag} 3 ข้อความไม้นอกแผน → 'P&L ฿0'", "ไม้นอกแผน 1 ไม้" in dec and "P&L ฿0" in dec and not NEG0.search(dec), dec)
        ports = txt(page, "#jPorts") or ""
        setups = txt(page, "#setupBody") or ""
        check(f"{tag} 3 สถิติ port + สถิติตาม setup ไม่มี '฿-0'", not NEG0.search(ports) and not NEG0.search(setups) and "฿0" in ports and "฿0" in setups, json.dumps([ports, setups], ensure_ascii=False))
        check(f"{tag} 3 ทั้งหน้า Journal ไม่มี '฿-0' / '-฿0'", not NEG0.search(full) and "-฿0" not in full and "−฿0" not in full, "".join(NEG0.findall(full)))
        # (ข) Setup ไม่ครบ (setup_incomplete) → 'P&L ฿0'
        P37.put_trades(page, "main", [pnl_trade(1, -0.3, setup_incomplete=True)])
        js(page, "()=>{ switchTab('journal'); setJFilter('all'); }"); page.wait_for_timeout(400)
        dec = txt(page, '[data-jsum="decision"]') or ""
        check(f"{tag} 3 ข้อความ Setup ไม่ครบ → 'P&L ฿0'", "Setup ไม่ครบ 1 ไม้" in dec and "P&L ฿0" in dec and not NEG0.search(dec), dec)
        # (ค) ไม้ −0.3 + ไม้ +0.1 (รวมยัง ≈ 0) · ผลจริงติดลบ −5 ยังขึ้น ฿-5 + ป้ายขาดทุน (ไม่กระทบกรณีปกติ)
        P37.put_trades(page, "main", [pnl_trade(1, -5)])
        js(page, "()=>{ switchTab('journal'); setJFilter('all'); }"); page.wait_for_timeout(400)
        pnl_cell = txt(page, '[data-sum="pnl"]') or ""
        check(f"{tag} 3 ขาดทุนจริง −5 → '฿-5' + ป้ายขาดทุนยังขึ้น (กรณีปกติไม่เปลี่ยน)", "฿-5" in pnl_cell and "ขาดทุน" in pnl_cell, pnl_cell)
        check(f"{tag} 3 ไม่มี console error (฿-0)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()


# ───────────────────────── 4 · Watchlist ตัวรอสร้าง Thesis ─────────────────────────
def wl_status_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    def run(syms_with, syms_without):
        def ex(pg):
            for s in syms_with: P40.seed_wl(pg, s, P40.fx(s))
            for s in syms_without: P40.seed_wl(pg, s, None)
        return P40.launch(pw, w, h, ex, iso=P41.CLK)
    browser, context, page, ce, pe, dialogs = run(["AVGO", "NVDA"], [])
    try:
        P40.go_watch(page); page.wait_for_timeout(300)
        n = js(page, "()=>document.querySelectorAll('.wlStat').length")
        body = js(page, "()=>document.body.innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 4 Watchlist ทุกตัวมี Thesis → ไม่มีคำ 'ตัวรอสร้าง Thesis' · ไม่มีแถวว่าง", "ตัวรอสร้าง Thesis" not in body and n == 0, json.dumps([n]))
        check(f"{tag} 4 ไม่มี console error (ครบ)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()
    browser, context, page, ce, pe, dialogs = run(["AVGO"], ["NVDA", "MSFT"])
    try:
        P40.go_watch(page); page.wait_for_timeout(300)
        t = txt(page, ".wlStat") or ""
        check(f"{tag} 4 มี 2 ตัวไม่มี Thesis → '2 ตัวรอสร้าง Thesis'", "2 ตัวรอสร้าง Thesis" in t, t)
        check(f"{tag} 4 ไม่มี console error (2 ตัว)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()


# ───────────────────────── 5 · DD Core ตัวที่อ่อนสุด ─────────────────────────
def dd_weak_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = P37.launch(pw, w, h, P37.doc37(), cards={})
    try:
        P37.fx_core(page); P37.go_core(page)
        tr = lambda tid, sym, sl, **kw: T(tid, "core", "open", sym=sym, entry=100, sl=sl, qty=100, date="2026-09-10", openedAt="2026-09-10", **kw)
        # ไม่มีการ์ด/ราคา → ddWeakest ว่าง · DD ≥ เกณฑ์ จากไม้ปิดขาดทุน
        P37.clear_cards(page)
        P37.put_trades(page, "main", [P37.closed("c1", pnl=-150000), tr("tw1", "W1.BK", 70, sl0=90)])
        P37.set_dd(page, "main", "core", P37.ds0(700000))
        e = P37.dd(page, "main", "core")
        P37.open_sheet(page, "main", "core")
        t = txt(page, "[data-dd-weak]") or ""
        check(f"{tag} 5 DD ≥ เกณฑ์ + ไม่มีราคา (stage={e['stage']}) → 'ตัวที่อ่อนสุด — ยังเลือกไม่ได้' + 'ไม่มีตัวที่มีราคาปิดสัปดาห์ — อัปเดตราคาก่อน'",
              e["stage"] == "pause" and "ตัวที่อ่อนสุด — ยังเลือกไม่ได้" in t and "ไม่มีตัวที่มีราคาปิดสัปดาห์ — อัปเดตราคาก่อน" in t, t)
        check(f"{tag} 5 ไม่มี '0 ตัว' · ไม่มี 'ไม่มีตัวที่มีราคา' แบบเดิมโดดๆ", "0 ตัว" not in t and not re.search(r"ไม่มีตัวที่มีราคา(?!ปิดสัปดาห์)", t), t)
        shot(page, f"num1-dd-weak-none-{label.replace('px', '')}.png", ".core-sheet .ui-sheet")
        js(page, "()=>coreSheetClose()")
        # มีราคา 3 ตัว → รายชื่อเหมือนเดิม
        mk = lambda cid, tk, px, sl, **kw: p24.open_card(cid, "t" + cid, ticker=tk, qty=100, entry=100, sl=sl, px=px, pxDate="2026-09-25", emaW=50, tier="A", **kw)
        P37.seed_cards(page, {"w1": mk("w1", "W1.BK", 80, 70), "w2": mk("w2", "W2.BK", 85, 70), "w3": mk("w3", "W3.BK", 92, 70)})
        P37.put_trades(page, "main", [P37.closed("c1", pnl=-150000), tr("tw1", "W1.BK", 70, sl0=90), tr("tw2", "W2.BK", 70, sl0=90), tr("tw3", "W3.BK", 70, sl0=90)])
        P37.set_dd(page, "main", "core", P37.ds0(700000))
        P37.open_sheet(page, "main", "core")
        t = txt(page, "[data-dd-weak]") or ""
        rows = js(page, "()=>[...document.querySelectorAll('[data-dd-weakrow]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim().split(' ·')[0])")
        check(f"{tag} 5 มีราคา 3 ตัว → 'ตัวที่อ่อนสุด 3 ตัว — ทบทวน ลดตัวอ่อนสุด — คุณตัดสินใจเอง' + รายชื่อ 3 ตัวเหมือนเดิม", "ตัวที่อ่อนสุด 3 ตัว" in t and "ทบทวน ลดตัวอ่อนสุด — คุณตัดสินใจเอง" in t and len(rows) == 3 and "ยังเลือกไม่ได้" not in t, json.dumps([t, rows], ensure_ascii=False))
        check(f"{tag} 5 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()


# ───────────────────────── 6 · คำ f ตอนไม่มี Fund-flow ─────────────────────────
def ff_word_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = P37.launch(pw, w, h, P37.doc37(), cards={})
    try:
        # ไม่มี fundflow.json (stub คืน {}) → ไม่ set ff · demo
        js(page, "async ()=>{ window.__FF_JSON = {}; await ffLoadJson(true); render(); }"); page.wait_for_timeout(300)
        P37.go_core(page)
        fw = js(page, "()=>coreFWarn(coreFNow())")
        dom = txt(page, "[data-c-ffwarn]") or ""
        check(f"{tag} 6 ไม่มี fundflow.json → '⚠ ยังไม่มีข้อมูล Fund-flow · ไม่ลดขนาดไม้ (100%)'", fw == "⚠ ยังไม่มีข้อมูล Fund-flow · ไม่ลดขนาดไม้ (100%)", fw)
        check(f"{tag} 6 ข้อความบนจอ (Core strip) ไม่มี '· f 100%' · มี 'ไม่ลดขนาดไม้ (100%)'", ("ไม่ลดขนาดไม้ (100%)" in dom or dom == "") and "· f 100%" not in dom, dom)
        # stale
        P37.fx_core(page)
        p24.set_ff(page, {"as_of": "2026-09-10", "ratios": {"ACWI_BIL": {"up": False}, "HYG_IEI": {"up": True}}})
        js(page, "()=>render()"); page.wait_for_timeout(300)
        fw2 = js(page, "()=>coreFWarn(coreFNow())")
        check(f"{tag} 6 stale → '⚠ Fund-flow เก่า n วันทำการ · ไม่ลดขนาดไม้ (100%)' (ไม่มี 'f ไม่ลด')", bool(re.match(r"^⚠ Regime data is \d+ business days old — size from last known state$", fw2 or "")) and "f ไม่ลด" not in (fw2 or ""), fw2)
        P37.go_core(page)
        dom2 = txt(page, "[data-c-ffwarn]") or ""
        check(f"{tag} 6 ข้อความ stale บนจอ: 'ไม่ลดขนาดไม้' · ไม่มี 'f ไม่ลด'", "size from last known state" in dom2 and "f ไม่ลด" not in dom2, dom2)
        check(f"{tag} 6 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()


# ───────────────────────── 7 · ตารางใน Thesis ─────────────────────────
def table_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, context, page, ce, pe, dialogs = P40.launch(pw, w, h, lambda pg: P40.seed_wl(pg, "AVGO", P41.v3()), iso=P41.CLK)
    try:
        P40.go_watch(page, "AVGO", "biz"); page.wait_for_timeout(400)
        info = js(page, """()=>{ const td=[...document.querySelectorAll('.ltTw td')].find(e=>e.innerText.includes('+127%'));
          if(!td) return null;
          const w = document.createTreeWalker(td, NodeFilter.SHOW_TEXT); let nd, rects = null;
          while((nd = w.nextNode())){ const i = nd.nodeValue.indexOf('+127%'); if(i>=0){ const r=document.createRange(); r.setStart(nd,i); r.setEnd(nd,i+5); rects = [...r.getClientRects()].map(x=>Math.round(x.top)); break; } }
          const cs = getComputedStyle(td), tw = td.closest('.ltTw');
          return {rects, tops:[...new Set(rects||[])].length, ow: cs.overflowWrap, wb: cs.wordBreak, wrapOx: getComputedStyle(tw).overflowX, tw:{sw:tw.scrollWidth, cw:tw.clientWidth}}; }""")
        check(f"{tag} 7 ช่อง '+127%' ไม่ถูกตัดกลางคำ (อยู่บรรทัดเดียว · rect 1 แถว)", info and info["tops"] == 1 and len(info["rects"]) == 1, json.dumps(info))
        check(f"{tag} 7 ช่องตาราง overflow-wrap:normal · word-break:keep-all · กล่องตาราง overflow-x:auto", info and info["ow"] == "normal" and info["wb"] == "keep-all" and info["wrapOx"] == "auto", json.dumps(info))
        ov = overflow(page)
        check(f"{tag} 7 หน้าเว็บไม่ล้นแนวนอน (scrollWidth − innerWidth = {ov})", ov <= 0, str(ov))
        tabs = js(page, """()=>[...document.querySelectorAll('.ltTw')].map(t=>({sw:t.scrollWidth, cw:t.clientWidth, cut:[...t.querySelectorAll('td,th')].filter(c=>c.scrollWidth>c.clientWidth+1).length}))""")
        if w > 900:
            check(f"{tag} 7 1440: ตารางไม่มี scrollbar แนวนอนในกล่อง (scrollWidth ≤ clientWidth ทุกตาราง)", tabs and all(t["sw"] <= t["cw"] + 1 for t in tabs), json.dumps(tabs))
        else:
            check(f"{tag} 7 390: ตารางกว้างเกินเลื่อนใน .ltTw ได้ (ไม่ตัดช่อง · ไม่ดันหน้า)", tabs and all(t["cut"] == 0 for t in tabs), json.dumps(tabs))
        shot(page, f"num1-thesis-table-{sfx}.png", ".ltTw")
        check(f"{tag} 7 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()


def static_tests():
    root = os.path.join(HERE, "..")
    check("[static] สำรอง index.backup-pre-NUM1.html + tests/_bk_num1/ อยู่", os.path.exists(os.path.join(root, "index.backup-pre-NUM1.html")) and os.path.isdir(os.path.join(HERE, "_bk_num1")))
    html = open(os.path.join(root, "index.html"), encoding="utf-8").read()
    check("[static] มี pnlOutcome ใช้ใน statsFor/ตัวกรอง/สถิติ setup · ไม่เหลือ realizedPnlOf(t)>0 ในที่นับ win", "function pnlOutcome(" in html and html.count("pnlOutcome(t)==='win'") == 4 and "list.filter(t=>realizedPnlOf(t)>0).length" not in html)


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            sat_plan_tests(pw, w, h, label)
            journal_tests(pw, w, h, label)
            wl_status_tests(pw, w, h, label)
            dd_weak_tests(pw, w, h, label)
            ff_word_tests(pw, w, h, label)
            table_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 42 / NUM1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
