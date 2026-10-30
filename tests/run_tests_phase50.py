#!/usr/bin/env python3
"""ID4 — Ideas เชื่อมแท็บ Today (เฉพาะสิ่งที่ต้องลงมือ) · เทส 50
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-05 (จันทร์ 10:00 ไทย) · fixture = สำเนา idea_semis.json ปรับในเทส + การ์ด Core open 1 ตัว (HELD) + Watchlist
ภาพ tests/screenshots/id4-{today-ideas,today-cap}-{1440,390}.png
รัน: python3 run_tests_phase50.py"""
import copy, json, os
from playwright.sync_api import sync_playwright
import run_tests_phase24 as p24
import run_tests_phase38 as P38
import run_tests_phase39 as P39
import run_tests_phase40 as P40
import run_tests_phase44 as P44
import run_tests_phase47 as P47

js, check, shot = P39.js, P39.check, P39.shot
results = P39.results
ENGINE = P39.ENGINE
CLK = "2026-10-05T03:00:00Z"      # จันทร์ 5 ต.ค. 10:00 ไทย
OK_LINE = "[data-td-okline]"
IDEA_KINDS = ("idea-kill", "idea-held", "idea-study", "idea-recheck")


def chk(name, ok, detail=""): check(name, ok, detail)


def idea(iid, name, status="need_evidence", date="2026-10-04", kill_level="ok", cands=(), losers=(), recheck=None, scope=("US",), **kw):
    d = copy.deepcopy(P44.SEMIS)
    d.update(id=iid, name=name, status=status, date=date, scope=list(scope), candidates=list(cands), losers=list(losers))
    d["kill"] = [{"signal": "สัญญาณทดสอบ " + iid, "now": "x", "level": kill_level}]
    d["recheck"] = recheck if recheck is not None else {"date": "2026-12-31", "what": "ไกลมาก"}
    d.update(kw); return d


def cand(sym, rank, state="study", src="10-K FY25 — รายได้หลักตรงธีม", market="US", **kw):
    return P44.cand(sym, sym + " Inc", rank, state, src=src, market=market, **kw)


def loser(sym, why="พึ่งพารายได้จากส่วนที่เสีย", state=None):
    d = {"sym": sym, "market": "US", "why": why, "segment": "อุปกรณ์"}
    if state: d["state"] = state
    return d


def wl_doc(sym, th_date=None):
    t = P38.th(sym, date=th_date) if th_date else None
    return P38.wl_th(sym, t)


def seed_wl(page, sym, th_date=None):
    page.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["users", "testuid", "watchlist", sym], wl_doc(sym, th_date)])


def reseed_wl(page, sym, th_date=None):
    page.evaluate("([s,d])=>firebase.firestore().collection('users').doc('testuid').collection('watchlist').doc(s).set(d)", [sym, wl_doc(sym, th_date)]); page.wait_for_timeout(500)


def reseed_idea(page, d):
    page.evaluate("([i,x])=>firebase.firestore().collection('users').doc('testuid').collection('ideas').doc(i).set(x)", [d["id"], {"idea": {k: v for k, v in d.items() if k != "log"}, "idea_log": [], "user": {}}]); page.wait_for_timeout(500)


def launcher(pw, w, h, ideas=(), wl=(("HELD", "2026-09-20"),), deny=False):
    doc = P38.doc38(clean=True, log={})
    doc["books"]["main"]["trades"] = [P38.T("theld", "core", "open", sym="HELD", entry=100, sl=90, qty=100, cur="USD", date="2026-09-10", openedAt="2026-09-10")]
    cards = {"cheld": p24.open_card("cheld", "theld", ticker="HELD", acct="main", qty=100, entry=100, sl=90, px=110, pxDate="2026-10-02", emaW=100, tier="A")}

    def ex(pg):
        if deny: pg.evaluate("()=>window.firebase.__mockDb.__denyPath(['users','testuid','ideas'])")
        for sym, thd in wl: seed_wl(pg, sym, thd)
        for it in ideas: P44.seed_idea(pg, it)
    r = P39.launch(pw, w, h, doc=doc, cards=cards, iso=CLK, clean=True, extra=ex)
    P38.go_today(r[2]) if hasattr(P38, "go_today") else js(r[2], "()=>switchTab('today')")
    r[2].wait_for_timeout(400)
    return r


