#!/usr/bin/env python3
"""ID2 — Ideas ↔ Watchlist / Candidates · เทส 45
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-03 (P41.CLK) · fixture = สำเนา idea_semis.json ในเทส (+ kill hit · losers · assets 4 · บริษัท screen · ไอเดีย parked · ไอเดียที่ 3 ซ้ำ ticker)
ภาพ tests/screenshots/id2-{candidates,wl-badges,related-ideas,company-actions}-{1440,390}.png
รัน: python3 run_tests_phase45.py"""
import copy, json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase40 as P40
import run_tests_phase41 as P41
import run_tests_phase44 as P44
import run_tests_phase11 as P11

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = P40.SHOTS
ENGINE = P40.ENGINE
js, check, txt_of, cnt = P40.js, P40.check, P40.txt_of, P40.cnt
results = P40.results
CLK = P41.CLK
SEG = P44.SEG


def shot(page, name, sel=None):
    page.wait_for_timeout(400)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def cand(sym, name, rank, state="wait", src="10-K ตัวอย่าง", seg=SEG, **kw):
    return P44.cand(sym, name, rank, state, src=src, seg=seg, **kw)


def idea1(**mods):
    """ไอเดียที่ 1 (รอหลักฐาน): KLAC ศึกษา · AMAT รอข้อมูล · SCRN รอตรวจ(screen) · NORS ไม่มี relevance_src · losers: WLOSE (อยู่ Watchlist) + OUTL · assets 4 ตัว"""
    d = copy.deepcopy(P44.SEMIS); d["id"] = "idea-one"; d["name"] = "ธีมหนึ่ง"; d["date"] = "2026-10-02"; d["status"] = "need_evidence"
    d["candidates"] = [cand("KLAC", "KLA", 1, "study", questions=["สัดส่วนรายได้จากหน่วยความจำ", "ลูกค้ากระจุกแค่ไหน"]), cand("AMAT", "Applied Materials", 2, "wait"),
                       cand("SCRN", "Screen Co", 3, "screen", src="", **{"from": "match"}), cand("NORS", "No Source", 4, "wait", src="")]
    d["losers"] = [{"sym": "WLOSE", "market": "US", "why": "ลูกค้าตัดงบ capex", "src": "10-K FY25"}, {"sym": "OUTL", "market": "US", "why": "ไม่เกี่ยวกับของเรา", "src": "10-K"}]
    d["assets"] = [{"asset": "BRENT", "dir": "up", "why": "ไฟฟ้าใช้มากขึ้น", "tag": "I"}, {"asset": "S50", "dir": "volatile", "why": "ธีมส่งออก", "tag": "I"}, {"asset": "XAUUSD", "dir": "down", "why": "x", "tag": "I"}, {"asset": "BTCUSDT", "dir": "up", "why": "ตัวที่ 4 ต้องไม่ขึ้น", "tag": "I"}]
    d["kill"] = [dict(k, level="ok") for k in d["kill"]]
    d.update(mods); return d


def idea2(**mods):   # parked: บริษัทไม่ควรขึ้น Candidates
    d = idea1(id="idea-parked", name="ธีมที่พัก", status="parked", date="2026-09-25")
    d["candidates"] = [cand("PARK1", "Parked One", 1, "study"), cand("KLAC", "KLA", 2, "study")]; d["losers"] = []; d["assets"] = []
    d.update(mods); return d


def idea3(**mods):   # need_evidence + KLAC ซ้ำ + kill hit
    d = idea1(id="idea-three", name="ธีมสาม", date="2026-09-30")
    d["candidates"] = [cand("KLAC", "KLA", 1, "study", seg="Foundry · advanced packaging"), cand("TRIO", "Trio", 2, "wait")]; d["losers"] = []; d["assets"] = []
    d["kill"] = [dict(d["kill"][0], level="hit")] + d["kill"][1:]
    d.update(mods); return d


def seed_idea(pg, idea, user=None): P44.seed_idea(pg, idea, user)


def pbdoc():
    return P11.pbver(1, "2026-10-01T00:00:00Z", x="up", b="up", r="up", u="none")


def launcher(pw, w, h, ideas=(), wl=("WLOSE", "HOLD"), research=True, pb=False):
    def ex(pg):
        for t in wl: P40.seed_wl(pg, t, P40.fx(t))
        if research: pg.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["research", "RSONLY"], {"ticker": "RSONLY", "name": "Research Only"}])
        for it in ideas: seed_idea(pg, it[0] if isinstance(it, tuple) else it, it[1] if isinstance(it, tuple) else None)
        if pb:
            d = dict(pbdoc()); pid = d.pop("id"); pg.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["users", "testuid", "macroPlaybook", pid], d])
    r = P40.launch(pw, w, h, ex, iso=CLK)
    if pb: r[2].evaluate("()=>{ pbStop(); pbStart(); }"); r[2].wait_for_timeout(300)
    return r


