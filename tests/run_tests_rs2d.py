#!/usr/bin/env python3
"""RS2d — Screen presets editable: Edit rules sheet (live count · custom tag · Reset to default · validation) · saved to settings + localStorage · Today b/d/e follow the custom Leaders rule.
Run: python3 tests/run_tests_rs2d.py   (RS2D_SHOTS=1 writes docs/screenshots/rs2d-*.png)"""
import os, sys
from playwright.sync_api import sync_playwright
import rs2a_common as C
from re1d_common import js, check, results

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")
DEF = {"leaders": {"rs12Min": 80, "near": 15}, "emerging": {"m3Min": 90, "m1Min": 90, "rs12Max": 85}, "pullback": {"rs12Min": 85, "m3Min": 80, "m1Max": 60, "near": 15}}
N = "()=>rs2View().length"
PR = "()=>{ const P = rs2Presets(), o = {}; Object.keys(P).forEach(k=>{ const x = Object.assign({}, P[k]); delete x.name; o[k] = x; }); return o; }"
LINES = "()=>[...document.querySelectorAll('[data-rs2-chg]')].map(r=>r.innerText.replace(/\\s+/g,' ').replace(/ Open ›$/,'').trim())"


def shot(page, name):
    if os.environ.get("RS2D_SHOTS") and page.viewport_size["width"] > 1000:
        os.makedirs(SHOTS, exist_ok=True); page.screenshot(path=os.path.join(SHOTS, "rs2d-%s.png" % name))


def setv(page, f, v):
    page.fill(f'[data-rs2ed-in="{f}"]', v); page.wait_for_timeout(120)


