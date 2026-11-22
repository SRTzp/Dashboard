#!/usr/bin/env python3
"""NT2c — TV undo · Today › Ideas fill to 3 + AI row anatomy · Today resizable split · Watch › AI list fits any width (docs/briefs/NT2c-brief.md).
Run: python3 tests/run_tests_nt2c.py   (NT2C_SHOTS=1 writes docs/screenshots/nt2c-*.png)"""
import sys, os
from playwright.sync_api import sync_playwright
from re1d_common import js, check, results
import nt1_common as N
import run_tests_nt1 as T
import run_tests_nt1b as B
import run_tests_nt2 as P2

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")


def shot(page, name, **kw):
    if os.environ.get("NT2C_SHOTS"):
        os.makedirs(SHOTS, exist_ok=True); page.screenshot(path=os.path.join(SHOTS, "nt2c-%s.png" % name), **kw)


def seed_ai_rich(page, iid, name, recheck, n_g=7, n_l=6, one=None):
    import lr5_common as C
    d = C.idea_doc(iid, name); d["status"] = "need_evidence"; d["recheck"] = {"date": recheck}
    d["candidates"] = [{"sym": s, "name": s, "state": "study", "segments": [], "relevance_src": "10-K"} for s in ["CNC", "HCA", "UNH", "MMM", "ELV", "CVS", "HUM", "CI", "MOH"][:n_g]]
    d["losers"] = [{"sym": s, "why": "x"} for s in ["HUT", "STRL", "MOD", "CRWV", "NVDA", "AMD", "TSM"][:n_l]]
    if one: d["idea"] = dict(d.get("idea") or {}, change=one)
    page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas').doc(i).set(d)", [iid, {"idea": {k: v for k, v in d.items() if k != "log"}, "idea_log": d.get("log", []), "user": {}}])
    page.wait_for_timeout(300)


ROWS = "()=>[...document.querySelectorAll('[data-nt1b-it]')].map(r=>r.dataset.nt1bIt)"
WROWS = "()=>[...document.querySelectorAll('[data-nt2c-watch]')].map(r=>r.dataset.nt2cWatch)"
# every row: height (px) vs the line height of its tallest text, ellipsis, clipped descendants
FIT = """(sel)=>[...document.querySelectorAll(sel)].map(r=>{
  const cr = r.getBoundingClientRect(); const bad = []; let ell = 0;
  r.querySelectorAll('*').forEach(e=>{ const cs = getComputedStyle(e); if(cs.textOverflow === 'ellipsis' && cs.overflow !== 'visible') ell++; const b = e.getBoundingClientRect(); if(b.width && b.right > cr.right + 0.5) bad.push(e.className); if(e.scrollWidth > e.clientWidth + 1 && cs.overflow !== 'visible' && e.clientWidth) bad.push('scroll:' + e.className); });
  const lines = e=>{ if(!e) return 0; const lh = parseFloat(getComputedStyle(e).lineHeight) || 18; return Math.round(e.getBoundingClientRect().height / lh); };
  return {key:r.dataset.nt1bIt || r.dataset.nt2cWatch, ell, bad, t:lines(r.querySelector('.nt1b-tt .t')), n:lines(r.querySelector('.n')), w:Math.round(cr.width), txt:r.innerText.replace(/\\s+/g, ' ')};
})"""


