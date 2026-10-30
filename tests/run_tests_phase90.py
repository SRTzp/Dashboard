#!/usr/bin/env python3
"""LN3fix §2–4 — แผน Sat: แถวแผน Entry/SL · หลาย Asset (แถบปุ่มมือถือ / 2 คอลัมน์ Mac) · เลือก Asset แล้ว Strategy ตาม · ไม่มีฟอร์ม · วันที่หัวสั้น
 + หน้าตาจอ Mac ≥1000px ทุกแท็บ (2 คอลัมน์ตาม brief §3) + Today งาน heat → Open Risk Sat · เทส 90
mock Firestore · Chromium 1440 + 390 + 300 · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3fix-<tab>-{1440,390}.png (plan · port · today · watch · flow · journal · settings) + ln3fix-plan-noform-1440.png
รัน: python3 run_tests_phase90.py"""
import pf2_retire as RT
import json, os, re
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase77 as P77

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
overflow = C.overflow


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def sat_launch(pw, w, h, picks=("XAUUSD", "BTCUSD", "S50"), plans=True):
    """Sat: XAU ▲ Up · BTC ▼ Down · S50 งด (+ แผน XAU Main · BTC Tactical)"""
    browser, page, ce, pe = P77.launch(pw, w, h)
    js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", list(picks))
    if "BTCUSD" in picks: P11.wk(page, "BTCUSD", "Short", "down")
    if "S50" in picks: js(page, "()=>satwSetBias('S50','None')")
    page.wait_for_timeout(400)
    ids = []
    if plans:
        ids.append(P77.idea(page, asset="XAUUSD", sleeve="main", entry=4180, sl=4117))
        if "BTCUSD" in picks: ids.append(P77.idea(page, asset="BTCUSD", sleeve="tactical", entry=63500, sl=64200))
    js(page, "()=>{ satV3Render({force:true}); }"); page.wait_for_timeout(400)
    return browser, page, ce, pe, ids


def vis_tiles(page):
    return js(page, "()=>[...document.querySelectorAll('#satV3Panel .ln1-tile')].filter(e=>e.getBoundingClientRect().width>0).map(e=>e.dataset.key)")


def shot(page, name, full=True): C.shot(page, name, full=full)


