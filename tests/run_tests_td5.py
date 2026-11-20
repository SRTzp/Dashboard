#!/usr/bin/env python3
"""TD5 (delta) — my own to-dos in Today › To do: "+" in the header opens the input as the first row (hint · closes after save/Esc · N still opens New plan · disabled at 30) · Enter trim · 120 limit · empty ignored
· own rows reuse the tag slot (round tick, no MINE tag, × 28px) · 2-line textarea while editing · tick → done + Undo · × → delete + Undo · order (after red) · same cap (4/3) + "+N more" fold · card height unchanged when not adding
· empty card = header only · persists (settings doc, no new collection) · shortcuts silent while typing · 360/390/1440 no overflow.   Run: python3 tests/run_tests_td5.py"""
import sys
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results

ENGINE = """()=>{ window.__o = window.__o || ln4TodoItems; ln4TodoItems = function(M){ return [
  {c:'r', id:'t:r1', t:'Red one', fn:"void 0"}, {c:'a', id:'t:a1', t:'Amber one', fn:"void 0"},
  {c:'g', id:'t:g1', t:'Grey one', fn:"void 0"}, {c:'g', id:'t:g2', t:'Grey two', fn:"void 0"}, {c:'g', id:'t:g3', t:'Grey three', fn:"void 0"}, {c:'g', id:'t:g4', t:'Grey four', fn:"void 0"}, {c:'g', id:'t:g5', t:'Grey five', fn:"void 0"}]; }; todayRefresh(true); }"""
NOENG = "()=>{ ln4TodoItems = function(M){ return []; }; todayRefresh(true); }"
LIST = "()=>[...document.querySelectorAll('[data-td5-row] .td5-t, [data-td5-row] [data-td5-edit]')].map(e=>e.value != null ? e.value : e.textContent)"
ORDER = "()=>[...document.querySelector('[data-ln4-todorow]').children].filter(r=>r.matches('[data-lr2-ti],[data-td5-row]')).map(r=>r.matches('[data-td5-row]') ? 'MINE:' + r.querySelector('.td5-t').textContent : r.querySelector('.t').textContent)"
TOAST = "()=>{ const t = document.getElementById('td5Toast'); return t && t.style.display !== 'none' ? t.innerText.replace(/\\s+/g,' ').trim() : null }"
NUM = "()=>document.querySelector('[data-ln4-todorow] .lr2-th .num').textContent"
INP = "[data-td5-add]"


def opn(page):
    page.click("[data-td5-plus]"); page.wait_for_timeout(120)


def add(page, text):
    opn(page); page.fill(INP, text); page.press(INP, "Enter"); page.wait_for_timeout(150)


def over(page):
    return js(page, "()=>({sw:document.documentElement.scrollWidth - innerWidth, bad:[...document.querySelectorAll('[data-ln4-todorow] *')].filter(e=>{const r=e.getBoundingClientRect(); const c=document.querySelector('[data-ln4-todorow]').getBoundingClientRect(); return r.width>0 && (r.right > c.right + 1 || r.left < c.left - 1)}).length})")


def cardh(page): return js(page, "()=>document.querySelector('[data-ln4-todorow]').getBoundingClientRect().height")


