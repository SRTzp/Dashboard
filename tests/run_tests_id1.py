#!/usr/bin/env python3
"""ID1 — Watch > Ideas fixes: one panel with a sticky header · short never-clipped tabs · 'Picked 5 Nov' · weakest-link number inside its box · desktop panel scrolls inside itself ·
opaque expand layer · phone sheet header always visible · list: no RS column, 'No companies yet', one Filter menu · Journal > Not taken without overlap · no Thai in UI labels.
Run: python3 tests/run_tests_id1.py"""
import re, sys
from playwright.sync_api import sync_playwright
from re1d_common import js, check, results
import id1_common as C
import lr5b_common as JC

THAI = re.compile(r"[฀-๿]")
CHROME = "()=>[...document.querySelectorAll('[data-idea-sticky], .ideaMeta, [data-idea-filter], .lr5-ith, .lr5-ir .c-sec, .lr5-ir .c-hw, .lr5-ir .lr5-act, .lr5-ir .lr5-id .ltChip, .ideaFilBar')].map(e=>e.innerText).join(' | ')"
TABS = ["sum", "mech", "evd", "vc", "co"]


def tabs(pw, w, h):
    tag = "[%s]" % w
    b, page, r = C.open_ideas(pw, w, h)
    try:
        bad = []
        for t in TABS:
            js(page, "(t)=>ideaSetTab(t)", t); page.wait_for_timeout(250)
            m = js(page, """()=>{ const tb = document.querySelector('[data-idea-tabs]'), on = tb.querySelector('.ltTab.on'), p = document.querySelector('[data-idea-panel]').getBoundingClientRect(), a = tb.getBoundingClientRect(), o = on.getBoundingClientRect();
              const scr = tb.scrollWidth > tb.clientWidth + 1; return {l: o.left >= a.left - 1, r: o.right <= a.right + 1, inP: a.left >= p.left - 1 && a.right <= p.right + 1, scr, ov: document.documentElement.scrollWidth - innerWidth, labels: [...tb.children].map(x=>x.innerText.replace(/\\s+/g,' ').trim())}; }""")
            if not (m["l"] and m["r"] and m["inP"] and m["ov"] <= 0): bad.append((t, m))
        check(f"{tag} 2 every tab: the active tab fully visible in the tab row · row inside the panel · no page overflow", not bad, bad)
        check(f"{tag} 2 short labels Summary · How · Evidence · Chain · Companies", m["labels"] == ["Summary", "How", "Evidence 1", "Chain", "Companies"] or [re.sub(r"\s*\d+$", "", x) for x in m["labels"]] == ["Summary", "How", "Evidence", "Chain", "Companies"], m["labels"])
    finally:
        b.close()


