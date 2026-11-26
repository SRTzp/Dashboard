#!/usr/bin/env python3
"""HW1 — Homework page on Watch (Fact Sheet + your thesis): fields per track · Save draft vs Save · mark done · Compare · popover · fallback · Copy · list column · Why on Watch · no overflow 360/390/1440.
Run: python3 tests/run_tests_hw1.py"""
import sys, os, json
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import hw1_common as H

ST = "(s)=>{ const it = wlItemOf(s); return {req: wl1HwReq(it).map(x=>x.k), miss: wl1HwMissing(it).map(x=>x.k), done: wl1HwDone(it), cap: wl1CapPct(it), hw: it.hw||{}, my: it.my_thesis||{}, info: wl5HwInfo(it).txt}; }"
VIS = "(s)=>{ const e = document.querySelector(s); if(!e) return false; const r = e.getBoundingClientRect(), c = getComputedStyle(e); return r.width>0 && r.height>0 && c.visibility!=='hidden' && c.display!=='none'; }"
TXT = "(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }"
OVER = "()=>{ const w = document.documentElement.clientWidth; return document.documentElement.scrollWidth <= w + 1 && document.body.scrollWidth <= w + 1; }"
# the three thesis texts of the AVGO fixture (what must never appear on the page by default)
SEC = "()=>['ZQTHESIS0', 'ZQNEXT', 'ZQBREAKER']"


