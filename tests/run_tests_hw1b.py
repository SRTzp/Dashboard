#!/usr/bin/env python3
"""HW1b — Backspace / Esc = back on the Homework page and the Full thesis view.
Run: python3 tests/run_tests_hw1b.py"""
import sys
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import hw1_common as H

ON = "()=>!!document.querySelector('[data-hw1-page]')"
LIST = "()=>!document.querySelector('[data-hw1-page]') && !!document.querySelector('[data-lr5-row]')"
FULL = "()=>wl5FullSym !== '' && !hwSym"


def key(page, k):
    page.keyboard.press(k); page.wait_for_timeout(250)


def blur(page): js(page, "()=>{ document.activeElement && document.activeElement.blur(); }")


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = H.open_hw(pw, w, h)
    try:
        js(page, "()=>{ cl2Ask = (o)=>{ if(o.onOk) o.onOk(); }; }")
        # ---- Backspace / Esc go back, stock stays selected
        for k in ("Backspace", "Escape"):
            H.go(page, "COST", "ladder"); blur(page)
            check(f"[{k}] page open", js(page, ON))
            key(page, k)
            check(f"{tag} {k} on the Homework page -> back to the list", js(page, LIST))
            check(f"{tag} {k}: same stock still selected", js(page, "()=>wlSel") == "COST")
        title = None
        H.go(page, "COST", "ladder")
        check(f"{tag} ‹ Watch has title 'Back (Esc or Backspace)'", js(page, "()=>document.querySelector('[data-hw1-back]').title") == "Back (Esc or Backspace)")
        # ---- typing: Backspace deletes text and stays; Esc blurs, second Esc goes back
        H.fill(page, "why", "abcdef")
        page.focus('[data-hw1-ta="why"]'); page.keyboard.press("End"); key(page, "Backspace")
        check(f"{tag} Backspace in a field deletes text and stays", js(page, ON) and page.input_value('[data-hw1-ta="why"]') == "abcde", page.input_value('[data-hw1-ta="why"]'))
        key(page, "Escape")
        check(f"{tag} first Esc in a field only blurs it", js(page, ON) and not js(page, "()=>!!document.activeElement && document.activeElement.tagName === 'TEXTAREA'"))
        # dirty draft -> confirm guard: dismiss = stay
        check(f"{tag} the draft is dirty", js(page, "()=>wlMtDirty('COST')"))
        js(page, "()=>{ window.__c = 0; cl2Ask = (o)=>{ window.__c++; }; }")
        key(page, "Escape")
        check(f"{tag} dirty draft: second Esc asks to confirm, dismiss = stay", js(page, "()=>window.__c") == 1 and js(page, ON))
        key(page, "Backspace")
        check(f"{tag} dirty draft: Backspace asks too, dismiss = stay", js(page, "()=>window.__c") == 2 and js(page, ON))
        js(page, "()=>{ cl2Ask = (o)=>{ if(o.onOk) o.onOk(); }; }")
        key(page, "Escape")
        check(f"{tag} confirm accepted -> back to the list, stock selected", js(page, LIST) and js(page, "()=>wlSel") == "COST")
        # ---- Fact Sheet popover: Esc closes it first
        H.go(page, "COST", "ladder"); blur(page)
        js(page, "()=>document.querySelector('[data-hw1-page] .tap[data-hw1-row]').click()"); page.wait_for_timeout(150)
        check(f"{tag} popover open", js(page, "()=>document.querySelectorAll('[data-hw1-page] [data-hw1-row][aria-expanded=\"true\"]').length") == 1)
        key(page, "Backspace")
        check(f"{tag} Backspace with a popover open does not go back", js(page, ON))
        key(page, "Escape")
        check(f"{tag} Esc closes the popover first, page stays", js(page, ON) and js(page, "()=>document.querySelectorAll('[data-hw1-page] [data-hw1-row][aria-expanded=\"true\"]').length") == 0)
        key(page, "Escape")
        check(f"{tag} next Esc goes back", js(page, LIST))
        # ---- import sheet (ZZ has no Fact Sheet) : Esc closes the sheet first, page stays
        H.go(page, "ZZ", "ladder"); blur(page)
        js(page, "()=>ltImportOpen('ZZ')"); page.wait_for_timeout(200)
        key(page, "Escape")
        check(f"{tag} Esc closes the import sheet first (ltImp cleared), page stays", js(page, "()=>ltImp === null && !document.getElementById('ltOverlay').classList.contains('show')") and js(page, ON))
        js(page, "()=>ltImportOpen('ZZ')"); page.wait_for_timeout(200)
        key(page, "Escape")  # focus is in the sheet textarea: still closes the sheet (Esc closes the top layer even while typing)
        check(f"{tag} Esc with focus in the sheet textarea closes the sheet, page stays", js(page, ON) and js(page, "()=>ltImp === null"))
        js(page, "()=>ltImportOpen('ZZ')"); page.wait_for_timeout(200)
        key(page, "Backspace")
        check(f"{tag} Backspace while the sheet is open does not go back", js(page, ON))
        js(page, "()=>ltSheetClose()")
        # ---- ⋯ menu open: Esc closes it first
        js(page, "()=>{ wlMenu = hwSym; renderWatchlist(); }"); blur(page)
        key(page, "Escape")
        check(f"{tag} Esc closes an open menu first", js(page, ON) and js(page, "()=>wlMenu") == "")
        # ---- Full thesis view -> back to the summary
        js(page, "()=>{ hwBack(); wl5Full('COST','sum'); }"); page.wait_for_timeout(300); blur(page)
        check(f"{tag} Full thesis view open", js(page, FULL))
        key(page, "Backspace")
        check(f"{tag} Backspace on Full thesis -> summary (same stock)", js(page, "()=>wl5FullSym === '' && !hwSym && wlSel === 'COST'") and not js(page, ON))
        js(page, "()=>{ wl5Full('COST','sum'); }"); page.wait_for_timeout(300); blur(page)
        key(page, "Escape")
        check(f"{tag} Esc on Full thesis -> summary", js(page, "()=>wl5FullSym === '' && wlSel === 'COST'"))
        # ---- other tabs / views unaffected
        js(page, "()=>{ wlSetView('idea'); }"); page.wait_for_timeout(200); blur(page)
        key(page, "Backspace"); key(page, "Escape")
        check(f"{tag} Ideas view: Backspace/Esc change nothing", js(page, "()=>wlView") == "idea")
        js(page, "()=>{ wlSetView('wl'); wlOpen('COST'); }"); page.wait_for_timeout(200); blur(page)
        key(page, "Backspace")
        check(f"{tag} Watch list detail (not Homework): Backspace does not close it", js(page, "()=>wlSel") == "COST")
        check(f"{tag} no console / page errors", not pe, pe)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        run(pw, 1440, 900)
        run(pw, 1280, 800)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY HW1b: {len(results) - len(bad)}/{len(results)} pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
