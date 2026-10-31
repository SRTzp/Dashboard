#!/usr/bin/env python3
"""LN3fix3c — ＋ Asset เริ่มว่าง · Watch เต็มจอใช้ความกว้างเต็ม · Risk Sat / Risk Core ของทุกบัญชีเห็นพร้อมกัน (Sat = A · Core = C1) · เทส 96
Chromium · FF_STUB_BASE = Lean · 300 / 320 / 390 / 1280 / 1440
ภาพ tests/screenshots/ln3fix3c-{addasset-390,addasset-1440,watch-fullscreen-1440,watch-fullscreen-1280,risksat-300,risksat-390,risksat-1440,riskcore-390,riskcore-1440}.png
รัน: python3 run_tests_phase96.py"""
import json, os
from pf2_retire import retired as retired2
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase13 as P13
import run_tests_phase77 as P77
import run_tests_phase81 as P81
import run_tests_phase93 as P93
import run_tests_phase95 as P95

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
overflow = C.overflow
SEED = {"bias": "Short", "trend_dir": "down", "zone_up": "100-110", "zone_dn": "90-95", "zone_bp": True, "invalidation": 88, "opinion_txt": "ลงต่อ ตาม real yield",
        "support": [{"p": 90}], "resistance": [{"p": 110}], "flips": 0,
        "trend_log": [{"at": "2026-10-01T03:00:00Z", "from": "up", "to": "down", "why": "หลุด Zone"}, {"at": "2026-10-02T03:00:00Z", "from": "down", "to": "up", "why": "เด้งกลับ"}]}


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=500): page.wait_for_timeout(ms)


# ══════════════════════════ §1 ＋ Asset เริ่มว่าง
def db_btc(page):
    return js(page, "()=>{ const d = window.firebase.__mockDb.__getDoc(['users','testuid','satWeek', wpWeekKey()]); return d ? (d.BTCUSD || null) : null; }")


def seed_btc(page, listen=True):
    """BTC ยังไม่ถูกเลือกสัปดาห์นี้ แต่ในเอกสารสัปดาห์นี้ยังมีค่าเก่าค้าง (เคยเพิ่มแล้วเอาออก)"""
    js(page, "()=>satWeekPickWrite(wpWeekKey(), ['XAUUSD'])"); settle(page, 300)
    if listen:
        js(page, "(s)=>satwWrite('BTCUSD', s)", SEED); settle(page, 500)
    else:
        js(page, "(s)=>{ const wk = wpWeekKey(); const cur = JSON.parse(JSON.stringify(window.firebase.__mockDb.__getDoc(['users','testuid','satWeek', wk]) || {})); cur.BTCUSD = s; window.firebase.__mockDb.__seedDoc(['users','testuid','satWeek', wk], cur); }", SEED); settle(page, 200)


def tile_state(page):
    return js(page, """()=>{ const t = document.querySelector('[data-ln1-tile="BTCUSD"]'); if(!t) return null; const q = s => t.querySelector(s);
      return {on: [...t.querySelectorAll('[data-ln1-trend].on')].length, flat: !!(q('[data-ln1-flat]') && q('[data-ln1-flat]').checked), hint: (q('[data-ln3-trend-empty]')||{}).innerText || null,
        planDis: !!(q('[data-ln1-plan]') && q('[data-ln1-plan]').disabled), zu: (q('[data-ln3-zone=up]')||{}).value, zd: (q('[data-ln3-zone=dn]')||{}).value, bp: !!(q('[data-ln3-bp]') && q('[data-ln3-bp]').checked),
        shift: (q('[data-ln3-shift]')||{}).value, op: (q('[data-ln3-opinion]')||{}).value, hist: (q('[data-ln3-hist]')||{}).innerText || null}; }""")


