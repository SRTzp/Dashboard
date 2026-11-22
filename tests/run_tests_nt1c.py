#!/usr/bin/env python3
"""NT1c — (1) Today › Ideas card never truncates with "…" (title wraps, short pills, button stays right) at 1280 / 1440 / 390 ·
(2) Watch › Ideas: filter chips + Find + + Idea (AI generated: chips + Import JSON) live in the top row of the list card → the page header is ONE line at 1280 / 1440.
Run: python3 tests/run_tests_nt1c.py"""
import sys
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import nt1_common as N
import run_tests_nt1 as T
import run_tests_nt1b as B

LONG = "Long title that used to be cut with dots next to the pill"


def part_today(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h, my_docs=False, notes=False)
    try:
        t0 = B.td(page); B.quiet_fixture_ai(page)
        B.seed_my(page, {
            "a": B.mkmy(1, ("stock", "AVGO"), LONG, B.add(t0, -1), B.add(t0, 6), next="Close above 190 on volume and then write the plan with the stop under the base, sized for the week", level=102),
            "b": B.mkmy(2, ("tag", "Free tag of twenty"), "Risk-off until CPI", B.add(t0, -2), B.add(t0, -2), next="Read CPI → still bear?")})
        B.seed_ai(page, "ai-x", "AI power: grid equipment and the long chain behind it", "need_evidence", recheck=t0)
        B.px(page, "AVGO", 100.0); B.to_today(page)
        card = js(page, B.TXT, "[data-nt1b-ideas]")
        check(f"{tag} 1 no `…` anywhere in the Ideas card text", "…" not in card and "..." not in card, card)
        bad = js(page, """()=>[...document.querySelectorAll('[data-nt1b-ideas] *')].filter(e=>{ const s = getComputedStyle(e); return e.getClientRects().length && (s.textOverflow === 'ellipsis' || (s.overflow === 'hidden' && e.scrollWidth > e.clientWidth + 1 && !e.matches('[data-nt1b-ideas]'))); }).map(e=>e.className || e.tagName)""")
        check(f"{tag} 1 nothing in the card is clipped or set to ellipsis", bad == [], bad)
        ov = js(page, "()=>{ const c = document.querySelector('[data-nt1b-ideas]'); return [c.scrollWidth <= c.clientWidth + 1, [...c.querySelectorAll('.nt1b-it')].every(r=>r.scrollWidth <= r.clientWidth + 1)]; }")
        check(f"{tag} 1 card and rows do not overflow sideways", all(ov), ov)
        r = js(page, """()=>{ const row = document.querySelector('[data-nt1b-it="my:a"]'), t = row.querySelector('.t'), p = row.querySelector('[data-nt1b-pill]'), btn = row.querySelector('[data-nt1b-btn]'), n = row.querySelector('.n');
          const rr = x=>x.getBoundingClientRect(); const lh = parseFloat(getComputedStyle(t).lineHeight) || 18;
          return {titleLines: Math.round(rr(t).height / lh), titleFull: t.innerText === arguments0, pill: p.innerText, btnRight: Math.round(rr(btn).right), rowRight: Math.round(rr(row).right), btnAfterTitle: rr(btn).left >= rr(t).right - 1, nextFull: n.innerText.length}; }""".replace("arguments0", repr(LONG)))
        check(f"{tag} 1 long title is shown in full (wraps, never cut) · pill short `2.0% to level`", r["titleFull"] and r["pill"] == "2.0% to level" and (r["titleLines"] <= 2 or w < 600), r)  # noqa, r)
        check(f"{tag} 1 the button stays on the right edge of the row", abs(r["btnRight"] - r["rowRight"]) <= 2 and r["btnAfterTitle"], r)
        nx = js(page, "()=>document.querySelector('[data-nt1b-it=\"my:a\"] .n').innerText")
        check(f"{tag} 1 the Next line is shown in full", nx.endswith("sized for the week"), nx)
        pills = js(page, "()=>[...document.querySelectorAll('[data-nt1b-pill]')].map(p=>p.innerText)")
        check(f"{tag} 1 short pills: `2.0% to level` · `2 days late` · AI `evidence n/4`", "2.0% to level" in pills and "2 days late" in pills and any(x.startswith("evidence ") and x.endswith("/4") for x in pills), pills)
        check(f"{tag} 1 no page overflow · no page errors", js(page, B.OVER) and not pe, pe[:3])
    finally:
        b.close()


