#!/usr/bin/env python3
"""EN1 — Enter submits the primary button of the top-most sheet/modal; Esc closes it.
Run: python3 tests/run_tests_en1.py"""
import sys, os, re
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()

# every form named in the brief has its primary marked (static, by handler)
PRIMARY = {"New/Edit plan Core": ["coreNewSave", "coreStopSave"], "Sat plan": ["pbSave", "satPyrSave"], "Record buy/sell": ["coreBuy1Save", "coreBuyAddSave", "coreLBuySave", "corePxSave", "saveTradeEdit", "lfAddSave"],
           "Place order": ["pb2PlaceYes", "efCorePlaceYes"], "Journal Save review": ["lr5Save", "jBackfillSave"], "Watch": ["wl2UseThesis", "wlNoteSave", "wlAddSave"], "Settings": ["saveSettings", "saveSystemSettings"],
           "Import sheets": ["wiSave", "stkSave", "ltImpSave", "ideaImpSave", "tv1ImportApply"]}
NOENTER = ["confirmClosePos", "coreDelGo", "satV3ClosedDelGo", "re4Go", "coreDeleteClosed", "cl2aRun", "bkRestoreRun"]


def static():
    for grp, fns in PRIMARY.items():
        miss = [f for f in fns if not re.search(r'<button\b[^>]*data-enter-primary[^>]*on[cC]lick="[^"]*\b%s\(' % f, SRC)]
        check("1 %s: primary marked data-enter-primary" % grp, not miss, miss)
    miss = [f for f in NOENTER if not re.search(r'<button\b[^>]*data-no-enter[^>]*on[cC]lick="[^"]*\b%s\(' % f, SRC)]
    check("1 destructive (Delete / Remove / Cancel order / Close / Reset) marked data-no-enter", not miss, miss)
    check("1 no destructive button also marked primary", not re.search(r'<button\b[^>]*data-enter-primary[^>]*data-no-enter|<button\b[^>]*data-no-enter[^>]*data-enter-primary', SRC))


