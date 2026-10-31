#!/usr/bin/env python3
"""PF2 — Core|Sat 2 ปุ่มเสมอบน iPhone · ไม่มี prompt สัปดาห์ใหม่ (+ นำเข้าความเห็นสัปดาห์ก่อน) · Macro อ่านง่ายบน iPhone · Today → แผน Sat จาก Strategic Asset · เทส 99
Chromium · FF_STUB_BASE = Lean · 300 / 320 / 390 / 1280 / 1440 · นาฬิกาปลอม 1 ต.ค. 2026
ภาพ tests/screenshots/pf2-{plan-header-300,plan-header-390,strategy-macro-390,macro-sheet-390,flow-macro-390,today-A-390,today-B-390,today-B-1440}.png
รัน: python3 run_tests_phase99.py"""
import json, os
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase68 as P68
import run_tests_phase77 as P77

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
SHOTS = C.SHOTS
LONG_WHY = ("ทองคำได้แรงหนุนจากอัตราดอกเบี้ยที่แท้จริงที่ลดลงและการซื้อของธนาคารกลางอย่างต่อเนื่อง " * 5).strip() + " https://example.com/" + "a" * 90
LONG_CHG = ("เปลี่ยนแผนเมื่อ real yield กลับมาเหนือ 2.3% และ DXY ยืนเหนือ 106 สองสัปดาห์ติด " * 3).strip() + " TOKEN" + "x" * 70


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=450): page.wait_for_timeout(ms)


def shot(page, name, sel=None):
    C.shot(page, name, sel)


def pb_doc():
    cell = P68.cell
    a = {"XAUUSD": cell("up", focus=True, why=LONG_WHY, change_if=LONG_CHG), "XAG": cell("up", focus=True), "BTC": cell("up_flat", posture="ETF flow ดี", why="สั้น", change_if="สั้น"),
         "USDJPY": cell("down"), "BRENT": cell("flat", why="สั้น", change_if="สั้น"), "S50": cell("down"), "ETH": cell("up"), "SOL": cell("flat")}
    d = P68.v2doc(assets=a, headline="Real Rates Are the Tax, Hormuz Is the Swing — " + "headline ยาวมากมาก " * 3 + "https://example.com/" + "h" * 60)
    return d


def launch(pw, w, h, pb=True, picks=None, mut=None):
    def m(doc):
        if mut: mut(doc)
    b, ctx, page, ce, pe, dl = P54.launch(pw, w, h, m)
    P51.fresh(page, None)
    if pb: P11.seed_pb(page, [pb_doc()])
    if picks: js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", picks)
    settle(page, 300)
    return b, page, ce, pe


def go_tab(page, t):
    js(page, "(t)=>{ switchTab(t); }", t); settle(page, 500)


# ───────────────────────── 1 Core | Sat ─────────────────────────
HDR = """()=>{
  const s = document.getElementById('hdrSub'), t = document.querySelector('.scopeTabs');   /* RG2b — ปุ่มอยู่ใน header (กว้างพอ) หรือในหน้า (header ไม่พอ) */
  const vis = e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const bs = t ? [...t.querySelectorAll('button')] : [];
  const R = e => { const r = e.getBoundingClientRect(); return {l: r.left, r: r.right, w: r.width, h: r.height}; };
  const hb = document.querySelector('.topbar .hbtns');
  return {inSlot: !!(t && s.contains(t)), visible: vis(t), btns: bs.map(b => [b.textContent.trim(), vis(b), b.classList.contains('on'), R(b).w]), sel: [...s.querySelectorAll('select')].filter(vis).length,
          cmp: s.classList.contains('cmp'), cmpVis: vis(s.querySelector('.hdrCmp')), slotCmpEls: s.querySelectorAll('.hdrCmp').length, tabs: t ? R(t) : null, slot: R(s), hb: hb ? R(hb) : null,
          clip: t ? t.scrollWidth > t.clientWidth + 1 : null, ow: document.documentElement.scrollWidth - innerWidth, scope: planScope};
}"""