def part_watch(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h)
    try:
        T.extra_ai(page); N.goto_watch(page)
        for seg in ("my", "ai"):
            (T.to_my if seg == "my" else T.to_ai)(page); page.wait_for_timeout(250)
            m = js(page, """()=>{ const h = document.querySelector('[data-lr5-head]'), kids = [...h.children].filter(e=>e.getClientRects().length && e.getBoundingClientRect().width > 0), tops = kids.map(e=>Math.round(e.getBoundingClientRect().top + e.getBoundingClientRect().height / 2));
              const lt = document.querySelector('[data-nt1-lt]'), list = document.querySelector('[data-nt1-list]'), hr = h.getBoundingClientRect();
              return {oneLine: Math.max(...tops) - Math.min(...tops) <= 6, hh: Math.round(hr.height), inList: !!(lt && list && list.contains(lt)), chipsInList: !!(lt && lt.querySelector('[data-nt1-chips]')), chipsInHead: !!h.querySelector('[data-nt1-chips]'),
                headTxt: h.innerText.replace(/\\s+/g, ' '), ltTxt: lt ? lt.innerText.replace(/\\s+/g, ' ') : '', ltTop: lt ? Math.round(lt.getBoundingClientRect().top - list.getBoundingClientRect().top) : null}; }""")
            check(f"{tag} 2 {seg}: header is ONE line (no wrap)", m["oneLine"] and m["hh"] <= 80, m)
            check(f"{tag} 2 {seg}: chips live in the top row of the list card, not in the header", m["inList"] and m["chipsInList"] and not m["chipsInHead"] and m["ltTop"] <= 2, m)
            if seg == "my":
                check(f"{tag} 2 my: top row = All · Due · Markets · Stocks · Sat · Plan + ⌕ Find + + Idea; header has none of them", all(x in m["ltTxt"] for x in ("All", "Due", "Markets", "Stocks", "Sat", "Plan", "Find", "+ Idea")) and "+ Idea" not in m["headTxt"] and "Find" not in m["headTxt"], m)
                ia = js(page, "()=>{ const b = document.querySelector('[data-nt1-new]'), l = document.querySelector('[data-nt1-ltools]'); const r = b.getBoundingClientRect(), lr = l.getBoundingClientRect(); return [Math.round(r.top), Math.round(document.querySelector('[data-nt1-chips]').getBoundingClientRect().top), r.right <= document.querySelector('[data-nt1-list]').getBoundingClientRect().right + 1]; }")
                check(f"{tag} 2 + Idea sits in the card's top row (never on its own line in the header)", abs(ia[0] - ia[1]) <= 40 and ia[2], ia)
                page.click("[data-nt1-find]"); page.wait_for_timeout(200)
                check(f"{tag} 2 ⌕ Find still opens the search field (in the card)", js(page, B.VIS, "[data-nt1-q]") and js(page, "()=>!!document.querySelector('[data-nt1-lt] [data-nt1-q]')"))
                js(page, "()=>{ myFindOpen = false; myQ = ''; renderWatchlist(); }")
            else:
                check(f"{tag} 2 ai: top row = chips (All · Themes · Trades · Needs evidence · Ready) + Import JSON; header has neither", all(x in m["ltTxt"] for x in ("All", "Themes", "Trades", "Needs evidence", "Ready", "Import JSON")) and "Import JSON" not in m["headTxt"], m)
        check(f"{tag} 2 no overflow · no page errors", js(page, B.OVER) and not pe, pe[:3])
    finally:
        b.close()


def part_phone(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h)
    try:
        N.goto_watch(page); T.to_my(page); page.wait_for_timeout(250)
        m = js(page, "()=>({lt:!!document.querySelector('[data-nt1-list] [data-nt1-lt]'), head:!!document.querySelector('[data-lr5-head] [data-nt1-chips]'), sz:[...document.querySelectorAll('[data-nt1-lt] button')].filter(b=>b.getClientRects().length).map(b=>Math.round(b.getBoundingClientRect().height))})")
        check(f"{tag} 2 phone: chips + Find + Idea in the list card · 44px targets · no overflow", m["lt"] and not m["head"] and m["sz"] and all(x >= 44 for x in m["sz"]) and js(page, B.OVER), m)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 800), (390, 844)):
            part_today(pw, w, h)
        for w, h in ((1440, 900), (1280, 800)):
            part_watch(pw, w, h)
        part_phone(pw, 390, 844)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY nt1c: {len(results) - len(bad)}/{len(results)}")
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