def key(page, k, target=None, **kw):
    js(page, """([k, sel, o])=>{ const t = sel ? document.querySelector(sel) : document.activeElement; if(t && t.focus) t.focus();
      const ev = new KeyboardEvent('keydown', Object.assign({key:k, bubbles:true, cancelable:true}, o)); if(o.keyCode) Object.defineProperty(ev, 'keyCode', {get:()=>o.keyCode}); (t||document.body).dispatchEvent(ev); }""", [k, target, kw])
    page.wait_for_timeout(120)


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        # --- real overlays: Settings (saveSettings), Watch add (wlAddSave)
        js(page, "()=>{ window.__c = {}; ['saveSettings','wlAddSave'].forEach(n=>{ const o = window[n]; window[n] = function(){ window.__c[n] = (window.__c[n]||0) + 1; }; }); openSettings(); }"); page.wait_for_timeout(300)
        first = js(page, "()=>{ const i = document.querySelector('#setOverlay input[type=text], #setOverlay input[type=number]'); if(!i) return null; i.id = i.id || 'en1First'; return '#' + i.id; }")
        key(page, "Enter", first)
        c = js(page, "()=>window.__c.saveSettings||0")
        check(f"{tag} 2 Settings: Enter in an input -> Save once", c == 1, c)
        key(page, "Enter", first, repeat=True)
        check(f"{tag} 2 Settings: key repeat does not submit again", js(page, "()=>window.__c.saveSettings||0") == 1)
        js(page, "()=>document.getElementById('setOverlay').classList.remove('show')")
        js(page, "()=>{ document.getElementById('wlAddOverlay').classList.add('show'); }"); page.wait_for_timeout(800)
        wi = js(page, "()=>{ const i = document.querySelector('#wlAddOverlay input'); if(!i) return null; i.id = i.id || 'en1W'; return '#' + i.id; }")
        key(page, "Enter", wi)
        check(f"{tag} 2 Watch add: Enter -> Save once", js(page, "()=>window.__c.wlAddSave||0") == 1)
        key(page, "Escape", wi)
        check(f"{tag} 5 Esc closes the Watch add modal", not js(page, "()=>document.getElementById('wlAddOverlay').classList.contains('show')"))

        # --- sheet (core-sheet style): input + textarea + primary + destructive sibling
        html = ("<h3>EN1</h3><input id='en1a' type='text'><textarea id='en1t'></textarea><select id='en1s'><option>a</option><option>b</option></select>"
                "<div class='ccFoot'><button type='button' class='ccBtn' data-no-enter onclick='window.__d=(window.__d||0)+1'>Delete</button>"
                "<button type='button' id='en1go' class='ccBtn pri' data-enter-primary onclick='window.__n=(window.__n||0)+1'>Save</button></div>")
        open_ = lambda: js(page, "(h)=>{ window.__n = 0; window.__d = 0; coreSheet('en1', h); }", html)
        n = lambda: js(page, "()=>window.__n")
        open_(); page.wait_for_timeout(200)
        h = js(page, "()=>[...document.querySelectorAll('.ui-sheet-backdrop input')].map(i=>i.getAttribute('enterkeyhint'))")
        check(f"{tag} 4 text inputs inside a sheet get enterkeyhint (last = done)", h and h[-1] == "done", h)
        key(page, "Enter", "#en1a")
        check(f"{tag} 2 sheet: Enter in a text input clicks the primary once", n() == 1, n())
        page.wait_for_timeout(800)
        key(page, "Enter", "#en1a", isComposing=True)
        check(f"{tag} 2 IME composing (isComposing) -> no submit", n() == 1, n())
        key(page, "Enter", "#en1a", keyCode=229)
        check(f"{tag} 2 keyCode 229 -> no submit", n() == 1, n())
        key(page, "Enter", "#en1t")
        check(f"{tag} 2 Enter in a textarea -> no submit (newline)", n() == 1, n())
        key(page, "Enter", "#en1t", metaKey=True)
        check(f"{tag} 2 Cmd+Enter in a textarea -> submits", n() == 2, n())
        page.wait_for_timeout(800)
        key(page, "Enter", "#en1t", ctrlKey=True)
        check(f"{tag} 2 Ctrl+Enter in a textarea -> submits", n() == 3, n())
        page.wait_for_timeout(800)
        key(page, "Enter", "#en1s")
        check(f"{tag} 2 Enter on a select -> no submit", n() == 3, n())
        key(page, "Enter", "#en1a"); key(page, "Enter", "#en1a")
        check(f"{tag} 2 double Enter inside 700ms -> ONE submit", n() == 4, n())
        page.wait_for_timeout(800)
        js(page, "()=>{ document.getElementById('en1go').disabled = true; }")
        key(page, "Enter", "#en1a")
        check(f"{tag} 2 invalid / disabled primary -> no submit, first field focused", n() == 4 and js(page, "()=>document.activeElement && document.activeElement.id") == "en1a", n())
        key(page, "Escape", "#en1a")
        check(f"{tag} 5 Esc closes the sheet", js(page, "()=>!document.querySelector('.ui-sheet-backdrop')"))
        # --- delete dialog: only a destructive button -> Enter never fires it
        js(page, "()=>{ window.__d = 0; coreSheet('en1d', \"<h3>Delete?</h3><input id='en1x' type='text'><div class='ccFoot'><button type='button' class='ccBtn' onclick='coreSheetClose()'>Cancel</button><button type='button' class='ccBtn pri dn' data-no-enter onclick='window.__d=(window.__d||0)+1'>Delete</button></div>\"); }"); page.wait_for_timeout(200)
        key(page, "Enter", "#en1x")
        check(f"{tag} 3 delete dialog: Enter does not delete", js(page, "()=>window.__d") == 0)
        key(page, "Escape", "#en1x")
        check(f"{tag} 5 Esc closes the delete dialog", js(page, "()=>!document.querySelector('.ui-sheet-backdrop')"))
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


if __name__ == "__main__":
    static()
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("SUMMARY en1: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
