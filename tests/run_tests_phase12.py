#!/usr/bin/env python3
"""F2d — Playbook view.watch + แถบดำ #ffAction 4 ช่องใหม่ (Regime · ธีมนำ · เพดาน Core · Macro) + ป้ายความสดบนบรรทัดสรุป
ลบ #ffChanges / ffRenderChanges / ffChg* · เก็บ ffChangesData (pure) + prevQuad ใน rrgCompute
ภาพเก็บที่ tests/screenshots/f2d-*.png · รัน: python3 run_tests_phase12.py (mock Firestore + fundflow stub)"""
import json, os, re
import run_tests_phase4 as base
import run_tests_phase11 as p11
from run_tests_phase11 import pbver, seed_pb, iso, txt, norm, no_overflow, shot, fresh
from playwright.sync_api import sync_playwright

ENGINE = base.BROWSER_ENGINE
results = p11.results
check = p11.check
UP, DN = "rgb(110, 231, 160)", "rgb(252, 165, 165)"


def set_ff(page, cur, prev=None, age=1, flip=None):
    """cur/prev = {ratio: bool} · prev None = ไม่มี prev_week · age = วันทำการของ as_of · flip = {ratio: flip_days}"""
    flip = flip or {}
    ratios = {}
    for k, up in cur.items():
        r = {"up": up, "flip_days": flip.get(k, 3), "tf": "D" if k in ("SPHB_SPLV", "RSP_SPY") else "W"}
        if prev is not None and k in prev and prev[k] is not None:
            r["prev_week"] = {"up": prev[k]}
        ratios[k] = r
    asof = page.evaluate("""(n)=>{ for(let i=0;i<40;i++){ const d=new Date(); d.setDate(d.getDate()-i); const s=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
        if(ffBizDaysSince(s)===n) return s; } return null; }""", age)
    page.evaluate("([j])=>{ window.__FF_JSON = j; }", [{"as_of": asof, "ratios": ratios}])
    page.evaluate("() => { ffJsonAt = 0; ffLoadJson(true); }"); page.wait_for_timeout(400)


def no_ff(page):
    page.evaluate("() => { window.__FF_JSON = null; ffJsonAt = 0; ffLoadJson(true); }"); page.wait_for_timeout(400)


def rrg_rows(page, rows):
    page.evaluate("""(rows)=>{ const f = ffState(); f.rrg = {rowsD: rows, rowsW: rows, build: RRG_BUILD, day: rrgToday(), at: new Date().toISOString(), loading:false, err:''}; ffRenderActionBar(); }""", rows)
    page.wait_for_timeout(80)


def row(sym, name, quad, prev=None, dmom=1.0):
    return {"sym": sym, "name": name, "quad": quad, "prevQuad": prev or quad, "dMom": dmom, "dRatio": 0, "ratio": 101, "mom": 101, "days": 3, "off52": -2}


def cellt(page, k, sel=""):
    return txt(page, f'#ffAction [data-ff="{k}"] {sel}'.strip())


def watch_pb(page, w, quarter="2026Q4", savedAt=None, **kw):
    v = pbver(2, savedAt or iso(), quarter=quarter, **kw)
    if w is not None: v["view"]["watch"] = w
    return v


def validate_tests(page, tag):
    def base_obj(**v):
        o = {"schema": "macroPlaybook/v1", "quarter": "2099Q4", "status": "draft", "doc_url": "https://x.example/d",
             "view": {"headline": "h", "thesis": "t", "pillars": [{"id": "P1", "title": "p"}]},
             "assets": {a: {"stance": "none"} for a in ["XAUUSD", "BTC", "BRENT", "US"]}}
        o["view"].update(v); return o
    val = lambda o: page.evaluate("(o)=>Calc.pbValidate(o)", o)
    r = val(base_obj())
    check(f"{tag} pbValidate: ไม่มี view.watch → ไม่ error ไม่เตือน", not r["errors"] and not r["warnings"], json.dumps(r, ensure_ascii=False))
    r = val(base_obj(watch="ดู CPI วันพฤหัส"))
    check(f"{tag} pbValidate: watch เป็นข้อความสั้น → ผ่าน ไม่เตือน (ไม่ใช่ key แปลก)", not r["errors"] and not r["warnings"], json.dumps(r, ensure_ascii=False))
    for bad in (5, ["a"], {"a": 1}, True):
        r = val(base_obj(watch=bad))
        check(f"{tag} pbValidate: watch = {json.dumps(bad)} → error 'view.watch: ต้องเป็นข้อความ'", "view.watch: ต้องเป็นข้อความ" in r["errors"], json.dumps(r, ensure_ascii=False))
    r = val(base_obj(watch="ก" * 140))
    check(f"{tag} pbValidate: watch ยาว 140 → ไม่เตือน", not r["errors"] and not r["warnings"], json.dumps(r, ensure_ascii=False))
    r = val(base_obj(watch="ก" * 201))
    check(f"{tag} pbValidate: watch ยาว 201 → warning (ไม่ใช่ error · บันทึกได้)", not r["errors"] and any("view.watch" in x for x in r["warnings"]), json.dumps(r, ensure_ascii=False))