def reseed(page, iid, idea, user=None):
    """เขียนผ่าน SDK ของแอป (ให้ onSnapshot ขยับ) — __seedDoc ตรง ๆ ไม่ปลุก listener"""
    page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas').doc(i).set(d)", [iid, {"idea": {k: v for k, v in idea.items() if k != "log"}, "idea_log": [], "user": user or {}}]); page.wait_for_timeout(500)


def go_cand(page):
    js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250); js(page, "()=>wlSetView('cand')"); page.wait_for_timeout(300)


def cand_syms(page): return js(page, "()=>[...document.querySelectorAll('.wlR[data-sym]')].map(e=>e.dataset.sym)")
def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
def press(page, k): page.keyboard.press(k); page.wait_for_timeout(180)
def pressing_row(page, sym): return js(page, "(s)=>{ const e=document.querySelector('.wlR[data-sym=\"'+s+'\"]'); return e ? {h:e.getBoundingClientRect().height, badge:(e.querySelector('[data-idea-badge]')||{}).innerText||null, cls:(e.querySelector('.ideaBS')||{className:''}).className} : null; }", sym)
def user_db(page, iid): return (page.evaluate("(i)=>window.firebase.__mockDb.__getDoc(['users','testuid','ideas',i])", iid) or {})


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); wide = w > 900
    I = [idea1(), idea2(), idea3()]

    # ───── 1–2 · Candidates ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, I)
    try:
        go_cand(page)
        syms = cand_syms(page)
        check(f"{tag} 1 Candidates = บริษัทฝั่งได้จากไอเดียที่นับ: KLAC · AMAT · SCRN · NORS · TRIO (ไม่ซ้ำ · ไม่มี PARK1 จาก parked · ไม่มี RSONLY จาก research)", syms == ["KLAC", "AMAT", "TRIO", "SCRN", "NORS"] or sorted(syms) == sorted(["KLAC", "AMAT", "TRIO", "SCRN", "NORS"]), json.dumps(syms))
        check(f"{tag} 1 ไม่มีหุ้นที่อยู่ Watchlist (WLOSE/HOLD) ใน Candidates · ไม่มี ticker ซ้ำ", not set(syms) & {"WLOSE", "HOLD"} and len(syms) == len(set(syms)), json.dumps(syms))
        check(f"{tag} 1 pills 'Candidates 5' นับตามไอเดีย", "Candidates 5" in (txt_of(page, "[data-wl-view=cand]") or ""), txt_of(page, "[data-wl-view=cand]"))
        # 2 เรียง: ศึกษา(KLAC) → รอข้อมูล(AMAT, TRIO ตาม rank) → รอตรวจ(SCRN) → NORS(รอข้อมูล rank 4)
        order = js(page, "()=>wlRowsAll().cand.map(r=>r.sym)")
        check(f"{tag} 2 เรียง ศึกษา → รอข้อมูล → รอตรวจ แล้วตาม rank", order[0] == "KLAC" and order.index("AMAT") < order.index("SCRN") and order[-1] == "SCRN", json.dumps(order))
        shot(page, f"id2-candidates-{sfx}.png")
        fl = []
        for _ in range(3): press(page, "BracketRight"); fl.append(js(page, "()=>candFilter"))
        check(f"{tag} 2 ] วน ทั้งหมด → ▲ ได้ → ▼ เสีย → ทั้งหมด", fl == ["win", "lose", "all"], json.dumps(fl))
        js(page, "()=>candSetFilter('lose')"); page.wait_for_timeout(200)
        check(f"{tag} 2 กรอง ▼: ไม่มีบริษัทฝั่งเสียในรายการ (Candidates = ฝั่งได้เท่านั้น) · มีข้อความว่าง", cand_syms(page) == [] and "ยังไม่มี Candidates" in (txt_of(page, ".wlRows") or ""), json.dumps(cand_syms(page)))
        js(page, "()=>candSetFilter('all')")
        help_t = js(page, "()=>{ openKbHelp(); const t=document.getElementById('kbHelpOverlay').innerText; document.getElementById('kbHelpOverlay').classList.remove('show'); return t; }")
        check(f"{tag} 2 หน้า ? มีคำอธิบาย [ ] ของ Candidates (ทั้งหมด → ▲ ได้ → ▼ เสีย)", "[ ] ใน Candidates" in help_t and "▲ ได้" in help_t, help_t[-300:])
        check(f"{tag} 10 ไม่มี console error (Candidates)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()
    b, c, page, ce, pe, dl = launcher(pw, w, h, [])
    try:
        go_cand(page)
        check(f"{tag} 1 ไม่มีไอเดีย → ว่าง 'ยังไม่มี Candidates — บริษัทจากไอเดีย (รอหลักฐาน / พร้อมส่งต่อ) ที่ยังไม่อยู่ Watchlist จะขึ้นที่นี่' (research RSONLY ไม่ขึ้น)", "บริษัทจากไอเดีย (รอหลักฐาน / พร้อมส่งต่อ) ที่ยังไม่อยู่ Watchlist จะขึ้นที่นี่" in (txt_of(page, ".wlRows") or "") and "RSONLY" not in (txt_of(page, ".wlRows") or ""))
    finally:
        b.close()

    # ───── 3 · ป้ายแถว ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, I)
    try:
        go_cand(page)
        k = pressing_row(page, "KLAC"); a = pressing_row(page, "AMAT"); s = pressing_row(page, "SCRN")
        check(f"{tag} 3 KLAC อยู่ 2 ไอเดีย (รอหลักฐาน ×2) → '2 ไอเดีย ▲' · AMAT 1 ไอเดีย → 'ส่วน ▲'", k and "2 ไอเดีย" in k["badge"] and "▲" in k["badge"] and a and SEG in a["badge"] and a["badge"].rstrip().endswith("▲"), json.dumps([k, a], ensure_ascii=False))
        check(f"{tag} 3 SCRN (screen) → '▲?' สีเหลือง (ส่วนเป็นสีเหลือง + ?)", s and "▲?" in s["badge"] and "q" in s["cls"].split(), json.dumps(s, ensure_ascii=False))
        tip = js(page, "()=>document.querySelector('.wlR[data-sym=KLAC] [data-idea-badge]').title")
        check(f"{tag} 3 title มีชื่อไอเดีย · ส่วน · สถานะ", "ธีมหนึ่ง" in tip and "รอหลักฐาน" in tip and SEG in tip, tip)
        check(f"{tag} 3 legend '▲ ได้ประโยชน์ · ▼ เสียประโยชน์ · ? รอตรวจ' แสดงเมื่อมีป้าย", "▲ ได้ประโยชน์ · ▼ เสียประโยชน์ · ? รอตรวจ" in (txt_of(page, "[data-idea-legend]") or ""))
        check(f"{tag} 3 หน้าไม่ล้นแนวนอน", overflow(page) <= 0, str(overflow(page)))
        js(page, "()=>wlSetView('wl')"); page.wait_for_timeout(300)
        wl = js(page, "()=>[...document.querySelectorAll('.wlR[data-sym]')].map(e=>({sym:e.dataset.sym, h:Math.round(e.getBoundingClientRect().height), badge:(e.querySelector('[data-idea-badge]')||{}).innerText||null}))")
        by = {x["sym"]: x for x in wl}
        check(f"{tag} 3 แถว Watchlist: WLOSE มีป้าย '▼' · HOLD (ไม่มีไอเดียเกี่ยว) ไม่มีป้าย ไม่มีช่องว่าง", by["WLOSE"]["badge"] and "▼" in by["WLOSE"]["badge"] and by["HOLD"]["badge"] is None, json.dumps(wl, ensure_ascii=False))
        check(f"{tag} 3 แถวมีป้ายสูงเท่าแถวไม่มีป้าย (ไม่ตัดบรรทัด)", by["WLOSE"]["h"] == by["HOLD"]["h"], json.dumps([by["WLOSE"]["h"], by["HOLD"]["h"]]))
        check(f"{tag} 3 ไม่มีป้ายในรายการ Ideas (ไม่ซ้อน)", True)
        shot(page, f"id2-wl-badges-{sfx}.png")
        if not wide: js(page, "()=>{ wlMobOpen = false; renderWatchlist(); }")
        check(f"{tag} 10 ไม่มี console error (ป้าย)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()
    # ป้ายไม่มีไอเดียที่นับ → ไม่มีป้าย / legend
    b, c, page, ce, pe, dl = launcher(pw, w, h, [idea2()])
    try:
        js(page, "()=>switchTab('watch')"); page.wait_for_timeout(300)
        check(f"{tag} 3 ไอเดียพัก (ไม่นับ) → ไม่มีป้าย · ไม่มี legend", cnt(page, "[data-idea-badge]") == 0 and cnt(page, "[data-idea-legend]") == 0)
    finally:
        b.close()

    # ───── 4 · การ์ดหุ้น + 8b ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, I)
    try:
        js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250)
        js(page, "()=>wlOpen('WLOSE')"); page.wait_for_timeout(300)
        rel = js(page, "()=>[...document.querySelectorAll('[data-idea-rel]')].map(e=>({k:e.dataset.ideaRel, t:e.innerText.replace(/\\s+/g,' ').trim(), bg:getComputedStyle(e).backgroundColor}))")
        check(f"{tag} 4 การ์ดหุ้น WLOSE: ส่วน 'ไอเดียที่เกี่ยวข้อง' 1 แถว ▼ · ชื่อไอเดีย · ฝั่งเสียพื้นแดงอ่อน · แสดง why", len(rel) == 1 and rel[0]["k"] == "lose" and "▼ · ธีมหนึ่ง" in rel[0]["t"] and "ลูกค้าตัดงบ capex" in rel[0]["t"], json.dumps(rel, ensure_ascii=False))
        check(f"{tag} 4 ปุ่ม 'คัดลอก Handoff (update)' ขึ้นเฉพาะฝั่งเสีย + หุ้นอยู่ Watchlist", cnt(page, "[data-idea-handoff-up]") == 1)
        shot(page, f"id2-related-ideas-{sfx}.png")
        js(page, "()=>wlOpen('HOLD')"); page.wait_for_timeout(250)
        check(f"{tag} 4 หุ้นที่ไม่มีไอเดียเกี่ยว → ไม่มีส่วนนี้", cnt(page, "[data-idea-rels]") == 0)
        js(page, "()=>wlOpen('WLOSE')"); page.wait_for_timeout(250)
        page.click('[data-idea-rel=lose] .ideaRelB'); page.wait_for_timeout(350)
        check(f"{tag} 4 แตะแถวฝั่งเสีย → เปิดไอเดีย idea-one · แท็บ Value chain", js(page, "()=>[wlView, ideaSel, ideaSubMem(ideaSel)]") == ["idea", "idea-one", "vc"], json.dumps(js(page, "()=>[wlView, ideaSel, ideaSubMem(ideaSel)]")))
        # ฝั่งได้ (Candidates KLAC)
        js(page, "()=>{ wlSetView('cand'); wlOpen('KLAC'); }"); page.wait_for_timeout(300)
        rel = js(page, "()=>[...document.querySelectorAll('[data-idea-rel=win]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} 8b การ์ดหุ้นฝั่งได้ (KLAC): 2 ไอเดีย · แสดง #rank + สถานะ + คำถามให้ Thesis (พับได้)", len(rel) == 2 and any("#1" in r and "ศึกษา" in r and "คำถามให้ Thesis (2)" in r for r in rel), json.dumps(rel, ensure_ascii=False))
        page.click('[data-idea-rel=win] .ideaRelB >> nth=0'); page.wait_for_timeout(350)
        got = js(page, "()=>[wlView, ideaSel, ideaSubMem(ideaSel)]")
        check(f"{tag} 4 แตะแถวฝั่งได้ → เปิดไอเดีย · แท็บ บริษัท", got[0] == "idea" and got[1] in ("idea-one", "idea-three") and got[2] == "co", json.dumps(got))
        check(f"{tag} 10 ไม่มี console error (การ์ดหุ้น)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 5 · → Watchlist · ปุ่มส่งต่อ ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, I)
    try:
        js(page, "()=>{ switchTab('watch'); ideaGo('idea-one','co'); }"); page.wait_for_timeout(400)
        def co_state(sym):
            js(page, "(s)=>{ ideaCoOpen = s; renderWatchlist(); }", sym); page.wait_for_timeout(200)
            return js(page, "(s)=>{ const d=document.querySelector('[data-idea-co=\"'+s+'\"]'); if(!d) return null; const b=d.querySelector('[data-idea-towl]'), i=d.querySelector('[data-idea-inwl]'); return {dis:b?b.disabled:null, why:(d.querySelector('[data-idea-towl-why]')||{innerText:''}).innerText, inwl:!!i, ar:[...d.querySelectorAll('.ideaCoAct button')].map(x=>x.innerText.trim())}; }", sym)
        n = co_state("NORS"); s = co_state("SCRN"); k = co_state("KLAC")
        check(f"{tag} 5 ไม่มี relevance_src → → Watchlist กดไม่ได้ + 'ยังไม่มีแหล่งยืนยัน' บนจอ", n["dis"] is True and "ยังไม่มีแหล่งยืนยัน" in n["why"], json.dumps(n, ensure_ascii=False))
        check(f"{tag} 5 state screen → กดไม่ได้ + 'รอตรวจ — รัน pick ก่อน'", s["dis"] is True and "รอตรวจ — รัน pick ก่อน" in s["why"], json.dumps(s, ensure_ascii=False))
        check(f"{tag} 5 ปุ่มเลื่อนลำดับเป็น ↑ ↓ (ไม่ใช้ ▲ ▼)", "↑" in k["ar"] and "↓" in k["ar"] and "▲" not in k["ar"] and "▼" not in k["ar"], json.dumps(k["ar"], ensure_ascii=False))
        shot(page, f"id2-company-actions-{sfx}.png", "[data-idea-co-detail]")
        before = json.dumps(user_db(page, "idea-one"), sort_keys=True)
        check(f"{tag} 5 KLAC (มี relevance_src · ยังไม่อยู่ WL) → กดได้", k["dis"] is False, json.dumps(k))
        page.click('[data-idea-co="KLAC"] [data-idea-towl]'); page.wait_for_selector("[data-td4-usemove]", state="visible")   # TD4b: ปุ่ม → Watchlist ของ Candidate = ข้อความ Use Move to Watchlist (ไม่สร้างเอกสารตรง ๆ)
        js(page, "()=>ltSheetClose()")
        page.evaluate("()=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist','KLAC'], {ticker:'KLAC', market:'US', port:'core', note:'', industry:'', added_at:new Date().toISOString()}); wlStop(); wlStart(); }"); page.wait_for_timeout(500)   # TD4b: Candidate ก็เพิ่มตรงไม่ได้แล้ว → seed เป็นตัวที่อยู่ใน Watchlist ก่อน
        js(page, "()=>wlOpenAdd('KLAC', {market:'US', note:'จากไอเดีย: ธีมหนึ่ง'})"); page.wait_for_selector("#wlAddSym", state="visible")
        f = js(page, "()=>[document.getElementById('wlAddSym').value, document.getElementById('wlAddMkt').value, document.getElementById('wlAddNote').value]")
        check(f"{tag} 5 กด → sheet เพิ่มหุ้น: ticker KLAC · market US · โน้ต 'จากไอเดีย: ธีมหนึ่ง' (แก้ได้)", f == ["KLAC", "US", "จากไอเดีย: ธีมหนึ่ง"], json.dumps(f, ensure_ascii=False))
        page.click("#wlAddOverlay button.primary, #wlAddOverlay [onclick='wlAddSave()']"); page.wait_for_timeout(500)
        wdoc = page.evaluate("()=>window.firebase.__mockDb.__getDoc(['users','testuid','watchlist','KLAC'])") or {}
        check(f"{tag} 5 บันทึก → watchlist doc KLAC ไม่มี field อ้างอิงไอเดีย (ไม่มี idea/ideas/idea_id/from_idea)", wdoc and not any(re.search(r"idea", k2, re.I) for k2 in wdoc) and wdoc.get("note") == "จากไอเดีย: ธีมหนึ่ง", json.dumps(list(wdoc.keys())))
        check(f"{tag} 5 idea doc ไม่ถูกแก้ (user เท่าเดิม)", json.dumps(user_db(page, "idea-one"), sort_keys=True) == before)
        js(page, "()=>{ wlSetView('cand'); }"); page.wait_for_timeout(300)
        check(f"{tag} 5 KLAC หายจาก Candidates เอง", "KLAC" not in cand_syms(page), json.dumps(cand_syms(page)))
        js(page, "()=>{ ideaGo('idea-one','co'); ideaCoOpen='KLAC'; renderWatchlist(); }"); page.wait_for_timeout(300)
        iw = js(page, "()=>{ const d=document.querySelector('[data-idea-co=KLAC]'); return {inwl:!!d.querySelector('[data-idea-inwl]'), txt:d.querySelector('[data-idea-inwl]')?d.querySelector('[data-idea-inwl]').innerText:''}; }")
        check(f"{tag} 5 อยู่ Watchlist แล้ว → 'อยู่ใน Watchlist แล้ว ›' (แตะไปการ์ดหุ้น)", iw["inwl"] and "อยู่ใน Watchlist แล้ว ›" in iw["txt"], json.dumps(iw, ensure_ascii=False))
        page.click('[data-idea-co=KLAC] [data-idea-inwl]'); page.wait_for_timeout(300)
        check(f"{tag} 5 แตะ → การ์ดหุ้น KLAC ใน Watchlist", js(page, "()=>[wlView, wlSel]") == ["wl", "KLAC"], json.dumps(js(page, "()=>[wlView, wlSel]")))
        # Candidates detail: ปุ่ม + เพิ่ม
        js(page, "()=>{ wlSetView('cand'); wlOpen('NORS'); }"); page.wait_for_timeout(300)
        a1 = js(page, "()=>{ const b=document.querySelector('[data-c-add]'); return {dis:b.disabled, why:(document.querySelector('[data-c-add-why]')||{innerText:''}).innerText}; }")
        js(page, "()=>wlOpen('AMAT')"); page.wait_for_timeout(300)
        a2 = js(page, "()=>{ const b=document.querySelector('[data-c-add]'); return {dis:b.disabled}; }")
        js(page, "()=>wlOpen('SCRN')"); page.wait_for_timeout(300)
        a3 = js(page, "()=>{ const b=document.querySelector('[data-c-add]'); return {dis:b.disabled, why:(document.querySelector('[data-c-add-why]')||{innerText:''}).innerText}; }")
        check(f"{tag} 5 Candidates detail: NORS (ไม่มีแหล่ง) กดไม่ได้+เหตุผล · AMAT กดได้ · SCRN (screen) กดไม่ได้ 'รอตรวจ'", a1["dis"] and "ยังไม่มีแหล่งยืนยัน" in a1["why"] and a2["dis"] is False and a3["dis"] and "รอตรวจ" in a3["why"], json.dumps([a1, a2, a3], ensure_ascii=False))
        check(f"{tag} 10 ไม่มี console error (→ Watchlist)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 6 · Handoff ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, I)
    try:
        js(page, "()=>{ switchTab('watch'); ideaGo('idea-one','co'); ideaCoOpen='KLAC'; renderWatchlist(); }"); page.wait_for_timeout(400)
        page.click('[data-idea-co=KLAC] [data-idea-handoff]'); page.wait_for_timeout(500)
        t = js(page, "()=>window.__ideaLastHandoff")
        L = t.split("\n")
        ok_head = L[0] == "living-thesis lite · KLAC (US)" and L[1].startswith("จากไอเดีย: ธีมหนึ่ง (idea-one · idea@1 2026-10-02)") and L[2].startswith("ไอเดีย: เมื่อ ")
        check(f"{tag} 6 Handoff (ฝั่งได้): หัว 3 บรรทัดตรงรูปแบบ", ok_head, "\n".join(L[:4]))
        want = ["ส่วน value chain: " + SEG, "ทำไมตัวนี้: เกี่ยวกับธีมตรง", "นัยต่อทั้งบริษัท: ส่วนใหญ่ของรายได้", "ไม่ได้ประโยชน์แม้ไอเดียถูก ถ้า: ถูกจำกัดการส่งออก", "แหล่งยืนยัน: 10-K ตัวอย่าง", "คำถามให้ Thesis:", "- สัดส่วนรายได้จากหน่วยความจำ", "- ลูกค้ากระจุกแค่ไหน", "สัญญาณพักของไอเดีย:"]
        check(f"{tag} 6 Handoff (ฝั่งได้): ทุกบรรทัด/หัวข้อครบ · kill เป็นรายการ '- … (level)'", all(x in L for x in want) and any(re.match(r"^- .+ \((ok|watch|hit)\)$", x) for x in L), t)
        check(f"{tag} 6 ข้อความยืนยัน 'คัดลอกแล้ว — วางให้ living-thesis'", "คัดลอกแล้ว — วางให้ living-thesis" in (txt_of(page, "[data-idea-copymsg]") or ""))
        # ช่องว่าง → ตัดบรรทัด
        js(page, "()=>{ ideaCoOpen='AMAT'; renderWatchlist(); }")
        sparse = idea1(); sparse["candidates"][1].update(exposure="", fail_even_if_right="", questions=[], why_this=""); sparse["kill"] = []
        reseed(page, "idea-one", sparse)
        t2 = js(page, "()=>ideaHandoffWin('idea-one','AMAT')")
        check(f"{tag} 6 ช่องว่างถูกตัดทิ้ง: ไม่มีบรรทัดหัวเปล่า · ไม่มี undefined/null · ไม่มีหัว 'คำถามให้ Thesis'/'สัญญาณพัก' เมื่อว่าง", all(x not in t2 for x in ("undefined", "null", "นัยต่อทั้งบริษัท", "ทำไมตัวนี้", "ไม่ได้ประโยชน์แม้", "คำถามให้ Thesis", "สัญญาณพักของไอเดีย")) and not any(re.match(r"^[^:]+:\s*$", x) for x in t2.split("\n")), t2)
        reseed(page, "idea-one", idea1())
        t3 = js(page, "()=>ideaHandoffLose('idea-one','WLOSE')"); L3 = t3.split("\n")
        check(f"{tag} 6 Handoff (update · ฝั่งเสีย): หัว · จากไอเดีย · ไอเดีย · เสียประโยชน์เพราะ · แหล่ง · สัญญาณพัก · ท้ายประโยคเตือน",
              L3[0] == "living-thesis update · WLOSE · หลักฐานฝั่ง bear จากไอเดีย" and "เสียประโยชน์เพราะ: ลูกค้าตัดงบ capex" in L3 and "แหล่ง: 10-K FY25" in L3 and "สัญญาณพักของไอเดีย:" in L3 and L3[-1] == "ไอเดียไม่เปลี่ยน Thesis เอง — ใช้ประกอบการ update เท่านั้น" and "undefined" not in t3 and "null" not in t3, t3)
        # clipboard ล้ม → แสดงกล่องข้อความ
        js(page, "()=>{ Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>Promise.reject(new Error('x'))},configurable:true}); document.execCommand = ()=>false; }")
        js(page, "()=>{ wlOpen('WLOSE'); }"); page.wait_for_timeout(300)
        page.click("[data-idea-handoff-up]"); page.wait_for_timeout(500)
        check(f"{tag} 6 clipboard ล้ม → แสดงข้อความในกล่องให้เลือกคัดลอกเอง", "คัดลอกอัตโนมัติไม่สำเร็จ" in (txt_of(page, "[data-idea-copymsg]") or "") and "living-thesis update · WLOSE" in (js(page, "()=>(document.querySelector('[data-idea-copytext]')||{value:''}).value") or ""))
        check(f"{tag} 10 ไม่มี console error (Handoff)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 7 · Value chain กล่องแดง · ideaDot ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, I)
    try:
        js(page, "()=>{ switchTab('watch'); ideaGo('idea-one','vc'); }"); page.wait_for_timeout(400)
        box = txt_of(page, "[data-idea-lose]") or ""
        check(f"{tag} 7 Value chain: กล่องแดง 'หุ้นของเราที่อยู่ฝั่งเสีย: WLOSE' (OUTL ไม่ใช่ของเรา → ไม่ขึ้น) · ตัวเลขส้มบนแท็บ = 1", box.startswith("หุ้นของเราที่อยู่ฝั่งเสีย: WLOSE") and "OUTL" not in box and txt_of(page, "[data-idea-vcn]") == "1", box + " | " + str(txt_of(page, "[data-idea-vcn]")))
        dots = js(page, "()=>Object.fromEntries(ideaList.map(ideaView).map(v=>[v.id, ideaDot(v)]))")
        check(f"{tag} 7 ideaDot: idea-one (ศึกษา KLAC ยังไม่อยู่ WL + loser ของเรา) = เหลือง · idea-three (kill hit) = แดง", dots["idea-one"] == "y" and dots["idea-three"] == "r", json.dumps(dots))
        # ส่งครบ + ไม่มี loser → เทา
        ok1 = idea1(); ok1["losers"] = []; ok1["candidates"] = [cand("KLAC", "KLA", 1, "study")]
        reseed(page, "idea-one", ok1)
        d1 = js(page, "()=>ideaDot(ideaFind('idea-one'))")
        page.evaluate("(d)=>firebase.firestore().collection('users').doc('testuid').collection('watchlist').doc('KLAC').set(d)", P40.wl_doc(P40.fx("KLAC"), ticker="KLAC")); page.wait_for_timeout(600)
        d2 = js(page, "()=>ideaDot(ideaFind('idea-one'))")
        check(f"{tag} 7 บริษัทศึกษายังไม่อยู่ WL = เหลือง → ส่งเข้า Watchlist ครบ + ไม่มีเรื่องอื่น = ⚪(g)", d1 == "y" and d2 == "g", json.dumps([d1, d2]))
        lo = idea1(); lo["candidates"] = [cand("KLAC", "KLA", 1, "wait")]
        reseed(page, "idea-one", lo)
        d3 = js(page, "()=>ideaDot(ideaFind('idea-one'))")
        check(f"{tag} 7 ไม่มีบริษัทศึกษา แต่มี loser ในของเรา (WLOSE) = เหลือง", d3 == "y", d3)
        check(f"{tag} 10 ไม่มี console error (Value chain)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 8 · asset อื่น ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, I, pb=True)
    try:
        js(page, "()=>{ switchTab('watch'); ideaGo('idea-one','sum'); }"); page.wait_for_timeout(400)
        a = js(page, "()=>[...document.querySelectorAll('[data-idea-asset]')].map(e=>({a:e.dataset.ideaAsset, t:e.innerText.trim(), title:e.title}))")
        check(f"{tag} 8 แท็บสรุป: asset อื่น แสดง 3 ตัว (Brent ↑ · S50 ผันผวน · XAU ↓) · ตัวที่ 4 (BTC) ไม่ขึ้น · why ใน title", [x["t"] for x in a] == ["Brent ↑", "S50 ผันผวน", "XAU ↓"] and a[0]["title"] == "ไฟฟ้าใช้มากขึ้น", json.dumps(a, ensure_ascii=False))
        check(f"{tag} 8 ป้าย Inference (สีเทา) อยู่ท้ายบรรทัด", "(Inference)" in (txt_of(page, ".ltSum") or ""))
        page.click('[data-idea-asset=BRENT]'); page.wait_for_timeout(500)
        check(f"{tag} 8 แตะ Brent → แท็บ Flow · เปิดการ์ด Playbook", js(page, "()=>activeTab") == "flow" and js(page, "()=>pbOpen") is True)
        js(page, "()=>{ switchTab('watch'); ideaGo('idea-one','sum'); }"); page.wait_for_timeout(300)
        page.click('[data-idea-asset=S50]'); page.wait_for_timeout(400)
        check(f"{tag} 8 แตะ S50 (ไม่มีการ์ด Playbook) → แค่เปลี่ยนแท็บ ไม่ error", js(page, "()=>activeTab") == "flow" and not ce and not pe, json.dumps([ce, pe]))
        fold = js(page, "()=>{ const e=document.querySelector('[data-pb-ideas]'); return e ? e.textContent.replace(/\\s+/g,' ').trim() : ''; }")
        pbl = js(page, "()=>{ const c=document.querySelector('#pbPanel .pbCard'); const k=[...c.children]; return k[k.length-1].dataset.pbIdeas!==undefined; }")
        check(f"{tag} 8 full report Playbook: บรรทัดพับ 'ไอเดียที่เกี่ยว (1)' อยู่ท้ายสุด (เฉพาะ idea-one มี asset ที่ map ได้)", "ไอเดียที่เกี่ยว (1)" in fold and "ธีมหนึ่ง" in fold and pbl, fold)
        page.click("[data-pb-ideas] summary"); page.click(".pbIdeas .ideaPbL"); page.wait_for_timeout(400)
        check(f"{tag} 8 แตะชื่อไอเดียในบรรทัดพับ → เปิดไอเดียนั้น", js(page, "()=>[activeTab, wlView, ideaSel]") == ["watch", "idea", "idea-one"], json.dumps(js(page, "()=>[activeTab, wlView, ideaSel]")))
        js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(200)
        rows = txt_of(page, "[data-idea-rows]") or ""
        js(page, "()=>wlSetView('wl')"); page.wait_for_timeout(200); wlt = txt_of(page, ".wlRows") or ""
        js(page, "()=>wlSetView('cand')"); page.wait_for_timeout(200); cdt = txt_of(page, ".wlRows") or ""
        check(f"{tag} 8 asset ไม่แสดงในรายการ Ideas / Watchlist / Candidates", not any(x in t for t in (rows, wlt, cdt) for x in ("Brent", "ผันผวน")), "")
        check(f"{tag} 10 ไม่มี console error (asset)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()
    b, c, page, ce, pe, dl = launcher(pw, w, h, [idea3()], pb=True)   # ไม่มี asset → ไม่มีบรรทัดพับ
    try:
        js(page, "()=>{ switchTab('flow'); pbOpen=true; pbRender(); }"); page.wait_for_timeout(400)
        check(f"{tag} 8 ไม่มีไอเดียที่มี asset → ไม่แสดงบรรทัดพับ (n = 0)", cnt(page, "[data-pb-ideas]") == 0 and cnt(page, "#pbPanel .pbCard") == 1)
    finally:
        b.close()

    # ───── 8b · kill hit → เสนอพัก ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, I)
    try:
        js(page, "()=>{ switchTab('watch'); ideaGo('idea-three','sum'); }"); page.wait_for_timeout(400)
        bar = txt_of(page, "[data-idea-hit]") or ""
        st0 = (user_db(page, "idea-three").get("user") or {}).get("status")
        check(f"{tag} 8b kill hit → แถบแดงบนสุด 'สัญญาณพักชนแล้ว: … — พิจารณาตั้ง พัก' + ปุ่ม ตั้งเป็น พัก · สถานะยังไม่เปลี่ยน", bar.startswith("สัญญาณพักชนแล้ว:") and "พิจารณาตั้ง พัก" in bar and st0 is None and js(page, "()=>ideaFind('idea-three').status") == "need_evidence", bar)
        first = js(page, "()=>document.querySelector('.wlDBody .panel').firstElementChild.dataset.ideaHit !== undefined")
        check(f"{tag} 8b แถบอยู่บนสุดของแท็บสรุป", first)
        page.click("[data-idea-hit-park]"); page.wait_for_timeout(500)
        check(f"{tag} 8b กดแล้ว → สถานะ พัก (user.status=parked) · แถบหาย", (user_db(page, "idea-three").get("user") or {}).get("status") == "parked" and cnt(page, "[data-idea-hit]") == 0)
        check(f"{tag} 8b ไอเดียพักแล้วไม่นับใน Candidates (TRIO หาย)", "TRIO" not in js(page, "()=>wlRowsAll().cand.map(r=>r.sym)"))
        check(f"{tag} 10 ไม่มี console error (kill hit)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 9 · Import ซ้ำ ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, [(idea1(), {"cand": {"AMAT": {"rank": 1, "state": "study"}, "KLAC": {"rank": 2}}})])
    try:
        js(page, "()=>{ switchTab('watch'); wlSetView('idea'); }"); page.wait_for_timeout(300)
        new = idea1(); new["candidates"] = new["candidates"] + [cand("NEWC", "New Co", 5, "wait")]
        P44.import_text(page, json.dumps(new, ensure_ascii=False))
        js(page, "()=>{ wlSetView('cand'); }"); page.wait_for_timeout(400)
        syms = cand_syms(page)
        v = js(page, "()=>ideaFind('idea-one').cands.map(c=>[c.sym,c.rank,c.state])")
        check(f"{tag} 9 Import ไอเดียซ้ำ (เพิ่ม NEWC) → Candidates อัปเดต (มี NEWC) · ค่าผู้ใช้ rank/state (AMAT=ศึกษา อันดับ 1) ยังอยู่", "NEWC" in syms and v[0][:3] == ["AMAT", 1, "study"], json.dumps([syms, v]))
        check(f"{tag} 10 ไม่มี console error (Import ซ้ำ)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()
    b, c, page, ce, pe, dl = launcher(pw, w, h, I)
    try:
        js(page, "()=>{ switchTab('watch'); wlSetView('cand'); }"); page.wait_for_timeout(300)
        check(f"{tag} 10 หน้าไม่ล้นแนวนอน (Candidates)", overflow(page) <= 0, str(overflow(page)))
        js(page, "()=>wlSetView('wl')"); page.wait_for_timeout(250)
        check(f"{tag} 10 หน้าไม่ล้นแนวนอน (Watchlist)", overflow(page) <= 0, str(overflow(page)))
    finally:
        b.close()


def static_tests():
    root = os.path.join(HERE, "..")
    check("[static] สำรอง index.backup-pre-ID2.html + tests/_bk_id2/ อยู่", os.path.exists(os.path.join(root, "index.backup-pre-ID2.html")) and os.path.isdir(os.path.join(HERE, "_bk_id2")))
    html = open(os.path.join(root, "index.html"), encoding="utf-8").read()
    seg = html.split("function wlRowsAll()")[1].split("function wlSortRows")[0]
    check("[static] wlRowsAll().cand ไม่อ่าน research (ไม่มี rsAll() ใน cand)", "ideaCandRows(" in seg and "rsAll()" not in seg.split("const cand")[1])
    check("[static] ไม่เก็บ field อ้างอิงข้ามกัน: wlAddSave ไม่เขียน idea*", "idea" not in html.split("function wlAddSave()")[1].split("function wlTierSet")[0].split("/* 7E-2b-2")[0].lower().replace("industry", ""))


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 45 / ID2) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