def edit(pw, w, h):
    tag = "[%s]" % w
    b, page, pe, ce = C.open_screen(pw, w, h)
    try:
        js(page, "()=>{ localStorage.removeItem('dash.rs2Presets'); }")
        n0 = js(page, N)
        check(f"{tag} 1 default Leaders = {n0} matches, no custom tag, rule line has Edit rules", n0 > 20 and not js(page, "()=>!!document.querySelector('[data-rs2-ctag],[data-rs2-ctag-rule]')") and js(page, "()=>!!document.querySelector('[data-rs2-edit]')") or w < 600, n0)
        if w < 600:
            page.click("[data-rs2-dots]"); page.wait_for_timeout(200)
            check(f"{tag} 1 phone: Edit rules is in the ⋯ menu", js(page, "()=>!!document.querySelector('[data-rs2-pm-edit]')"))
            page.click("[data-rs2-pm-edit]")
        else:
            page.click("[data-rs2-edit]")
        page.wait_for_timeout(300)
        check(f"{tag} 2 sheet: chips Leaders · Emerging · Pullback, two labelled inputs for Leaders", js(page, "()=>[...document.querySelectorAll('[data-rs2ed-chip]')].map(x=>x.innerText.trim()).join('|')") == "Leaders|Emerging|Pullback" and js(page, "()=>[...document.querySelectorAll('.rs2ed-pr label')].map(x=>x.innerText).join('|')") == "12M RS at least|Within this % of the 52-week high")
        check(f"{tag} 2 hints show the range · Default line · count 'Now: N match'", js(page, "()=>[...document.querySelectorAll('[data-rs2ed-hint]')].map(x=>x.innerText).join('|')") == "0–99|1–50" and "Default: 12M ≥ 80 · within 15% of high" in js(page, "()=>document.querySelector('[data-rs2ed-default]').innerText") and f"{n0} match" in js(page, "()=>document.querySelector('[data-rs2ed-count]').innerText"))
        check(f"{tag} 2 Reset is quiet/disabled while at default · Save enabled", js(page, "()=>document.querySelector('[data-rs2ed-reset]').disabled && !document.querySelector('[data-rs2ed-save]').disabled"))
        shot(page, "edit-sheet")
        setv(page, "rs12Min", "90")
        t = js(page, "()=>document.querySelector('[data-rs2ed-count]').innerText")
        c90 = js(page, "()=>rs2EdCount({rs12Min:90, near:15})")
        check(f"{tag} 3 live count: 'Now: {c90} match · was {n0} with the default'", c90 < n0 and f"Now: {c90} match" in t and f"was {n0} with the default" in t, t)
        check(f"{tag} 3 typing keeps focus (no re-render)", js(page, "()=>document.activeElement && document.activeElement.dataset.rs2edIn === 'rs12Min'"))
        for bad in ["abc", "100", "-1", "8.5"]:
            setv(page, "rs12Min", bad)
            check(f"{tag} 4 invalid '{bad}' → amber hint + Save disabled", js(page, "()=>document.querySelector('[data-rs2ed-save]').disabled && document.querySelector('[data-rs2ed-hint=rs12Min]').classList.contains('bad') && /Whole number 0–99/.test(document.querySelector('[data-rs2ed-hint=rs12Min]').innerText)"))
        setv(page, "rs12Min", "90"); setv(page, "near", "0")
        check(f"{tag} 4 % out of range (0 · needs 1–50) blocks Save", js(page, "()=>document.querySelector('[data-rs2ed-save]').disabled"))
        setv(page, "near", "51")
        check(f"{tag} 4 51 blocks Save too", js(page, "()=>document.querySelector('[data-rs2ed-save]').disabled"))
        setv(page, "near", "")
        check(f"{tag} 4 empty = default (Save enabled; presets unchanged until saved)", js(page, "()=>!document.querySelector('[data-rs2ed-save]').disabled") and js(page, PR) == DEF)
        setv(page, "near", "15")
        page.click("[data-rs2ed-chip=emerging]"); page.wait_for_timeout(150)
        check(f"{tag} 2 Emerging inputs: 3M at least · 1M at least · 12M under", js(page, "()=>[...document.querySelectorAll('.rs2ed-pr label')].map(x=>x.innerText).join('|')") == "3M RS at least|1M RS at least|12M RS under")
        page.click("[data-rs2ed-chip=pullback]"); page.wait_for_timeout(150)
        check(f"{tag} 2 Pullback inputs: 12M at least · 3M at least · 1M under · % from high", js(page, "()=>[...document.querySelectorAll('.rs2ed-pr label')].map(x=>x.innerText).join('|')") == "12M RS at least|3M RS at least|1M RS under|Within this % of the 52-week high")
        check(f"{tag} 3 Leaders chip shows 'custom' (unsaved draft) · Pullback does not", js(page, "()=>!!document.querySelector('[data-rs2ed-chip=leaders] .rs2-ct') && !document.querySelector('[data-rs2ed-chip=pullback] .rs2-ct')"))
        page.click("[data-rs2ed-cancel]"); page.wait_for_timeout(200)
        check(f"{tag} 3 Cancel closes the sheet and saves nothing", js(page, "()=>!document.getElementById('rs2Edit')") and js(page, PR) == DEF and js(page, "()=>localStorage.getItem('dash.rs2Presets')") is None)
        # save
        if w < 600:
            page.click("[data-rs2-dots]"); page.click("[data-rs2-pm-edit]")
        else:
            page.click("[data-rs2-edit]")
        page.wait_for_timeout(250); setv(page, "rs12Min", "90")
        page.click("[data-rs2ed-save]"); page.wait_for_timeout(500)
        n1 = js(page, N)
        check(f"{tag} 5 Save closes the sheet and changes the match count ({n0} → {n1})", js(page, "()=>!document.getElementById('rs2Edit')") and n1 == c90 and n1 < n0, [n0, n1, c90])
        pr = js(page, PR)
        check(f"{tag} 5 saved: only Leaders changed; localStorage mirror holds just the override", pr["leaders"]["rs12Min"] == 90 and pr["leaders"]["near"] == 15 and pr["emerging"] == DEF["emerging"] and pr["pullback"] == DEF["pullback"] and js(page, "()=>localStorage.getItem('dash.rs2Presets')") == '{"leaders":{"rs12Min":90}}', js(page, "()=>localStorage.getItem('dash.rs2Presets')"))
        check(f"{tag} 5 also written to the user's settings (settings.rs2Presets → syncs)", js(page, "()=>JSON.stringify(tdSettings().rs2Presets)") == '{"leaders":{"rs12Min":90}}', js(page, "()=>JSON.stringify(tdSettings().rs2Presets)"))
        check(f"{tag} 5 'custom' appears once — on the rule line only, never on the preset chips", js(page, "()=>!!document.querySelector('[data-rs2-ctag-rule]') && !document.querySelector('[data-rs2-preset] [data-rs2-ctag]')") or w < 600)
        if w >= 600: check(f"{tag} 5 rule line reads the new numbers", "RS ≥ 90" in js(page, "()=>document.querySelector('[data-rs2-note]').innerText") and "custom" in js(page, "()=>document.querySelector('[data-rs2-note]').innerText"), js(page, "()=>document.querySelector('[data-rs2-note]').innerText"))
        shot(page, "custom-tag")
        # other device cleared in settings ({}) beats a stale mirror
        js(page, "()=>{ const B = getBook(tdHome()); B.settings.rs2Presets = {}; }")
        check(f"{tag} 6 an empty settings object (a Reset on another device) wins over a stale mirror", js(page, PR) == DEF)
        js(page, "()=>{ const B = getBook(tdHome()); B.settings.rs2Presets = {leaders:{rs12Min:90}}; }")
        # reset
        js(page, "()=>{ switchTab('watch'); wlSetView('screen'); }"); page.wait_for_timeout(500)
        if w < 600:
            page.click("[data-rs2-dots]"); page.click("[data-rs2-pm-edit]")
        else:
            page.click("[data-rs2-edit]")
        page.wait_for_timeout(250)
        check(f"{tag} 7 sheet reopens with the saved value (90) and Reset to default enabled", js(page, "()=>document.querySelector('[data-rs2ed-in=rs12Min]').value") == "90" and js(page, "()=>!document.querySelector('[data-rs2ed-reset]').disabled"))
        page.click("[data-rs2ed-reset]"); page.wait_for_timeout(200)
        check(f"{tag} 7 Reset to default puts the ORIGINAL numbers back (80 · 15) in the draft", js(page, "()=>[...document.querySelectorAll('.rs2ed-in')].map(i=>i.value).join('|')") == "80|15" and js(page, "()=>document.querySelector('[data-rs2ed-reset]').disabled"))
        page.click("[data-rs2ed-save]"); page.wait_for_timeout(500)
        check(f"{tag} 7 Save after Reset: exact defaults, no custom tag, overrides removed", js(page, PR) == DEF and js(page, N) == n0 and js(page, "()=>!document.querySelector('[data-rs2-ctag],[data-rs2-ctag-rule]')") and js(page, "()=>localStorage.getItem('dash.rs2Presets')") == "{}" and js(page, "()=>JSON.stringify(tdSettings().rs2Presets)") == "{}", js(page, PR))
        # scenario: custom value typed equal to the default is not 'custom'
        page.click("[data-rs2-edit]") if w >= 600 else (page.click("[data-rs2-dots]"), page.click("[data-rs2-pm-edit]"))
        page.wait_for_timeout(250); setv(page, "rs12Min", "80"); page.click("[data-rs2ed-save]"); page.wait_for_timeout(300)
        check(f"{tag} 7 typing the default value is not 'custom'", js(page, "()=>!rs2Custom('leaders') && localStorage.getItem('dash.rs2Presets') === '{}'"))
        # esc closes
        page.click("[data-rs2-edit]") if w >= 600 else (page.click("[data-rs2-dots]"), page.click("[data-rs2-pm-edit]"))
        page.wait_for_timeout(250); page.keyboard.press("Escape"); page.wait_for_timeout(200)
        check(f"{tag} 8 Escape closes the sheet", js(page, "()=>!document.getElementById('rs2Edit')"))
        page.click("[data-rs2-edit]") if w >= 600 else (page.click("[data-rs2-dots]"), page.click("[data-rs2-pm-edit]"))
        page.wait_for_timeout(250)
        o = js(page, "()=>({sw:document.documentElement.scrollWidth - innerWidth, b:(()=>{const r=document.querySelector('.rs2ed-b').getBoundingClientRect(); return r.left >= -1 && r.right <= innerWidth + 1 && r.top >= -1 && r.bottom <= innerHeight + 1})()})")
        check(f"{tag} 8 sheet fits the viewport, no horizontal overflow", o["sw"] <= 0 and o["b"], o)
        # persists after reload (the mock book is blank after a reload, so this reads the localStorage mirror; on a real device settings are re-read first)
        page.click("[data-rs2ed-cancel]") if False else page.keyboard.press("Escape")
        js(page, "()=>{ localStorage.setItem('dash.rs2Presets', JSON.stringify({leaders:{rs12Min:90}})); }")
        page.reload(); page.wait_for_timeout(1200)
        check(f"{tag} 6 persists after reload (read path: settings → mirror)", js(page, PR)["leaders"]["rs12Min"] == 90 and js(page, PR)["emerging"] == DEF["emerging"], js(page, PR))
        check(f"{tag} page errors none", not pe, pe[:2])
    finally:
        b.close()