def rows(page, kind):
    return js(page, "(k)=>[...document.querySelectorAll('.tdRow[data-kind=\"'+k+'\"]')].map(e=>({t:e.querySelector('.tdWhat').textContent.replace(/\\s+/g,' ').trim(), full:e.textContent.replace(/\\s+/g,' ').trim(), grp:e.closest('[data-td-grp]').dataset.tdGrp, sub:(e.querySelector('.tdWhere')||{}).textContent||'', args:e.dataset.args, go:e.dataset.go}))", kind)


def all_idea_rows(page):
    return js(page, "(ks)=>[...document.querySelectorAll('.tdRow')].filter(e=>ks.includes(e.dataset.kind)).map(e=>({k:e.dataset.kind, g:e.closest('[data-td-grp]').dataset.tdGrp, t:e.querySelector('.tdWhat').textContent.replace(/\\s+/g,' ').trim()}))", list(IDEA_KINDS))


def tags(page, kind):
    return js(page, "(k)=>tdLast.tasks.filter(t=>t.kind===k).map(t=>t.tags)", kind)


def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")


def one_line(page):
    return js(page, """()=>[...document.querySelectorAll('.tdRow[data-kind^="idea-"]')].map(e=>{ const w=e.querySelector('.tdWhat'), s=w.querySelector('.tdWhere'); const lh=parseFloat(getComputedStyle(w).lineHeight)||20;
      const h = w.getBoundingClientRect().height - (s && getComputedStyle(s).display!=='none' ? s.getBoundingClientRect().height : 0); return {k:e.dataset.kind, h:Math.round(h), lh:Math.round(lh), ok:h <= lh*1.6}; })""")


def tap(page, kind, i=0):
    page.locator(f'.tdRow[data-kind="{kind}"]').nth(i).click(); page.wait_for_timeout(450)