def detail(pw, w, h):
    tag = "[%s]" % w
    b, page, r = C.open_ideas(pw, w, h, tab="mech")
    try:
        one = js(page, "()=>({panels: document.querySelectorAll('[data-idea-panel]').length, wlDPanel: document.querySelectorAll('.wlDet > .wlDPanel').length, inner: [...document.querySelectorAll('.wlDBody > .panel')].map(p=>getComputedStyle(p).borderTopWidth)})")
        check(f"{tag} 1 ONE panel (no second stacked card) · inner content panels have no border", one["panels"] == 1 and one["wlDPanel"] == 1 and all(x == "0px" for x in one["inner"]), one)
        hd = js(page, """()=>{ const q = s=>document.querySelector(s); const h = q('[data-idea-sticky]'); return {title: q('[data-idea-title]').innerText, st: q('[data-idea-status]').innerText, rdy: q('[data-idea-ready]').innerText, main: q('[data-idea-main]').innerText, more: !!q('[data-idea-menu]'), pos: getComputedStyle(h).position, gate: q('[data-idea-gatefold]').open}; }""")
        check(f"{tag} 1 sticky header: title · status chip · '3 of 4 ready' · 'Add evidence ›' · ⋯ ; conditions collapsed", hd["title"] == "Semis AI memory" and hd["rdy"] == "3 of 4 ready" and hd["main"] == "Add evidence ›" and hd["more"] and hd["pos"] == "sticky" and hd["gate"] is False and "Waiting for evidence" in hd["st"], hd)
        js(page, "()=>document.querySelector('[data-idea-gatefold]').open = true")
        check(f"{tag} 1 expanding 'Ready to hand off' lists the 4 conditions", js(page, "()=>document.querySelectorAll('[data-idea-gate] > div').length") == 4)
        # main action per status
        got = {}
        for iid in ("idea-draft", "ready-idea", "grid-power"):
            js(page, "(i)=>ideaOpen(i)", iid); page.wait_for_timeout(250)
            got[iid] = js(page, "()=>[document.querySelector('[data-idea-main]').innerText, (document.querySelector('[data-idea-ready]')||{}).innerText||'', document.querySelector('[data-idea-meta]').innerText]")
        check(f"{tag} 1 main action by status: Draft → 'Finish draft ›' · Ready → 'Hand off ›' · Exploring/Waiting → 'Add evidence ›'", got["idea-draft"][0] == "Finish draft ›" and got["ready-idea"][0] == "Hand off ›" and got["grid-power"][0] == "Add evidence ›", got)
        check(f"{tag} 1 Ready idea shows '4 of 4 ready'", got["ready-idea"][1] == "4 of 4 ready", got["ready-idea"])
        check(f"{tag} 3 tag 'Picked 5 Nov' (no idea@1 · pick · …)", got["ready-idea"][2] == "Picked 5 Nov" and "idea@1" not in got["ready-idea"][2], got["ready-idea"][2])
        js(page, "()=>ideaMenuToggle('more')"); page.wait_for_timeout(200)
        mt = js(page, "()=>[...document.querySelectorAll('.ideaP .ltMenu button, .ideaP .ltMenu .ltMenuMsg')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} 1 ⋯ menu has Park · Export · Delete and the version idea@1", any(x.startswith("Park") for x in mt) and any(x.startswith("Export") for x in mt) and any(x.startswith("Delete") for x in mt) and any("idea@1" in x for x in mt), mt)
        js(page, "()=>{ ideaMenu=''; ideaOpen('semis-ai-memory-2026'); ideaSetTab('mech'); }"); page.wait_for_timeout(300)
        wk = js(page, """()=>{ const li = document.querySelector('.ideaSteps li.weak'), r = li.getBoundingClientRect(), cs = getComputedStyle(li, '::before'), pl = parseFloat(getComputedStyle(li).paddingLeft), l = parseFloat(cs.left);
          return {num: cs.content, l, pl, inside: l >= 0 && l + 10 <= pl, bg: getComputedStyle(li).backgroundColor}; }""")
        check(f"{tag} 4 Mechanism: the weakest-link number sits inside its highlighted box", wk["inside"] and wk["num"].startswith("counter("), wk)
        check(f"{tag} 3/9 no Thai in UI labels (header · chips · tabs · list head · filter · buttons)", not THAI.search(js(page, CHROME)), js(page, CHROME)[:200])
    finally:
        b.close()


def desktop(pw):
    w, h = 1440, 900; tag = "[1440]"
    b, page, r = C.open_ideas(pw, w, h, tab="sum")
    try:
        m = js(page, """()=>{ const a = document.querySelector('.ideaAside'), r = a.getBoundingClientRect(), cs = getComputedStyle(a); return {oy: cs.overflowY, ch: a.clientHeight, sh: a.scrollHeight, bottom: Math.round(r.bottom), vh: innerHeight, doc: document.documentElement.scrollHeight}; }""")
        check(f"{tag} 5 side panel scrolls inside itself (overflow auto, fits the viewport, page does not grow to its length)", m["oy"] == "auto" and m["sh"] > m["ch"] and m["bottom"] <= m["vh"] and m["doc"] <= m["vh"] + 2, m)
        js(page, "()=>{ document.querySelector('.ideaAside').scrollTop = 600; }"); page.wait_for_timeout(150)
        s = js(page, "()=>{ const a = document.querySelector('.ideaAside').getBoundingClientRect(), t = document.querySelector('[data-idea-title]').getBoundingClientRect(), b = document.querySelector('[data-idea-tabs]').getBoundingClientRect(); return {titleTop: Math.round(t.top - a.top), tabsInside: b.top >= a.top && b.bottom <= a.bottom, st: document.querySelector('.ideaAside').scrollTop}; }""")
        check(f"{tag} 5 header + tabs stay visible after scrolling the panel", s["st"] > 0 and s["titleTop"] >= 0 and s["tabsInside"], s)
        # expand layer
        btn = js(page, "()=>document.querySelector('[data-wl-full]').innerText.trim()")
        check(f"{tag} 6 labelled button '⤢ Expand'", btn == "⤢ Expand", btn)
        js(page, "()=>document.querySelector('[data-wl-full]').click()"); page.wait_for_timeout(500)
        x = js(page, """()=>{ const a = document.querySelector('.ideaAside'), cs = getComputedStyle(a), r = a.getBoundingClientRect(), tb = document.querySelector('.topbar').getBoundingClientRect();
          const cells = [...document.querySelectorAll('.lr5-list .lr5r, .lr5-list .lbl, .lr5-list .c-sec, .lr5-list .c-hw, .lr5-hd, .lr5-h1, .lr5-seg')].filter(e=>e.getClientRects().length);
          const through = cells.filter(e=>{ const q = e.getBoundingClientRect(); const cx = Math.min(innerWidth-2, Math.max(1, q.left + q.width/2)), cy = Math.min(innerHeight-2, Math.max(1, q.top + q.height/2)); if(cy < r.top) return false; const t = document.elementFromPoint(cx, cy); return !(t && a.contains(t)); }).length;
          const top = document.elementFromPoint(tb.left + 20, tb.top + tb.height/2);
          return {pos: cs.position, bg: cs.backgroundColor, z: cs.zIndex, top: Math.round(r.top), tbBottom: Math.round(tb.bottom), through, cells: cells.length, topbarOnTop: !!(top && top.closest('.topbar')), btn: document.querySelector('[data-wl-full]').innerText.trim(), full: wlFull}; }""")
        check(f"{tag} 6 expand = solid full-page layer: opaque white, starts at the app top bar, nothing of the Ideas table/header behind it shows through", x["full"] and x["pos"] == "fixed" and x["bg"] == "rgb(255, 255, 255)" and x["through"] == 0 and abs(x["top"] - x["tbBottom"]) <= 2 and x["topbarOnTop"], x)
        check(f"{tag} 6 button becomes '✕ Close'", x["btn"] == "✕ Close", x)
        t2 = js(page, "()=>{ const tb = document.querySelector('[data-idea-tabs]').getBoundingClientRect(), on = document.querySelector('.ltTab.on').getBoundingClientRect(), a = document.querySelector('.ideaAside').getBoundingClientRect(); return on.left >= tb.left && on.right <= tb.right && tb.right <= a.right; }")
        check(f"{tag} 6 tabs not clipped in the expand view", t2)
        js(page, "()=>document.querySelector('[data-wl-full]').click()"); page.wait_for_timeout(400)
        check(f"{tag} 6 '✕ Close' returns to the side panel", js(page, "()=>!wlFull && !!document.querySelector('[data-wl-full=\"0\"]')"))
    finally:
        b.close()