def ytoday(pw, w, h):
    tag = "[%s]" % w
    rows = C.rows()
    prev = {"CRDO": [85, -0.05, 76, 82], "HOOD": [92, -0.30, 80, 85], "APP": [96, -0.05, 87, 90], "PB0": [90, -0.10, 40, 82], "ZETA": [95, -0.10, 90, 92], "PLTR": [95, -0.05, 85, 88], "GE": [91, -0.06, 82, 88], "NVDA": [99, 0.0, 90, 95], "RKLB": [90, -0.05, 81, 87]}
    for r in rows:
        if r["t"] not in prev and r["r"] >= 90: prev[r["t"]] = [r["r"], r["o"], r["m1"], r["m3"]]
    CH = {"asOf": "2026-11-19", "prevAsOf": "2026-11-18", "items": [{"sym": "APP", "k": "d", "from": 80, "to": 93}], "pv": prev}
    b, page, pe, ce = C.open_screen(pw, w, h, data=rows, go=False)
    try:
        def go():
            js(page, "(c)=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','rs2','changes'], c); localStorage.removeItem('dash.rs2ChgSeen'); localStorage.removeItem('dash.rs2Alerts'); rs2Chg.at = 0; rs2Chg.doc = null; rs2.at = 0; rs2.rows = null; rs2.state = 'idle'; }", CH)
            js(page, "()=>{ switchTab('today'); }"); page.wait_for_timeout(1200)
            js(page, "()=>todayRefresh(true)"); page.wait_for_timeout(600)
            js(page, "()=>todayRefresh(true)"); page.wait_for_timeout(300)
            return js(page, LINES)
        js(page, "()=>{ localStorage.removeItem('dash.rs2Presets'); const B = getBook(tdHome()); if(B.settings) delete B.settings.rs2Presets; }")
        L = go()
        check(f"{tag} 9 no custom rule → the job's own d item shows as before", len(L) == 1 and "New Leader: APP RS 93" in L[0], L)
        js(page, "()=>{ localStorage.setItem('dash.rs2Presets', JSON.stringify({leaders:{rs12Min:90, near:12}})); }")
        L = go()
        check(f"{tag} 9 custom Leaders (RS ≥ 90 · within 12%): b/d recomputed in the app — ZETA left Leaders, CRDO + HOOD are new Leaders, APP (already one) is not", len(L) == 3 and "ZETA left Leaders · RS 99" in L[0] and "New Leader: CRDO RS 95" in L[1] and "New Leader: HOOD RS 94" in L[2] and not any("APP" in x for x in L), L)
        js(page, "()=>{ localStorage.setItem('dash.rs2Presets', JSON.stringify({leaders:{rs12Min:70, near:20}})); }")
        L = go()
        check(f"{tag} 9 a looser custom rule changes the alerts again (CRDO already a Leader yesterday → gone)", not any("CRDO" in x for x in L), L)
        js(page, "()=>{ localStorage.removeItem('dash.rs2Presets'); }")
        check(f"{tag} page errors none", not pe, pe[:2])
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        edit(pw, 1440, 900)
        edit(pw, 390, 844)
        ytoday(pw, 1440, 900)
    f = [r for r in results if not r[1]]
    print("\nSUMMARY RS2d: %d/%d pass" % (len(results) - len(f), len(results)))
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
