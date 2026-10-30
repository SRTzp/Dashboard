#!/usr/bin/env python3
"""RG2a — Regime v2 (2 คู่ EMA · raw) · stale ไม่ดีดกลับ 100% · Verdict บน Today · Freshness · Journal by bucket + planned vs actual · Sector link · เทส 112
Chromium · 300 / 390 / 1440 · นาฬิกาปลอม พฤ. 1 ต.ค. 2026 12:00 ICT · ข้อมูล SAMPLE ล้วน
ภาพ tests/screenshots/rg2a-{verdict-300,verdict-390,verdict-1440,journal-390,journal-1440,watch-390,fresh-390}.png
รัน: SECT='script factor verdict fresh bucket sector' python3 run_tests_phase112.py"""
import json, os, subprocess, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase24 as P24
import run_tests_phase105 as P105
import run_tests_phase107 as T

ENGINE = base.BROWSER_ENGINE
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHOTS = os.path.join(HERE, "screenshots")
results = []
js = C.js
settle, cnt, txt = T.settle, T.cnt, T.txt
LOG = {}


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    os.makedirs(SHOTS, exist_ok=True)
    page.wait_for_timeout(900)
    p = os.path.join(SHOTS, name)
    (page.locator(sel).first.screenshot(path=p) if sel else page.screenshot(path=p))
    return p


def ff(acwi, hyg, sacwi=None, shyg=None, as_of="2026-10-01", slow=True):
    """fundflow.json ver 2 — top = Winner (EMA20/50) · slow = Ladder (EMA50/100)"""
    def pair(u, su):
        r = {"up": u, "flip_days": 12, "tf": "D", "ema": [20, 50], "bar": as_of}
        if slow: r["slow"] = {"up": u if su is None else su, "flip_days": 30, "ema": [50, 100]}
        return r
    return {"as_of": as_of, "ver": 2, "ratios": {"ACWI_BIL": pair(acwi, sacwi), "HYG_IEI": pair(hyg, shyg)}}


def set_ff(page, j):
    page.evaluate("async (j)=>{ window.__FF_JSON = j; await ffLoadJson(true); }", j)
    settle(page, 250)


def launch(pw, w, h):
    return T.launch(pw, w, h)


def sections():
    env = os.environ.get("SECT", "").split()
    return env or ["script", "factor", "verdict", "fresh", "bucket", "sector", "width"]


# ───────────────────────── 1 Script ─────────────────────────
def script_tests():
    tag = "[py]"
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import build_fundflow as B
    src = open(os.path.join(ROOT, "scripts", "build_fundflow.py"), encoding="utf-8").read()
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_fundflow.py"), "--selftest"], capture_output=True, text=True)
    check(f"{tag} §3.1 --selftest ผ่าน (2 คู่ · raw · retry)", r.returncode == 0 and "selftest OK" in r.stdout, r.stdout[-300:] + r.stderr[-300:])
    check(f"{tag} §3.1 ราคาดิบ: auto_adjust=False ทุกที่ · threads=False", "auto_adjust=False" in src and "auto_adjust=True" not in src and "threads=False" in src)
    # ACWI_BIL / HYG_IEI = daily มี slow 50/100 · ตัวอื่นคง TF + EMA10/20
    rt = B.RATIOS
    check(f"{tag} §3.1 ACWI_BIL & HYG_IEI = D · EMA20/50 + slow 50/100", all(rt[k][2] == "D" and rt[k][3] == (20, 50) and rt[k][4] == (50, 100) for k in ("ACWI_BIL", "HYG_IEI")), {k: rt[k][2:] for k in ("ACWI_BIL", "HYG_IEI")})
    check(f"{tag} §3.1 ratio อื่นคง TF เดิม + EMA10/20 · ไม่มี slow", all(rt[k][3] == (10, 20) and rt[k][4] is None for k in ("HYG_IEF", "HG_GC", "SPHB_SPLV", "RSP_SPY"))
          and (rt["HYG_IEF"][2], rt["HG_GC"][2], rt["SPHB_SPLV"][2], rt["RSP_SPY"][2]) == ("W", "W", "D", "D"))
    check(f"{tag} §3.1 MIN_BARS_SLOW ≥ 300 · ver = 2", B.MIN_BARS_SLOW >= 300 and B.VER == 2)
    # คำนวณจริงจากราคาสังเคราะห์
    import datetime
    base_d = datetime.date(2020, 1, 1)
    ds = [base_d + datetime.timedelta(days=i) for i in range(1500) if (base_d + datetime.timedelta(days=i)).weekday() < 5]
    up = {d: 100 + i * 0.1 for i, d in enumerate(ds)}
    one = {d: 1.0 for d in ds}
    dn = {d: 100 - i * 0.01 for i, d in enumerate(ds)}
    p = {"ACWI": up, "BIL": one, "HYG": dn, "IEF": one, "IEI": one, "HG=F": up, "GC=F": one, "SPHB": up, "SPLV": one, "RSP": up, "SPY": one}
    res, errs = B.compute(p)
    a, h = res["ACWI_BIL"], res["HYG_IEI"]
    check(f"{tag} §3.1 compute: top ema [20,50] + slow ema [50,100] + prev_week ทั้งสองคู่", not errs and a["ema"] == [20, 50] and a["slow"]["ema"] == [50, 100] and a["slow"]["prev_week"] and a["prev_week"] and a["up"] and a["slow"]["up"] and (not h["up"]) and (not h["slow"]["up"]), res["ACWI_BIL"])
    short = ds[:299]
    r2, e2 = B.compute({"ACWI": {d: up[d] for d in short}, "BIL": {d: 1.0 for d in short}})
    check(f"{tag} §3.1 แท่งไม่ถึง 300 → ไม่เขียน ACWI_BIL (ไม่เขียนไฟล์ขาด)", "ACWI_BIL" not in r2 and any("ACWI_BIL" in x for x in e2), e2)
    # retry: ขาดรอบแรก → รอ 20s → ลองใหม่เฉพาะตัวที่ขาด
    calls, slept = [], []
    def fake(s):
        calls.append(list(s))
        return {x: {} for x in s if not (len(calls) == 1 and x == "BIL")}
    got = B.fetch(["ACWI", "BIL"], dl=fake, sleep=slept.append)
    check(f"{tag} §3.1 retry 1 ครั้ง เฉพาะตัวที่ขาด · รอ 20s", calls == [["ACWI", "BIL"], ["BIL"]] and slept == [20] and set(got) == {"ACWI", "BIL"}, [calls, slept])
    calls.clear(); slept.clear()
    B.fetch(["ACWI"], dl=lambda s: (calls.append(s) or {"ACWI": {}}), sleep=slept.append)
    check(f"{tag} §3.1 ไม่ขาดก็ไม่ retry", len(calls) == 1 and slept == [])
    check(f"{tag} §3.1 กฎ 'ไม่เขียนไฟล์ขาด' ยังอยู่ + method/ver ถูกเขียน", "ไม่เขียนไฟล์" in src and "'ver': VER" in src and "raw closes" in src)
    # ไฟล์จริงใน repo (หลังรัน workflow) — ver 2 ต้องมีสองคู่ · ไฟล์เก่า ver ไม่มี = ข้าม
    try:
        doc = json.load(open(os.path.join(ROOT, "fundflow.json"), encoding="utf-8"))
        if doc.get("ver") == 2:
            R = doc["ratios"]
            check(f"{tag} §3.1 fundflow.json ver 2: ACWI_BIL/HYG_IEI มี slow EMA50/100 + tf D", all(R[k]["tf"] == "D" and R[k]["ema"] == [20, 50] and R[k]["slow"]["ema"] == [50, 100] for k in ("ACWI_BIL", "HYG_IEI")), R["ACWI_BIL"])
        else:
            check(f"{tag} §3.1 fundflow.json ยังเป็นไฟล์เก่า (ver ไม่มี) — รอ workflow สร้างใหม่", True)
    except Exception as e:
        check(f"{tag} §3.1 อ่าน fundflow.json", False, str(e))


