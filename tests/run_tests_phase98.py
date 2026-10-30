#!/usr/bin/env python3
"""PF1 — Strategy = Macro อย่างเดียว · ฟอร์มแผนใหม่ (TF / Trend / Classify · Zone Activation · Setup 3 ข้อ) · ถอดระบบ Trend ของ Strategy · เทส 98
Chromium · FF_STUB_BASE = Lean · 300 / 320 / 390 / 1280 / 1440
ภาพ tests/screenshots/pf1-{strategy-300,strategy-390,strategy-1440,form-main-390,form-tactical-390,form-main-1440,form-tactical-1440}.png
รัน: python3 run_tests_phase98.py"""
from pf2_retire import retired_wm1 as retired3
import json, os
from pf2_retire import retired as retired2
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase77 as P77
import run_tests_phase93 as P93

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
TV1 = "https://www.tradingview.com/x/pSb8OxWO/"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=450): page.wait_for_timeout(ms)


def launch(pw, w, h, bias="Short"):
    """XAUUSD: Strategy bias เก่า = bias (ไว้พิสูจน์ว่าไม่ถูกอ่านแล้ว) · Playbook seed (Macro XAUUSD ▲) · Lean"""
    b, page, ce, pe = P93.launch(pw, w, h, bias=bias, pb=True)
    return b, page, ce, pe


def new_plan(page, sleeve="main", asset="XAUUSD"):
    iid = js(page, "([a,s])=>{ lfSatSet(a); const i = satV2NewPlan(a,s); satV3Render({force:true}); return i; }", [asset, sleeve]); settle(page, 600)
    return iid


def idea(page, iid): return js(page, "(i)=>JSON.parse(JSON.stringify(satIdeasList.find(x=>x.id===i)||null))", iid)


def sel_opt(page, iid, which, val):
    if which == "classify-sel": val = {"strong": "clear", "normal": "clear", "uncertain": "unclear"}.get(val, val)   # CS1 — Classify เหลือ Clear Trend / Unclear
    page.locator(f'.ln1-form [data-pf-{which}]').first.select_option(val); settle(page, 450)


ROWS = """()=>{
  const f = document.querySelector('.ln1-form'); if(!f) return null;
  const R = e => { const b = e.getBoundingClientRect(); return {l:b.left, r:b.right, t:b.top, b:b.bottom, w:b.width, h:b.height}; };
  const tw = (el, txt) => { const c = document.createElement('canvas').getContext('2d'); const cs = getComputedStyle(el); c.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily; return c.measureText(txt).width; };
  const innerW = el => { const cs = getComputedStyle(el); return el.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight); };
  const seg = f.querySelector('.ln1-seg'), st = f.querySelector('.ln3-st'), r1 = f.querySelector('[data-pf-row="1"] .pf-r1') || f.querySelector('.pf-r1'), r2 = f.querySelector('[data-pf-row="2"]'), r3 = f.querySelector('[data-pf-row="3"]'), pr = f.querySelector('[data-ln1-prices]');
  const kids = [...r1.children].map(R), z = [...f.querySelectorAll('[data-pf-row="2"] > *')].map(R), ch = [...f.querySelectorAll('.pf-chip')].map(R);
  const sels = [...f.querySelectorAll('.pf-r1 select')].map(s => { const o = s.options[s.selectedIndex]; return {txt: o.textContent, need: tw(s, o.textContent), have: innerW(s) + (getComputedStyle(s).appearance === 'none' ? 0 : -18)}; });
  const chips = [...f.querySelectorAll('.pf-chip')].map(c => ({txt: c.textContent.trim(), clip: c.scrollWidth > c.clientWidth + 1, need: tw(c, c.textContent.trim()), have: c.clientWidth}));
  const stE = f.querySelector('.ln3-st'), stl = {h: stE.getBoundingClientRect().height, clip: stE.scrollWidth > stE.clientWidth + 1, fs: parseFloat(getComputedStyle(stE).fontSize), names: !!(stE.querySelector('.ln2-fn .dn') && stE.querySelector('.ln2-fn .dn').getClientRects().length), txt: stE.innerText};
  const zt = f.querySelector('[data-pf-ztxt]'), zv = zt.value || '4,230–4,250';
  const zneed = tw(zt, zv), zhave = innerW(zt);
  const ord = [seg, st, r1, r2, r3, pr].map(e => e ? R(e).t : null);
  const fr = f.querySelector('[data-pf-assess]'), fr3 = f.querySelector('[data-pf-row="3"]');
  const frames = {f1: fr ? fr.innerText.split('\\n')[0] : null, in1: fr ? (fr.contains(r1) && fr.contains(r2)) : false, f2: fr3 ? fr3.innerText.split('\\n')[0] : null, f2sep: fr3 ? (!fr.contains(fr3)) : false};
  return {ord, tops1: kids.map(k=>Math.round(k.t)), tops2: z.map(k=>Math.round((k.t+k.b)/2)), tops3: ch.map(k=>Math.round(k.t)), sels, chips, zneed, zhave, ow: document.documentElement.scrollWidth - innerWidth,
    tfw: kids[0].w, lasts: [kids[kids.length-1].r, z[z.length-1].r, ch[ch.length-1].r, R(f).r],
    frames, stl, txt: f.innerText, tfIn: !!f.querySelector('.ln1-more [data-v2-tf]'), idea: !!f.querySelector('[data-ln3-idea]'), dirBtn: f.querySelectorAll('[data-dir]').length, oldChips: f.querySelectorAll('[data-v2-setup]').length,
    zwarn: !!f.querySelector('[data-ln3-zwarn]') || /ไม่อยู่ใน Zone/.test(f.innerText)};
}"""