def pbpanel_tests(page, tag):
    page.evaluate("() => switchTab('flow')"); page.wait_for_timeout(200)
    seed_pb(page, [watch_pb(page, "ดู CPI วันพฤหัส")])
    page.evaluate("() => { pbOpen = true; pbRender(); }"); page.wait_for_timeout(80)
    t = txt(page, "#pbPanel .pbBody")
    ok = page.evaluate("() => { const w=document.querySelector('#pbPanel [data-pb=watch]'), t=document.querySelector('#pbPanel .pbThesis'); return !!w && t.nextElementSibling===w; }")
    check(f"{tag} #pbPanel กาง: [UI2a แก้] กล่อง 'ข้อควรติดตาม' (หัวแยก) + 'ดู CPI วันพฤหัส' ใต้ thesis", ok and "ข้อควรติดตาม" in t and "ดู CPI วันพฤหัส" in t and txt(page, "#pbPanel .pbWatchK") == "ข้อควรติดตาม" and txt(page, "#pbPanel .pbWatchV") == "ดู CPI วันพฤหัส", t)
    seed_pb(page, [watch_pb(page, None)])
    page.evaluate("() => { pbOpen = true; pbRender(); }"); page.wait_for_timeout(80)
    check(f"{tag} #pbPanel กาง: ไม่มี watch → ไม่แสดงข้อควรติดตาม", "ข้อควรติดตาม" not in txt(page, "#pbPanel") and page.locator("#pbPanel [data-pb=watch]").count() == 0)
    page.evaluate("() => { pbOpen = false; pbRender(); }")


def regime_tests(page, tag):
    no_ff(page)
    t = cellt(page, "regime")
    check(f"{tag} Regime: ไม่มี fundflow.json (demo) → 'ACWI/BIL —' 'HYG/IEI —' ไม่มีป้ายเพิ่งพลิก", "ACWI/BIL —" in t and "HYG/IEI —" in t and "เพิ่งพลิก" not in t, t)
    both = {"ACWI_BIL": True, "HYG_IEI": False, "HG_GC": True, "SPHB_SPLV": True, "RSP_SPY": True}
    set_ff(page, both, None, flip={"ACWI_BIL": 3, "HYG_IEI": 1})
    t = cellt(page, "regime")
    col = page.evaluate("() => [...document.querySelectorAll('#ffAction [data-ff=regime] [data-rg]')].map(e=>getComputedStyle(e).color)")
    check(f"{tag} Regime: 'ACWI/BIL ↑ เขียว · 3w' + 'HYG/IEI ↓ แดง · 1w' (ป้ายสีเขียว/แดง)", "ACWI/BIL ↑ เขียว · 3d" in t and "HYG/IEI ↓ แดง · 1d" in t and col == [UP, DN], t + json.dumps(col))
    check(f"{tag} Regime: ไม่มี prev_week → ไม่มีป้ายเพิ่งพลิก · ไม่ error", "เพิ่งพลิก" not in t)
    set_ff(page, both, {"ACWI_BIL": True, "HYG_IEI": True}, flip={"ACWI_BIL": 3, "HYG_IEI": 1})
    flips = page.evaluate("() => [...document.querySelectorAll('#ffAction [data-rg-flip]')].map(e=>e.dataset.rgFlip)")
    check(f"{tag} Regime: HYG/IEI พลิกสัปดาห์นี้ (up ≠ prev_week.up) → ป้าย 'เพิ่งพลิก' เฉพาะ HYG/IEI", flips == ["HYG_IEI"], json.dumps(flips))
    set_ff(page, both, {"ACWI_BIL": False, "HYG_IEI": True})
    flips = page.evaluate("() => [...document.querySelectorAll('#ffAction [data-rg-flip]')].map(e=>e.dataset.rgFlip)")
    check(f"{tag} Regime: พลิกทั้งคู่ → ป้ายเพิ่งพลิก 2 ป้าย", flips == ["ACWI_BIL", "HYG_IEI"], json.dumps(flips))
    set_ff(page, both, {"ACWI_BIL": True, "HYG_IEI": False})
    check(f"{tag} Regime: ไม่พลิก → ไม่มีป้าย", "เพิ่งพลิก" not in cellt(page, "regime"))
    set_ff(page, {"ACWI_BIL": True, "HYG_IEI": True}, None, flip={"ACWI_BIL": 5, "HYG_IEI": 2})
    page.evaluate("() => { ffJson.ratios.ACWI_BIL.flip_days = null; ffRenderActionBar(); }")
    t = cellt(page, "regime")
    check(f"{tag} Regime: flip_days ขาด → 'ACWI/BIL ↑ เขียว' ไม่มีตัวเลข ไม่ error", "ACWI/BIL ↑ เขียว" in t and "ACWI/BIL ↑ เขียว ·" not in t, t)
    set_ff(page, {"ACWI_BIL": True})
    check(f"{tag} Regime: ratio ขาดจากไฟล์ → 'HYG/IEI —' ไม่ error", "HYG/IEI —" in cellt(page, "regime"), cellt(page, "regime"))


