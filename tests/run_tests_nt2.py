#!/usr/bin/env python3
"""NT2 — My ideas: Scenarios (Pullback zone / Breakout level) · reasons visible · In plan · flexible width (docs/briefs/NT2-brief.md).
1 migration · 2 trigger logic · 3 page layout · 4 card · 5 sheet · 6 TradingView copy · 7 Today + Make plan · 8 drag-to-resize.
Run: python3 tests/run_tests_nt2.py   (NT2_SHOTS=1 writes docs/screenshots/nt2-*.png)"""
import sys, os, re, base64, json
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import nt1_common as N
import run_tests_nt1 as T
import run_tests_nt1b as B

TXT, VIS, DOC = B.TXT, B.VIS, B.DOC
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")
SAMPLE = os.path.join(HERE, "..", "docs", "briefs", "nt2", "nt2-watch-full.html")
GOLD = "Opportunity to Buy Gold"
TV = "https://www.tradingview.com/x/AbC123/"


def sample_png():
    html = open(SAMPLE, encoding="utf-8").read()
    m = re.search(r"data:image/(?:png|jpeg|jpg);base64,([A-Za-z0-9+/=]+)", html)
    return base64.b64decode(m.group(1))


IMG = sample_png()


def shot(page, name, **kw):
    if os.environ.get("NT2_SHOTS"):
        os.makedirs(SHOTS, exist_ok=True); page.screenshot(path=os.path.join(SHOTS, "nt2-%s.png" % name), **kw)


def stub(page):
    page.route("https://s3.tradingview.com/**", lambda r: r.fulfill(status=200, content_type="image/png", body=IMG))


def clip(page, mode="ok"):
    page.evaluate("""(mode)=>{ window.__clip = ''; Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:t=>{ if(mode==='deny') return Promise.reject(new Error('denied')); window.__clip = t; return Promise.resolve(); }}}); if(mode==='deny') document.execCommand = ()=>false; }""", mode)


def now_iso(page, h=0):
    return js(page, "(d)=>new Date(Date.now() + d * 3600000).toISOString()", h)


def sc(kind, a, b=None, note="", hit=None, i="A"):
    if kind == "pullback":
        return {"id": i, "kind": "pullback", "lo": a, "hi": b, "level": None, "note": note, "hitAt": hit}
    return {"id": i, "kind": "breakout", "lo": None, "hi": None, "level": a, "note": note, "hitAt": hit}


def idea(i, subj, title, t0, check_on=None, scs=None, **x):
    d = B.mkmy(i, subj, title, B.add(t0, -1), check_on if check_on is not None else B.add(t0, 5), **x)
    d["next"] = x.get("next")
    if scs is not None: d["scenarios"] = scs
    return d


def state(page, m):
    return js(page, "(m)=>{ const s = nt1bLevelState(m); return {state:s.state, sc:s.sc && s.sc.id, dist:s.distPct, old:s.old, list:s.list.map(x=>({id:x.id, hit:x.hit, cond:x.cond, dist:x.dist}))}; }", m)


def mm(subj, view, scs, px, inv=None, side=None, ago_h=0, hit=None):
    m = {"subject": {"type": subj[0], "key": subj[1]}, "title": "T", "view": view, "side": side, "scenarios": scs, "invLevel": inv, "lastPx": None, "planId": None}
    return m


def save(page):
    page.click("[data-nt1-save]"); page.wait_for_timeout(350)


def edit(page, i):
    js(page, "(i)=>nt1SheetOpen({id:i})", i); page.wait_for_timeout(250)


GEOM = """()=>{ const q = s=>document.querySelector(s), r = e=>{ const b = e.getBoundingClientRect(); return {l:Math.round(b.left), t:Math.round(b.top), r:Math.round(b.right), b:Math.round(b.bottom), w:Math.round(b.width), h:Math.round(b.height)}; };
  return {list:r(q('.nt1-list')), det:r(q('.nt1-det')), head:r(q('.nt1-dh')), chart:r(q('[data-nt1-chartw]')), card:r(q('[data-nt1b-block]')), notes:q('[data-nt1-notes]') && r(q('[data-nt1-notes]')), foot:r(q('[data-nt1-foot]')),
    find:r(q('[data-nt1-find]')), lt:r(q('[data-nt1-lt]')), cells:[...document.querySelectorAll('[data-nt1-notes] [data-nt1-ang]')].map(e=>r(e)), cols:getComputedStyle(q('[data-nt1-notes]')).gridTemplateColumns.split(' ').length,
    img:(()=>{ const i = q('[data-nt1-chartw] img'); return [i.naturalWidth, i.naturalHeight]; })(), page:document.documentElement.scrollHeight <= innerHeight + 1, detScroll:q('.nt1-det').scrollHeight <= q('.nt1-det').clientHeight + 1}; }"""

LABELS = """()=>[...document.querySelectorAll('[data-nt1b-block] [data-nt1r-lbl]')].map(e=>{ const b = e.getBoundingClientRect(); return {k:e.dataset.nt1rLbl, side:e.dataset.nt1rSide, l:b.left, r:b.right, t:b.top, b:b.bottom, tx:e.innerText.replace(/\\s+/g,' ').trim()}; })"""


def overlap(ls):
    for i in range(len(ls)):
        for j in range(i + 1, len(ls)):
            a, b = ls[i], ls[j]
            if a["l"] < b["r"] and b["l"] < a["r"] and a["t"] < b["b"] and b["t"] < a["b"]: return [a["k"], b["k"]]
    return None