def left(page, sel):
    return js(page, "(s)=>{ const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect(); return r.width>0 ? Math.round(r.left) : null; }", sel)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    mac = w >= 1000
    # ───────── 1 แผน Sat
    b, page, ce, pe, ids = sat_launch(pw, w, h)
    try:
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); page.wait_for_timeout(500)
        rows = js(page, "()=>[...document.querySelectorAll('.ln3-prow')].map(r=>({t: r.querySelector('.ln3-pm').innerText.replace(/\\s+/g,' ').trim(), px: !!r.querySelector('.lf-px'), nowrap: r.querySelector('.lf-px') ? getComputedStyle(r.querySelector('.lf-px')).whiteSpace : null, ek: r.querySelectorAll('.lf-px .ek').length}))")
        check(f"{tag} 1 แถวแผน 'XAUUSD [Main] ▲ Entry 4,180 · SL 4,117' · 'BTC [Tactical] ▼?… Entry 63,500 · SL 64,200' (คำ Entry/SL จาง · ทั้งก้อนไม่ตัดกลาง)", len(rows) == 2 and "Entry 4,180 · SL 4,117" in rows[0]["t"] and rows[0]["t"].startswith("XAUUSD Main") and "Entry 63,500 · SL 64,200" in rows[1]["t"] and all(r["px"] and r["nowrap"] == "nowrap" and r["ek"] == 2 for r in rows), rows)
        wk = js(page, "()=>{ const s = document.getElementById('satV3WeekSel'); return {txt: s.options[s.selectedIndex].text, all: [...s.options].map(o=>o.text)}; }")
        check(f"{tag} 1 ตัวเลือกสัปดาห์แสดงสั้น (เช่น '27 ก.ย.–3 ต.ค.' ไม่มี 'อา./ส.')", re.match(r"^\d{1,2}( [^\s–]+)?–\d{1,2} [^\s–]+$", wk["txt"]) is not None and not any("อา." in t or t.startswith("ส. ") for t in wk["all"]), wk)
        tabs = js(page, "()=>[...document.querySelectorAll('.waBar.lf .waChip')].map(c=>({k: c.dataset.lfAt, t: c.innerText.replace(/\\s+/g,' ').trim(), on: c.classList.contains('on'), off: c.classList.contains('off'), shown: c.getBoundingClientRect().width>0, bs: getComputedStyle(c).borderTopStyle, op: +getComputedStyle(c).opacity}))")
        if not mac:
            check(f"{tag} 1 PF3 มือถือ: แถบปุ่ม Asset มี 3 ปุ่ม ชื่อล้วน (XAUUSD · BTC · S50) ไม่มีลูกศร ▲▼ / งด (ปุ่มเมนู ⋯ เท่านั้นที่ต่อท้ายได้)", len(tabs) == 3 and all(re.fullmatch(r"(☆\s*)?[A-Za-z0-9]+\s*⋯?", t["t"]) for t in tabs) and [t["t"].replace("☆", "").split()[0] for t in tabs] == ["XAUUSD", "BTC", "S50"], [t["t"] for t in tabs])
            check(f"{tag} 1 PF1 — แถบปุ่ม Asset: XAUUSD · BTC · S50 (ไม่มีลูกศร/งด · ไม่จาง) + ＋ Asset", [t["k"] for t in tabs] == ["XAUUSD", "BTCUSD", "S50"] and all(t["shown"] for t in tabs) and all(not t["off"] and t["bs"] == "solid" and "▲" not in t["t"] and "▼" not in t["t"] and "งด" not in t["t"] for t in tabs), tabs)
            check(f"{tag} 1 PF3 ปุ่ม Asset ที่ไม่ได้เลือกสีตัวอักษรเดียวกันทุกปุ่ม (ไม่มีลูกศร ▲ เขียว / ▼ แดง แยกสีตามทิศ)", js(page, "()=>new Set([...document.querySelectorAll('.waBar.lf .waChip:not(.on) .waName')].map(e=>getComputedStyle(e).color)).size") <= 1)
            js(page, "()=>document.querySelector('[data-lf-at=BTCUSD] .waName').click()"); page.wait_for_timeout(400)
            check(f"{tag} 1 มือถือแสดงการ์ดทีละตัว: แตะ BTC → เหลือการ์ด BTC ตัวเดียว · จำตัวที่เลือก (localStorage)", vis_tiles(page) == ["BTCUSD"] and js(page, "()=>localStorage.getItem('lf_sat_asset')") == "BTCUSD", vis_tiles(page))
            js(page, "()=>document.querySelector('[data-lf-at=XAUUSD] .waName').click()"); page.wait_for_timeout(300)
            check(f"{tag} 1 แตะ XAU → การ์ด XAUUSD ตัวเดียว", vis_tiles(page) == ["XAUUSD"], vis_tiles(page))
        else:
            check(f"{tag} 1 Mac: ไม่มีแถบปุ่ม Asset (ไม่แสดงปุ่มต่อ Asset) · การ์ด 2 คอลัมน์ เห็นทุก Asset", not any(t["shown"] for t in tabs) and len(vis_tiles(page)) == 3 and len(set(js(page, "()=>[...document.querySelectorAll('#satV3Panel .ln1-tile')].map(e=>Math.round(e.getBoundingClientRect().left))"))) == 2, [tabs, vis_tiles(page)])
            check(f"{tag} 1 Mac: การ์ด Asset มีลิงก์ 'เอาออกจากสัปดาห์นี้' (ย้ายจาก ⋯ ของแถบที่ซ่อน — ไม่ตัดฟีเจอร์)", js(page, "()=>document.querySelectorAll('[data-lf-remove]').length") == 3)
            gx = js(page, "()=>{ const l = document.getElementById('satV3Sum').getBoundingClientRect(), r = document.querySelector('.lf-sat-r').getBoundingClientRect(); return [Math.round(l.right), Math.round(r.left)]; }")
            check(f"{tag} 1 Mac: ซ้าย Strategy + การ์ด Asset · ขวา แผนเทรด + ฟอร์ม (2 คอลัมน์)", gx[0] <= gx[1] + 2, gx)
        # เลือก Asset แล้ว Strategy ตาม
        sy0 = js(page, "()=>{ window.scrollTo(0, 0); return scrollY; }")
        js(page, "()=>document.querySelector('.ln3-prow[data-lf-asset=BTCUSD]').click()"); page.wait_for_timeout(500)
        st = js(page, "()=>({sel: localStorage.getItem('lf_sat_asset'), rowSel: [...document.querySelectorAll('.ln3-prow.lf-sel')].map(r=>r.dataset.lfAsset), tileSel: [...document.querySelectorAll('.ln1-tile.lf-sel')].map(t=>t.dataset.key), sy: scrollY})")
        check(f"{tag} 1 แตะแถวแผน BTC → Strategy ตาม (" + ("Mac ไฮไลต์กรอบฟ้าที่การ์ด BTC" if mac else "มือถือสลับเป็นการ์ด BTC") + ") · แถวที่เลือกมีแถบฟ้าซ้าย · จอไม่เลื่อน",
              st["sel"] == "BTCUSD" and st["rowSel"] == ["BTCUSD"] and st["tileSel"] == ["BTCUSD"] and st["sy"] == sy0 and (vis_tiles(page) == ["BTCUSD"] if not mac else True), [st, sy0])
        bs = js(page, "()=>getComputedStyle(document.querySelector('.ln3-prow.lf-sel')).boxShadow")
        check(f"{tag} 1 แถวที่เลือกมีแถบฟ้าซ้าย (inset box-shadow สี #2B5BD7)", "rgb(43, 91, 215)" in bs, bs)
        if mac:
            ol = js(page, "()=>getComputedStyle(document.querySelector('.ln1-tile.lf-sel')).boxShadow")
            check(f"{tag} 1 Mac: การ์ด Asset ที่เลือกมีกรอบฟ้า", "rgb(143, 176, 255)" in ol, ol)
        # + แผน ของ Asset
        js(page, "()=>{ ln3Open.clear(); satV3Render({force:true}); }"); page.wait_for_timeout(300)
        js(page, "()=>{ window.scrollTo(0, 0); }")
        sy1 = js(page, "()=>scrollY")
        js(page, "()=>document.querySelector('[data-ln1-plan=XAUUSD]') && document.querySelector('[data-ln1-plan=XAUUSD]').click()")
        if not mac:
            js(page, "()=>document.querySelector('[data-lf-at=XAUUSD] .waName').click()"); page.wait_for_timeout(300)
            js(page, "()=>document.querySelector('[data-ln1-plan=XAUUSD]').click()")
        page.wait_for_timeout(600)
        hd = js(page, "()=>({heads: [...document.querySelectorAll('#satV3Panel .ui-plan')].map(e=>e.innerText.replace(/\\s+/g,' ').trim().slice(0,40)), sel: localStorage.getItem('lf_sat_asset'), sy: scrollY})")
        check(f"{tag} 1 + แผน ของ XAU → การ์ด XAU ตาม · หัวฟอร์ม = ชื่อ Asset นั้น ('XAUUSD · แผนใหม่') · จอไม่เลื่อน", hd["sel"] == "XAUUSD" and any(x.startswith("XAUUSD · แผนใหม่") for x in hd["heads"]) and hd["sy"] == sy1, [hd, sy1])
        # ไม่มีฟอร์มเปิด
        js(page, "()=>{ ln3Open.clear(); satV3Render({force:true}); }"); page.wait_for_timeout(400)
        nf = js(page, "()=>{ const e = document.querySelector('[data-lf-noform]'); const r = e ? e.getBoundingClientRect() : null; return {shown: !!r && r.width>0 && r.height>0, btns: [...document.querySelectorAll('[data-lf-nf]')].map(b=>b.innerText.trim()), forms: document.querySelectorAll('#satV3Panel .ui-plan').length, txt: e ? e.innerText.replace(/\\s+/g,' ') : ''}; }")
        if mac:
            check(f"{tag} 1 ไม่มีฟอร์มเปิด (Mac): การ์ดเล็ก 'ยังไม่ได้เปิดฟอร์มแผน' + ปุ่มลัด '+ แผน <Asset>' ทุก Asset ที่เลือกสัปดาห์นี้", nf["shown"] and nf["forms"] == 0 and "ยังไม่ได้เปิดฟอร์มแผน" in nf["txt"] and nf["btns"] == ["+ แผน XAUUSD", "+ แผน BTC", "+ แผน S50"], nf)
            shot(page, "ln3fix-plan-noform-1440.png", full=False)
            js(page, "()=>document.querySelector('[data-lf-nf=BTCUSD]').click()"); page.wait_for_timeout(600)
            after = js(page, "()=>({heads: [...document.querySelectorAll('#satV3Panel .ui-plan')].map(e=>e.innerText.replace(/\\s+/g,' ').trim().slice(0,30)), sel: localStorage.getItem('lf_sat_asset')})")
            check(f"{tag} 1 ปุ่มลัด '+ แผน BTC' เปิดฟอร์ม BTC · เลือก Asset ตาม", after["sel"] == "BTCUSD" and any(x.startswith("BTC") for x in after["heads"]), after)
        else:
            check(f"{tag} 1 ไม่มีฟอร์มเปิด (มือถือ): เหลือ Strategy + แถวแผนเท่านั้น (ไม่มีการ์ดว่าง/ปุ่มลัด)", not nf["shown"] and nf["forms"] == 0, nf)
        # ไม่ล้น + console
        ov = js(page, "()=>{ const W = innerWidth, bad = []; document.querySelectorAll('#satV3Panel *').forEach(e=>{ if(e.closest('.waBar, table, pre')) return; const r = e.getBoundingClientRect(); if(r.width>0 && r.right > W + 1) bad.push(e.className||e.tagName); }); return bad.slice(0,5); }")
        check(f"{tag} 1 {label} หน้าแผน Sat ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ov and not ce and not pe, [overflow(page), ov, ce[:2], pe[:2]])
        js(page, "()=>{ ln3Open.clear(); lfSatSet('XAUUSD'); satV3Render({force:true}); }"); page.wait_for_timeout(300)
        if w in (1440, 390): shot(page, f"ln3fix-plan-{sfx}.png")
    finally: b.close()

    # ───────── 1b ยังไม่ตั้ง
    b, page, ce, pe, ids = sat_launch(pw, w, h, picks=("XAUUSD", "BRENT"), plans=False)
    try:
        js(page, "()=>satwWrite('BRENT', {bias: null, trend_dir: null})"); page.wait_for_timeout(400)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); page.wait_for_timeout(500)
        t = js(page, "()=>[...document.querySelectorAll('.waBar.lf .waChip')].map(c=>({t: c.innerText.replace(/\\s+/g,' ').trim(), off: c.classList.contains('off')}))")
        check(f"{tag} 1 PF3 ชิป Asset ที่เลือก 2 ตัว (XAU · Brent): Brent (Strategy ไม่มี Trend) แสดงชื่อปกติ ไม่จาง ไม่มีป้าย ยังไม่ตั้ง", len(t) == 2 and any("BRENT" in x["t"].upper() for x in t) and all(not x["off"] for x in t), t)
        check(f"{tag} 1 PF1 — ชิป Asset ไม่มีลูกศร/คำว่า ยังไม่ตั้ง/งด · ไม่จาง", all(not x["off"] and "ยังไม่ตั้ง" not in x["t"] and "▲" not in x["t"] and "▼" not in x["t"] for x in t), t)
        add = js(page, "()=>{ const e = document.querySelector('[data-wa-add]'); if(!e) return null; const r = e.getBoundingClientRect(); return {shown: r.width>0, t: e.innerText.trim()}; }")
        check(f"{tag} 1 '＋ Asset' ยังอยู่ (เลือกไม่ครบโควตา) ทั้งมือถือและ Mac", add is not None and add["shown"] and "Asset" in add["t"], add)
    finally: b.close()

    # ───────── 2 หน้าตาจอ Mac ทุกแท็บ
    b, page, ce, pe = C.launch(pw, w, h)
    try:
        def go(tab):
            js(page, "(t)=>switchTab(t)", tab); page.wait_for_timeout(1300)
        if mac:
            go("mix")
            x = js(page, "()=>{ const q = s => { const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top)]; }; return {struct: q('[data-ln3-struct]'), core: q('[data-ln3-core]'), sat: q('[data-ln3-sat]'), sum: q('[data-ln3-sum]'), seg: q('.ln3-pseg')}; }")
            check(f"{tag} 2 Port (Mac): ซ้าย โครงพอร์ต + Sat · ขวา Core Port · สรุปบนสุดเต็มกว้าง · Sat ใต้โครงพอร์ต คอลัมน์เดียวกัน", x["struct"] and x["core"] and x["sat"] and x["struct"][0] < x["core"][0] and x["sat"][0] == x["struct"][0] and x["sat"][2] > x["struct"][2] and x["sum"][1] - x["sum"][0] > 1000 and x["seg"][1] - x["seg"][0] <= 430, x)
            shot(page, f"ln3fix-port-{sfx}.png")
            go("today")
            RT.retired_td3a(f"{tag} 2 Today (Mac) SN1: ซ้ายช่วงเวลา · ขวาเป้าหมาย Port → … → อื่น ๆ ปกติ — ดู TD3a_retired.md")
            x = js(page, RT.PANELS_JS)
            check(f"{tag} 2 Today (Mac): TD3a 3 panels ชิดบนเท่ากัน · ไม่ล้นแนวนอน", RT.panels_ok(x), x)
            shot(page, f"ln3fix-today-{sfx}.png")
            go("watch")
            x = js(page, "()=>{ const l = document.querySelector('.wlList').getBoundingClientRect(), d = document.querySelector('.wlDet').getBoundingClientRect(); return [Math.round(l.right), Math.round(d.left), Math.round(l.width), Math.round(d.width)]; }")
            check(f"{tag} 2 Watch (Mac): ซ้าย ลิสต์ + Candidate · ขวา รายละเอียดหุ้น (กว้างกว่า)", x[0] <= x[1] + 2 and x[3] > x[2], x)
            shot(page, f"ln3fix-watch-{sfx}.png")
            go("flow")
            x = js(page, "()=>{ const q = s => { const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top)]; }; return {hero: q('#ffAction'), pb: q('#pbPanel'), reg: q('#ffRegime'), cal: q('#ffCal'), rrg: q('#ffThemesPanel'), body: document.getElementById('ffThemesBody').offsetParent !== null, boards: q('#ffManualBoards')}; }")
            check(f"{tag} 2 Flow (Mac): ซ้าย Macro · Regime · ข่าว · บอร์ด · ขวา RRG (กางเป็นค่าเริ่มต้น) · การ์ดสรุปบนสุดเต็มกว้าง", x["pb"][0] == x["reg"][0] == x["cal"][0] == x["boards"][0] and x["rrg"][0] > x["pb"][0] and x["body"] and x["hero"][1] - x["hero"][0] > 1000, x)
            js(page, "()=>ffToggleThemes()"); page.wait_for_timeout(300)
            col = js(page, "()=>document.getElementById('ffThemesBody').offsetParent === null")
            js(page, "()=>ffToggleThemes()"); page.wait_for_timeout(300)
            check(f"{tag} 2 Flow (Mac): กดหุบ RRG ได้ (ผู้ใช้กดเอง = จำตามที่กด)", col and js(page, "()=>document.getElementById('ffThemesBody').offsetParent !== null"), col)
            shot(page, f"ln3fix-flow-{sfx}.png")
            go("journal")
            x = js(page, "()=>{ const q = s => { const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top)]; }; return {sum: q('#jSum'), closed: q('#closedPanel'), setup: q('#setupPanel'), cond: q('#condPanel'), table: !!document.querySelector('#closedPanel table') && document.querySelector('#closedPanel .tablewrap').getBoundingClientRect().width > 400}; }")
            check(f"{tag} 2 Journal (Mac): ซ้าย กล่องสรุป + Setup/เงื่อนไข · ขวา Closed Trades เป็นตาราง", x["sum"][0] == x["setup"][0] == x["cond"][0] and x["closed"][0] > x["sum"][0] and x["table"] and x["setup"][2] > x["sum"][2], x)
            shot(page, f"ln3fix-journal-{sfx}.png")
            js(page, "()=>openSettings()"); page.wait_for_timeout(1300)
            print("RETIRED - [p90] ตั้งค่า (Mac) 4 เช็ก: ซ้ายรายชื่อหมวด/ทีละหมวด/เริ่มพับ/กางทุกหมวดไม่ทับ — เลย์เอาต์กลุ่ม LN3 ถูกแทนด้วย 5 การ์ด SET1 (ดู tests/SET1_retired.md · phase110 ตรวจเลย์เอาต์ใหม่)")
            shot(page, f"ln3fix-settings-{sfx}.png", full=False)
            js(page, "()=>document.getElementById('setOverlay').classList.remove('show')")
            wd = js(page, "()=>{ const c = document.querySelector('.wrap'); return Math.round(c.getBoundingClientRect().width); }")
            check(f"{tag} 2 ความกว้างเนื้อหาสูงสุด ~1280px (Mac 1440)", wd <= 1280, wd)
        else:
            for tab, nm in (("mix", "port"), ("today", "today"), ("watch", "watch"), ("flow", "flow"), ("journal", "journal")):
                go(tab)
                if w == 390: shot(page, f"ln3fix-{nm}-390.png")
            js(page, "()=>openSettings()"); page.wait_for_timeout(1000)
            if w == 390: shot(page, "ln3fix-settings-390.png", full=False)
            ls = js(page, "()=>({grid: getComputedStyle(document.querySelector('#setOverlay .modal')).display, w: document.querySelector('#setOverlay .modal').getBoundingClientRect().width})")
            check(f"{tag} 2 มือถือ: หน้าต่างตั้งค่าเป็นคอลัมน์เดียวเหมือน LN3 (ไม่เป็น grid 2 คอลัมน์)", ls["grid"] != "grid", ls)
            js(page, "()=>document.getElementById('setOverlay').classList.remove('show')")
            for tab, sel in (("mix", "#mixBody"), ("flow", "#tabFlow"), ("journal", "#tabJournal")):
                go(tab)
                d = js(page, "(s)=>getComputedStyle(document.querySelector(s)).display", sel)
                check(f"{tag} 2 มือถือ {tab}: เรียงคอลัมน์เดียวเหมือน LN3 (ไม่เป็น grid)", d != "grid", d)
        # ไม่ล้นทุกแท็บ
        bad = {}
        for tab in ("plan", "mix", "today", "watch", "flow", "journal"):
            go(tab); o = overflow(page)
            if o > 0: bad[tab] = o
        check(f"{tag} 2 {label} ทุกแท็บไม่ล้นแนวนอน · ไม่มี console error", not bad and not ce and not pe, [bad, ce[:2], pe[:2]])
    finally: b.close()

    # ───────── 3 Today: งาน heat → Open Risk Sat
    b, page, ce, pe, ids = sat_launch(pw, w, h, plans=False)
    try:
        js(page, """()=>{ const R0 = satV2Risk, C0 = satV2Caps;
          window.satV2Risk = (id)=>Object.assign({}, R0(id), {sat: 1500*40, main: 1000*40, tac: 500*40});
          window.satV2Caps = (id)=>Object.assign({}, C0(id), {sat: 1800*40}); }""")
        js(page, "()=>{ todayRefresh(true); }"); page.wait_for_timeout(400)
        t = js(page, "()=>tdLast.tasks.filter(x=>x.kind==='heat').map(x=>x.html.replace(/<[^>]+>/g,''))")
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); satV3Render({force:true}); }"); page.wait_for_timeout(500)
        hdr = js(page, "()=>({used: document.querySelector('[data-ln2-used]').innerText.trim(), cap: document.querySelector('[data-ln2-cap]').innerText.trim(), left: document.querySelector('[data-ln2-left]').innerText.trim()})")
        check(f"{tag} 3 Today งาน heat → 'Open Risk Sat <บัญชี> $x/$cap · เหลือ $y' (ข้อความ/ค่าเดียวกับหัวกล่องแผน · ไม่มีคำ 'heat Sat')",
              len(t) >= 1 and all(x.startswith("Open Risk Sat") and "heat" not in x.lower() and hdr["used"] in x and hdr["cap"] in x and hdr["left"] in x for x in t), [t, hdr])
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        vis = js(page, "()=>document.querySelector('[data-ln3-today]').innerText.includes('Open Risk Sat') && !/heat Sat/.test(document.querySelector('[data-ln3-today]').innerText)")
        check(f"{tag} 3 หน้า Today แสดงงานนี้เป็น 'Open Risk Sat' (ไม่มี 'heat Sat')", vis)
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