def lead_tests(page, tag):
    set_ff(page, {"ACWI_BIL": True, "HYG_IEI": True}, {"ACWI_BIL": True, "HYG_IEI": True})
    rrg_rows(page, [])
    check(f"{tag} ธีมนำ: 0 ธีม → '—' ไม่มีบรรทัดธีมเปลี่ยน", cellt(page, "lead", ".ffActLead") == "—" and page.locator('#ffAction [data-mv]').count() == 0)
    rrg_rows(page, [row("XLK", "Technology", "lead")])
    check(f"{tag} ธีมนำ: 1 ธีม → 'XLK Technology'", cellt(page, "lead", ".ffActLead") == "XLK Technology", cellt(page, "lead", ".ffActLead"))
    rrg_rows(page, [row("XLK", "Technology", "lead", dmom=3), row("XLF", "Financials", "lead", dmom=2), row("XLI", "Industrials", "lead", dmom=1)])
    t = cellt(page, "lead", ".ffActLead")
    check(f"{tag} ธีมนำ: 3 ธีม lead → แสดงสูงสุด 2 (เรียง Δmom)", t == "XLK Technology XLF Financials", t)
    small = page.evaluate("() => { const s=document.querySelector('#ffAction [data-lead=XLK] small'); return s ? getComputedStyle(s).fontSize : ''; }")
    check(f"{tag} ธีมนำ: ชื่อธีมตัวเล็กจาง (เล็กกว่า sym)", small and float(small[:-2]) < page.evaluate("() => parseFloat(getComputedStyle(document.querySelector('#ffAction [data-lead=XLK]')).fontSize)"), small)
    # ธีมเปลี่ยนควอดแรนต์
    rrg_rows(page, [row("XLK", "Technology", "lead")])
    check(f"{tag} ธีมเปลี่ยน: 0 → ไม่แสดงบรรทัด", page.locator('#ffAction [data-mv]').count() == 0)
    rrg_rows(page, [row("XLK", "Technology", "lead"), row("XLE", "Energy", "imp", "lag")])
    t = cellt(page, "lead")
    check(f"{tag} ธีมเปลี่ยน: 1 → '↗ Energy → Improving' ไม่มี +n", "↗ Energy → Improving" in t and page.locator('#ffAction [data-mv=more]').count() == 0, t)
    rrg_rows(page, [row("A", "Alpha", "lead", "imp"), row("B", "Beta", "lag", "weak"), row("C", "Gamma", "imp", "lag"), row("E", "Err", "lag", "lag"), {"sym": "X", "name": "X", "err": "x"}])
    t = cellt(page, "lead")
    n = page.locator('#ffAction [data-mv=theme]').count()
    check(f"{tag} ธีมเปลี่ยน: 3 → แสดง 2 บรรทัด + '+1 ธีม'", n == 2 and txt(page, '#ffAction [data-mv=more]') == "+1 ธีม" and "Gamma" not in t, t)
    no_ff(page)
    rrg_rows(page, [row("A", "Alpha", "lead", "imp")])
    check(f"{tag} ธีมเปลี่ยน: demo (ไม่มี fundflow.json) → ไม่แสดงบรรทัดธีมเปลี่ยน", page.locator('#ffAction [data-mv]').count() == 0)


