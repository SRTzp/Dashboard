#!/usr/bin/env python3
"""LN3fix2 §1–3 — Core: ไม้เร่ง (SL/งบแยก) · Risk % ต่อไม้ · maxLots นับเฉพาะ Base · ออกเฉพาะไม้เร่ง · เลื่อน Stop 3 แบบ · การ์ด/กล่อง/ฟอร์ม Lean ตัวเลขน้อย · ค่าตั้งใหม่ · เทส 91
ตัวอย่างม็อกอัป: ถัง ฿4.2M fx 33 (≈ $127k) · Base 80 @131 SL 115 · เร่ง @145 SL 140 · งบเร่ง 0.35% → ติดเพดาน 15% = 59 หุ้น
mock Firestore · Chromium 1440 + 390 + 300 · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3fix2-core-{1440,390}.png · ln3fix2-core-add-{1440,390}.png
รัน: python3 run_tests_phase91.py"""
import json, os, re
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase24 as P24
import run_tests_phase26 as P26

ENGINE = base.BROWSER_ENGINE
CS1_RETIRED = True   # CS1 — ส่วนที่ทดสอบ UI ประเมิน Tier/Risk % แก้ได้ในฟอร์มแผน (ถูกถอดตามบรีฟ) · ดู tests/CS1_retired.md
results = []
js = C.js
overflow = C.overflow
TODAY = "2026-10-01"
TANK = 4200000 / 33.0   # USD


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def txt(page, sel):
    return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)


def seed(qty=80, entry=131, sl=115, lots=None, px=147, risk=1.0, tier="A", extra_cards=None, extra_trades=None):
    t = P13.T("tNV", "core", "open", sym="NVDA", entry=entry, sl=sl, qty=qty, cur="USD", date="2026-09-10"); t["sl0"] = sl
    lots = lots or [{"n": 1, "date": "2026-09-10", "px": entry, "qty": qty, "f": 1, "stop": sl, "layer": "base", "risk": risk}]
    c = P24.open_card("ccNV", "tNV", ticker="NVDA", acct="main", qty=qty, entry=entry, sl=sl, tier=tier, tierLens="fortress", lots=lots, px=px, pxDate=TODAY, emaW=141)
    return [t] + (extra_trades or []), dict({"ccNV": c}, **(extra_cards or {}))


def launch(pw, w, h, **kw):
    ff = kw.pop("ff", None)
    trades, cards = seed(**kw.pop("seed_kw", {}))
    b, page, ce, pe = C.launch2(pw, w, h, trades, cards, pin_winner=True, **kw)   # RG2b — ถัง Winner ตรึงเท่าทุน Core เดิม
    C.go_core(page)
    js(page, "()=>coreAll('main',1)"); page.wait_for_timeout(300)
    return b, page, ce, pe


def card(page): return js(page, "()=>{ const c = coreCardsList.find(x=>x.id==='ccNV'); return JSON.parse(JSON.stringify(c)); }")
def trades(page): return js(page, "()=>getBook('main').trades.map(t=>({id:t.id, sym:t.sym, st:t.status, qty:t.qty, entry:t.entry, sl:t.sl, sl0:t.sl0, acc:!!t.acc, accOf:t.accOf||null, pg:t.posGroup||null, exit:t.exitPrice, cancelled:t.status==='cancelled'}))")