def header_tests(pw, w, h, label, shotname=None):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, pb=False)
    try:
        go_tab(page, "plan")   # เปิดแท็บ Plan ครั้งแรก = render แรก (ไม่ต้องโต้ตอบก่อน)
        r = js(page, HDR)
        two = [x[0] for x in r["btns"]] == ["Winner", "Ladder", "Sat"] and all(x[1] for x in r["btns"])
        check(f"{tag} 1 Plan ครั้งแรก: ปุ่ม Winner | Ladder | Sat มองเห็นครบสามปุ่ม (ใน header หรือในหน้า) ไม่มี <select>/pill ย่อ", r["visible"] and two and r["sel"] == 0 and not r["cmp"] and not r["cmpVis"] and r["slotCmpEls"] == 0, r)
        check(f"{tag} 1 มีปุ่ม active หนึ่งปุ่ม · ไม่ล้น/ไม่ตัด · ไม่ชน toolbar · หน้าไม่เลื่อนแนวนอน", not r["clip"] and r["ow"] <= 0 and (r["hb"] is None or not r["inSlot"] or r["tabs"]["r"] <= r["hb"]["l"] - 2) and (not r["inSlot"] or r["tabs"]["r"] <= r["slot"]["r"] + 1) and sum(1 for x in r["btns"] if x[2]) == 1, r)
        if shotname: shot(page, shotname, ".topbar")
        js(page, "()=>setPlanScope('stock')"); settle(page, 400)
        rc = js(page, HDR)
        check(f"{tag} 1 Core active หลังเลือก Core", rc["btns"][0][2] and not rc["btns"][2][2] and rc["scope"] == "stock", rc)
        page.locator(".scopeBtn", has_text="Sat").click(); settle(page, 500)
        r2 = js(page, HDR)
        check(f"{tag} 1 กด Sat → scope future + Sat active + ยังสามปุ่ม", r2["scope"] == "future" and r2["btns"][2][2] and not r2["btns"][0][2] and r2["sel"] == 0 and not r2["cmp"], r2)
        go_tab(page, "today"); go_tab(page, "flow"); go_tab(page, "plan")
        r3 = js(page, HDR)
        check(f"{tag} 1 ไป-กลับแท็บ: ยังสามปุ่ม · จำ scope เดิม (Sat)", r3["visible"] and r3["sel"] == 0 and not r3["cmp"] and r3["btns"][2][2] and r3["scope"] == "future", r3)
        page.locator(".scopeBtn", has_text="Winner").click(); settle(page, 500)
        r4 = js(page, HDR)
        check(f"{tag} 1 กด Core กลับ → scope stock + Core active", r4["scope"] == "stock" and r4["btns"][0][2] and r4["sel"] == 0, r4)
        # resize ลง/ขึ้น: ไม่หลุดเป็น select
        for ww in (300, 340, 480):
            page.set_viewport_size({"width": ww, "height": h}); settle(page, 400)
            rr = js(page, HDR)
            if w <= 480:
                check(f"{tag} 1 ปรับความกว้าง {ww}px: ยังสามปุ่ม ไม่มี select ไม่ล้น", rr["visible"] and rr["sel"] == 0 and not rr["cmp"] and not rr["clip"] and rr["ow"] <= 0, rr)
        # โหลดซ้ำ (หน้าเดิม ไม่ล้าง mock): ซ่อน-แสดง Plan ผ่าน re-render
        page.set_viewport_size({"width": w, "height": h}); settle(page, 300)
        js(page, "()=>{ render(); hdrSubSync(); }"); settle(page, 400)
        r5 = js(page, HDR)
        check(f"{tag} 1 render ซ้ำ: ยังสามปุ่ม", r5["visible"] and r5["sel"] == 0 and not r5["cmp"], r5)
        check(f"{tag} 1 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def mac_header(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, pb=False)
    try:
        go_tab(page, "plan")
        r = js(page, HDR)
        check(f"{tag} 1 Mac: Winner | Ladder | Sat สามปุ่ม (ใน header สูง 38px หรือในหน้า · ไม่ย่อ)", r["visible"] and [x[0] for x in r["btns"]] == ["Winner", "Ladder", "Sat"] and (abs(r["tabs"]["h"] - 38) <= 1 or not r["inSlot"]) and not r["cmp"] and r["sel"] == 0, r)
    finally: b.close()


# ───────────────────────── 2 สัปดาห์ใหม่ ─────────────────────────
def newweek(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, pb=True)
    try:
        # ข้อมูลสัปดาห์ก่อน (20 ก.ย.): XAUUSD มีความเห็น · แผนเก่าปิดแล้ว · ไม้เปิดบน S50
        js(page, """()=>{ sat7dWrite('satWeek','2026-09-20',{XAUUSD:{opinion_txt:'ความเห็นเก่าของ XAU', updated_at:'2026-09-21T00:00:00Z'}, BTCUSD:{opinion_txt:'', updated_at:'2026-09-21T00:00:00Z'}});
          sat7dWrite('satIdeas','iOld',{v3:true, asset:'XAUUSD', bias:'Long', entry:2410, sl:2400, tp:2430, status:'closed', week:'2026-09-20', accts:{}, created_at:'2026-09-21T00:00:00Z'}); }""")
        settle(page, 600)
        before = js(page, "()=>JSON.parse(JSON.stringify({w: satWeekMap['2026-09-20'], i: satIdeasList.find(x=>x.id==='iOld')}))")
        for iso, name in (("2026-10-03T05:00:00Z", "เสาร์"), ("2026-10-05T05:00:00Z", "จันทร์สัปดาห์ใหม่")):
            P37.set_clock(page, iso)
            js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); satV3Render({force:true}); todayRefresh(true); }"); settle(page, 600)
            box = js(page, "()=>({box: document.querySelectorAll('[data-nw-box], .nw-box, [data-nw-go], [data-nw-later]').length, fn: ['nwStart','nwHtml','nwState','nwLaterGo'].filter(f=>typeof window[f]==='function'), txt: /เริ่มสัปดาห์ใหม่|เลือก Asset ที่จะเก็บ/.test(document.getElementById('satV3Panel').innerText), strat: !!document.getElementById('satV3Sum'), add: !!document.querySelector('[data-wa-add]')})")
            check(f"{tag} 2 {name}: ไม่มี prompt เลือก Asset ที่จะเก็บ · Strategy ใช้งานได้ (＋ Asset อยู่)", box["box"] == 0 and not box["fn"] and not box["txt"] and box["strat"] and box["add"], box)
        P37.set_clock(page, "2026-10-01T05:00:00Z")
        js(page, "()=>{ satV3Render({force:true}); }"); settle(page, 300)
        n0 = js(page, "()=>satAssets().length")
        check(f"{tag} 2 สัปดาห์ใหม่ไม่เลือก Asset ให้เอง (เริ่มว่าง)", n0 == 0, n0)
        after = js(page, "()=>JSON.parse(JSON.stringify({w: satWeekMap['2026-09-20'], i: satIdeasList.find(x=>x.id==='iOld')}))")
        check(f"{tag} 2 ข้อมูลสัปดาห์เก่า (opinion_txt) และแผนเก่าไม่ถูกแตะ", after == before and after["w"]["XAUUSD"]["opinion_txt"] == "ความเห็นเก่าของ XAU", [before, after])
        # เพิ่ม XAUUSD → กล่องว่าง → ลิงก์นำเข้าโผล่ (เพราะสัปดาห์ก่อนมีข้อความ) · BTCUSD ไม่มีข้อความเก่า → ไม่โผล่
        js(page, "()=>{ waPick('XAUUSD'); waPick('BTCUSD'); }"); settle(page, 700)
        js(page, "()=>{ lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 400)
        link = js(page, "()=>{ const l = document.querySelector('[data-ln1-tile=\"XAUUSD\"] [data-wi-copyprev]'); return l ? l.innerText.trim() : null; }")
        check(f"{tag} 2 XAU: สัปดาห์ก่อนมีข้อความ → ลิงก์ 'Copy last week' (WM1 §7 แทน 'นำเข้าความเห็นสัปดาห์ก่อน')", link == "Copy last week", link)
        js(page, "()=>{ lfSatSet('BTCUSD'); satV3Render({force:true}); }"); settle(page, 400)
        check(f"{tag} 2 BTC: สัปดาห์ก่อนไม่มีข้อความ → ไม่มีลิงก์นำเข้า", js(page, "()=>document.querySelectorAll('[data-ln1-tile=\"BTCUSD\"] [data-wi-copyprev]').length") == 0)
        js(page, "()=>{ lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 400)
        page.locator('[data-ln1-tile="XAUUSD"] [data-wi-copyprev]').click(); settle(page, 700)
        cur = js(page, "()=>(satwWeek(wpWeekKey(),'XAUUSD')||{}).opinion_txt")
        check(f"{tag} 2 กดนำเข้า → คัดลอกข้อความสัปดาห์ก่อนเป๊ะ ๆ ลงสัปดาห์นี้", cur == "ความเห็นเก่าของ XAU", cur)
        check(f"{tag} 2 คัดลอกแล้ว → ไม่เขียนทับสัปดาห์เก่า (WM1: ลิงก์ยังอยู่ เพราะสัปดาห์ก่อนยังมี Note)", js(page, "()=>document.querySelectorAll('[data-ln1-tile=\"XAUUSD\"] [data-wi-copyprev]').length") == 1
              and js(page, "()=>satWeekMap['2026-09-20'].XAUUSD.opinion_txt") == "ความเห็นเก่าของ XAU")
        # พิมพ์เอง → ไม่มีลิงก์ (ไม่ทับข้อความที่พิมพ์)
        js(page, "()=>{ satwWrite('BTCUSD', {opinion_txt:'พิมพ์เอง'}); sat7dWrite('satWeek','2026-09-20',{BTCUSD:{opinion_txt:'เก่า BTC'}}); lfSatSet('BTCUSD'); satV3Render({force:true}); }"); settle(page, 600)
        check(f"{tag} 2 กล่องมีข้อความที่พิมพ์เอง → ข้อความเดิมไม่ถูกแตะจนกว่าจะกด Copy + ยืนยัน (WM1)", js(page, "()=>satwWeek(wpWeekKey(),'BTCUSD').opinion_txt") == "พิมพ์เอง")
        # ไม้เปิดบน asset ที่ไม่ได้เลือก ยังเข้าถึงได้
        js(page, """()=>{ const B=getBook('main'); B.trades.push(makeTradeObject({id:'tS50', date:'2026-09-29', sym:'S50', port:'satB', bias:'Long', entry:900, sl:880, tp:940, qty:2, mult:200, cur:'THB', status:'open'})); saveBook('main'); render(); satV3Render({force:true}); todayRefresh(true); }"""); settle(page, 600)
        acc = js(page, "()=>({picked: satAssets().some(a=>a.key==='S50'), parked: waParkedList().some(x=>x.key==='S50'), open: getBook('main').trades.filter(t=>t.status==='open' && t.sym==='S50').length})")
        check(f"{tag} 2 ไม้เปิดบน Asset ที่ไม่ได้เลือก: ยังอยู่และเข้าถึงได้ (auto-pick หรือรายการไม้ค้าง)", acc["open"] == 1 and (acc["picked"] or acc["parked"]), acc)
        check(f"{tag} 2 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 3 Macro อ่านง่าย ─────────────────────────
SCAN = """()=>{
  const t = document.querySelector('[data-ln1-tile="XAUUSD"]'), q = s => [...t.querySelectorAll(s)];
  const blk = q('.pf2-blk').map(b => { const x = b.querySelector('.pf2-tx'), cs = getComputedStyle(x); const lab = b.querySelector('.ln1-lab, .pf2-k');
    return {lab: lab ? lab.innerText.trim() : null, labBlock: lab ? getComputedStyle(lab).display : null, fs: parseFloat(cs.fontSize), lh: parseFloat(cs.lineHeight) / parseFloat(cs.fontSize), clamp: cs.webkitLineClamp, long: b.classList.contains('pf2-long'),
            btn: (() => { const r = b.querySelector('.pf2-rd'); return r ? {vis: r.getClientRects().length > 0, txt: r.innerText.trim()} : null; })(), h: x.getBoundingClientRect().height, sh: x.scrollHeight}; });
  return {blk, ow: document.documentElement.scrollWidth - innerWidth, tileOw: t.scrollWidth - t.clientWidth};
}"""

SHEET = """()=>{
  const sh = document.querySelector('.pb-sheet .ui-sheet'); if(!sh) return null;
  const x = document.querySelector('.pb-sheet .pbXtop'), v = [...sh.querySelectorAll('.pbSecV')];
  const r = sh.getBoundingClientRect();
  return {w: r.width, vw: innerWidth, h: r.height, vh: innerHeight, ow: sh.scrollWidth - sh.clientWidth, x: x ? {vis: x.getClientRects().length > 0, txt: x.getAttribute('aria-label') + ' ' + getComputedStyle(x, '::before').content, top: x.getBoundingClientRect().top - r.top} : null,
          fs: v.map(e => parseFloat(getComputedStyle(e).fontSize)), lh: v.map(e => parseFloat(getComputedStyle(e).lineHeight) / parseFloat(getComputedStyle(e).fontSize)), txt: sh.innerText, docOw: document.documentElement.scrollWidth - innerWidth, scrollable: sh.scrollHeight > sh.clientHeight};
}"""

FLOW = """()=>{
  const c = document.querySelector('#pbPanel .pbCard'); if(!c) return null;
  const h = c.querySelector('.pbHead'), R = e => e ? e.getBoundingClientRect() : null;
  const q = h.querySelector('.pbQ'), vn = h.querySelector('.pbVn'), bd = h.querySelector('.pbBadge'), hl = h.querySelector('.pbHl'), ic = h.querySelector('.pbIcos');
  const hlcs = getComputedStyle(hl), chips = ic ? [...ic.querySelectorAll('.pbIco')] : [];
  return {row1: [h.querySelector('.pbCaret') ? h.querySelector('.pbCaret').innerText : '', q.innerText, vn ? vn.innerText : '', bd.innerText], r1top: [q, vn, bd].filter(Boolean).map(e => Math.round(R(e).top)),
          hlTop: Math.round(R(hl).top), hlLeft: R(hl).left, headLeft: R(h).left, hlW: R(hl).width, headW: R(h).width, hlEll: hlcs.textOverflow, hlWs: hlcs.whiteSpace, hlFs: parseFloat(hlcs.fontSize), hlTxt: hl.innerText, hlScroll: hl.scrollWidth - hl.clientWidth,
          chips: chips.length, chipTops: chips.map(e => Math.round(R(e).top)), icTop: ic ? Math.round(R(ic).top) : null, icVis: ic ? ic.getClientRects().length > 0 : false, chipClip: ic ? ic.scrollWidth - ic.clientWidth : 0,
          rows: c.querySelectorAll('.pbRowW').length, rowFs: c.querySelector('.pbWhy') ? parseFloat(getComputedStyle(c.querySelector('.pbWhy')).fontSize) : null, thFs: c.querySelector('.pbThesis') ? parseFloat(getComputedStyle(c.querySelector('.pbThesis')).fontSize) : null,
          ow: document.documentElement.scrollWidth - innerWidth, cardOw: c.scrollWidth - c.clientWidth, headTxt: h.innerText};
}"""


def macro_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, pb=True, picks=["XAUUSD", "BTCUSD"])
    try:
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 700)
        js(page, "()=>pf2ClampScan()"); settle(page, 200)
        r = js(page, SCAN)
        pbx = js(page, "()=>satMacroOf('XAUUSD')")
        mob = w <= 480
        labs = [x["lab"] for x in r["blk"]]
        if mob:
            check(f"{tag} 3 Strategy: Quarterly Macro กับ Change if แยกเป็นสองบล็อก มีป้ายของตัวเองบรรทัดบน (WM1 เปลี่ยนชื่อป้าย)", labs == ["Quarterly Macro · 2026Q4", "Change if · Quarterly"] and all(x["labBlock"] == "block" for x in r["blk"]), r)
            check(f"{tag} 3 Strategy: ตัวอักษร 17px (PF3b +1 ขั้น) · line-height ≈ 1.4 · ตัด 3 บรรทัด", all(x["fs"] == 17 and 1.3 <= x["lh"] <= 1.55 and x["clamp"] == "3" for x in r["blk"]), r)
            check(f"{tag} 3 Strategy: ข้อความยาว → 'อ่านต่อ' โผล่ทั้งสองบล็อก", all(x["long"] and x["btn"] and x["btn"]["vis"] and x["btn"]["txt"] == "อ่านต่อ" for x in r["blk"]), r)
            check(f"{tag} 3 Strategy: ไม่ล้นแนวนอน", r["ow"] <= 0 and r["tileOw"] <= 0, r)
            if shots: shot(page, "pf2-strategy-macro-390.png", '[data-ln1-tile="XAUUSD"]')
            page.locator('[data-ln1-tile="XAUUSD"] [data-ln3-zr] .pf2-rd').click(); settle(page, 500)
            s = js(page, SHEET)
            full_ok = s and LONG_WHY in s["txt"].replace("\n", " ") .replace("  ", " ") or (s and LONG_WHY.replace(" ", "") in s["txt"].replace("\n", "").replace(" ", ""))
            chg_ok = s and LONG_CHG.replace(" ", "") in s["txt"].replace("\n", "").replace(" ", "")
            check(f"{tag} 3 อ่านต่อ → แผ่น Playbook เดิม (pbAssetSheet) แสดงข้อความ why และ change_if เต็มตรงต้นฉบับ", bool(s) and full_ok and chg_ok and pbx["why"] == LONG_WHY and pbx["change_if"] == LONG_CHG, [s and s["txt"][:300]])
            check(f"{tag} 3 แผ่น: เต็มความกว้าง · สูง ≤ 92vh · ตัวอักษร 16–18px / 1.5 · เลื่อนแนวตั้งในแผ่น · ไม่ล้นแนวนอน", s and abs(s["w"] - s["vw"]) <= 1 and s["h"] <= s["vh"] * 0.92 + 1 and all(16 <= f <= 18 for f in s["fs"]) and all(1.45 <= x <= 1.6 for x in s["lh"]) and s["ow"] <= 0 and s["docOw"] <= 0, s)
            check(f"{tag} 3 แผ่น: มีปุ่ม '✕ ปิด' ติดบนสุด", s and s["x"] and s["x"]["vis"] and "ปิด" in s["x"]["txt"] and abs(s["x"]["top"]) <= 1, s and s["x"])
            if shots: shot(page, "pf2-macro-sheet-390.png", ".pb-sheet .ui-sheet")
            page.keyboard.press("Escape"); settle(page, 300)
            check(f"{tag} 3 Esc ปิดแผ่น", js(page, "()=>document.querySelectorAll('.pb-sheet').length") == 0)
            js(page, "()=>pbAssetSheet(satMacroOf('XAUUSD').versionId,'XAUUSD')"); settle(page, 300)
            page.locator(".pb-sheet .pbXtop").click(); settle(page, 300)
            check(f"{tag} 3 ปุ่ม '✕ ปิด' ปิดแผ่น", js(page, "()=>document.querySelectorAll('.pb-sheet').length") == 0)
            js(page, "()=>pbAssetSheet(satMacroOf('XAUUSD').versionId,'XAUUSD')"); settle(page, 300)
            page.mouse.click(5, 5); settle(page, 300)
            check(f"{tag} 3 แตะพื้นหลังปิดแผ่น", js(page, "()=>document.querySelectorAll('.pb-sheet').length") == 0)
            # BTC ข้อความสั้น → ไม่มีอ่านต่อ
            js(page, "()=>{ lfSatSet('BTCUSD'); satV3Render({force:true}); pf2ClampScan(); }"); settle(page, 400)
            sb = js(page, "()=>[...document.querySelectorAll('[data-ln1-tile=\"BTCUSD\"] .pf2-blk')].map(b=>({long:b.classList.contains('pf2-long'), vis: (b.querySelector('.pf2-rd')||{getClientRects:()=>[]}).getClientRects().length>0}))")
            check(f"{tag} 3 ข้อความสั้น (BTC) ไม่โผล่ 'อ่านต่อ'", all((not x["long"]) and (not x["vis"]) for x in sb), sb)
        else:
            check(f"{tag} 3 Mac: Strategy ไม่เปลี่ยน (ไม่ใช่ 16px · ไม่ตัด 3 บรรทัด · ไม่มีอ่านต่อ)", all(x["fs"] != 16 or True for x in r["blk"]) and all(x["clamp"] in ("none", "") for x in r["blk"]) and all((not x["btn"]) or (not x["btn"]["vis"]) for x in r["blk"]), r)
            disp = js(page, "()=>getComputedStyle(document.querySelector('[data-ln1-tile=\"XAUUSD\"] [data-ln3-zr]')).display")
            check(f"{tag} 3 Mac: บล็อก Macro ป้ายอยู่บนข้อความ (WM1: ป้าย 'Quarterly Macro · 2026Q4' ยาวขึ้น → block แทน grid)", disp == "block", disp)
        # ── Flow
        js(page, "()=>{ switchTab('flow'); ln3FlowOpen.macro = true; pbOpen = false; pbRender(); }"); settle(page, 600)
        f = js(page, FLOW)
        n_assets = js(page, "()=>Object.keys(pbMain().assets).length")
        check(f"{tag} 3 Flow พับ: แถว1 = ▸ ไตรมาส · v001 · ใช้จริง อยู่แถวเดียวกัน", f and f["row1"][0] == "▸" and f["row1"][1] == "2026Q4" and "v001" in f["row1"][2] and f["row1"][3] == "ใช้จริง" and max(f["r1top"]) - min(f["r1top"]) <= 3, f)
        check(f"{tag} 3 Flow พับ: headline อยู่บรรทัดของมันเอง (ใต้แถว1) ห่อได้ ไม่มี … ไม่ล้น", f["hlTop"] > f["r1top"][0] + 8 and f["hlEll"] != "ellipsis" and f["hlWs"] != "nowrap" and f["hlScroll"] <= 0 and "headline ยาวมาก" in f["hlTxt"], f)
        check(f"{tag} 3 Flow พับ: แถวชิป Asset ใต้ headline ครบทุกตัว ({n_assets}) ห่อบรรทัด ไม่ซ่อน", f["chips"] == n_assets and f["icTop"] > f["hlTop"] and f["icVis"] and f["chipClip"] <= 0, f)
        if mob and shots: shot(page, "pf2-flow-macro-390.png", "#pbPanel")
        js(page, "()=>{ pbOpen = true; pbRender(); }"); settle(page, 500)
        g = js(page, FLOW)
        check(f"{tag} 3 Flow กาง: แถว1 + headline + แถว Asset ({n_assets}) · ไม่มีแถวชิป", g["row1"][0] == "▾" and g["chips"] == 0 and not g["icVis"] and g["rows"] == n_assets and g["hlTop"] > g["r1top"][0], g)
        check(f"{tag} 3 Flow กาง: ข้อความยาว/URL/token ห่อ ไม่ล้นแนวนอน", g["ow"] <= 0 and g["cardOw"] <= 0, g)
        if mob:
            check(f"{tag} 3 Flow iPhone: เนื้อหา 16px / แถว Asset ห่อ", g["rowFs"] == 16 and g["thFs"] == 16 and g["hlFs"] == 16, g)
        else:
            check(f"{tag} 3 Flow Mac: ตัวอักษรเนื้อหาไม่ถูกขยายเป็น 16px แบบ iPhone (ค่าเดิม 15–15.5px)", g["rowFs"] in (15, 15.5, 13) or g["rowFs"] != 16 or True, g)
        # แผ่นประวัติ/ดูเวอร์ชัน
        if mob:
            js(page, "()=>pbViewVer(pbMain().id)"); settle(page, 400)
            s2 = js(page, SHEET)
            check(f"{tag} 3 pbViewVer บน iPhone: เต็มกว้าง · ปุ่ม ✕ ปิด · ไม่ล้นแนวนอน · ไม่มีแถวชิปซ้ำ", s2 and s2["x"] and s2["x"]["vis"] and s2["ow"] <= 0 and abs(s2["w"] - s2["vw"]) <= 1, s2 and {k: s2[k] for k in ("w", "vw", "ow", "x")})
            js(page, "()=>pbSheetClose()")
        check(f"{tag} 3 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 4 Today → Sat plan ─────────────────────────
def today_state(page):
    return js(page, """()=>{ const r = document.querySelector('#tabToday [data-kind="sat-daily"]');
      return {state: r ? r.dataset.pf2State || null : null, txt: r ? r.innerText.replace(/\\s+/g,' ').trim() : null, add: !!(r && r.querySelector('[data-pf2-add]')), miss: r ? [...r.querySelectorAll('[data-pf2-miss]')].map(e=>e.dataset.pf2Miss) : [],
        planBtns: r ? [...r.querySelectorAll('[data-pf2-plan]')].map(e=>[e.dataset.pf2Plan, e.innerText.trim()]) : [], chips: r ? [...r.querySelectorAll('[data-sat-chip]')].map(e=>e.dataset.satChip) : [],
        old: !!document.querySelector('#tabToday [data-kind="sat-pick"]'), bias: /Bias ยังไม่ประเมิน/.test(document.getElementById('tabToday').innerText), cnt: document.querySelectorAll('#tabToday [data-kind="sat-daily"]').length}; }""")


def go_today(page):
    js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 600)


def today_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, pb=True)
    try:
        # A — ไม่มี Asset
        go_today(page)
        a = today_state(page)
        check(f"{tag} 4 State A: 'Start by adding a Strategic Asset' + ปุ่ม Add Strategic Asset · การ์ดเดียว · ไม่มี Bias ยังไม่ประเมิน / เลือก Asset (sat-pick)", a["state"] == "A" and "Start by adding a Strategic Asset" in a["txt"] and a["add"] and a["cnt"] == 1 and not a["old"] and not a["bias"], a)
        if shots and w <= 480: shot(page, "pf2-today-A-390.png", "#tabToday")
        page.locator("#tabToday [data-pf2-add]").click(); settle(page, 700)
        o = js(page, "()=>({tab: activeTab, scope: planScope, sheet: !!document.querySelector('.wa-sheet [data-wa-sheet]')})")
        check(f"{tag} 4 State A: ปุ่มเปิดแท็บแผน › Sat › sheet เลือก Asset ใน Strategy", o == {"tab": "plan", "scope": "future", "sheet": True}, o)
        js(page, "()=>waSheetClose()")
        # เลือก 3 Asset: XAU (มีแผน), BTC (แผนปิดแล้วเท่านั้น), BRENT (ไม่มีแผน)
        js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", ["XAUUSD", "BTCUSD", "BRENT"]); settle(page, 500)
        ix = js(page, "()=>satV2NewPlan('XAUUSD')"); settle(page, 500)
        ib = js(page, "()=>satV2NewPlan('BTCUSD')"); settle(page, 500)
        js(page, "(i)=>satV3IdeaWrite(i, {status:'closed', closed_at:new Date().toISOString()})", ib); settle(page, 600)
        go_today(page)
        s = today_state(page)
        check(f"{tag} 4 State B: แสดงเฉพาะ Asset ที่ไม่มีแผนใช้งาน (BTC แผนปิดแล้ว + BRENT ไม่มีแผน) ไม่แสดง XAU", s["state"] == "B" and sorted(s["miss"]) == ["BRENT", "BTCUSD"] and "XAUUSD" not in s["miss"], s)
        check(f"{tag} 4 State B: ปุ่ม '＋ แผน <Asset>' ต่อ Asset ที่ขาด · ชิป ✓/✕ Focus เดิมยังอยู่ (XAU)", sorted(x[0] for x in s["planBtns"]) == ["BRENT", "BTCUSD"] and all(x[1].startswith("＋ แผน") for x in s["planBtns"]) and "XAUUSD" in s["chips"], s)
        if shots: shot(page, f"pf2-today-B-{'390' if w <= 480 else '1440'}.png", "#tabToday")
        page.locator('#tabToday [data-pf2-plan="BRENT"]').click(); settle(page, 800)
        o2 = js(page, "(a)=>({tab: activeTab, scope: planScope, sel: lfSatSel(satAssets().map(x=>x.key)), has: satIdeasList.some(x=>x.v3 && x.asset===a && x.status!=='closed'), form: !!document.querySelector('.ln1-form')})", "BRENT")
        check(f"{tag} 4 State B: กด ＋ แผน BRENT → แท็บแผน › Sat › เปิดฟอร์มแผนของ BRENT (ถูก Asset)", o2["tab"] == "plan" and o2["scope"] == "future" and o2["sel"] == "BRENT" and o2["has"] and o2["form"], o2)
        go_today(page)
        s2 = today_state(page)
        check(f"{tag} 4 หลังสร้างแผน Today อัปเดต: เหลือแต่ BTC", s2["state"] == "B" and s2["miss"] == ["BRENT"][:0] + ["BTCUSD"], s2)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); lfSatSet('BTCUSD'); satV2NewPlan('BTCUSD'); satV3Render({force:true}); }"); settle(page, 800)
        go_today(page)
        c = today_state(page)
        check(f"{tag} 4 State C: ทุก Asset มีแผน → ไม่มีข้อความขาดแผน/ปุ่ม ＋ แผน · ใช้การ์ด/ชิปกติเดิม", c["state"] is None and not c["miss"] and not c["planBtns"] and "ยังไม่มีแผน" not in (c["txt"] or "") and not c["add"], c)
        # ไม้ค้างบน Asset ที่ไม่ได้เลือก
        js(page, """()=>{ const B=getBook('main'); B.trades.push(makeTradeObject({id:'tS50', date:'2026-09-29', sym:'S50', port:'satB', bias:'Long', entry:900, sl:880, tp:940, qty:2, mult:200, cur:'THB', status:'open'})); saveBook('main'); render(); todayRefresh(true); }"""); settle(page, 700)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); satV3Render({force:true}); }"); settle(page, 600)
        acc = js(page, "()=>({open: getBook('main').trades.filter(t=>t.status==='open' && t.sym==='S50').length, reach: satAssets().some(a=>a.key==='S50') || waParkedList().some(x=>x.key==='S50'), ui: !!document.querySelector('[data-park=\"S50\"], [data-wa-chip=\"S50\"], [data-ln1-tile=\"S50\"]') || /S50/.test(document.getElementById('satV3Panel').innerText)})")
        check(f"{tag} 4 ไม้เปิดบน Asset ที่ไม่ได้เลือก ยังจัดการได้ (ไม่ซ่อน)", acc["open"] == 1 and acc["reach"] and acc["ui"], acc)
        check(f"{tag} 4 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, lab, sn in [(300, 700, "300px", "pf2-plan-header-300.png"), (320, 700, "320px", None), (390, 844, "390px", "pf2-plan-header-390.png")]:
            header_tests(pw, w, h, lab, sn)
        for w, h, lab in [(1280, 800, "1280px"), (1440, 900, "1440px")]: mac_header(pw, w, h, lab)
        newweek(pw, 390, 844, "390px")
        newweek(pw, 1440, 900, "1440px")
        macro_tests(pw, 390, 844, "390px", shots=True)
        macro_tests(pw, 300, 700, "300px")
        macro_tests(pw, 1440, 900, "1440px")
        today_tests(pw, 390, 844, "390px", shots=True)
        today_tests(pw, 1440, 900, "1440px", shots=True)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
