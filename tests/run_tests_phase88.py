#!/usr/bin/env python3
"""LN3 — ตั้งค่าแบบ Lean: 15 หมวด → 6 หมวด · ทุกค่าเดิมยังแก้/บันทึกได้ · ขั้นสูงมีครบ · สวิตช์หน้าตาเปลี่ยนทุกแท็บ · เทส 88
mock Firestore · Chromium 1440 + 390 + 300 · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3-settings-{closed,sat}-{1440,390}.png
รัน: python3 run_tests_phase88.py"""
import json, os, re
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase77 as P77

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
overflow = P54.overflow
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-LN3.html"))


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


def orig_ids():
    """ทุก id ของช่อง input/select/textarea ในหน้าต่างตั้งค่าเดิมทั้งสองใบ (อ่านจาก index.backup-pre-LN3.html)"""
    src = open(BACKUP, encoding="utf-8").read()
    ids = []
    for ov in ("setOverlay", "sysOverlay"):
        a = src.index(f'<div class="overlay" id="{ov}">')
        b = src.index("<!-- =====", a + 10) if "<!-- =====" in src[a + 10:] else len(src)
        blk = src[a:b]
        for m in re.finditer(r"<(input|select|textarea)\b[^>]*?\bid=\"([A-Za-z0-9_]+)\"", blk):
            ids.append(m.group(2))
    return sorted(set(ids))


def launch(pw, w, h):
    def mut(doc):
        P77.fixture()(doc)
        doc["books"]["fam"]["settings"]["capital"]["core"] = 1234567
    browser, context, page, ce, pe, dl = P54.launch(pw, w, h, mut)
    P51.fresh(page, None)
    return browser, page, ce, pe