def part_logic(pw):
    tag = "[logic]"
    b, page, pe = N.open_nt1(pw, 1440, 900, my_docs=False, notes=False)
    try:
        t0 = B.td(page); B.quiet_fixture_ai(page); now = now_iso(page)
        # ───── 1 · migration
        old = idea(1, ("sat", "XAU"), GOLD, t0, view="bull", next="Wait for a reversal candle on H4", level=3340, invLevel=3200, ang={"tech": "Support"})
        old.update({"levelDir": "down", "invDir": "down", "lastPx": {"v": 3412, "at": now}, "hitAt": None})
        up = idea(2, ("stock", "AVGO"), "Range 160–190", t0, view="bull", next="x" * 90, level=190); up["levelDir"] = "up"
        sell = idea(3, ("sat", "BTC"), "Sell the rally", t0, view="bear", next="Short it", level=90000); sell["levelDir"] = "up"
        sell2 = idea(4, ("sat", "OIL"), "Sell the break", t0, view="bear", next="Short it", level=70); sell2["levelDir"] = "down"
        B.seed_my(page, {"old": old, "up": up, "sell": sell, "sell2": sell2}); T.to_my(page, "old"); page.wait_for_timeout(300)
        mg = js(page, "()=>['old','up','sell','sell2'].map(i=>{ const m = myList.find(x=>x.id===i); return nt1Scs(m).map(s=>[s.id, s.kind, s.lo, s.hi, s.level, s.note, s.hitAt]); })")
        check("[migrate] NT1d idea (level 3,340 down, Bull, next, invLevel 3,200) → A pullback 3,340–3,340 · note = next · Wrong 3,200", mg[0] == [["A", "pullback", 3340, 3340, None, "Wait for a reversal candle on H4", None]] and js(page, "()=>myList.find(x=>x.id==='old').invLevel") == 3200, mg[0])
        check("[migrate] Bull + `up` → breakout · next > 80 chars → note empty · Bear + `up` → pullback (sell) · Bear + `down` → breakout", mg[1][0][1] == "breakout" and mg[1][0][5] == "" and mg[2][0][1] == "pullback" and mg[3][0][1] == "breakout", mg)
        cp = js(page, "()=>{ nt1Copy('up'); return window.__nt1LastCopy; }")
        check("[migrate] a long old next step stays stored and shows only in the Copy export", "Next step: " + "x" * 90 in cp and js(page, "()=>myList.find(x=>x.id==='up').next").startswith("xxx"), cp[-120:])
        d0 = js(page, DOC, "old")
        check("[migrate] nothing is written by reading (no `scenarios` stored yet)", d0.get("scenarios") is None and d0["level"] == 3340)
        edit(page, "old"); page.fill("#nt1fTitle", GOLD + " v2"); save(page)
        d1 = js(page, DOC, "old")
        check("[migrate] Save writes `scenarios` · old level / levelDir / next / invLevel are NOT deleted · invDir written for compatibility", d1["scenarios"] and d1["scenarios"][0]["kind"] == "pullback" and d1["scenarios"][0]["lo"] == 3340 and d1["level"] == 3340 and d1["levelDir"] == "down" and d1["next"] == "Wait for a reversal candle on H4" and d1["invLevel"] == 3200 and d1["invDir"] == "down", d1)
        # ───── 2 · trigger logic
        G = "()=>({})"
        def S(scs, px, view="bull", inv=None, subj=("sat", "XAU"), side=None):
            m = mm(subj, view, scs, px, inv, side); m["lastPx"] = {"v": px, "at": now_iso(page)} if subj[0] != "stock" else None
            return state(page, m)
        PB, BO = [sc("pullback", 3290, 3340)], [sc("breakout", 3500)]
        r = [S(PB, 3330)["state"], S(PB, 3280)["state"], S(PB, 3340)["state"], S(PB, 3345)["state"], S(BO, 3500)["state"], S(BO, 3499)["state"], S(BO, 3600)["state"]]
        check("[logic] buy pullback: hit inside the zone, below it and on `hi` · just above it is `near` (not hit) · buy breakout: hit at/above level", r == ["hit", "hit", "hit", "near", "hit", "near", "hit"], r)
        r = [S(PB, 3290, "bear")["state"], S(PB, 3250, "bear")["state"], S(PB, 3300, "bear")["state"], S([sc("breakout", 3200)], 3200, "bear")["state"], S([sc("breakout", 3200)], 3201, "bear")["state"]]
        check("[logic] sell pullback (rally zone): hit when px ≥ lo · sell breakout (breakdown): hit when px ≤ level", r == ["hit", "near", "hit", "hit", "near"], r)
        w1, w2, w3 = S(PB, 3199, inv=3200), S(PB, 3601, "bear", inv=3600), S(PB, 3201, inv=3200)
        check("[logic] Wrong: buy px ≤ Wrong-if · sell px ≥ Wrong-if · WRONG WINS over a hit in the same moment", w1["state"] == "wrong" and w2["state"] == "wrong" and w3["state"] == "hit" and w1["list"][0]["hit"], [w1, w2, w3])
        # distance + near + at level
        n1, n2, n3 = S(PB, 3410), S(PB, 3480), S(BO, 3499.9)
        check("[logic] distance: buy pullback (px−hi)/px · near within 3 % → state near, the nearest scenario · 4 % → none", abs(n1["dist"] - (3410 - 3340) / 3410 * 100) < .001 and n1["state"] == "near" and n2["state"] == "none" and n1["sc"] == "A", [n1, n2])
        bo = S(BO, 3300)
        check("[logic] buy breakout distance (level−px)/px · sell mirrored", abs(bo["dist"] - (3500 - 3300) / 3300 * 100) < .001 and abs(S(PB, 3250, "bear")["dist"] - (3290 - 3250) / 3250 * 100) < .001, bo)
        B.seed_my(page, {"lv": idea(5, ("sat", "XAU"), "At level", t0, scs=[sc("breakout", 3500)], view="bull", lastPx={"v": 3499.9, "at": now}, next=None)}); T.to_my(page, "lv"); page.wait_for_timeout(250)
        pt = js(page, TXT, '[data-nt1b-block] [data-nt1s-pill]'); lp = js(page, TXT, '[data-nt1-my="lv"] [data-nt1b-pill]')
        check("[logic] |dist| < 0.05 % → text `at level`, never `0.0%`", pt == "at level" and lp == "A at level" and "0.0%" not in js(page, "()=>document.querySelector('[data-nt1-detail]').innerText"), [pt, lp])
        # old price
        B.seed_my(page, {"op": idea(6, ("sat", "BTC"), "Old price", t0, scs=[sc("pullback", 80000, 82000)], view="bull", lastPx={"v": 84000, "at": now_iso(page, -30)}, next=None)}); T.to_my(page, "op"); page.wait_for_timeout(250)
        o = js(page, "()=>({old:nt1bLevelState(myList.find(x=>x.id==='op')).old, tx:!!document.querySelector('[data-nt1d-oldpx]') && document.querySelector('[data-nt1d-oldpx]').innerText})")
        check("[logic] typed price older than 24 h → `old price` shown", o["old"] and o["tx"] == "old price", o)
        # write-once + edit clears only that scenario
        B.seed_my(page, {"wo": idea(7, ("stock", "AMD"), "Write once", t0, scs=[sc("pullback", 95, 100), sc("breakout", 110, i="B")], view="bull", next=None, invLevel=80)}); B.px(page, "AMD", 99.0)
        js(page, "()=>nt1bHitSweep()"); page.wait_for_timeout(500)
        wo = js(page, DOC, "wo"); a0 = wo["scenarios"][0]["hitAt"]
        B.px(page, "AMD", 120.0); js(page, "()=>nt1bHitSweep()"); page.wait_for_timeout(500)
        wo2 = js(page, DOC, "wo"); B.px(page, "AMD", 90.0); js(page, "()=>nt1bHitSweep()"); page.wait_for_timeout(400)
        check("[logic] write-once: A hit at 99 writes hitAt · price moving to 120 hits B but A keeps its first hitAt · back to 90 changes nothing", a0 and wo["scenarios"][1]["hitAt"] is None and wo2["scenarios"][0]["hitAt"] == a0 and wo2["scenarios"][1]["hitAt"] and js(page, DOC, "wo")["scenarios"][1]["hitAt"] == wo2["scenarios"][1]["hitAt"], [wo["scenarios"], wo2["scenarios"]])
        check("[logic] state stays `hit` after the price leaves (never cleared by price moving back)", js(page, "()=>nt1bLevelState(myList.find(x=>x.id==='wo')).state") == "hit")
        wr = idea(8, ("sat", "XAU"), "Edit clears", t0, scs=[sc("pullback", 3290, 3340, hit=now), sc("breakout", 3500, hit=now, i="B")], view="bull", next=None, invLevel=3200, tvAlert=True, lastPx={"v": 3420, "at": now})
        B.seed_my(page, {"ec": wr}); T.to_my(page, "ec"); edit(page, "ec")
        page.fill('[data-nt1s-r="1"] [data-nt1s-f="level"]', "3550"); save(page)
        ec = js(page, DOC, "ec")
        check("[logic] editing B's level clears B's hitAt only · A keeps it · tvAlert → false", ec["scenarios"][0]["hitAt"] == now and ec["scenarios"][1]["hitAt"] is None and ec["scenarios"][1]["level"] == 3550 and ec["tvAlert"] is False, ec["scenarios"])
        edit(page, "ec"); js(page, "()=>{ myList.find(x=>x.id==='ec').tvAlert = true; }"); page.fill("#nt1fTitle", "New title"); page.fill('[data-nt1s-r="0"] [data-nt1s-f="note"]', "a note"); save(page)
        ec2 = js(page, DOC, "ec")
        check("[logic] title / note edits clear nothing (hitAt kept)", ec2["scenarios"][0]["hitAt"] == now and ec2["scenarios"][0]["note"] == "a note", ec2["scenarios"])
        # invLevel edit clears invHitAt + invAckAt
        iw = idea(9, ("sat", "XAU"), "Wrong edit", t0, scs=[sc("pullback", 3290, 3340)], view="bull", next=None, invLevel=3200, tvAlert=True, lastPx={"v": 3420, "at": now}); iw.update({"invHitAt": now, "invAckAt": now})
        B.seed_my(page, {"iw": iw}); edit(page, "iw"); page.fill("#nt1fInv", "3150"); save(page)
        i2 = js(page, DOC, "iw")
        check("[logic] changing Wrong-if clears invHitAt + invAckAt and tvAlert", i2["invLevel"] == 3150 and i2["invHitAt"] is None and i2["invAckAt"] is None and i2["tvAlert"] is False, i2)
        check("[logic] no page errors", not pe, pe[:3])
    finally:
        b.close()


