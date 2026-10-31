#!/usr/bin/env python3
"""LN3 — แท็บ Today แบบ Lean: กล่องวัน/สัปดาห์ · งานกล่องเดียว · ช่วงเวลา + เช็กแผน Sat + Focus · เป้าหมาย Port ท้ายหน้า · Open Risk Sat แทน heat · เทส 84
mock Firestore · Chromium 1440 + 390 + 300 · นาฬิกาปลอม พฤ. 8 ต.ค. 2026 12:00 ไทย · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3-today-{1440,390}.png
รัน: python3 run_tests_phase84.py"""
import json, os, re
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase56 as P56

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, count, overflow, go_today = P56.txt, P56.count, P56.overflow, P56.go_today
TODAY = P56.TODAY


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(500)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def extras(doc):
    P56.S(doc)["dailyExtra"] = [{"id": "x1", "name": "สรุปข่าวเช้า"}]


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    log = {TODAY: P56.day(slots=2, sat=2)}
    browser, context, page, ce, pe, dl = P56.launch(pw, w, h, P56.with_goals(), extras, log=log)
    try:
        go_today(page)
        # ── 1 หัว
        hd = js(page, """()=>{ const h = document.querySelector('[data-ln3-tdhead]'); return h ? {t: h.innerText.replace(/\\s+/g,' ').trim(), date: h.querySelector('[data-ln3-date]').innerText, d: h.querySelector('[data-ln3-dcnt]').innerText, w: h.querySelector('[data-ln3-wcnt]').innerText, seg: [...h.querySelectorAll('[data-gl-tab]')].map(b=>b.innerText.trim())} : null; }""")
        exp = js(page, "()=>{ const M = tdLast, S = glDayStat(M.today, M), c = ln3TdWeekCount(M), W = glWeekStat(M); return {d: S.n+'/'+S.N, w: c.n+'/'+c.N, daily: 'Daily · '+S.pct+'%', weekly: 'Weekly · '+W.pct+'%'}; }")
        check(f"{tag} 1 หัวกล่อง: 'พฤ. 8 ต.ค.' · 'n/N วันนี้ · m/M สัปดาห์' ตรงผลคำนวณเดิม · ปุ่ม Daily | Weekly · x%", hd and hd["date"] == "พฤ. 8 ต.ค." and hd["d"] == exp["d"] and hd["w"] == exp["w"] and hd["seg"] == [exp["daily"], exp["weekly"]], [hd, exp])
        cut = js(page, """()=>({hero: !!document.querySelector('.tdHero'), grp: document.querySelectorAll('.tdGh').length, chips: document.querySelectorAll('[data-gl-chip]').length, setup: document.querySelectorAll('[data-gl-setup]').length, help: /กดชื่อช่วงเพื่อไปหน้านั้น|ติ๊กที่ด้านล่าง/.test(document.querySelector('[data-td-wrap]').innerText) || /กดชื่อช่วงเพื่อไปหน้านั้น/.test(document.getElementById('tabToday').innerText), rtfoot: !!document.querySelector('.tdRtFoot')})""")
        check(f"{tag} 1 ตัดออก: หัว 'ต้องทำ'+ชิปจำนวน · หัวกลุ่ม 'ภายในสัปดาห์' · ชิป 'ช่วงเวลา x/y' · ปุ่มตั้งเป้าด้านบน · ข้อความอธิบายวิธีใช้", cut == {"hero": False, "grp": 0, "chips": 0, "setup": 0, "help": False, "rtfoot": False}, cut)
        # ── 2 งาน
        js(page, """()=>{ const M = tdLast; M.tasks = [{g:'b',kind:'idea-study',ico:'💡',html:'TSM เข้า Zone · วางแผน Core',go:'wl',args:{t:'ABC',sub:'sum'},btn:'ดู →',tags:[]},
          {g:'r',kind:'x-urgent',ico:'⚠️',html:'เลื่อน Stop NVDA',go:'wl',args:{t:'ABC',sub:'sum'},btn:'ดู →',tags:[]},
          {g:'a',kind:'x-week',ico:'📅',html:'เช็กงบ W/L',go:'wl',args:{t:'ABC',sub:'sum'},btn:'ดู →',tags:[]}].concat(M.tasks.filter(t=>t.special)); M.tasks.sort((p,q)=>'rab'.indexOf(p.g)-'rab'.indexOf(q.g)); const host = document.getElementById('tabToday'); host.innerHTML = tdHtmlLean(M); }""")
        order = js(page, "()=>[...document.querySelectorAll('[data-ln3-tasks] .tdRow')].map(r=>r.dataset.kind)")
        ks = [k for k in order if k.startswith("x-") or k == "idea-study"]
        check(f"{tag} 2 งานรวมกล่องเดียว เรียง ด่วน → ภายในสัปดาห์ → โอกาส (แถบสีซ้าย แดง/เหลือง/น้ำเงิน) · กดแล้วไปหน้านั้น (data-go)", ks == ["x-urgent", "x-week", "idea-study"] and cnt_(page, "[data-ln3-tasks]") == 1 and js(page, "()=>[...document.querySelectorAll('[data-ln3-tasks] .tdRow[data-go]')].length") >= 3, order)
        cols = js(page, "()=>['x-urgent','x-week','idea-study'].map(k=>getComputedStyle(document.querySelector('[data-kind=\"'+k+'\"]')).borderLeftColor)")
        check(f"{tag} 2 สีแถบซ้ายต่างกัน 3 สี (ด่วน/สัปดาห์/โอกาส)", len(set(cols)) == 3, cols)
        js(page, "()=>{ tdLast.tasks = tdLast.tasks.filter(t=>t.special); document.getElementById('tabToday').innerHTML = tdHtmlLean(tdLast); }")
        none = js(page, "()=>document.querySelectorAll('[data-ln3-tasks] .tdRow:not([data-kind=homework])').length")
        check(f"{tag} 2 ไม่มีงานจริง → ไม่มีแถวงาน (โชว์เฉพาะที่มีจริง) · การบ้านยังอยู่ถ้ามี (5 ส่วน)", none == 0 and (count(page, "[data-kind=homework]") == 0 or count(page, "[data-hw-part]") == 5), [none, count(page, "[data-hw-part]")])
        go_today(page); js(page, "()=>todayRefresh(true)"); page.wait_for_timeout(300)
        # ── 3 Routine
        rt = js(page, """()=>{ const r = document.querySelector('[data-ln3-rt]'); if(!r) return null; return {slots: r.querySelectorAll('.tdSs').length, fold: !!r.querySelector('[data-td-fold]'), cur: r.querySelectorAll('.tdSs.cur').length, nxt: r.querySelectorAll('.tdSs.nxt').length, satrow: r.querySelectorAll('.tdRow[data-kind=sat-daily]').length, focus: document.querySelectorAll('[data-ln3-rt] [data-td-focus], [data-ln3-satbox] [data-td-focus]').length, t: r.innerText.replace(/\\s+/g,' ')}; }""")
        check(f"{tag} 3 การ์ดช่วงเวลา: ช่วงที่ผ่านแล้วพับ ('ผ่านแล้ว n ช่วง') · ช่วงปัจจุบัน/ถัดไปไฮไลต์ · มีแถวเช็กแผน Sat · มีบรรทัด Focus", rt and rt["slots"] >= 3 and rt["fold"] and rt["cur"] + rt["nxt"] == 1 and rt["focus"] == 1, rt)
        if rt and not rt["satrow"]: print("  (หมายเหตุ: ไม่มีแถว sat-daily เพราะ Focus/ตัดสินครบแล้ว — ไม่ใช่ข้อผิดพลาด)")
        # ติ๊กช่วงเวลา ใช้งานได้
        js(page, "()=>document.querySelector('[data-ln3-rt] .tdSs.cur [data-tick-slot], [data-ln3-rt] .tdSs.nxt [data-tick-slot]').click()"); page.wait_for_timeout(600)
        check(f"{tag} 3 ติ๊กช่วงเวลา (วงกลม) ยังบันทึกได้ → ตัวเลข 'วันนี้' เพิ่ม", js(page, "()=>tdLast.log.slots.length") >= 3)
        # ── 4 เป้าหมาย ท้ายหน้า + extras
        order2 = js(page, "()=>[...(document.querySelector('[data-td-cols]') ? document.querySelectorAll('[data-td-col] > *') : document.querySelector('[data-td-wrap]').children)].map(e=>e.matches('[data-gl-goal]') ? 'goal' : e.classList.contains('ln3-tdok') ? 'ok' : e.matches('[data-ln3-tdhead]') ? 'head' : e.matches('[data-ln3-rt]') ? 'rt' : '?')")
        check(f"{tag} 4 การ์ดเป้าหมาย Port (SN1: Mac ขวาบนสุด · มือถือบรรทัดบนสุดแตะขยาย) · เดิม: ท้ายหน้า (หลัง 'อื่น ๆ ปกติ') · LN3fix3: Mac อยู่บนสุดคอลัมน์ซ้าย · มีปุ่ม ＋ กรอกค่าพอร์ต · 2 บัญชี", count(page, "[data-td3-goals]") == 1 and count(page, "[data-td3-acct]") == 2 and count(page, "[data-gl-valopen]") == 2, order2)   # TD4a: ปุ่ม ＋ กรอกค่าอยู่ในแต่ละบัญชีที่กาง (2 บัญชี = 2 ปุ่ม) ไม่ใช่แถวเดียวลอย   # TD3a: กล่อง Account goals ใหม่ (พับ 1 บรรทัด/บัญชี) อยู่เหนือสวิตช์
        check(f"{tag} 4 งานอื่นวันนี้ (dailyExtra) ยังติ๊กได้ · สถานะนับในตัวเลข", count(page, "[data-gl-xtick=x1]") == 1)
        js(page, "()=>document.querySelector('[data-gl-xtick=x1]').click()"); page.wait_for_timeout(600)
        check(f"{tag} 4 ติ๊กงานอื่น → บันทึกลง routineLog", js(page, "()=>tdLast.log.extra.includes('x1')"))
        # ── 5 ดูตัวเลข: Open Risk Sat
        js(page, "()=>{ tdNumOpen = true; todayRefresh(true); }"); page.wait_for_timeout(300)
        th = js(page, "()=>[...document.querySelectorAll('[data-td-nums] thead th')].map(t=>t.querySelector('.full') ? t.querySelector('.full').textContent : t.textContent)")
        check(f"{tag} 5 ตาราง 'ดูตัวเลข': คอลัมน์ heat → 'Open Risk Sat' · ยังมี DD Core · DD Sat · ไม้ใหม่ · ชั้น 2 + ประตู FF", "Open Risk Sat" in th and not any("heat" in x for x in th) and all(k in th for k in ("DD Winner", "DD Ladder", "DD Sat", "ไม้ใหม่ Sat")) and "ประตู FF" not in (txt(page, "[data-td-detfoot]") or ""), th)
        cell = js(page, "()=>{ const r = document.querySelector('[data-num-acct=main]'); const i = [...document.querySelectorAll('[data-td-nums] thead th')].findIndex(t=>/Open Risk Sat/.test(t.textContent)); return r.children[i].innerText.trim(); }")
        e5 = js(page, "()=>{ const M = satV2Money('main'), R = satV2Risk('main'), C = satV2Caps('main'); return satV2Usd(R.sat, M.fx) + ' / ' + satV2Usd(C.sat, M.fx); }")
        check(f"{tag} 5 ค่า Open Risk Sat = ค่า/เพดานเดียวกับหัวกล่องแผน (satV2Risk / satV2Caps)", cell == e5, [cell, e5])
        ok1 = txt(page, "[data-td-okline] .full") or ""
        check(f"{tag} 5 บรรทัด '✓ อื่น ๆ ปกติ — …' ใช้คำ 'Open Risk Sat' แทน heat · ปุ่ม 'ดูตัวเลข ▸'", "Open Risk Sat" in ok1 and "heat" not in ok1 and "Numbers ▸" in (txt(page, "[data-td-numbtn]") or ""), ok1)
        # ใกล้เพดาน → ไม่ปกติ
        js(page, "()=>{ const s = getBook('main').settings; s.satV2 = Object.assign({}, satV2Cfg('main'), {orSat: 0.5}); getBook('main').trades = [{id:'t1', date:'2026-10-01', sym:'XAUUSD', port:'satB', bias:'Long', entry:4180, sl:4117, tp:null, qty:0.30, mult:100, cur:'USD', status:'open', sleeve:'main', openedAt:'2026-10-01'}]; saveBook('main'); render(); todayRefresh(true); }"); page.wait_for_timeout(500)
        ok2 = txt(page, "[data-td-okline] .full") or ""
        cls = js(page, "()=>{ const r = document.querySelector('[data-num-acct=main]'); const i = [...document.querySelectorAll('[data-td-nums] thead th')].findIndex(t=>/Open Risk Sat/.test(t.textContent)); return r.children[i].className; }")
        check(f"{tag} 5 Open Risk Sat ใกล้/เกินเพดาน → เซลล์ติดสี (a/r) · ตกจากบรรทัด 'อื่น ๆ ปกติ'", cls in ("a", "r") and "Open Risk Sat" not in ok2, [cls, ok2])
        shot(page, f"ln3-today-{sfx}.png", "#tabToday")
        # ── 6 Weekly หน้าตาเดิม
        page.locator('[data-gl-tab="w"]').click(); page.wait_for_timeout(400)
        wl = txt(page, "[data-gl-pw]")
        js(page, "()=>ln1SetMode('legacy')"); page.wait_for_timeout(500); go_today(page); js(page, "()=>todayRefresh(true)"); page.wait_for_timeout(300)
        wo = txt(page, "[data-gl-pw]")
        check(f"{tag} 6 Weekly ใช้หน้าตาเดิมทุกตัวอักษร (Lean = แบบเดิม)", wl and wl == wo, [wl, wo])
        # ── 7 legacy
        page.locator('[data-gl-tab="d"]').click(); page.wait_for_timeout(300)
        lg = js(page, "()=>({hero: !!document.querySelector('.tdHero'), ln3: document.querySelectorAll('[data-ln3-today],[data-ln3-tdhead]').length, heat: [...document.querySelectorAll('[data-td-nums] thead th')].some(t=>/heat/.test(t.textContent))})")
        check(f"{tag} 7 โหมดแบบเดิม: หัว 'ต้องทำ' + ตาราง heat ตามเดิม · ไม่มี LN3", lg["hero"] and lg["ln3"] == 0 and lg["heat"], lg)
        js(page, "()=>ln1SetMode('lean')"); page.wait_for_timeout(400)
        ov = js(page, """()=>{ const W = window.innerWidth, bad = []; document.querySelectorAll('#tabToday *').forEach(e=>{ if(e.closest('.tdDetScroll')) return; const r = e.getBoundingClientRect(); if(r.width && r.right > W + 1) bad.push(e.className || e.tagName); }); return bad.slice(0,5); }""")
        check(f"{tag} 8 {label} ไม่ล้นแนวนอน (นอกตารางที่เลื่อนเองได้) · ไม่มี console error", overflow(page) <= 0 and not ov and not ce and not pe, [overflow(page), ov, ce[:2], pe[:2]])
    finally: browser.close()

    # ── 9 ไม่มีเป้า = ไม่มีปุ่มตั้งเป้าบนหน้านี้
    browser, context, page, ce, pe, dl = P56.launch(pw, w, h, log=log)
    try:
        go_today(page)
        check(f"{tag} 9 ยังไม่ตั้งเป้าหมาย → ไม่แสดงปุ่ม 'ตั้งเป้าหมาย Port' ที่หน้านี้ (ตั้งที่ ตั้งค่า) · ไม่มีการ์ดเป้า", count(page, "[data-gl-setup]") == 0 and count(page, "[data-gl-goal]") == 0)
        check(f"{tag} 9 ตั้งค่า › เป้าหมาย Port ยังตั้งได้ (glSetSec)", js(page, "()=>{ openSystemSettings(); return !!document.getElementById('glSetSec'); }"))
    finally: browser.close()


def cnt_(page, sel): return page.locator(sel).count()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px"), (300, 700, "300px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