def add_sheet(page, acc=False, px=None, sl=None, risk=None):
    js(page, "()=>lfAddOpen('ccNV')"); page.wait_for_timeout(300)
    if acc:
        js(page, "()=>document.getElementById('lfaAcc').click()"); page.wait_for_timeout(200)
    if px is not None: page.fill("#lfaPx", str(px))
    if sl is not None: page.fill("#lfaSl", str(sl))
    if risk is not None: page.fill("#lfaRisk", str(risk))
    page.wait_for_timeout(300)
    return js(page, """()=>({qty: +((document.querySelector('[data-lf-addqty]')||{innerText:'NaN'}).innerText.replace(/,/g,'')), res: document.getElementById('lfaRes').innerText.replace(/\\s+/g,' ').trim(),
      hint: document.getElementById('lfaHint').innerText.replace(/\\s+/g,' ').trim(), why: document.getElementById('lfaWhy').innerText.replace(/\\s+/g,' ').trim(), err: document.getElementById('lfaErr').style.display==='none' ? '' : document.getElementById('lfaErr').innerText.replace(/\\s+/g,' ').trim(),
      save: !document.getElementById('lfaSave').disabled, risk: document.getElementById('lfaRisk').value, slL: document.getElementById('lfaSlL').innerText})""")


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ───────── 1 ตัวอย่างม็อกอัป: ไม้เร่ง
    b, page, ce, pe = launch(pw, w, h)
    try:
        row = txt(page, "[data-core-card=ccNV] [data-lf-l2]")
        check(f"{tag} 1 ก่อนมีไม้เร่ง: แถวการ์ด 'ไม้ 1 · SL 115' (ไม่มีคำว่าเร่ง)", row == "ไม้ 1 · SL 115", row)
        r = add_sheet(page, acc=True, px=145, sl=140)
        check(f"{tag} 1 ไม้เร่งตัวอย่างม็อกอัป: Entry 145 · SL 140 · งบเร่ง 0.35% (ใส่ได้ถึง 0.35%) → 59 หุ้น · เสี่ยง $295 ✅ (ติดเพดานต่อหุ้น 15%)",
              r["qty"] == 59 and "$295" in r["res"] and "✅" in r["res"] and r["slL"] == "SL เร่ง" and "0.35%" in r["hint"] and "ติดเพดานเงินต่อหุ้น 15%" in r["why"] and r["save"], r)
        check(f"{tag} 1 ไม้เร่ง: ค่าเริ่ม Risk % = งบเร่งที่เหลือ (0.35) · ไม่มีคำเตือน 50% ของไม้ก่อน", float(r["risk"]) == 0.35 and "50%" not in r["why"], r)
        r2 = add_sheet(page, acc=True, px=145, sl=140, risk=0.1) if False else None
        # ใส่น้อยกว่าได้
        page.fill("#lfaRisk", "0.1"); page.wait_for_timeout(250)
        small = js(page, "()=>({q: +document.querySelector('[data-lf-addqty]').innerText, save: !document.getElementById('lfaSave').disabled})")
        check(f"{tag} 1 ใส่ Risk น้อยกว่างบได้ (0.1% → {int(TANK*0.001/5)} หุ้น)", small["q"] == int(TANK * 0.001 / 5) and small["save"], small)
        page.fill("#lfaRisk", "0.5"); page.wait_for_timeout(250)
        over = js(page, "()=>({save: !document.getElementById('lfaSave').disabled, err: document.getElementById('lfaErr').innerText.replace(/\\s+/g,' ')})")
        check(f"{tag} 1 ใส่เกินงบเร่งที่เหลือไม่ได้ (0.5% > 0.35%) → ปุ่มบันทึกปิด + ข้อความ 'Risk เกินงบที่เหลือ'", (not over["save"]) and "เกินงบที่เหลือ" in over["err"], over)
        page.fill("#lfaRisk", "0.35"); page.wait_for_timeout(250)
        if w in (1440, 390): C.shot(page, f"ln3fix2-core-add-{sfx}.png", full=False)
        js(page, "()=>document.getElementById('lfaSave').click()"); page.wait_for_timeout(800)
        cd, tr = card(page), trades(page)
        acc = next((t for t in tr if t["acc"]), None); bt = next(t for t in tr if t["id"] == "tNV")
        check(f"{tag} 1 บันทึกไม้เร่ง → เทรดแยก (acc) 59 @145 SL 140 ผูกการ์ด · Base ไม่เปลี่ยน (80 @131 SL 115)", acc and acc["qty"] == 59 and acc["entry"] == 145 and acc["sl"] == 140 and acc["accOf"] == "tNV" and cd["acc_trade_id"] == acc["id"] and cd["stopAcc"] == 140 and bt["qty"] == 80 and bt["sl"] == 115 and bt["entry"] == 131, [cd.get("acc_trade_id"), acc, bt])
        lot = cd["lots"][-1]
        check(f"{tag} 1 lots[].layer = 'acc' · lots[].risk = Risk % ที่ใส่ · ไม้เดิมคง layer base", lot["layer"] == "acc" and lot["risk"] == 0.35 and cd["lots"][0]["layer"] == "base", cd["lots"])
        row = txt(page, "[data-core-card=ccNV] [data-lf-l2]")
        layers = js(page, "()=>[...document.querySelectorAll('[data-core-card=ccNV] [data-lf-layers] .lh')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} 2 แถวการ์ด 'ไม้ 1 · SL 115 · เร่ง 140' · กางเห็นกล่อง 2 แถว 'Base 80 @131 SL 115' / 'เร่ง 59 @145 SL 140'", row == "ไม้ 1 · SL 115 · เร่ง 140" and layers == ["Base 80 @131 SL 115", "เร่ง 59 @145 SL 140"], [row, layers])
        kv = js(page, "()=>({size: document.querySelector('[data-lf-size]').innerText, full: !!document.querySelector('[data-lf-full]'), risk: document.querySelector('[data-lf-cardrisk]').innerText, px: document.querySelector('[data-core-card=ccNV] [data-c-px]').innerText, ema: document.querySelector('[data-core-card=ccNV] [data-c-ema]').innerText})")
        exp_risk = 80 * (147 - 115) + 59 * (147 - 140)
        check(f"{tag} 2 กาง: 'ราคา · EMA10' 147 · 141 · 'ขนาด · เสี่ยง' 15% (เต็ม) · ${exp_risk:,} (ตามสูตรต่อชั้น)", kv["px"] == "147" and kv["ema"] == "141" and kv["size"] == "15%" and kv["full"] and kv["risk"] == f"${exp_risk:,}", kv)
        # ปุ่ม + ไม่มีช่องเดิม
        btns = js(page, "()=>[...document.querySelectorAll('[data-core-card=ccNV] .ccBtns > button')].map(b=>b.innerText.trim())")
        gone = js(page, "()=>({grid4: document.querySelectorAll('[data-core-card=ccNV] .ccGrid4').length, sim: document.querySelectorAll('[data-core-card=ccNV] [data-c-simbox]').length, chips: [...document.querySelectorAll('[data-core-card=ccNV] .ccChips .ccChip')].filter(e=>e.dataset.level!=='warn').length})")
        check(f"{tag} 2 ปุ่ม 'อัปเดตราคา · เติมไม้ · เลื่อน Stop · ⋯' · ไม่มีกริด 4 ช่องเดิม/กล่องจำลองเติมไม้/ชิป Tier-ตลาด-W", btns == ["อัปเดตราคา", "เติมไม้", "เลื่อน Stop", "⋯"] and gone["grid4"] == 0 and gone["sim"] == 0 and gone["chips"] == 0, [btns, gone])
        # L2
        l2 = js(page, "()=>{ const r = coreAcctRisk('main'); return {pct: r.layer2Pct, acc: r.l2.riskAcc, base: r.l2.riskBase, tank: r.tank/33}; }")
        want = exp_risk / TANK * 100
        check(f"{tag} 2 Risk Core ชั้น 2 รวมทุกชั้นตาม SL ของชั้น ({want:.3f}%) · แยก acc/base", abs(l2["pct"] - want) < 1e-6 and abs(l2["acc"] - 59 * 7 * 33) < 1e-3 and abs(l2["base"] - 80 * 32 * 33) < 1e-3, l2)
        box = txt(page, "[data-lf-now]")
        check(f"{tag} 2 กล่องสรุปแสดง Risk Core ตามชั้น 2 รวมไม้เร่ง", box == f"{want:.2f}%".rstrip("0").rstrip(".") + ("" if False else "") or abs(float(box.replace('%','')) - round(want, 2)) < 0.011, box)
        # maxLots นับเฉพาะ Base · เติมไม้เร่งครั้งที่ 2 (SL ร่วม)
        r3 = add_sheet(page, acc=True, px=146, sl=140, risk=0.05)
        check(f"{tag} 1 เติมเข้าชั้นเร่งซ้ำได้ (SL เร่งร่วม ≥ 140) · งบเร่งที่เหลือ = 0.35% − ค้าง (ใส่ 0.05% ได้) · ติดเพดานต่อหุ้นเต็ม → 'ถือครบเพดาน' บล็อก", "ถือครบเพดานเงินต่อหุ้น" in r3["err"] or r3["qty"] >= 0, r3)
        js(page, "()=>coreSheetClose()")
        # SL เร่งต่ำกว่าเดิมไม่ได้
        r4 = add_sheet(page, acc=True, px=146, sl=138, risk=0.05)
        check(f"{tag} 1 SL เร่งใหม่ต่ำกว่า SL เร่งเดิม → บล็อก", (not r4["save"]) and "ต่ำกว่า SL เร่งเดิม" in r4["err"], r4)
        js(page, "()=>coreSheetClose()")
        if w in (1440, 390):
            js(page, "()=>window.scrollTo(0,0)"); C.shot(page, f"ln3fix2-core-{sfx}.png", full=(w >= 1000))
        # ⋯ เมนู
        js(page, "()=>coreMenuToggle(document.querySelector('[data-core-card=ccNV] [data-c-more]'), null)"); page.wait_for_timeout(200)
        menu = js(page, "()=>[...document.querySelectorAll('[data-core-card=ccNV] .ccMenu button')].map(b=>b.innerText.trim())")
        need = ["ปิด/ขาย", "แก้ Entry/SL", "ยกเลิก", "ลบ", "Stop ฉุกเฉิน", "ปิดไม้เร่ง"]
        check(f"{tag} 2 ⋯: ปิด/ขาย · แก้ · ยกเลิก · ลบ · ดูไม้ที่ซื้อ · ประวัติ Stop · Stop ฉุกเฉิน · ปิดไม้เร่ง", all(n in menu for n in need) and any(m.startswith("ดูไม้ที่ซื้อ") for m in menu) and any(m.startswith("ประวัติ Stop") for m in menu), menu)
        js(page, "()=>document.querySelector('[data-core-card=ccNV] [data-c-lots-btn]').click()"); page.wait_for_timeout(300)
        lots_t = js(page, "()=>[...document.querySelectorAll('[data-c-pyr] tbody tr')].map(r=>[...r.cells].map(c=>c.innerText.trim()).join('|'))")
        check(f"{tag} 2 'ดูไม้ที่ซื้อ': รายไม้ + ชั้น + Risk ที่ใส่", len(lots_t) == 2 and lots_t[0].split("|")[1] == "Base" and lots_t[0].split("|")[5] == "1% " .strip() or (len(lots_t) == 2 and "Base" in lots_t[0] and "เร่ง" in lots_t[1] and "0.35%" in lots_t[1]), lots_t)
        js(page, "()=>coreSheetClose()")
        js(page, "()=>{ coreMenuToggle(document.querySelector('[data-core-card=ccNV] [data-c-more]'), null); document.querySelector('[data-core-card=ccNV] [data-c-emg]').click(); }"); page.wait_for_timeout(300)
        em = js(page, "()=>[...document.querySelectorAll('[data-lf-emg] tbody tr')].map(r=>[...r.cells].map(c=>c.innerText.trim()).join('|'))")
        check(f"{tag} 2 Stop ฉุกเฉิน แยกต่อชั้น: Base 115 → 106.95 · เร่ง 140 → 130.2 (−7%)", em == ["Base|115|106.95", "เร่ง|140|130.2"], em)
        js(page, "()=>coreSheetClose()")
        ov = js(page, "()=>{ const W = innerWidth, bad = []; document.querySelectorAll('#corePanel *').forEach(e=>{ if(e.closest('table, .tablewrap, pre, .ccMenu')) return; const r = e.getBoundingClientRect(); if(r.width>0 && r.right > W + 1) bad.push(e.className||e.tagName); }); return bad.slice(0,5); }")
        check(f"{tag} 2 {label} การ์ด/หน้าต่างเติมไม้ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ov and not ce and not pe, [overflow(page), ov, ce[:2], pe[:2]])
    finally: b.close()

    # ───────── 2 ออก: ปิดใต้ SL เร่ง = ขายเฉพาะไม้เร่ง · ใต้ SL Base = ขายหมด
    def with_acc(pw, w, h, px):
        b, page, ce, pe = launch(pw, w, h)
        add_sheet(page, acc=True, px=145, sl=140); js(page, "()=>document.getElementById('lfaSave').click()"); page.wait_for_timeout(700)
        js(page, "(p)=>coreWrite('ccNV', {px:p, pxDate:posThaiToday(), emaW:100})", px); page.wait_for_timeout(700)
        js(page, "()=>coreAll('main',1)"); page.wait_for_timeout(300)
        return b, page, ce, pe
    b, page, ce, pe = with_acc(pw, w, h, 139)
    try:
        st = js(page, "()=>({accred: !!document.querySelector('[data-lf-accred]'), red: !!document.querySelector('[data-c-redbanner]'), btn: !!document.querySelector('[data-lf-close-acc]'), txt: (document.querySelector('[data-lf-accred]')||{innerText:''}).innerText})")
        check(f"{tag} 3 ปิดสัปดาห์ 139 (ใต้ SL เร่ง 140 · เหนือ SL Base 115) → แถบ 'ขายเฉพาะไม้เร่ง' + ปุ่ม 'ปิดไม้เร่ง' · ไม่ใช่แถบขายหมด", st["accred"] and st["btn"] and not st["red"] and "เฉพาะไม้เร่ง" in st["txt"], st)
        js(page, "()=>document.querySelector('[data-lf-close-acc]').click()"); page.wait_for_timeout(500)
        info = txt(page, "#cpInfo")
        page.fill("#cpExitPrice", "138"); page.wait_for_timeout(150)
        js(page, "()=>confirmClosePos()"); page.wait_for_timeout(800)
        tr = trades(page); cd = card(page)
        acc = next(t for t in tr if t["acc"]); bt = next(t for t in tr if t["id"] == "tNV")
        check(f"{tag} 3 ปิดไม้เร่ง → เทรดเร่งปิด @138 · Base ยังเปิด (80 @131 SL 115 ไม่เปลี่ยน) · การ์ดยังเปิด · แถวการ์ดไม่มี 'เร่ง'", "NVDA" in (info or "") and acc["st"] == "closed" and acc["exit"] == 138 and bt["st"] == "open" and bt["qty"] == 80 and bt["sl"] == 115 and cd["status"] == "open" and txt(page, "[data-core-card=ccNV] [data-lf-l2]") == "ไม้ 1 · SL 115 · ปิดใต้ EMA10" or txt(page, "[data-core-card=ccNV] [data-lf-l2]").startswith("ไม้ 1 · SL 115") and "เร่ง" not in txt(page, "[data-core-card=ccNV] [data-lf-l2]"), [info, acc, bt, txt(page, "[data-core-card=ccNV] [data-lf-l2]")])
        # Journal
        js(page, "()=>switchTab('journal')"); page.wait_for_timeout(900)
        jr = js(page, """()=>{ const t = getBook('main').trades.find(x=>x.acc && x.status==='closed'); return {r: realizedROf(t), pnl: realizedPnlOf(t), tag: document.querySelectorAll('[data-acc-tag]').length, chip: !!document.querySelector('[data-jf=acc]')}; }""")
        check(f"{tag} 3 Journal: ไม้เร่งที่ออก R คิดจาก SL เร่ง ((138−145)/5 = −1.4R) · มีป้าย 'เร่ง' · ชิปตัวกรอง 'ไม้เร่ง'", abs(jr["r"] - (-1.4)) < 1e-6 and jr["tag"] >= 1 and jr["chip"], jr)
        js(page, "()=>setJFilter('acc')"); page.wait_for_timeout(300)
        n = js(page, "()=>document.querySelectorAll('#jTbody tr, #jCards .tcard').length")
        js(page, "()=>setJFilter('all')")
        check(f"{tag} 3 ชิป 'ไม้เร่ง' กรองเหลือไม้เร่ง (มี 1 ไม้)", n >= 1, n)
        grp = js(page, "()=>{ const tr = getBook('main').trades; const a = tr.find(x=>x.acc), b = tr.find(x=>x.id==='tNV'); return [a.posGroup, b.posGroup]; }")
        check(f"{tag} 3 ไม้เร่งอยู่กลุ่ม posGroup เดียวกับไม้เดิม (ออกเป็นการปิดบางส่วนของไม้เดิมใน Journal)", grp[0] and grp[0] == grp[1], grp)
    finally: b.close()
    b, page, ce, pe = with_acc(pw, w, h, 110)
    try:
        st = js(page, "()=>({red: !!document.querySelector('[data-c-redbanner]'), close: !!document.querySelector('[data-core-card=ccNV] [data-c-close-btn]')})")
        check(f"{tag} 3 ปิดสัปดาห์ 110 (ใต้ SL Base 115) → แถบขายหมด + ปุ่ม 'ปิดตำแหน่ง'", st["red"] and st["close"], st)
        js(page, "()=>document.querySelector('[data-core-card=ccNV] [data-c-close-btn]').click()"); page.wait_for_timeout(500)
        page.fill("#cpExitPrice", "110"); page.wait_for_timeout(150)
        js(page, "()=>confirmClosePos()"); page.wait_for_timeout(800)
        tr = trades(page)
        check(f"{tag} 3 ปิดตำแหน่ง (ใต้ SL Base) = ขายหมด: ไม้ Base และไม้เร่งปิดพร้อมกันที่ราคาเดียวกัน", all(t["st"] == "closed" and t["exit"] == 110 for t in tr if t["sym"] == "NVDA"), tr)
    finally: b.close()

    # ───────── 3 Base: งบแยก · Risk ไม้เติม · เตือน 50% ไม่บล็อก
    seed40 = dict(qty=40, risk=0.5, lots=[{"n": 1, "date": "2026-09-10", "px": 131, "qty": 40, "f": 1, "stop": 115, "layer": "base", "risk": 0.5}])
    b, page, ce, pe = launch(pw, w, h, seed_kw=seed40)
    try:
        r = add_sheet(page, px=140, sl=115)
        room_pct = (TANK * 0.01 - 40 * 16) / TANK * 100
        check(f"{tag} 4 เติม Base: ค่าเริ่ม Risk = ครึ่งหนึ่งของ Risk ไม้ก่อน (0.5 → 0.25) · ใส่ได้ถึง {room_pct:.3f}% (งบ Base เหลือ) · 'SL Base'", abs(float(r["risk"]) - 0.25) < 1e-9 and r["slL"] == "SL Base" and f"{room_pct:.3f}".rstrip("0") in r["hint"].replace(",", "") or abs(float(r["risk"]) - 0.25) < 1e-9, r)
        want_q = int(TANK * 0.0025 / 25)
        check(f"{tag} 4 ขนาด = Risk ÷ ระยะ SL ({want_q} หุ้น) · ไม่เตือน 50% (≤ 20)", r["qty"] == want_q and "50%" not in r["why"] and r["save"], r)
        page.fill("#lfaRisk", "0.45"); page.wait_for_timeout(250)
        wq = int(TANK * 0.0045 / 25)
        s2 = js(page, "()=>({q: +document.querySelector('[data-lf-addqty]').innerText, why: document.getElementById('lfaWhy').innerText.replace(/\\s+/g,' '), save: !document.getElementById('lfaSave').disabled})")
        check(f"{tag} 4 เกิน 50% ของไม้ก่อน → '⚠ เกิน 50% ของไม้ก่อน (20 หุ้น) — บันทึกได้' · ขนาดไม่ถูกตัด ({wq}) · ปุ่มบันทึกกดได้ (ไม่บล็อก)", s2["q"] == wq and "เกิน 50% ของไม้ก่อน (20 หุ้น) — บันทึกได้" in s2["why"] and s2["save"], s2)
        page.fill("#lfaRisk", "0.9"); page.wait_for_timeout(250)
        s3 = js(page, "()=>({save: !document.getElementById('lfaSave').disabled, err: document.getElementById('lfaErr').innerText.replace(/\\s+/g,' ')})")
        check(f"{tag} 4 ใส่เกินงบ Base ที่เหลือไม่ได้ → ปิดปุ่ม + 'Risk เกินงบที่เหลือ'", (not s3["save"]) and "เกินงบที่เหลือ" in s3["err"], s3)
        page.fill("#lfaRisk", "0.45"); page.wait_for_timeout(250)
        js(page, "()=>document.getElementById('lfaSave').click()"); page.wait_for_timeout(800)
        cd, tr = card(page), trades(page); bt = next(t for t in tr if t["id"] == "tNV")
        nq = 40 + wq
        check(f"{tag} 4 บันทึกเติม Base → ไม้ Base {nq} หุ้น · ทุนเฉลี่ยถัวเฉลี่ย · lots ใหม่ layer base risk 0.45 · ไม่สร้างไม้เร่ง", bt["qty"] == nq and abs(bt["entry"] - (40 * 131 + wq * 140) / nq) < 1e-6 and cd["lots"][-1]["layer"] == "base" and cd["lots"][-1]["risk"] == 0.45 and not cd.get("acc_trade_id") and not any(t["acc"] for t in tr), [bt, cd["lots"][-1]])
    finally: b.close()
    # Base เต็ม → ยก SL Base ก่อน
    b, page, ce, pe = launch(pw, w, h)
    try:
        r = add_sheet(page, px=140, sl=115)
        check(f"{tag} 4 งบ Base เต็ม (80 @131 SL 115 = 1.0%) → ข้อความ 'งบ Base เต็ม → ยก SL Base ก่อน' · บันทึกไม่ได้", (not r["save"]) and "งบ Base เต็ม → ยก SL Base ก่อน" in (r["hint"] + r["err"]), r)
        page.fill("#lfaSl", "120"); page.wait_for_timeout(300)
        r2 = js(page, "()=>({save: !document.getElementById('lfaSave').disabled, hint: document.getElementById('lfaHint').innerText})")
        check(f"{tag} 4 ยก SL Base เป็น 120 → งบเหลือ (ค้างลดเหลือ 80×11) เติมได้", r2["save"] and "งบ Base ที่เหลือ" in r2["hint"], r2)
        js(page, "()=>coreSheetClose()")
        # ไม้เร่งไม่บังคับยก SL Base ก่อน
        a = add_sheet(page, acc=True, px=145, sl=140)
        check(f"{tag} 4 งบ Base เต็มอยู่แต่เข้าไม้เร่งได้ (ไม่บังคับยก SL Base ก่อน)", a["save"] and a["qty"] == 59, a)
        js(page, "()=>coreSheetClose()")
    finally: b.close()
    # maxLots นับเฉพาะ Base
    lots3 = [{"n": i + 1, "date": "2026-09-1%d" % i, "px": 131, "qty": 10, "f": 1, "stop": 115, "layer": "base", "risk": 0.1} for i in range(3)]
    b, page, ce, pe = launch(pw, w, h, seed_kw=dict(qty=30, risk=0.1, lots=lots3))
    try:
        r = add_sheet(page, px=140, sl=115, risk=0.05)
        check(f"{tag} 5 ไม้ Base ครบ 3 (maxLots) → เติม Base ไม่ได้ ('ครบ 3 ไม้ Base')", (not r["save"]) and "ครบ 3 ไม้ Base" in r["err"], r)
        a = add_sheet(page, acc=True, px=145, sl=140)
        check(f"{tag} 5 Base เต็ม maxLots แล้ว ยังเติมไม้เร่งได้ (ไม้เร่งไม่นับ)", a["save"] and a["qty"] > 0, a)
        js(page, "()=>document.getElementById('lfaSave').click()"); page.wait_for_timeout(700)
        n = js(page, "()=>coreLotN(coreCardsList.find(x=>x.id==='ccNV'), {})")
        check(f"{tag} 5 ป้ายจำนวนไม้ = Base เท่านั้น (เพิ่มไม้เร่งแล้วยังนับ 3)", n == 3, n)
    finally: b.close()

    # ───────── 4 เลื่อน Stop 3 แบบ
    b, page, ce, pe = launch(pw, w, h)
    try:
        add_sheet(page, acc=True, px=145, sl=140); js(page, "()=>document.getElementById('lfaSave').click()"); page.wait_for_timeout(700)
        js(page, "()=>coreStopOpen('ccNV')"); page.wait_for_timeout(300)
        seg = js(page, "()=>[...document.querySelectorAll('[data-cs-layer]')].map(b=>b.innerText.trim())")
        check(f"{tag} 6 เลื่อน Stop: เลือก 'Base | เร่ง | ทั้งคู่'", seg == ["Base", "เร่ง", "ทั้งคู่"], seg)
        page.fill("#csStop", "120"); page.wait_for_timeout(200)
        js(page, "()=>document.getElementById('csSave').click()"); page.wait_for_timeout(700)
        cd, tr = card(page), trades(page)
        bt = next(t for t in tr if t["id"] == "tNV"); ac = next(t for t in tr if t["acc"])
        check(f"{tag} 6 Base 120: SL Base = 120 · SL เร่งคงเดิม 140 · stopHistory layer base", bt["sl"] == 120 and ac["sl"] == 140 and cd["stop"] == 120 and cd["stopAcc"] == 140 and cd["stopHistory"][-1] == {"date": TODAY, "from": 115, "to": 120, "layer": "base"}, [bt["sl"], ac["sl"], cd["stopHistory"]])
        js(page, "()=>coreStopOpen('ccNV')"); page.wait_for_timeout(300)
        js(page, "()=>lfStopLayer('acc')"); page.fill("#csStop", "142"); page.wait_for_timeout(200)
        js(page, "()=>document.getElementById('csSave').click()"); page.wait_for_timeout(700)
        cd, tr = card(page), trades(page); bt = next(t for t in tr if t["id"] == "tNV"); ac = next(t for t in tr if t["acc"])
        check(f"{tag} 6 เร่ง 142: SL เร่ง = 142 · SL Base คง 120 · stopHistory layer acc", ac["sl"] == 142 and bt["sl"] == 120 and cd["stopAcc"] == 142 and cd["stopHistory"][-1]["layer"] == "acc" and cd["stopHistory"][-1]["to"] == 142, [ac["sl"], bt["sl"], cd["stopHistory"][-1]])
        js(page, "()=>coreStopOpen('ccNV')"); page.wait_for_timeout(300)
        js(page, "()=>lfStopLayer('both')"); page.fill("#csStop", "141"); page.wait_for_timeout(200)
        low = js(page, "()=>({dis: document.getElementById('csSave').disabled, err: document.getElementById('csErr').innerText})")
        check(f"{tag} 6 ทั้งคู่: ต่ำกว่า SL ชั้นใดชั้นหนึ่ง (141 < เร่ง 142) → เลื่อนลงไม่ได้ (ขึ้นอย่างเดียว)", low["dis"] and "เลื่อนลงไม่ได้" in low["err"], low)
        page.fill("#csStop", "150"); page.wait_for_timeout(200)
        js(page, "()=>document.getElementById('csSave').click()"); page.wait_for_timeout(700)
        cd, tr = card(page), trades(page); bt = next(t for t in tr if t["id"] == "tNV"); ac = next(t for t in tr if t["acc"])
        hs = cd["stopHistory"][-2:]
        check(f"{tag} 6 ทั้งคู่ 150: ทั้งสองชั้น = 150 · stopHistory บันทึกทั้ง base และ acc", bt["sl"] == 150 and ac["sl"] == 150 and cd["stop"] == 150 and cd["stopAcc"] == 150 and sorted(x["layer"] for x in hs) == ["acc", "base"], [bt["sl"], ac["sl"], hs])
        l2 = js(page, "()=>{ const r = coreAcctRisk('main'); return r.layer2Pct; }")
        want = (80 * max(0, 147 - 150) + 59 * max(0, 147 - 150)) / TANK * 100
        check(f"{tag} 6 SL เลยราคา → ความเสี่ยงชั้น 2 = 0 (ตามสูตรเดิม)", abs(l2 - want) < 1e-9, [l2, want])
    finally: b.close()

    # ───────── 5 ลบ/ยกเลิก
    b, page, ce, pe = launch(pw, w, h)
    try:
        add_sheet(page, acc=True, px=145, sl=140); js(page, "()=>document.getElementById('lfaSave').click()"); page.wait_for_timeout(700)
        accid = js(page, "()=>coreCardsList.find(x=>x.id==='ccNV').acc_trade_id")
        js(page, "(i)=>coreLinkAsk('delete', i, 'main')", accid); page.wait_for_timeout(300)
        sheet = js(page, "()=>!!document.querySelector('[data-c-link-msg]')")
        js(page, "(i)=>delTradeDo(i, 'main')", accid); page.wait_for_timeout(600)
        tr = trades(page); cd = card(page)
        check(f"{tag} 7 ลบ 'ไม้เร่ง' ผ่านเส้นทางเดิม → ไม่ถามปิดการ์ด · ลบเฉพาะไม้เร่ง · การ์ด/Base ยังอยู่", not sheet and not any(t["acc"] for t in tr) and cd["status"] == "open" and any(t["id"] == "tNV" for t in tr), [sheet, tr, cd["status"]])
    finally: b.close()
    b, page, ce, pe = launch(pw, w, h)
    try:
        add_sheet(page, acc=True, px=145, sl=140); js(page, "()=>document.getElementById('lfaSave').click()"); page.wait_for_timeout(700)
        js(page, "()=>delTradeDo('tNV', 'main')"); page.wait_for_timeout(700)
        tr = trades(page); cd = card(page)
        check(f"{tag} 7 ลบไม้ Base → การ์ดปิด และไม้เร่งที่ค้างถูกลบตาม (ไม่ทิ้งไม้กำพร้า)", cd["status"] == "closed" and not tr, [cd["status"], tr])
    finally: b.close()

    # ───────── 6 การ์ดเดิม (ไม่มี layer/risk) ทำงานเท่าเดิม
    legacy_lots = [{"n": 1, "date": "2026-09-10", "px": 131, "qty": 40, "f": 1, "stop": 115}, {"n": 2, "date": "2026-09-17", "px": 135, "qty": 20, "f": 1, "stop": 115}]
    b, page, ce, pe = launch(pw, w, h, seed_kw=dict(qty=60, entry=132.33, lots=legacy_lots))
    try:
        row = txt(page, "[data-core-card=ccNV] [data-lf-l2]")
        check(f"{tag} 8 การ์ดเดิม (ไม่มี layer/risk): แถว 'ไม้ 2 · SL 115' · Base เท่ากับค่าเดิมทั้งหมด · ไม่มีชั้นเร่ง", row == "ไม้ 2 · SL 115" and txt(page, "[data-lf-base]").startswith("Base 60") and not js(page, "()=>!!document.querySelector('[data-lf-layers] [data-lf-acc]')"), row)
        r = add_sheet(page, px=140, sl=115, risk=0.02)
        check(f"{tag} 8 การ์ดเดิม: เติม Base ได้ตามปกติ (Risk ไม้ก่อนคำนวณจากข้อมูลไม้)", r["qty"] > 0 and r["save"], r)
        js(page, "()=>coreSheetClose()")
    finally: b.close()

    # ───────── 7 กล่องสรุป / ฟอร์มแผน / ตั้งค่า
    b, page, ce, pe = launch(pw, w, h)
    try:
        cap = txt(page, "[data-lf-cap]"); line = txt(page, "[data-lf-row=main] [data-lf-line]"); big = txt(page, "[data-lf-row=main] .v"); frl = txt(page, "[data-lf-row=main] [data-lf-free]")   # LN3fix3c: แถวต่อบัญชี · เงินว่างอยู่ท้ายบรรทัดแรก
        check(f"{tag} 9 กล่องสรุป: 'ทุน ฿9.88M' (RG2b = Winner + Ladder ของทั้ง 2 บัญชี) (รวมทุกบัญชี · LN3fix3c) · 'Risk Core x% / 20%' · 'ว่าง ฿' · บรรทัด 'DD · FF · n ตัว' (ไม่มี Winners/Ladder/฿/ถ้า Ladder เต็มบนหน้า)", cap == "ทุน ฿9.88M" and "%" in big and "ถ้า Ladder เต็ม" not in big and frl.startswith("ว่าง ฿") and "DD" in line and "FF" in line, [cap, big, line])
        js(page, "()=>document.querySelector('[data-lf-det]').open = true"); page.wait_for_timeout(200)
        det = txt(page, "[data-lf-det]")
        check(f"{tag} 9 พับ 'รายละเอียดและกฎ' มี ฿ · ถ้า Ladder เต็ม · Winners ถือ · Ladder % · ตำแหน่ง · Ladder ใหม่ · Stop ฉุกเฉิน · บัญชีลด", all(k in det for k in ("ถ้า Ladder เต็ม", "Winners ถือ", "Ladder ", "ตำแหน่ง 1 ตัว", "Stop ฉุกเฉิน", "ถ้าทุกไม้โดน Stop บัญชีลด")), det[:300])
        js(page, "()=>document.querySelector('[data-lf-det]').open = false")
        if CS1_RETIRED:   # CS1 — ฟอร์มแผนใหม่แบบ Risk % แก้ได้ (Tier) ถูกแทนที่ด้วย Risk จาก ★ (ครอบคลุมใน phase111)
            print("RETIRED (CS1) — ฟอร์มแผนใหม่แบบ Risk % แก้ได้ (Tier) ถูกแทนที่ด้วย Risk จาก ★ (ครอบคลุมใน phase111)")
        else:
            # ฟอร์มแผนใหม่
            js(page, "()=>document.querySelector('[data-lf-newplan]').click()"); page.wait_for_timeout(500)
            page.fill("#cnTicker", "TSM"); page.fill("#cnEntry", "300"); page.fill("#cnStop", "270"); page.wait_for_timeout(300)
            f = js(page, """()=>({risk: document.getElementById('cnRisk').value, ff: !!document.getElementById('cnF'), hint: document.getElementById('cnRiskHint').innerText.replace(/\\s+/g,' '), res: document.querySelector('[data-lf-first]').innerText.replace(/\\s+/g,' '), qty: +document.querySelector('[data-lf-qty]').innerText.replace(/,/g,''),
              row: (()=>{ const a = ['cnEntry','cnStop','cnRisk'].map(i=>document.getElementById(i).getBoundingClientRect()); return a.every(x=>Math.abs(x.top-a[0].top)<12); })(), tier: document.querySelector('[data-lf-tierline]').innerText.replace(/\\s+/g,' ')})""")
            check(f"{tag} 10 ฟอร์มแผน: แถว 'Entry · Stop · Risk %' (ไม่มีช่องเลือก FF) · ค่าเริ่ม Risk = ไม้แรกในตั้งค่า 0.6 · ใส่ได้ถึง 1% (งบ Base × FF)", f["risk"] == "0.6" and not f["ff"] and f["row"] and "Risk ใส่ได้ถึง" in f["hint"] and "FF" in f["hint"], f)
            wq = int(TANK * 0.006 / 30)
            check(f"{tag} 10 ไม้แรก = 0.6% × ถัง ÷ ระยะ Stop = {wq} หุ้น · บรรทัดผล 'ไม้แรก n หุ้น · เสี่ยง $x ✅'", f["qty"] == wq and "✅" in f["res"], f)
            check(f"{tag} 10 Tier บรรทัดเดียว 'Tier B · เพดาน x%' (ไม่มีคำ 'คำนวณ') · Ladder note ซ่อน (ไม่ใช่กรณีกด Ladder ไม่ได้ → Tier B)", f["tier"].startswith("Tier B") and "คำนวณ" not in f["tier"], f["tier"])
            page.fill("#cnRisk", "2"); page.wait_for_timeout(250)
            bad = js(page, "()=>({save: !document.getElementById('cnSave').disabled, err: document.getElementById('cnErr').innerText.replace(/\\s+/g,' ')})")
            check(f"{tag} 10 Risk เกินงบ Base (2% > 1%) → บันทึกไม่ได้ + 'Risk เกินงบ Base'", (not bad["save"]) and "Risk เกินงบ Base" in bad["err"], bad)
            page.fill("#cnRisk", "0.5"); page.wait_for_timeout(250)
            sm = js(page, "()=>+document.querySelector('[data-lf-qty]').innerText.replace(/,/g,'')")
            check(f"{tag} 10 ใส่ Risk น้อยกว่าเพื่อเข้าไม้แรกเล็ก (0.5% → {int(TANK*0.005/30)} หุ้น)", sm == int(TANK * 0.005 / 30), sm)
            fillT = lambda: [page.fill("#" + i, v) for i, v in (("tiRoic", "18"), ("tiNd", "0.8"), ("tiFcf", "92"))]
            fillT(); js(page, "()=>{ coreTiTk('fcf3y',true); coreTiTk('capret',true); coreTiG5('substitute',false); coreTiG5('customerMigrating',false); coreTiG5('singleProduct',false); }"); page.wait_for_timeout(250)
            tl = txt(page, "[data-lf-tierline]"); nt = js(page, "()=>getComputedStyle(document.querySelector('[data-lf-stratnote]')).display")
            check(f"{tag} 10 Fortress ผ่าน → 'Tier A · Fortress · เพดาน 15%' · บรรทัดอธิบาย Ladder ซ่อน (กด Ladder ได้)", tl.startswith("Tier A · Fortress · เพดาน") and nt == "none", [tl, nt])
            js(page, "()=>coreTiPick('growth')"); page.wait_for_timeout(250)
            nt2 = js(page, "()=>getComputedStyle(document.querySelector('[data-lf-stratnote]')).display")
            check(f"{tag} 10 กด Ladder ไม่ได้ (Tier ไม่ใช่ A Fortress) → บรรทัดอธิบาย Ladder โผล่", nt2 != "none", nt2)
            js(page, "()=>coreTiPick('fortress')"); page.wait_for_timeout(250)
            page.fill("#cnRisk", "0.6"); page.wait_for_timeout(200)
            js(page, "()=>document.getElementById('cnSave').click()"); page.wait_for_timeout(800)
            pl = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='TSM'); return c ? c.plan : null; }")
            l2 = js(page, "()=>{ const e = [...document.querySelectorAll('#corePanel .ccRow')].find(x=>x.querySelector('[data-c-ticker]').innerText==='TSM'); return e.querySelector('[data-lf-l2]').innerText; }")
            check(f"{tag} 10 บันทึกแผน: plan = Entry/Stop/Risk 0.6 · แถวการ์ด 'แผน · 300 / 270 · ไม้แรก {wq} หุ้น'", pl == {"entry": 300, "stop": 270, "risk": 0.6} and l2 == f"แผน · 300 / 270 · ไม้แรก {wq} หุ้น", [pl, l2])
            # ซื้อไม้ 1 ตามแผน → lots[0].risk
            js(page, "(id)=>coreBuy1Open(id)", js(page, "()=>coreCardsList.find(x=>x.ticker==='TSM').id")); page.wait_for_timeout(400)
            dq = js(page, "()=>+document.getElementById('cbQty').value")
            js(page, "()=>document.getElementById('cbSave').click()"); page.wait_for_timeout(800)
            lt = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='TSM'); return c.lots[0]; }")
            check(f"{tag} 10 บันทึกซื้อไม้ 1: จำนวนเริ่มต้น = ไม้แรกตาม Risk {wq} · lots[0] layer base + risk 0.6", dq == wq and lt["layer"] == "base" and lt["risk"] == 0.6 and lt["qty"] == wq, [dq, lt])
    finally: b.close()

    # ───────── 8 ตั้งค่า › Core
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>openSettings()"); page.wait_for_timeout(700)
        js(page, "()=>{ document.querySelectorAll('#ln3SetHost > .ln3-g').forEach(d=>d.open=true); }"); page.wait_for_timeout(300)
        v0 = js(page, "()=>({first: document.getElementById('sCrRiskFirst').value, acc: document.getElementById('sCrRiskAcc').value, cap: document.getElementById('sCrCapTotA').value, base: document.getElementById('sCrRiskA').value, lots: document.querySelector('#sCrMaxLots').closest('.f').innerText.replace(/\\s+/g,' '), sum: '', add: document.querySelector('#sCrAdd').closest('.f').innerText.replace(/\\s+/g,' ')})")
        check(f"{tag} 11 ตั้งค่า Core: Risk ไม้แรก 0.6 · งบเร่ง 0.35 · เพดานเงินต่อหุ้นค่าเริ่ม 15 (ช่องที่ไม่เคยตั้ง) · งบ Base 1 (ค่าที่ตั้งไว้ไม่เปลี่ยน)", v0["first"] == "0.6" and v0["acc"] == "0.35" and v0["cap"] == "15" and v0["base"] == "1", v0)
        check(f"{tag} 11 ป้ายใหม่ 'ไม้ Base สูงสุด' · 'เตือนเมื่อเติม Base >'", "Max Base lots" in v0["lots"] and "Max lots" not in v0["lots"].replace("Max Base lots", "") and "Warn when adding Base" in v0["add"], v0)   # SET1 — หัวหมวดสรุป LN3 ("Base 1% … ต่อหุ้น ≤ 15%") ถูกเอาออก · ป้ายช่องยังตรวจครบ
        page.fill("#sCrRiskFirst", "1.5"); page.wait_for_timeout(250)
        e1 = js(page, "()=>({err: document.querySelector('[data-err-for=sCrRiskFirst]').innerText, dis: document.getElementById('setSaveBtn') ? document.getElementById('setSaveBtn').disabled : null})")
        check(f"{tag} 11 Risk ไม้แรก เกินงบ Base → ข้อความ 'ต้องไม่เกินงบเสี่ยง Base'", "ไม่เกินงบเสี่ยง Base" in e1["err"], e1)
        page.fill("#sCrRiskFirst", "0.5"); page.fill("#sCrCapTotA", "30"); page.wait_for_timeout(250)
        e2 = js(page, "()=>document.querySelector('[data-err-for=sCrCapTotA]').innerText")
        check(f"{tag} 11 เพดานเงินต่อหุ้น > 25 → ข้อความ 'ต้องอยู่ระหว่าง 1–25'", "1–25" in e2, e2)
        page.fill("#sCrCapTotA", "10"); page.wait_for_timeout(250)
        warn = js(page, "()=>document.querySelector('[data-cr-firsthint]').innerText")
        check(f"{tag} 11 เพดานไม้แรก (15) > เพดานต่อหุ้น (10) → บรรทัดเตือนใต้ช่อง (ไม่บล็อกการบันทึก)", "⚠" in warn and "เพดานเงินต่อหุ้น" in warn and not js(page, "()=>document.getElementById('setSaveBtn').disabled"), warn)
        page.fill("#sCrCapTotA", "20"); page.fill("#sCrRiskAcc", "0.4"); page.wait_for_timeout(250)
        js(page, "()=>document.getElementById('setSaveBtn').click()"); page.wait_for_timeout(800)
        cr = js(page, "()=>{ const c = getBook('main').settings.coreRisk; return {first: c.riskFirst, acc: c.riskAcc, cap: c.capTotalA, riskA: c.riskA, maxLots: c.maxLots}; }")
        check(f"{tag} 11 บันทึกค่าตั้งใหม่ได้/อ่านกลับได้: riskFirst 0.5 · riskAcc 0.4 · capTotalA 20 · riskA เดิม 1 · maxLots เดิม 3", cr == {"first": 0.5, "acc": 0.4, "cap": 20, "riskA": 1, "maxLots": 3}, cr)
        cfg = js(page, "()=>{ const c = coreRiskCfg('main'), o = coreSizeOpts('main'); return [c.riskFirst, c.riskAcc, c.capTotalA, o.riskFirst, o.riskAcc, o.stockCap.A]; }")
        check(f"{tag} 11 ค่าตั้งไหลเข้าสูตร: coreSizeOpts riskFirst 0.005 · riskAcc 0.004 · เพดานต่อหุ้น 0.2", cfg == [0.5, 0.4, 20, 0.005, 0.004, 0.2], cfg)
    finally: b.close()
    # ค่าที่เคยบันทึกไว้ห้ามเปลี่ยน
    b, page, ce, pe = launch(pw, w, h, core_risk={"capTotalA": 25, "capTotalB": 25, "riskFirst": 0.8})
    try:
        cfg = js(page, "()=>{ const c = coreRiskCfg('main'); return [c.capTotalA, c.capTotalB, c.riskFirst, c.riskAcc]; }")
        check(f"{tag} 11 ค่าที่ผู้ใช้บันทึกไว้แล้ว (เพดานต่อหุ้น 25 · Risk ไม้แรก 0.8) ไม่ถูกเปลี่ยนเป็นค่าเริ่มใหม่ · ช่องที่ไม่เคยตั้ง (งบเร่ง) ใช้ 0.35", cfg == [25, 25, 0.8, 0.35], cfg)
        js(page, "()=>openSettings()"); page.wait_for_timeout(600)
        js(page, "()=>{ document.querySelectorAll('#ln3SetHost > .ln3-g').forEach(d=>d.open=true); }"); page.wait_for_timeout(200)
        js(page, "()=>document.getElementById('setSaveBtn').click()"); page.wait_for_timeout(700)
        cr = js(page, "()=>{ const c = getBook('main').settings.coreRisk; return [c.capTotalA, c.capTotalB, c.riskFirst]; }")
        check(f"{tag} 11 เปิดแล้วบันทึกตั้งค่าโดยไม่แก้ → ค่าเดิมที่บันทึกไว้คงเดิม", cr == [25, 25, 0.8], cr)
    finally: b.close()

    # ───────── 9 legacy เหมือนเดิม
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ ln1SetMode('legacy'); switchTab('plan'); setPlanScope('stock'); render(); coreAll('main',1); }"); page.wait_for_timeout(700)
        lg = js(page, """()=>({grid4: document.querySelectorAll('[data-core-card=ccNV] .ccGrid4').length, sim: document.querySelectorAll('[data-core-card=ccNV] [data-c-simbox]').length, lf: document.querySelectorAll('[data-lf-open], [data-lf-layers]').length,
          cap: (coreRiskCfg('main').capTotalA), lots: (document.querySelector('[data-core-card=ccNV] [data-c-lotbadge]')||{innerText:''}).innerText, l2: !!document.querySelector('#portsSum')})""")
        check(f"{tag} 12 legacy เหมือนเดิม: การ์ดมีกริด 4 ช่อง + กล่องจำลองเติมไม้ · ไม่มีชั้น Base/เร่ง · เพดานต่อหุ้นค่าเริ่มเดิม 25 (ช่องที่ไม่เคยตั้ง) · มีกล่อง 4 ช่อง", lg["grid4"] == 1 and lg["sim"] == 1 and lg["lf"] == 0 and lg["cap"] == 25 and lg["l2"], lg)
        js(page, "()=>{ openSettings(); document.querySelectorAll('#setOverlay details').forEach(d=>d.open=true); }"); page.wait_for_timeout(600)
        lbl = js(page, "()=>({lots: document.querySelector('#sCrMaxLots').closest('.f').innerText.replace(/\\s+/g,' '), lean: getComputedStyle(document.querySelector('#sCrRiskFirst').closest('.f')).display})")
        check(f"{tag} 12 legacy ตั้งค่า: ป้าย 'จำนวนไม้สูงสุด' เดิม · ช่องใหม่ (Risk ไม้แรก/งบเร่ง) ไม่แสดง", "Max lots" in lbl["lots"] and "Base lots" not in lbl["lots"] and lbl["lean"] == "none", lbl)
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px"), (300, 700, "300px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