def cap_tests(page, tag):
    G = {"ACWI_BIL": True, "HYG_IEI": True}
    set_ff(page, G, G)
    t = cellt(page, "cap")
    check(f"{tag} เพดาน: 100% ไม่มีตัวแดง → '100%' + 'ไม่มีตัวแดง' · ไม่มีป้ายสัปดาห์ก่อน · ไม่ warn",
          "100%" in t and "ไม่มีตัวแดง" in t and "สัปดาห์ก่อน" not in t and not page.evaluate("() => document.querySelector('#ffAction [data-ff=cap]').classList.contains('warn')"), t)
    set_ff(page, {"ACWI_BIL": True, "HYG_IEI": False}, G)
    t = cellt(page, "cap")
    warn = page.evaluate("() => document.querySelector('#ffAction [data-ff=cap]').classList.contains('warn')")
    check(f"{tag} เพดาน: HYG/IEI แดง → '75%' + 'HYG/IEI แดง → ลด 25%' + ป้าย 'สัปดาห์ก่อน 100%' + warn",
          "75%" in t and "HYG/IEI แดง → ลด 25%" in t and "สัปดาห์ก่อน 100%" in t and warn, t)
    big = page.evaluate("() => parseFloat(getComputedStyle(document.querySelector('#ffAction [data-ff=cap] .ffActV')).fontSize)")
    small = page.evaluate("() => parseFloat(getComputedStyle(document.querySelector('#ffAction [data-ff=cap] .ffActWhy')).fontSize)")
    check(f"{tag} เพดาน: ค่าตัวใหญ่ · เหตุผลตัวเล็ก", big > small * 1.4, f"{big} vs {small}")
    set_ff(page, {"ACWI_BIL": False, "HYG_IEI": False}, {"ACWI_BIL": False, "HYG_IEI": False})
    t = cellt(page, "cap")
    check(f"{tag} เพดาน: แดงสองตัว → '50%' + 'ACWI/BIL · HYG/IEI แดง → ลด 50%' (capPrev เท่าเดิม ไม่มีป้าย)",
          "50%" in t and "ACWI/BIL · HYG/IEI แดง → ลด 50%" in t and "สัปดาห์ก่อน" not in t, t)
    set_ff(page, {"ACWI_BIL": False, "HYG_IEI": False}, None, age=6)
    t = cellt(page, "cap")
    sm = txt(page, "#ffAction [data-ff=sum]")
    check(f"{tag} เพดาน: stale (6 วันทำการ) → 100% + เหตุผล = ข้อความบรรทัดสรุปเดิม · warn",
          "100%" in t and "ข้อมูลเก่า 6 วันทำการ — ไม่ลดเพดาน (Core 100%)" in t and "ข้อมูลเก่า 6 วันทำการ" in sm and page.evaluate("() => document.querySelector('#ffAction [data-ff=cap]').classList.contains('warn')"), t)
    set_ff(page, {"ACWI_BIL": True})
    t = cellt(page, "cap")
    check(f"{tag} เพดาน: missing (HYG/IEI ขาด) → เหตุผล = ข้อความบรรทัดสรุปเดิม 'HYG/IEI ขาด' · warn",
          "HYG/IEI ขาด" in t and page.evaluate("() => document.querySelector('#ffAction [data-ff=cap]').classList.contains('warn')"), t)
    no_ff(page)
    t = cellt(page, "cap")
    check(f"{tag} เพดาน: demo → '—' ไม่มีป้ายสัปดาห์ก่อน ไม่มีเหตุผล", norm(t.replace("เพดาน Core", "")) == "—" and "สัปดาห์ก่อน" not in t, t)