def run(pw, w, h):
    tag = "[%s]" % w
    cap = 4 if w >= 900 else 3
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ serverConfirmed = true; stateFromServer = true; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(400)
        js(page, ENGINE); page.wait_for_timeout(300)
        # ---- 1 "+" in the header · no permanent input
        hd = js(page, "()=>{ const t = document.querySelector('[data-ln4-todorow] .lr2-th'); const p = t.querySelector('[data-td5-plus]'); const e = t.querySelector('[data-ln4-exec]'); return {plus:!!p, txt:p && p.textContent, beforeExec: !e || (p.getBoundingClientRect().right <= e.getBoundingClientRect().left + 1), inHeader:!!p, perm: !!document.querySelector('[data-td5-add]')} }")
        check(f"{tag} 1 small '+' in the To do header (left of the Exec pill) · no permanent input row", hd["plus"] and hd["txt"] == "+" and hd["beforeExec"] and not hd["perm"], hd)
        n0 = int(js(page, NUM))
        h0 = cardh(page)
        js(page, "()=>document.querySelector('[data-td5-plus]').style.display = 'none'"); h_no = cardh(page); js(page, "()=>document.querySelector('[data-td5-plus]').style.display = ''")
        check(f"{tag} 1 card height unchanged by the '+' when not adding ({h0:.0f} vs {h_no:.0f})", abs(h0 - h_no) <= 0.5, [h0, h_no])
        pt = js(page, "()=>{ const r = document.querySelector('[data-td5-plus]').getBoundingClientRect(); return [r.width, r.height] }")
        check(f"{tag} 1 '+' is 28px (44px target on phone)", pt == ([44, 44] if w <= 600 else [28, 28]), pt)
        # ---- open
        opn(page)
        o = js(page, "()=>{ const row = document.querySelector('[data-td5-addrow]'); const card = document.querySelector('[data-ln4-todorow]'); const hint = document.querySelector('[data-td5-hint]'); return {first: row.previousElementSibling === card.querySelector('.lr2-th'), focus: document.activeElement.matches('[data-td5-add]'), hint: hint.textContent.trim(), fs: getComputedStyle(row.querySelector('input')).fontSize} }")
        check(f"{tag} 1 '+' opens the input as the FIRST row under the header · focused · hint 'Enter save · Esc close · 0/120'", o["first"] and o["focus"] and o["hint"] == "Enter save · Esc close · 0/120", o)
        if w <= 600: check(f"{tag} 1 phone input is 16px", o["fs"] == "16px", o)
        h_open = cardh(page)
        check(f"{tag} 1 adding makes the card taller (input + hint)", h_open > h0 + 20, [h0, h_open])
        page.keyboard.type("hello"); page.wait_for_timeout(80)
        check(f"{tag} 1 hint counts n/120", js(page, "()=>document.querySelector('[data-td5-hint]').textContent.trim()") == "Enter save · Esc close · 5/120")
        page.press(INP, "Escape"); page.wait_for_timeout(120)
        check(f"{tag} 1 Esc closes it (nothing saved) · card back to its height", js(page, "()=>!document.querySelector('[data-td5-add]')") and js(page, LIST) == [] and abs(cardh(page) - h0) <= 0.5, [js(page, LIST), cardh(page), h0])
        # N still opens New plan (not the to-do input)
        page.click("body", position={"x": 2, "y": 2}) if False else js(page, "()=>document.activeElement && document.activeElement.blur()")
        page.keyboard.press("n"); page.wait_for_timeout(300)
        st = js(page, "()=>({inp: !!document.querySelector('[data-td5-add]'), pop: (typeof bdPopOpen === 'function') && bdPopOpen()})")
        check(f"{tag} 1 N still opens New plan, not the to-do input", st["pop"] and not st["inp"], st)
        page.keyboard.press("Escape"); page.wait_for_timeout(250)
        # ---- add
        opn(page); page.press(INP, "Enter"); page.wait_for_timeout(150)
        check(f"{tag} 2 empty Enter does nothing (stays open)", js(page, LIST) == [] and js(page, "()=>!!document.querySelector('[data-td5-add]')"))
        page.fill(INP, "   "); page.press(INP, "Enter"); page.wait_for_timeout(120)
        check(f"{tag} 2 spaces-only Enter does nothing", js(page, LIST) == [])
        page.fill(INP, "  Call broker  "); page.press(INP, "Enter"); page.wait_for_timeout(200)
        check(f"{tag} 2 Enter saves trimmed · input closes after save", js(page, LIST) == ["Call broker"] and js(page, "()=>!document.querySelector('[data-td5-add]')"), js(page, LIST))
        a = js(page, "()=>{ const r = document.querySelector('[data-td5-row]'); const k = r.querySelector('[data-td5-tick]').getBoundingClientRect(), x = r.querySelector('[data-td5-del]').getBoundingClientRect(); return {tag: !!r.querySelector('.td5-tag, .lr2-tg'), mine: /MINE/.test(r.innerText), tickW: k.width, xW: x.width, title: r.querySelector('.td5-t').title, lines: r.querySelector('.td5-t').getClientRects().length} }")
        check(f"{tag} 3 own row: tick in the 46px tag slot · no MINE tag · × {'44' if w <= 600 else '28'}px · title = full text", not a["tag"] and not a["mine"] and a["tickW"] == 46 and a["xW"] == (44 if w <= 600 else 28) and a["title"] == "Call broker", a)
        check(f"{tag} 3 header number +1", int(js(page, NUM)) == n0 + 1, js(page, NUM))
        add(page, "x" * 130)
        L = js(page, LIST)
        check(f"{tag} 2 120-char limit", len(L) == 2 and len(L[1]) == 120, [len(x) for x in L])
        r1 = js(page, "()=>{ const t = document.querySelectorAll('[data-td5-row] .td5-t')[1]; const r = t.getBoundingClientRect(); return {h: r.height, ell: getComputedStyle(t).textOverflow, ws: getComputedStyle(t).whiteSpace} }")
        check(f"{tag} 3 a long own item stays ONE line with ellipsis", r1["ell"] == "ellipsis" and r1["ws"] == "nowrap" and r1["h"] < 30, r1)
        # ---- order · cap · fold
        o = js(page, ORDER)
        check(f"{tag} 4 order: red first, then my to-dos (oldest first), then amber/grey", o[:4] == ["Red one", "MINE:Call broker", "MINE:" + "x" * 120, "Amber one"][:len(o[:4])] and o[0] == "Red one" and o[1] == "MINE:Call broker", o)
        f = js(page, "()=>({more:(document.querySelector('[data-ln4-todomore]')||{}).textContent, rows:document.querySelectorAll('[data-lr2-ti],[data-td5-row]').length})")
        check(f"{tag} 4 same cap ({cap}) for engine + own rows; rest behind '+N ›' (9 total → +{9 - cap} hmm engine 7 + own 2)", f["rows"] == cap and f["more"] == "+%d ›" % (9 - cap), f)
        js(page, "()=>document.querySelector('[data-ln4-todomore]').click()"); page.wait_for_timeout(200)
        check(f"{tag} 4 expanding shows all 9", js(page, "()=>document.querySelectorAll('[data-lr2-ti],[data-td5-row]').length") == 9)
        js(page, "()=>document.querySelector('[data-ln4-todomore]').click()"); page.wait_for_timeout(200)
        # ---- edit
        js(page, "()=>document.querySelector('[data-td5-row] .td5-t').click()"); page.wait_for_timeout(150)
        ta = js(page, "()=>{ const t = document.querySelector('[data-td5-edit]'); return {tag: t.tagName, rows: t.rows, focus: document.activeElement === t} }")
        check(f"{tag} 5 click text → 2-line textarea, focused", ta == {"tag": "TEXTAREA", "rows": 2, "focus": True}, ta)
        page.fill("[data-td5-edit]", "Call broker today"); page.press("[data-td5-edit]", "Enter"); page.wait_for_timeout(150)
        check(f"{tag} 5 Enter saves · back to one line", js(page, LIST)[0] == "Call broker today" and js(page, "()=>!document.querySelector('[data-td5-edit]')"), js(page, LIST))
        js(page, "()=>document.querySelector('[data-td5-row] .td5-t').click()"); page.wait_for_timeout(150)
        page.fill("[data-td5-edit]", "zzz"); page.press("[data-td5-edit]", "Escape"); page.wait_for_timeout(150)
        check(f"{tag} 5 Esc cancels", js(page, LIST)[0] == "Call broker today")
        js(page, "()=>document.querySelector('[data-td5-row] .td5-t').click()"); page.wait_for_timeout(150)
        page.fill("[data-td5-edit]", "  "); page.press("[data-td5-edit]", "Enter"); page.wait_for_timeout(150)
        check(f"{tag} 5 empty = no change", js(page, LIST)[0] == "Call broker today" and js(page, "()=>!document.querySelector('[data-td5-edit]')"))
        # ---- tick → done + Undo
        js(page, "()=>document.querySelector('[data-td5-row] [data-td5-tick]').click()"); page.wait_for_timeout(120)
        st = js(page, "()=>{ const r = document.querySelector('[data-td5-row]'); return {done:r.classList.contains('done'), tick:r.querySelector('.td5-ck i').textContent, td:getComputedStyle(r.querySelector('.td5-t')).textDecorationLine} }")
        check(f"{tag} 6 tick → row shows ✓ + strikethrough first", st["done"] and st["tick"] == "✓" and "line-through" in st["td"], st)
        page.wait_for_timeout(600)
        check(f"{tag} 6 …then leaves · toast 'Done: <text> · Undo'", js(page, LIST) == ["x" * 120] and js(page, TOAST) == "Done: Call broker today · Undo", [js(page, LIST), js(page, TOAST)])
        page.click("[data-td5-undo]"); page.wait_for_timeout(300)
        check(f"{tag} 6 Undo restores it in its old place", js(page, LIST) == ["Call broker today", "x" * 120], js(page, LIST))
        js(page, "()=>document.querySelectorAll('[data-td5-row] [data-td5-del]')[1].click()") if js(page, "()=>document.querySelectorAll('[data-td5-row]').length") > 1 else js(page, "()=>{ ln4TodoAll = true; todayRefresh(true); document.querySelectorAll('[data-td5-row] [data-td5-del]')[1].click(); }")
        page.wait_for_timeout(700)
        check(f"{tag} 7 × removes · toast 'Deleted: <text> · Undo'", js(page, "()=>td5List().length") == 1 and js(page, TOAST).startswith("Deleted: xxx") and js(page, TOAST).endswith("· Undo"), [js(page, "()=>td5List().length"), js(page, TOAST)])
        page.click("[data-td5-undo]"); page.wait_for_timeout(300)
        check(f"{tag} 7 Undo restores it in its old place", js(page, "()=>td5List().map(x=>x.t)") == ["Call broker today", "x" * 120])
        js(page, "()=>{ ln4TodoAll = true; todayRefresh(true); document.querySelectorAll('[data-td5-row] [data-td5-del]')[1].click(); }"); page.wait_for_timeout(7000)
        check(f"{tag} 7 the toast goes after ~6 s", js(page, TOAST) is None, js(page, TOAST))
        # ---- 30 cap
        js(page, "()=>{ ln4TodoAll = true; todayRefresh(true); }")
        for i in range(30):
            if js(page, "()=>td5List().length") >= 30: break
            add(page, "item %d" % i)
        c = js(page, "()=>{ const p = document.querySelector('[data-td5-plus]'); return {n:td5List().length, dis:p.disabled, title:p.title} }")
        check(f"{tag} 8 30 open → '+' disabled with tooltip '30 open — finish one first'", c == {"n": 30, "dis": True, "title": "30 open — finish one first"}, c)
        o = over(page)
        check(f"{tag} 8 no overflow with 30 rows expanded", o["sw"] <= 0 and o["bad"] == 0, o)
        js(page, "()=>document.querySelectorAll('[data-td5-row] [data-td5-del]')[0].click()"); page.wait_for_timeout(700)
        check(f"{tag} 8 finishing one re-enables '+'", js(page, "()=>!document.querySelector('[data-td5-plus]').disabled"))
        js(page, "()=>{ ln4TodoAll = false; todayRefresh(true); }")
        if w <= 600:
            t = js(page, "()=>{ const r = e=>e.getBoundingClientRect(); const a = document.querySelector('[data-td5-tick]'), x = document.querySelector('[data-td5-del]'), p = document.querySelector('[data-td5-plus]'); const q = getComputedStyle(p, '::after'); return {tick:[r(a).width, r(a).height], x:[r(x).width, r(x).height], plus:[r(p).width, r(p).height]} }")
            check(f"{tag} 9 phone targets >= 44px (tick · × · '+' with its hit area)", t["tick"][1] >= 44 and t["x"][0] >= 44 and t["x"][1] >= 44 and t["plus"][0] >= 44, t)
        page.wait_for_timeout(2500)
        saved = js(page, "()=>{ const o = window.firebase.__mockDb.__dump(); const r = []; for(const k in o){ if(JSON.stringify(o[k]).includes('myTodos')) r.push(k); } return {paths:r, doc:o['users/testuid']}; }")
        check(f"{tag} 10 saved in the existing user doc (settings.myTodos) · no new collection", saved["paths"] == ["users/testuid"], saved["paths"])
        mine = js(page, "()=>td5List().map(x=>x.t)")
        check(f"{tag} no page errors", not pe, pe)
        return saved["doc"], mine
    finally:
        b.close()


