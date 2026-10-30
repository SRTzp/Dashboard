#!/usr/bin/env python3
"""PF3b — p23 (เขียน users/{uid} ครั้งที่ 2 จาก snapshot Weekly Impact) · Today ข่าว ครั้งก่อน (period) · Today สมดุลคอลัมน์ (ลองย้าย Sat/ช่วงเวลา/ทั้งคู่)
· Sat accordion ร่างแผน (กางได้ทีละฟอร์ม) · หัว Weekly Impact แถวเดียว · ตัวอักษร +1 (Weekly Impact + การ์ด Macro .ln1-tile) · เทส 104
Chromium · FF_STUB_BASE = Lean · 300 / 320 / 375 / 390 / 1280 / 1440 · ข้อมูลทดสอบ = SAMPLE ล้วน
ภาพ tests/screenshots/pf3b-{today-1440,today-1280,drafts-390,drafts-1440,wi-320,wi-390,wi-1440,macro-390}.png
รัน: python3 run_tests_phase104.py"""
import copy, json, os
import pf2_retire as RT
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase56 as P56
import run_tests_phase100 as P100
import run_tests_phase102 as P102
import run_tests_phase103 as P103

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle = P100.settle


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def user_sets(page):
    return page.evaluate("() => (window.__setLog||[]).filter(x=>x.path==='users/testuid').length")


# ───────────────────────── 1 · p23 / carry-over ─────────────────────────
def write_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = P100.launch(pw, 390, 844, picks=["XAUUSD"])
    try:
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 800)
        n0 = user_sets(page)
        P100.seed(page, P100.sample()); settle(page, 1500)
        n1 = user_sets(page)
        d = js(page, "()=>({dirty: wiStratDirty, tab: activeTab})")
        check(f"{tag} 1 snapshot Weekly Impact ตอนอยู่แท็บ Today → ไม่เขียน users/{{uid}} เพิ่ม (หลัง {n0} → {n1}) · Strategy ติดธงรอวาด", n1 == n0 and d["dirty"] is True, [n0, n1, d])
        P100.go_strategy(page)
        d2 = js(page, "()=>({dirty: wiStratDirty, panel: !!document.querySelector('#satV3Panel [data-wi-panel]'), chips: document.querySelectorAll('#satV3Panel [data-wi-chip]').length, tiles: document.querySelectorAll('#satV3Panel [data-ln1-tile]').length})")
        check(f"{tag} 1 เปิด Plan › Sat → Strategy วาดแผง Weekly Impact + การ์ด Asset ตามสแนปช็อต · ธงล้าง", d2["dirty"] is False and d2["panel"] and d2["chips"] > 0 and d2["tiles"] > 0, d2)
        # เปิดอยู่แล้วเจอ snapshot ใหม่ → วาดทันที (ไม่ข้ามการเปลี่ยนจริง)
        doc2 = P100.sample(); doc2["assets"]["XAUUSD"]["note"] = "SAMPLE: ข้อความใหม่หลัง snapshot"
        doc2["assets"]["XAUUSD"]["impact"] = "MED"
        P100.seed(page, doc2); settle(page, 600)
        t = js(page, "()=>{ const c = document.querySelector('#satV3Panel [data-wi-chip=\"XAUUSD\"]'); return c ? c.getAttribute('data-wi-tier') : null; }")
        check(f"{tag} 1 Plan › Sat เปิดอยู่ + snapshot เปลี่ยน (HIGH→MED) → วาดใหม่ทันที", t == "MED", t)
        check(f"{tag} 1 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 2 · Today ครั้งก่อน (period) ─────────────────────────
def news_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = P100.launch(pw, 390, 844, picks=["XAUUSD"])
    try:
        d = P100.sample()
        d["events"]["e_pce"]["previous_period"] = "Sep 2026"
        d["events"]["e_late"]["previous_period"] = None
        d["assets"]["XAUUSD"]["event_refs"] = ["e_pce", "e_late"]
        P100.seed(page, d)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 800)
        rows = js(page, "()=>[...document.querySelectorAll('[data-wi-today] [data-wi-td]')].map(e=>({id:e.dataset.wiTd, txt:e.innerText.replace(/\\s+/g,' ')}))")
        by = {r["id"]: r["txt"] for r in rows}
        check(f"{tag} 2 Today ข่าววันนี้: มี previous_period → 'ครั้งก่อน (Sep 2026) 2.7%'", "Previous (Sep 2026) 2.7%" in by.get("e_pce", ""), by)
        has_late = "e_late" in by
        check(f"{tag} 2 Today ข่าววันนี้: ไม่มี previous_period → 'ครั้งก่อน 49.5' ไม่มีวงเล็บ (เหมือนเดิม)", (not has_late) or ("Previous 49.5" in by["e_late"] and "Previous (" not in by["e_late"]), by)
        # แผงใน Strategy ใช้ข้อความเดียวกัน (ตัวช่วยเดียว wiPrevLbl)
        s = js(page, "()=>[wiPrevLbl({previous_period:'Sep 2026'}), wiPrevLbl({previous_period:null}), wiPrevLbl({})]")
        check(f"{tag} 2 wiPrevLbl ตัวเดียวใช้ทุกจุด", s == ["ครั้งก่อน (Sep 2026)", "ครั้งก่อน", "ครั้งก่อน"], s)
    finally: b.close()