def macro_tests(page, tag, w):
    page.evaluate("() => switchTab('flow')"); page.wait_for_timeout(150)
    seed_pb(page, [])
    t = cellt(page, "macro")
    check(f"{tag} Macro: ไม่มี active → '—' + 'ยังไม่มี Playbook ใช้จริง' · ไม่มีกล่อง watch/ป้ายใหม่", t.startswith("Macro —") and "ยังไม่มี Playbook ใช้จริง" in t and page.locator("#ffAction [data-mac]").count() == 0, t)
    seed_pb(page, [pbver(1, iso(), status="draft", x="up")])
    check(f"{tag} Macro: มีแต่ร่าง → ถือว่าไม่มี active", "ยังไม่มี Playbook ใช้จริง" in cellt(page, "macro"))
    old = iso(-24 * 21)
    seed_pb(page, [watch_pb(page, None, savedAt=old, x="up", b="up_flat", r="down", u="none")])
    t = cellt(page, "macro")
    check(f"{tag} Macro: active ไม่มี watch → ไม่มีกล่อง 'ข้อควรติดตาม' · savedAt ไม่ใช่สัปดาห์นี้ → ไม่มีป้ายเวอร์ชันใหม่",
          "XAU ▲ · BTC ▲▬ · BR ▼ · US —" in t and "2026Q4 v002" in t and "ข้อควรติดตาม" not in t and "เวอร์ชันใหม่สัปดาห์นี้" not in t, t)
    cols = page.evaluate("() => [...document.querySelectorAll('#ffAction [data-ff=macro] .as')].map(e=>getComputedStyle(e).color)")
    check(f"{tag} Macro: สีตามท่าที (▲ เขียว · ▲▬ เขียว · ▼ แดง · — เทา)", cols[0] == UP and cols[1] == UP and cols[2] == DN and cols[3] not in (UP, DN), json.dumps(cols))
    seed_pb(page, [watch_pb(page, "ดู CPI วันพฤหัส", x="up", b="up_flat", r="down", u="none")])
    t = cellt(page, "macro")
    check(f"{tag} Macro: active + watch → กล่อง 'ข้อควรติดตาม' (หัวแยก) + เนื้อความ + ป้าย 'ใหม่สัปดาห์นี้'", "ข้อควรติดตาม ดู CPI วันพฤหัส" in t and "ใหม่สัปดาห์นี้" in t and "เวอร์ชันใหม่" not in t, t)
    clamp = page.evaluate("() => { const e=document.querySelector('#ffAction [data-mac=watch-tx]'), c=getComputedStyle(e); return [c.webkitLineClamp, c.overflow]; }")
    check(f"{tag} Macro: กล่อง watch ตัดที่ 2 บรรทัด (line-clamp 2)", clamp == ["2", "hidden"], json.dumps(clamp))
    seed_pb(page, [watch_pb(page, "ก" * 300, x="up")])
    h = page.evaluate("() => { const e=document.querySelector('#ffAction [data-mac=watch-tx]'); return [e.getBoundingClientRect().height, parseFloat(getComputedStyle(e).lineHeight)||0, parseFloat(getComputedStyle(e).fontSize)]; }")
    check(f"{tag} Macro: watch ยาวมาก → สูงไม่เกิน ~2 บรรทัด", h[0] <= h[1] * 2 + 1, json.dumps(h))
    # asset ไม่ตัดกลาง
    seed_pb(page, [watch_pb(page, None, x="up", b="up_flat", r="down", u="none")])
    nb = page.evaluate("""() => { const sp=[...document.querySelectorAll('#ffAction [data-ff=macro] .as')];
        return sp.map(e=>({t:e.textContent, ws:getComputedStyle(e).whiteSpace})); }""")
    br = [x for x in nb if "BR" in x["t"] and "▼" in x["t"]]
    check(f"{tag} Macro: 'BR' กับ '▼' อยู่ใน element white-space:nowrap เดียวกัน (ทุก asset ห่อ nowrap)", len(br) == 1 and br[0]["ws"] == "nowrap" and all(x["ws"] == "nowrap" for x in nb) and len(nb) == 4, json.dumps(nb, ensure_ascii=False))
    lines = page.evaluate("""() => { const sp=[...document.querySelectorAll('#ffAction [data-ff=macro] .as')]; return sp.map(e=>e.getClientRects().length); }""")
    check(f"{tag} Macro: แต่ละ asset อยู่บรรทัดเดียว (ไม่ถูกตัดกลาง)", all(n == 1 for n in lines), json.dumps(lines))