def after_reload(pw, w, h, doc, mine):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h, d=doc)
    try:
        js(page, "()=>{ serverConfirmed = true; stateFromServer = true; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        check(f"{tag} 10 persists after reload (same list, same order)", js(page, "()=>td5List().map(x=>x.t)") == mine and len(mine) == 29, [mine[:3], js(page, "()=>td5List().length")])
        check(f"{tag} 10 one list in the home-account settings (Main and Family share it)", js(page, "()=>{ const h = tdSettings().myTodos; return !!h && h.length === td5List().length }"))
        js(page, ENGINE); page.wait_for_timeout(300)
        t0 = js(page, "()=>activeTab"); opn(page)
        page.keyboard.type("2 3 n / . ? 4abc"); page.wait_for_timeout(200)
        s = js(page, "()=>({tab:activeTab, v:document.querySelector('[data-td5-add]').value, ov:document.querySelectorAll('.overlay.show').length, pop:bdPopOpen()})")
        check(f"{tag} 11 global shortcuts do not fire while typing in the input", s["tab"] == t0 and s["v"] == "2 3 n / . ? 4abc" and s["ov"] == 0 and not s["pop"], s)
        page.press("[data-td5-add]", "Escape"); page.wait_for_timeout(120)
        js(page, "()=>document.querySelector('[data-td5-row] .td5-t').click()"); page.wait_for_timeout(150)
        page.keyboard.type("5 6 n x"); page.wait_for_timeout(150)
        s = js(page, "()=>({tab:activeTab, v:document.querySelector('[data-td5-edit]').value, pop:bdPopOpen()})")
        check(f"{tag} 11 …nor inside an inline edit", s["tab"] == t0 and s["v"].endswith("5 6 n x") and not s["pop"], s)
        page.press("[data-td5-edit]", "Escape"); page.wait_for_timeout(150)
        o = over(page)
        check(f"{tag} 12 no horizontal overflow (page and card)", o["sw"] <= 0 and o["bad"] == 0, o)
        # empty state: header only
        js(page, "()=>{ td5Write(l=>[]); }"); js(page, NOENG); page.wait_for_timeout(300)
        e = js(page, "()=>{ const c = document.querySelector('[data-ln4-todorow]'); return c ? {num: c.querySelector('.num').textContent, rows: c.querySelectorAll('[data-lr2-ti],[data-td5-row],[data-td5-addrow],[data-ln4-todomore]').length, txt: c.innerText.replace(/\\s+/g,' ').trim()} : null }")
        check(f"{tag} 13 empty: card shows with just the header (To do 0 +) · no extra text", e and e["num"] == "0" and e["rows"] == 0 and e["txt"].startswith("To do 0 +") and len(e["txt"]) < 40, e)
        add(page, "first one")
        check(f"{tag} 13 …and you can add from it", js(page, "()=>td5List().length") == 1)
        check(f"{tag} no page errors (reload)", not pe, pe)
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844), (360, 800)):
            doc, mine = run(pw, w, h)
            after_reload(pw, w, h, doc, mine)
    bad = [r for r in results if not r[1]]
    print("SUMMARY td5: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