def phone(pw, w, h):
    tag = "[%s]" % w
    b, page, r = C.open_ideas(pw, w, h, tab="mech")
    try:
        page.add_style_tag(content=C.HIDE_NAV) if False else None
        def hd():
            return js(page, """()=>{ const q = s=>document.querySelector(s), a = q('.ideaAside').getBoundingClientRect(), t = q('[data-idea-title]').getBoundingClientRect(), x = q('[data-idea-close]').getBoundingClientRect(), s = q('[data-idea-status]').getBoundingClientRect();
              const hit = e=>{ const r = e.getBoundingClientRect(), el = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); return !!(el && q('.ideaAside').contains(el)); };
              return {title: t.top >= a.top - 1 && t.bottom <= innerHeight && hit(q('[data-idea-title]')), status: hit(q('[data-idea-status]')), x: hit(q('[data-idea-close]')), xw: Math.round(x.width), xh: Math.round(x.height), aTop: Math.round(a.top), sheetZ: getComputedStyle(q('.ideaAside')).zIndex}; }""")
        h0 = hd()
        check(f"{tag} 7 sheet header (title · status · ✕ 44px) visible and on top of the app bars", h0["title"] and h0["status"] and h0["x"] and h0["xw"] >= 44 and h0["xh"] >= 44, h0)
        js(page, "()=>{ document.querySelector('.ideaAside').scrollTop = 500; }"); page.wait_for_timeout(200)
        h1 = hd()
        check(f"{tag} 7 header still visible after scrolling the sheet", h1["title"] and h1["status"] and h1["x"], h1)
        cov = js(page, "()=>{ const tb = document.querySelector('#tabsMain, .topbar .tabs'); if(!tb) return null; const r = tb.getBoundingClientRect(), a = document.querySelector('.ideaAside').getBoundingClientRect(); const mid = [r.left + r.width/2, Math.min(innerHeight - 4, r.top + r.height/2)]; const el = document.elementFromPoint(mid[0], mid[1]); return {overlap: r.bottom > a.top && r.top < a.bottom, sheetOnTop: !!(el && document.querySelector('.ideaAside').contains(el))}; }")
        check(f"{tag} 7 no app bar drawn over the sheet where they overlap", cov is None or not cov["overlap"] or cov["sheetOnTop"], cov)
        p = js(page, """()=>{ const a = document.querySelector('.ideaAside').getBoundingClientRect(), b = document.querySelector('.ideaP .wlDBody > .panel'), r = b.getBoundingClientRect(), cs = getComputedStyle(b); return {border: cs.borderTopWidth, shadow: cs.boxShadow, left: Math.round(r.left - a.left), right: Math.round(a.right - r.right)}; }""")
        check(f"{tag} 8 no inner card border in the sheet · content uses the full sheet width (<=16px side gutter)", p["border"] == "0px" and p["shadow"] == "none" and p["left"] <= 16 and p["right"] <= 16, p)
    finally:
        b.close()