def fresh_tests(page, tag):
    G = {"ACWI_BIL": True, "HYG_IEI": True}
    set_ff(page, G, G, age=1)
    f = txt(page, "#ffAction [data-ff=fresh]")
    warn = page.evaluate("() => document.querySelector('#ffAction [data-ff=fresh]').classList.contains('warn')")
    check(f"{tag} ป้ายความสด: สด → '<d MMM> · สด' (จุดเขียวนำหน้า) ไม่ warn", re.fullmatch(r"\d{1,2} \S+ · สด", f) is not None and not warn, f)
    set_ff(page, G, G, age=4)
    f = txt(page, "#ffAction [data-ff=fresh]")
    warn = page.evaluate("() => document.querySelector('#ffAction [data-ff=fresh]').classList.contains('warn')")
    check(f"{tag} ป้ายความสด: เก่า → '… · เก่า 4 วันทำการ' สีเตือน", f.endswith("· เก่า 4 วันทำการ") and warn, f)
    no_ff(page)
    check(f"{tag} ป้ายความสด: demo/ไม่มีไฟล์ → ไม่มีป้าย", page.locator("#ffAction [data-ff=fresh]").count() == 0)
    check(f"{tag} ไม่มีช่อง 'ความสดข้อมูล' แล้ว · ไม่มี #ffChanges / ffRenderChanges / ffChg*",
          "ความสดข้อมูล" not in txt(page, "#ffAction") and page.locator("#ffChanges").count() == 0
          and page.evaluate("() => typeof ffRenderChanges === 'undefined' && typeof ffChgToggle === 'undefined' && typeof ffChgOpen === 'undefined'")
          and "ffChg" not in open(base.DEFAULT_INDEX, encoding="utf-8").read())
    check(f"{tag} ffChangesData (pure) ยังอยู่ · demo = null", page.evaluate("() => typeof ffChangesData === 'function' && ffChangesData() === null"))
    cells = page.evaluate("() => [...document.querySelectorAll('#ffAction .ffActCell')].map(c=>c.dataset.ff)")
    check(f"{tag} แถบดำมี 4 ช่อง Regime · ธีมนำ · เพดาน Core · Macro", sorted(cells) == ["cap", "lead", "macro", "regime"], json.dumps(cells))


def nav_tests(page, tag):
    G = {"ACWI_BIL": True, "HYG_IEI": True}
    set_ff(page, G, G)
    seed_pb(page, [watch_pb(page, None)])
    page.evaluate("() => { window.__scr = []; Element.prototype.scrollIntoView = function(){ window.__scr.push(this.id); }; }")
    for k, want in (("regime", "ffRegime"), ("cap", "ffRegime"), ("lead", "ffThemesPanel"), ("macro", "pbPanel")):
        page.evaluate("() => { window.__scr = []; }")
        page.click(f'#ffAction [data-ff="{k}"]'); page.wait_for_timeout(60)
        got = page.evaluate("() => window.__scr")
        check(f"{tag} แตะช่อง {k} → เลื่อนไป #{want}", got == [want], json.dumps(got))
    check(f"{tag} เป้าหมายเลื่อนมีอยู่จริง (#ffRegime · #ffThemesPanel · #pbPanel)", page.evaluate("() => ['ffRegime','ffThemesPanel','pbPanel'].every(i=>!!document.getElementById(i))"))


