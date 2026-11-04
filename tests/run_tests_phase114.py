#!/usr/bin/env python3
"""PL1 Step 2 — A4 (Base Risk ค่าเดียว · ถอด ★→risk/evalGate) + A3 (RS stars manual · rank-only) · เทส 114
Chromium · 390 / 1440 · ข้อมูล SAMPLE ล้วน · Core ฿4.2M fx 33 (≈ $127,272.73)
รัน: python3 run_tests_phase114.py"""
import json, os
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase108 as P108
import run_tests_phase111 as P111

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle = T.settle


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def calc_tests(pw):
    tag = f"[{ENGINE}/calc]"
    b, page, ce, pe = P111.core(pw)
    try:
        gone = js(page, "()=>['starBaseRisk','starBudget','starsFromEval','evalGate'].map(k=>typeof Calc[k])")
        check(f"{tag} A4: Calc.starBaseRisk / starBudget / starsFromEval / evalGate ถูกถอดแล้ว", gone == ["undefined"] * 4, gone)
        fns = js(page, "()=>['csGateOf','csStarsOf','csPendHtml','csMissTxt','csWlStars','csStarsWrite','td4ProStar'].map(k=>typeof window[k])")
        check(f"{tag} A4: csGateOf / csStarsOf / Pending Review / csStarsWrite / td4ProStar ถูกถอด (ไม่มีด่าน ★)", fns == ["undefined"] * 7, fns)
        s = js(page, "()=>[Calc.riskBudget({base:1, equity:1000000, f:0.75, dd:1, used:3000}), Calc.riskBudget({base:1, equity:1000000, f:1, dd:0.5, used:99999999}), Calc.riskBudget({base:0, equity:1000}), Calc.riskBudget({base:1, equity:0})]")
        check(f"{tag} riskBudget: 1% × 1,000,000 = 10,000 × FF 0.75 (ครั้งเดียว) = 7,500 − ใช้ 3,000 = เหลือ 4,500", abs(s[0]["full"] - 10000) < 1e-6 and abs(s[0]["adj"] - 7500) < 1e-6 and abs(s[0]["left"] - 4500) < 1e-6, s[0])
        check(f"{tag} riskBudget: DD ×0.5 · ใช้เกิน → เหลือ 0 · ไม่มี base / ไม่มี equity → ok:false", abs(s[1]["adj"] - 5000) < 1e-6 and s[1]["left"] == 0 and s[2]["ok"] is False and s[3]["ok"] is False, s)
        cfg = js(page, "()=>{ const c = coreRiskCfg('main'); return {base:c.baseRisk, riskA:c.riskA, riskFirst:c.riskFirst, riskAcc:c.riskAcc}; }")
        check(f"{tag} cfg.baseRisk ค่าเริ่ม = 1 · riskA/riskFirst/riskAcc เดิมยังอยู่ (ไม่ migrate ไม่ลบ)", cfg["base"] == 1 and cfg["riskA"] > 0 and cfg["riskFirst"] > 0 and cfg["riskAcc"] > 0, cfg)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def size_tests(pw, w=390, h=844):
    tag = f"[{ENGINE}/size/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        # ไม่มี ★/ไม่ประเมิน ก็ใช้ Base 1% ได้ · ไม้แรก 127 หุ้น (1% × $127,273 ÷ 10)
        P111.open_form(page, "FLAT1"); P111.setpx(page, 100, 90)
        bn, fm = P111.banner(page), P111.form(page)
        check(f"{tag} A4: หุ้นไม่มีการประเมิน/ไม่มี ★ → 'Base risk 1.00% of Momentum pool' · ไม้แรก 127 หุ้น · Risk 1% อ่านอย่างเดียว · บันทึกได้ (ไม่มีด่าน)",
              bn["l1"] == "Base risk 1.00% of Momentum pool" and fm["qty"].replace(",", "") == "127" and abs(float(fm["risk"]) - 1.0) < 1e-3 and fm["ro"] is True and fm["save"] is False, [bn, fm])
        txt0 = js(page, "()=>(document.querySelector('[data-cs-l2]')||{}).innerText||''")
        check(f"{tag} แบนเนอร์ไม่มีบรรทัด RS/Gate 5/Missing/Edit Stock Evaluation/Eval suggests", txt0 == "" and not bn["miss"] and not bn["edit"], bn)
        # เปลี่ยน RS stars ของหุ้นนี้ → ความเสี่ยง/ขนาดไม่เปลี่ยน
        js(page, "()=>wlCol().doc('FLAT1').set({ticker:'FLAT1', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'})"); settle(page, 400)
        base_q = P111.form(page)["qty"]
        for st in (0, 1, 2, 3, None):
            js(page, "(v)=>{ wlStarSet('FLAT1', v==null ? '' : String(v)); }", st); settle(page, 300); js(page, "()=>coreNewIn()"); settle(page, 150)
            fm2 = P111.form(page)
            check(f"{tag} A3: RS={'Unrated' if st is None else st} → ขนาดไม้/Risk ไม่เปลี่ยน ({base_q} หุ้น · 1%)", fm2["qty"] == base_q and abs(float(fm2["risk"]) - 1.0) < 1e-3, fm2)
        # ★ เก่าใน data (stars=3 ใน eval + wl) ถูกเพิกเฉย
        P111.ev(page, "FLAT1", stars=3, f="passed", p="passed")
        js(page, "()=>wlCol().doc('FLAT1').update({stars:3})"); settle(page, 300); js(page, "()=>coreNewIn()"); settle(page, 150)
        fm3 = P111.form(page)
        check(f"{tag} A3: ★ เก่า (eval.stars=3 / wl.stars=3) ถูกเพิกเฉย → ยัง 1% เท่าเดิม", fm3["qty"] == base_q and abs(float(fm3["risk"]) - 1.0) < 1e-3, fm3)
        # บันทึก → snapshot ไม่มี ★, Base 1
        js(page, "()=>coreNewSave()"); settle(page, 900)
        c = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='FLAT1'); return c ? JSON.parse(JSON.stringify(c)) : null; }")
        cs = (c or {}).get("cs") or {}
        check(f"{tag} บันทึกแผน → snapshot cs: baseRiskPct 1 · stars null · ไม่เขียน tier*", c and cs.get("baseRiskPct") == 1 and cs.get("stars") is None and "tier" not in c, cs)
        chip = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='FLAT1'); return csLbl(c); }")
        check(f"{tag} ป้ายการ์ดใหม่ = 'Base 1.00%' (ไม่มี ★)", chip == "Base 1.00%", chip)
        # ปรับ Base ใน Settings → แผนใหม่ใช้ค่าใหม่ · การ์ดที่บันทึกแล้วไม่ถูกคำนวณใหม่
        before = js(page, "()=>JSON.stringify(coreCardsList.find(x=>x.ticker==='FLAT1').cs)")
        js(page, "()=>{ const st = state; st.settings.coreRisk = Object.assign({}, st.settings.coreRisk || {}, {baseRisk:0.5}); }")
        P111.open_form(page, "FLAT2"); P111.setpx(page, 100, 90)
        fm4, bn4 = P111.form(page), P111.banner(page)
        after = js(page, "()=>JSON.stringify(coreCardsList.find(x=>x.ticker==='FLAT1').cs)")
        check(f"{tag} A4: Base Risk = 0.5% ใน Settings → แผนใหม่ 63 หุ้น · Risk 0.5% · snapshot ของแผนเก่าไม่เปลี่ยน", abs(float(fm4["risk"]) - 0.5) < 1e-3 and fm4["qty"].replace(",", "") == "63" and bn4["l1"].startswith("Base risk 0.50%") and before == after, [fm4, bn4["l1"], before == after])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def old_plan_tests(pw):
    tag = f"[{ENGINE}/oldplan]"
    tr = [T.P13.T("tB1", "core", "open", sym="AAPL", entry=100, sl=90, qty=60, cur="USD", date="2026-10-20")] if hasattr(T, "P13") else []
    b, page, ce, pe = P111.core(pw, 390, 844)
    try:
        card = {"acct": "main", "ticker": "OLD", "market": "US", "strategy": "W", "plan": {"entry": 100, "stop": 90, "risk": 0.75}, "stop": 90, "stopHistory": [], "px": 100, "pxDate": "2026-10-29", "emaW": 95,
                "lots": [], "trade_id": None, "acc_trade_id": None, "status": "plan", "created_at": "2026-10-20T00:00:00Z",
                "cs": {"eval": None, "date": "2026-10-20", "evalDate": "", "stars": 2, "stars_src": "manual", "baseRiskPct": 0.75, "riskAmt": 955, "equity": P111.TANK, "used": 0, "budget": P111.TANK * 0.0075, "adj": {"ff": 1, "dd": 1}, "capKey": "A"}}
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", ["ccOLD", card]); js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 800)
        r = js(page, "()=>{ const c = coreCardsList.find(x=>x.id==='ccOLD'); return {lbl:csLbl(c), base:c.cs.baseRiskPct, stars:c.cs.stars, add:csAddRisk(c, coreCtx('main'), 'A', coreCtx('main').tankTHB/33)}; }")
        check(f"{tag} แผนเก่า (★★ · Base 0.75%) ไม่ถูกคำนวณใหม่: ป้ายยังเป็น '★★ · Base 0.75%' · cs.baseRiskPct 0.75 · เติมไม้ใช้ 0.75%", r["lbl"] == "★★ · Base 0.75%" and r["base"] == 0.75 and r["stars"] == 2 and abs(r["add"] - 0.0075) < 1e-9, r)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def rs_tests(pw, w=390, h=844):
    tag = f"[{ENGINE}/rs/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        js(page, "()=>{ const col = wlCol(); col.doc('RSA').set({ticker:'RSA', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', stars:3}); col.doc('RSB').set({ticker:'RSB', market:'US', port:'core', note:'', added_at:'2026-10-02T00:00:00Z', rs_stars:0, rs_rated_at:'2026-10-20'}); }"); settle(page, 500)
        v = js(page, "()=>wlItems.filter(x=>/^RS[AB]$/.test(x.ticker)).map(x=>[x.ticker, x.stars, x.rs_stars, x.rs_rated_at]).sort()")
        check(f"{tag} A3: เอกสารเก่า stars=3 → rs_stars=null (Unrated · ไม่แปลง) · ค่า stars เดิมยังอยู่ใน data · rs_stars 0 ≠ Unrated", v == [["RSA", 3, None, None], ["RSB", 0, 0, "2026-10-20"]], v)
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); renderWatchlist(); }"); settle(page, 500)
        ui = js(page, "()=>({a:wlStarsOf({item:wlItems.find(x=>x.ticker==='RSA')}), b:wlStarsOf({item:wlItems.find(x=>x.ticker==='RSB')}), opts:[...new Set([...document.querySelectorAll('[data-wl-rs] option')].map(o=>o.textContent))]})")
        check(f"{tag} A3: wlStarsOf RSA = null (★ เก่าไม่แสดงเป็น RS) · RSB = 0 · ตัวเลือก Unrated · 0 · ★ · ★★ · ★★★", ui["a"] is None and ui["b"] == 0 and ui["opts"] == ["RS: Unrated", "RS: 0", "RS: ★", "RS: ★★", "RS: ★★★"], ui)
        js(page, "()=>wlStarSet('RSA', '2')"); settle(page, 400)
        w = js(page, "()=>{ const x = wlItems.find(x=>x.ticker==='RSA'); return [x.rs_stars, x.rs_rated_at, x.stars]; }")
        check(f"{tag} A3: ตั้ง RS ★★ → rs_stars=2 · rs_rated_at=วันนี้ · stars เดิม (3) ไม่ถูกแตะ", w[0] == 2 and bool(w[1]) and w[2] == 3, w)
        js(page, "()=>wlStarSet('RSA', '')"); settle(page, 400)
        w = js(page, "()=>{ const x = wlItems.find(x=>x.ticker==='RSA'); return [x.rs_stars, x.rs_rated_at]; }")
        check(f"{tag} A3: เลือก Unrated → rs_stars=null · rs_rated_at=null", w == [None, None], w)
        js(page, "()=>wlStarSet('RSA', '0')"); settle(page, 400)
        w = js(page, "()=>wlItems.find(x=>x.ticker==='RSA').rs_stars")
        check(f"{tag} A3: เลือก 0 → rs_stars=0 (ไม่ใช่ null)", w == 0, w)
        o = C.overflow(page)
        check(f"{tag} Watchlist ไม่ล้นแนวนอน", not o, o)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def promote_tests(pw, w=390, h=844):
    tag = f"[{ENGINE}/promote/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        P108.seed_cands(page); T.go_today(page)
        page.locator('[data-td3-cand="NEW1"] [data-td4-promote]').click(); settle(page, 300)
        page.fill("[data-td4-pro-note]", ""); settle(page, 200)
        f = js(page, "()=>({stars:document.querySelectorAll('[data-td4-star]').length, need:document.querySelector('[data-td4-need]').innerText, go:document.querySelector('[data-td4-pro-go]').disabled})")
        check(f"{tag} interim: ฟอร์ม Cand → WL ไม่มีปุ่ม ★ · Need: note อย่างเดียว · ปุ่มย้ายกดไม่ได้จนกว่าจะมี note", f["stars"] == 0 and f["need"] == "Need: note" and f["go"] is True, f)
        page.fill("[data-td4-pro-note]", "why watch"); settle(page, 200)
        f = js(page, "()=>({need:document.querySelector('[data-td4-need]').innerText, go:document.querySelector('[data-td4-pro-go]').disabled})")
        check(f"{tag} interim: กรอก note แล้ว → Ready · ปุ่มกดได้ (ไม่ต้องมี ★/RS/Gate 5)", f["need"] == "Ready" and f["go"] is False, f)
        page.locator("[data-td4-pro-go]").click(); settle(page, 700)
        wl = js(page, "()=>{ const x = wlItems.find(x=>x.ticker==='NEW1'); return x ? {stars:x.stars, rs:x.rs_stars} : null; }")
        check(f"{tag} ย้ายเข้า Watchlist สำเร็จ → stars=0 (ไม่เขียนดาว) · rs_stars=null (Unrated)", wl == {"stars": 0, "rs": None}, wl)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def settings_tests(pw, w=390, h=844):
    tag = f"[{ENGINE}/settings/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        lab = js(page, "()=>document.querySelector('#sCrRiskA').closest('.f').querySelector('label').innerText.replace(/\\s+/g,' ').trim()")
        check(f"{tag} Settings: ป้ายช่อง = 'Base Risk per trade (% of pool)'", lab == "Base Risk per trade (% of pool)", lab)
        note = js(page, "()=>document.querySelector('[data-cs-setnote]').innerText")
        check(f"{tag} Settings: คำอธิบายไม่พูดถึง ★★★ 1.00% · ★★ 0.75% แล้ว", "★" not in note.replace("RS stars", "") and "Base Risk" in note, note)
        js(page, "()=>{ settingsOpen && 0; }") if False else None
        val = js(page, "()=>{ settingsFill && 0; return document.getElementById('sCrRiskA').value; }") if False else None
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        calc_tests(pw); size_tests(pw, 390); size_tests(pw, 1440, 900); old_plan_tests(pw)
        rs_tests(pw, 390); rs_tests(pw, 1440, 900); promote_tests(pw, 390); settings_tests(pw, 390)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