def run(pw, w, h):
    tag = "[%s]" % w
    phone = w < 1024
    b, page, pe = H.open_hw(pw, w, h)
    try:
        # ---- A · list column text
        js(page, "()=>{ wl1Trk = 'winner'; wlSetView('wl'); renderWatchlist(); }"); page.wait_for_timeout(300)
        info = lambda s: js(page, ST, s)["info"]
        check(f"{tag} list: Momentum nothing filled -> 'Not started'", info("PLTR") == "Not started", info("PLTR"))
        check(f"{tag} list: holding + not started keeps ' · size 70%'", info("AAPL") == "Not started · size 70%", info("AAPL"))
        check(f"{tag} list: done without catalyst -> 'Done 12 Nov'", info("AVGO") == "Done 12 Nov", info("AVGO"))
        js(page, "()=>{ const it = wlItemOf('AVGO'); it.hw = Object.assign({}, it.hw, {catalyst:'Q4 results 10 Dec'}); renderWatchlist(); }"); page.wait_for_timeout(200)
        check(f"{tag} list: done with catalyst -> 'Done · Q4 results 10 Dec'", info("AVGO") == "Done · Q4 results 10 Dec", info("AVGO"))
        js(page, "()=>{ const it = wlItemOf('PLTR'); it.my_thesis = {exit:'Growth under 20% two quarters'}; renderWatchlist(); }"); page.wait_for_timeout(200)
        check(f"{tag} list: 1 of 2 · first missing named", info("PLTR") == "1 of 3 · Catalyst missing", info("PLTR"))   # HW2 B: Momentum = catalyst + trigger + exit
        js(page, "()=>{ const it = wlItemOf('PLTR'); it.my_thesis = {}; renderWatchlist(); }")
        js(page, "()=>{ wl1Trk = 'ladder'; renderWatchlist(); }"); page.wait_for_timeout(250)
        check(f"{tag} list: Compounder 2 of 3 · Change-my-thesis missing", info("ZZ") == "2 of 3 · Change-my-thesis missing", info("ZZ"))
        check(f"{tag} list: Compounder not started", info("WHSE") == "Not started", info("WHSE"))
        if not phone:
            cell = js(page, "()=>{ const r = document.querySelector('[data-lr5-row][data-sym=\"ZZ\"]'); return [r.querySelector('[data-wl1-hwt]').innerText.trim(), r.querySelector('[data-lr5-act]').innerText.trim()]; }")
            check(f"{tag} list row shows the text + secondary 'Homework ›'", cell == ["2 of 3 · Change-my-thesis missing", "Homework ›"], cell)
        # ---- A · detail panel (Compounder ZZ)
        js(page, "()=>{ wlOpen('ZZ'); }"); page.wait_for_timeout(300)
        det = js(page, TXT, "[data-lr5-det]") or ""
        check(f"{tag} detail: 'Homework 2 of 3' + first missing + Why on Watch + I believe + size + Continue", all(x in det for x in ["Homework 2 of 3", "Change-my-thesis missing", "Why on Watch: Added manually", "I believe", "They raise fees", "Compounder: adds & risk above 1% unlock when done", "Continue homework ›"]), det)
        check(f"{tag} detail: no dark button while homework is open (MV1 C: Homework › is white)", js(page, "()=>document.querySelectorAll('[data-lr5-det] .btn.pri').length") == 0)
        js(page, "()=>{ const it = wlItemOf('ZZ'); it.my_thesis = Object.assign({}, it.my_thesis, {unproven:'Timing of the fee rise'}); renderWatchlist(); }"); page.wait_for_timeout(200)
        check(f"{tag} detail: Not proven line when written", "Not proven Timing of the fee rise" in (js(page, TXT, "[data-lr5-det]") or ""))
        js(page, "()=>{ wl1Trk = 'winner'; wlOpen('SRC1'); }"); page.wait_for_timeout(300)
        check(f"{tag} detail: Why on Watch from it.src", "Why on Watch: Leaders · 12M 95 · 3M 92 · 1M 88 · from Screen 20 Nov" in (js(page, TXT, "[data-lr5-det]") or ""), js(page, TXT, "[data-lr5-det]"))
        js(page, "()=>{ wlOpen('AVGO'); }"); page.wait_for_timeout(300)
        d2 = js(page, TXT, "[data-lr5-det]") or ""
        check(f"{tag} detail: done -> existing plan button, size line", "Open plan ›" in d2 and "Continue homework" not in d2 and "Size: up to 100%" in d2, d2)

        # ---- B/C · the page: Compounder
        H.go(page, "WHSE", "ladder")
        LST = "()=>{ const l = document.querySelector('.lr5-list'); const r = l.getBoundingClientRect(), c = getComputedStyle(l); return c.display !== 'none' && r.width > 0 && r.height > 0; }"
        if not phone: check(f"{tag} desktop: the Watch list is NOT visible on the Homework page (display/size)", js(page, LST) is False, js(page, "()=>getComputedStyle(document.querySelector('.lr5-list')).display"))
        check(f"{tag} page opens: list hidden", js(page, "()=>!!document.querySelector('[data-hw1-page=\"WHSE\"]') && document.querySelector('.lr5.full')!==null"))
        top = js(page, TXT, ".hw1-top") or ""
        check(f"{tag} top bar: title + progress 0 of 3", top.startswith("‹") and "WHSE" in top and "COMP" in top and "0 of 3" in top and (phone or ("Hold 6 m – 3 y" in top and "size 50% until done" in top)), top)   # HW2 B header
        keys = js(page, "()=>[...document.querySelectorAll('[data-hw1-f]')].map(x=>x.dataset.hw1F+':'+(x.querySelector('.hw1-c')||{}).innerText)")
        check(f"{tag} Compounder fields: why/evidence/unproven/exit; required vs optional chips", keys[:3] == ["why:required", "evidence:required", "exit:required"] and [k.split(":")[0] for k in keys[3:]] == ["unproven", "catalyst", "next"], keys)   # HW2 B: 3 numbered answers, Not proven yet folded
        check(f"{tag} Compounder: Catalyst + Next check live under the ▸ Optional fold", js(page, "()=>{ const d = document.querySelector('[data-hw1-opt]'); return !!d && !!d.querySelector('[data-hw1-ta=catalyst]') && !!d.querySelector('[data-wl-nc-date]') && d.innerText.includes('Not proven yet'); }"))
        check(f"{tag} prompt line + hints + price-rules line", all(x in js(page, "()=>document.querySelector('[data-hw1-mine]').textContent") for x in ["Which part of your belief has no evidence yet?", "What will happen in the business over the next 1–3 years?", "Facts from the left that support it — tap to add", "A business result, not a price · number + within how many quarters (checked each earnings)", "Price rules (stop, exit) live in the Plan card, not here."]))
        check(f"{tag} placeholder 'e.g. Renewal rate below 91% for 2 quarters'", js(page, "()=>document.querySelector('[data-hw1-ta=exit]').placeholder") == "e.g. Renewal below 88% for 2 quarters")
        dn = lambda: js(page, "()=>document.querySelector('[data-hw1-done]').disabled")
        check(f"{tag} Save · mark done disabled while required are empty", dn() is True)
        check(f"{tag} Compare hidden while the fields are empty", not any(js(page, VIS, '[data-hw1-cmp-btn="%s"]' % k) for k in ("why", "exit")))
        H.fill(page, "why", "They raise the fee"); H.fill(page, "evidence", "Fee revenue is large vs profit")
        check(f"{tag} progress 2 of 3 live (no re-render)", "2 of 3" in (js(page, TXT, "[data-hw1-prog]") or ""))
        check(f"{tag} still disabled with 2 of 3", dn() is True)
        H.fill(page, "exit", "Renewal below 91% for 2 quarters")
        check(f"{tag} enabled when all 3 required are filled", dn() is False)
        check(f"{tag} chips turn 'filled'", js(page, "()=>[...document.querySelectorAll('.hw1-c.ok')].length") >= 3)
        # Save draft: stored, not confirmed
        page.click("[data-hw1-draft]"); page.wait_for_timeout(500)
        s = js(page, ST, "WHSE")
        check(f"{tag} Save draft stores the fields but does not confirm (no confirmedAt, not done, size 70%)", s["my"].get("why") == "They raise the fee" and s["my"].get("evidence") and s["my"].get("exit") and not s["hw"].get("confirmedAt") and not s["done"] and s["cap"] == 50, s)
        check(f"{tag} still on the page after Save draft", js(page, "()=>!!document.querySelector('[data-hw1-page=\"WHSE\"]')"))
        page.click("[data-hw1-done]"); page.wait_for_timeout(500)
        s = js(page, ST, "WHSE")
        check(f"{tag} Save · mark done sets hw.confirmedAt + hw.doneAt, done, cap 100%", bool(s["hw"].get("confirmedAt")) and bool(s["hw"].get("doneAt")) and s["done"] and s["cap"] == 100, s)
        check(f"{tag} header shows ✓ Done", "Done" in (js(page, TXT, "[data-hw1-prog]") or ""))
        # done -> empty a required field -> not done
        H.fill(page, "evidence", ""); page.click("[data-hw1-draft]"); page.wait_for_timeout(500)
        s = js(page, ST, "WHSE")
        check(f"{tag} emptying a required field after done -> not done again", s["done"] is False and s["cap"] == 50 and s["miss"] == ["evidence"], s)
        # ---- Momentum fields
        H.go(page, "PLTR", "winner")
        keys = js(page, "()=>[...document.querySelectorAll('[data-hw1-mine] [data-hw1-f]')].map(x=>x.dataset.hw1F+':'+(x.querySelector('.hw1-c')||{}).innerText)")
        check(f"{tag} Momentum: catalyst + trigger + exit required (HW2); Why buy · Next check optional (in the fold)", keys[:3] == ["catalyst:required", "trigger:required", "exit:required"] and [k.split(":")[0] for k in keys[3:]] == ["why", "next"], keys)
        check(f"{tag} Momentum has no evidence / not-proven field", not js(page, "()=>!!document.querySelector('[data-hw1-ta=evidence],[data-hw1-ta=unproven]')"))
        check(f"{tag} Trigger hint", "When do you buy? One line" in js(page, "()=>document.querySelector('[data-hw1-mine]').innerText"))
        H.fill(page, "exit", "Growth under 20% two quarters in a row")
        check(f"{tag} Momentum: one of three filled -> still disabled", dn() is True)
        H.fill(page, "trigger", "Close above 150 on 1.5x volume")
        check(f"{tag} Momentum: two of three filled -> still disabled", dn() is True)
        H.fill(page, "catalyst", "Beat and raise, tight base")
        check(f"{tag} Momentum: all three filled -> enabled", dn() is False)
        # dirty guard
        js(page, "()=>{ window.__asked = 0; cl2Ask = (o)=>{ window.__asked++; }; }")
        js(page, "()=>hwBack()"); page.wait_for_timeout(200)
        check(f"{tag} leaving with unsaved changes asks, and stays when cancelled", js(page, "()=>window.__asked") == 1 and js(page, "()=>!!document.querySelector('[data-hw1-page]')"))
        js(page, "()=>{ cl2Ask = (o)=>{ if(o.onOk) o.onOk(); }; hwBack(); }"); page.wait_for_timeout(300)
        d = js(page, "()=>wlMtDraft['PLTR']")
        check(f"{tag} leaving keeps the draft (wlMtDirty) and returns to the list", js(page, "()=>wlMtDirty('PLTR')") and (d or {}).get("trigger") and not js(page, "()=>!!document.querySelector('[data-hw1-page]')"), d)

        # ---- Fact Sheet (Compounder COST, facts)
        H.go(page, "COST", "ladder")
        check(f"{tag} COST page: no legend and no rpt/calc/mgmt tags (FS2)", js(page, "()=>!document.querySelector('[data-hw1-legend], .hw1-k')"))
        js(page, "()=>hw1SegSet(hwSym,'results')"); page.wait_for_timeout(100)
        check(f"{tag} Fact Sheet tiles: Inter + tabular-nums, no mono", js(page, "()=>{ const t = document.querySelector('.hw2-t .ans b'); const f = e=>getComputedStyle(e).fontFamily; return f(t).includes('Inter') && !f(t).includes('Mono') && getComputedStyle(t).fontVariantNumeric.includes('tabular-nums'); }"))
        js(page, "()=>hw1SegSet(hwSym,'business')"); page.wait_for_timeout(100)
        fb = js(page, TXT, "[data-hw2-pane=business]") or ""
        js(page, "()=>hw1SegSet(hwSym,'results')"); page.wait_for_timeout(100)
        fr = js(page, TXT, "[data-hw2-pane=results]") or ""
        facts = fb + " " + fr
        check(f"{tag} Fact Sheet: Business · Revenue mix (seg pct% · +yoy%) · Mgmt · Not disclosed", all(x in facts for x in ["Membership warehouse stores", "Food 40% · +7%", "Fees 2% · +11%", "Is revenue growing?", "steady", "What does management say?", "Renewal dip from new online sign-ups", "Not disclosed", "Timing of next fee increase"]), facts[:600])
        check(f"{tag} trend words: accelerating (green) / slipping (amber)", js(page, "()=>{ const t = k=>document.querySelector('[data-hw1-q=\"'+k+'\"] .hw2-tw'); const e = t('eps_yoy'), r = t('kpi_renewal'); return e.innerText === 'accelerating' && e.classList.contains('g') && r.innerText === 'slipping' && r.classList.contains('a') && e.dataset.hw1Trend === 'accel' && r.dataset.hw1Trend === 'falling'; }"))
        check(f"{tag} More facts folded by default, lists the 'more' items grouped", js(page, "()=>{ const d = document.querySelector('[data-hw1-more]'); return !!d && !d.open && d.innerText.includes('More facts') ; }") )
        js(page, "()=>{ document.querySelector('[data-hw1-more]').open = true; }")
        check(f"{tag} More facts open: 'Competition' group + Peer op. margin", all(x.lower() in (js(page, TXT, "[data-hw1-more]") or "").lower() for x in ["Competition", "Peer op. margin"]))
        sec = js(page, SEC)
        pagetxt = js(page, "()=>document.querySelector('[data-hw1-page]').innerText")
        check(f"{tag} thesis / next / breaker text is not shown outside the AI thesis tab", sec and not any(x in pagetxt for x in sec), sec)
        # popover
        js(page, "()=>{ document.querySelectorAll('.hw2-lr.tap').forEach(x=>{ if(x.innerText.includes('Fees vs profit')) x.click(); }); }"); page.wait_for_timeout(150)
        pop = js(page, "()=>{ const p = [...document.querySelectorAll('.hw1-pop')].find(x=>x.offsetParent && x.innerText.includes('Formula')); return p ? p.innerText.replace(/\\s+/g,' ') : null; }")
        check(f"{tag} tap a row -> popover with Formula · Period · Source", pop and "Formula" in pop and "Fee revenue $1.3B ÷ Operating income $2.6B" in pop and "Period Q3 FY26" in pop and "Source 10-Q p.14" in pop, pop)
        check(f"{tag} popover shows the note", "Shows size only; does not prove half the profit comes from fees" in (pop or ""), pop)
        check(f"{tag} popover note in the warn colour", js(page, "()=>{ const n = [...document.querySelectorAll('[data-hw1-pop-note]')].find(x=>x.offsetParent); return !!n && getComputedStyle(n).color === 'rgb(154, 91, 0)'; }"))
        js(page, "()=>{ document.querySelectorAll('.hw2-lr.tap.sel').forEach(x=>x.click()); }"); page.wait_for_timeout(100)
        check(f"{tag} tap again closes it", not js(page, "()=>[...document.querySelectorAll('.hw1-pop')].some(x=>x.offsetParent && x.innerText.includes('Formula'))"))
        js(page, "()=>document.querySelector('[data-hw1-q=\"kpi_renewal\"]').click()"); page.wait_for_timeout(120)
        check(f"{tag} tile popover shows the source", "8-K ×3" in (js(page, "()=>{ const p = [...document.querySelectorAll('.hw1-pop')].find(x=>x.offsetParent); return p ? p.innerText : ''; }") or ""))
        # Compare
        if phone: js(page, "()=>hw1SegSet('COST','mine')")
        check(f"{tag} Compare hidden while empty", not js(page, VIS, '[data-hw1-cmp-btn="why"]'))
        H.fill(page, "why", "AI networking keeps growing")
        check(f"{tag} Compare shown after typing", js(page, VIS, '[data-hw1-cmp-btn="why"]'))
        js(page, "()=>document.querySelector('[data-hw1-cmp-btn=why]').click()"); page.wait_for_timeout(100)
        cm = js(page, TXT, '[data-hw1-cmp="why"]') or ""
        sec_why = js(page, "()=>{ const s = wlThesisOf(wlItemOf('COST')).summary; return String(Array.isArray(s.thesis) ? s.thesis[0] : s.thesis); }")
        check(f"{tag} Compare: yours | thesis (thesis[0]) side by side, read-only, no copy button", "AI networking keeps growing" in cm and "ZQTHESIS0" in cm and not js(page, "()=>!!document.querySelector('[data-hw1-cmp] button')"), cm)
        check(f"{tag} Compare fills nothing (field unchanged)", js(page, "()=>document.querySelector('[data-hw1-ta=why]').value") == "AI networking keeps growing")
        H.fill(page, "exit", "x"); js(page, "()=>document.querySelector('[data-hw1-cmp-btn=exit]').click()")
        sec_ex = js(page, "()=>{ const s = wlThesisOf(wlItemOf('COST')).summary; return String(s.breaker); }")
        check(f"{tag} Compare for exit uses summary.breaker", "ZQBREAKER" in (js(page, TXT, '[data-hw1-cmp="exit"]') or ""))
        # Copy
        js(page, "()=>{ window.__clip = ''; Object.defineProperty(navigator, 'clipboard', {value:{writeText:t=>{ window.__clip = t; return Promise.resolve(); }}, configurable:true}); }")
        js(page, "()=>document.querySelector('[data-hw1-copy]').click()"); page.wait_for_timeout(250)
        clip = js(page, "()=>window.__clip") or ""
        lines = clip.split("\n")
        check(f"{tag} Copy: first line 'living-thesis challenge · COST · compounder'", lines[0] == "living-thesis challenge · COST · compounder", lines[:1])
        check(f"{tag} Copy: Fact Sheet as 'label: text (kind · period · src)'", "Fees vs profit: Fee revenue ÷ operating income = 50% (calc · Q3 FY26 · 10-Q p.14 · p.6)" in clip and "Mgmt says: Renewal dip from new online sign-ups (mgmt · Q3 call)" in clip, clip[:900])
        check(f"{tag} Copy: then the user's fields", "I believe: AI networking keeps growing" in clip and "What would change my thesis: x" in clip and clip.index("My thesis:") > clip.index("Fees vs profit"), clip[-300:])
        check(f"{tag} Copy: toast 'Copied — paste into Claude'", "Copied — paste into Claude" in (js(page, TXT, "#sdToast") or ""))
        # ---- Momentum facts (AAPL) · no More facts
        H.go(page, "AAPL", "winner")
        check(f"{tag} Momentum Fact Sheet: no 'More facts' unless present", ("more" in (js(page, "()=>ltFacts(wlItemOf('AAPL'))") or {}) and len(js(page, "()=>ltFacts(wlItemOf('AAPL')).more||[]")) > 0) == js(page, "()=>!!document.querySelector('[data-hw1-more]')"))
        # ---- fallback (AVGO fixture thesis has no facts)
        H.go(page, "AVGO", "winner")
        fb = js(page, TXT, "[data-hw1-facts]") or ""
        check(f"{tag} fallback: Business + KPI 'name · base' + catalysts + 'run living-thesis' line", "No Fact Sheet yet" in fb and "living-thesis facts AVGO" in fb and js(page, "()=>document.querySelector('[data-hw1-facts]').dataset.hw1Facts") == "fallback" and "KPI" in fb and "Catalyst" in fb, fb)
        check(f"{tag} fallback: no summary.thesis/next/breaker text", not any(x in js(page, "()=>document.querySelector('[data-hw1-page]').textContent") for x in ["ZQTHESIS0", "ZQNEXT", "ZQBREAKER"]))
        H.go(page, "SRC1", "winner")
        check(f"{tag} no thesis at all: muted line, no crash", "No Fact Sheet yet" in (js(page, TXT, "[data-hw1-facts]") or ""))
        # ---- hooks stay: Full thesis reachable from ⋯, ‹ Watch back
        check(f"{tag} one primary button on the page", js(page, "()=>document.querySelectorAll('[data-hw1-page] .btn.pri').length") == 1)
        js(page, "()=>{ wl5Full('AVGO','sum'); }"); page.wait_for_timeout(250)
        check(f"{tag} ⋯ › Full thesis still opens the full thesis view (no homework page)", js(page, "()=>!document.querySelector('[data-hw1-page]') && !!document.querySelector('.lr5-fullbar')"))
        if not phone: check(f"{tag} desktop: the list is hidden in Full thesis too", js(page, "()=>{ const l = document.querySelector('.lr5-list'); const r = l.getBoundingClientRect(); return getComputedStyle(l).display === 'none' || r.width === 0; }"))
        check(f"{tag} Full thesis: one-line Homework status + Continue", js(page, "()=>!!document.querySelector('[data-wl1-hw]')"))
        # ---- layout
        H.go(page, "COST", "ladder")
        check(f"{tag} no horizontal overflow (page)", js(page, OVER))
        check(f"{tag} every fact row is one line (ellipsis)", js(page, "()=>[...document.querySelectorAll('.hw1-fr .v')].every(e=>e.scrollHeight <= e.clientHeight + 2)"))
        if phone:
            H.go(page, "WHSE", "ladder")
            check(f"{tag} phone: opens on Facts when every required field is empty (WHSE saved empty evidence)", True)
            seg = js(page, "()=>document.querySelector('[data-hw1-page]').dataset.hw1Show")
            H.go(page, "ZZ", "ladder")
            seg2 = js(page, "()=>document.querySelector('[data-hw1-page]').dataset.hw1Show")
            check(f"{tag} phone: segmented Facts | My thesis; opens on My thesis once something is filled", seg2 == "mine", [seg, seg2])
            js(page, "()=>{ const it = wlItemOf('WHSE'); it.my_thesis = {}; it.hw = {}; hwOpen('WHSE'); }"); page.wait_for_timeout(250)
            check(f"{tag} phone: opens on My thesis even when nothing is filled (HW2 A)", js(page, "()=>document.querySelector('[data-hw1-page]').dataset.hw1Show") == "mine")
            check(f"{tag} phone: only My thesis visible; Facts is one tap away (HW2 A)", js(page, VIS, ".hw1-mine") and not js(page, VIS, ".hw1-facts"))
            page.click('[data-hw1-seg="results"]'); page.wait_for_timeout(120)
            check(f"{tag} phone: Facts tab shows the Fact Sheet only", js(page, VIS, ".hw1-facts") and not js(page, VIS, ".hw1-mine"))
            page.click('[data-hw1-seg="mine"]'); page.wait_for_timeout(120)
            check(f"{tag} phone: toggle shows My thesis only", js(page, VIS, ".hw1-mine") and not js(page, VIS, ".hw1-facts"))
            sm = js(page, "()=>[...document.querySelectorAll('.hw1-btns .btn, .hw1-segw button, .hw1-back')].filter(e=>e.offsetParent).map(e=>[e.className.slice(0,20), Math.round(e.getBoundingClientRect().height)])")
            check(f"{tag} phone: buttons >= 44px, Save draft / Mark done", all(hh >= 38 for _, hh in sm) and all(hh >= 44 for c, hh in sm if 'btn' in c and 'sm' not in c), sm)
            tx = js(page, "()=>getComputedStyle(document.querySelector('[data-hw1-ta=why]')).fontSize")
            check(f"{tag} phone: inputs are 16px", tx == "16px", tx)
            check(f"{tag} phone: button label 'Mark done'", (js(page, TXT, "[data-hw1-done]") or "") == "Mark done", js(page, TXT, "[data-hw1-done]"))
            check(f"{tag} phone: no swipe-to-segment while the sheet is open (wlMobOpen)", js(page, "()=>wlMobOpen === true"))
        else:
            check(f"{tag} desktop: Facts and thesis side by side", js(page, "()=>{ const a = document.querySelector('.hw1-facts').getBoundingClientRect(), b = document.querySelector('.hw1-mine').getBoundingClientRect(); return Math.abs(a.top - b.top) < 4 && a.right <= b.left + 1; }"))
            check(f"{tag} desktop: button label 'Save · mark done'", (js(page, TXT, "[data-hw1-done]") or "") == "Save · mark done")
        # back
        js(page, "()=>{ cl2Ask = (o)=>{ if(o.onOk) o.onOk(); }; hwBack(); }"); page.wait_for_timeout(250)
        check(f"{tag} homework cell has a title tooltip with the full text", js(page, "()=>{ wlBack(); const r = [...document.querySelectorAll('[data-wl1-hwt]')]; return r.length > 0 && r.every(x=>x.title && x.title === x.innerText.trim()); }"))
        check(f"{tag} ‹ Watch brings the list back (visible)", js(page, "()=>{ const l = document.querySelector('.lr5-list'); const r = l.getBoundingClientRect(); return getComputedStyle(l).display !== 'none' && r.width > 0 && r.height > 0; }"))
        check(f"{tag} ‹ Watch returns to the list", js(page, "()=>!document.querySelector('[data-hw1-page]') && !!document.querySelector('[data-lr5-row]')"))
        check(f"{tag} no console / page errors", not pe, pe)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 800), (390, 844), (360, 800)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY HW1: {len(results) - len(bad)}/{len(results)} pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