def rows(page): return js(page, ROWS)


def one_line(tops): return max(tops) - min(tops) <= 2


def strategy_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ satwWrite('XAUUSD', {opinion_txt: 'ถือ Long ตาม Macro', chart: {url: '%s', at: '2026-10-20'}}); }" % TV1); settle(page, 500)
        js(page, "()=>{ lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 500)
        t = js(page, """()=>{ const e = document.querySelector('[data-ln1-tile="XAUUSD"]'); const T = e.innerText.replace(/\\s+/g,' ');
          return {pill: e.querySelectorAll('.ln1-pill,[data-ln1-trend]').length, flat: e.querySelectorAll('[data-ln1-flat]').length, zone: e.querySelectorAll('[data-ln3-zone],[data-ln3-bp],[data-ln3-shift]').length, empty: e.querySelectorAll('[data-ln3-trend-empty]').length,
            hist: e.querySelectorAll('[data-ln3-hist],[data-ln3-tlog]').length, nt: e.querySelectorAll('[data-ln1-notrade]').length, ask: e.querySelectorAll('[data-ln3-ask]').length, T,
            macro: !!e.querySelector('[data-ln1-row=macro]'), chg: !!e.querySelector('[data-ln3-chg]'), ta: !!e.querySelector('textarea[data-ln3-opinion]'), cap: (e.querySelector('[data-ln1-cap]')||{}).textContent || '',
            del: !!e.querySelector('[data-vw-img-del]'), tv: !!e.querySelector('[data-ln1-tv]'), plan: (e.querySelector('[data-ln1-plan]')||{}).disabled,
            tabs: document.querySelectorAll('[data-wa-chip]').length, wk: !!document.getElementById('satV3WeekSel'), risk: document.querySelectorAll('[data-ln2-row]').length, ow: document.documentElement.scrollWidth - innerWidth}; }""")
        check(f"{tag} 1 Strategy: ไม่มี Trend/Flat · Zone ▲▼ · B&P · Shift · ข้อความ ยังไม่เลือก Trend · ประวัติสลับ · งดเทรด · กล่องเหตุผลสลับ",
              t["pill"] == 0 and t["flat"] == 0 and t["zone"] == 0 and t["empty"] == 0 and t["hist"] == 0 and t["nt"] == 0 and t["ask"] == 0 and not any(x in t["T"] for x in ("Trend Shift", "Flat", "B&P", "ประวัติสลับ", "งดเทรด", "ยังไม่เลือก Trend", "My opinion")), {k: v for k, v in t.items() if k != "T"} | {"T": t["T"][:200]})
        retired3(f"{tag} 1 Strategy: รูป + คำกำกับ 'ภาพ Week with EMA50' + ปุ่มลบรูป + ปุ่ม TradingView", "WM1 §7 — ไม่มีรูป/ลิงก์ chart ใน Strategy (w.chart ยังเก็บในข้อมูล)")
        check(f"{tag} 1 Strategy (WM1): Quarterly Macro · Change if · Note · This week (textarea) · ไม่มีรูป/TradingView", t["macro"] and t["ta"] and "Note · This week" in t["T"] and "Quarterly Macro" in t["T"] and not t["del"] and not t["tv"], t)
        check(f"{tag} 1 Strategy: แท็บ Asset · เลือกสัปดาห์ · Risk Sat ทุกบัญชี ยังอยู่ · + แผน กดได้โดยไม่มี Trend ใน Strategy · ไม่ล้นแนวนอน", t["tabs"] >= 2 and t["wk"] and t["risk"] == 2 and t["plan"] is False and t["ow"] <= 1, t)
        if label in ("390px", "300px", "1440px"):
            C.shot(page, f"pf1-strategy-{label.replace('px', '')}.png", sel=None, full=True)
        retired3(f"{tag} 1 ลบรูป: w.chart ถูกลบ · ความเห็นไม่เปลี่ยน", "WM1 §7 — ไม่มีปุ่มลบรูปใน Strategy แล้ว")
        # + แผน → ร่างใหม่ ไม่มี Trend
        page.locator('[data-ln1-tile="XAUUSD"] [data-ln1-plan]').first.click(); settle(page, 700)
        iid = js(page, "()=>{ const x = satIdeasList.filter(i=>i.v2 && i.asset==='XAUUSD').pop(); return x && x.id; }")
        x = idea(page, iid)
        check(f"{tag} 1 + แผน (Strategy bias เก่า = Short): แผนใหม่ bias ว่าง · classify/zone_act/setup_ck เริ่มว่าง · ไม่อ่าน Bias Strategy", x and x["bias"] == "" and x["classify"] == "" and x["zone_act"] is False and x["zone_act_txt"] == "" and x["setup_ck"] == [], x)
        check(f"{tag} 9 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def form_tests(pw, w, h, label, sleeve):
    tag = f"[{ENGINE}/{label}/{sleeve}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        iid = new_plan(page, sleeve)
        r = rows(page)
        # ลำดับ
        o = r["ord"]
        check(f"{tag} 2 ลำดับ: ส่วน → สถานะ → TF/Trend/Classify → Zone Activation → Setup → Entry/SL/TP", all(v is not None for v in o) and o == sorted(o), o)
        check(f"{tag} 2 ไม่มี Idea · ปุ่ม Long/Short · Setup เดิม · TF ใน 'เพิ่มเติม' · ⚠ ไม่อยู่ใน Zone", not r["idea"] and r["dirBtn"] == 0 and r["oldChips"] == 0 and not r["tfIn"] and not r["zwarn"] and "Idea" not in r["txt"], {k: r[k] for k in ("idea", "dirBtn", "oldChips", "tfIn", "zwarn")})
        d0 = idea(page, iid)
        opts = js(page, "()=>({tf:[...document.querySelector('[data-pf-tf]').options].map(o=>o.value), tr:[...document.querySelector('[data-pf-trend-sel]').options].map(o=>o.textContent), cl:[...document.querySelector('[data-pf-classify-sel]').options].map(o=>o.textContent), tfv: document.querySelector('[data-pf-tf]').value, trv: document.querySelector('[data-pf-trend-sel]').value, clv: document.querySelector('[data-pf-classify-sel]').value})")
        want_tf = "D" if sleeve == "main" else "4H"
        check(f"{tag} 2 TF = 15m 30m 1H 4H D W · ค่าเริ่ม = ค่า default ({want_tf}) · Trend เริ่ม '— เลือก —' (Up/Down เท่านั้น) · Classify เริ่ม '— เลือก —'",
              opts["tf"] == ["15m", "30m", "1H", "4H", "D", "W"] and opts["tfv"] == want_tf and opts["tr"] == ["— เลือก —", "▲ Up", "▼ Down"] and opts["trv"] == "" and opts["clv"] == "" and opts["cl"][0] == "— เลือก —" and d0["bias"] == "", opts)
        check(f"{tag} 2 แถว 1 / 2 / 3 อยู่บรรทัดเดียว (top ± 2px) · ไม่ล้นแนวนอน · ไม่ล้นขอบการ์ด", one_line(r["tops1"]) and one_line(r["tops2"]) and one_line(r["tops3"]) and r["ow"] <= 1 and max(r["lasts"][:3]) <= r["lasts"][3] + 1, r)
        check(f"{tag} 2 TF แคบ ({'≈40–48' if w <= 340 else '≈60'}px) · chip 'MMT Shift Pivot' ไม่ถูกตัด · ช่อง Zone ใส่ '4,230–4,250' พอ",
              (r["tfw"] <= (48 if w <= 340 else 66)) and all(not c["clip"] for c in r["chips"]) and r["zneed"] <= r["zhave"] + 1, {"tfw": r["tfw"], "chips": r["chips"], "z": [r["zneed"], r["zhave"]]})
        check(f"{tag} 2 กรอบ 'Trade Overview (ภาพหลัก)' มีแถว TF/Trend/Classify + Zone Activation อยู่ในกรอบเดียวกัน · กรอบ 'Setup on minor' แยกต่างหาก · ไม่มีคำว่า ประเมินการเทรด",
              r["frames"] == {"f1": "Trade Overview (ภาพหลัก)", "in1": True, "f2": "Setup on minor", "f2sep": True} and "ประเมินการเทรด" not in r["txt"], r["frames"])
        stl = r["stl"]
        check(f"{tag} 11 บรรทัดสถานะ (ln2FormLine) บรรทัดเดียว ไม่ห่อ ไม่ถูกตัด · {'Mac คงชื่อบัญชี' if w >= 900 else 'มือถือซ่อนชื่อบัญชี เหลือจุดสี + จำนวนเงิน'}",
              stl["h"] <= 28 and not stl["clip"] and (stl["names"] == (w >= 900)), stl)
        # สร้าง order ไม่ได้เมื่อไม่มี Trend
        js(page, "([i])=>{ satV3PlanEdit(i,'entry','4180'); satV3PlanEdit(i,'sl','4117'); }", [iid]); settle(page, 500)
        st = js(page, "()=>{ const b = document.querySelector('.ln1-card [data-ui-save], .ln1-card .ui-save, .ln1-card button.ui-btn-pri[onclick*=satV3SaveReady]'); return {dis: b ? b.disabled : null, hint: (document.querySelector('[data-pf-trend-hint]')||{}).textContent || '', msg: [...document.querySelectorAll('[data-ln1-acct] .ui-hint')].map(e=>e.textContent)}; }")
        check(f"{tag} 3 ไม่มี Trend: บันทึกเป็นร่างได้ แต่ปุ่มบันทึก order ปิด + คำใบ้ 'เลือก Trend ก่อน' · ไม่สร้างไม้", st["dis"] is True and "เลือก Trend ก่อน" in st["hint"], st)
        js(page, "(i)=>satV3SaveReadyAccounts(i)", iid); settle(page, 500)
        n = js(page, "()=>acctList.reduce((s,a)=>s+getBook(a.id).trades.filter(t=>t.port==='satB').length,0)")
        check(f"{tag} 3 เรียกบันทึก order ตรง ๆ ตอนไม่มี Trend → ไม่มีไม้ถูกสร้าง", n == 0, n)
        # Trend Up → Long, สี
        sel_opt(page, iid, "trend-sel", "up")
        x = idea(page, iid)
        col = js(page, "()=>{ const s = document.querySelector('[data-pf-trend-sel]'); const st = document.querySelector('[data-ln3-trend] [data-pf-trend]'); return {sel: getComputedStyle(s).color, selTxt: s.options[s.selectedIndex].textContent, st: st ? getComputedStyle(st).color : null, stTxt: st ? st.textContent : null, hintTxt: (document.querySelector('[data-pf-trend-hint]')||{}).textContent || ''}; }")
        check(f"{tag} 4 Trend Up → bias Long · เขียว (rgb 31,157,107) พร้อมข้อความ ▲ Up ทั้งในช่องเลือกและสถานะบนการ์ด · คำใบ้ 'เลือก Trend' หาย (เหลือคำใบ้ TP)", x["bias"] == "Long" and col["sel"] == "rgb(31, 157, 107)" and col["st"] == "rgb(31, 157, 107)" and "Up" in col["selTxt"] and col["stTxt"] == "▲ Up" and "เลือก Trend" not in col["hintTxt"], col)
        # A4 — TP บังคับ + R:R
        def rrstate():
            return js(page, """()=>{ const f = document.querySelector('.ln1-form'), b = document.querySelector('.ln1-card button.ui-btn-pri[onclick*=satV3SaveReady]'), tp = f.querySelector('[data-pf-tp]');
              return {cls: f.querySelector('[data-pf-rr]').dataset.pfRr, t: f.querySelector('[data-pf-rrt]').textContent, p: f.querySelector('[data-pf-rrp]').textContent, dis: b ? b.disabled : null, hint: (document.querySelector('.ln1-card [data-pf-trend-hint]')||{}).textContent || '',
                need: tp.classList.contains('pf-need'), ph: tp.placeholder, lab: tp.parentElement.querySelector('label').textContent.trim(), lines: f.querySelectorAll('[data-pf-rr]').length, h: f.querySelector('[data-pf-rr]').getBoundingClientRect().height,
                below: f.querySelector('[data-pf-rr]').getBoundingClientRect().top >= f.querySelector('[data-ln1-prices]').getBoundingClientRect().bottom - 1}; }""")
        z0 = rrstate()
        check(f"{tag} 12 TP บังคับ ({sleeve}): ป้าย TP * แดง · placeholder 'ต้องใส่' · ช่องว่างขอบแดงอ่อน · แถบ R:R เดียวใต้ Entry/SL/TP 'ใส่ TP เพื่อคำนวณ R:R' + pill 'R:R —' · ปุ่มบันทึกปิด + คำใบ้ 'ใส่ TP ให้ R:R ≥ 1.5 ก่อน'",
              z0["lab"] == "TP *" and z0["ph"] == "ต้องใส่" and z0["need"] and z0["cls"] == "none" and z0["t"] == "ใส่ TP เพื่อคำนวณ R:R" and z0["p"] == "R:R —" and z0["dis"] is True and "ใส่ TP ให้ R:R ≥ 1.5 ก่อน" in z0["hint"] and z0["lines"] == 1 and z0["below"] and z0["h"] <= 28, z0)
        if sleeve == "tactical": sel_opt(page, iid, "classify-sel", "clear")   # CS1 — Tactical ต้อง Clear Trend ก่อนช่อง TP เปิด
        tpi = page.locator("[data-pf-tp]")
        tpi.fill("4000"); settle(page, 150); z1 = rrstate()
        tpi.fill("4243"); settle(page, 150); z2 = rrstate()
        tpi.fill("4300"); settle(page, 150); z3 = rrstate()
        tpi.blur(); settle(page, 600); z4 = rrstate(); xx = idea(page, iid)
        check(f"{tag} 12 R:R อัปเดตขณะพิมพ์: TP ผิดฝั่ง (แดง 'R:R —') · R:R 1.0 'ต่ำกว่าขั้นต่ำ 1.5' (แดง) · R:R 1.9 'ความเสี่ยง 63 · กำไร 120' (เขียว ✓) · ปิดปุ่มจนกว่าจะผ่าน · ผ่านแล้วปุ่มเปิด คำใบ้หาย tp ถูกเก็บ",
              z1["cls"] == "bad" and z1["t"] == "TP อยู่ผิดฝั่ง" and z1["p"] == "R:R —" and z1["dis"] is True
              and z2["cls"] == "bad" and z2["t"] == "ต่ำกว่าขั้นต่ำ 1.5" and z2["p"] == "R:R 1.0" and z2["dis"] is True
              and z3["cls"] == "ok" and z3["t"] == "ความเสี่ยง 63 · กำไร 120" and z3["p"] == "R:R 1.9 ✓"
              and z4["dis"] is False and z4["hint"] == "" and not z4["need"] and xx["tp"] == 4300, [z1, z2, z3, z4, xx["tp"]])
        # Classify สี ตาม Trend
        exp_up = {"strong": ("Clear Trend Up", "rgb(31, 157, 107)"), "normal": ("Clear Trend Up", "rgb(31, 157, 107)"), "uncertain": ("Unclear", "rgb(169, 110, 6)")}   # CS1
        got = {}
        for k, (txt, colr) in exp_up.items():
            sel_opt(page, iid, "classify-sel", k)
            got[k] = js(page, "()=>{ const s = document.querySelector('[data-pf-classify-sel]'); return [s.options[s.selectedIndex].textContent, getComputedStyle(s).color]; }")
        check(f"{tag} 4 Classify เมื่อ Up: Strong Up เขียว · Normal Up น้ำเงิน · Uncertain เหลือง (ข้อความอ่านได้) ", all(got[k] == [exp_up[k][0], exp_up[k][1]] for k in exp_up), got)
        sel_opt(page, iid, "classify-sel", "normal")
        # ตัวเลข/ทิศ: Trend Up → ready ของ Entry/SL ถูกฝั่ง
        c = js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x, acctList[0].id); return {lot: c.lot, ready: c.ready, noTrend: c.noTrend, offBias: c.offBias}; }", [iid])
        check(f"{tag} 4 Trend Up + Entry 4180 / SL 4117 → คำนวณไม้ได้ ready · ทั้งที่ Strategy bias เก่า = Short (ไม่ถูกอ่าน · ไม่ลดไม้ · ไม่นอกแผน)", c["lot"] and c["ready"] and not c["noTrend"], c)
        # สลับ Up → Down: ไม่มี prompt/เหตุผล/trend_log, classify ไม่เปลี่ยน + สีเปลี่ยน
        before = js(page, "()=>JSON.stringify(satWeekMap)")
        sel_opt(page, iid, "trend-sel", "dn")
        x = idea(page, iid)
        col = js(page, """()=>{ const s = document.querySelector('[data-pf-trend-sel]'), c = document.querySelector('[data-pf-classify-sel]'); return {sel: getComputedStyle(s).color, txt: s.options[s.selectedIndex].textContent, cl: c.options[c.selectedIndex].textContent, clc: getComputedStyle(c).color,
          ask: document.querySelectorAll('[data-ln3-ask],[data-ln3-why]').length, tl: /trend_log/.test(JSON.stringify(satWeekMap)), st: (document.querySelector('[data-ln3-trend] [data-pf-trend]')||{}).textContent}; }""")
        after = js(page, "()=>JSON.stringify(satWeekMap)")
        check(f"{tag} 4 Up → Down ทันที: bias Short · แดง + ▼ Down · ไม่มี popup/กล่องเหตุผล · ไม่เขียน trend_log/satWeek · Classify เดิม (normal) เปลี่ยนเป็น Normal Down สีม่วง",
              x["bias"] == "Short" and col["sel"] == "rgb(208, 69, 58)" and col["txt"] == "▼ Down" and col["st"] == "▼ Down" and col["ask"] == 0 and not col["tl"] and before == after and x["classify"] == "clear" and col["cl"] == "Clear Trend Down" and col["clc"] == "rgb(208, 69, 58)", col)
        got = {}
        for k in ("strong", "uncertain"):
            sel_opt(page, iid, "classify-sel", k)
            got[k] = js(page, "()=>{ const s = document.querySelector('[data-pf-classify-sel]'); return [s.options[s.selectedIndex].textContent, getComputedStyle(s).color]; }")
        check(f"{tag} 4 Classify เมื่อ Down: Strong Down แดง · Uncertain เหลือง", got["strong"] == ["Clear Trend Down", "rgb(208, 69, 58)"] and got["uncertain"] == ["Unclear", "rgb(169, 110, 6)"], got)
        # สวน Macro (Macro ▲ vs Down) ยังขึ้น และต้องใส่เหตุผล
        mw = js(page, "()=>({box: !!document.querySelector('[data-ln3-macro-box]'), txt: (document.querySelector('[data-ln3-macro-box]')||{}).innerText || '', offb: /สวน Bias|สวน Trend/.test(document.body.innerText)})")
        check(f"{tag} 5 Trend ของแผน (Down) สวน Macro ▲ → กล่อง 'สวน Macro · ใส่เหตุผล' ยังอยู่ · ไม่มีข้อความ สวน Bias/สวน Trend ทั้งหน้า", mw["box"] and "สวน Macro" in mw["txt"] and not mw["offb"], mw)
        # Zone Activation / Setup อิสระ
        page.locator('[data-pf-ztxt]').fill("4,230–4,250"); page.locator('[data-pf-ztxt]').blur(); settle(page, 400)
        x = idea(page, iid)
        check(f"{tag} 6 ติ๊ก Zone Activation + กรอก Zone → zone_act true / zone_act_txt · Setup ไม่ถูกติ๊กแทน", x["zone_act"] is True and x["zone_act_txt"] == "4,230–4,250" and x["setup_ck"] == [], {k: x[k] for k in ("zone_act", "zone_act_txt", "setup_ck")})
        if sleeve == "tactical": sel_opt(page, iid, "classify-sel", "clear")   # CS1
        for k in ("align_ma50",):
            page.locator(f'[data-pf-setup="{k}"]').check(force=True); settle(page, 350)
        x = idea(page, iid)
        zs = js(page, "()=>({z: document.querySelector('[data-pf-ztxt]').value !== '', s: [...document.querySelectorAll('[data-pf-setup]')].map(e=>e.checked)})")
        check(f"{tag} 6 ติ๊ก MA Align Overlap อย่างเดียว → setup_ck = [align_ma50] · Zone Activation ไม่เปลี่ยน · ตัวอื่นไม่ติ๊กตาม", x["setup_ck"] == ["align_ma50"] and x["zone_act"] is True and zs == {"z": True, "s": [False, True, False]}, [x["setup_ck"], zs])
        page.locator('[data-pf-setup="mmt_shift_pivot"]').check(force=True); page.locator('[data-pf-setup="in_zone"]').check(force=True); settle(page, 350)
        x = idea(page, iid)
        check(f"{tag} 6 ติ๊กครบ 3 ข้อ (ไม่บังคับ) · Zone เดิมยังอยู่ (Setup กับ Zone เก็บแยกกัน)", x["setup_ck"] == ["in_zone", "align_ma50", "mmt_shift_pivot"] and x["zone_act"] is True and x["zone_act_txt"] == "4,230–4,250", {k: x[k] for k in ("zone_act", "setup_ck")})
        # สลับ Main ⇄ Tactical: ค่าไม่หาย
        other = "tactical" if sleeve == "main" else "main"
        page.locator(f'[data-sleeve="{other}"]').click(); settle(page, 600)
        y = idea(page, iid)
        keep = all(y[k] == x[k] for k in ("bias", "classify", "zone_act", "zone_act_txt", "setup_ck")) and y["sleeve"] == other
        ui = js(page, "()=>({tr: document.querySelector('[data-pf-trend-sel]').value, cl: document.querySelector('[data-pf-classify-sel]').value, zt: document.querySelector('[data-pf-ztxt]').value, s: [...document.querySelectorAll('[data-pf-setup]')].map(e=>e.checked)})")
        check(f"{tag} 7 สลับ Main ⇄ Tactical ในร่างเดียวกัน: Trend/Classify/Zone/Setup ไม่หาย (ทั้งในข้อมูลและหน้าจอ)", keep and ui == {"tr": "dn", "cl": "clear" if sleeve == "tactical" else "unclear", "zt": "4,230–4,250", "s": [True, True, True]}, [keep, ui])
        page.locator(f'[data-sleeve="{sleeve}"]').click(); settle(page, 500)
        # reload: ปิด-เปิดฟอร์มใหม่ (render ใหม่) แล้วค่ายังอยู่ · แผนสองใบไม่ใช้ค่าร่วมกัน
        js(page, "()=>{ satV3Render({force:true}); }"); settle(page, 500)
        ui2 = js(page, "()=>({tr: document.querySelector('[data-pf-trend-sel]').value, zt: document.querySelector('[data-pf-ztxt]').value, s: [...document.querySelectorAll('[data-pf-setup]')].map(e=>e.checked)})")
        check(f"{tag} 7 วาดใหม่/เปิดใหม่ → ค่ายังอยู่", ui2 == {"tr": "dn", "zt": "4,230–4,250", "s": [True, True, True]}, ui2)
        if sleeve == "main":
            iid2 = new_plan(page, "main", "BTCUSD")
            z = idea(page, iid2)
            check(f"{tag} 7 แผนอีกใบ (BTCUSD) เริ่มว่าง — ค่าไม่รั่วข้ามแผน", z["bias"] == "" and z["classify"] == "" and z["zone_act"] is False and z["zone_act_txt"] == "" and z["setup_ck"] == [] and idea(page, iid)["zone_act_txt"] == "4,230–4,250", z)
            js(page, "(i)=>satV3IdeaDelete(i)", iid2); settle(page, 500)
        # ภาพ
        js(page, "(i)=>{ lfSatSet('XAUUSD'); ln3Open.add(i); satV3Render({force:true}); }", iid); settle(page, 500)   # PF3b — แผนร่างเปิดทีละอัน: ลบแผน 2 แล้วต้องกางแผนแรกกลับเอง
        if w in (390, 1440):
            sel_opt(page, iid, "trend-sel", "up"); sel_opt(page, iid, "classify-sel", "normal")
            page.locator('[data-pf-ztxt]').fill("4,230–4,250"); page.locator('[data-pf-ztxt]').blur()
            js(page, "([i])=>{ satV3PlanEdit(i,'entry','4180'); satV3PlanEdit(i,'sl','4117'); satV3PlanEdit(i,'tp','4300'); }", [iid]); settle(page, 500)
            C.shot(page, f"pf1-form-{sleeve if sleeve == 'main' else 'tactical'}-{w}.png", sel=".ln1-card", full=False)
        check(f"{tag} 9 ไม่มี console error · ไม่ล้นแนวนอน", not ce and not pe and rows(page)["ow"] <= 1, [ce[:2], pe[:2]])
    finally: b.close()


