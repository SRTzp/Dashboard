#!/usr/bin/env python3
"""TD4b — Satellite / Plan polish · Watchlist add-on-candidate · Today Cand→WL พับ · เอา Other ออก · เทส 108
Chromium · 300 / 390 / 1280 / 1440 · Sat: fixture P77 (Lean) · Watch/Today: fixture P106/P107 (นาฬิกาปลอม 1 ต.ค. 2026 12:00 ICT) · ข้อมูล SAMPLE ล้วน
ภาพ tests/screenshots/td4b-{plan-1440,plan-390,tranche2-390,today-sat-390,form-390,watch-390,watch-1440,today-core-390}.png
รัน: SECT='sat watch today' python3 run_tests_phase108.py   (ส่วน = rename zone ctx pin tranche height sat watch today width)"""
import json, os, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน (ตั้ง FF_STUB = Lean ก่อน P39 ถูก import)
import run_tests_phase4 as base
import run_tests_phase39 as P39
import run_tests_phase77 as P77
import run_tests_phase78 as P78
import run_tests_phase79 as P79
import run_tests_phase107 as T

ENGINE = base.BROWSER_ENGINE
P39.TD3_OTHER_DEV = False   # ชุดนี้ตรวจว่า Today ไม่มี Other จริง (ไม่เปิดจุดต่อของเทสเก่า)
HERE = os.path.dirname(os.path.abspath(__file__))
OLD_INDEX = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-TD4b.html"))
results = []
js, settle, txt, cnt, ovf = T.js, T.settle, T.txt, T.cnt, T.ovf
LOG = {}   # ตัวเลขที่ใช้ในรายงาน


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


# ───────────────────────── helpers: Sat ─────────────────────────
def sat_launch(pw, w, h, old=False, bias="Long"):
    """P77 launcher (Lean) · old=True → index.backup-pre-TD4b.html (เทียบก่อน/หลัง)"""
    keep = P39.INDEX
    if old: P39.INDEX = OLD_INDEX
    try:
        b, page, ce, pe = P77.launch(pw, w, h, bias=bias)
    finally:
        P39.INDEX = keep
    js(page, "()=>{ ln1SetMode('lean'); render(); }"); settle(page, 400)
    return b, page, ce, pe


def sat_rows(page): return js(page, "()=>[...document.querySelectorAll('#satV3Panel .ln3-prow[data-ln3-row]')].map(e=>e.dataset.ln3Row)")
def today_sat(page): return js(page, "()=>[...document.querySelectorAll('[data-td3-sat]')].map(e=>e.dataset.td3Sat + ':' + e.dataset.sleeve)")
def to_today(page): js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
def to_plan(page): js(page, "()=>{ switchTab('plan'); setPlanScope('future'); satV3Render({force:true}); }"); settle(page, 500)


def opened_main(page, split="50/30/20"):
    """Main XAUUSD เข้าแล้ว 1 ไม้ + เติมไม้ 2 (บัญชี main) → (idea id, trade 1 id)"""
    P78.setcfg(page, splitMain=split)
    iid = P79.make(page, "main", 4180, 4117)
    P79.save(page, iid); P79.openall(page)
    t1 = js(page, "()=>getBook('main').trades.find(t=>t.port==='satB').id")
    return iid, t1


MEASURE = """()=>{ const h = document.querySelector('.lf-held'), d = document.querySelector('.lf-pd');
  const a = h ? h.getBoundingClientRect().height : 0, b = d ? d.getBoundingClientRect().height : 0;
  return {held:a, detail:b, lines:[...document.querySelectorAll('.lf-pl')].map(e=>Math.round(e.getBoundingClientRect().height)), total:a + b}; }"""