def listing(pw, w, h):
    tag = "[%s]" % w
    b, page, r = C.open_ideas(pw, w, h, sel=None)
    try:
        js(page, "()=>{ if(wlMobOpen) wlBack(); }"); page.wait_for_timeout(200)
        L = js(page, """()=>({rs: document.querySelectorAll('.lr5-ir .c-rs').length, hd: [...document.querySelectorAll('.lr5-ith .lbl')].map(e=>e.innerText), co: [...document.querySelectorAll('.lr5-ir')].map(r=>r.dataset.idea + ':' + r.querySelector('.c-hw').innerText), kinds: document.querySelectorAll('.ideaFilBar > [data-trade-kinds], .lr5-list > .wlListHead > [data-trade-kinds]').length, filBtn: document.querySelector('[data-idea-filter]').innerText.trim(), chipsShown: document.querySelectorAll('.wlListHead [data-idea-f]').length})""")
        check(f"{tag} 9 no RS column in Ideas", L["rs"] == 0 and "RS" not in L["hd"], L)
        check(f"{tag} 9 'No companies yet' when there are none; counts otherwise", "no-cands:No companies yet" in L["co"] and "semis-ai-memory-2026:1 to study · 3 waiting" in L["co"], L["co"])
        check(f"{tag} 10 one 'Filter ▾' button, the two chip rows are hidden until it is opened", js(page, "()=>document.querySelector('[data-idea-filter]').getAttribute('aria-label')") == "Filter"  and L["chipsShown"] == 0, L)
        page.click("[data-idea-filter]"); page.wait_for_timeout(200)
        M = js(page, """()=>{ const m = document.querySelector('[data-idea-filmenu]'), r = m.getBoundingClientRect(), a = document.querySelector('.lr5-list').getBoundingClientRect(); const g = [...m.querySelectorAll('.ideaFilG')].map(e=>e.innerText); const el = document.elementFromPoint(r.left + 20, r.bottom - 8); return {g, types: m.querySelectorAll('[data-trade-kind]').length, st: m.querySelectorAll('[data-idea-f]').length, vis: !!(el && m.contains(el)), inVp: r.right <= innerWidth && r.bottom <= innerHeight}; }""")
        check(f"{tag} 10 Filter menu = Type (All/Trade/Invest) + Status (All/Waiting/Ready/Parked), fully visible", [x.lower() for x in M["g"]] == ["type", "status"] and M["types"] == 3 and M["st"] == 4 and M["vis"] and M["inVp"], M)
        page.click("[data-idea-f='parked']"); page.wait_for_timeout(250)
        n = js(page, "()=>[document.querySelectorAll('.lr5-ir').length, !!document.querySelector('[data-idea-filmenu]'), document.querySelector('[data-idea-filter]').innerText.trim()]")
        if w > 600: check(f"{tag} 10 button shows the active count 'Filter · 1 ▾'", "1" in n[2], n)
        check(f"{tag} 10 choosing Status filters the list, menu stays open, button shows the active count", n[0] == 0 and n[1], n)
        check(f"{tag} 9 no Thai in list chrome", not THAI.search(js(page, CHROME)))
    finally:
        b.close()


def nottaken(pw):
    w, h = 1440, 900; tag = "[1440]"
    b, page, pe = JC.open_journal(pw, w, h)
    try:
        js(page, "()=>lrSwPick('journal','both')"); page.wait_for_timeout(300)
        js(page, "()=>{ const d = document.querySelector('[data-lr5-nt]'); if(d) d.open = true; }"); page.wait_for_timeout(250)
        o = js(page, """()=>[...document.querySelectorAll('.lr5-nrow')].map(r=>{ const k = [...r.children].map(c=>c.getBoundingClientRect()); let ov = false; for(let i = 0; i < k.length - 1; i++) if(k[i].right > k[i+1].left + 0.5 && k[i].width && k[i+1].width) ov = true; const chip = r.querySelector('.lr5-rs'); return {ov, disp: getComputedStyle(chip).display, w: Math.round(chip.getBoundingClientRect().width), t: r.innerText.replace(/\\s+/g, ' ').trim().slice(0, 60)}; })""")
        check(f"{tag} 11 Journal › Not taken: reason chip does not overlap the date/note (chip is a pill, not the RS grid)", len(o) > 0 and not any(x["ov"] or x["disp"] == "inline-grid" for x in o), o[:3])
        check(f"{tag} 11 no page errors", not pe, pe)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            tabs(pw, w, h); detail(pw, w, h); listing(pw, w, h)
        desktop(pw); phone(pw, 390, 844); nottaken(pw)
    bad = [r for r in results if not r[1]]
    print("SUMMARY id1: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