def layout_tests(page, tag, w):
    G = {"ACWI_BIL": True, "HYG_IEI": False}
    set_ff(page, G, {"ACWI_BIL": True, "HYG_IEI": True}, flip={"ACWI_BIL": 12, "HYG_IEI": 1})
    seed_pb(page, [watch_pb(page, "ดู CPI วันพฤหัส และผลประชุม Fed ที่จะออกกลางสัปดาห์ ระวังดอลลาร์แข็งกดทอง", x="up", b="up_flat", r="down", u="none")])
    rrg_rows(page, [row("XLK", "Technology", "lead", dmom=3), row("XLF", "Financials", "lead", dmom=2), row("A", "Energy", "imp", "lag"), row("B", "Health Care", "weak", "lead"), row("C", "Utilities", "lag", "weak")])
    pos = page.evaluate("() => Object.fromEntries([...document.querySelectorAll('#ffAction .ffActCell')].map(c=>{ const r=c.getBoundingClientRect(); return [c.dataset.ff, [Math.round(r.left), Math.round(r.top)]]; }))")
    if w > 900:
        ok = len({p[1] for p in pos.values()}) == 1 and pos["regime"][0] < pos["lead"][0] < pos["cap"][0] < pos["macro"][0]
        check(f"{tag} grid 1440: 4 คอลัมน์แถวเดียว ลำดับ Regime · ธีมนำ · เพดาน Core · Macro", ok, json.dumps(pos))
    else:
        ok = (pos["regime"][1] == pos["cap"][1] < pos["lead"][1] == pos["macro"][1] and pos["regime"][0] < pos["cap"][0] and pos["lead"][0] < pos["macro"][0] and pos["regime"][0] == pos["lead"][0])
        check(f"{tag} grid 430: 2×2 บน Regime | เพดาน Core · ล่าง ธีมนำ | Macro", ok, json.dumps(pos))
    cellsov = page.evaluate("() => [...document.querySelectorAll('#ffAction .ffActCell')].filter(c=>c.scrollWidth>c.clientWidth+1).map(c=>c.dataset.ff)")
    check(f"{tag} ไม่มีช่องล้นแนวนอนในแถบดำ", cellsov == [], json.dumps(cellsov))
    no_overflow(page, w, f"{tag} Flow (แถบดำเต็ม)")
    lbl = "1440" if w > 900 else "430"
    page.evaluate("() => window.scrollTo(0,0)")
    page.evaluate("() => { delete Element.prototype.scrollIntoView; }")
    shot(page, f"f2d-{lbl}-active.png", "#ffAction")
    no_ff(page); rrg_rows(page, []); seed_pb(page, [])
    page.wait_for_timeout(150)
    shot(page, f"f2d-{lbl}-nopb.png", "#ffAction")
    shot(page, f"f2d-{lbl}-flow.png", None)
    no_overflow(page, w, f"{tag} Flow (ไม่มี Playbook · demo)")