def tf_and_old(pw):
    tag = f"[{ENGINE}/old]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        # TF alias / unknown
        res = {}
        for tf in ("Daily", "1D", "Weekly", "4h", "1h", "2H"):
            iid = js(page, "([t])=>{ const id = 'tf' + Math.floor(Math.random()*1e6); sat7dWrite('satIdeas', id, {v3:true, v2:true, sleeve:'main', asset:'XAUUSD', bias:'Long', week: wpWeekKey(), created_at: new Date().toISOString(), entry:null, sl:null, tp:null, cancel_level:null, tf:t, setups:[], setup_note:'', status:'active', accts:{}}); ln3Open.add(id); lfSatSet('XAUUSD'); return id; }", [tf]); settle(page, 500)
            js(page, "()=>{ satV3Render({force:true}); }"); settle(page, 400)
            res[tf] = js(page, "(i)=>{ const f = document.querySelector('.ln1-card'); const s = f && f.querySelector('[data-pf-tf]'); return s ? [s.value, [...s.options].map(o=>o.value).join(','), (satIdeasList.find(x=>x.id===i)||{}).tf] : null; }", iid)
            js(page, "(i)=>satV3IdeaDelete(i)", iid); settle(page, 400)
        ok = (res["Daily"] and res["Daily"][0] == "D" and res["Daily"][2] == "Daily" and res["1D"][0] == "D" and res["Weekly"][0] == "W" and res["4h"][0] == "4H" and res["1h"][0] == "1H"
              and res["2H"][0] == "2H" and res["2H"][1].endswith(",2H") and res["2H"][2] == "2H")
        check(f"{tag} 8 TF เก่า: Daily/1D แสดง D · Weekly แสดง W · 4h → 4H · 1h → 1H · ค่านอกตัวเลือก (2H) แสดงและเก็บไว้ · ไม่เขียนทับ", ok, res)
        mg = js(page, """()=>{ const a = acctList[0].id; const B = getBook(a); const keep = B.settings.satV2; 
            B.settings.satV2 = {tfTac:'30m'}; const c1 = satV2Cfg(a).tfTac;
            B.settings.satV2 = {tfTac:'30m', tfMig:'PF1'}; const c2 = satV2Cfg(a).tfTac;
            B.settings.satV2 = {tfTac:'1H'}; const c3 = satV2Cfg(a).tfTac;
            B.settings.satV2 = {}; const c4 = [satV2Cfg(a).tfMain, satV2Cfg(a).tfTac];
            B.settings.satV2 = keep; return [c1, c2, c3, c4]; }""")
        check(f"{tag} 2 ค่าเริ่มต้น TF: Main D · Tactical 4H · ค่าที่บันทึกเดิม tfTac 30m (ไม่มี tfMig) → 4H · หลังบันทึกตั้งค่า (tfMig) เลือก 30m เองได้ · ค่าอื่นที่ผู้ใช้ตั้ง (1H) ไม่ถูกแตะ", mg == ["4H", "30m", "1H", ["D", "4H"]], mg)
        # แผนเก่า
        js(page, """()=>{ sat7dWrite('satIdeas', 'oldplan', {v3:true, v2:true, sleeve:'main', asset:'XAUUSD', bias:'Long', tf:'D', week: wpWeekKey(), created_at: new Date().toISOString(), entry:4180, sl:4117, tp:null, cancel_level:null,
            setups:['Break EMA20'], setup_note:'note เก่า', idea_txt:'ย่อมาแนวรับ', zone_ok:true, zone_txt:'4,280–4,320', zone_side:'dn', status:'active', accts:{}}); ln3Open.add('oldplan'); }"""); settle(page, 600)
        js(page, "()=>{ lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 500)
        o = js(page, """()=>{ const f = document.querySelector('.ln1-card'); const x = satIdeasList.find(i=>i.id==='oldplan');
          return {tr: f.querySelector('[data-pf-trend-sel]').value, cl: f.querySelector('[data-pf-classify-sel]').value, tf: f.querySelector('[data-pf-tf]').value, za: false, zt: f.querySelector('[data-pf-ztxt]').value,
            s: [...f.querySelectorAll('[data-pf-setup]')].map(e=>e.checked), doc: {setups: x.setups, idea: x.idea_txt, zok: x.zone_ok, ztxt: x.zone_txt, zside: x.zone_side, note: x.setup_note, bias: x.bias}, txt: f.innerText}; }""")
        check(f"{tag} 8 แผนเก่า (Long · D · Setup/Zone/Idea เก่า): เปิดได้ · Trend = Up · Classify ว่าง · TF = D · Zone/Setup ใหม่ว่าง · ฟิลด์เก่าอยู่ครบไม่ถูกแปลง · ไม่แสดง Idea/Setup เดิม",
              o["tr"] == "up" and o["cl"] == "" and o["tf"] == "D" and not o["za"] and o["zt"] == "" and o["s"] == [False, False, False]
              and o["doc"] == {"setups": ["Break EMA20"], "idea": "ย่อมาแนวรับ", "zok": True, "ztxt": "4,280–4,320", "zside": "dn", "note": "note เก่า", "bias": "Long"} and "ย่อมาแนวรับ" not in o["txt"] and "Break EMA20" not in o["txt"], o)
        # order ที่สร้างแล้วไม่ถูกแก้เมื่อเปลี่ยน Trend
        js(page, "()=>{ satV3PlanEdit('oldplan','tp','4300'); }"); settle(page, 400); js(page, "()=>satV3SaveReadyAccounts('oldplan')"); settle(page, 700)
        t0 = js(page, "()=>acctList.flatMap(a=>getBook(a.id).trades.filter(t=>t.port==='satB').map(t=>({id:t.id, bias:t.bias, entry:t.entry, sl:t.sl, qty:t.qty, ts:t.trend_state, tc:t.trend_changed, setups:t.setups})))")
        js(page, "()=>satV2SetDir('oldplan','Short')"); settle(page, 500)
        t1 = js(page, "()=>acctList.flatMap(a=>getBook(a.id).trades.filter(t=>t.port==='satB').map(t=>({id:t.id, bias:t.bias, entry:t.entry, sl:t.sl, qty:t.qty, ts:t.trend_state, tc:t.trend_changed, setups:t.setups})))")
        check(f"{tag} 8 บันทึก order จากแผนเก่า (ฝั่ง Long) แล้วเปลี่ยน Trend เป็น Down → order/ไม้เดิมไม่ถูกแก้ (ทิศ · ราคา · lot) · trend_state ว่าง (ไม่อ่าน Strategy)", len(t0) >= 1 and t0 == t1 and all(t["bias"] == "Long" and t["ts"] is None and t["tc"] is None for t in t0), [t0, t1])
        check(f"{tag} 9 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def removed_rules(pw):
    tag = f"[{ENGINE}/rules]"
    b, page, ce, pe = launch(pw, 390, 844, bias="Short")
    try:
        iid = new_plan(page, "main")
        js(page, "([i])=>{ satV2SetDir(i,'Long'); satV3PlanEdit(i,'entry','4180'); satV3PlanEdit(i,'sl','4117'); satV3PlanEdit(i,'tp','4300'); }", [iid]); settle(page, 700)
        c = js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x, acctList[0].id); return {lot: c.lot, ready: c.ready, factor: c.factor, offBias: !!c.offBias, off: c.offplan, warns: c.warns}; }", [iid])
        txt = js(page, "()=>document.body.innerText")
        check(f"{tag} 5 Strategy bias เก่า = Short · แผน Long: ไม่มี 'สวน Bias / สวน Trend' ที่ไหนเลย · แผน ready · ไม้ไม่ลด (factor 1) · ไม่ติดนอกแผน", c["lot"] and c["ready"] and c["factor"] == 1 and not c["offBias"] and not any(k in txt for k in ("สวน Bias", "สวน Trend", "เปลี่ยนทิศ")), {**c, "t": [k for k in ("สวน Bias", "สวน Trend") if k in txt]})
        js(page, "(i)=>satV3SaveReadyAccounts(i)", iid); settle(page, 700)
        tg = js(page, "()=>{ const o = []; acctList.forEach(a=>getBook(a.id).trades.filter(t=>t.port==='satB').forEach(t=>o.push({off: tradeOffPlan(t), bias: t.bias, tag: /นอกแผน|สวน Bias/.test(posTagsHtml ? '' : '')}))); return o; }") if False else js(page, "()=>acctList.flatMap(a=>getBook(a.id).trades.filter(t=>t.port==='satB').map(t=>({off: tradeOffPlan(t), bias: t.bias, flag: !!t.offplanOverride})))")
        check(f"{tag} 5 ไม้ที่บันทึก (ทิศ Long สวน Strategy เก่า Short): ไม่ติดนอกแผน (offplanOverride false) · ทิศ Long", tg and all(not t["off"] and not t["flag"] and t["bias"] == "Long" for t in tg), tg)
        # Today: ไม่มีงาน Bias
        js(page, "()=>{ switchTab('today'); todayRefresh && todayRefresh(); }"); settle(page, 600)
        tt = js(page, "()=>document.body.innerText")
        check(f"{tag} 10 Today: ไม่มี 'Bias ยังไม่ประเมิน'", "Bias ยังไม่ประเมิน" not in tt, "")
        # สัปดาห์ใหม่: hint ไม่มีลูกศร
        check(f"{tag} 10 ฟังก์ชัน/ตัวแปรของระบบ Trend Strategy ถูกถอดออกจากแอป", js(page, "()=>['ln1Trend','ln1TrendOf','ln1Flat','ln1NoTrade','ln3TrendOk','satOffBias','satWeekBiasNow','satTradeOffBias','satwSetZone','satV3Warnings','ln3ZoneCheckHtml','satV3TrendSet'].filter(n=>typeof window[n]==='function')") == [], "")
        check(f"{tag} 9 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def newweek(pw):
    tag = f"[{ENGINE}/newweek]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        retired2(f"{tag} 10 สัปดาห์ใหม่: hint ของ nwRows", "prompt เริ่มสัปดาห์ใหม่ถอดแล้ว (PF2 A2)")
        check(f"{tag} 10 PF2 — ไม่มี nwRows/nwStart แล้ว", js(page, "()=>typeof nwRows==='undefined' && typeof nwStart==='undefined'"))
        fresh = js(page, "()=>Object.keys(satWeekFreshPatch()).sort()")
        check(f"{tag} 10 satWeekFreshPatch ล้างเฉพาะ opinion_txt (+updated_at) — ไม่แตะ/ไม่เคลียร์ฟิลด์ Trend เดิม", fresh == ["opinion_txt", "updated_at"], fresh)
        check(f"{tag} 9 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, lab in [(300, 700, "300px"), (390, 844, "390px"), (1440, 900, "1440px")]: strategy_tests(pw, w, h, lab)
        for w, h, lab in [(300, 700, "300px"), (320, 700, "320px"), (390, 844, "390px"), (1440, 900, "1440px")]:
            for sv in ("main", "tactical"):
                if lab in ("300px", "320px") and sv == "tactical": continue
                form_tests(pw, w, h, lab, sv)
        tf_and_old(pw)
        removed_rules(pw)
        newweek(pw)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