def vals(page, ids):
    return js(page, "(ids)=>Object.fromEntries(ids.map(i=>{ const e = document.getElementById(i); return [i, e ? (e.type==='checkbox' ? String(e.checked) : e.value) : '__MISSING__']; }))", ids)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    IDS = orig_ids()
    # ── ค่าเดิมของแบบเดิม (อ้างอิง)
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>ln1SetMode('legacy')"); page.wait_for_timeout(300)
        js(page, "()=>{ openSettings(); openSystemSettings(); }"); page.wait_for_timeout(500)
        ref = vals(page, IDS)
        legacy_vis = js(page, "()=>({secs: [...document.querySelectorAll('#setOverlay .setsec, #sysOverlay .setsec')].filter(e=>e.offsetParent !== null || e.parentElement.offsetParent !== null).length, ln3: document.querySelectorAll('#ln3SetHost').length})")
    finally: b.close()

    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>openSettings()"); page.wait_for_timeout(500)
        # ── 1 6 หมวด
        g = js(page, """()=>({gs: [...document.querySelectorAll('#ln3SetHost > .ln3-g')].map(d=>({k: d.dataset.ln3G, t: d.querySelector('.t').innerText.trim(), s: d.querySelector('small').innerText.trim(), open: d.open})),
          shells: [...document.querySelectorAll('#setOverlay .setsec')].filter(e=>!e.closest('.ln3-g') && getComputedStyle(e).display !== 'none').length,
          shown: document.getElementById('setOverlay').classList.contains('show'), sys: document.getElementById('sysOverlay').classList.contains('show'),
          jump: [...document.querySelectorAll('#setOverlay .setjump')].filter(b=>getComputedStyle(b).display !== 'none').map(b=>b.textContent.replace(/\\s+/g,' ').slice(0,30))})""")
        check(f"{tag} 1 6 หมวด: บัญชี&เงินต้น · Core · Sat Main/Tactical · กิจวัตร&ข่าว · หน้าจอ · ข้อมูล&การเชื่อมต่อ (หน้าต่างเดียว · ไม่มีหมวดเดิมค้าง)", [x["k"] for x in g["gs"]] == ["acct", "core", "sat", "routine", "screen", "data"] and g["shells"] == 0 and g["shown"] and g["sys"] is False, g)
        check(f"{tag} 1 หัวหมวดสรุปค่าหลัก (ไม่ต้องกางก็เห็น): 'Core ฿4.2M · Sat $45k · fx …' · 'Base x% (ไม้แรก y) · เร่ง z% · ต่อหุ้น ≤ w%' · '70:30 · RPT 2/2%' · 'หน้าตา Lean'", g["gs"][0]["s"].startswith("Core ฿4.2M · Sat $45k · fx") and g["gs"][1]["s"].startswith("Base ") and "ต่อหุ้น ≤" in g["gs"][1]["s"] and g["gs"][2]["s"] == "70:30 · RPT 2/2%" and g["gs"][4]["s"] == "หน้าตา Lean" and all(not x["open"] for x in g["gs"]), [x["s"] for x in g["gs"]])
        check(f"{tag} 1 ปุ่มลัด 'ตั้งค่าระบบ' / 'Port & Risk' เดิมถูกซ่อน (ไม่มีสองหน้าต่างแล้ว) · เหลือ 'จัดการ Industry' ในหมวดข้อมูล", all("Industry" in x for x in g["jump"]) and len(g["jump"]) <= 1, g["jump"])
        # ── 2 ทุก id เดิมอยู่ครบ + ค่าเท่ากับแบบเดิม
        cur = vals(page, IDS)
        missing = [k for k, v in cur.items() if v == "__MISSING__"]
        inside = js(page, "(ids)=>ids.filter(i=>{ const e = document.getElementById(i); return e && !e.closest('#setOverlay'); })", IDS)
        check(f"{tag} 2 ช่องกรอกเดิมทุกช่อง ({len(IDS)} ช่อง) ยังอยู่ครบ และอยู่ในหน้าต่างเดียว (#setOverlay)", not missing and not inside, [missing, inside])
        # LN3fix2 §1.5 — เพดานเงินต่อหุ้น (capTotal) ช่องที่ยังไม่เคยตั้ง: Lean ค่าเริ่ม 15 · แบบเดิม 25 (ค่าที่บันทึกไว้ไม่เปลี่ยน) — เป็นข้อยกเว้นเดียวที่อนุญาต
        NEWDEF = {"sCrCapTotA": ["25", "15"], "sCrCapTotB": ["25", "15"]}
        diff = {k: [ref[k], cur[k]] for k in IDS if ref.get(k) != cur.get(k) and NEWDEF.get(k) != [ref.get(k), cur.get(k)]}
        check(f"{tag} 2 ค่าที่โหลดมาเท่ากับแบบเดิมทุกช่อง (ย้ายหมวดเท่านั้น ไม่เปลี่ยนค่า)", not diff, diff)
        # ── 3 จัดวาง
        lay = js(page, """()=>{ const y = id => Math.round(document.getElementById(id).closest('.f').getBoundingClientRect().top); const grp = id => document.getElementById(id).closest('[data-ln3-g]').dataset.ln3G;
          document.querySelectorAll('#ln3SetHost > .ln3-g').forEach(d=>d.open = true);
          const adv = k => [...document.querySelectorAll('[data-ln3-adv="'+k+'"] .f input, [data-ln3-adv="'+k+'"] .f textarea')].map(e=>e.id);
          return {pairMT: y('sV2Main') === y('sV2Tac'), pairRpt: y('sV2RptMain') === y('sV2RptTac'), triple: y('sV2OrSat') === y('sV2OrAsset') && y('sV2OrAsset') === y('sV2OrTot'), pairBrk: y('sV2BrkN') === y('sV2BrkDd'),
            groups: {sCore: grp('sCore'), sFx: grp('sFx'), sCrL2Cap: grp('sCrL2Cap'), sCrTierRoic: grp('sCrTierRoic'), sV2Main: grp('sV2Main'), sSatRpt: grp('sSatRpt'), tdRtSet: grp('tdRtSet'), newsSet: grp('newsSet'), ideaGroupMinIn: grp('ideaGroupMinIn'), sizeWl: grp('sizeWl'), tabsOffset: grp('tabsOffset'), ln1: grp('ln1ModeLean'), sTdKey: grp('sTdKey'), bk: grp('bkSummary'), acctMgr: grp('acctMgr'), glSet: grp('glSet')},
            satadv: adv('satadv'), dd: adv('dd'), tier: adv('tier'), ddPauseHidden: getComputedStyle(document.getElementById('sSatDdPause').closest('.f')).display}; }""")
        check(f"{tag} 3 ช่องคู่แถวเดียว 2 ช่อง: สัดส่วน Main/Tactical · RPT M/T · เบรก Tactical · เพดาน Open Risk 3 ช่องแถวเดียว", lay["pairMT"] and lay["pairRpt"] and lay["pairBrk"] and (lay["triple"] or w <= 360), lay)   # ≤ 360px: 3 ช่องตัดเป็น 2 คอลัมน์โดยออกแบบ
        gp = lay["groups"]
        check(f"{tag} 3 ช่องอยู่หมวดถูกต้อง: เงินต้น/fx → 1 · ชั้น 2/Tier → 2 · Sat → 3 · Daily/ข่าว/Ideas → 4 · ฟอนต์/แท็บ/สวิตช์หน้าตา → 5 · API key/สำรอง → 6 · จัดการบัญชี/เป้าหมาย → 1",
              gp["sCore"] == "acct" and gp["sFx"] == "acct" and gp["acctMgr"] == "acct" and gp["glSet"] == "acct" and gp["sCrL2Cap"] == "core" and gp["sCrTierRoic"] == "core" and gp["sV2Main"] == "sat" and gp["sSatRpt"] == "sat" and gp["tdRtSet"] == "routine" and gp["newsSet"] == "routine" and gp["ideaGroupMinIn"] == "routine" and gp["sizeWl"] == "screen" and gp["tabsOffset"] == "screen" and gp["ln1"] == "screen" and gp["sTdKey"] == "data" and gp["bk"] == "data", gp)
        need = ["sPortSatB", "sV2CapMain", "sV2CapTac", "sV2Tp1R", "sV2Tp1Pct", "sV2Tp2R", "sSatMacroNeutral", "sSatRpt", "sSatRptHi", "sV2TfMain", "sV2TfTac"]
        check(f"{tag} 3 'ขั้นสูง ▸' ใน Sat มีครบ: Max Heat Sat · เพดานมูลค่า M/T · TP Tactical · Macro Neutral · RPT เดิม · TF ค่าเริ่ม", sorted(lay["satadv"]) == sorted(need), lay["satadv"])
        check(f"{tag} 3 Max DD Sat ช่องเดียว (ช่อง 'พักเมื่อ DD' เดิมซ่อน · ยังซิงก์) · ลดขนาด/พักนาน/ฟื้นจบ อยู่ในพับ · เกณฑ์ Tier อยู่ในพับของ Core", lay["ddPauseHidden"] == "none" and sorted(lay["dd"]) == sorted(["sSatDdReduce", "sSatDdRecoverR", "sSatDdWeeks"]) and len(lay["tier"]) == 6, [lay["ddPauseHidden"], lay["dd"], lay["tier"]])
        hint = js(page, "()=>({m: (document.querySelector('[data-v2-hint=sV2Main]')||{}).innerText, r: (document.querySelector('[data-v2-hint=sV2RptMain]')||{}).innerText})")
        check(f"{tag} 3 ข้างช่องยังบอก '= x% ของพอร์ตรวม' เหมือนเดิม", hint["m"] == "= 21% ของพอร์ตรวม" and hint["r"] == "= 0.42% ของพอร์ตรวม", hint)
        shot(page, f"ln3-settings-sat-{sfx}.png", "#setOverlay .modal")
        # ── 4 แก้ + บันทึก
        js(page, """()=>{ const set = (id, v) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input', {bubbles:true})); e.dispatchEvent(new Event('change', {bubbles:true})); };
          set('sCore', '4300000'); set('sV2Main', '60'); set('sV2Tac', '40'); set('sV2OrSat', '1.5'); set('sSatMacroAgainst', '1'); set('sCrL2Cap', '18'); set('sCrL2Warn', '14');
          set('sTdKey', 'KEYTEST'); set('sizeWl', '0.9'); set('tabsOffset', '3'); set('sV2Tp1R', '2.5'); set('sSatRpt', '0.9'); set('sPortSatB', '5'); set('sV2MaxDd', '15'); set('sV2CapMain', '3'); }""")
        page.wait_for_timeout(300)
        sync = js(page, "()=>document.getElementById('sSatDdPause').value")
        sm = js(page, "()=>[...document.querySelectorAll('#ln3SetHost small[data-ln3-gsum]')].map(e=>e.innerText)")
        check(f"{tag} 4 แก้แล้วหัวหมวดสรุปค่าใหม่ทันที ('Core ฿4.3M' · '60:40') · Max DD Sat ซิงก์กับช่อง 'พักเมื่อ DD' เดิม (15)", sm[0].startswith("Core ฿4.3M") and sm[2].startswith("60:40") and sync == "15", [sm, sync])
        err = js(page, "()=>document.querySelector('[data-ln3-save]').disabled")
        page.locator("[data-ln3-save]").click(); page.wait_for_timeout(700)
        st = js(page, """()=>{ const s = state.settings; return {core: s.capital.core, main: s.satV2 && s.satV2.mainPct, tac: s.satV2 && s.satV2.tacPct, orSat: s.satV2 && s.satV2.orSat, against: s.satRisk && s.satRisk.macroAgainst, l2: s.coreRisk && s.coreRisk.l2Cap, warn: s.coreRisk && s.coreRisk.l2Warn,
          td: s.tdKey, font: state.fontSizes && state.fontSizes.wl, tabs: state.tabsOffset, tp1: s.satV2 && s.satV2.tp1R, rpt: s.satRisk && s.satRisk.rpt, heat: s.limits.port.satB, dd: s.satRisk && s.satRisk.ddPause, v2dd: s.satV2 && s.satV2.maxDd, cap: s.satV2 && s.satV2.capMain}; }""")
        exp = {"core": 4300000, "main": 60, "tac": 40, "orSat": 1.5, "against": 1, "l2": 18, "warn": 14, "td": "KEYTEST", "font": 0.9, "tabs": 3, "tp1": 2.5, "rpt": 0.9, "heat": 5, "dd": 15, "v2dd": 15, "cap": 3}
        check(f"{tag} 4 กด 'บันทึก' ครั้งเดียว → ทุกค่าที่แก้ (เงินต้น · สัดส่วน · เพดาน Open Risk · Macro · ชั้น 2 · API key · ฟอนต์ · แท็บ · ขั้นสูง: TP1/RPT เดิม/Max Heat Sat/เพดานมูลค่า · Max DD) ถูกบันทึกถูกที่ · หน้าต่างปิด", st == exp and not js(page, "()=>document.getElementById('setOverlay').classList.contains('show')"), [st, exp])
        # ── 5 ค่าผิด = ไม่บันทึกต่อ
        js(page, "()=>openSettings()"); page.wait_for_timeout(400)
        js(page, "()=>{ const e = document.getElementById('sV2Main'); e.value = '90'; e.dispatchEvent(new Event('input', {bubbles:true})); }"); page.wait_for_timeout(200)
        page.locator("[data-ln3-save]").click(); page.wait_for_timeout(400)
        check(f"{tag} 5 สัดส่วน Main+Tactical ≠ 100 → ไม่บันทึก · หน้าต่างยังเปิด · ค่าในระบบเดิมไม่เปลี่ยน", js(page, "()=>document.getElementById('setOverlay').classList.contains('show')") and js(page, "()=>state.settings.satV2.mainPct") == 60)
        js(page, "()=>document.getElementById('setOverlay').classList.remove('show')")
        # ── 6 บัญชี
        js(page, "()=>openSettings()"); page.wait_for_timeout(400)
        seg = js(page, "()=>[...document.querySelectorAll('[data-ln3-sacct]')].map(b=>[b.innerText.trim(), b.classList.contains('on')])")
        page.locator('[data-ln3-sacct="fam"]').click(); page.wait_for_timeout(900)
        check(f"{tag} 6 ปุ่มเลือกบัญชีบนสุด (2 บัญชี) · เลือก Family → โหลดค่าของ Family (ทุนเงินต้น 1,234,567) · ตั้งต่อบัญชีเหมือนเดิม", len(seg) == 2 and js(page, "()=>acctActive") == "fam" and js(page, "()=>document.getElementById('sCore').value") == "1234567", [seg, js(page, "()=>document.getElementById('sCore').value")])
        js(page, "()=>document.getElementById('setOverlay').classList.remove('show')")
        # ── 7 หมวดระบบ: glGoSettings เปิดหมวดแม่ + หัวข้อย่อย
        js(page, "()=>glGoSettings()"); page.wait_for_timeout(500)
        check(f"{tag} 7 ลิงก์ 'ตั้งเป้าหมาย' (glGoSettings) เปิดหมวดบัญชี & เงินต้น + หัวข้อ 'เป้าหมาย Port' อัตโนมัติ", js(page, "()=>document.querySelector('[data-ln3-g=acct]').open && document.getElementById('glSetSec').open && document.getElementById('setOverlay').classList.contains('show')"))
        check(f"{tag} 7 จัดการบัญชี / เป้าหมาย / Daily routine / ข่าว / Ideas / สำรองข้อมูล ยังมีเนื้อหาของเดิม", js(page, "()=>['acctMgr','glSet','tdRtSet','newsSet','bkSummary'].every(i=>{ const e = document.getElementById(i); return e && e.innerHTML.length > 0 || i==='bkSummary'; }) && !!document.querySelector('[onclick*=exportBackupNow]') && !!document.querySelector('[onclick*=acctAdd]')"))
        # ── 8 สวิตช์หน้าตาเปลี่ยนทุกแท็บ
        js(page, "()=>{ document.querySelector('[data-ln3-g=screen]').open = true; }")
        page.locator("#ln1ModeLegacy").check(); page.wait_for_timeout(700)
        tabs = js(page, """()=>{ switchTab('mix'); const mix = {stats: document.querySelectorAll('#mixSummary .stat').length, ln3: document.querySelectorAll('[data-ln3-sum]').length};
          switchTab('today'); todayRefresh(true); const today = {hero: !!document.querySelector('.tdHero'), ln3: document.querySelectorAll('[data-ln3-today]').length};
          switchTab('journal'); renderJournal(); const jr = {ln3: document.querySelectorAll('[data-ln3-jbox]').length, cells: document.querySelectorAll('#jSum .sumCell').length};
          switchTab('flow'); renderFundflow(); const fl = {grid: document.querySelectorAll('#ffAction .ffActCell').length, ln3: document.querySelectorAll('[data-ln3-fhero]').length};
          switchTab('watch'); renderWatchlist(); const wl = {ln3: document.querySelectorAll('[data-ln3-wl2]').length};
          return {mix, today, jr, fl, wl, secs: !!document.querySelector('#ln3SetHost'), mode: ln1Mode()}; }""")
        check(f"{tag} 8 สลับเป็น 'แบบเดิม' ในตั้งค่า → ทุกแท็บ (Port · Today · Journal · Flow · Watch) กลับหน้าตาเดิม · หน้าต่างตั้งค่ากลับเป็นแบบ 2 หน้าต่างเดิม", tabs["mode"] == "legacy" and tabs["mix"] == {"stats": 4, "ln3": 0} and tabs["today"]["hero"] and tabs["today"]["ln3"] == 0 and tabs["jr"]["ln3"] == 0 and tabs["jr"]["cells"] == 6 and tabs["fl"]["grid"] == 4 and tabs["fl"]["ln3"] == 0 and tabs["wl"]["ln3"] == 0 and tabs["secs"] is False, tabs)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); openSettings(); }"); page.wait_for_timeout(400)
        lg = js(page, "()=>({secs: [...document.querySelectorAll('#setOverlay .setsec')].filter(e=>getComputedStyle(e).display !== 'none').length, host: !!document.getElementById('ln3SetHost'), core: !!document.querySelector('#crSec .secbody #sCrL2Cap'), sat: !!document.querySelector('#satV2Sec #sV2Main'), lab: ((document.querySelector('[data-ln1-switch] label')||{}).textContent||'').trim()})")
        check(f"{tag} 8 โหมดเดิม: Port & Risk เป็นหมวดเดิม (เงินต้น · Core · SAT · SATELLITE v2 · RRG · Max Heat) · ช่องกลับที่เดิม · ป้ายสวิตช์เดิม 'หน้าแผน Sat'", lg["host"] is False and lg["secs"] >= 6 and lg["core"] and lg["sat"] and (lg["lab"] or "").startswith("หน้าแผน Sat"), lg)
        js(page, "()=>ln1SetMode('lean')"); page.wait_for_timeout(500)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); switchTab('mix'); }"); page.wait_for_timeout(300)
        check(f"{tag} 8 สลับกลับ Lean → ทุกแท็บเป็น Lean · เปิดตั้งค่าใหม่ได้ 6 หมวด", js(page, "()=>document.querySelectorAll('[data-ln3-sum]').length") == 1 and js(page, "()=>{ openSettings(); return document.querySelectorAll('#ln3SetHost > .ln3-g').length; }") == 6)
        # ── 9 ล้น + console
        js(page, "()=>document.querySelectorAll('#ln3SetHost > .ln3-g').forEach(d=>d.open = true)"); page.wait_for_timeout(300)
        ov = js(page, """()=>{ const W = window.innerWidth, bad = []; document.querySelectorAll('#setOverlay .modal *').forEach(e=>{ if(e.closest('table, .tablewrap, pre')) return; const r = e.getBoundingClientRect(); if(r.width && r.right > W + 1) bad.push((e.id || e.className || e.tagName) + ':' + Math.round(r.right)); }); return bad.slice(0, 5); }""")
        check(f"{tag} 9 {label} ไม่ล้นแนวนอน (กางทุกหมวด) · ไม่มี console error", overflow(page) <= 0 and not ov and not ce and not pe, [overflow(page), ov, ce[:2], pe[:2]])
        js(page, "()=>document.querySelectorAll('#ln3SetHost > .ln3-g').forEach(d=>d.open = false)")
        shot(page, f"ln3-settings-closed-{sfx}.png", "#setOverlay .modal")
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px"), (300, 700, "300px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": print("RETIRED - [p88] เทสตั้งค่าแบบ 6 หมวด LN3 + สวิตช์ Lean/เดิม: ฟีเจอร์ถูกแทนด้วยหน้า Settings 5 การ์ด (SET1) และ Lean ตายตัว — ดู tests/SET1_retired.md · ตรวจใหม่ใน phase110")