# ───────────────────────── 3 · Today สมดุลคอลัมน์ ─────────────────────────
MEASURE4 = """()=>{ const c1=document.querySelector('[data-td-col="1"]'),c2=document.querySelector('[data-td-col="2"]'),sat=document.querySelector('[data-ln3-satbox]'),sl=document.querySelector('[data-td-routine],[data-td-off]');
 const goal=c2.querySelector('[data-sd-today]')||c2.querySelector('[data-gl-goal]'); const out={};
 const cur=[sl,sat].map(x=>x.parentNode===c2);
 const arr=(ms,mt)=>{ [sl,sat].forEach(x=>c1.appendChild(x)); let a=goal; [[sl,ms],[sat,mt]].forEach(([x,on])=>{ if(on){ if(a) a.insertAdjacentElement('afterend',x); else c2.insertBefore(x,c2.firstChild); a=x; } });
   const r1=c1.getBoundingClientRect().bottom,r2=c2.getBoundingClientRect().bottom; return [Math.round(r1),Math.round(r2),+(Math.abs(r1-r2)/Math.max(r1,r2)).toFixed(3)]; };
 out.default=arr(0,0); out.sat=arr(0,1); out.slots=arr(1,0); out.both=arr(1,1); arr(cur[0],cur[1]); return out; }"""


def bal_numbers(page):
    return js(page, MEASURE4)