def at_idea(page, iid, tab):
    return js(page, "([i,t])=>({tab:activeTab, view:wlView, sel:ideaSel, sub:ideaSubMem(i), want:t})", [iid, tab])


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ───── 1 · A: kill hit ─────
    ideas = [idea("ia", "ไอเดียสัญญาณชน", kill_level="hit"),
             idea("ip", "ไอเดียพักที่ชน", status="parked", kill_level="hit"),
             idea("id", "ไอเดียสำรวจที่ชน", status="exploring", kill_level="hit"),
             idea("in", "ไอเดียปกติ")]
    b, c, page, ce, pe, dl = launcher(pw, w, h, ideas)
    try:
        r = rows(page, "idea-kill")
        chk(f"{tag} 1 kill hit → แถวด่วน 💡 แถวเดียว (ไอเดียพัก / กำลังสำรวจ ที่ชน = ไม่ขึ้น)", len(r) == 1 and r[0]["grp"] == "r", json.dumps(r, ensure_ascii=False)[:400])
        chk(f"{tag} 1 ข้อความ '💡 ไอเดียสัญญาณชน สัญญาณพักชน — ทบทวนไอเดีย' · sub = signal ที่ hit", r and r[0]["full"].startswith("💡") and "ไอเดียสัญญาณชน สัญญาณพักชน — ทบทวนไอเดีย" in r[0]["t"] and "สัญญาณทดสอบ ia" in r[0]["sub"], json.dumps(r, ensure_ascii=False)[:400])
        chk(f"{tag} 1 ป้ายแดงบนปุ่มแท็บ Today นับแถวนี้", js(page, "()=>document.getElementById('tabBadgeToday').textContent") == "1")
        shot(page, f"id4-today-ideas-{sfx}.png")
        ol = one_line(page)
        chk(f"{tag} 1 แถวไอเดียบรรทัดเดียว", ol and all(x["ok"] for x in ol), json.dumps(ol))
        tap(page, "idea-kill")
        a = at_idea(page, "ia", "sum")
        chk(f"{tag} 1 แตะ → Watch › Ideas › การ์ดนั้น › สรุป", a["tab"] == "watch" and a["view"] == "idea" and a["sel"] == "ia" and a["sub"] == "sum", json.dumps(a))
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
        # ideas listener เปลี่ยน → Today วาดใหม่เอง
        reseed_idea(page, idea("ib", "ไอเดียที่เพิ่งชน", kill_level="hit"))
        chk(f"{tag} 1 ideas เปลี่ยน (snapshot) → Today วาดใหม่ มี 2 แถวด่วนจากไอเดีย", len(rows(page, "idea-kill")) == 2, json.dumps(rows(page, "idea-kill"))[:300])
        reseed_idea(page, idea("ib", "ไอเดียที่เพิ่งชน", status="parked", kill_level="hit"))
        chk(f"{tag} 1 ตั้งเป็น พัก → แถวหาย", len(rows(page, "idea-kill")) == 1)
        chk(f"{tag} 7 (1) ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()

    # ───── 2 · B: ถืออยู่ฝั่ง ▼ ─────
    ideas = [idea("rb", "ไอเดียส่งต่อ", status="ready", date="2026-10-02", losers=[loser("HELD", "พึ่งพารายได้จากส่วนที่เสีย")]),
             idea("nb", "ไอเดียรอหลักฐาน", status="need_evidence", date="2026-10-02", losers=[loser("HELD")]),
             idea("sb", "ไอเดีย loser รอตรวจ", status="ready", date="2026-10-03", losers=[loser("HELD", state="screen")])]
    b, c, page, ce, pe, dl = launcher(pw, w, h, ideas)
    try:
        r = rows(page, "idea-held")
        chk(f"{tag} 2 B: ถือ HELD อยู่ฝั่ง ▼ ของไอเดียพร้อมส่งต่อ · Thesis (20 ก.ย.) เก่ากว่าไอเดีย (2 ต.ค.) → 1 แถว กลุ่ม a (รอหลักฐาน / state screen = ไม่มี)", len(r) == 1 and r[0]["grp"] == "a", json.dumps(r, ensure_ascii=False)[:400])
        chk(f"{tag} 2 ข้อความ '💡 HELD ▼ ไอเดียส่งต่อ — update Thesis' · sub = losers[].why", r and r[0]["full"].startswith("💡") and "HELD ▼ ไอเดียส่งต่อ — update Thesis" in r[0]["t"] and "พึ่งพารายได้จากส่วนที่เสีย" in r[0]["sub"], json.dumps(r, ensure_ascii=False)[:400])
        tap(page, "idea-held")
        a = js(page, "()=>({tab:activeTab, view:wlView, sel:wlSel, sub:wlSub})")
        chk(f"{tag} 2 แตะ → Watch › การ์ดหุ้นนั้น › สรุป", a == {"tab": "watch", "view": "wl", "sel": "HELD", "sub": "sum"}, json.dumps(a))
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
        reseed_wl(page, "HELD", "2026-10-03")
        chk(f"{tag} 2 Import Thesis ฉบับใหม่ (3 ต.ค. ≥ 2 ต.ค.) → แถวหาย", len(rows(page, "idea-held")) == 0)
        reseed_wl(page, "HELD", "2026-09-30")
        chk(f"{tag} 2 Thesis เก่ากว่าไอเดียอีกครั้ง → กลับมา", len(rows(page, "idea-held")) == 1)
        page.evaluate("()=>firebase.firestore().collection('users').doc('testuid').collection('watchlist').doc('HELD').delete()"); page.wait_for_timeout(500)
        chk(f"{tag} 2 ไม่มี Thesis / ไม่อยู่ Watchlist เลย → ยังมีแถว (ยังไม่มี Thesis)", len(rows(page, "idea-held")) == 1)
        chk(f"{tag} 7 (2) ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()
    # หุ้นที่ไม่ได้ถือ → ไม่มี B
    b, c, page, ce, pe, dl = launcher(pw, w, h, [idea("rb", "ไอเดียส่งต่อ", status="ready", date="2026-10-02", losers=[loser("NOTHELD")])], wl=(("NOTHELD", "2026-09-01"),))
    try:
        chk(f"{tag} 2 loser ที่ไม่ได้ถือ (ไม่มีการ์ด Core open) → ไม่มี B", len(rows(page, "idea-held")) == 0)
    finally: b.close()

    # ───── 3 · C: ส่งต่อ → Watchlist ─────
    ideas = [idea("c1", "ไอเดียส่งต่อบริษัท", cands=[cand("NEWC", 1), cand("WAITC", 2, state="wait"), cand("NOSRC", 3, src=""), cand("INWL", 4), cand("THCO.BK", 5, market="TH")], date="2026-10-04")]
    b, c, page, ce, pe, dl = launcher(pw, w, h, ideas, wl=(("HELD", "2026-09-20"), ("INWL", None)))
    try:
        r = rows(page, "idea-study")
        names = [x["t"] for x in r]
        chk(f"{tag} 3 C: study + relevance_src + ไม่อยู่ WL → NEWC และ THCO.BK (WAITC wait · NOSRC ไม่มีแหล่ง · INWL อยู่ WL แล้ว = ไม่มี)", len(r) == 2 and "ส่งต่อ NEWC → Watchlist" in names[0] and "ส่งต่อ THCO.BK → Watchlist" in names[1] and all(x["grp"] == "b" and x["full"].startswith("💡") for x in r), json.dumps(r, ensure_ascii=False)[:500])
        chk(f"{tag} 3 sub = ชื่อไอเดีย", all("ไอเดียส่งต่อบริษัท" in x["sub"] for x in r))
        tg = tags(page, "idea-study")
        chk(f"{tag} 3 tag selUS (NEWC) / selTH (THCO.BK)", tg == [["selUS"], ["selTH"]], json.dumps(tg))
        tap(page, "idea-study", 0)
        a = at_idea(page, "c1", "co")
        chk(f"{tag} 3 แตะ → Ideas › การ์ดนั้น › แท็บ บริษัท", a["tab"] == "watch" and a["view"] == "idea" and a["sel"] == "c1" and a["sub"] == "co", json.dumps(a))
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
        seed_wl_live = lambda s: page.evaluate("(s)=>firebase.firestore().collection('users').doc('testuid').collection('watchlist').doc(s).set({ticker:s,market:'US',port:'core',note:'',industry:'',added_at:'2026-10-05T00:00:00.000Z'})", s)
        seed_wl_live("NEWC"); page.wait_for_timeout(500)
        chk(f"{tag} 3 เพิ่ม NEWC เข้า WL → แถวหาย (เหลือ THCO.BK)", [x["t"] for x in rows(page, "idea-study")] == ["💡 ส่งต่อ THCO.BK → Watchlist"] or len(rows(page, "idea-study")) == 1 and "THCO.BK" in rows(page, "idea-study")[0]["t"], json.dumps(rows(page, "idea-study"), ensure_ascii=False)[:300])
        chk(f"{tag} 7 (3) ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()
    # บริษัทเดียวอยู่หลายไอเดีย → 1 แถว (ไอเดียที่ rank ดีสุด)
    ideas = [idea("m1", "ไอเดียแรก", cands=[cand("DUP", 3)]), idea("m2", "ไอเดียสอง", cands=[cand("DUP", 1)])]
    b, c, page, ce, pe, dl = launcher(pw, w, h, ideas)
    try:
        r = rows(page, "idea-study")
        chk(f"{tag} 3 บริษัทเดียวอยู่ 2 ไอเดีย → 1 แถว · sub = ไอเดียที่ rank ดีสุด (ไอเดียสอง)", len(r) == 1 and "ไอเดียสอง" in r[0]["sub"], json.dumps(r, ensure_ascii=False)[:300])
    finally: b.close()

    # ───── 4 · D: เช็คหลักฐาน ─────
    ideas = [idea("d_today", "ถึงวันนัด", recheck={"date": "2026-10-05", "what": "ยอดขาย Q3"}),
             idea("d_future", "นัดอนาคต", date="2026-10-04", recheck={"date": "2026-10-20", "what": "ยังไม่ถึง"}),
             idea("d_ready", "พร้อมส่งต่อแต่ถึงนัด", status="ready", recheck={"date": "2026-10-01", "what": "ไม่นับ"})]
    b, c, page, ce, pe, dl = launcher(pw, w, h, ideas)
    try:
        r = rows(page, "idea-recheck")
        chk(f"{tag} 4 D: recheck = วันนี้ → 1 แถว (นัดอนาคต · ไอเดียพร้อมส่งต่อ = ไม่มี) กลุ่ม a", len(r) == 1 and r[0]["grp"] == "a", json.dumps(r, ensure_ascii=False)[:300])
        chk(f"{tag} 4 ข้อความ '💡 เช็คหลักฐาน: ถึงวันนัด (ยอดขาย Q3)' · tag selUS · แตะ → หลักฐาน", r and r[0]["full"].startswith("💡") and "เช็คหลักฐาน: ถึงวันนัด (ยอดขาย Q3)" in r[0]["t"] and tags(page, "idea-recheck") == [["selUS"]], json.dumps([r, tags(page, "idea-recheck")], ensure_ascii=False)[:300])
        tap(page, "idea-recheck")
        a = at_idea(page, "d_today", "evd")
        chk(f"{tag} 4 แตะ → Ideas › การ์ดนั้น › แท็บ หลักฐาน", a["tab"] == "watch" and a["view"] == "idea" and a["sel"] == "d_today" and a["sub"] == "evd", json.dumps(a))
    finally: b.close()
    ideas = [idea("o31", "เก่า 31 วัน", date="2026-09-04", scope=("TH",), recheck={"date": "2026-12-31", "what": "ไกล"}), idea("o30", "เก่า 30 วัน", date="2026-09-05"),
             idea("nw", "ไม่มี what", date="2026-10-04", recheck={"date": "2026-10-05"})]
    b, c, page, ce, pe, dl = launcher(pw, w, h, ideas)
    try:
        r = rows(page, "idea-recheck")
        chk(f"{tag} 4 date เก่า 31 วัน → มี · 30 วัน → ไม่มี · 2 ไอเดียเข้าเงื่อนไข → แสดง 1 (recheck เก่าสุดก่อน = 'ไม่มี what')", len(r) == 1 and "ไม่มี what" in r[0]["t"] and "(" not in r[0]["t"], json.dumps(r, ensure_ascii=False)[:300])
    finally: b.close()
    b, c, page, ce, pe, dl = launcher(pw, w, h, [ideas[0], ideas[1]])
    try:
        r = rows(page, "idea-recheck")
        chk(f"{tag} 4 เหลือ o31 (เก่า 31 วัน) → 1 แถว tag selTH ตาม scope[0] · o30 ไม่ขึ้น", len(r) == 1 and "เก่า 31 วัน" in r[0]["t"] and tags(page, "idea-recheck") == [["selTH"]], json.dumps([r, tags(page, "idea-recheck")], ensure_ascii=False)[:300])
    finally: b.close()

    # ───── 5 · เพดาน 2 แถว/วัน ─────
    ideas = [idea("ca1", "ด่วนหนึ่ง", kill_level="hit"), idea("ca2", "ด่วนสอง", kill_level="hit"),
             idea("cb", "ไอเดีย B", status="ready", date="2026-10-02", losers=[loser("HELD")]),
             idea("cc", "ไอเดีย C", cands=[cand("CAND1", 1), cand("CAND2", 2), cand("CAND3", 3)]),
             idea("cd", "ไอเดีย D", recheck={"date": "2026-10-05", "what": "นัดวันนี้"})]
    b, c, page, ce, pe, dl = launcher(pw, w, h, ideas)
    try:
        rr = all_idea_rows(page)
        urgent = [x for x in rr if x["g"] == "r"]; other = [x for x in rr if x["g"] != "r"]
        chk(f"{tag} 5 นอกด่วน: แถว 💡 แค่ 2 · B ก่อน แล้ว C ตัวแรก (CAND2/CAND3/D ถูกตัด · ไม่มีข้อความ 'อีก n')", [x["k"] for x in other] == ["idea-held", "idea-study"] and "CAND1" in other[1]["t"], json.dumps(other, ensure_ascii=False))
        chk(f"{tag} 5 A 2 ไอเดีย → ด่วนมี 2 แถว (ไม่นับเพดาน)", [x["k"] for x in urgent] == ["idea-kill", "idea-kill"], json.dumps(urgent, ensure_ascii=False))
        body = js(page, "()=>document.querySelector('[data-td-wrap]').innerText")
        chk(f"{tag} 5 ไม่มีข้อความ 'อีก n' ของแถวที่ถูกตัด", "CAND2" not in body and "CAND3" not in body and "นัดวันนี้" not in body and "อีก 3" not in body)
        shot(page, f"id4-today-cap-{sfx}.png")
        ol = one_line(page)
        chk(f"{tag} 5 ทุกแถว 💡 บรรทัดเดียว (4 แถว)", len(ol) == 4 and all(x["ok"] for x in ol), json.dumps(ol))
        chk(f"{tag} 7 (5) ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()
    # ชื่อยาว → ตัด …
    longname = "ไอเดียที่ชื่อยาวมากมายก่อนจะถึงคำว่าสัญญาณพักชนแน่นอนแน่ๆ ยาวต่อไปอีกหลายสิบตัวอักษร"
    b, c, page, ce, pe, dl = launcher(pw, w, h, [idea("lg", longname, kill_level="hit")])
    try:
        r = rows(page, "idea-kill")
        ol = one_line(page)
        chk(f"{tag} 5 ชื่อไอเดียยาว → ตัด '…' · ไม่ล้นบรรทัดเดียว", len(r) == 1 and "…" in r[0]["t"] and longname not in r[0]["t"] and all(x["ok"] for x in ol), json.dumps([r, ol], ensure_ascii=False)[:400])
    finally: b.close()

    # ───── 6 · ไม่มีไอเดียเข้าเงื่อนไข / อ่านไม่ได้ ─────
    ideas = [idea("q1", "ร่าง", status="draft", kill_level="hit"), idea("q2", "สำรวจ", status="exploring", kill_level="hit"), idea("q3", "พัก", status="parked", kill_level="hit"),
             idea("q4", "รอหลักฐานปกติ", recheck={"date": "2026-11-30", "what": "ยังไม่ถึง"}, losers=[loser("HELD")], cands=[cand("WAITX", 1, state="wait")], assets=[{"asset": "XAUUSD", "dir": "↑", "why": "x"}])]
    b, c, page, ce, pe, dl = launcher(pw, w, h, ideas)
    try:
        chk(f"{tag} 6 ไม่มีไอเดียเข้าเงื่อนไข → ไม่มีแถว 💡 เลย (ร่าง/สำรวจ/พัก/รอหลักฐานปกติ/asset/▲▼)", len(all_idea_rows(page)) == 0, json.dumps(all_idea_rows(page), ensure_ascii=False))
        chk(f"{tag} 6 บรรทัด '✓ อื่น ๆ ปกติ' ยังทำงานเดิม", js(page, "()=>(document.querySelector('[data-td-okline] .txt')||{}).textContent||''").replace("\n", " ").strip().startswith("✓ อื่น ๆ ปกติ") or "อื่น ๆ ปกติ" in js(page, "()=>document.querySelector('[data-td-okline]').textContent"))
        chk(f"{tag} 6 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally: b.close()
    b, c, page, ce, pe, dl = launcher(pw, w, h, [idea("z1", "ชนแต่ rules ปิด", kill_level="hit")], deny=True)
    try:
        chk(f"{tag} 6 ideas อ่านไม่ได้ (rules) → ไม่มีแถวจากไอเดีย · Today ยังวาด · ไม่มี pageerror", len(all_idea_rows(page)) == 0 and page.locator("[data-td-wrap]").count() == 1 and not pe, json.dumps([all_idea_rows(page), pe]))
    finally: b.close()

    # ───── 7 · Routine Selection นับ C/D ที่ tag selUS ─────
    ideas = [idea("s1", "ไอเดียส่งต่อ", cands=[cand("SELX", 1)]), idea("s2", "ไอเดียเช็ค", recheck={"date": "2026-10-05", "what": "ตรวจ"}, date="2026-10-04")]
    b, c, page, ce, pe, dl = launcher(pw, w, h, ideas)
    try:
        info = js(page, """()=>{ const n = tdLast.tasks.filter(t=>(t.tags||[]).includes('selUS')).length, idea = tdLast.tasks.filter(t=>(t.tags||[]).includes('selUS') && t.kind.startsWith('idea-')).length;
          const slots = tdLast.rt.slots.filter(s=>tdSlotTag(s)==='selUS').map(s=>{ const e = document.querySelector('[data-slot-n="'+s.id+'"]'); return e ? +e.textContent : 0; }); return {n, idea, slots}; }""")
        chk(f"{tag} 7 ช่อง Routine Selection US นับรวมแถว C/D ที่ tag selUS (ไอเดีย 2 แถว)", info["idea"] == 2 and info["slots"] and all(s == info["n"] for s in info["slots"]), json.dumps(info))
        ol = one_line(page)
        chk(f"{tag} 7 แถวไอเดียทุกแถวบรรทัดเดียว · ไม่ล้นแนวนอน · ไม่มี console error", len(ol) == 2 and all(x["ok"] for x in ol) and overflow(page) <= 0 and not ce and not pe, json.dumps([ol, overflow(page), ce, pe]))
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 50 / ID4) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