def addasset(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = P93.launch(pw, w, h)
    try:
        seed_btc(page)
        before = js(page, "()=>satWeekPickList()")
        js(page, "()=>waPick('BTCUSD')"); settle(page, 700)
        P93.show(page, "BTCUSD")
        t = js(page, "()=>{ const t = document.querySelector('[data-ln1-tile=\"BTCUSD\"]'); return t ? {old: t.querySelectorAll('[data-ln1-trend],[data-ln1-flat],[data-ln3-zone],[data-ln3-shift],[data-ln3-bp],[data-ln3-trend-empty],[data-ln3-hist]').length, op: t.querySelector('[data-ln3-opinion]').value, plan: t.querySelector('[data-ln1-plan]').disabled} : null; }")
        check(f"{tag} 1 PF1 — ＋ Asset: BTC (มีค่าเก่าค้าง) → tile ไม่มี Trend/Flat/Zone/Shift/B&P/แถบเหลือง/ประวัติ · ความเห็นเรา ว่าง · ＋ แผน กดได้", before == ["XAUUSD"] and t == {"old": 0, "op": "", "plan": False}, [before, t])
        if w in (390, 1440): C.shot(page, f"ln3fix3c-addasset-{w}.png", full=False)
        d = db_btc(page)
        tt = js(page, "()=>{ const t = document.querySelector('[data-ln1-tile=\"BTCUSD\"]'); return {ta: t.querySelectorAll('textarea').length, ask: t.querySelectorAll('[data-ln3-ask]').length, yel: t.querySelectorAll('[data-ln3-trend-empty]').length}; }")
        check(f"{tag} 1 PF3 ＋ Asset: ไม่มีปุ่ม Trend on · ไม่มีช่องติ๊ก Flat · ไม่มีข้อความเหลือง · ＋ แผน กดได้ (ไม่ปิด)", t["old"] == 0 and tt["yel"] == 0 and t["plan"] is False, [t, tt])
        check(f"{tag} 1 PF3 ＋ Asset: ไม่มี Zone ▲/▼ · Shift · B&P · ประวัติสลับ ใน UI แต่ข้อมูลเก่ายังอยู่ใน DB (trend_log 2 · zone_up เดิม · invalidation เดิม)", t["old"] == 0 and d and len(d.get("trend_log") or []) == 2 and d.get("zone_up") == SEED["zone_up"] and d.get("invalidation") == SEED["invalidation"], d)
        check(f"{tag} 1 PF3 ＋ Asset แล้วไม่มีกล่องถามเหตุผล (ไม่มีปุ่ม Trend ให้เลือกครั้งแรก)", tt["ask"] == 0 and t["old"] == 0, tt)
        check(f"{tag} 1 PF3 ไม่มีกล่องเหตุผลหลังเลือกทิศตรงข้าม (ไม่มีปุ่ม) · textarea เดียว = ความเห็นเรา", tt["ta"] == 1 and tt["ask"] == 0, tt)
        check(f"{tag} 1 PF3 เพิ่มกลับจากไม้ค้าง: รีเซ็ตเฉพาะความเห็น (opinion_txt ว่าง) · Trend/Zone/Shift/B&P ไม่ถูกรีเซ็ต (เก็บข้อมูลเก่า)", d and d.get("opinion_txt") == "" and d.get("bias") == SEED["bias"] and d.get("zone_bp") == SEED.get("zone_bp") and d.get("zone_dn") == SEED.get("zone_dn"), d)
        check(f"{tag} 1 PF1 — เอกสารสัปดาห์ของ BTC: opinion_txt ว่าง · ฟิลด์ Trend/Zone/Shift/B&P/S-R/trend_log เดิมไม่ถูกแตะ (เก็บข้อมูลเก่า ไม่ใช้)",
              d and d.get("opinion_txt") == "" and d.get("bias") == SEED["bias"] and d.get("zone_up") == SEED["zone_up"] and d.get("invalidation") == SEED["invalidation"] and len(d.get("trend_log") or []) == 2 and d.get("updated_at"), d)
        ok3 = []
        for i in range(3):
            js(page, "()=>{ ln1Mem = null; }")
            js(page, "()=>satWeekPickWrite(wpWeekKey(), ['XAUUSD'])"); settle(page, 300)
            seed_btc(page, listen=False)
            js(page, "()=>waPick('BTCUSD')"); settle(page, 500)
            d = db_btc(page)
            ok3.append(bool(d and d.get("opinion_txt") == "" and d.get("zone_up") == SEED["zone_up"]))
        check(f"{tag} 1 ฝัง BTC ด้วย __seedDoc (ไม่ปลุก listener) แล้ว ＋ Asset 3 รอบ → ล้างความเห็นทุกรอบ (เขียน merge เสมอ)", ok3 == [True, True, True], ok3)
        js(page, "()=>{ lfSatSet('XAUUSD'); }"); settle(page, 300)
        js(page, "()=>satwWrite('XAUUSD', {opinion_txt: 'ความเห็นเดิม'})"); settle(page, 400)
        js(page, "()=>waPick('XAUUSD')"); settle(page, 500)
        keep = js(page, "()=>satwWeek(wpWeekKey(),'XAUUSD').opinion_txt")
        check(f"{tag} 1 Asset ที่เลือกอยู่แล้ว (ไม่มีการเพิ่มจริง) → ความเห็นเดิมอยู่ครบ ไม่ถูกรีเซ็ต", keep == "ความเห็นเดิม", keep)
        src = js(page, "()=>({nw: typeof nwStart==='undefined', pick: waPick.toString().includes('satWeekFreshWrite'), keys: Object.keys(satWeekFreshPatch()).sort()})")
        check(f"{tag} 1 ＋ Asset ใช้ satWeekFreshWrite · ฟิลด์ = opinion_txt + updated_at (PF1 · PF2: nwStart ถอดแล้ว)", src["pick"] and src["keys"] == ["opinion_txt", "updated_at"], src)
        has_copy = js(page, "()=>[...document.querySelectorAll('[data-ln3-links] button')].some(b=>b.innerText.includes('นำเข้าความเห็นสัปดาห์ก่อน'))")
        check(f"{tag} 1 PF2 — ลิงก์ 'นำเข้าความเห็นสัปดาห์ก่อน' ไม่โผล่เมื่อกล่องมีข้อความอยู่แล้ว (เดิม: 'คัดลอกจากสัปดาห์ก่อน' ยังมีให้กด)", not has_copy)
        js(page, "()=>ln1SetMode('legacy')"); settle(page, 500)
        lg = js(page, "()=>({pv2: document.querySelectorAll('[data-pv2-header]').length > 0, ln2: document.querySelectorAll('[data-ln2-row]').length})")
        check(f"{tag} 1 แบบเดิม (legacy) ยังวาดหัว PV2 เหมือนเดิม ไม่มีแถว Lean", lg["pv2"] and lg["ln2"] == 0, lg)
        check(f"{tag} 1 {label} ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: b.close()


# ══════════════════════════ §2 Watch เต็มจอ
def watch(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = P95.wlaunch(pw, w, h)
    try:
        P95.go(page)
        js(page, "()=>wlOpen('AVGO','sum')"); settle(page, 500)
        n0 = js(page, """()=>{ const p = document.querySelector('.wlDPanel'), c = document.querySelector('.wlDBody > *'); return {panel: Math.round(p.getBoundingClientRect().width), card: Math.round(c.getBoundingClientRect().width)}; }""")
        page.locator("[data-wl-full]").click(); settle(page, 600)
        js(page, """(u)=>{ const b = document.querySelector('.wlDBody'); const d = document.createElement('div'); d.className = 'panel wlOv'; d.id = 'p96pad';
          d.innerHTML = '<p id="p96p">' + 'บรรทัดทดสอบความกว้างข้อความอ่านยาว ๆ หลายประโยคต่อกัน test line measure '.repeat(14) + '</p><p>' + u + '</p><div class="ltTw" id="p96tw"><table><tr><th>รายได้แยกส่วน</th>' + Array.from({length: 30}, (_, i) => '<th>Q' + i + ' FY26</th>').join('') + '</tr><tr><td>AI</td>' + Array.from({length: 30}, (_, i) => '<td>' + (i * 3.1).toFixed(1) + '</td>').join('') + '</tr></table></div>';
          b.appendChild(d); }""", P95.LONGURL)
        settle(page, 300)
        g = js(page, """()=>{ const W = innerWidth, p = document.querySelector('.wlDPanel').getBoundingClientRect(), body = document.querySelector('.wlDBody'), kids = [...body.children].filter(k => k.id !== 'p96pad' && k.getBoundingClientRect().width > 0),
          c = kids[0] ? kids[0].getBoundingClientRect() : null, pad = document.getElementById('p96pad').getBoundingClientRect();
          return {W, panel: Math.round(p.width), panelL: Math.round(p.left), card: c ? Math.round(c.width) : null, pad: Math.round(pad.width), hs: document.documentElement.scrollWidth - W, dbSw: body.scrollWidth - body.clientWidth}; }""")
        need = g["W"] - 96 - 2
        check(f"{tag} 2 เต็มจอ: .wlDPanel กว้าง ≥ จอ − 2×48px − 2 ({g['panel']} ≥ {need}) · เริ่มชิดขอบด้านใน", g["panel"] >= need and g["panelL"] <= 48 + 2, g)
        check(f"{tag} 2 เต็มจอ: การ์ดใน .wlDBody กว้างเท่ากัน (≥ {need}) · เดิมปกติแคบกว่า (ปกติ {n0['panel']}px)", g["card"] is not None and g["card"] >= need and g["pad"] >= need and n0["panel"] < g["panel"] - 100, [g, n0])
        pw_ = js(page, """()=>{ const p = document.getElementById('p96p'), cs = getComputedStyle(p), probe = document.createElement('span'); probe.style.cssText = 'position:absolute;visibility:hidden;width:1ch;font:' + cs.font; document.body.appendChild(probe); const ch = probe.getBoundingClientRect().width; probe.remove();
          return {w: p.getBoundingClientRect().width, ch, n: p.getBoundingClientRect().width / ch}; }""")
        check(f"{tag} 2 บรรทัดข้อความ ≤ 80ch (วัด {pw_['n']:.1f}ch · ±2%)", pw_["w"] <= 80 * pw_["ch"] * 1.02, pw_)
        tw = js(page, """()=>{ const t = document.getElementById('p96tw'), r = t.getBoundingClientRect(); return {sw: t.scrollWidth, cw: t.clientWidth, ox: getComputedStyle(t).overflowX, inView: r.right <= innerWidth + 1}; }""")
        check(f"{tag} 2 ตารางกว้างเลื่อนในกล่องของตัวเอง · หน้าไม่ล้น (overflow 0)", tw["sw"] > tw["cw"] + 20 and tw["ox"] in ("auto", "scroll") and tw["inView"] and g["hs"] <= 0 and g["dbSw"] <= 1, [tw, g["hs"], g["dbSw"]])
        us = js(page, """()=>{ const p = document.querySelector('#p96pad p:nth-of-type(2)'), r = p.getBoundingClientRect(); return {right: Math.round(r.right), W: innerWidth, sw: p.scrollWidth, cw: p.clientWidth}; }""")
        check(f"{tag} 2 URL ยาวไม่ดันหน้าล้น", us["right"] <= us["W"] and us["sw"] <= us["cw"] + 1, us)
        if w == 1440: C.shot(page, "ln3fix3c-watch-fullscreen-1440.png", full=False)
        if w == 1280: C.shot(page, "ln3fix3c-watch-fullscreen-1280.png", full=False)
        page.keyboard.press("Escape"); settle(page, 600)
        n1 = js(page, """()=>{ const p = document.querySelector('.wlDPanel'), c = document.querySelector('.wlDBody > *'); return {panel: Math.round(p.getBoundingClientRect().width), card: Math.round(c.getBoundingClientRect().width)}; }""")
        check(f"{tag} 2 ย่อกลับ: ความกว้างมุมมองปกติเท่าเดิม (±2px)", abs(n1["panel"] - n0["panel"]) <= 2 and abs(n1["card"] - n0["card"]) <= 2, [n0, n1])
        check(f"{tag} 2 {label} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ══════════════════════════ §3 Risk Sat
def rect(page, sel):
    return js(page, "(s)=>{ const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return {l: Math.round(r.left), t: Math.round(r.top), r: Math.round(r.right), b: Math.round(r.bottom), w: Math.round(r.width)}; }", sel)


def risksat(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; mac = w >= 1000
    b, page, ce, pe, dl = P81.launch(pw, w, h)
    try:
        P81.put(page, [P81.sat_t("m1", "open", entry=4180, sl=4117, qty=0.10), P81.sat_t("t1", "open", entry=4180, sl=4160, qty=0.10, sleeve="tactical")], "main")
        P81.put(page, [P81.sat_t("f1", "open", entry=4180, sl=4117, qty=0.05)], "fam")
        js(page, "()=>window.scrollTo(0,0)")
        sw = js(page, "()=>({sw: document.querySelectorAll('[data-ln2-accsw],[data-ln2-acc]').length, rows: [...document.querySelectorAll('[data-ln2-row]')].map(e=>e.dataset.ln2Row), boxes: document.querySelectorAll('[data-ln2-box]').length, ls: localStorage.getItem('ln2_acc')})")
        check(f"{tag} 3 Lean: ไม่มีสวิตช์เลือกบัญชี · กล่องเดียว · 2 แถว (main, fam)", sw["sw"] == 0 and sw["rows"] == ["main", "fam"] and sw["boxes"] == 1, sw)
        for acc in ("main", "fam"):
            hh = P81.hd(page, acc); ee = P81.expect(page, acc)
            dd = js(page, "(a)=>{ const d = ddEval(a,'sat'); return d ? fmt2 ? 0 : 0 : 0; }", acc) if False else None
            check(f"{tag} 3 แถว {acc}: ใช้/เพดาน/เหลือ/Main/Tactical ตรงฟังก์ชันเดิม (satV2Risk/satV2Caps) · DD a/b%", all(hh[k] == ee[k] for k in ("used", "cap", "left", "main", "tac")) and hh["used"] != "$0" and hh["ddl"].startswith("DD") and "/20%" in hh["ddl"], [hh, ee])
        # เรียงเคียงกัน / ซ้อนกัน
        r1, r2 = rect(page, '[data-ln2-row="main"]'), rect(page, '[data-ln2-row="fam"]')
        H = js(page, "()=>innerHeight")
        if mac:
            check(f"{tag} 3 Mac: 2 กล่องเคียงข้างกัน (top เท่ากัน) เห็นทั้งคู่โดยไม่ต้องเลื่อน", abs(r1["t"] - r2["t"]) <= 1 and r2["l"] >= r1["r"] - 1 and r1["b"] <= H and r2["b"] <= H and r1["t"] >= 0, [r1, r2, H])
            tt = js(page, "()=>[...document.querySelectorAll('[data-ln2-row] .nm')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
            check(f"{tag} 3 Mac: หัวกล่อง '● ชื่อ · Risk Sat' ต่อบัญชี", all("Risk Sat" in t for t in tt) and len(tt) == 2, tt)
        else:
            check(f"{tag} 3 มือถือ: 2 แถวซ้อนกันในกล่องเดียว (แถว fam อยู่ใต้ main)", r2["t"] >= r1["b"] - 1 and abs(r1["l"] - r2["l"]) <= 1, [r1, r2])
        cl = js(page, """()=>{ const out = []; document.querySelectorAll('[data-ln2-row]').forEach(r => { const v = r.querySelector('.v'), l = r.querySelector('.l'); if(!v || !l) return; const a = v.getBoundingClientRect(), c = l.getBoundingClientRect(), R = r.getBoundingClientRect();
            out.push({acc: r.dataset.ln2Row, sameLine: Math.abs((a.top + a.bottom) / 2 - (c.top + c.bottom) / 2) <= Math.max(a.height, c.height) * 0.8, vClip: v.scrollWidth > v.clientWidth + 1, lClip: l.scrollWidth > l.clientWidth + 1, inside: c.right <= R.right + 1 && a.left >= R.left - 1, rowClip: r.scrollWidth > r.clientWidth + 1}); }); return out; }""")
        check(f"{tag} 3 ตัวเลข '$ใช้ / $เพดาน' กับ 'เหลือ $x' อยู่บรรทัดเดียวกัน ไม่ถูกตัด ไม่ล้นแถว", len(cl) == 2 and all(x["sameLine"] and not x["vClip"] and not x["lClip"] and x["inside"] and not x["rowClip"] for x in cl), cl)
        if w in (300, 390, 1440):
            js(page, "()=>{ const e = document.querySelector('#satV3Sum'); window.scrollTo(0, Math.max(0, e.getBoundingClientRect().top + scrollY - 70)); }")
            C.shot(page, f"ln3fix3c-risksat-{w}.png", full=False)
        # DD link → sheet ของบัญชีนั้น
        js(page, "()=>{ window.__dd = []; const f = window.ddSheetOpen; window.ddSheetOpen = function(a, b){ window.__dd.push([a, b]); }; }")
        page.locator('[data-ln2-row="fam"] [data-ln2-dd]').click(); settle(page, 200)
        page.locator('[data-ln2-row="main"] [data-ln2-dd]').click(); settle(page, 200)
        check(f"{tag} 3 ลิงก์ DD ในแถวบัญชีไหน เปิด ddSheetOpen ของบัญชีนั้น", js(page, "()=>window.__dd") == [["fam", "sat"], ["main", "sat"]], js(page, "()=>window.__dd"))
        # พับรายละเอียด
        det = js(page, "()=>{ const d = document.querySelector('[data-ln2-det]'); d.open = true; return {n: d.querySelectorAll('[data-ln2-detacc]').length, accs: [...d.querySelectorAll('[data-ln2-detacc]')].map(e=>e.dataset.ln2Detacc), txt: d.innerText.replace(/\\s+/g,' '), folds: document.querySelectorAll('[data-ln2-det]').length}; }")
        check(f"{tag} 3 พับเดียว 'รายละเอียดและกฎบัญชี' ลิสต์ทั้ง 2 บัญชีใต้ชื่อบัญชี (เงิน Sat · เพดาน · วิธีนับ)", det["folds"] == 1 and det["accs"] == ["main", "fam"] and "เงิน Sat" in det["txt"] and "วิธีนับ" in det["txt"], det)
        js(page, "()=>{ document.querySelector('[data-ln2-det]').open = false; }")
        # แถบเตือนใต้แถวของบัญชีนั้น
        P81.setcfg(page, maxDd=20, orSat=1.0)
        js(page, "()=>{ const s = getBook('main').settings; s.ddState.sat = %s; saveBook('main'); render(); }" % json.dumps(P81.P37.ds0(45000))); settle(page, 300)
        P81.put(page, [P81.sat_t("o1", "open", entry=4180, sl=4117, qty=0.30)], "main")
        al = js(page, "()=>[...document.querySelectorAll('[data-ln2-alert]')].map(e=>({k: e.dataset.ln2Alert, row: e.closest('[data-ln2-row]').dataset.ln2Row, t: e.innerText.trim()}))")
        h_main = P81.hd(page, "main")
        check(f"{tag} 3 ใกล้เพดาน → '⚠ ใกล้เพดาน: เหลือ $x' อยู่ใต้แถวบัญชีหลักเท่านั้น (แถว fam ไม่มีเตือน)", len(al) == 1 and al[0]["row"] == "main" and al[0]["k"] == "cap" and al[0]["t"] == "⚠ ใกล้เพดาน: เหลือ " + h_main["left"], [al, h_main["left"]])
        ov = js(page, "()=>({main: document.querySelector('[data-ln2-row=main]').classList.contains('over'), fam: document.querySelector('[data-ln2-row=fam]').classList.contains('over'), expMain: satV2Risk('main').sat > satV2Caps('main').sat + 1e-6, expFam: satV2Risk('fam').sat > satV2Caps('fam').sat + 1e-6, box: document.querySelector('[data-ln2-box]').classList.contains('over')})")
        check(f"{tag} 3 สไตล์ over ต่อแถว: แถวไหนเกินเพดาน Sat แถวนั้น over (ตรง satV2Risk > satV2Caps) · อีกแถวไม่ over", ov["main"] == ov["expMain"] and ov["fam"] == ov["expFam"] and ov["box"] == (ov["expMain"] or ov["expFam"]), ov)
        # ฟอร์มแผน: $ ต่อไม้ของทุกบัญชี
        iid = P81.idea(page, sleeve="main", entry=4180, sl=4117); P81.note(page, iid)
        fm = js(page, "()=>{ const e = document.querySelector('[data-ln2-form]'); return e ? {t: e.innerText.replace(/\\s+/g,' ').trim(), deals: [...e.querySelectorAll('[data-ln2-deal-acc]')].map(x=>[x.dataset.ln2DealAcc, x.innerText.trim()]), pct: (e.innerText.match(/(\\d+)%/)||[])[1]} : null; }")
        expd = js(page, "()=>['main','fam'].map(a=>{ const M = satV2Money(a); return [a, satV2Usd(M.mainTHB*M.cfg.rptMain/100, M.fx)]; })")
        check(f"{tag} 3 บรรทัดสถานะฟอร์ม: '2% · <บัญชี> $x · <บัญชี> $y' แสดงทั้ง 2 บัญชี (ตรงสูตรเดิม) · ส่วนอื่นเดิม (ทิศ · Macro · ไม้ใหม่)", fm and fm["deals"] == expd and fm["pct"] == "5" and fm["t"].startswith("▲ Up · Macro") and "ใหม่" in fm["t"], [fm, expd])   # PF1 — ทิศ = Trend ของแผน · มือถือย่อเป็น ใหม่
        if w <= 340:
            dots = js(page, "()=>{ const e = document.querySelector('[data-ln2-form] .ln2-fn'); return {dn: getComputedStyle(e.querySelector('.dn')).display, dd: getComputedStyle(e.querySelector('.dd')).display}; }")
            check(f"{tag} 3 ≤340px: บรรทัดสถานะใช้จุดสีแทนชื่อบัญชี", dots == {"dn": "none", "dd": "inline-block"}, dots)
        check(f"{tag} 3 {label} ไม่ล้นแนวนอน", overflow(page) <= 1, overflow(page))
        # ไม่มีเงิน Sat → ข้อความตั้งค่า
        js(page, "()=>{ const bk = getBook('fam'); bk.settings.capital.satB = 0; bk.settings.pools = {winner:62.5, ladder:37.5, sat:0, reviewed:true}; saveBook('fam');   /* RG2b — ถัง Sat = % ของบัญชี: 'ไม่ตั้งเงิน Sat' = ตั้งสัดส่วน Sat 0% */ render(); satV3Render({force:true}); }"); settle(page, 500)
        nm = js(page, "()=>{ const e = document.querySelector('[data-ln2-row=fam]'); return e ? {t: e.innerText.replace(/\\s+/g,' ').trim(), nomoney: !!e.querySelector('[data-ln2-nomoney]'), link: !!e.querySelector('[data-ln2-setup]'), mainNum: !!document.querySelector('[data-ln2-row=main] [data-ln2-used]')} : null; }")
        check(f"{tag} 3 บัญชีที่ยังไม่ตั้งเงิน Sat → แถวบอก 'ยังไม่ได้ตั้งเงิน Sat — ตั้งค่า' (มีลิงก์) · อีกบัญชียังแสดงตัวเลข", nm and nm["nomoney"] and nm["link"] and "ยังไม่ได้ตั้งเงิน Sat" in nm["t"] and nm["mainNum"], nm)
        # บัญชีเดียว
        js(page, "()=>{ acctList.find(a=>a.id==='fam').ports = ['core']; satV3Render({force:true}); }"); settle(page, 400)
        one = js(page, "()=>({rows: document.querySelectorAll('[data-ln2-row]').length, sw: document.querySelectorAll('[data-ln2-accsw],[data-ln2-acc]').length, box: document.querySelectorAll('[data-ln2-box]').length})")
        check(f"{tag} 3 บัญชี Sat เดียว → 1 แถว/1 กล่อง ไม่มีสวิตช์", one == {"rows": 1, "sw": 0, "box": 1}, one)
        if mac:
            r = rect(page, "[data-ln2-row]"); bx = rect(page, "[data-ln2-box]")
            check(f"{tag} 3 Mac: บัญชีเดียว = กล่องเดียวเต็มความกว้างคอลัมน์", r and bx and r["w"] >= bx["w"] - 2, [r, bx])
        # legacy
        js(page, "()=>ln1SetMode('legacy')"); settle(page, 500)
        lg = js(page, "()=>({ln2: document.querySelectorAll('[data-ln2-hd]').length, pv2: document.querySelectorAll('[data-pv2-header]').length > 0})")
        check(f"{tag} 3 แบบเดิม (legacy) ไม่เปลี่ยน: ไม่มีหัว Lean · มีหัว PV2", lg["ln2"] == 0 and lg["pv2"], lg)
        check(f"{tag} 3 {label} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ══════════════════════════ §4 Risk Core
def riskcore(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; mac = w >= 1000
    b, page, ce, pe = C.launch(pw, w, h)
    try:
        C.go_core(page)
        js(page, "()=>window.scrollTo(0,0)")
        info = js(page, """()=>{ const rows = [...document.querySelectorAll('[data-lf-row]')]; return {ids: rows.map(r=>r.dataset.lfRow), n: rows.length, cap: (document.querySelector('[data-lf-cap]')||{}).innerText, boxes: document.querySelectorAll('[data-lf-riskbox]').length}; }""")
        check(f"{tag} 4 Risk Core: 1 กล่อง · 2 แถว (main, fam) พร้อมกัน · หัว Core = ถัง Winner + Ladder รวม ฿9.6M", info["ids"] == ["main", "fam"] and info["boxes"] == 1 and info["cap"] == "ทุน ฿9.6M", info)   # RG2b — ทุน Core = ถัง Winner + Ladder (80% ของยอดบัญชี ฿12M)
        # ค่าเดียวกับกล่องเดิมของบัญชีนั้น
        for A in ("main", "fam"):
            ref = js(page, """(A)=>{ const rk = coreAcctRisk(A), cx = coreCtx(A), cfg = cx.cfg, sp = cx.split, tank = cx.tankTHB; if(!(tank > 0)) return null;
              return {now: fmt2(rk.layer2Pct)+'%', free: Math.round(sp ? (sp.cashFree + sp.lCashFree) : (tank - cx.held)), ff: Math.round(cx.F.f*100)+'%', dd: fmt2(Math.round(ddEval(A,'winner').ddPct*100)/100)+'%'}; }""", A)
            got = js(page, """(A)=>{ const r = document.querySelector('[data-lf-row="'+A+'"]'); return {now: r.querySelector('[data-lf-now]').innerText.trim(), free: +r.querySelector('[data-lf-free]').dataset.lfFree, line: r.querySelector('[data-lf-line]').innerText.replace(/\\s+/g,' ').trim()}; }""", A)
            check(f"{tag} 4 แถว {A}: Risk ชั้น 2 ตอนนี้ / เพดาน / ว่าง / DD / FF ตรงฟังก์ชันเดิม (coreAcctRisk · coreCtx · ddEval)",
                  ref and got["now"] == ref["now"] and abs(got["free"] - ref["free"]) <= 1 and f"DD {ref['dd']}" in got["line"] and ref["ff"] in got["line"], [ref, got])
        # เตือนใต้แถวของบัญชีนั้น (NVDA ไม่มีราคา อยู่บัญชีหลัก)
        al = js(page, "()=>[...document.querySelectorAll('[data-lf-alert]')].map(e=>({k: e.dataset.lfAlert, row: e.closest('[data-lf-row]').dataset.lfRow}))")
        check(f"{tag} 4 เตือน 'ขาดราคา' อยู่ใต้แถวบัญชีหลัก (ที่มี NVDA) · ไม่มีใต้ Family", any(a["k"] == "missing" and a["row"] == "main" for a in al) and not any(a["row"] == "fam" and a["k"] == "missing" for a in al), al)
        # พับเดียว
        det = js(page, "()=>{ const d = document.querySelector('[data-lf-det]'); d.open = true; return {folds: document.querySelectorAll('[data-lf-det]').length, accs: [...d.querySelectorAll('[data-lf-detacc]')].map(e=>e.dataset.lfDetacc), txt: d.innerText.replace(/\\s+/g,' ')}; }")
        check(f"{tag} 4 พับเดียว 'รายละเอียดและกฎ' ลิสต์ทั้ง 2 บัญชีใต้ชื่อบัญชี (ตำแหน่ง · Ladder · เพดานต่อตัว)", det["folds"] == 1 and det["accs"] == ["main", "fam"] and "เพดานต่อตัว" in det["txt"] and "ตำแหน่ง" in det["txt"], det)
        js(page, "()=>{ document.querySelector('[data-lf-det]').open = false; }")
        # สวิตช์ = เหนือรายการการ์ด
        pos = js(page, """()=>{ const sw = document.querySelector('[data-lf-accsw]'), cards = document.querySelector('[data-lf-cards]'), box = document.querySelector('[data-lf-riskbox]'); if(!sw) return null; const a = sw.getBoundingClientRect(), c = cards.getBoundingClientRect(), r = box.getBoundingClientRect();
          return {gap: Math.round(c.top - a.bottom), belowRisk: a.top >= r.bottom - 1, nextIsCards: sw.nextElementSibling === cards, inRisk: box.contains(sw), labels: [...sw.querySelectorAll('[data-lf-acc]')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())}; }""")
        check(f"{tag} 4 สวิตช์บัญชีย้ายลงมาอยู่เหนือรายการการ์ด (ติดกัน) ไม่อยู่ในกล่อง Risk", pos and pos["nextIsCards"] and pos["belowRisk"] and not pos["inRisk"] and pos["gap"] <= 24, pos)
        n_main = js(page, "()=>document.querySelectorAll('#corePanel .ccCard').length")
        before = js(page, "()=>[...document.querySelectorAll('[data-lf-row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
        lab_main = pos["labels"][0] if pos else ""
        check(f"{tag} 4 ป้ายสวิตช์ '● ชื่อ · n ตัว': n ของบัญชีหลัก = จำนวนการ์ดที่ลิสต์แสดง ({n_main})", pos and lab_main.endswith(f"{n_main} ตัว") and "·" in lab_main, [pos["labels"] if pos else None, n_main])
        page.locator('[data-lf-acc="fam"]').click(); settle(page, 600)
        n_fam = js(page, "()=>document.querySelectorAll('#corePanel .ccCard').length")
        after = js(page, "()=>[...document.querySelectorAll('[data-lf-row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
        lab = js(page, "()=>[...document.querySelectorAll('[data-lf-acc]')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} 4 สลับเป็น Family: เปลี่ยนเฉพาะการ์ด ({n_main}→{n_fam}) · แถว Risk ทั้ง 2 ไม่เปลี่ยน · ป้ายตรงกับจำนวนการ์ด", before == after and n_fam != n_main and lab[1].endswith(f"{n_fam} ตัว") and js(page, "()=>document.querySelector('[data-lf-box]').dataset.lfBox") == "fam", [before, after, lab, n_main, n_fam])
        page.locator('[data-lf-acc="main"]').click(); settle(page, 500)
        # เรียง
        r1, r2 = rect(page, '[data-lf-row="main"]'), rect(page, '[data-lf-row="fam"]')
        if mac:
            check(f"{tag} 4 Mac: 2 กล่อง Risk เคียงข้างกัน (top เท่ากัน) · สวิตช์+การ์ดอยู่ใต้", abs(r1["t"] - r2["t"]) <= 1 and r2["l"] >= r1["r"] - 1 and rect(page, "[data-lf-accsw]")["t"] >= max(r1["b"], r2["b"]) - 1, [r1, r2])
        else:
            check(f"{tag} 4 มือถือ: 2 แถวซ้อนกันในกล่องเดียว", r2["t"] >= r1["b"] - 1 and abs(r1["l"] - r2["l"]) <= 1, [r1, r2])
        cl = js(page, """()=>{ const out = []; document.querySelectorAll('[data-lf-row]').forEach(r => { const v = r.querySelector('.v'), l = r.querySelector('.l'); const a = v.getBoundingClientRect(), c = l.getBoundingClientRect(), R = r.getBoundingClientRect();
            out.push({sameLine: Math.abs((a.top + a.bottom) / 2 - (c.top + c.bottom) / 2) <= Math.max(a.height, c.height) * 0.8, clip: r.scrollWidth > r.clientWidth + 1 || l.scrollWidth > l.clientWidth + 1, inside: c.right <= R.right + 1}); }); return out; }""")
        check(f"{tag} 4 'x% / lim%' กับ 'ว่าง ฿…' อยู่บรรทัดเดียวกัน ไม่ถูกตัด", all(x["sameLine"] and not x["clip"] and x["inside"] for x in cl), cl)
        if w == 390: C.shot(page, "ln3fix3c-riskcore-390.png", full=False)
        if w == 1440: C.shot(page, "ln3fix3c-riskcore-1440.png", full=False)
        check(f"{tag} 4 {label} ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
        js(page, "()=>ln1SetMode('legacy')"); settle(page, 500)
        lg = js(page, "()=>({lf: document.querySelectorAll('[data-lf-box]').length, rows: document.querySelectorAll('[data-lf-row]').length})")
        check(f"{tag} 4 แบบเดิม (legacy): ไม่มีกล่อง Lean ({lg})", lg == {"lf": 0, "rows": 0}, lg)
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px"), (300, 700, "300px")):
            print(f"\n=== {ENGINE} {label} · ＋ Asset ===")
            addasset(pw, w, h, label)
        for w, h in ((1440, 900), (1280, 800)):
            print(f"\n=== {ENGINE} {w}px · Watch เต็มจอ ===")
            watch(pw, w, h, f"{w}px")
        for w, h in ((1440, 900), (1280, 800), (390, 844), (320, 700), (300, 700)):
            print(f"\n=== {ENGINE} {w}px · Risk Sat ===")
            risksat(pw, w, h, f"{w}px")
        for w, h in ((1440, 900), (1280, 800), (390, 844), (300, 700)):
            print(f"\n=== {ENGINE} {w}px · Risk Core ===")
            riskcore(pw, w, h, f"{w}px")
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