def part_desktop(pw):
    tag = "[1440]"
    b, page, pe = N.open_nt1(pw, 1440, 900, my_docs=False, notes=False)
    try:
        stub(page); t0 = B.td(page); B.quiet_fixture_ai(page); clip(page); now = now_iso(page)
        ang = {"tech": "แนวรับสำคัญ 3,290–3,340 ระดับ Month · EMA ยังชันขึ้น · กรอบบน 3,500 = high เดิม", "sent": "ทองลง ~11% ใน 8 สัปดาห์ · positioning เบาลง", "fund": "ธนาคารกลางยังซื้อต่อ · real yield ลดลง", "macro": "CPI 20:30 พฤหัส · Fed 8–9 ธ.ค."}
        gold = idea(1, ("sat", "XAU"), GOLD, t0, B.add(t0, 10), scs=[sc("pullback", 3290, 3340, "wait for a reversal candle on H4"), sc("breakout", 3500, i="B")], view="bull", chart=TV, builtOn="en-idea-1", ang=ang, next=None, invLevel=3200, lastPx={"v": 3412, "at": now})
        avgo = idea(2, ("stock", "AVGO"), "Range 160–190", t0, B.add(t0, 3), scs=[sc("breakout", 190)], view="bull", next=None)
        mkt = idea(3, ("market", "US"), "Risk-off until CPI", t0, B.add(t0, 4), scs=[], view="bear", next=None)
        B.seed_my(page, {"gold": gold, "avgo": avgo, "mkt": mkt}); B.px(page, "AVGO", 188.0)
        T.to_my(page, "gold"); page.wait_for_timeout(500)
        g = js(page, GEOM)
        check(f"{tag} L list 380 · detail = the rest (880) · gap 20", abs(g["list"]["w"] - 380) <= 1 and abs(g["det"]["w"] - 880) <= 1 and g["det"]["l"] - g["list"]["r"] == 20, [g["list"], g["det"]])
        check(f"{tag} L header sits above the chart (full width) · chart left of the Scenarios card · card top-aligned with the chart", g["head"]["b"] <= g["chart"]["t"] and g["chart"]["r"] <= g["card"]["l"] and abs(g["chart"]["t"] - g["card"]["t"]) <= 2, [g["head"], g["chart"], g["card"]])
        ratio = g["img"][0] / g["img"][1]; box = g["chart"]["w"] / g["chart"]["h"]
        check(f"{tag} L chart box has the image's own ratio (no bars > 2px) and is not stretched to the card height", abs(g["chart"]["w"] / ratio - g["chart"]["h"]) <= 2 and g["chart"]["h"] < g["card"]["h"] + 80, [g["chart"], g["img"], ratio, box])
        check(f"{tag} L Reasons: 2 columns below the chart row (full width) · 4 cells · footer below", g["cols"] == 2 and len(g["cells"]) == 4 and g["notes"]["t"] >= max(g["chart"]["b"], g["card"]["b"]) and g["notes"]["w"] > 800 and g["foot"]["t"] >= g["notes"]["b"] and len({c["l"] for c in g["cells"]}) == 2, g["cells"])
        lab = js(page, "()=>[...document.querySelectorAll('[data-nt1-notes] .rk')].map(e=>[e.innerText, e.scrollWidth <= e.clientWidth + 1, Math.round(e.getBoundingClientRect().width)])")
        check(f"{tag} L reason labels TECH · SENT · FUND · MACRO fit their 44px column", [x[0] for x in lab] == ["TECH", "SENT", "FUND", "MACRO"] and all(x[1] for x in lab), lab)
        check(f"{tag} L no page scroll · detail needs no scroll when filled", g["page"] and g["detScroll"], g)
        check(f"{tag} L `⌕` fully inside the list card · chips + ⌕ on ONE row", g["find"]["r"] <= g["list"]["r"] and g["find"]["l"] >= g["list"]["l"] and g["lt"]["h"] < 60, [g["find"], g["lt"]])
        shot(page, "watch-full")
        # ───── card
        rd = js(page, """()=>{ const q = s=>document.querySelector('[data-nt1b-block] ' + s), l = e=>e ? parseFloat(e.style.left) : null, b = q('[data-nt1r-band="A"]'), r = e=>e.getBoundingClientRect();
            return {band:[l(b), parseFloat(b.style.width)], bt:getComputedStyle(b).backgroundColor, tickB:l(q('[data-nt1r-tick="B"]')), tbc:getComputedStyle(q('[data-nt1r-tick="B"]')).backgroundColor, wrong:l(q('[data-nt1r-tick="wrong"]')), wc:getComputedStyle(q('[data-nt1r-tick="wrong"]')).backgroundColor, now:l(q('[data-nt1r-now]')), nowc:getComputedStyle(q('[data-nt1r-now]')).backgroundColor,
              hdr:q('[data-nt1d-hdr]').innerText, check:q('[data-nt1d-check]').innerText}; }""")
        check(f"{tag} C ruler order: Wrong tick < Pullback band A < now dot < Breakout tick B · blue band / blue tick / amber tick / dark dot", rd["wrong"] < rd["band"][0] < rd["now"] < rd["tickB"] and rd["tbc"] == "rgb(59, 79, 196)" and rd["wc"] == "rgb(217, 146, 26)" and rd["nowc"] == "rgb(20, 22, 26)" and rd["bt"] != "rgba(0, 0, 0, 0)" and rd["hdr"] == "SCENARIOS · WATCHING" and rd["check"].startswith("Check again"), rd)
        ls = js(page, LABELS)
        up = [x for x in ls if x["side"] == "u"]; dn = [x for x in ls if x["side"] == "d"]
        check(f"{tag} C labels: `A 3,290–3,340` and `B 3,500` above · `Wrong 3,200` and `now 3,412 manual` below · no two touching", [x["tx"] for x in up] == ["A 3,290–3,340", "B 3,500"] and sorted(x["tx"] for x in dn) == ["Wrong 3,200", "now 3,412 manual"] and not overlap(ls), ls)
        rows = js(page, """()=>[...document.querySelectorAll('[data-nt1b-block] [data-nt1s-row]')].map(r=>({t:r.innerText.replace(/\\s+/g,' ').trim(), pill:(()=>{ const p = r.querySelector('[data-nt1s-pill]'); const c = getComputedStyle(p); return [p.innerText, c.backgroundColor, c.color, c.borderRadius]; })()}))""")
        check(f"{tag} C rows: `Pullback · note … 2.1% away` / `Breakout … 2.6% away` · scenario numbers are NOT repeated in the rows · pills are real pills (background colour)", rows[0]["t"] == "A Pullback · wait for a reversal candle on H4 2.1% away" and rows[1]["t"] == "B Breakout 2.6% away" and all(r["pill"][1] != "rgba(0, 0, 0, 0)" and float(r["pill"][3].replace("px", "")) > 8 for r in rows) and rows[0]["pill"][1] == "rgb(232, 236, 251)", rows)
        tv = js(page, "()=>document.querySelector('[data-nt1d-tv]').innerText.replace(/\\s+/g,' ')")
        acts = js(page, "()=>document.querySelector('[data-nt1b-block] .acts').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} C TV row `TV Copy A Copy B Copy ✕ ✓ Set` on one line · actions `Snooze 3 days Done … Mark ▾`", tv == "TV Copy A Copy B Copy ✕ ✓ Set" and acts == "Snooze 3 days Done Mark ▾", [tv, acts])
        page.click("[data-nt1d-mark-btn]"); page.wait_for_timeout(120)
        mk = js(page, "()=>[...document.querySelectorAll('[data-nt1d-mark-menu] button')].map(b=>b.innerText)")
        page.keyboard.press("Escape"); page.wait_for_timeout(100)
        check(f"{tag} C Mark ▾ → `A reached · B reached · Idea wrong`", mk == ["A reached", "B reached", "Idea wrong"], mk)
        ell = js(page, """()=>{ const bad = []; document.querySelectorAll('[data-nt1-detail] *, [data-nt1-my] *').forEach(e=>{ if(e.getClientRects().length && getComputedStyle(e).textOverflow === 'ellipsis') bad.push(e.className || e.tagName); }); return bad; }""")
        check(f"{tag} C no text-overflow ellipsis in the detail or the list rows", ell == [], ell)
        # list rows
        lr = js(page, """()=>[...document.querySelectorAll('[data-nt1-my]')].map(r=>({id:r.dataset.nt1My, t2:r.querySelector('.t2').innerText.replace(/\\s+/g,' '), l3:r.querySelector('[data-nt1b-l3]').innerText.replace(/\\s+/g,' '), pills:[...r.querySelectorAll('[data-nt1b-pill]')].map(p=>[p.innerText, getComputedStyle(p).backgroundColor]), blue:[...r.querySelectorAll('.nt1-sl')].map(e=>getComputedStyle(e).color)}))""")
        by = {x["id"]: x for x in lr}
        check(f"{tag} F list row: `A pullback 3,290–3,340 · B breakout 3,500` (letters blue) · line 3 = date + ONE pill `2.1% to A`", by["gold"]["t2"] == "A pullback 3,290–3,340 · B breakout 3,500" and by["gold"]["pills"][0][0] == "2.1% to A" and by["gold"]["pills"][0][1] == "rgb(232, 236, 251)" and by["gold"]["blue"] == ["rgb(59, 79, 196)"] * 2 and len(by["gold"]["pills"]) == 1, by["gold"])
        check(f"{tag} F Draft row: `No scenario yet` · grey `Draft` pill + `check …` · stock near → `1.1% to A` · all pills have a background", by["mkt"]["t2"] == "No scenario yet" and by["mkt"]["pills"][0][0] == "Draft" and "check" in by["mkt"]["l3"] and by["avgo"]["pills"][0][0] == "1.1% to A" and all(p[1] != "rgba(0, 0, 0, 0)" for x in lr for p in x["pills"]), by)
        T.to_my(page, "avgo"); page.wait_for_timeout(300)
        nc = js(page, """()=>{ const q = s=>document.querySelector(s), r = e=>e.getBoundingClientRect(), d = r(q('.nt1-det')), c = r(q('[data-nt1b-block]')), n = q('[data-nt1-notes]'); return {one:q('[data-nt1-r1]').classList.contains('one'), chart:!!q('[data-nt1-chartw]'), cardW:Math.round(c.width), detW:Math.round(d.width), notes:n ? r(n).top >= c.bottom - 1 : null}; }""")
        check(f"{tag} L no chart → the Scenarios card is full width on top (reasons below, if any)", nc["one"] and not nc["chart"] and nc["cardW"] >= nc["detW"] - 40 and nc["notes"] in (None, True), nc)
        # ───── states
        hit = idea(4, ("sat", "XAU"), "Hit state", t0, B.add(t0, 5), scs=[sc("pullback", 3290, 3340, hit=now), sc("breakout", 3500, i="B")], view="bull", next=None, invLevel=3200, lastPx={"v": 3330, "at": now}, ang={"tech": "x"})
        stk = idea(5, ("stock", "AMD"), "Stock hit", t0, B.add(t0, 5), scs=[sc("breakout", 110, hit=now)], view="bull", next=None, invLevel=95)
        wrong = idea(6, ("sat", "XAU"), "Wrong state", t0, B.add(t0, 5), scs=[sc("pullback", 3290, 3340)], view="bull", next=None, invLevel=3200, lastPx={"v": 3190, "at": now}, ang={"tech": "x"}); wrong["invHitAt"] = now
        plan = idea(7, ("stock", "AMD"), "In plan", t0, B.add(t0, 5), scs=[sc("pullback", 95, 100, hit=now)], view="bull", next=None, planId="ccp1")
        none = idea(8, ("sat", "BTC"), "No scenario", t0, B.add(t0, 5), scs=[], view="bull", next=None)
        B.seed_my(page, {"hit": hit, "stk": stk, "wrong": wrong, "plan": plan, "none": none}); B.px(page, "AMD", 111.0)
        js(page, "()=>{ coreWrite('ccp1', {acct:tdHome(), ticker:'AMD', market:'US', strategy:'W', plan:{entry:100, stop:90}, stop:90, stopHistory:[], px:null, lots:[], status:'plan', created_at:new Date().toISOString()}); }"); page.wait_for_timeout(700)
        def card(i):
            B.px(page, "AVGO", 188.0); T.to_my(page, i); page.wait_for_timeout(300)
            return js(page, """()=>{ const b = document.querySelector('[data-nt1b-block]'), c = getComputedStyle(b), btns = [...b.querySelectorAll('.acts .btn')].map(x=>[x.innerText, x.classList.contains('pri')]), links = [...b.querySelectorAll('.acts .nt1-lnk')].map(x=>x.innerText);
              return {st:b.dataset.nt1dState, hdr:b.querySelector('[data-nt1d-hdr]').innerText, bg:c.backgroundColor, btns, links, nx:b.querySelector('.nx') ? b.querySelector('.nx').innerText : null, ruler:!!b.querySelector('[data-nt1-ruler]'), rows:b.querySelectorAll('[data-nt1s-row]').length, tv:!!b.querySelector('[data-nt1d-tv]'), check:!!b.querySelector('[data-nt1d-check]'), mark:!!b.querySelector('[data-nt1d-mark-btn]')}; }""")
        h = card("hit")
        check(f"{tag} S hit (non-stock): amber card · `A IN ZONE · <date time>` · NO dark button · quiet `Not yet · snooze 3 days` + `Done` · ruler + rows stay", h["st"] == "hit" and h["bg"] == "rgb(255, 244, 224)" and re.match(r"^A IN ZONE · \d+ \w+ \d\d:\d\d$", h["hdr"]) and not any(x[1] for x in h["btns"]) and h["links"][:2] == ["Not yet · snooze 3 days", "Done"] and h["ruler"] and h["rows"] == 2, h)
        hp = js(page, "()=>[...document.querySelectorAll('[data-nt1b-block] [data-nt1s-pill]')].map(p=>{ const c = getComputedStyle(p); return [p.innerText, c.backgroundColor, c.color, c.borderTopWidth, c.boxShadow]; })")
        check(f"{tag} S hit card: row pills are filled pills like the list — `▼ in zone` amber #FFF4E0 / #9A5B00 · `x% away` blue — no outline / shadow", hp[0][:3] == ["▼ in zone", "rgb(255, 244, 224)", "rgb(154, 91, 0)"] and hp[1][1] == "rgb(232, 236, 251)" and all(x[3] == "0px" and x[4] == "none" for x in hp), hp)
        shot(page, "hit")
        h2 = card("stk")
        check(f"{tag} S hit (stock): header `B BROKE OUT`… → dark `Make plan ›`", h2["st"] == "hit" and h2["hdr"].startswith("A BROKE OUT") and ["Make plan ›", True] in h2["btns"], h2)
        w = card("wrong")
        check(f"{tag} S wrong: amber (never red) card · `IDEA WRONG · …` · `price below 3,200` · dark `Drop idea` · quiet `Keep watching · snooze 3 days`", w["st"] == "wrong" and w["bg"] == "rgb(255, 244, 224)" and w["hdr"].startswith("IDEA WRONG · ") and w["nx"] == "price below 3,200" and ["Drop idea", True] in w["btns"] and w["links"] == ["Keep watching · snooze 3 days"], w)
        check(f"{tag} S wrong card: NO status pill on the scenario rows (the header already says why)", js(page, "()=>document.querySelectorAll('[data-nt1b-block] [data-nt1s-pill]').length") == 0 and js(page, "()=>document.querySelectorAll('[data-nt1b-block] [data-nt1s-row]').length") == 1)
        shot(page, "wrong")
        p = card("plan")
        check(f"{tag} S in plan: green card `IN PLAN` + `Open plan ›` · ruler/rows visible · no snooze/done/mark", p["st"] == "plan" and p["hdr"] == "IN PLAN" and p["bg"] not in ("rgb(255, 244, 224)", "rgb(243, 244, 247)") and p["bg"].startswith("rgb(2") and p["btns"] == [["Open plan ›", True]] and p["ruler"] and p["rows"] == 1 and not p["links"] and not p["mark"], p)
        ip = js(page, "()=>[...document.querySelectorAll('[data-nt1b-block] [data-nt1s-pill]')].map(p=>[p.innerText, getComputedStyle(p).backgroundColor, getComputedStyle(p).color])")
        check(f"{tag} S in-plan card: a fired scenario shows a plain grey `reached` pill — no amber", ip == [["reached", "rgb(240, 241, 244)", "rgb(95, 102, 114)"]], ip)
        mix = idea(14, ("stock", "AMD"), "In plan mixed", t0, B.add(t0, 5), scs=[sc("pullback", 95, 100, hit=now), sc("breakout", 130, i="B")], view="bull", next=None, planId="ccp1")
        B.seed_my(page, {"mix": mix}); T.to_my(page, "mix"); page.wait_for_timeout(300)
        mp = js(page, "()=>[...document.querySelectorAll('[data-nt1b-block] [data-nt1s-pill]')].map(p=>p.innerText)")
        check(f"{tag} S in-plan card: other scenarios keep their normal distance pill (`x% away`)", mp[0] == "reached" and mp[1].endswith("% away"), mp)
        T.to_my(page, "plan"); page.wait_for_timeout(300)
        shot(page, "in-plan")
        n = card("none")
        check(f"{tag} S no scenario: `No scenario yet` + plain `Add scenario ›` (not dark, not amber)", n["st"] == "none" and n["nx"] == "No scenario yet" and ["Add scenario ›", False] in n["btns"] and n["bg"] != "rgb(255, 244, 224)", n)
        page.click("[data-nt1s-add]"); page.wait_for_timeout(250)
        check(f"{tag} S `Add scenario ›` opens the sheet with the first scenario field focused", js(page, "()=>!!document.querySelector('[data-nt1-sheet]') && document.activeElement.id") == "nt1s-in-0")
        page.click("[data-nt1-cancel]"); page.wait_for_timeout(150)
        # keep watching
        T.to_my(page, "wrong"); page.click("[data-nt1d-keep]"); page.wait_for_timeout(300)
        kw = js(page, DOC, "wrong")
        check(f"{tag} S Keep watching writes invAckAt + snoozeTo (+3 days)", kw["invAckAt"] and kw["snoozeTo"] == B.add(t0, 3), kw)
        # Mark ▾ · Drop idea + Undo · a Wrong that fires again only after the price left and crossed again
        B.seed_my(page, {"mk": idea(12, ("sat", "S50"), "Mark me", t0, B.add(t0, 5), scs=[sc("pullback", 900, 920), sc("breakout", 1000, i="B")], view="bull", next=None, invLevel=850, lastPx={"v": 960, "at": now})})
        T.to_my(page, "mk"); page.click("[data-nt1d-mark-btn]"); page.click('[data-nt1d-mark="B"]'); page.wait_for_timeout(350)
        mk = js(page, DOC, "mk")
        check(f"{tag} S Mark ▾ › B reached → B.hitAt written (A untouched) · card turns amber `B BROKE OUT`", mk["scenarios"][1]["hitAt"] and mk["scenarios"][0]["hitAt"] is None and "B BROKE OUT" in js(page, TXT, "[data-nt1b-block]"), mk["scenarios"])
        page.click("[data-nt1d-mark-btn]"); page.click('[data-nt1d-mark="wrong"]'); page.wait_for_timeout(350)
        check(f"{tag} S Mark ▾ › Idea wrong → invHitAt written · `IDEA WRONG` card", bool(js(page, DOC, "mk").get("invHitAt")) and "IDEA WRONG" in js(page, TXT, "[data-nt1b-block]"))
        page.click("[data-nt1d-drop]"); page.wait_for_timeout(300)
        check(f"{tag} S Drop idea drops it with the Undo toast · Undo restores it", js(page, DOC, "mk")["dropped"] is True and js(page, VIS, "[data-nt1b-undo]"))
        page.click("[data-nt1b-undo]"); page.wait_for_timeout(300)
        check(f"{tag} S Undo brings it back", js(page, DOC, "mk")["dropped"] is False)
        B.seed_my(page, {"rf": idea(13, ("sat", "OIL"), "Re-fire", t0, B.add(t0, 5), scs=[sc("pullback", 80, 90)], view="bull", next=None, invLevel=60, lastPx={"v": 55, "at": now})})
        js(page, "()=>nt1bHitSweep()"); page.wait_for_timeout(400); r1 = js(page, DOC, "rf")
        js(page, "()=>nt1KeepWatching('rf')"); page.wait_for_timeout(300)
        js(page, "()=>nt1bHitSweep()"); page.wait_for_timeout(300); r2 = js(page, DOC, "rf")
        js(page, "()=>{ const m = myList.find(x=>x.id==='rf'); m.lastPx = {v:80, at:new Date().toISOString()}; nt1bHitSweep(); m.lastPx = {v:55, at:new Date().toISOString()}; nt1bHitSweep(); }"); page.wait_for_timeout(400)
        r3 = js(page, DOC, "rf")
        check(f"{tag} S Wrong: written once at 55 · Keep watching + price still beyond → quiet · fires again only after the price left (80) and crossed again (55)", r1["invHitAt"] and r2["invHitAt"] == r1["invHitAt"] and r3["invHitAt"] > r3["invAckAt"] and js(page, "()=>nt1bLevelState(myList.find(x=>x.id==='rf')).state") == "wrong", [r1.get("invHitAt"), r2.get("invHitAt"), r3.get("invHitAt"), r3.get("invAckAt")])
        # label collision: A zone + B + wrong + now all near each other
        cl = idea(9, ("sat", "XAU"), "Crowded", t0, B.add(t0, 5), scs=[sc("pullback", 3290, 3300), sc("breakout", 3310, i="B"), sc("breakout", 3320, i="C")], view="bull", next=None, invLevel=3285, lastPx={"v": 3305, "at": now})
        B.seed_my(page, {"cl": cl}); T.to_my(page, "cl"); page.wait_for_timeout(300)
        ls = js(page, LABELS)
        check(f"{tag} C crowded ruler (3 scenarios + Wrong + now close together): no two labels overlap", not overlap(ls) and len(ls) == 5, ls)
        # sell side ruler: sell pullback band + order
        sl = idea(10, ("sat", "BTC"), "Sell", t0, B.add(t0, 5), scs=[sc("pullback", 92000, 94000), sc("breakout", 80000, i="B")], view="bear", next=None, invLevel=96000, lastPx={"v": 88000, "at": now})
        B.seed_my(page, {"sl": sl}); T.to_my(page, "sl"); page.wait_for_timeout(300)
        sr = js(page, """()=>{ const q = s=>document.querySelector('[data-nt1b-block] ' + s), l = e=>parseFloat(e.style.left); return {tickB:l(q('[data-nt1r-tick="B"]')), now:l(q('[data-nt1r-now]')), band:l(q('[data-nt1r-band="A"]')), wrong:l(q('[data-nt1r-tick="wrong"]')), pills:[...document.querySelectorAll('[data-nt1b-block] [data-nt1s-pill]')].map(x=>x.innerText), tv:document.querySelector('[data-nt1d-tv]').innerText.replace(/\\s+/g,' ')}; }""")
        check(f"{tag} C sell side: Breakout B < now < band A < Wrong · pills `4.5% away` / `9.1% away`", sr["tickB"] < sr["now"] < sr["band"] < sr["wrong"] and sr["pills"] == ["4.5% away", "9.1% away"], sr)
        # no ruler dots outside 4–96
        edge = idea(11, ("sat", "XAU"), "Edge", t0, B.add(t0, 5), scs=[sc("pullback", 3290, 3340)], view="bull", next=None, invLevel=3200, lastPx={"v": 9000, "at": now})
        B.seed_my(page, {"edge": edge}); T.to_my(page, "edge"); page.wait_for_timeout(250)
        ed = js(page, "()=>[...document.querySelectorAll('[data-nt1b-block] [data-nt1r-tick], [data-nt1b-block] [data-nt1r-now]')].map(e=>parseFloat(e.style.left))")
        check(f"{tag} C scale padded 25 % · everything clamped inside 4–96 %", all(4 <= v <= 96 for v in ed), ed)
        # ───── sheet
        T.to_my(page, "gold"); edit(page, "gold")
        s = js(page, """()=>{ const q = s=>document.querySelector(s), t = s=>Math.round(q(s).getBoundingClientRect().top), sh = q('[data-nt1-sheet]');
            return {head:q('[data-nt1s-head]').innerText, rows:document.querySelectorAll('[data-nt1s-r]').length, order:t('#nt1fSubj') < t('[data-nt1s-blk]') && t('[data-nt1s-blk]') < t('[data-nt1s-reasons]') && t('[data-nt1s-reasons]') < t('#nt1fCheck'), next:!!q('#nt1fNext'), more:!!q('[data-nt1d-more]'), dirs:!!q('[data-nt1d-dir]'), built:!!q('#nt1fBuilt'), sec:[...sh.querySelectorAll('.nt1d-sec')].map(x=>x.innerText),
              reasons:[...sh.querySelectorAll('[data-nt1s-reasons] label')].map(x=>x.innerText), open:[...sh.querySelectorAll('[data-nt1-fa]')].every(e=>e.getBoundingClientRect().height > 0), wl:q('.nt1s-wr label').innerText, now:!!q('#nt1fLast'), toggle:!!q('[data-nt1s-side]'), nowNote:(q('[data-nt1d-lastnote]')||{}).innerText}; }""")
        check(f"{tag} E sheet: SCENARIOS · BUY (My view: Bull) · max 3 · 2 rows · Reasons always open (4 inputs) · no Next step / More notes / direction toggles / Built on", s["head"] == "SCENARIOS · BUY (My view: Bull) · max 3" and s["rows"] == 2 and s["order"] and not s["next"] and not s["more"] and not s["dirs"] and not s["built"] and s["reasons"] == ["Technical", "Sentiment", "Fundamental", "Macro / news"] and s["open"], s)
        check(f"{tag} E `Wrong if below` + `Now` (non-stock) with `typed · date` · no Buy|Sell toggle while My view is set", s["wl"] == "Wrong if below" and s["now"] and s["nowNote"].startswith("typed") and not s["toggle"], s)
        js(page, "()=>{ for(const id of ['nt1Toast','nt1bToast']){ const t = document.getElementById(id); if(t) t.style.display = 'none'; } }")
        page.set_viewport_size({"width": 1440, "height": 1240}); page.wait_for_timeout(250); shot(page, "sheet"); page.set_viewport_size({"width": 1440, "height": 900}); page.wait_for_timeout(200)
        page.click('[data-nt1s-r="1"] [data-nt1s-kind="pullback"]'); page.wait_for_timeout(100)
        sw = js(page, "()=>({lo:!!document.querySelector('[data-nt1s-r=\"1\"] [data-nt1s-f=\"lo\"]'), hi:!!document.querySelector('[data-nt1s-r=\"1\"] [data-nt1s-f=\"hi\"]'), lv:!!document.querySelector('[data-nt1s-r=\"1\"] [data-nt1s-f=\"level\"]')})")
        page.click('[data-nt1s-r="1"] [data-nt1s-kind="breakout"]'); page.wait_for_timeout(100)
        sw2 = js(page, "()=>({lo:!!document.querySelector('[data-nt1s-r=\"1\"] [data-nt1s-f=\"lo\"]'), lv:!!document.querySelector('[data-nt1s-r=\"1\"] [data-nt1s-f=\"level\"]')})")
        check(f"{tag} E Pullback ↔ Breakout swaps the inputs (from–to ↔ one level)", sw == {"lo": True, "hi": True, "lv": False} and sw2 == {"lo": False, "lv": True}, [sw, sw2])
        page.click("[data-nt1s-addrow]"); page.wait_for_timeout(100)
        mx = js(page, "()=>({rows:document.querySelectorAll('[data-nt1s-r]').length, add:!!document.querySelector('[data-nt1s-addrow]')})")
        check(f"{tag} E max 3 scenarios: `+ Add scenario` disappears at 3", mx == {"rows": 3, "add": False}, mx)
        page.click('[data-nt1s-r="0"] [data-nt1s-rm]'); page.wait_for_timeout(100)
        lt = js(page, "()=>[...document.querySelectorAll('[data-nt1s-r] .nt1s-lt')].map(e=>e.innerText)")
        check(f"{tag} E removing a row re-letters the rest (A B C → A B) and brings `+ Add` back", lt == ["A", "B"] and js(page, "()=>!!document.querySelector('[data-nt1s-addrow]')"), lt)
        page.click('[data-nt1s-r="0"] [data-nt1s-kind="pullback"]'); page.fill('[data-nt1s-r="0"] [data-nt1s-f="lo"]', "3350"); page.fill('[data-nt1s-r="0"] [data-nt1s-f="hi"]', "3340")
        hint = js(page, TXT, '[data-nt1s-hint="0"]')
        check(f"{tag} E from > to → amber `⚠ from must be below to` (Save is blocked)", hint == "⚠ from must be below to", hint)
        page.click("[data-nt1-save]"); page.wait_for_timeout(150)
        check(f"{tag} E …and Save refuses with a message", "from" in (js(page, TXT, "#nt1Err") or "") and js(page, "()=>!!document.querySelector('[data-nt1-sheet]')"))
        page.click("[data-nt1-cancel]"); page.wait_for_timeout(250)
        # breakout hint: buy breakout at/below now
        js(page, "()=>nt1SheetOpen({})"); page.wait_for_timeout(200); page.select_option("#nt1fSubj", "sat:XAU"); page.click('[data-nt1-fv="bull"]'); page.fill("#nt1fLast", "3400")
        page.click('[data-nt1s-r="0"] [data-nt1s-kind="breakout"]'); page.fill('[data-nt1s-r="0"] [data-nt1s-f="level"]', "3350")
        h1 = js(page, TXT, '[data-nt1s-hint="0"]'); c1 = js(page, "()=>getComputedStyle(document.querySelector('[data-nt1s-hint=\"0\"]')).color")
        page.click('[data-nt1-fv="bull"]'); page.click('[data-nt1-fv="bear"]'); page.fill('[data-nt1s-r="0"] [data-nt1s-f="level"]', "3450"); page.wait_for_timeout(80)
        h2 = js(page, TXT, '[data-nt1s-hint="0"]'); wl2 = js(page, TXT, ".nt1s-wr label")
        check(f"{tag} E inline hints: buy breakout ≤ now → `already above — fires on save` (muted) · sell mirrored `already below …` · Wrong if flips to `above`", h1 == "already above — fires on save" and c1 != "rgb(154, 91, 0)" and h2 == "already below — fires on save" and wl2 == "Wrong if above", [h1, h2, wl2])
        page.click('[data-nt1-fv="bear"]'); page.wait_for_timeout(80)
        tg = js(page, "()=>({toggle:[...document.querySelectorAll('[data-nt1s-side-b]')].map(b=>b.innerText), head:document.querySelector('[data-nt1s-head]').innerText})")
        page.click('[data-nt1s-side-b="sell"]'); page.wait_for_timeout(80)
        tg2 = js(page, "()=>[...document.querySelectorAll('[data-nt1s-side-b]')].map(b=>b.getAttribute('aria-pressed'))")
        check(f"{tag} E Buy | Sell toggle appears only when My view is empty / neutral (`SCENARIOS · Buy Sell · max 3`)", tg["toggle"] == ["Buy", "Sell"] and tg["head"].replace("\n", " ").startswith("SCENARIOS ·") and tg2 == ["false", "true"], [tg, tg2])
        page.select_option("#nt1fSubj", "stock:AVGO"); page.wait_for_timeout(100)
        check(f"{tag} E `Now` is hidden for a stock", not js(page, "()=>!!document.querySelector('#nt1fLast')"))
        page.fill("#nt1fTitle", "Draft only"); page.evaluate("()=>{ document.querySelector('[data-nt1s-r=\"0\"] [data-nt1s-f=\"level\"]').value=''; nt1ScIn(0,'level',''); }")
        clip(page); save(page); nid = js(page, "()=>mySel"); dd = js(page, DOC, nid)
        check(f"{tag} E Save needs only About + Title → a Draft (no scenario) · side stored from the toggle (sell) · nothing copied", dd and dd["scenarios"] == [] and dd["side"] == "sell" and js(page, "()=>window.__clip") == "", dd)
        # ───── TV copy lines
        clip(page)
        js(page, "()=>nt1SheetOpen({})"); page.wait_for_timeout(200); page.select_option("#nt1fSubj", "sat:XAU"); page.click('[data-nt1-fv="bull"]'); page.fill("#nt1fTitle", GOLD)
        page.fill('[data-nt1s-r="0"] [data-nt1s-f="lo"]', "3290"); page.fill('[data-nt1s-r="0"] [data-nt1s-f="hi"]', "3340")
        page.click("[data-nt1s-addrow]"); page.click('[data-nt1s-r="1"] [data-nt1s-kind="breakout"]'); page.fill('[data-nt1s-r="1"] [data-nt1s-f="level"]', "3500"); page.fill("#nt1fInv", "3200")
        save(page); gid = js(page, "()=>mySel")
        cp = js(page, "()=>window.__clip"); tt = js(page, TXT, "#nt1Toast"); ln = js(page, "()=>[...document.querySelectorAll('#nt1Toast a, #nt1Toast button')].map(x=>[x.innerText, x.href || ''])")
        check(f"{tag} T new idea: clipboard = first scenario `XAU ≤ 3,340 · A pullback · {GOLD}` · toast `Saved · copied for TradingView: …` + Copy B + Copy ✕ + Open TradingView ↗", cp == f"XAU ≤ 3,340 · A pullback · {GOLD}" and tt.startswith("Saved · copied for TradingView: " + cp) and [x[0] for x in ln] == ["Copy B", "Copy ✕", "Open TradingView ↗"], [cp, tt, ln])
        page.click('[data-nt1-toast-oth="0"]'); page.wait_for_timeout(120); l2 = js(page, "()=>window.__clip")
        page.click('[data-nt1-toast-oth="1"]') if js(page, "()=>!!document.querySelector('[data-nt1-toast-oth=\"1\"]')") else None
        page.wait_for_timeout(120)
        check(f"{tag} T toast links copy the other lines: B → `XAU ≥ 3,500 · B breakout · …`", l2 == f"XAU ≥ 3,500 · B breakout · {GOLD}", l2)
        T.to_my(page, gid); page.wait_for_timeout(200)
        page.click('[data-nt1d-copyinv]'); page.wait_for_timeout(120); wl = js(page, "()=>window.__clip")
        check(f"{tag} T Wrong line `XAU ≤ 3,200 WRONG · {GOLD}`", wl == f"XAU ≤ 3,200 WRONG · {GOLD}", wl)
        js(page, "()=>{ window.__clip = ''; }"); edit(page, gid); page.fill("#nt1fTitle", GOLD + "!"); save(page)
        check(f"{tag} T title-only edit leaves the clipboard alone", js(page, "()=>window.__clip") == "")
        edit(page, gid); page.fill('[data-nt1s-r="1"] [data-nt1s-f="level"]', "3520"); save(page)
        check(f"{tag} T changing B copies B's line (the first CHANGED scenario)", js(page, "()=>window.__clip") == f"XAU ≥ 3,520 · B breakout · {GOLD}!", js(page, "()=>window.__clip"))
        js(page, "()=>{ window.__clip = ''; }"); edit(page, gid); page.fill("#nt1fInv", "3150"); save(page)
        check(f"{tag} T changing only Wrong-if copies the WRONG line", js(page, "()=>window.__clip") == f"XAU ≤ 3,150 WRONG · {GOLD}!", js(page, "()=>window.__clip"))
        T.to_my(page, gid); page.wait_for_timeout(200)
        page.click("[data-nt1d-tvset]"); page.wait_for_timeout(250)
        one = js(page, "()=>({tv:document.querySelector('[data-nt1d-tv]').innerText.replace(/\\s+/g,' '), chips:document.querySelectorAll('[data-nt1d-tv] .cp').length, doc:window.firebase.__mockDb.__getDoc(['users','testuid','ideas_my',mySel]).tvAlert})")
        check(f"{tag} T one tick covers every scenario + Wrong: `TV alerts set ✓`, chips hidden, stored", one["tv"] == "TV alerts set ✓" and one["chips"] == 0 and one["doc"] is True, one)
        js(page, "()=>{ window.__clip = ''; }"); clip(page, "deny"); edit(page, gid); page.fill('[data-nt1s-r="0"] [data-nt1s-f="hi"]', "3345"); save(page)
        fb = js(page, TXT, "#nt1Toast")
        check(f"{tag} T clipboard denied → never silent: `Saved · could not copy the alert text:` + the line + Copy", fb.startswith("Saved · could not copy the alert text: XAU ≤ 3,345") and js(page, "()=>!!document.querySelector('[data-nt1-toast-copy]')"), fb)
        clip(page)
        # built on in ⋯
        T.to_my(page, "gold"); page.wait_for_timeout(200); page.click("[data-nt1-menu]")
        mi = js(page, "()=>[...document.querySelectorAll('.ltMenu button')].map(b=>b.innerText)")
        check(f"{tag} E `Built on…` lives in the ⋯ menu (Copy text · Built on… · Delete)", mi == ["Copy text", "Built on…", "Delete"], mi)
        page.click("[data-nt1-builton]"); page.wait_for_timeout(200); page.select_option("#nt1fBuilt", ""); page.click("[data-nt1-built-save]"); page.wait_for_timeout(300)
        check(f"{tag} E …and it edits builtOn (cleared here)", js(page, DOC, "gold").get("builtOn") is None)
        # ───── Today
        B.seed_my(page, {"w2": idea(20, ("stock", "AVGO"), "Rank wrong", t0, B.add(t0, 5), scs=[sc("pullback", 150, 160)], view="bull", next=None, invLevel=100),
                         "h2": idea(21, ("stock", "AAPL"), "Rank hit", t0, B.add(t0, 5), scs=[sc("breakout", 100, hit=now)], view="bull", next=None),
                         "n2": idea(22, ("stock", "COST"), "Rank near", t0, B.add(t0, 5), scs=[sc("pullback", 95, 98)], view="bull", next=None),
                         "l2": idea(23, ("sat", "BTC"), "Rank late", t0, B.add(t0, -2), scs=[sc("pullback", 50, 60)], view="bull", next=None, lastPx={"v": 99, "at": now}),
                         "c2": idea(24, ("market", "US"), "Rank today", t0, t0, scs=[sc("pullback", 50, 60)], view="bull", next=None),
                         "dr": idea(25, ("market", "TH"), "Draft not due", t0, B.add(t0, 5), scs=[], view="bull", next=None),
                         "dr2": idea(26, ("market", "TH"), "Draft due", t0, t0, scs=[], view="bull", next=None),
                         "ip": idea(27, ("stock", "AMD"), "In plan hit", t0, B.add(t0, -2), scs=[sc("pullback", 95, 100, hit=now)], view="bull", next=None, planId="ccp1"),
                         "nn": idea(28, ("market", "US"), "Has no next step", t0, B.add(t0, 9), scs=[sc("pullback", 50, 60)], view="bull", next=None)})
        B.px(page, "AVGO", 99.0); B.px(page, "AAPL", 101.0); B.px(page, "COST", 99.0); B.px(page, "AMD", 90.0)
        B.to_today(page)
        due = js(page, "()=>nt1bDueAll().filter(x=>x.kind==='my').map(x=>[x.id, x.rank, x.pill, x.btn[0], x.sub])")
        ids = [x[0] for x in due]; rk = {x[0]: x for x in due}
        check(f"{tag} Y ranks: wrong 0 · hit 1 · near 2 · late 4 · check today 5 · the old rank 3 (`no next step`) is gone", rk["w2"][1] == 0 and rk["h2"][1] == 1 and rk["n2"][1] == 2 and rk["l2"][1] == 4 and rk["c2"][1] == 5 and not any(x[1] == 3 for x in due) and not any("no next step" in x[2] for x in due), due)
        check(f"{tag} Y in-plan ideas never appear · an idea without next step does not appear · Drafts only through their Check-again date", "ip" not in ids and "nn" not in ids and "dr" not in ids and "dr2" in ids, ids)
        check(f"{tag} Y buttons: wrong → `Drop idea ›` · hit + stock → `Make plan ›` · near / late / check → `Open ›` · pills `✕ idea wrong` / `▲ A broke out` / `1.0% to A` …", rk["w2"][3] == "Drop idea ›" and rk["h2"][3] == "Make plan ›" and rk["n2"][3] == "Open ›" and rk["w2"][2] == "✕ idea wrong" and rk["h2"][2] == "▲ A broke out" and rk["n2"][2].endswith("to A"), due)
        td_ = js(page, TXT, "[data-nt1b-ideas]")
        check(f"{tag} Y Today row line 2 = scenario summary + pill (`A pullback 95–98` / `below 100`)", "A pullback 95–98" in (js(page, TXT, '[data-nt1b-it="my:n2"]') or "") or "A pullback 95–98" in td_ or any("A pullback 95–98" in x[4] for x in due), due)
        # Make plan: entry + SL
        js(page, "()=>nt1bMakePlan('h2')"); page.wait_for_timeout(500)
        o = js(page, "()=>({tab:activeTab, entry:(coreEl('cnEntry')||{}).value, pend:nt1bPend && nt1bPend.id})")
        check(f"{tag} G Make plan › (stock): entry = the fired breakout level (100) · pending link to the idea", o["tab"] == "plan" and o["entry"] == "100" and o["pend"] == "h2", o)
        B.seed_my(page, {"mp": idea(29, ("stock", "NVDA"), "Pull plan", t0, B.add(t0, 5), scs=[sc("pullback", 95, 98, hit=now)], view="bull", next=None, invLevel=90)})
        js(page, "()=>{ switchTab('watch'); }"); js(page, "()=>nt1bMakePlan('mp')"); page.wait_for_timeout(500)
        o = js(page, "()=>({entry:(coreEl('cnEntry')||{}).value, stop:(coreEl('cnStop')||{}).value})")
        check(f"{tag} G pullback (buy) → entry = `hi` 98 · SL = Wrong-if 90 (box was empty)", o["entry"] == "98" and o["stop"] == "90", o)
        js(page, "()=>{ coreWrite('ccnew2', {acct:tdHome(), ticker:'NVDA', market:'US', strategy:'W', plan:{entry:98, stop:90}, stop:90, stopHistory:[], px:null, lots:[], status:'plan', created_at:new Date().toISOString()}); nt1bLinkPlan('ccnew2', 'NVDA'); }"); page.wait_for_timeout(900)
        T.to_my(page, "mp"); page.wait_for_timeout(300)
        o = js(page, "()=>({pid:myList.find(x=>x.id==='mp').planId, st:document.querySelector('[data-nt1b-block]').dataset.nt1dState})")
        B.to_today(page); gone = "mp" not in js(page, "()=>nt1bDueAll().map(x=>x.id)")
        check(f"{tag} G linking the saved plan → planId set · card shows IN PLAN · idea leaves Today", o["pid"] == "ccnew2" and o["st"] == "plan" and gone, o)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def part_today_shot(pw):
    tag = "[today shot]"
    b, page, pe = N.open_nt1(pw, 1440, 900, my_docs=False, notes=False)
    try:
        t0 = B.td(page); B.quiet_fixture_ai(page); now = now_iso(page)
        B.seed_my(page, {"w": idea(1, ("sat", "BTC"), "Pullback to 82k", t0, B.add(t0, 5), scs=[sc("pullback", 80000, 82000)], view="bull", next=None, invLevel=80500, lastPx={"v": 80100, "at": now}),
                         "h": idea(2, ("stock", "AVGO"), "Range 160–190", t0, B.add(t0, 5), scs=[sc("breakout", 190, hit=now)], view="bull", next=None),
                         "n": idea(3, ("sat", "XAU"), "Gold: buy the dip or the breakout", t0, B.add(t0, 5), scs=[sc("pullback", 3290, 3340), sc("breakout", 3500, i="B")], view="bull", next=None, lastPx={"v": 3412, "at": now})})
        B.px(page, "AVGO", 191.0); B.to_today(page)
        js(page, "()=>{ for(const id of ['nt1Toast','nt1bToast']){ const t = document.getElementById(id); if(t) t.style.display = 'none'; } }")
        rows = js(page, "()=>[...document.querySelectorAll('[data-nt1b-it]')].map(r=>[r.dataset.nt1bRank, r.querySelector('[data-nt1b-pill]').innerText, r.querySelector('[data-nt1b-btn]').innerText, r.querySelector('[data-nt1b-sub]').innerText])")
        check(f"{tag} Y Today › Ideas: wrong → hit → near · `Drop idea ›` / `Make plan ›` / `Open ›` · line 2 = scenario + pill", rows == [["0", "✕ idea wrong", "Drop idea ›", "below 80,500"], ["1", "▲ A broke out", "Make plan ›", "A breakout 190"], ["2", "2.1% to A", "Open ›", "A pullback 3,290–3,340"]], rows)
        shot(page, "today")
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def part_resize(pw, w=1440):
    tag = "[resize %s]" % w
    b, page, pe = N.open_nt1(pw, w, 900, my_docs=False, notes=False)
    try:
        stub(page); t0 = B.td(page); B.quiet_fixture_ai(page); now = now_iso(page)
        B.seed_my(page, {"g": idea(1, ("sat", "XAU"), GOLD, t0, scs=[sc("pullback", 3290, 3340), sc("breakout", 3500, i="B")], view="bull", chart=TV, next=None, ang={"tech": "x", "sent": "y"}, lastPx={"v": 3412, "at": now})})
        T.to_my(page, "g"); page.wait_for_timeout(400)
        W = lambda: js(page, "()=>[Math.round(document.querySelector('.nt1-list').getBoundingClientRect().width), Math.round(document.querySelector('.nt1-det').getBoundingClientRect().width)]")
        a = js(page, """()=>{ const h = document.querySelector('[data-nt1-rz]'), r = h.getBoundingClientRect(); return {role:h.getAttribute('role'), o:h.getAttribute('aria-orientation'), min:h.getAttribute('aria-valuemin'), max:h.getAttribute('aria-valuemax'), now:h.getAttribute('aria-valuenow'), tab:h.tabIndex, w:Math.round(r.width), cur:getComputedStyle(h).cursor, op:getComputedStyle(h, '::after').opacity}; }""")
        check(f"{tag} R handle: role=separator · vertical · 8px wide · col-resize · tabindex 0 · aria min 300 · now 380 · grip invisible until hover", a["role"] == "separator" and a["o"] == "vertical" and a["w"] == 8 and a["cur"] == "col-resize" and a["tab"] == 0 and a["min"] == "300" and a["now"] == "380" and a["op"] == "0", a)
        box = js(page, "()=>{ const r = document.querySelector('[data-nt1-rz]').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
        page.mouse.move(box[0], box[1]); page.mouse.down(); page.mouse.move(box[0] + 40, box[1], steps=4); page.mouse.move(box[0] + 70, box[1], steps=4)
        mid = W(); page.mouse.up(); page.wait_for_timeout(200)
        r1 = W()
        check(f"{tag} R drag +70 → list 450 (detail 810) · saved in localStorage `nt.listW`", r1[0] == 450 and r1[1] == 810 and js(page, "()=>localStorage.getItem('nt.listW')") == "450", [mid, r1])
        js(page, "()=>{ nt1ListW = null; document.documentElement.style.removeProperty('--nt-list'); renderWatchlist(); }"); page.wait_for_timeout(200)
        r0 = W(); js(page, "()=>{ nt1RzLoad(); renderWatchlist(); }"); page.wait_for_timeout(250); ra = W()
        check(f"{tag} R after a reload (state wiped, `nt1RzLoad` = the start-up read) the list is 450 again", r0[0] == 380 and ra[0] == 450, [r0, ra])
        box = js(page, "()=>{ const r = document.querySelector('[data-nt1-rz]').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
        page.mouse.move(box[0], box[1]); page.mouse.down(); page.mouse.move(box[0] + 50, box[1], steps=4); page.mouse.up(); page.wait_for_timeout(250)
        r5 = W(); check(f"{tag} R drag +50 more → list 500 (the widest the detail allows at 1440) · chart + Scenarios still side by side", r5[0] == 500 and r5[1] == 760, r5)
        shot(page, "resized")
        # clamps
        box = js(page, "()=>{ const r = document.querySelector('[data-nt1-rz]').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
        page.mouse.move(box[0], box[1]); page.mouse.down(); page.mouse.move(box[0] - 400, box[1], steps=6); page.mouse.up(); page.wait_for_timeout(150)
        lo = W()
        box = js(page, "()=>{ const r = document.querySelector('[data-nt1-rz]').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
        page.mouse.move(box[0], box[1]); page.mouse.down(); page.mouse.move(box[0] + 700, box[1], steps=6); page.mouse.up(); page.wait_for_timeout(150)
        hi = W(); mx = None
        check(f"{tag} R clamps: far left → 300 · far right → at most 520, and at 1440 the detail never under 760 → 500", lo[0] == 300 and hi[1] >= 760 and hi[0] == 500, [lo, hi])
        # keyboard
        page.focus("[data-nt1-rz]"); page.keyboard.press("Home"); page.wait_for_timeout(80); k0 = W()[0]
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(80); k1 = W()[0]; page.keyboard.press("ArrowLeft"); page.keyboard.press("ArrowLeft"); page.wait_for_timeout(80); k2 = W()[0]
        page.keyboard.press("End"); page.wait_for_timeout(80); k3 = W()
        check(f"{tag} R keyboard: Home = min 300 · → +20 · ← −20 · End = max (detail ≥ 760)", k0 == 300 and k1 == 320 and k2 == 300 and k3[1] >= 760 and k3[0] >= 480, [k0, k1, k2, k3])
        page.keyboard.press("Enter"); page.wait_for_timeout(100); e1 = W()[0]
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(80)
        page.dblclick("[data-nt1-rz]"); page.wait_for_timeout(100); e2 = W()[0]
        check(f"{tag} R Enter and double-click both reset to 380 (and forget the saved width)", e1 == 380 and e2 == 380 and js(page, "()=>localStorage.getItem('nt.listW')") is None, [e1, e2])
        # thin grip on focus
        page.keyboard.press("ArrowDown"); page.focus("[data-nt1-rz]"); page.wait_for_timeout(300); op = js(page, "()=>getComputedStyle(document.querySelector('[data-nt1-rz]'), '::after').opacity")
        check(f"{tag} R grip appears on keyboard focus", op == "1", op)
        # chart + scenarios side by side at the minimum detail width
        page.keyboard.press("End"); page.wait_for_timeout(150)
        sb = js(page, "()=>{ const c = document.querySelector('[data-nt1-chartw]').getBoundingClientRect(), k = document.querySelector('[data-nt1b-block]').getBoundingClientRect(); return c.right <= k.left + 1; }")
        check(f"{tag} R at the narrowest detail (≥ 760) the chart and Scenarios card stay side by side", sb)
        page.keyboard.press("Enter")
        # localStorage throwing
        errs = []; page.on("pageerror", lambda e: errs.append(str(e)))
        js(page, "()=>{ Storage.prototype.getItem = ()=>{ throw new Error('blocked'); }; Storage.prototype.setItem = ()=>{ throw new Error('blocked'); }; Storage.prototype.removeItem = ()=>{ throw new Error('blocked'); }; nt1RzLoad(); renderWatchlist(); }"); page.wait_for_timeout(250)
        bx = js(page, "()=>{ const r = document.querySelector('[data-nt1-rz]').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
        page.mouse.move(bx[0], bx[1]); page.mouse.down(); page.mouse.move(bx[0] + 30, bx[1], steps=3); page.mouse.up(); page.wait_for_timeout(200)
        d0 = W(); page.focus("[data-nt1-rz]"); page.keyboard.press("Enter"); page.wait_for_timeout(120)
        check(f"{tag} R localStorage throwing → starts at 380, dragging still works for the session, no uncaught error", d0[0] == 410 and W()[0] == 380 and not errs, [d0, W(), errs[:3]])
    finally:
        b.close()


def part_narrow(pw):
    tag = "[1000]"
    b, page, pe = N.open_nt1(pw, 1000, 800, my_docs=False, notes=False)
    try:
        t0 = B.td(page); B.quiet_fixture_ai(page)
        B.seed_my(page, {"g": idea(1, ("sat", "XAU"), GOLD, t0, scs=[sc("pullback", 3290, 3340)], view="bull", next=None)})
        T.to_my(page, "g"); page.wait_for_timeout(300)
        check(f"{tag} R below 1100px the resize handle is hidden", not js(page, VIS, "[data-nt1-rz]"))
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def part_phone(pw):
    tag = "[390]"
    b, page, pe = N.open_nt1(pw, 390, 844, my_docs=False, notes=False)
    try:
        stub(page); t0 = B.td(page); B.quiet_fixture_ai(page); now = now_iso(page)
        ang = {"tech": "แนวรับสำคัญ 3,290–3,340", "sent": "ทองลง ~11%", "fund": "ธนาคารกลางยังซื้อต่อ", "macro": "CPI 20:30 พฤหัส"}
        B.seed_my(page, {"g": idea(1, ("sat", "XAU"), GOLD, t0, B.add(t0, 9), scs=[sc("pullback", 3290, 3340, "wait for H4"), sc("breakout", 3500, i="B")], view="bull", chart=TV, ang=ang, next=None, invLevel=3200, lastPx={"v": 3412, "at": now}, builtOn="en-idea-1")})
        T.to_my(page, "g"); page.wait_for_timeout(400)
        y = js(page, """()=>{ const q = s=>document.querySelector(s), t = s=>Math.round(q(s).getBoundingClientRect().top); return {chart:t('[data-nt1-chartw]'), card:t('[data-nt1b-block]'), notes:t('[data-nt1-notes]'), foot:t('[data-nt1-foot]'), cols:getComputedStyle(q('[data-nt1-notes]')).gridTemplateColumns.split(' ').length, over:document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1,
            lbl:[...document.querySelectorAll('[data-nt1b-block] [data-nt1r-lbl]')].map(e=>{ const b = e.getBoundingClientRect(); return {k:e.dataset.nt1rLbl, l:b.left, r:b.right, t:b.top, b:b.bottom}; }), card_r:q('[data-nt1b-block]').getBoundingClientRect().right, vw:innerWidth}; }""")
        check(f"{tag} P order: chart → Scenarios → Reasons (1 column) → footer · no sideways scroll", y["chart"] < y["card"] < y["notes"] < y["foot"] and y["cols"] == 1 and y["over"], y)
        check(f"{tag} P ruler labels do not overlap and stay inside the card", not overlap(y["lbl"]) and all(x["l"] >= 0 and x["r"] <= y["vw"] for x in y["lbl"]), y["lbl"])
        shot(page, "phone")
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        part_logic(pw)
        part_desktop(pw)
        part_today_shot(pw)
        part_resize(pw, 1440)
        part_narrow(pw)
        part_phone(pw)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY nt2: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