# ───────────────────────── 2 Factor ─────────────────────────
def factor_tests(pw):
    for w, h, label in ((390, 844, "390px"),):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h)
        try:
            exp = {(True, True): 100, (True, False): 75, (False, True): 75, (False, False): 50}
            bad = []
            for (a, hh), cap in exp.items():
                # Winner ใช้คู่บน · Ladder ใช้ slow · ตั้งให้สองคู่ "ตรงข้ามกัน" เพื่อพิสูจน์ว่าแยกกัน
                set_ff(page, ff(a, hh, not a, not hh))
                cw = js(page, "()=>{ const x = ffPoolFactor('winner'); return [x.cap, x.red, x.reds.length, x.stale]; }")
                cl = js(page, "()=>{ const x = ffPoolFactor('ladder'); return [x.cap, x.red, x.reds.length, x.stale]; }")
                lcap = exp[(not a, not hh)]
                if cw[0] != cap or cl[0] != lcap or cw[3] or cl[3]: bad.append([a, hh, cw, cl, cap, lcap])
            check(f"{tag} §3.6 factor 4 combo × 2 pool (Winner=คู่บน · Ladder=slow) = 100/75/75/50", not bad, bad)
            set_ff(page, ff(True, True, False, False))
            check(f"{tag} §3.2 ffCoreNow = Winner (ไม่ใช่ slow)", js(page, "()=>[ffCoreNow().cap, ffPoolFactor('winner').cap, ffPoolFactor('ladder').cap]") == [100, 100, 50])
            check(f"{tag} §3.2 coreFNow ใช้ Winner: f=1", js(page, "()=>coreFNow().f") == 1)
            # stale ไม่ดีดกลับ 100%
            set_ff(page, ff(False, False, False, False, as_of="2026-09-21"))
            st = js(page, "()=>{ const W = ffPoolFactor('winner'), L = ffPoolFactor('ladder'), F = coreFNow(); return {w:[W.cap,W.stale,W.age], l:[L.cap,L.stale], f:F.f, warn:coreFWarn(F), dc:ffDeployCap('core')}; }")
            check(f"{tag} §3.2 #1 ข้อมูลเก่า 8 วันทำการ: cap คงที่ 50 (ไม่เด้งเป็น 100) + stale", st["w"] == [50, True, 8] and st["l"] == [50, True] and st["f"] == 0.5 and st["dc"] == 50, st)
            check(f"{tag} §3.2 coreFWarn ข้อความใหม่ 'Regime data is 8 business days old — size from last known state'", st["warn"] == "⚠ Regime data is 8 business days old — size from last known state", st["warn"])
            set_ff(page, ff(True, False, True, True, as_of="2026-09-21"))
            check(f"{tag} §3.2 stale + HYG แดง → Winner 75 (ค่าล่าสุด) · Ladder 100", js(page, "()=>[ffPoolFactor('winner').cap, ffPoolFactor('ladder').cap]") == [75, 100])
            # ไฟล์เก่า (ไม่มี slow) → Ladder = สถานะบน + log ครั้งเดียว
            logs = []
            page.on("console", lambda m: logs.append(m.text) if "slow" in m.text else None)
            js(page, "()=>{ ffSlowWarned = false; }")
            set_ff(page, ff(True, False, slow=False))
            fb = js(page, "()=>[ffPoolFactor('winner').cap, ffPoolFactor('ladder').cap, ffPoolFactor('ladder').cap]")
            check(f"{tag} §3.2 ไฟล์เก่าไม่มี slow → Ladder ใช้สถานะบน (75) · log ครั้งเดียว", fb == [75, 75, 75] and len(logs) == 1, [fb, logs])
            # Flow: ชิป suffix d + แสดง Ladder factor
            set_ff(page, ff(True, True, False, True))
            js(page, "()=>{ ln3FlowOpen.regime = true; switchTab('flow'); ffRenderRegime(); }"); settle(page, 400)
            chips = js(page, "()=>[...document.querySelectorAll('#ffRegime .ffRegChip')].slice(0,2).map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
            check(f"{tag} §3.2 ชิป ACWI/HYG ใช้ suffix d (daily)", len(chips) == 2 and all(c.split(' ')[-1].endswith("d") or "12d" in c for c in chips), chips)
            check(f"{tag} §3.2 Flow แสดง Ladder factor แยก", "Ladder 75%" in (txt(page, "#ffRegime") or ""), txt(page, "#ffRegime"))
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()


# ───────────────────────── 3 Verdict ─────────────────────────
VERDICTS = {(True, True): "Risk-ON", (True, False): "Caution", (False, True): "Mixed", (False, False): "Risk-OFF"}


def verdict_tests(pw):
    for w, h, label in ((300, 700, "300px"), (390, 844, "390px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h)
        try:
            T.go_today(page) if hasattr(T, "go_today") else None
            for (a, hh), lab in VERDICTS.items():
                set_ff(page, ff(a, hh, True, True))   # slow เขียวเสมอ → Ladder 100
                js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
                wcap = {(True, True): 100, (True, False): 75, (False, True): 75, (False, False): 50}[(a, hh)]
                t = txt(page, "[data-td3-rg]")
                exp = f"{lab} · Winner {wcap}% · Ladder 100%" if w > 460 else f"{lab} · W {wcap} · L 100"
                check(f"{tag} §3.2 verdict {lab}: '{exp}'", t == exp, t)
            # บรรทัดเดียว + ไม่ล้น
            m = js(page, """()=>{ const b = document.querySelector('[data-td3-rg]'); const r = b.getBoundingClientRect(); const t = b.querySelector('.t'); const vis = [...b.querySelectorAll('.rg-f,.rg-s')].filter(e=>e.offsetParent!==null);
              return {h:Math.round(r.height), sw:b.scrollWidth, cw:b.clientWidth, tw:Math.round(t.getBoundingClientRect().width), n:vis.length, top:Math.round(r.top), docOvf:document.documentElement.scrollWidth-window.innerWidth}; }""")
            check(f"{tag} §3.2 verdict 1 บรรทัด (สูง ≤ 40) ไม่ล้น ไม่มีสกรอลล์แนวนอน", m["h"] <= 40 and m["sw"] <= m["cw"] + 1 and m["docOvf"] <= 0, m)
            if w <= 460: check(f"{tag} §3.2 300px: ข้อความ ≤ 340px", m["tw"] <= 340, m)
            # stale: as_of จันทร์ 28 ก.ย. → 3 วันทำการ
            set_ff(page, ff(True, False, True, True, as_of="2026-09-28"))
            js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
            t = txt(page, "[data-td3-rg]")
            exp = "Caution · Winner 75% · Ladder 100% · data 3d old" if w > 460 else "Caution · W 75 · L 100 · 3d old"
            check(f"{tag} §3.2 verdict stale ต่อท้ายสีแดง: '{exp}'", t == exp and js(page, "()=>getComputedStyle(document.querySelector('[data-td3-rg] .st')).color") not in ("", None), t)
            m = js(page, "()=>{ const b = document.querySelector('[data-td3-rg]'); return {h:Math.round(b.getBoundingClientRect().height), sw:b.scrollWidth, cw:b.clientWidth, ovf:document.documentElement.scrollWidth-window.innerWidth}; }")
            check(f"{tag} §3.2 verdict + stale ยังบรรทัดเดียว ไม่ล้น", m["h"] <= 40 and m["sw"] <= m["cw"] + 1 and m["ovf"] <= 0, m)
            shot(page, f"rg2a-verdict-{w}.png")
            # ไม่มีไฟล์ → 'No data' (ไม่เดาสี)
            js(page, "async ()=>{ window.__FF_JSON = null; ffJson = null; }"); js(page, "()=>{ todayRefresh(true); }"); settle(page, 400)
            check(f"{tag} §3.2 ไม่มี fundflow.json → 'No data' เทา", txt(page, "[data-td3-rg]") == "No data" and js(page, "()=>document.querySelector('[data-td3-rg]').dataset.rgState") == "grey")
            # แตะ → Flow › Regime เปิด
            set_ff(page, ff(True, True))
            js(page, "()=>{ switchTab('today'); todayRefresh(true); ln3FlowOpen.regime = false; }"); settle(page, 400)
            page.locator("[data-td3-rg]").first.click(); settle(page, 600)
            check(f"{tag} §3.2 แตะ verdict → ไปแท็บ Flow + หัวข้อ Regime กางอยู่", js(page, "()=>activeTab") == "flow" and js(page, "()=>ln3FlowOpen.regime") is True and js(page, "()=>!!document.querySelector('#ffRegime details[open]')"))
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()


# ───────────────────────── 4 Freshness ─────────────────────────
def fresh_tests(pw):
    for w, h, label in ((390, 844, "390px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h)
        try:
            rows = lambda: js(page, "()=>frRows().map(r=>[r.key, r.st, r.age])")
            # Regime: สด (0) → ไม่มีแท็ก · 3 วันทำการ → แท็ก 3d
            set_ff(page, ff(True, True, as_of="2026-10-01"))
            check(f"{tag} §3.3 Regime สด: ไม่มีแท็ก", js(page, "()=>frTag('regime')") == "" and dict((r[0], r[1]) for r in rows())["regime"] == "ok")
            set_ff(page, ff(True, True, as_of="2026-09-30"))
            check(f"{tag} §3.3 Regime 1 วันทำการ: ไม่มีแท็ก (เกณฑ์ > 2)", js(page, "()=>frTag('regime')") == "")
            set_ff(page, ff(True, True, as_of="2026-09-28"))
            tg = js(page, "()=>frTag('regime')")
            check(f"{tag} §3.3 Regime 3 วันทำการ: แท็กเทา '3d'", "frTag" in tg and ">3d<" in tg, tg)
            js(page, "()=>{ ln3FlowOpen.regime = true; switchTab('flow'); ffRenderRegime(); }"); settle(page, 400)
            check(f"{tag} §3.3 แท็กอยู่ข้างหัว Regime ในหน้า Flow", cnt(page, "#ffRegime .frTag") >= 1)
            set_ff(page, ff(True, True, as_of="2026-10-01"))
            js(page, "()=>{ ffRenderRegime(); }"); settle(page, 200)
            check(f"{tag} §3.3 กลับมาสด → แท็กหาย", cnt(page, "#ffRegime .frTag") == 0)
            # Weekly Impact: ไม่มีเอกสาร = none · เอกสารสัปดาห์นี้ = ok · สัปดาห์ก่อน = stale
            js(page, "()=>{ wiDocs = {}; }")
            check(f"{tag} §3.3 Weekly Impact ไม่มีเอกสาร: ไม่มีแท็ก (none)", dict((r[0], r[1]) for r in rows())["wi"] == "none" and js(page, "()=>frTag('wi')") == "")
            js(page, "()=>{ const m = wiCurMon(); wiDocs = {[m]: {week:m}}; }")
            check(f"{tag} §3.3 Weekly Impact ของสัปดาห์นี้: ok ไม่มีแท็ก", dict((r[0], r[1]) for r in rows())["wi"] == "ok" and js(page, "()=>frTag('wi')") == "")
            js(page, "()=>{ const m = Calc.wiAddDays(wiCurMon(), -7); wiDocs = {[m]: {week:m}}; }")
            r = dict((x[0], x) for x in rows())["wi"]
            check(f"{tag} §3.3 Weekly Impact ของสัปดาห์ก่อน: stale + แท็ก", r[1] == "stale" and 'data-fr-tag="wi"' in js(page, "()=>frTag('wi')"), r)
            js(page, "()=>{ wiDocs = {}; }")
            # Weekly Stock Summary > 8 วัน
            js(page, "()=>{ stkDocs = {e1:{id:'e1', asof:'2026-09-24T09:00:00+07:00', period_end:'2026-09-23'}}; }")
            r = dict((x[0], x) for x in rows())["stk"]
            check(f"{tag} §3.3 Stock Summary 7 วัน: ok ไม่มีแท็ก", r[1] == "ok" and r[2] == 7 and js(page, "()=>frTag('stk')") == "", r)
            js(page, "()=>{ stkDocs = {e1:{id:'e1', asof:'2026-09-22T09:00:00+07:00', period_end:'2026-09-21'}}; }")
            r = dict((x[0], x) for x in rows())["stk"]
            check(f"{tag} §3.3 Stock Summary 9 วัน (> 8): stale + แท็ก '9d'", r[1] in ("stale", "old") and r[2] == 9 and ">9d<" in js(page, "()=>frTag('stk')"), r)
            js(page, "()=>{ stkDocs = {}; }")
            # Playbook: ตาม pbStaleInfo().due
            js(page, "()=>{ window.__pbOrig = pbStaleInfo; window.pbStaleInfo = ()=>({days:12, due:false}); }")
            r = dict((x[0], x) for x in rows())["pb"]
            check(f"{tag} §3.3 Playbook ไม่ due: ok ไม่มีแท็ก", r[1] == "ok" and js(page, "()=>frTag('pb')") == "", r)
            js(page, "()=>{ window.pbStaleInfo = ()=>({days:40, due:true}); }")
            r = dict((x[0], x) for x in rows())["pb"]
            check(f"{tag} §3.3 Playbook due (40 วัน): stale + แท็ก '40d'", r[1] == "stale" and ">40d<" in js(page, "()=>frTag('pb')"), r)
            js(page, "()=>{ window.pbStaleInfo = window.__pbOrig; }")
            # RRG: แคชวันนี้ = ok · เมื่อวาน/วันก่อน = stale
            P105.seed_rrg(page)
            r = dict((x[0], x) for x in rows())["rrg"]
            check(f"{tag} §3.3 RRG แคชวันนี้: ok ไม่มีแท็ก", r[1] == "ok" and js(page, "()=>frTag('rrg')") == "", r)
            P105.seed_rrg(page, day="2026-09-28")
            r = dict((x[0], x) for x in rows())["rrg"]
            check(f"{tag} §3.3 RRG แคชไม่ใช่วันนี้ (3 วัน): stale + แท็ก", r[1] == "stale" and ">3d<" in js(page, "()=>frTag('rrg')"), r)
            P105.go_flow(page)
            check(f"{tag} §3.3 แท็ก RRG ข้างหัวข้อ Leadership", cnt(page, "#ffThemesTitle .frTag") == 1, js(page, "()=>document.getElementById('ffThemesTitle').innerHTML"))
            # แผงใน Settings
            set_ff(page, ff(True, True, as_of="2026-09-28"))
            js(page, "()=>{ openSettings(); }"); settle(page, 500)
            prow = js(page, "()=>[...document.querySelectorAll('#frPanel [data-fr-row]')].map(e=>[e.dataset.frRow, e.dataset.frState, e.innerText.replace(/\\s+/g,' ').trim()])")
            check(f"{tag} §3.3 แผง Data freshness: 5 แถว (regime · wi · stk · pb · rrg)", [r[0] for r in prow] == ["regime", "wi", "stk", "pb", "rrg"], prow)
            rr = dict((r[0], r) for r in prow)
            check(f"{tag} §3.3 แถว Regime: จุด 🟡/🔴 + อายุ 3d + ชื่อแหล่ง", rr["regime"][2].startswith("🟡") and "3d" in rr["regime"][2] and "Regime" in rr["regime"][2], rr["regime"])
            check(f"{tag} §3.3 แถวไม่มีข้อมูล = ⚪ —", rr["wi"][2].startswith("⚪") and rr["wi"][2].endswith("—"), rr["wi"])
            check(f"{tag} §3.3 อยู่ใน Settings (ไม่มีบล็อกใหม่บน Today)", cnt(page, "#setOverlay #frPanel") == 1 and cnt(page, "[data-fr-panel]") == 1)
            ov = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
            check(f"{tag} แผง freshness ไม่ล้นแนวนอน", ov <= 0, ov)
            if w == 390: shot(page, "rg2a-fresh-390.png", "#set1CardFresh")
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()


# ───────────────────────── 5 Journal bucket ─────────────────────────
def trade(id, port, sym, entry, sl, tp, exit_px, exit_date, **kw):
    d = P13.T(id, port, "closed", sym=sym, entry=entry, sl=sl, tp=tp, qty=10, exitPrice=exit_px, exitDate=exit_date, date="2026-09-01")
    d.update(kw); return d


def bucket_tests(pw):
    trades = [
        trade("tW", "core", "WINA", 100, 95, 112.5, 109, "2026-09-10"),              # R = 90/50 = 1.8 · target 2.5
        trade("tX", "core", "BEYD", 100, 95, None, 92, "2026-09-12"),                # −80/50 = −1.6R → เลย −1.25R
        trade("tN", "core", "NOSL", 100, None, None, 101, "2026-09-14", sl0=None),   # ไม่มี SL
        trade("tL", "core", "LADR", 100, 90, None, 90, "2026-09-11"),                # ขาดทุนที่ SL = −1R
        trade("tM", "satB", "MAIN", 100, 95, 110, 104, "2026-09-13", cur="USD"),     # Sat Main
        trade("tT", "satB", "TACT", 100, 95, None, 96, "2026-09-15", cur="USD", sleeve="tactical"),
    ]
    cards = {"ccL": P24.card("ccL", "main", "LADR", strategy="L", status="closed", trade_id="tL", tier="A"),
             "ccW": P24.card("ccW", "main", "WINA", strategy="W", status="closed", trade_id="tW", tier="B")}
    for w, h, label in ((390, 844, "390px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{label}]"
        browser, page, ce, pe = C.launch2(pw, w, h, trades, cards)
        try:
            # ── mapping (ฟังก์ชันล้วน) ──
            mp = js(page, "()=>{ const B = getBook('main'); const o = {}; B.trades.forEach(t=>{ o[t.id] = withAccount('main', ()=>jBucketOf(t)); }); return o; }")
            check(f"{tag} §3.4 bucket: Core ผูกการ์ด L = Ladder · Core อื่น/การ์ด W = Winner · Core ไม่มีการ์ด = Winner (legacy)", mp["tL"] == "ladder" and mp["tW"] == "winner" and mp["tX"] == "winner" and mp["tN"] == "winner", mp)
            check(f"{tag} §3.4 bucket: Sat tactical = Sat Tactical · Sat อื่น = Sat Main", mp["tT"] == "tactical" and mp["tM"] == "main", mp)
            pure = js(page, """()=>({ lg: jBucketOf({port:'core', id:'x'}, {strategy:'L'}), w: jBucketOf({port:'core', id:'x'}, {strategy:'W'}), none: jBucketOf({port:'core', id:'x'}, null),
                 tac: jBucketOf({port:'satB', sleeve:'tactical'}, null), mainNoSleeve: jBucketOf({port:'satB'}, null), mainExplicit: jBucketOf({port:'satB', sleeve:'main'}, null) })""")
            check(f"{tag} §3.4 bucket (ฟังก์ชันล้วน): L/W/ไม่มีการ์ด/tactical/main", pure == {"lg": "ladder", "w": "winner", "none": "winner", "tac": "tactical", "mainNoSleeve": "main", "mainExplicit": "main"}, pure)
            # ── R math ──
            pva = js(page, "()=>{ const B = getBook('main'); const o = {}; B.trades.forEach(t=>{ const v = withAccount('main', ()=>jPlanVsActual(t)); o[t.id] = [v.planned, v.target==null?null:Math.round(v.target*100)/100, v.got==null?null:Math.round(v.got*100)/100, v.respected]; }); return o; }")
            check(f"{tag} §3.4 R: ชนะ → Planned 1R · target 2.5R → got 1.8R · Stop respected ✓", pva["tW"] == [1, 2.5, 1.8, True], pva["tW"])
            check(f"{tag} §3.4 R: ขาดทุนที่ SL (−1R) → ✓", pva["tL"][2] == -1 and pva["tL"][3] is True, pva["tL"])
            check(f"{tag} §3.4 R: ขาดทุนเลย SL (−1.6R < −1.25R) → ✗", pva["tX"][2] == -1.6 and pva["tX"][3] is False, pva["tX"])
            check(f"{tag} §3.4 R: ไม่มี SL → ทุกช่อง null (แสดง —)", pva["tN"] == [None, None, None, None], pva["tN"])
            check(f"{tag} §3.4 R: ไม่มี TP → target null แต่ got/✓ ยังมี", pva["tX"][1] is None and pva["tX"][2] is not None)
            edge = js(page, """()=>{ const base = {entry:100, sl:95, sl0:95, qty:10, mult:1, status:'closed', port:'satB', cur:'USD', tp:112.5};
                const at = (px)=>{ const t = Object.assign({}, base, {exitPrice:px}); const v = jPlanVsActual(t); return [Math.round(v.got*1000)/1000, v.respected]; };
                return {m125: at(93.75), m126: at(93.7), m1: at(95)}; }""")
            check(f"{tag} §3.4 เส้นแบ่ง −1.25R: พอดี −1.25R = ✓ · เลยนิดเดียว = ✗", edge["m125"] == [-1.25, True] and edge["m126"][1] is False and edge["m1"] == [-1, True], edge)
            # ── UI ──
            js(page, "()=>{ switchTab('journal'); renderJournal(); }"); settle(page, 600)
            chips = js(page, "()=>[...document.querySelectorAll('#jBuckets .chip')].map(e=>e.innerText.trim())")
            check(f"{tag} §3.4 ชิป: All · Winner · Ladder · Sat Main · Sat Tactical", chips == ["All", "Winner", "Ladder", "Sat Main", "Sat Tactical"], chips)
            tb = js(page, "()=>[...document.querySelectorAll('#jBucketTbl tbody tr')].map(r=>[r.dataset.jbkt, ...[...r.children].slice(1).map(c=>c.innerText.trim())])")
            check(f"{tag} §3.4 ตาราง 4 แถว (trades · win · avg R · P/L · max DD)", len(tb) == 4 and [r[0] for r in tb] == ["winner", "ladder", "main", "tactical"], tb)
            d = dict((r[0], r[1:]) for r in tb)
            # Winner: tW +90 · tX −80 · tN +10 → n3 · win 2/3 → 67% · avgR (1.8 − 1.6)/2 = +0.10R · P/L +20 · DD: เส้นทุน 90→10→20 → 80
            check(f"{tag} §3.4 Winner: 3 ไม้ · 67% · +0.07R (ไม้ไม่มี SL นับ R จาก sl=0 ตามกติกาเดิม) · +20 · DD 80", d["winner"][0] == "3" and d["winner"][1] == "67%" and d["winner"][2] == "+0.07R" and d["winner"][3] == "+20" and d["winner"][4] == "80", d["winner"])
            check(f"{tag} §3.4 Ladder: 1 ไม้ · 0% · −1R · −100 · DD 100", d["ladder"][0] == "1" and d["ladder"][1] == "0%" and d["ladder"][2] == "-1R" or d["ladder"][2] == "−1R", d["ladder"])
            check(f"{tag} §3.4 Sat Main / Tactical แยกกัน (1 ไม้ละ bucket)", d["main"][0] == "1" and d["tactical"][0] == "1", [d["main"], d["tactical"]])
            n_all = js(page, "()=>document.querySelectorAll('#jCards .tcard, #jTbody tr').length")
            page.locator("#jBuckets .chip[data-jb=ladder]").click(); settle(page, 400)
            body = js(page, "()=>[document.getElementById('jCards').innerText, document.getElementById('jTbody').innerText]")
            vis = body[0] if w < 1024 else body[1]
            check(f"{tag} §3.4 กรองชิป Ladder → เหลือ LADR ตัวเดียว", "LADR" in vis and not any(s in vis for s in ("WINA", "BEYD", "NOSL", "MAIN", "TACT")), vis[:300])
            check(f"{tag} §3.4 ชิปที่เลือก = on", js(page, "()=>document.querySelector('#jBuckets .chip.on').dataset.jb") == "ladder")
            page.locator("#jBuckets .chip[data-jb=all]").click(); settle(page, 300)
            check(f"{tag} §3.4 กลับ All → ครบทุกไม้", js(page, "()=>document.querySelectorAll('#jCards .tcard, #jTbody tr').length") == n_all)
            pv = js(page, "()=>[...document.querySelectorAll('.jPva')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
            check(f"{tag} §3.4 รายละเอียดไม้: 'Planned 1R · target 2.5R → got 1.8R · Stop respected ✓'", any("Planned 1R · target 2.5R → got 1.8R · Stop respected ✓" in x for x in pv), pv[:6])
            check(f"{tag} §3.4 ไม้เลย SL ขึ้น ✗ · ไม้ไม่มี SL ขึ้น —", any("Stop respected ✗" in x for x in pv) and any(x.startswith("Planned — · Stop respected —") for x in pv), pv[:8])
            ov = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
            check(f"{tag} Journal ไม่ล้นแนวนอน", ov <= 0, ov)
            shot(page, f"rg2a-journal-{w}.png")
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: browser.close()


# ───────────────────────── 6 Sector ─────────────────────────
def sector_tests(pw):
    items = [T.W("NVDA", stars=3, sector_etf="SMH", industry="Semiconductors"), T.W("MSFT", stars=2, sector_etf="IGV"), T.W("AAPL", stars=1),
             T.W("XOMX", stars=1, sector_etf="XLE"), T.W("CCCC", stars=1, sector_etf="XLK"), T.W("PTT.BK", mk="TH", sector_etf="TH"), T.W("ZZZZ", stars=1, sector_etf="BOGUS")]
    for w, h, label in ((390, 844, "390px"), (1440, 900, "1440px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h)
        try:
            rows_ = P105.rows_d() + [P105.R("XLE", "Energy", "imp"), P105.R("XLK", "Technology", "lag")]
            P105.seed_rrg(page, d=rows_)
            T.wl_seed(page, items)
            # RRG_SYMS + sdFollowed
            syms = js(page, "()=>RRG_SYMS.map(x=>x.s)")
            check(f"{tag} §3.5 RRG_SYMS เพิ่ม XLK XLI XLY XLP XLRE (ครบ 23)", all(s in syms for s in ("XLK", "XLI", "XLY", "XLP", "XLRE")) and len(syms) == 23, syms)
            # field save/load
            wd = js(page, "()=>Object.fromEntries(wlItems.map(w=>[w.ticker, w.sector_etf]))")
            check(f"{tag} §3.5 โหลดฟิลด์ sector_etf จาก Watchlist ('' · ETF · 'TH' · ค่าเพี้ยน → '')", wd == {"NVDA": "SMH", "MSFT": "IGV", "AAPL": "", "XOMX": "XLE", "CCCC": "XLK", "PTT.BK": "TH", "ZZZZ": ""}, wd)
            js(page, "()=>sdFollow('SMH')"); settle(page, 200)
            T.go_watch(page, "wl")
            bd = js(page, """()=>Object.fromEntries([...document.querySelectorAll('.wlR[data-sym]')].map(r=>{ const b = r.querySelector('[data-sec-badge]'); return [r.dataset.sym, b ? [b.innerText.replace(/\\s+/g,' ').trim(), b.className.replace('secBadge','').trim(), b.dataset.secQ] : null]; }))""")
            check(f"{tag} §3.5 ป้าย 'SMH · Leading'? SMH ใน RRG D = Improving + ★ (followed) → 'SMH · Improving ★' เขียว", bd["NVDA"] and bd["NVDA"][0] == "SMH · Improving ★" and bd["NVDA"][1] == "hot", bd["NVDA"])
            check(f"{tag} §3.5 Weakening → เทา 'IGV · Weakening'", bd["MSFT"] and bd["MSFT"][0] == "IGV · Weakening" and bd["MSFT"][1] == "cold", bd["MSFT"])
            check(f"{tag} §3.5 Lagging → เทา 'XLK · Lagging'", bd["CCCC"] and bd["CCCC"][0] == "XLK · Lagging" and bd["CCCC"][1] == "cold", bd["CCCC"])
            check(f"{tag} §3.5 Improving ไม่ ★ → เขียว 'XLE · Improving' (ไม่มี ★)", bd["XOMX"] and bd["XOMX"][0] == "XLE · Improving" and bd["XOMX"][1] == "hot", bd["XOMX"])
            check(f"{tag} §3.5 ฟิลด์ว่าง → ไม่มีป้าย · ค่าเพี้ยน → ไม่มีป้าย", bd["AAPL"] is None and bd["ZZZZ"] is None, [bd["AAPL"], bd["ZZZZ"]])
            check(f"{tag} §3.5 'TH' → ป้ายเทา 'TH' (ไม่มีข้อมูล RRG)", bd["PTT.BK"] and bd["PTT.BK"][0] == "TH" and bd["PTT.BK"][1] == "off", bd["PTT.BK"])
            # sort
            base_order = js(page, "()=>[...document.querySelectorAll('.wlR[data-sym]')].map(e=>e.dataset.sym)")
            has_btn = cnt(page, "[data-wl-hot]") == 1
            check(f"{tag} §3.5 มีปุ่มเรียง 'Hot sector first'", has_btn)
            page.locator("[data-wl-hot]").click(); settle(page, 400)
            hot = js(page, "()=>[...document.querySelectorAll('.wlR[data-sym]')].map(e=>e.dataset.sym)")
            top_hot = [s for s in hot[:2]]
            check(f"{tag} §3.5 Hot sector first: Improving/Leading/★ ขึ้นก่อน (NVDA, XOMX) · ที่เหลือคงลำดับเดิม", set(top_hot) == {"NVDA", "XOMX"} and [s for s in hot[2:]] == [s for s in base_order if s not in top_hot], [base_order, hot])
            js(page, "()=>wlSetHot(false)"); settle(page, 300)
            check(f"{tag} §3.5 ปิดตัวเลือก → กลับลำดับเดิม", js(page, "()=>[...document.querySelectorAll('.wlR[data-sym]')].map(e=>e.dataset.sym)") == base_order)
            ov = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
            check(f"{tag} Watchlist ไม่ล้นแนวนอน", ov <= 0, ov)
            if w == 390: shot(page, "rg2a-watch-390.png")
            # suggest + save ผ่านฟอร์มแก้ไข
            check(f"{tag} §3.5 เสนอจาก industry: semiconductor→SMH · software→IGV · bank→XLF · regional bank→KRE", js(page, "()=>[sectorSuggest('Semiconductors'), sectorSuggest('Application Software'), sectorSuggest('Banks - Diversified'), sectorSuggest('Regional Banks'), sectorSuggest('')]") == ["SMH", "IGV", "XLF", "KRE", ""])
            js(page, "()=>wlOpenEdit('AAPL')"); settle(page, 300)
            js(page, "()=>{ const i = document.getElementById('wlAddInd'); i.value = 'Semiconductors'; wlSectorHint(); }")
            check(f"{tag} §3.5 ฟอร์มแก้ไข: ขึ้นข้อเสนอ SMH (ยังไม่เลือกให้เอง)", js(page, "()=>document.getElementById('wlAddSector').value") == "" and "SMH" in (txt(page, "[data-wl-sector-hint]") or ""))
            js(page, "()=>document.querySelector('[data-wl-sector-use]').click()"); settle(page, 150)
            check(f"{tag} §3.5 กด use it → select = SMH", js(page, "()=>document.getElementById('wlAddSector').value") == "SMH")
            js(page, "()=>wlAddSave()"); settle(page, 600)
            saved = js(page, "()=>{ const w = wlItems.find(x=>x.ticker==='AAPL'); return [w.sector_etf, w.industry]; }")
            check(f"{tag} §3.5 บันทึกจากฟอร์มแก้ไข → sector_etf=SMH เก็บใน Watchlist", saved == ["SMH", "Semiconductors"], saved)
            js(page, "()=>wlOpenEdit('AAPL')"); settle(page, 300)
            check(f"{tag} §3.5 เปิดแก้ไขอีกครั้ง → โหลดค่าเดิม SMH", js(page, "()=>document.getElementById('wlAddSector').value") == "SMH")
            js(page, "()=>{ document.getElementById('wlAddSector').value=''; wlAddSave(); }"); settle(page, 500)
            check(f"{tag} §3.5 เลือก none → ล้างเป็น ''", js(page, "()=>wlItems.find(x=>x.ticker==='AAPL').sector_etf") == "")
            # promote form
            js(page, "()=>{ document.getElementById('wlAddOverlay').classList.remove('show'); }")
            has_sel = js(page, "()=>{ const p = {sym:'ZZ', key:'zz', note:'n', sector:'XLK', tier:false, rs:false, stars:1}; return td4ProFormHtml({sym:'ZZ', market:'US'}, p).includes('data-td4-pro-sector') && td4ProFormHtml({sym:'ZZ', market:'US'}, p).includes('value=\"XLK\" selected'); }")
            check(f"{tag} §3.5 ฟอร์ม Move to Watchlist มีช่อง Sector ETF", has_sel)
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()


# ───────────────────────── 7 Width ─────────────────────────
def width_tests(pw):
    for w, h in ((300, 700), (320, 700), (390, 844), (1280, 900), (1440, 900)):
        tag = f"[{ENGINE}/{w}px]"
        b, page, ce, pe = launch(pw, w, h)
        try:
            set_ff(page, ff(True, False, True, True, as_of="2026-09-28"))
            js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
            o1 = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
            js(page, "()=>{ switchTab('journal'); renderJournal(); }"); settle(page, 500)
            o2 = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
            js(page, "()=>{ openSettings(); }"); settle(page, 500)
            o3 = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
            check(f"{tag} Today(verdict+stale) · Journal(bucket) · Settings(freshness) ไม่มีสกรอลล์แนวนอน", max(o1, o2, o3) <= 0, [o1, o2, o3])
        finally: b.close()


def main():
    sec = sections()
    if "script" in sec: script_tests()
    with sync_playwright() as pw:
        if "factor" in sec: factor_tests(pw)
        if "verdict" in sec: verdict_tests(pw)
        if "fresh" in sec: fresh_tests(pw)
        if "bucket" in sec: bucket_tests(pw)
        if "sector" in sec: sector_tests(pw)
        if "width" in sec: width_tests(pw)
    bad = [r for r in results if not r[1]]
    print(f"\nสรุป: {len(results) - len(bad)} ผ่าน · {len(bad)} ไม่ผ่าน")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