def balance_tests(pw):
    # TD3a — Today ไม่มี 2 คอลัมน์/tdBalance แล้ว (ดู TD3a_retired.md): ใช้เคสแทน = 3 panels ชิดบนเท่ากัน · ไม่ล้นแนวนอน · ไม่มี console error
    for w, h, lab in ((1280, 800, "1280px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{lab}/p94]"
        RT.retired_td3a(f"{tag} 3 tdBalance เลือกแบบที่ต่างน้อยสุด · phase94 fixture ≤ 35% — ดู TD3a_retired.md")
        b, ctx, page, ce, pe, dl = P56.launch(pw, w, h, P56.with_goals(), None, log={})
        try:
            js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 900)
            o = js(page, RT.PANELS_JS)
            check(f"{tag} 3 TD3a: 3 panels ชิดบนเท่ากัน · ไม่ล้นแนวนอน · ไม่มี console error", RT.panels_ok(o) and not [e for e in ce if "investing.com" not in e and "X-Frame" not in e and "403" not in e] and not pe, [o, ce[:2], pe[:2]])
            if lab == "1440px": C.shot(page, "pf3b-today-1440.png", full=True)
            if lab == "1280px": C.shot(page, "pf3b-today-1280.png", full=True)
        finally: b.close()
    for w, h, lab in ((1280, 800, "1280px"), (1440, 900, "1440px")):
        for variant in ("long", "short", "shortnews"):
            tag = f"[{ENGINE}/{lab}/{variant}]"
            V = P103.VARIANTS[variant]
            RT.retired_td3a(f"{tag} 3 tdBalance ≤ 15% · ลำดับขวา: เป้าหมาย → การ์ดที่ย้าย → การบ้านหุ้น — ดู TD3a_retired.md")
            b, page, ce, pe = P102.launch(pw, w, h)
            try:
                if V["news"]: P102.seed_wi(page)
                P102.seed(page, P102.stock_doc())
                P103.set_sat(page, V["picks"], V["plans"])
                if V["recheck"]: js(page, "()=>{ window.pbStaleInfo = ()=>({days:32,last:Date.now()-32*86400000,due:true}); }")
                P103.go_today(page)
                o = js(page, RT.PANELS_JS)
                check(f"{tag} 3 TD3a: 3 panels ชิดบนเท่ากัน · ไม่ล้นแนวนอน", RT.panels_ok(o), o)
            finally: b.close()


# ───────────────────────── 4 · Sat accordion ─────────────────────────
ST = """()=>{
  const P = document.getElementById('satV3Panel');
  const els = [...P.querySelectorAll('[data-ln3-row], .ln1-card')];
  const seq = els.map(e => e.matches('.ln1-card') ? 'F' : (e.getAttribute('data-ln3-state') === 'draft' ? 'D' : 'S'));
  const draftRows = [...P.querySelectorAll('[data-ln3-row][data-ln3-state="draft"]')].map(e => e.getAttribute('data-ln3-row'));
  const act = (typeof satActiveDraft !== 'undefined') ? satActiveDraft : null, ar = act ? P.querySelector('[data-ln3-row="' + act + '"]') : null, fm = P.querySelector('.ln1-card');
  const rowDup = act ? P.querySelectorAll('[data-ln3-row="' + act + '"]').length : 0;
  return {seq: seq.join(''), forms: P.querySelectorAll('.ln1-card').length, draftRows, collapsed: draftRows.filter(x => x !== act), rowDup, headAdj: !!(ar && fm && (ar.compareDocumentPosition(fm) & 4) && els.indexOf(fm) === els.indexOf(ar) + 1), active: (typeof satActiveDraft !== 'undefined') ? satActiveDraft : null,
          ow: document.documentElement.scrollWidth - innerWidth,
          ids: (satIdeasList || []).filter(x => x.v2 && x.status !== 'closed').map(x => x.id)};
}"""
FIELDS = """(id)=>{ const x = sat7dIdea(id); if(!x) return null; return {entry: x.entry, sl: x.sl, tp: x.tp, note: x.setup_note || '', zact: !!x.zone_act, ztxt: x.zone_act_txt || '', ck: (x.setup_ck || []).slice().sort(), bias: x.bias || '', classify: x.classify || '', skip: JSON.stringify(x.accts || {}), sleeve: x.sleeve, asset: x.asset}; }"""
FORM = """()=>{ const f = document.querySelector('#satV3Panel .ln1-card'); if(!f) return null; const v = s => { const e = f.querySelector(s); return e ? e.value : null; };
  return {entry: v('[data-v2-entry]'), sl: v('[data-v2-sl]'), tp: v('[data-v2-tp]'), note: ((f.querySelector('[data-ln1-oldnote] .ln1-fb') || {}).textContent || '').trim(), zact: !!v('[data-pf-ztxt]'), ck: [...f.querySelectorAll('[data-pf-setup]:checked')].map(e=>e.dataset.pfSetup).sort(),
          lot: [...f.querySelectorAll('[data-ln1-lot]')].map(e=>e.innerText.trim()), risk: [...f.querySelectorAll('[data-ln1-risk]')].map(e=>e.innerText.trim())}; }"""


def fill_active(page, entry, sl, tp, note, ck_keys):
    js(page, "()=>{ const i = satIdeasList.find(x=>x.id===satActiveDraft); if(i && satV2Sleeve(i)==='tactical' && pfClsKey(i.classify)!=='clear') satV3IdeaWrite(i.id,{classify:'clear'}); }"); settle(page, 500)   # CS1 — Tactical ต้อง Clear Trend
    f = page.locator("#satV3Panel .ln1-card").first
    f.locator("[data-v2-entry]").fill(str(entry)); f.locator("[data-v2-sl]").fill(str(sl)); f.locator("[data-v2-tp]").fill(str(tp))
    f.locator("[data-v2-tp]").press("Tab"); settle(page, 300)
    js(page, "()=>{ document.querySelectorAll('#satV3Panel .ln1-more').forEach(d => d.open = true); }")
    js(page, "(n)=>satV2Edit(satActiveDraft,'setup_note',n)", note); settle(page, 400)   # TD4b: ไม่มีช่องโน้ต 'เสริม' แล้ว — เขียนค่าตรง ๆ (โน้ตเดิมแสดงอ่านอย่างเดียว)
    page.locator("#satV3Panel .ln1-card [data-pf-ztxt]").first.fill("4,230–4,250"); page.locator("#satV3Panel .ln1-card [data-pf-ztxt]").first.press("Tab"); settle(page, 300)   # TD4b: ไม่มีช่องติ๊ก Zone Activation — กรอก Zone = ตั้ง Zone
    for k in ck_keys:
        page.locator(f"#satV3Panel .ln1-card [data-pf-setup='{k}']").first.check(); settle(page, 250)


def ok_order(s):
    """S* D* F? : saved → collapsed → expanded"""
    import re
    return re.fullmatch(r"S*D*F?", s) is not None


def drafts_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = P100.launch(pw, w, h, picks=["XAUUSD", "BTCUSD", "BRENT"])
    try:
        P100.go_strategy(page)
        ids = []
        for a, sv in (("XAUUSD", "main"), ("BTCUSD", "main"), ("XAUUSD", "tactical")):
            i = js(page, "([a, sv])=>{ lfSatSet(a); const id = satV2NewPlan(a, sv); satV3Render({force:true}); return id; }", [a, sv]); settle(page, 500)
            ids.append(i)
        A, B, Cc = ids
        s = js(page, ST)
        check(f"{tag} 4 สร้างร่าง 3 ใบ (+ แผน ทีละใบ) → ร่างล่าสุดกาง ใบก่อนหน้าพับ · กางได้ ≤ 1 · ลำดับ DOM = พับ → กาง", s["forms"] == 1 and s["active"] == Cc and s["collapsed"] == [A, B] and s["rowDup"] == 1 and s["headAdj"] and ok_order(s["seq"]), s)
        vals = {A: (4180, 4117, 4350, "A-note", ["sweep"]), B: (68200, 66900, 71000, "B-note", []), Cc: (82.5, 84.0, 78.0, "C-note", [])}
        # ชนิดของ setup_ck: ใช้คีย์จริงของแอป
        keys = js(page, "()=>PF_SETUP_CK.map(x=>x[0])")
        vals[A] = (4180, 4117, 4350, "A-note", keys[:2]); vals[B] = (68200, 66900, 71000, "B-note", keys[1:3]); vals[Cc] = (4200, 4160, 4330, "C-note", keys[:1])
        rec = {}; risk = {}
        steps_ok = True; step_log = []

        def act(i):
            if js(page, "()=>satActiveDraft") != i:
                page.locator(f'[data-ln3-row="{i}"]').click(); settle(page, 600)
            st = js(page, ST); step_log.append(st["seq"])
            return st
        # กรอก A → B → C (สลับระหว่างกรอก)
        for i in (A, B, Cc):
            st = act(i)
            steps_ok = steps_ok and st["forms"] == 1 and ok_order(st["seq"]) and st["active"] == i and i not in st["collapsed"] and st["rowDup"] == 1 and st["headAdj"]
            tr = "up"
            js(page, "([id])=>{ pfTrendSet(id, 'up'); }", [i]); settle(page, 400)
            fill_active(page, *vals[i])
            rec[i] = js(page, FIELDS, i); risk[i] = js(page, FORM)
        check(f"{tag} 4 กรอกค่าร่าง A/B/C สลับกันไป → ทุกขั้นกางฟอร์ม ≤ 1 · ใบที่กางไม่โผล่ในกลุ่มพับ · ลำดับ 'ที่บันทึก → พับ → กาง' ({step_log})", steps_ok, step_log)
        check(f"{tag} 4 ค่าถูกเก็บในร่างจริง (A: Entry {rec[A]['entry']} SL {rec[A]['sl']} TP {rec[A]['tp']} · note · Zone · setup {rec[A]['ck']})", rec[A]["entry"] == 4180 and rec[A]["sl"] == 4117 and rec[A]["tp"] == 4350 and rec[A]["note"] == "A-note" and rec[A]["zact"] and len(rec[A]["ck"]) == 2 and rec[B]["note"] == "B-note" and rec[Cc]["entry"] == 4200, rec)
        n_before = len(js(page, ST)["ids"])
        # สลับ A→B→C→A
        seqs = []
        for i in (A, B, Cc, A):
            st = act(i); seqs.append(st["seq"])
            fm = js(page, FORM)
            exp = rec[i]
            same = (float(fm["entry"]) == float(exp["entry"]) and float(fm["sl"]) == float(exp["sl"]) and float(fm["tp"]) == float(exp["tp"]) and fm["zact"] == exp["zact"] and sorted(fm["ck"]) == exp["ck"])
            check(f"{tag} 4 สลับไปร่าง {['A','B','C'][[A,B,Cc].index(i)]} → ฟอร์มกางอันเดียว · ค่าในฟอร์มเท่าที่กรอก (Entry/SL/TP/Zone/Setup)", st["forms"] == 1 and ok_order(st["seq"]) and same and st["active"] == i, [st["seq"], fm, exp])
        note_dom = js(page, "()=>{ document.querySelectorAll('#satV3Panel .ln1-more').forEach(d=>d.open=true); const e = document.querySelector('#satV3Panel .ln1-card [data-ln1-oldnote] .ln1-fb'); return e ? e.textContent.trim() : null; }")
        check(f"{tag} 4 โน้ตในฟอร์มกลับมาครบหลังสลับ ({note_dom})", note_dom == "A-note", note_dom)
        a2 = js(page, FORM)
        check(f"{tag} 4 ตัวเลข lot/Risk ของร่าง A เท่าเดิมก่อน-หลังสลับ ({a2['lot']} · {a2['risk']})", a2["lot"] == risk[A]["lot"] and a2["risk"] == risk[A]["risk"] and len(a2["lot"]) > 0, [risk[A], a2])
        all_same = all(js(page, FIELDS, i) == rec[i] for i in (A, B, Cc))
        check(f"{tag} 4 หลังสลับ A→B→C→A ค่าทุกร่างใน idea ยังเท่าเดิมทุกช่อง · จำนวนร่างไม่เปลี่ยน ({n_before})", all_same and len(js(page, ST)["ids"]) == n_before, [n_before, len(js(page, ST)["ids"])])
        # + แผน (ร่างใหม่ของ S50) → ร่างปัจจุบันพับ ค่าคงเดิม
        js(page, "()=>{ lfSatSet('BRENT'); satV3Render({force:true}); }"); settle(page, 400)
        page.locator('[data-ln1-plan="BRENT"]').first.click(); settle(page, 700)
        st = js(page, ST); newid = st["active"]
        check(f"{tag} 4 กด + แผน → ร่างปัจจุบันพับ · ร่างใหม่กาง (ใบเดียว) · ร่าง 4 ใบ · ใบเดิมไม่ซ้ำ", st["forms"] == 1 and ok_order(st["seq"]) and newid not in ids and len(st["ids"]) == n_before + 1 and all(i in st["collapsed"] for i in ids) and newid not in st["collapsed"] and st["headAdj"], st)
        check(f"{tag} 4 ร่างเดิมค่าครบหลัง + แผน", all(js(page, FIELDS, i) == rec[i] for i in ids), "")
        if shots:
            page.add_style_tag(content=".tabs, .topbar{ display:none !important } *{ animation:none !important; transition:none !important }")   # ซ่อนแถบ fixed + ปิดแอนิเมชัน (เฉพาะตอนถ่าย)
            js(page, "()=>document.getElementById('satV3Panel').scrollIntoView()"); settle(page, 1200)
            C.shot(page, f"pf3b-drafts-{w}.png", "#satV3Panel")
        # พับหมด
        page.locator(f'[data-ln3-row="{newid}"]').click(); settle(page, 600)
        st = js(page, ST)
        check(f"{tag} 4 แตะหัวร่างที่กาง → พับ · พับหมดได้ (กาง 0) · ร่างทั้ง 4 อยู่เป็นแถวพับ", st["forms"] == 0 and st["active"] is None and len(st["collapsed"]) == 4 and ok_order(st["seq"]), st)
        check(f"{tag} 4 พับหมดแล้วค่าทุกร่างเท่าเดิม", all(js(page, FIELDS, i) == rec[i] for i in ids), "")
        # เปิดร่างอีกใบ แล้วบันทึกหนึ่งใบ → ย้ายไปแผนที่บันทึก ที่เหลือยังพับ + ค่าครบ
        st = act(A)
        saved = js(page, "(id)=>{ try{ satV3SaveReadyAccounts(id); return true; }catch(e){ return String(e); } }", A); settle(page, 1000)
        st = js(page, ST)
        stA = js(page, "(id)=>{ const x = sat7dIdea(id); return x ? satV3PlanRowState(x) : null; }", A)
        check(f"{tag} 4 บันทึกร่าง A → ออกจากกลุ่มร่าง ({stA}) · ไม่มีร่างกางอยู่ · ร่างอื่นพับและค่าเดิมครบ · ลำดับ 'ที่บันทึก → พับ'", saved is True and stA != "draft" and A not in st["draftRows"] and st["forms"] == 0 and st["draftRows"] == [x for x in st["draftRows"] if x != A] and all(js(page, FIELDS, i) == rec[i] for i in (B, Cc)) and ok_order(st["seq"]), [saved, stA, st, ])
        check(f"{tag} 4 ไม่ล้นแนวนอน · ไม่มี console error", st["ow"] <= 0 and not ce and not pe, [st["ow"], ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 5 · หัว Weekly Impact ─────────────────────────
HD = """()=>{ const w = document.querySelector('#satV3Panel [data-wi-panel]'); if(!w) return null; const hd = w.querySelector('.wiHd'), p = w.querySelector('[data-wi-paste]'), t = w.querySelector('.wiT');
  const metas = [...w.querySelectorAll('[data-wi-meta]')], pr = p.getBoundingClientRect(), wr = w.getBoundingClientRect(), lh = parseFloat(getComputedStyle(t).lineHeight) || 24;
  return {h: Math.round(hd.getBoundingClientRect().height), lh, lines: +(hd.getBoundingClientRect().height / lh).toFixed(2), paste: [Math.round(pr.width), Math.round(pr.height)], pasteIn: pr.right <= wr.right + 0.5 && pr.left >= wr.left - 0.5,
          metaTxt: metas.map(e => e.innerText.trim()), clip: metas.map(e => e.scrollWidth > e.clientWidth + 1), metaIn: metas.every(e => { const r = e.getBoundingClientRect(); return r.right <= wr.right + 0.5 && r.left >= wr.left - 0.5; }),
          ow: document.documentElement.scrollWidth - innerWidth, wiW: Math.round(wr.width), title: t.innerText.trim(),
          want: [wiRangeText(wiCurMon()) + ' · ICT', 'อัปเดต ' + wiAsofText(wiCurDoc().asof)],
          overlap: (() => { const a = t.getBoundingClientRect(), bb = metas[0].getBoundingClientRect(), c = pr; const hit = (x, y) => x.left < y.right - 0.5 && y.left < x.right - 0.5 && x.top < y.bottom - 0.5 && y.top < x.bottom - 0.5; return hit(a, bb) || hit(bb, c) || hit(a, c); })()}; }"""


def header_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = P100.launch(pw, w, h, picks=["XAUUSD"])
    try:
        P100.seed(page, P100.sample()); P100.go_strategy(page)
        o = js(page, HD)
        mac = w >= 1000
        check(f"{tag} 5 หัว Weekly Impact: ข้อความเดิมครบ (ช่วงวันที่ · ICT / อัปเดต …) {o['metaTxt']}", o["metaTxt"] == o["want"] and o["title"] == "Weekly Impact", [o["metaTxt"], o["want"]])
        check(f"{tag} 5 Paste แตะง่าย ≥ 40×40 ({o['paste']}) · อยู่ในกรอบแผง", o["paste"][0] >= 40 and o["paste"][1] >= 40 and o["pasteIn"], o)
        if mac: check(f"{tag} 5 Desktop: หัวอยู่แถวเดียว (สูง {o['h']}px ≈ {o['lines']} บรรทัด)", o["lines"] <= 1.25, o)
        else:
            lim = 2.25 if w >= 375 else 3.25   # 320px: แผงกว้างแค่ ~236px (ซ้อน padding) → ช่วงวันที่กับอัปเดตลงคนละบรรทัดได้ = 3 บรรทัด (ไม่ตัดข้อความ)
            check(f"{tag} 5 มือถือ: หัวสูงไม่เกิน {2 if w >= 375 else 3} บรรทัด (สูง {o['h']}px ≈ {o['lines']} บรรทัด · แผงกว้าง {o['wiW']}px)", o["lines"] <= lim, o)
        check(f"{tag} 5 วันที่ไม่ถูกตัด (scrollWidth ≤ clientWidth) · ไม่ทับกัน · ไม่ล้นแนวนอน", not any(o["clip"]) and not o["overlap"] and o["metaIn"] and o["ow"] <= 0, o)
        if shots: C.shot(page, f"pf3b-wi-{w}.png", "[data-wi-panel]")
        check(f"{tag} 5 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 6 · ตัวอักษร +1 ─────────────────────────
OLD = {  # ค่าเดิม (ก่อน PF3b) ที่วัดจริงจากหน้าเดียวกัน
    "wiT": ".wi .wiT", "wiSm": ".wi .wiSm", "wiNm": ".wi .wiNm", "wiTx": ".wi .wiTx", "wiDetH": ".wi .wiDetH", "wiK": ".wi .wiK", "wiBdg": ".wi .wiBdg", "wiAct": ".wi .wiAct",
    "tileTitle": ".ln1-tile .ui-tile-a", "wiS1": ".ln1-tile .wiS1", "wiSL": ".ln1-tile .wiSL", "wiTierP": ".ln1-tile .wiTierP", "zrLab": ".ln1-tile .ln3-zr .ln1-lab", "zrTx": ".ln1-tile .ln3-zr .pf2-tx",
    "chgK": ".ln1-tile .ln3-chg .pf2-k", "chgTx": ".ln1-tile .ln3-chg .pf2-tx", "opLab": ".ln1-tile .ln3-op .ln1-lab", "opTa": ".ln1-tile .ln3-op textarea", "link": ".ln1-tile .ln3-links .ln1-link"}
OLD_PX = {
    390: {"wiT": 15, "wiSm": 12, "wiNm": 14, "wiTx": 10.5, "wiDetH": 14, "wiK": 12, "wiBdg": 11, "wiAct": 13, "tileTitle": 14.96, "wiS1": 12, "wiSL": 14, "wiTierP": 11.5, "zrLab": 12, "zrTx": 16, "chgK": 12, "chgTx": 16, "opLab": 12, "opTa": 16, "link": 12},
    1440: {"wiT": 15, "wiSm": 12, "wiNm": 14, "wiTx": 10.5, "wiDetH": 14, "wiK": 12, "wiBdg": 11, "wiAct": 13, "tileTitle": 16.66, "wiS1": 12, "wiSL": 14, "wiTierP": 11.5, "zrLab": 12, "zrTx": 13, "chgK": 12, "chgTx": 12, "opLab": 12, "opTa": 16, "link": 12}}
OLD_H = {390: {"wi": 788, "tile": 614}, 1440: {"wi": 707, "tile": 700}}   # ก่อน PF3b: เปิดรายละเอียด XAUUSD ในแผง · sample เดียวกัน
SZ = """(S)=>{ const o = {}; for(const [k, s] of Object.entries(S)){ const e = document.querySelector(s); o[k] = e ? parseFloat(getComputedStyle(e).fontSize) : null; }
  const w = document.querySelector('#satV3Panel .wi'), t = document.querySelector('#satV3Panel .ln1-tile'); o.H = {wi: w && w.offsetHeight, tile: t && t.offsetHeight};
  o.ow = document.documentElement.scrollWidth - innerWidth;
  /* ส่วนที่มองเห็นต้องอยู่ในกรอบ (scrollWidth ของการ์ดมีส่วนซ่อนเดิมที่ไม่เกี่ยวกับรอบนี้) */
  o.clip = [w, t].map(c => { if(!c) return false; const cr = c.getBoundingClientRect(); return [...c.querySelectorAll('*')].some(e => { const r = e.getBoundingClientRect(); return e.clientWidth > 0 && r.width > 0 && r.height > 0 && (r.right > cr.right + 1 || r.left < cr.left - 1); }); }); return o; }"""


def text_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = P100.launch(pw, w, h, picks=["XAUUSD", "S50"])
    try:
        d = P100.sample(); d["events"]["e_pce"].update({"actual": 2.7, "status": "released"})
        P100.seed(page, d); P100.go_strategy(page)
        js(page, "()=>{ wiToggle('XAUUSD'); }"); settle(page, 400)
        o = js(page, SZ, OLD)
        old = OLD_PX[w]
        bad = {k: [old[k], o[k]] for k in old if o.get(k) is not None and abs(o[k] - (old[k] + 1)) > 0.03}
        miss = [k for k in old if o.get(k) is None]
        check(f"{tag} 6 ตัวอักษรใน Weekly Impact + การ์ด Macro = เดิม +1px ทุกจุดที่วัดได้ ({len(old) - len(miss)} จุด)", not bad, bad)
        print(f"INFO {tag} ไม่พบองค์ประกอบ (ไม่ได้วัด): {miss}")
        hb = OLD_H[w]
        check(f"{tag} 6 ความสูงแผง Weekly Impact {hb['wi']}→{o['H']['wi']}px · การ์ด Asset {hb['tile']}→{o['H']['tile']}px ไม่เกิน +10%", o["H"]["wi"] <= hb["wi"] * 1.10 and o["H"]["tile"] <= hb["tile"] * 1.10, [hb, o["H"]])
        check(f"{tag} 6 ไม่ล้นแนวนอน/ไม่ถูกตัด", o["ow"] <= 0 and not any(c for c in o["clip"] if c), o)
        if shots: C.shot(page, f"pf3b-macro-{w}.png", "#satV3Panel .ln1-tile")
        check(f"{tag} 6 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def narrow_tests(pw, w, h):
    tag = f"[{ENGINE}/{w}px]"
    b, page, ce, pe = P100.launch(pw, w, h, picks=["XAUUSD", "S50"])
    try:
        P100.seed(page, P100.sample()); P100.go_strategy(page)
        js(page, "()=>{ wiToggle('XAUUSD'); }"); settle(page, 300)
        o = js(page, SZ, OLD); hd = js(page, HD)
        check(f"{tag} 6 จอแคบ {w}px: ไม่ล้นแนวนอน · แผง/การ์ดไม่ถูกตัด · วันที่ไม่ถูกตัด · Paste ≥ 40", o["ow"] <= 0 and not any(c for c in o["clip"] if c) and not any(hd["clip"]) and hd["paste"][0] >= 40 and hd["paste"][1] >= 40 and not hd["overlap"], [o["ow"], o["clip"], hd])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        write_tests(pw)
        news_tests(pw)
        balance_tests(pw)
        drafts_tests(pw, 390, 844, "390px", shots=True)
        drafts_tests(pw, 1440, 900, "1440px", shots=True)
        for w, h, sh in ((320, 700, True), (375, 812, False), (390, 844, True), (1440, 900, True)):
            header_tests(pw, w, h, f"{w}px", shots=sh)
        text_tests(pw, 390, 844, "390px", shots=True)
        text_tests(pw, 1440, 900, "1440px")
        narrow_tests(pw, 300, 700); narrow_tests(pw, 320, 700)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