def style_tests(page, tag, w):
    G = {"ACWI_BIL": True, "HYG_IEI": False}
    set_ff(page, G, {"ACWI_BIL": False, "HYG_IEI": True}, flip={"ACWI_BIL": 12, "HYG_IEI": 1})
    seed_pb(page, [watch_pb(page, "ดู CPI วันพฤหัส และผลประชุม Fed ที่จะออกกลางสัปดาห์ ระวังดอลลาร์แข็งกดทอง " * 3, x="up", b="up_flat", r="down", u="none")])
    rrg_rows(page, [row("XLK", "Technology", "lead"), row("E", "Energy", "imp", "lag"), row("H", "Health Care", "weak", "lead"), row("U", "Utilities", "lag", "weak")])
    ff = page.evaluate("() => [...document.querySelectorAll('#ffAction, #ffAction *')].filter(e=>/mono/i.test(getComputedStyle(e).fontFamily)).length")
    check(f"{tag} แถบดำ: ไม่มี font-family mono ในแถบดำเลย", ff == 0, str(ff))
    rows = page.evaluate("""() => [...document.querySelectorAll('#ffAction [data-ff=regime] .ffActRg')].map(r=>{ const p=r.querySelector('.ffActPill'); const cs=getComputedStyle(p);
        return {ws: cs.whiteSpace, one: p.getClientRects().length===1, nameColor:getComputedStyle(r).color, right: p.getBoundingClientRect().right<=r.getBoundingClientRect().right+1, left: r.getBoundingClientRect().left<p.getBoundingClientRect().left, txt:p.textContent}; })""")
    check(f"{tag} Regime: ป้ายทั้งก้อนอยู่ใน element nowrap เดียว (บรรทัดเดียว) · ชื่อขาวชิดซ้าย ป้ายชิดขวา",
          len(rows) == 2 and all(r["ws"] == "nowrap" and r["one"] and r["right"] and r["nameColor"] == "rgb(255, 255, 255)" for r in rows) and (all(r["left"] for r in rows) if w > 700 else all(not r["left"] for r in rows)), json.dumps(rows, ensure_ascii=False))   # UI-1b: ช่องแคบ (≤700px) ทุกแถวเรียงลงเหมือนกัน (ป้ายใต้ชื่อ ชิดซ้าย) — ดู phase14
    fl = page.evaluate("() => [...document.querySelectorAll('#ffAction [data-rg-flip]')].map(e=>({t:e.textContent, ov:e.scrollWidth>e.parentElement.clientWidth}))")
    check(f"{tag} Regime: ป้าย '<ชื่อ> เพิ่งพลิก' ต่อ ratio ที่พลิก (ACWI/BIL · HYG/IEI) ไม่ล้นช่อง",
          [x["t"] for x in fl] == ["ACWI/BIL เพิ่งพลิก", "HYG/IEI เพิ่งพลิก"] and not any(x["ov"] for x in fl), json.dumps(fl, ensure_ascii=False))
    mv = page.evaluate("() => [...document.querySelectorAll('#ffAction [data-mv=theme]')].map(e=>e.textContent)")
    check(f"{tag} ธีมเปลี่ยน: ลูกศรถูกทาง (→Improving/Leading = ↗ · →Weakening/Lagging = ↘)", mv == ["↗ Energy → Improving", "↘ Health Care → Weakening"], json.dumps(mv, ensure_ascii=False))
    big = page.evaluate("() => parseFloat(getComputedStyle(document.querySelector('#ffAction [data-ff=cap] .ffActV')).fontSize)")
    exp = page.evaluate('() => parseFloat(getComputedStyle(document.documentElement).fontSize)') * (1.6 if w <= 420 else 1.9)
    check(f"{tag} เพดาน: ตัวเลขหลักใหญ่ ({'~1.6rem' if w <= 420 else '~1.9rem'}) หนา", abs(big - exp) < 1, str(big))
    mins = page.evaluate("""() => { const out=[]; document.querySelectorAll('#ffAction *').forEach(e=>{ if(e.children.length===0 && e.textContent.trim()){ const f=parseFloat(getComputedStyle(e).fontSize); if(f<11.5) out.push([e.className,f]); } }); return out; }""")
    check(f"{tag} ตัวเล็กสุดในแถบดำ ≥ ~12px (0.72rem)", not mins, json.dumps(mins))
    wt = page.evaluate("""() => { const w=document.querySelector('#ffAction [data-mac=watch]'), t=w.querySelector('[data-mac=watch-tx]'), ct=getComputedStyle(t), cw=getComputedStyle(w);
        const lh=parseFloat(ct.lineHeight); return {txH:t.getBoundingClientRect().height, lh, txPad: ct.paddingTop+ct.paddingBottom, wrapPad: cw.paddingTop, max: ct.maxHeight, head: w.querySelector('b').textContent}; }""")
    check(f"{tag} กล่อง watch: element line-clamp ไม่มี padding · สูง ≤ 2 บรรทัดพอดี · padding อยู่ที่ wrapper · หัว 'ข้อควรติดตาม' แยก",
          wt["txH"] <= wt["lh"] * 2 + 1 and wt["txPad"] == "0px0px" and wt["wrapPad"] != "0px" and wt["head"] == "ข้อควรติดตาม", json.dumps(wt, ensure_ascii=False))
    fr = page.evaluate("() => { const f=document.querySelector('#ffAction [data-ff=fresh]'); return [!!f.querySelector('i'), getComputedStyle(f.querySelector('i')).backgroundColor]; }")
    check(f"{tag} ป้ายความสด: มีจุดเขียวนำหน้า", fr[0] and fr[1] == "rgb(74, 222, 128)", json.dumps(fr))
    cell = page.evaluate("() => { const c=document.querySelector('#ffAction .ffActCell'); const s=getComputedStyle(c); return [s.backgroundColor, s.paddingTop, getComputedStyle(document.querySelector('#ffAction .ffActGrid')).gap]; }")
    check(f"{tag} ช่อง: พื้น #262A31 · padding 12px · gap 10px", cell == ["rgb(38, 42, 49)", "12px", "10px"], json.dumps(cell))


def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        page.evaluate("() => switchTab('flow')"); page.wait_for_timeout(250)
        validate_tests(page, tag)
        pbpanel_tests(page, tag)
        regime_tests(page, tag)
        lead_tests(page, tag)
        cap_tests(page, tag)
        macro_tests(page, tag, w)
        fresh_tests(page, tag)
        nav_tests(page, tag)
        style_tests(page, tag, w)
        layout_tests(page, tag, w)
        check(f"{tag} ไม่มีการเขียน macroPlaybook (set/add/update/delete) · ไม่แตะ collection 'macro' ตลอดการทดสอบ",
              page.evaluate("() => window.__pbW.length === 0 && window.__macroTouch.length === 0"), page.evaluate("() => JSON.stringify([window.__pbW, window.__macroTouch])"))
    finally:
        check(f"{tag} console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
        browser.close()


def main():
    with sync_playwright() as pw:
        ui_tests(pw, 1440, 900, "1440px")
        ui_tests(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 12 / F2d) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