def part_tv(pw):
    tag = "[tv undo]"
    b, page, pe = N.open_nt1(pw, 1440, 900, my_docs=False, notes=False)
    try:
        t0 = B.td(page); B.quiet_fixture_ai(page); now = P2.now_iso(page)
        B.seed_my(page, {"g": P2.idea(1, ("sat", "XAU"), P2.GOLD, t0, B.add(t0, 5), scs=[P2.sc("pullback", 3290, 3340), P2.sc("breakout", 3500, i="B")], view="bull", next=None, lastPx={"v": 3412, "at": now}, invLevel=2900)})
        T.to_my(page, "g"); page.wait_for_timeout(400)
        tv0 = js(page, "()=>({t:document.querySelector('[data-nt1d-tv]').innerText.replace(/\\s+/g, ' '), set:!!document.querySelector('[data-nt1d-tvset]'), undo:!!document.querySelector('[data-nt1d-tvundo]')})")
        check(f"{tag} before: TV · Copy A · Copy B · Copy ✕ · ✓ Set, no Undo", tv0["set"] and not tv0["undo"] and "Copy A" in tv0["t"] and "Copy ✕" in tv0["t"], tv0)
        page.click("[data-nt1d-tvset]"); page.wait_for_timeout(400)
        s = js(page, """()=>{ const r = document.querySelector('[data-nt1d-tv]'), d = r.querySelector('.d.ok'), u = r.querySelector('[data-nt1d-tvundo]');
          return {t:r.innerText.replace(/\\s+/g, ' '), same:!!u && Math.abs(d.getBoundingClientRect().top - u.getBoundingClientRect().top) < 8, right:!!u && u.getBoundingClientRect().left > d.getBoundingClientRect().right + 40, tv:myList.find(x=>x.id==='g').tvAlert, green:getComputedStyle(d).color}; }""")
        db = page.evaluate("()=>firebase.firestore().collection('users').doc('testuid').collection('ideas_my').doc('g').get().then(x=>x.data().tvAlert)")
        check(f"{tag} ✓ Set → `TV alerts set ✓` (green) + Undo at the right of the SAME line · Firestore tvAlert true", s["t"].startswith("TV alerts set ✓") and "Undo" in s["t"] and s["same"] and s["right"] and s["tv"] is True and db is True, [s, db])
        shot(page, "tv-set")
        js(page, "()=>new Promise(r=>setTimeout(r, 7000))")
        still = js(page, "()=>!!document.querySelector('[data-nt1d-tvundo]')")
        check(f"{tag} Undo stays after the 6 s toast window (not a timed toast)", still)
        page.focus("[data-nt1d-tvundo]"); page.keyboard.press("Enter"); page.wait_for_timeout(400)
        u = js(page, "()=>({set:!!document.querySelector('[data-nt1d-tvset]'), copy:document.querySelectorAll('[data-nt1d-copy]').length, inv:!!document.querySelector('[data-nt1d-copyinv]'), undo:!!document.querySelector('[data-nt1d-tvundo]'), tv:myList.find(x=>x.id==='g').tvAlert, dlg:[...document.querySelectorAll('[role=dialog]')].some(d=>d.offsetParent)})")
        db = page.evaluate("()=>firebase.firestore().collection('users').doc('testuid').collection('ideas_my').doc('g').get().then(x=>x.data().tvAlert)")
        check(f"{tag} Undo (keyboard Enter) → chips back · tvAlert false in the app and Firestore · no dialog", u["set"] and u["copy"] == 2 and u["inv"] and not u["undo"] and u["tv"] is False and db is False and not u["dlg"], [u, db])
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def part_today(pw, w=1440):
    tag = "[today fill]"
    b, page, pe = N.open_nt1(pw, w, 900, my_docs=False, notes=False)
    try:
        t0 = B.td(page); now = P2.now_iso(page)
        B.quiet_fixture_ai(page)
        seed_ai_rich(page, "ai-late", "US 30 Outperform", B.add(t0, -16))
        B.seed_my(page, {"x": P2.idea(1, ("sat", "XAU"), "Opportunity to Buy Gold", t0, B.add(t0, 9), scs=[P2.sc("pullback", 3290, 3340)], view="bull", lastPx={"v": 3650, "at": now}),
                         "y": P2.idea(2, ("sat", "BTC"), "Pullback to 82k", t0, B.add(t0, 9), scs=[P2.sc("pullback", 80000, 82000)], view="bull", lastPx={"v": 95000, "at": now}),
                         "z": P2.idea(3, ("sat", "XAG"), "Silver range", t0, B.add(t0, 9), scs=[P2.sc("breakout", 40)], view="bull", lastPx={"v": 30, "at": now}),
                         "dr": P2.idea(4, ("sat", "ETH"), "Dropped one", t0, B.add(t0, 9), scs=[P2.sc("pullback", 3000, 3100)], view="bull", lastPx={"v": 3300, "at": now}, dropped=True),
                         "sn": P2.idea(5, ("sat", "SOL"), "Snoozed one", t0, B.add(t0, 9), scs=[P2.sc("pullback", 150, 160)], view="bull", lastPx={"v": 170, "at": now}, snoozeTo=B.add(t0, 3))})
        B.to_today(page)
        due = js(page, ROWS); wat = js(page, WROWS)
        lab = js(page, "()=>({t:[...document.querySelectorAll('[data-nt2c-wlabel]')].map(e=>e.innerText), cs:(e=>({fs:getComputedStyle(e).fontSize, tt:getComputedStyle(e).textTransform}))(document.querySelector('[data-nt2c-wlabel]'))})")
        check(f"{tag} 1 due + 2 watching: due AI first, then My ideas nearest first (XAU → BTC); dropped / snoozed never fill", due == ["ai:ai-late"] and wat == ["my:x", "my:y"] and "my:dr" not in wat and "my:sn" not in wat, [due, wat])
        dd = js(page, "()=>nt2cWatching(9).filter(x=>x.kind==='my').map(x=>x.dist)")
        check(f"{tag} My ideas come nearest first (XAU 8% → BTC 14% → XAG 33%), then AI ideas by check date", dd == sorted(dd) and js(page, "()=>nt2cWatching(9).map(x=>x.kind)")[:4] == ["my", "my", "my", "ai"], dd)
        check(f"{tag} one small `WATCHING` label (10px) · header `1 due` + `N open`", lab["t"] == ["WATCHING"] and lab["cs"]["fs"] == "10px" and js(page, "()=>document.querySelector('[data-nt1b-due]').innerText") == "1 due", lab)
        wr = js(page, "()=>[...document.querySelectorAll('[data-nt2c-watch]')].map(r=>({btn:r.querySelector('[data-nt1b-btn]').innerText, pill:r.querySelector('[data-nt1b-pill]').innerText, cls:r.querySelector('[data-nt1b-pill]').className, tc:getComputedStyle(r.querySelector('.t')).color, dots:!!r.querySelector('.nt1b-dots')}))")
        check(f"{tag} watching rows: plain `Open ›` · ONE pill (blue distance for My ideas) · grey title · no ⋯", all(x["btn"] == "Open ›" and not x["dots"] for x in wr) and "p-b" in wr[0]["cls"] and " to " in wr[0]["pill"], wr)
        ai = js(page, "(s)=>{ const r = document.querySelector(s); return {tag:r.querySelector('[data-nt1b-tag]').innerText, sub:r.querySelector('[data-nt1b-sub]').innerText, pill:r.querySelector('[data-nt1b-pill]').innerText, cls:r.querySelector('[data-nt1b-pill]').className, txt:r.innerText.replace(/\\s+/g, ' ')}; }", "[data-nt1b-it='ai:ai-late']")
        check(f"{tag} overdue AI row: line 2 = `check <date>` + amber `16 days late` (no `AI generated` text)", ai["pill"] == "16 days late" and "p-a" in ai["cls"] and ai["sub"].startswith("check ") and "AI generated" not in ai["txt"], ai)
        shot(page, "today-fill")
        # 3 due → no WATCHING label
        B.seed_my(page, {"d1": P2.idea(11, ("sat", "XAU"), "Due one", B.add(t0, -5), B.add(t0, -3), scs=[P2.sc("pullback", 3290, 3340)], view="bull"),
                         "d2": P2.idea(12, ("sat", "BTC"), "Due two", B.add(t0, -5), B.add(t0, -2), scs=[P2.sc("pullback", 80000, 82000)], view="bull")})
        B.to_today(page)
        d3 = js(page, "()=>({due:document.querySelectorAll('[data-nt1b-it]').length, lab:document.querySelectorAll('[data-nt2c-wlabel]').length, w:document.querySelectorAll('[data-nt2c-watch]').length})")
        check(f"{tag} 3 due → no WATCHING label, no watching rows", d3 == {"due": 3, "lab": 0, "w": 0}, d3)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def part_today_fit(pw):
    tag = "[today rows fit]"
    b, page, pe = N.open_nt1(pw, 1440, 900, my_docs=False, notes=False)
    try:
        t0 = B.td(page); now = P2.now_iso(page)
        B.quiet_fixture_ai(page)
        seed_ai_rich(page, "ai-late", "US 30 Outperform", B.add(t0, -16))
        B.seed_my(page, {"x": P2.idea(1, ("sat", "XAU"), "Buy Gold", t0, B.add(t0, 9), scs=[P2.sc("pullback", 3290, 3340)], view="bull", lastPx={"v": 3650, "at": now}),
                         "y": P2.idea(2, ("sat", "BTC"), "BTC 82k", t0, B.add(t0, 9), scs=[P2.sc("pullback", 80000, 82000)], view="bull", lastPx={"v": 95000, "at": now})})
        B.to_today(page)
        for rw in (340, 360, 440, 560, 600):
            js(page, "(w)=>{ splitApply(TD_SPLIT, w, false); }", rw); page.wait_for_timeout(150)
            got = js(page, "()=>document.querySelector('.lr2-side').getBoundingClientRect().width")
            r = js(page, FIT, "[data-nt1b-it], [data-nt2c-watch]")
            check(f"{tag} right column {rw}px (is {round(got)}): every Ideas row ≤ 2 lines · no ellipsis · nothing past the right edge", abs(got - rw) < 2 and all(x["ell"] == 0 and not x["bad"] and x["t"] <= 2 and x["n"] <= 2 for x in r), [x for x in r if x["ell"] or x["bad"] or x["t"] > 2 or x["n"] > 2] or got)
        # Act column rows still fit at both extremes
        for rw in (340, 600):
            js(page, "(w)=>{ splitApply(TD_SPLIT, w, false); }", rw); page.wait_for_timeout(150)
            o = js(page, """()=>{ const side = document.querySelector('.lr2-side'), sr = side.getBoundingClientRect(); const bad = [];
              side.querySelectorAll('*').forEach(e=>{ const cs = getComputedStyle(e); if(cs.textOverflow === 'ellipsis' && e.scrollWidth > e.clientWidth + 1 && !e.closest('.lr2-ti, .td5-ti')) bad.push(e.className); const b = e.getBoundingClientRect(); if(b.width && b.right > sr.right + 1 && cs.position !== 'absolute') bad.push('over:' + e.className); });
              return {bad, sw:document.documentElement.scrollWidth <= document.documentElement.clientWidth}; }""")
            check(f"{tag} right column {rw}px: Ideas / To do / Risk room — no ellipsis, nothing past the edge, no sideways scroll", not o["bad"] and o["sw"], o)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def part_split(pw):
    tag = "[today split]"
    b, page, pe = N.open_nt1(pw, 1440, 900, my_docs=False, notes=False)
    try:
        B.to_today(page); page.wait_for_timeout(300)
        W = lambda: js(page, "()=>{ const s = document.querySelector('.lr2-side').getBoundingClientRect(), a = document.querySelector('.lr2-actcol').getBoundingClientRect(); return [Math.round(a.width), Math.round(s.width)]; }")
        h = js(page, """()=>{ const h = document.querySelector('[data-td-rz]'), r = h.getBoundingClientRect(); return {role:h.getAttribute('role'), o:h.getAttribute('aria-orientation'), min:h.getAttribute('aria-valuemin'), max:h.getAttribute('aria-valuemax'), now:h.getAttribute('aria-valuenow'), tab:h.tabIndex, w:Math.round(r.width), cur:getComputedStyle(h).cursor, op:getComputedStyle(h, '::after').opacity}; }""")
        w0 = W()
        check(f"{tag} handle: role=separator · vertical · 8px · col-resize · tabindex 0 · aria 340–600 · default right column 440", h["role"] == "separator" and h["o"] == "vertical" and h["w"] == 8 and h["cur"] == "col-resize" and h["tab"] == 0 and h["min"] == "340" and h["now"] == "440" and w0[1] == 440, [h, w0])

        def pos():
            return js(page, "()=>{ const r = document.querySelector('[data-td-rz]').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")

        def drag(dx):
            x, y = pos(); page.mouse.move(x, y); page.mouse.down(); page.mouse.move(x + dx, y, steps=6); page.mouse.up(); page.wait_for_timeout(200)
        drag(-60); w1 = W()
        check(f"{tag} drag −60 → right column 500 · saved in localStorage `td.rightW`", w1[1] == 500 and js(page, "()=>localStorage.getItem('td.rightW')") == "500", [w1])
        shot(page, "today-resized")
        js(page, "()=>{ TD_SPLIT.val = null; document.documentElement.style.removeProperty('--td-right'); todayRefresh(true); }"); page.wait_for_timeout(200)
        w2 = W(); js(page, "()=>{ splitLoad(TD_SPLIT); todayRefresh(true); }"); page.wait_for_timeout(250); w3 = W()
        check(f"{tag} after a reload (state wiped, `splitLoad` = the start-up read) the right column is 500 again", w2[1] == 440 and w3[1] == 500, [w2, w3])
        drag(-900); w4 = W()
        check(f"{tag} clamp: far left → right column grows but the left column stays ≥ 640 (and ≤ 600)", w4[0] >= 640 and 500 < w4[1] <= 600, w4)
        drag(+900); w5 = W()
        check(f"{tag} clamp: far right → right column stops at 340", w5[1] == 340, w5)
        page.focus("[data-td-rz]"); page.keyboard.press("ArrowLeft"); page.wait_for_timeout(100); k1 = W()[1]
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(100); k2 = W()[1]
        page.keyboard.press("End"); page.wait_for_timeout(100); k3 = W()[1]
        page.keyboard.press("Home"); page.wait_for_timeout(100); k4 = W()[1]
        check(f"{tag} keyboard: ← grows by 20, → shrinks by 20, End = widest, Home = 340", k1 == 360 and k2 == 340 and k3 > 340 and k4 == 340, [k1, k2, k3, k4])
        page.keyboard.press("Enter"); page.wait_for_timeout(100); e1 = W()[1]
        drag(-40); page.dblclick("[data-td-rz]"); page.wait_for_timeout(100); e2 = W()[1]
        check(f"{tag} Enter and double-click both reset to 440 (and forget the saved width)", e1 == 440 and e2 == 440 and js(page, "()=>localStorage.getItem('td.rightW')") is None, [e1, e2])
        # NT2 split unchanged
        check(f"{tag} the NT2 My ideas splitter still uses the same helper (`nt.listW`, 380 default)", js(page, "()=>[SPLITS.nt.key, SPLITS.nt.def, SPLITS.td.key, typeof splitInit]") == ["nt.listW", 380, "td.rightW", "function"])
        page.set_viewport_size({"width": 1000, "height": 800}); page.wait_for_timeout(300)
        check(f"{tag} hidden below 1100px (phone order unchanged)", not js(page, "()=>{ const h = document.querySelector('[data-td-rz]'); return !!h && h.getBoundingClientRect().width > 0; }"))
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def part_ai(pw):
    tag = "[ai list]"
    b, page, pe = N.open_nt1(pw, 1440, 900, my_docs=False, notes=False)
    try:
        t0 = B.td(page)
        seed_ai_rich(page, "ai-a", "US 30 Outperform: Democrats win both House and Senate so gridlock caps fiscal expansion", B.add(t0, -5), 7, 6,
                     "4 พ.ย. Dow ปิด 53,356.12 (+3.03%) ดีสุดตั้งแต่ 9 เม.ย. 2025 · S&P 500 +1.58% · Nasdaq +1.44% · ทอง spot กลับเหนือ $4,000 และ yield ลงแรงหลังผลโหวตออก ทำให้ตลาดอ่านว่า gridlock จำกัด fiscal expansion ราคาหุ้น large-cap ที่ไม่ใช่ AI จึงได้เปรียบ")
        seed_ai_rich(page, "ai-b", "Risk-Off??", B.add(t0, 22), 1, 1, "short")
        js(page, "()=>{ switchTab('journal'); switchTab('watch'); wlView = 'idea'; nt1Seg = 'ai'; renderWatchlist(); }"); page.wait_for_timeout(500)
        for lw in (300, 380, 500):
            js(page, "(w)=>{ splitApply(NT1_SPLIT, w, false); renderWatchlist(); }", lw); page.wait_for_timeout(350)
            o = js(page, """()=>{ const list = document.querySelector('.nt1-list'), lr = list.getBoundingClientRect(), out = {w:Math.round(lr.width), over:[], ell:0, share:[], plus:[], hdr:null, rows:0};
              list.querySelectorAll('.nt1-ai').forEach(r=>{ out.rows++;
                r.querySelectorAll('*').forEach(e=>{ if(e.hidden || e.closest('[hidden]')) return; const b = e.getBoundingClientRect(); if(b.width && b.right > lr.right + 0.5) out.over.push(e.className + ':' + e.innerText.slice(0, 12)); const cs = getComputedStyle(e); if(cs.textOverflow === 'ellipsis' && cs.overflow !== 'visible') out.ell++; });
                const ti = r.querySelector('.ideaRN').getBoundingClientRect(), pi = r.querySelector('[data-nt1-st]').getBoundingClientRect(); if(!(pi.top >= ti.bottom - 1)) out.share.push(r.dataset.idea);
                r.querySelectorAll('.nt2c-ch').forEach(c=>{ const all = c.querySelectorAll('.nt1-tk'), hid = [...all].filter(x=>x.hidden).length, n = c.querySelector('[data-nt2c-n]') || {hidden:true, textContent:''}; const shown = [...all].filter(x=>!x.hidden); const tops = new Set(shown.map(x=>Math.round(x.getBoundingClientRect().top))); out.plus.push({ok:(hid === 0 ? n.hidden : n.textContent === '+' + hid), one:tops.size <= 1, hid, tot:all.length}); });
              });
              const lt = list.querySelector('[data-nt1-lt]'); out.hdr = {r:Math.round(lt.getBoundingClientRect().right - lr.right), h:Math.round(lt.getBoundingClientRect().height), txt:lt.innerText.replace(/\\s+/g, ' '), imp:!!lt.querySelector('[data-nt1-import]')};
              return out; }""")
            check(f"{tag} list {lw}px (is {o['w']}): no element past the card's right edge · no ellipsis · title never shares a line with the status pill", abs(o["w"] - lw) < 2 and not o["over"] and o["ell"] == 0 and not o["share"] and o["rows"] >= 2, o)
            check(f"{tag} list {lw}px: Gains / Loses are one row each · `+n` = number of hidden chips", all(x["ok"] and x["one"] for x in o["plus"]) and (lw > 300 or any(x["hid"] > 0 for x in o["plus"])), o["plus"])
            check(f"{tag} list {lw}px: header chips present, Import JSON is an icon button (still `Import JSON`)", all(k in o["hdr"]["txt"] for k in ("All", "Themes", "Trades", "Needs evidence", "Ready")) and o["hdr"]["imp"] and o["hdr"]["r"] <= 0, o["hdr"])
            if lw in (300, 500):
                js(page, "()=>{ const l = document.querySelector('#wlListBody'); const r = document.querySelector('[data-idea=ai-a]'); l.scrollTop = r.offsetTop - 4; }"); page.wait_for_timeout(120)
                shot(page, "ai-list-%d" % lw)
        sm = js(page, "()=>[...document.querySelectorAll('.nt1-ai')].map(r=>{ const t = r.querySelector('.nt2c-sum'), m = r.querySelector('[data-nt2c-more]'); return {id:r.dataset.idea, clamped:t.scrollHeight > t.clientHeight + 1, more:!!m && !m.hidden, lh:Math.round(t.getBoundingClientRect().height / parseFloat(getComputedStyle(t).lineHeight))}; })")
        check(f"{tag} long summary: max 3 lines and a visible `more` link; short summary: no `more`", any(x["clamped"] and x["more"] and x["lh"] <= 3 for x in sm) and all(x["clamped"] == x["more"] for x in sm), sm)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        part_tv(pw)
        part_today(pw)
        part_today_fit(pw)
        part_split(pw)
        part_ai(pw)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY nt2c: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