# ───────────────────────── 1 rename · zone · notes ─────────────────────────
def rename_zone_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = sat_launch(pw, w, h)
    try:
        ck = js(page, "()=>PF_SETUP_CK.map(x=>x.join('|'))")
        check(f"{tag} §1 ป้ายใหม่ 'MA Align Overlap' · key เดิม align_ma50 ไม่เปลี่ยน · ไม่มีคำว่า Align MA50 ในรายการ", "align_ma50|MA Align Overlap" in ck and not any("Align MA50" in x for x in ck) and len(ck) == 3, ck)
        iid = P79.idea(page, sleeve="main", entry=4180, sl=4117)
        js(page, "(i)=>{ if(satActiveDraft!==i) ln3ToggleDraft(i); }", iid); settle(page, 400)
        chips = txt(page, "[data-pf-setups]") or ""
        body = js(page, "()=>document.body.innerText")
        check(f"{tag} §1 ฟอร์มแผนแสดง 'MA Align Overlap' ทั้งหน้าไม่มี 'Align MA50'", "MA Align Overlap" in chips and "Align MA50" not in body, chips)
        LOG["zone_old_plans_fixture"] = js(page, "()=>satIdeasList.filter(x=>x.v3 && x.zone_act!==true && String(x.zone_act_txt||'').trim()).length")   # แผนใน fixture ที่ไม่ติ๊ก Activation แต่มี Zone เก็บไว้
        # แผนเก่า: setup_ck ที่เก็บด้วย key เดิม + Zone ที่เคยบันทึกโดยไม่ติ๊ก Activation
        js(page, "(i)=>satV3IdeaWrite(i, {setup_ck:['align_ma50'], zone_act:false, zone_act_txt:'4,230–4,250'})", iid); settle(page, 500)
        js(page, "()=>satV3Render({force:true})"); settle(page, 300)
        st = js(page, "(i)=>{ const x = sat7dIdea(i); return {ck:x.setup_ck, za:x.zone_act, zt:x.zone_act_txt}; }", iid)
        on = js(page, "()=>document.querySelector('[data-pf-setup=\"align_ma50\"]').checked")
        zv = js(page, "()=>document.querySelector('[data-pf-ztxt]').value")
        check(f"{tag} §1 แผนเก่า (setup_ck ['align_ma50']) ยังติ๊กข้อ MA Align Overlap · key ใน Firestore เดิม", on is True and st["ck"] == ["align_ma50"], [on, st])
        check(f"{tag} §2 ไม่มีช่องติ๊ก Zone Activation · มีช่อง Zone ช่องเดียว · แผนเก่า (ไม่ติ๊ก + มี Zone) ยังเห็น Zone เดิม (ไม่แก้ข้อมูล)", cnt(page, "[data-pf-zact]") == 0 and "Zone Activation" not in js(page, "()=>document.body.innerText") and zv == "4,230–4,250" and st["za"] is False and st["zt"] == "4,230–4,250", [zv, st])
        page.fill("[data-pf-ztxt]", "4,300–4,320"); page.locator("[data-pf-ztxt]").blur(); settle(page, 500)
        st2 = js(page, "(i)=>{ const x = sat7dIdea(i); return [x.zone_act_txt, x.zone_act]; }", iid)
        check(f"{tag} §2 พิมพ์ Zone ได้ตรง ๆ · ไม่ว่าง = ตั้ง Zone (zone_act true)", st2 == ["4,300–4,320", True], st2)
        page.fill("[data-pf-ztxt]", ""); page.locator("[data-pf-ztxt]").blur(); settle(page, 500)
        st3 = js(page, "(i)=>{ const x = sat7dIdea(i); return [x.zone_act_txt, x.zone_act]; }", iid)
        check(f"{tag} §2 ล้างช่อง Zone = ไม่ตั้ง Zone (zone_act false) · ไม่กระทบ Risk/ขนาดไม้", st3 == ["", False], st3)
        # Additional notes
        txt_form = js(page, "()=>document.querySelector('#satV3Panel .ln1-form') ? document.querySelector('#satV3Panel').innerText : ''")
        check(f"{tag} §4 ฟอร์มแผนใหม่ไม่มีส่วน 'เพิ่มเติม' + ช่องโน้ต 'เสริม' (data-v2-note) · แผนที่ไม่มีโน้ต = ไม่มีแถวโน้ตว่าง", cnt(page, "[data-v2-note]") == 0 and "เพิ่มเติม" not in txt_form and cnt(page, "[data-ln1-oldnote]") == 0, txt_form[:200])
        js(page, "(i)=>satV2Edit(i,'setup_note','Break 4,245')", iid); settle(page, 500); js(page, "()=>satV3Render({force:true})"); settle(page, 300)
        det = js(page, "()=>{ const d = document.querySelector('[data-ln1-more]'); if(d) d.open = true; return d ? d.innerText.replace(/\\s+/g,' ') : ''; }")
        check(f"{tag} §4 แผนที่มีโน้ตเดิม: โน้ตยังแสดง (อ่านอย่างเดียว) · ค่า setup_note ยังเก็บอยู่ · ส่วน Macro/ขนาดไม้/Driver ยังอยู่", cnt(page, "[data-ln1-oldnote]") == 1 and "Break 4,245" in det and js(page, "(i)=>sat7dIdea(i).setup_note", iid) == "Break 4,245" and cnt(page, "[data-ln1-mac]") == 1 and cnt(page, "[data-v2-note]") == 0, det[:200])
        check(f"{tag} {label} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 1 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 2 context line · pin · sort ─────────────────────────
def ctx_pin_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = sat_launch(pw, w, h)
    try:
        # แผน A: XAU Tactical · B: BTC Main · C: XAU Main
        A = P79.idea(page, sleeve="tactical", entry=4180, sl=4157.5)
        B = P79.idea(page, asset="BTCUSD", sleeve="main", entry=60000, sl=58000, bias="Long")
        C_ = P79.idea(page, sleeve="main", entry=4180, sl=4117)
        js(page, "([a,c])=>{ satV2Edit(a,'tf','4H'); satV3IdeaWrite(c, {zone_act_txt:'4,230–4,250', zone_act:true}); satV2Edit(c,'tf','4H'); }", [A, C_]); settle(page, 500)
        js(page, "()=>{ satActiveDraft = null; satV3Render({force:true}); }"); settle(page, 400)
        ctx = lambda i: txt(page, f'[data-sat-ctx="{i}"]')
        check(f"{tag} §5 บรรทัดบริบท Plan: Main · 4H · Long · Zone 4,230–4,250 (ชนิดแผน · TF · Bias · Zone)", ctx(C_) == "Main · 4H · Long · Zone 4,230–4,250", ctx(C_))
        check(f"{tag} §5 Tactical: ไม่มี Zone = ข้ามส่วน Zone (ไม่แสดง —) · 'Tactical · 4H · Long'", ctx(A) == "Tactical · 4H · Long", ctx(A))
        js(page, "(i)=>{ satV3IdeaWrite(i, {bias:'', tf:''}); satV3Render({force:true}); }", B); settle(page, 400)
        c2 = ctx(B) or ""
        allctx = js(page, "()=>[...document.querySelectorAll('[data-sat-ctx]')].map(e=>e.innerText)")
        check(f"{tag} §5 ไม่มี Bias/Zone = ข้าม (เหลือชนิดแผน + TF ค่าเริ่ม) · ไม่มีขีด — ในบรรทัดบริบทเลย", c2.startswith("Main") and "Long" not in c2 and "Zone" not in c2 and all("—" not in x for x in allctx), [c2, allctx])
        js(page, "(i)=>{ satV2SetDir(i,'Long'); satV3Render({force:true}); }", B); settle(page, 300)
        # เรียง: ไม่ปักหมุด → Main ก่อน Tactical
        rows = sat_rows(page); iA, iB, iC = rows.index(A), rows.index(B), rows.index(C_)
        check(f"{tag} §5 เรียงค่าเริ่ม (ไม่มี ★): Main (BTC · XAU) ก่อน Tactical · Tactical ท้ายสุด", iA > iB and iA > iC, rows)
        js(page, "()=>satPinToggle('BTCUSD')"); settle(page, 500)
        pinned = js(page, "()=>satAssetCfg().BTCUSD")
        r1 = sat_rows(page)
        check(f"{tag} §5 ★ BTCUSD ปักหมุด: เก็บที่ satAssetCfg.BTCUSD.pinned (ต่อ Asset ไม่ผูกสัปดาห์) · แผน BTC ขึ้นบนสุดใน Plan", pinned == {"pinned": True} and r1[0] == B, [pinned, r1])
        js(page, "()=>{ satPinToggle('BTCUSD'); satPinToggle('XAUUSD'); }"); settle(page, 500)
        r2 = sat_rows(page)
        check(f"{tag} §5 ★ XAUUSD (ถอด BTC): XAU ก่อน — ภายใน XAU Main (C) ก่อน Tactical (A) แล้วค่อย BTC · BTC ถูกถอดหมุดจริง (ไม่มี key ค้าง)", r2.index(C_) < r2.index(A) < r2.index(B) and js(page, "()=>satAssetCfg().BTCUSD") is None, r2)
        chips = js(page, "()=>[...document.querySelectorAll('[data-wa-chip]')].map(e=>e.dataset.waChip)")
        tiles = js(page, "()=>[...document.querySelectorAll('.ln1-tile .satPin')].map(e=>e.dataset.satPin)")
        big = js(page, "()=>{ const b = [...document.querySelectorAll('[data-sat-pin]')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect()); return b.length > 0 && b.every(x=>x.height >= 31.5 && x.width >= 27); }")
        check(f"{tag} §5 Asset chips/การ์ด Asset เรียง ★ ก่อน: XAUUSD ก่อน BTCUSD · ปุ่ม ★ ที่มองเห็นแตะได้ ≥ 32px", chips[0] == "XAUUSD" and tiles[:2] == ["XAUUSD", "BTCUSD"] and big is True, [chips, tiles, big])
        # Today
        js(page, "()=>satPinToggle('XAUUSD')"); settle(page, 300)
        to_today(page)
        t0 = today_sat(page)
        check(f"{tag} §5 Today Satellite (ไม่มี ★): XAU Main · BTC Main · XAU Tactical (Main ก่อน Tactical ข้าม Asset)", t0 == ["XAUUSD:main", "BTCUSD:main", "XAUUSD:tactical"], t0)
        js(page, "()=>satPinToggle('BTCUSD')"); to_today(page)
        t1 = today_sat(page)
        check(f"{tag} §5 Today (★ BTC): BTC ขึ้นบนสุด แล้ว XAU Main · XAU Tactical", t1 == ["BTCUSD:main", "XAUUSD:main", "XAUUSD:tactical"] and cnt(page, "[data-td3-sat=\"BTCUSD\"] [data-sat-pinmk]") == 1, t1)
        tc = txt(page, '[data-td3-sat="XAUUSD"][data-sleeve="main"] [data-sat-ctx]') or ""
        check(f"{tag} §5 Today แถว XAU Main มีบรรทัดบริบทเดียวกับ Plan: 'Main · 4H · Long · Zone 4,230–4,250'", tc == "Main · 4H · Long · Zone 4,230–4,250", tc)
        # persist ผ่านการบันทึกตั้งค่า (brInit → brCfgClean ต้องไม่ทำ pinned หาย)
        keep = js(page, "()=>{ brInit(); const o = brCfgClean(brDraft.cfg.BTCUSD); brDraft = null; return o; }")
        check(f"{tag} §5 ★ รอดการบันทึก ตั้งค่าโบรก/สินค้า (brInit → brCfgClean ยังเก็บ pinned)", keep == {"pinned": True}, keep)
        if shots:
            to_plan(page); js(page, "()=>{ switchTab('plan'); }"); settle(page, 300)
        check(f"{tag} {label} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 1 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 3 tranche 2 + clutter + compact + byte-identical ─────────────────────────
def tranche_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    out = {}
    for old in (True, False):
        b, page, ce, pe = sat_launch(pw, w, h, old=old)
        try:
            iid, t1 = opened_main(page)
            calc1 = P78.calc(page, iid)
            ok = P79.pyr_save(page, t1, 4200, 4170); settle(page, 500)
            js(page, "()=>satV3Render({force:true})"); settle(page, 400)
            ts = P78.trades(page)
            rk = js(page, "()=>JSON.stringify({r:satV2Risk('main'), c:satV2Caps('main'), pos:satV2MainPos('main','XAUUSD')})")
            m = js(page, MEASURE)
            risk_ids = [t["id"] for t in ts if t["status"] == "open"]
            usd = P79.risk_usd(page, risk_ids)
            f2c = cnt(page, ".lf-pd > [data-f2c-trade]")
            lines = js(page, "()=>[...document.querySelectorAll('.lf-pl')].map(e=>e.innerText.replace(/\\s+/g,' '))")
            head = txt(page, ".lf-held [data-ln3-status]")
            to_today(page)
            today = txt(page, '[data-td3-sat="XAUUSD"]') or ""
            keys = sorted(set(ts[1].keys()) - {"id", "date", "openedAt"}) if len(ts) > 1 else []
            t2 = ts[1] if len(ts) > 1 else {}
            same = {k: (ts[0].get(k) == t2.get(k)) for k in ("sleeve", "macro_state", "size_rule", "driver", "trend_state", "tf", "playbook_version", "plan_bias") if k in t2}
            out["old" if old else "new"] = dict(ok=ok, n=len(ts), rk=rk, usd=usd, m=m, f2c=f2c, lines=lines, head=head, today=today, calc=json.dumps(calc1, sort_keys=True), keys=keys, same=same, ce=ce[:2], pe=pe[:2], ovf=ovf(page))
            if not old and shots:
                to_plan(page); C.shot(page, "td4b-tranche2-390.png", ".lf-held")
                js(page, "()=>{ const d = document.querySelector('.lf-pd'); if(d) d.scrollIntoView({block:'center'}); }"); settle(page, 300)
                page.screenshot(path=os.path.join(C.SHOTS, "td4b-tranche2-390.png"))
                to_today(page); js(page, "()=>{ const e = document.querySelector('[data-td3-panel=\"sat\"]'); if(e) e.scrollIntoView({block:'start'}); }"); settle(page, 500)
                page.screenshot(path=os.path.join(C.SHOTS, "td4b-today-sat-390.png"))
        finally: b.close()
    o, n = out["old"], out["new"]
    check(f"{tag} §5 ไม้สอง (Main): เติมไม้ได้ · มี 2 ไม้ open · หัวแถวแผน 'เข้าแล้ว 2' · มี 2 บรรทัดไม้ใน Plan · แต่ละไม้มีป้าย 'ไม้ 1/3' · 'ไม้ 2/3'", n["ok"] and n["n"] == 2 and n["head"].startswith("เข้าแล้ว 2") and len(n["lines"]) == 2 and "ไม้ 1/3" in n["lines"][0] and "ไม้ 2/3" in n["lines"][1], [n["ok"], n["n"], n["head"], n["lines"]])
    check(f"{tag} §5 Today Satellite นับไม้สอง: Size = 0.16 lot (0.05 + 0.05 Family + 0.06 ไม้สอง) · '×2' (ก่อนแก้ Size 0.1 และไม่มีไม้สอง)", "Size 0.16 lot ×2" in n["today"] and "Size 0.1 lot" in o["today"] and "×" not in o["today"], [n["today"], o["today"]])
    LOG["tranche_old_today"] = o["today"]; LOG["tranche_new_today"] = n["today"]
    check(f"{tag} §5 นับ Risk/ตำแหน่งเหมือนเดิมทุกตัวอักษร (satV2Risk · Caps · MainPos ก่อน = หลังแก้) · Risk รวมสองไม้ ${n['usd']:.0f} = ก่อนแก้ ${o['usd']:.0f}", n["rk"] == o["rk"] and abs(n["usd"] - o["usd"]) < 1e-6 and abs(n["usd"] - 230) < 1e-6 and json.loads(n["rk"])["pos"]["n"] == 2, [n["rk"][:200], o["rk"][:200], n["usd"], o["usd"]])
    check(f"{tag} §5 ขนาดไม้/ตัวเลขแผนเหมือนเดิมทุกตัวอักษร (satV3PlanAcctCalc ก่อน = หลัง)", n["calc"] == o["calc"], [n["calc"][:200], o["calc"][:200]])
    check(f"{tag} §4 ข้อความอัตโนมัติ 'Macro … · Trend … · Driver … · เต็ม' ไม่โผล่ซ้ำที่ไม้สอง (TD4c: ถอดบรรทัดนี้ออกจากแถวทั้งหมด · ก่อนแก้มี 2)", n["f2c"] == 0 and o["f2c"] == 2, [n["f2c"], o["f2c"]])
    check(f"{tag} §4 ค่าที่เก็บในไม้สองไม่เปลี่ยน (คีย์ทั้งชุดเท่าก่อนแก้ · ค่า macro/size/driver/TF เท่าไม้แรก)", n["keys"] == o["keys"] and n["keys"] and all(n["same"].values()), [n["same"], sorted(set(n["keys"]) ^ set(o["keys"]))])
    LOG[f"height_{label}"] = {"before": round(o["m"]["total"], 1), "after": round(n["m"]["total"], 1), "pct": round((1 - n["m"]["total"] / o["m"]["total"]) * 100, 1), "line_before": o["m"]["lines"], "line_after": n["m"]["lines"], "held_before": round(o["m"]["held"], 1), "held_after": round(n["m"]["held"], 1)}
    check(f"{tag} §5 มุมมองกระชับ: ความสูงแถว 'แผน & ไม้ที่ถือ' (หัว + รายการไม้) {o['m']['total']:.0f} → {n['m']['total']:.0f}px (ลด {LOG[f'height_{label}']['pct']}%) ≥ 25%", n["m"]["total"] <= o["m"]["total"] * 0.75, LOG[f"height_{label}"])
    check(f"{tag} §5 แต่ละบรรทัดไม้ไม่เตี้ยกว่าปุ่มกด (≥ 32px) · ปุ่ม ⋯ สูง ≥ 32", all(x >= 32 for x in n["m"]["lines"]), n["m"]["lines"])
    check(f"{tag} {label} ไม่ล้นแนวนอน · ไม่มี console error (ก่อน/หลัง)", n["ovf"] <= 1 and not n["ce"] and not n["pe"], [n["ovf"], n["ce"], n["pe"]])


def plan_shot(pw, w, h, name):
    b, page, ce, pe = sat_launch(pw, w, h)
    try:
        iid, t1 = opened_main(page)
        iid2 = P79.idea(page, sleeve="tactical", entry=4180, sl=4157.5)
        js(page, "()=>satPinToggle('XAUUSD')"); to_plan(page); settle(page, 600)
        js(page, "()=>{ const e = document.querySelector('.lf-held'); if(e) e.scrollIntoView({block:'start'}); }"); settle(page, 400)
        page.screenshot(path=os.path.join(C.SHOTS, name))
        if w == 390:   # ฟอร์มแผนที่กาง (Zone ไม่มีช่องติ๊ก · ไม่มีเพิ่มเติม · MA Align Overlap)
            js(page, "(i)=>{ if(satActiveDraft!==i) ln3ToggleDraft(i); }", iid2); settle(page, 600)
            js(page, "()=>{ const e = document.querySelector('.ln1-form'); if(e) e.scrollIntoView({block:'start'}); }"); settle(page, 400)
            page.screenshot(path=os.path.join(C.SHOTS, "td4b-form-390.png"))
        check(f"[{ENGINE}/{w}px] ภาพ {name} ถ่ายแล้ว · ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 4 Watch ─────────────────────────
def wl_cands(page): return js(page, "()=>Object.keys(tdSettings().candMeta || {})")
def wl_n(page): return js(page, "()=>wlItems.length")
def menu_items(page): return js(page, "()=>[...document.querySelectorAll('.ltMenu [role=menuitem]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")


def watch_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.wl_seed(page, [T.W("AAPL"), T.W("MSFT", note="m"), T.W("PTT.BK", "TH")])
        T.go_watch(page, "wl")
        row = js(page, """()=>{ const r = document.querySelector('[data-ln3-wl2]'); const els = [...r.children].flatMap(c=>c.matches('.wlPills') ? [...c.children] : c.matches('.ln3-wlr') ? [...c.querySelectorAll('button')].filter(x=>x.offsetParent) : [c]);
          const tops = els.map(e=>{ const b = e.getBoundingClientRect(); return Math.round(b.top + b.height/2); }); const hh = r.getBoundingClientRect().height;
          return {n: els.length, spread: Math.max(...tops) - Math.min(...tops), h: Math.round(hh), labels: els.map(e=>e.innerText.trim().slice(0, 18))}; }""")
        LOG[f"wl_row_{label}"] = row
        check(f"{tag} §B6b All|US|TH + Add on candidate + ⋯ อยู่บรรทัดเดียว (กึ่งกลางแนวตั้งต่างกัน ≤ 4px · สูง ≤ 44px)" + (" · Filter ▾ อยู่ในแถวเดียวกัน" if w >= 700 else " · Filter ▾ ย้ายเข้าเมนู ⋯"), row["spread"] <= 4 and row["h"] <= 44, row)
        add_t = txt(page, "[data-wl-addc-btn]") or ""
        check(f"{tag} §B6b ปุ่ม ＋ เปลี่ยนเป็น 'Add on candidate' (ไม่มีปุ่ม ＋ เพิ่มหุ้น/＋ ลัดเข้า Watchlist)", "Add on candidate" in add_t and cnt(page, "[onclick*=wlOpenAdd]") == 0, add_t)
        check(f"{tag} §B6b Export .txt ไม่อยู่บนแถบเครื่องมือแล้ว (อยู่ใน ⋯)", cnt(page, ".ln3-wlr > [data-wl-export]") == 0 and cnt(page, "[data-wl-export]") == 0, cnt(page, "[data-wl-export]"))
        js(page, "()=>document.querySelector('[data-ln3-listmenu]').click()"); settle(page, 250)
        mi = menu_items(page)
        check(f"{tag} §B6b เมนู ⋯ มี Import + Copy list (แทน Export .txt · SET1) จัดกลุ่มด้วยกัน" + (" + Filter" if w < 700 else ""), any("Import" in x for x in mi) and any("Copy list" in x for x in mi) and (w >= 700 or any(x.startswith("Filter") for x in mi)), mi)
        exp0 = js(page, "()=>wlCopyListText()")
        js(page, "()=>{ navigator.clipboard.writeText = t => Promise.resolve(); }")
        js(page, "()=>document.querySelector('.ltMenu [data-wl-copylist]').click()"); settle(page, 300)
        le = js(page, "()=>window.__sdLastCopy || null")
        check(f"{tag} §B6b SET1: Copy list จากเมนู ⋯ แทน Export .txt: ข้อความ = wlCopyListText() (ticker ตามที่แสดง คั่น ', ' · TH = PTT.BK) · ไม่มีไฟล์ .txt", le == exp0 and "PTT.BK" in exp0 and "AAPL" in exp0 and "SET:" not in exp0, [le, exp0])
        if w < 700:
            js(page, "()=>{ document.querySelector('[data-ln3-listmenu]').click(); }"); settle(page, 250)
            js(page, "()=>document.querySelector('[data-flt-menu]').click()"); settle(page, 300)
            check(f"{tag} §B6b Filter ▾ ในเมนู ⋯ เปิดแผงตัวกรองได้ (แถบ Filter เดิมซ่อนบนจอแคบ)", cnt(page, "[data-flt-panel]") == 1, cnt(page, "[data-flt-panel]"))
            js(page, "()=>{ fltOpen = false; renderWatchlist(); }"); settle(page, 200)
        if shots: C.shot(page, f"td4b-watch-{w}.png")
        # Add on candidate
        wl0 = wl_n(page)
        js(page, "()=>document.querySelector('[data-wl-addc-btn]').click()"); settle(page, 300)
        check(f"{tag} §B6b กด Add on candidate → แผงเล็ก [US|TH] + ช่อง Tickers + Add (ไม่ใช่โมดัลเพิ่มเข้า Watchlist)", cnt(page, "[data-wl-addc]") == 1 and cnt(page, "[data-wl-addc] [data-td4-wlmk]") == 2 and cnt(page, "#wlAddOverlay.show") == 0, cnt(page, "[data-wl-addc]"))
        page.fill("[data-wl-addc-t]", "nvda amd NVDA"); settle(page, 100)
        page.locator("[data-wl-addc-go]").click(); settle(page, 700)
        cm = wl_cands(page)
        check(f"{tag} §B6b เพิ่มหลายตัวคั่นช่องว่าง (ซ้ำในชุดเดียวกันตัดออก) → เป็น Candidates (candMeta) ไม่แตะ Watchlist ({wl0} ตัวเดิม)", sorted(cm) == ["AMD", "NVDA"] and wl_n(page) == wl0 and js(page, "()=>wlHas('NVDA')") is False and js(page, "()=>td4AddLog().length") == 2, [cm, wl_n(page)])
        check(f"{tag} §B6b ข้อความหลังเพิ่ม 'Added 2 to Candidates' · ช่องว่างหลังสำเร็จ (ไม่ค้างข้อความเก่า)", (txt(page, "[data-wl-addc-msg]") or "").startswith("Added 2") and js(page, "()=>document.querySelector('[data-wl-addc-t]').value") == "", txt(page, "[data-wl-addc-msg]"))
        page.fill("[data-wl-addc-t]", "NVDA AMD"); page.locator("[data-wl-addc-go]").click(); settle(page, 500)
        check(f"{tag} §B6b ซ้ำ = ไม่เพิ่มซ้ำ · บอก 'already a Candidate' · โควตาวันนี้ไม่ลด", "already a Candidate" in (txt(page, "[data-wl-addc-msg]") or "") and js(page, "()=>td4AddLog().length") == 2, txt(page, "[data-wl-addc-msg]"))
        js(page, "()=>document.querySelector('[data-td4-wlmk=\"TH\"]').click()"); settle(page, 300)
        page.fill("[data-wl-addc-t]", "ptt cpall"); page.locator("[data-wl-addc-go]").click(); settle(page, 500)
        cm2 = wl_cands(page)
        check(f"{tag} §B6b ปุ่ม TH → เก็บเป็น XXX.BK (market TH) ใน Candidates · PTT ที่อยู่ใน Watchlist อยู่แล้ว = ไม่เพิ่มเป็น Candidate", "CPALL" in cm2 and "PTT" not in cm2 and (js(page, "()=>td3Meta().CPALL")) and js(page, "()=>td3Meta().CPALL.market") == "TH" and "already in Watchlist" in (txt(page, "[data-wl-addc-msg]") or ""), [cm2, txt(page, "[data-wl-addc-msg]")])
        js(page, "()=>document.querySelector('[data-td4-wlmk=\"US\"]').click()"); settle(page, 200)
        page.fill("[data-wl-addc-t]", "AA BB CC DD EE FF GG HH II JJ"); page.locator("[data-wl-addc-go]").click(); settle(page, 600)
        n_log = js(page, "()=>td4AddLog().length")
        check(f"{tag} §B6b เพดาน 10 ต่อวัน (รวมที่เพิ่มแล้ว 3): เพิ่มได้อีก 7 · ที่เกินค้างในช่อง + 'Daily limit 10 reached'", n_log == 10 and "Daily limit 10" in (txt(page, "[data-wl-addc-msg]") or "") and js(page, "()=>document.querySelector('[data-wl-addc-t]').value") == "HH II JJ", [n_log, txt(page, "[data-wl-addc-msg]"), js(page, "()=>document.querySelector('[data-wl-addc-t]').value")])
        check(f"{tag} §B6b Watchlist ยังมี {wl0} ตัวเท่าเดิม (ไม่มีตัวใดเข้า Watchlist ตรง ๆ)", wl_n(page) == wl0, wl_n(page))
        # B0 — ทางเข้าตรงถูกปิดแม้เป็น Candidate
        js(page, "()=>wlOpenAdd('NVDA')"); settle(page, 300)
        h3 = txt(page, "[data-td4-usemove]") or ""
        check(f"{tag} B0 ＋/wlOpenAdd กับ Candidate (NVDA) → ข้อความ 'Use Move to Watchlist' + ปุ่ม 'Open move form' · ไม่เปิดโมดัลเพิ่มหุ้น", "Use Move to Watchlist" in h3 and cnt(page, "[data-td4-open-move]") == 1 and cnt(page, "#wlAddOverlay.show") == 0, h3)
        js(page, "()=>{ document.getElementById('wlAddSym').value = 'NVDA'; wlAddSave(); }"); settle(page, 400)
        check(f"{tag} B0 wlAddSave ตรง ๆ กับ Candidate (NVDA) ไม่สร้างเอกสาร Watchlist · แจ้ง 'Use Move to Watchlist'", js(page, "()=>wlHas('NVDA')") is False and "Use Move to Watchlist" in (txt(page, "#wlAddHint") or ""), txt(page, "#wlAddHint"))
        js(page, "()=>{ wlAddClose(); }")
        js(page, "()=>wlOpenAdd('ZZZZ')"); settle(page, 300)
        check(f"{tag} B0 ตัวที่ไม่ใช่ Candidate (ZZZZ) → 'Add it as a Candidate first' · ไม่สร้างเอกสาร", "Add it as a Candidate first" in (txt(page, "[data-td4-noadd]") or "") and js(page, "()=>wlHas('ZZZZ')") is False, txt(page, "[data-td4-noadd]"))
        js(page, "()=>ltSheetClose()")
        js(page, "()=>{ wlOpenEdit('AAPL'); document.getElementById('wlAddNote').value = 'edited'; wlAddSave(); }"); settle(page, 500)
        check(f"{tag} B0 แก้ตัวที่อยู่ใน Watchlist แล้ว (AAPL) ยังบันทึกได้ตามเดิม (อัปเดตเท่านั้น)", (T.wl_doc(page, "AAPL") or {}).get("note") == "edited", T.wl_doc(page, "AAPL"))
        js(page, "()=>wlOpenAdd('NVDA')"); settle(page, 300)
        js(page, "()=>document.querySelector('[data-td4-open-move]').click()"); settle(page, 700)
        on_today = js(page, "()=>activeTab") == "today"
        card = js(page, "()=>{ const e = document.querySelector('[data-td3-cand=\"NVDA\"]'); return e ? [e.dataset.open, !!e.querySelector('[data-td4-pro]')] : null; }")
        check(f"{tag} B0 ปุ่ม 'Open move form' → ไป Today · การ์ด NVDA เปิดฟอร์ม Move to Watchlist (ใบอื่นพับ)", on_today and card == ["1", True] and cnt(page, "[data-td4-pro]") == 1, [on_today, card])
        check(f"{tag} {label} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 1 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def watch_narrow_tests(pw):
    b, page, ce, pe = T.launch(pw, 300, 700)
    try:
        T.wl_seed(page, [T.W("AAPL")]); T.go_watch(page, "wl")
        check(f"[{ENGINE}/300px] Watch 300px: ไม่ล้นแนวนอน (แถวตัวกรองห่อบรรทัดได้) · ไม่มี console error", ovf(page) <= 1 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 5 Today: Cand → WL พับ · Not passed Undo · ไม่มี Other ─────────────────────────
def seed_cands(page):
    T.persist(page, {"candMeta": {"NEW1": dict(T.cm("NEW1", 0, "fresh note"), cand_at="2026-10-01T04:00:00Z"), "OLD1": T.cm("OLD1", 30, "o1"), "OLD2": T.cm("OLD2", 10, "o2"), "OLD3": T.cm("OLD3", 20, "o3")}})


def today_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        seed_cands(page); T.go_today(page)
        st = js(page, "()=>[...document.querySelectorAll('[data-td3-cand]')].map(e=>[e.dataset.td3Cand, e.dataset.open, e.querySelector('.l1').innerText.replace(/\\s+/g,' ').trim()])")
        check(f"{tag} §B6b การ์ด Cand → WL เริ่มพับทั้งหมด (ไม่มีฟอร์มเปิด) · แต่ละใบ 1 บรรทัด 'NEW1 · New today … Screen ›' / 'Candidate 30d … Screen ›'", len(st) == 3 and all(x[1] == "0" for x in st) and cnt(page, "[data-td4-pro]") == 0 and st[0][2].startswith("NEW1 · New today") and st[0][2].endswith("Screen ›") and "Candidate 30d" in st[1][2], st)
        if shots: C.shot(page, "td4b-today-core-390.png", '[data-td3-sec="screen"]')
        page.locator('[data-td3-cand="NEW1"] [data-td4-promote]').click(); settle(page, 250)
        check(f"{tag} §B6b แตะ Screen › เปิดฟอร์มของใบนั้น (ใบเดียว)", cnt(page, '[data-td4-pro="NEW1"]') == 1 and cnt(page, "[data-td4-pro]") == 1, cnt(page, "[data-td4-pro]"))
        page.fill("[data-td4-pro-note]", "typed in NEW1"); T.ev_pass(page); page.locator('[data-td4-star="2"]').click(); settle(page, 150)
        page.locator('[data-td3-cand="OLD1"] [data-td4-promote]').click(); settle(page, 250)
        check(f"{tag} §B6b เปิดใบอื่น (OLD1) → ใบแรกพับ · เปิดได้ทีละใบ", cnt(page, '[data-td4-pro="OLD1"]') == 1 and cnt(page, '[data-td4-pro="NEW1"]') == 0 and cnt(page, "[data-td4-pro]") == 1, [cnt(page, "[data-td4-pro]")])
        page.locator('[data-td3-cand="NEW1"] [data-td4-promote]').click(); settle(page, 250)
        kept = js(page, "()=>({note: document.querySelector('[data-td4-pro-note]').value, tier: csGateOf('NEW1').rs, stars: document.querySelectorAll('[data-td4-star].on').length})")
        check(f"{tag} §B6b กลับมาเปิด NEW1 → ค่าที่พิมพ์ค้างอยู่ครบ (Note · Tier · ดาว) เพราะเก็บในหน่วยความจำ", kept == {"note": "typed in NEW1", "tier": True, "stars": 2}, kept)
        js(page, "()=>{ switchTab('watch'); }"); settle(page, 300); js(page, "()=>{ switchTab('today'); }"); settle(page, 500)
        check(f"{tag} §B6b ออกไปแท็บอื่นแล้วกลับ Today → การ์ดพับหมดอีกครั้ง", cnt(page, "[data-td4-pro]") == 0 and all(x == "0" for x in js(page, "()=>[...document.querySelectorAll('[data-td3-cand]')].map(e=>e.dataset.open)")), cnt(page, "[data-td4-pro]"))
        # Not passed → Undo
        page.locator('[data-td3-cand="OLD3"] [data-td4-promote]').click(); settle(page, 200)
        trk0 = T.trk(page)
        before = js(page, "()=>td3MetaOf('OLD3').screened_at || null")
        page.locator("[data-td4-pro] [data-td3-np]").click(); settle(page, 500)
        row = txt(page, "[data-td4-np]") or ""
        check(f"{tag} §B6b Not passed → แถวยุบเป็น '✕ OLD3 · Not passed · Undo' · ตัวนับขยับ (0/3 → 1/3) · ฟอร์มหาย", row == "✕ OLD3 · Not passed · Undo" and T.trk(page) == "US 1 · TH 0 · 1/3" and trk0 == "US 0 · TH 0 · 0/3" and cnt(page, "[data-td4-pro]") == 0 and js(page, "()=>td3MetaOf('OLD3').screened_at") == "2026-10-01", [row, trk0, T.trk(page)])
        page.locator("[data-td4-npundo]").click(); settle(page, 500)
        after = js(page, "()=>td3MetaOf('OLD3').screened_at || null")
        check(f"{tag} §B6b Undo → screened_at กลับค่าเดิม ({before}) (ไม่มีฟิลด์ค้าง) · ตัวนับ 0/3 · OLD3 กลับเข้าคิว · แถว ✕ หาย", after == before and T.trk(page) == "US 0 · TH 0 · 0/3" and "OLD3" in T.qrows(page) and cnt(page, "[data-td4-np]") == 0, [after, T.trk(page), T.qrows(page)])
        # screened_at เดิมมีค่า (เช่นคัดกรองเมื่อวาน) → Undo คืนค่าเดิมนั้น
        T.persist(page, {"candMeta": dict(js(page, "()=>JSON.parse(JSON.stringify(tdSettings().candMeta))"), OLD1=dict(T.cm("OLD1", 30, "o1"), screened_at="2026-09-30"))}); T.go_today(page)
        page.locator('[data-td3-cand="OLD1"] [data-td4-promote]').click(); settle(page, 200)
        page.locator("[data-td4-pro] [data-td3-np]").click(); settle(page, 400)
        page.locator("[data-td4-npundo]").click(); settle(page, 400)
        check(f"{tag} §B6b Undo คืน screened_at เดิม '2026-09-30' (ไม่ใช่ลบ/ไม่ใช่วันนี้)", js(page, "()=>td3MetaOf('OLD1').screened_at") == "2026-09-30", js(page, "()=>td3MetaOf('OLD1').screened_at"))
        page.locator('[data-td3-cand="NEW1"] [data-td4-promote]').click(); settle(page, 200)
        page.locator("[data-td4-pro] [data-td3-np]").click(); settle(page, 400)
        page.wait_for_timeout(5400)
        check(f"{tag} §B6b ครบ 5 วินาที → ปุ่ม Undo หาย เหลือแถวสรุป '✓ NEW1 · Not passed' (ถาวร) · ตัวนับยัง 1/3", cnt(page, "[data-td4-npundo]") == 0 and "✓ NEW1" in (txt(page, '[data-td3-done="notpassed"]') or "") and T.trk(page) == "US 1 · TH 0 · 1/3", [T.trk(page), txt(page, '[data-td3-done="notpassed"]')])
        # ไม่มี Other
        body = js(page, "()=>document.body.innerText")
        check(f"{tag} Today ไม่มีส่วน 'Other ▸' (ไม่มี details.td3-other · ไม่มีข้อความ 'Other ▸')", cnt(page, "[data-td3-other]") == 0 and "Other ▸" not in body, cnt(page, "[data-td3-other]"))
        reach = js(page, """()=>({settingsRoutine: !!document.getElementById('tdSetSec'), fnGoal: typeof glWrite==='function', fnTasks: typeof glWeeklyPanel==='function', stkRead: typeof stkOpenView==='function', weekPanelTab: !!document.querySelector('[data-td3-tab=\"w\"]')})""")
        LOG["other_reach"] = reach
        check(f"{tag} ของเดิมใน Other ยังไม่ถูกลบจากโค้ด/ข้อมูล: ตั้งค่า Daily routine (Settings) · แท็บ Weekend ของ Today · ฟังก์ชัน Weekly panel/Stock summary ยังอยู่", reach["settingsRoutine"] and reach["fnGoal"] and reach["fnTasks"] and reach["stkRead"] and reach["weekPanelTab"], reach)
        check(f"{tag} {label} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 1 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 6 widths ─────────────────────────
def width_tests(pw):
    for w, h in ((300, 700), (390, 844), (1280, 800), (1440, 900)):
        tag = f"[{ENGINE}/{w}px]"
        b, page, ce, pe = sat_launch(pw, w, h)
        try:
            iid, t1 = opened_main(page); P79.pyr_save(page, t1, 4200, 4170); settle(page, 500)
            P79.idea(page, sleeve="tactical", entry=4180, sl=4157.5)
            js(page, "()=>satPinToggle('BTCUSD')"); to_plan(page); o1 = ovf(page)
            js(page, "()=>{ const i = satIdeasList.find(x=>x.v3 && satV3PlanRowState(x)==='draft'); if(i) ln3ToggleDraft(i.id); }"); settle(page, 500); o2 = ovf(page)
            to_today(page); o3 = ovf(page)
            check(f"{tag} Plan Sat (แถวถือ + ★ + ฟอร์ม) · Today Sat: ไม่ล้นแนวนอน · ไม่มี console error", o1 <= 1 and o2 <= 1 and o3 <= 1 and not ce and not pe, [o1, o2, o3, ce[:2], pe[:2]])
        finally: b.close()
        b, page, ce, pe = T.launch(pw, w, h)
        try:
            T.wl_seed(page, [T.W("AAPL"), T.W("PTT.BK", "TH")]); seed_cands(page)
            T.go_watch(page, "wl"); js(page, "()=>document.querySelector('[data-wl-addc-btn]').click()"); settle(page, 300); o1 = ovf(page)
            js(page, "()=>document.querySelector('[data-ln3-listmenu]').click()"); settle(page, 300); o2 = ovf(page)
            T.go_today(page); page.locator('[data-td3-cand="NEW1"] [data-td4-promote]').click(); settle(page, 300); o3 = ovf(page)
            check(f"{tag} Watch (Add on candidate เปิด · เมนู ⋯) · Today (การ์ด Cand→WL เปิด): ไม่ล้นแนวนอน · ไม่มี console error", o1 <= 1 and o2 <= 1 and o3 <= 1 and not ce and not pe, [o1, o2, o3, ce[:2], pe[:2]])
        finally: b.close()


SECTIONS = {
    "rename": lambda pw: (rename_zone_tests(pw, 390, 844, "390px"), rename_zone_tests(pw, 1440, 900, "1440px")),
    "ctx": lambda pw: (ctx_pin_tests(pw, 1440, 900, "1440px"), ctx_pin_tests(pw, 390, 844, "390px", shots=True)),
    "tranche": lambda pw: (tranche_tests(pw, 390, 844, "390px", shots=True), tranche_tests(pw, 1440, 900, "1440px")),
    "shots": lambda pw: (plan_shot(pw, 1440, 900, "td4b-plan-1440.png"), plan_shot(pw, 390, 844, "td4b-plan-390.png")),
    "watch": lambda pw: (watch_tests(pw, 390, 844, "390px", shots=True), watch_tests(pw, 1440, 900, "1440px", shots=True), watch_narrow_tests(pw)),
    "today": lambda pw: (today_tests(pw, 390, 844, "390px", shots=True), today_tests(pw, 1440, 900, "1440px")),
    "width": width_tests,
}


def main():
    want = os.environ.get("SECT", " ".join(SECTIONS)).split()
    with sync_playwright() as pw:
        for k in want: SECTIONS[k](pw)
    print("LOG " + json.dumps(LOG, ensure_ascii=False))
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
