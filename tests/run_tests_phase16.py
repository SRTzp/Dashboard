#!/usr/bin/env python3
"""7F — Journal: (A) บล็อกสรุปเข้ม #jSum · (B) ชิปบัญชี/พอร์ต + ปุ่มในแถวส่ง account = jAcct · (C) สถิติตาม Setup · (E) เงื่อนไขที่ยกเลิก
เทียบตัวเลขบล็อก A + การ์ดพอร์ตกับ index.backup-pre-7F.html (ชุดข้อมูลเดียวกัน · ต่อบัญชี)
ภาพเก็บที่ tests/screenshots/7f-*.png · รัน: python3 run_tests_phase16.py (mock Firestore + fundflow stub)
"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase13 as p13

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-7F.html"))
ENGINE = base.BROWSER_ENGINE
results = []
DIALOGS = []
SETUP_SEEN = []


def retired(name, reason):
    """CL2-b — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่พิมพ์ไว้ให้ตามรอยได้ (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:1500] + "...(truncated)") if (detail and len(detail) > 1500) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def T(*a, **k): return p13.T(*a, **k)


def C(id, port="core", win=True, **kw):
    """ไม้ปิด: win → exit 110 (กำไร) / lose → exit 90"""
    d = dict(exitPrice=110 if win else 90, exitDate=kw.pop("exitDate", "2026-09-20"))
    d.update(kw); return T(id, port, "closed", **d)


def fresh(pw, w, h, path=None):
    browser, context, page, ce, pe = p13.fresh(pw, w, h, path)
    page.on("dialog", lambda d: (DIALOGS.append(d.message), d.accept()))
    return browser, context, page, ce, pe


def retired(name, reason):
    """CL2-a — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่ต้องพิมพ์ไว้ให้ตามรอยได้ (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)


def shot(page, name, sel=None): return p13.shot(page, name, sel)


def seed(page, main, fam, ports=None):
    page.evaluate("""([m,f,ports])=>{ getBook('main').trades = m||[]; getBook('fam').trades = f||[];
        acctList.forEach(a=>{ a.ports = (ports && ports[a.id]) || ['core','satB']; });
        acctList.forEach(a=>{ const b=getBook(a.id); if(b.journalView) b.journalView={}; });
        jAcct = null; jFilter = 'all'; switchTab('journal'); render(); }""", [main, fam, ports])
    page.wait_for_timeout(150)


def seed_old(page, main, fam, ports=None):
    page.evaluate("""([m,f,ports])=>{ getBook('main').trades = m||[]; getBook('fam').trades = f||[];
        acctList.forEach(a=>{ a.ports = (ports && ports[a.id]) || ['core','satB']; });
        acctList.forEach(a=>{ const b=getBook(a.id); if(b.journalView) b.journalView={}; });
        jFilter = 'all'; switchTab('journal'); render(); }""", [main, fam, ports])
    page.wait_for_timeout(150)


def norm(t): return " ".join((t or "").split())


# ─────────────── ชุดข้อมูล ───────────────
MAIN = [
    C("m1", "core", True, sym="AAA", setup="acc", discScore=3, setupScore=2, date="2026-09-01"),
    C("m2", "core", True, sym="BBB", setup="acc", discScore=1, setupScore=1, date="2026-09-02", exitDate="2026-09-22"),   # โชค: กำไรแต่วินัย ≤1
    C("m3", "core", False, sym="CCC", setup="pp", discScore=3, exitDate="2026-09-23"),
    C("m4", "core", True, sym="DDD", unplanned=True, exitDate="2026-09-24"),                                          # นอกแผน · ไม่ระบุ setup
    C("m5", "core", True, sym="SAA", setup="pp", exitDate="2026-09-25"),   # CL2-a: ไม้ satA เดิมเปลี่ยนเป็น core
    C("m6", "satB", True, sym="XAUUSD", qty=0.1, mult=100, setups=["s1", "s2"], exitDate="2026-09-26"),
    C("m7", "satB", False, sym="XAUUSD", qty=0.1, mult=100, setups=["s1"], exitDate="2026-09-27"),
    C("m8", "satB", True, sym="XAUUSD", qty=0.1, mult=100, setups=["zzz-unknown"], exitDate="2026-09-27"),
    T("mm1", "core", "missed", sym="MISS", missedDate="2026-09-20", missedReason="x"),
    T("mc1", "core", "cancelled", sym="CANC", cancelDate="2026-09-21", cancelNote="y"),
    T("mo1", "core", "open", sym="OPENX"),
]
FAM = [
    C("f1", "satB", True, sym="XAUUSD", qty=0.05, mult=100, setups=["s2"], exitDate="2026-09-10"),
    C("f2", "satB", False, sym="XAUUSD", qty=0.05, mult=100, setups=[], exitDate="2026-09-11"),
    T("fm1", "satB", "missed", sym="FMISS", missedDate="2026-09-12", missedReason="fm"),
    T("fc1", "satB", "cancelled", sym="FCANC", cancelDate="2026-09-13", cancelNote="fc"),
]
FAM_PORTS = {"fam": ["satB"]}
SETUPS = {"XAUUSD": [{"id": "s1", "name": "Sweep"}, {"id": "s2", "name": "BigBar"}]}


def cells(page):
    return page.evaluate("""() => { const o={}; document.querySelectorAll('#jSum .sumCell').forEach(c=>{
        o[c.dataset.sum] = {big:c.querySelector('.sumBig').innerText.replace(/\\s+/g,' ').trim(),
          sub:(c.querySelector('.sumSub')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim(),
          pill:(c.querySelector('.sumPill:not(.ph)')||{className:''}).className}; }); return o; }""")


def decision(page):
    return page.evaluate("() => { const e=document.querySelector('#jSum [data-jsum=decision]'); return e ? {k:e.dataset.k, t:e.innerText.trim(), warn:!!e.querySelector('.sumM.warn')} : null; }")


def old_vals(page, acct):
    """หน้าเก่า: แถบสถิติ + การ์ดพอร์ต ของบัญชีนั้น (renderJournal ในบริบท withAccount)"""
    return page.evaluate("""(id)=>withAccount(id, ()=>{ renderJournal();
        const v=[...document.querySelectorAll('#jStrip .stat .val')].map(e=>e.innerText.replace(/\\s+/g,' ').trim());
        const keys=portsOn().map(x=>x[0]);
        const ports=[...document.querySelectorAll('#jPorts .port .nums')].map((e,i)=>({k:keys[i], t:e.innerText.replace(/\\s+/g,' ').trim()}));
        return {v, ports}; })""", acct)


def new_ports(page):
    return page.evaluate("() => [...document.querySelectorAll('#jPorts .port')].map(e=>({k:e.dataset.port, t:e.querySelector('.nums').innerText.replace(/\\s+/g,' ').trim(), name:e.querySelector('.pname').innerText.trim()}))")


def view(page, acct):
    page.evaluate("(id)=>setJAcct(id)", acct); page.wait_for_timeout(120)


def table_syms(page):
    return page.evaluate("() => [...document.querySelectorAll('#jTbody tr')].map(r=>(r.children[2]||{innerText:''}).innerText.trim()).filter(Boolean)")


def dump(page): return json.dumps(page.evaluate("() => window.firebase.__mockDb.__dump()"), sort_keys=True)


def trades(page, id):
    return page.evaluate("(id)=>getBook(id).trades.map(t=>t.id+':'+t.status)", id)


# ───────────────────────── A) ตัวเลขเท่าเดิม ─────────────────────────
def numbers_tests(pw, w, h, tag):
    browser, context, old, ce, pe = fresh(pw, w, h, BACKUP)
    try:
        seed_old(old, MAIN, FAM, FAM_PORTS)
        ov = {a: old_vals(old, a) for a in ("main", "fam")}
    finally:
        browser.close()
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        seed(page, MAIN, FAM, FAM_PORTS)
        for a in ("main", "fam"):
            view(page, a)
            c = cells(page); o = ov[a]["v"]
            got = [c["n"]["big"], c["win"]["big"], c["avgr"]["big"], c["pnl"]["big"], c["dd"]["big"] + " " + c["dd"]["sub"], c["disc"]["big"] + "|" + c["disc"]["sub"]]
            # เก่า: [n, win, avgR, pnl, "dd% ฿dd", "disc / 3 [setup x] [inval]"]
            ok = (got[0] == o[0] and got[1] == o[1] and got[2] == o[2] and got[3] == o[3] and got[4] == o[4]
                  and got[5].split("|")[0].replace(" ", "") == o[5].split("setup")[0].split("·")[0].replace(" ", ""))
            check(f"{tag} A บัญชี {a}: ตัวเลขบล็อก (ไม้ปิด/Win/AvgR/P&L/DD/วินัย) = ค่าเดิมของแถบเก่า", ok, json.dumps({"new": got, "old": o}, ensure_ascii=False))
            np_, op = new_ports(page), ov[a]["ports"]
            same = all(any(n["k"] == x["k"] and n["t"] == x["t"] for n in np_) for x in op if x["k"] != "satA" or any(n["k"] == "satA" for n in np_))
            check(f"{tag} A บัญชี {a}: การ์ดต่อพอร์ตตัวเลข = เดิมทุกพอร์ตที่แสดง", same and len(np_) >= 1, json.dumps({"new": np_, "old": op}, ensure_ascii=False))
        # เทียบกับ journalStats ตรง ๆ + ไม้ missed/cancel/open ไม่เข้า
        for a in ("main", "fam"):
            js = page.evaluate("(id)=>withAccount(id, ()=>{ const s=journalStats().overall; return {n:s.n}; })", a)
            n_closed = sum(1 for t in (MAIN if a == "main" else FAM) if t["status"] == "closed")
            view(page, a)
            check(f"{tag} A {a}: ไม้ปิด = journalStats = {n_closed} (missed/cancelled/open ไม่เข้าสถิติ)", js["n"] == n_closed and cells(page)["n"]["big"] == str(n_closed), json.dumps(js))
        # หัวบล็อก
        view(page, "fam")
        head = page.evaluate("() => ({t:document.querySelector('#jSum .sumT').innerText, r:document.querySelector('#jSum .sumR').innerText})")
        check(f"{tag} A หัว: 'Journal · <ชื่อบัญชี>' + ช่วงเวลา 'ทั้งหมด'", head["t"].startswith("Journal · ") and head["t"] != "Journal · " and head["r"] == "ทั้งหมด", json.dumps(head, ensure_ascii=False))
        # ช่วงเวลา → ก.ย. 2026 (ตั้งผ่าน UI ของพาเนล Closed)
        page.evaluate("() => { jvSetYear('closed','2026'); jvSetMonth('closed','09'); }"); page.wait_for_timeout(120)
        r = page.evaluate("() => document.querySelector('#jSum .sumR').innerText")
        check(f"{tag} A หัวขวา = ช่วงเวลาพาเนล Closed ('ก.ย. 2026') · เก็บลง book ของ fam ไม่ใช่ main", r == "ก.ย. 2026" and page.evaluate("() => getBook('fam').journalView.closed.y") == "2026" and page.evaluate("() => (getBook('main').journalView.closed||{}).y") in ("all", None), r)
        page.evaluate("() => jvSetYear('closed','all')")
        # pill โทนอ่อน · ไม่ใช้ mono
        pills = cells(page)
        check(f"{tag} A pill: fam Win 50% = เขียว (เกณฑ์ ≥ 50%)", "up" in pills["win"]["pill"], json.dumps(pills, ensure_ascii=False))
        check(f"{tag} A pill: P&L = 0 และ Avg R = 0 → ไม่มี pill", pills["pnl"]["pill"] == "" and pills["avgr"]["pill"] == "", json.dumps(pills, ensure_ascii=False))
        view(page, "main"); pm = cells(page)
        check(f"{tag} A pill: main P&L > 0 / Avg R > 0 = เขียว (.up)", "up" in pm["pnl"]["pill"] and "up" in pm["avgr"]["pill"], json.dumps(pm, ensure_ascii=False))
        seed(page, [C("n1", "core", False, sym="N1"), C("n2", "core", False, sym="N2")], [], FAM_PORTS); pn = cells(page)
        check(f"{tag} A pill: P&L < 0 / Avg R < 0 = แดง (.dn)", "dn" in pn["pnl"]["pill"] and "dn" in pn["avgr"]["pill"], json.dumps(pn, ensure_ascii=False))
        seed(page, MAIN, FAM, FAM_PORTS); view(page, "fam")
        mono = page.evaluate("() => [...document.querySelectorAll('#jSum *')].some(e=>/mono|monospace/i.test(getComputedStyle(e).fontFamily))")
        check(f"{tag} A บล็อกไม่ใช้ฟอนต์ mono", not mono)
        check(f"{tag} A #jStrip เดิมถูกแทนที่ (ไม่มีอยู่แล้ว) · ไม่มีตัวเลขรวมข้ามบัญชี", page.evaluate("() => !document.getElementById('jStrip') && document.querySelectorAll('#jSum').length===1"))
        # ว่าง
        seed(page, [], [], FAM_PORTS)
        c = cells(page)
        check(f"{tag} A ไม่มีไม้ปิด → '—' ทุกช่องที่ไม่มีข้อมูล · ไม้ปิด 0", c["n"]["big"] == "0" and c["win"]["big"] == "—" and c["avgr"]["big"] == "—" and c["pnl"]["big"] == "—" and c["dd"]["big"] == "—" and c["disc"]["big"] == "—", json.dumps(c, ensure_ascii=False))
        check(f"{tag} console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── บรรทัดตัดสินใจ 4 กรณี ─────────────────────────
def decision_tests(page, tag):
    seed(page, [], [], FAM_PORTS)
    d = decision(page)
    check(f"{tag} บรรทัด 1: ไม่มีไม้ปิด → 'ยังไม่มีไม้ปิดในช่วงนี้'", d and d["k"] == "empty" and d["t"] == "ยังไม่มีไม้ปิดในช่วงนี้" and not d["warn"], json.dumps(d, ensure_ascii=False))
    seed(page, [C("a", "core", True, sym="A", discScore=3), C("b", "core", True, sym="B", unplanned=True, discScore=0), C("c", "core", True, sym="C", discScore=0)], [], FAM_PORTS)
    d = decision(page)
    check(f"{tag} บรรทัด 2: มีไม้นอกแผน (ชนะเหนือ lucky) → 'ไม้นอกแผน 1 ไม้ · P&L ฿… — ดูชิป นอกแผน' (warn)", d and d["k"] == "offplan" and re.match(r"ไม้นอกแผน 1 ไม้ · P&L ฿[\d,\-]+ — ดูชิป นอกแผน$", d["t"]) and d["warn"], json.dumps(d, ensure_ascii=False))
    seed(page, [C("a", "core", True, sym="A", discScore=3), C("c", "core", True, sym="C", discScore=1), C("d", "core", True, sym="D", discScore=0)], [], FAM_PORTS)
    d = decision(page)
    check(f"{tag} บรรทัด 3: luckyWins>0 → 'ชนะแบบไม่ตามแผน 2 ไม้ — อย่านับเป็นฝีมือ' (warn)", d and d["k"] == "lucky" and d["t"] == "ชนะแบบไม่ตามแผน 2 ไม้ — อย่านับเป็นฝีมือ" and d["warn"], json.dumps(d, ensure_ascii=False))
    seed(page, [C("a", "core", True, sym="A", discScore=3), C("c", "core", False, sym="C", discScore=3)], [], FAM_PORTS)
    d = decision(page)
    check(f"{tag} บรรทัด 4: อื่น ๆ → 'ทุกไม้ในช่วงนี้ตามแผน'", d and d["k"] == "ok" and d["t"] == "ทุกไม้ในช่วงนี้ตามแผน" and not d["warn"], json.dumps(d, ensure_ascii=False))


# ───────────────────────── B) ชิปบัญชี / ชิปพอร์ต / ปุ่มส่ง account ─────────────────────────
def chip_tests(page, tag, w):
    page.evaluate("(s)=>{ satConfigSetups = s; }", SETUPS)
    seed(page, MAIN, FAM, FAM_PORTS)
    st0 = {"active": page.evaluate("() => acctActive"), "db": dump(page)}
    chips = page.evaluate("() => [...document.querySelectorAll('#jAcctRow .chip')].map(e=>({id:e.dataset.acct, on:e.classList.contains('on')}))")
    check(f"{tag} B แถวชิปบัญชี: 1 ชิปต่อบัญชี · ค่าเริ่มต้น = acctActive", len(chips) == 2 and [c["id"] for c in chips if c["on"]] == [st0["active"]], json.dumps(chips))
    # เปิดแท็บใหม่ทุกครั้ง = acctActive
    page.evaluate("() => { setJAcct('fam'); switchTab('plan'); switchTab('journal'); }")
    check(f"{tag} B เปิดแท็บ Journal ใหม่ → กลับเป็น acctActive", page.evaluate("() => jAcct") == st0["active"])
    # สลับไป fam
    page.click("#jAcctRow .chip[data-acct=fam]"); page.wait_for_timeout(150)
    syms = table_syms(page)
    names = page.evaluate("() => [document.querySelector('#jSum .sumT').innerText, [...document.querySelectorAll('#jPorts .pname')].map(e=>e.innerText)]")
    fam_syms = {"XAUUSD"}
    check(f"{tag} B สลับไป fam: บล็อก/ตาราง/พอร์ตเป็นของ fam (ตาราง {syms} · ไม้ปิด {cells(page)['n']['big']} · พอร์ต {names[1]})",
          set(syms) == fam_syms and len(syms) == 2 and cells(page)["n"]["big"] == "2" and names[1] == ["Sat"] and "ครอบครัว" in names[0] or (len(names[1]) == 1 and cells(page)["n"]["big"] == "2" and len(syms) == 2), json.dumps(names, ensure_ascii=False))
    check(f"{tag} B สลับบัญชีในแท็บ: acctActive ไม่เปลี่ยน · state/ฐานข้อมูลไม่ถูกเขียน · dirtyBooks ว่าง",
          page.evaluate("() => acctActive") == st0["active"] and dump(page) == st0["db"] and page.evaluate("() => dirtyBooks.size") == 0)
    # ชิปพอร์ต
    pf = lambda: page.evaluate("() => [...document.querySelectorAll('#jFilters .chip')].map(e=>e.dataset.jf)")
    check(f"{tag} B fam (ports=satB): ไม่มีชิป Core · ไม่มีชิปเก็บถาวร · มี Sat", "core" not in pf() and "satA" not in pf() and "satB" in pf(), json.dumps(pf()))
    view(page, "main")
    retired(f"{tag} B main มี satA → ชิป 'เก็บถาวร' ขึ้น (ค่า filter satA) + Core + Sat", "CL2-a ลบ Sat.A — ไม่มีชิป/การ์ด 'เก็บถาวร' ใน Journal แล้ว")
    retired(f"{tag} B การ์ดพอร์ต satA ชื่อ 'เก็บถาวร (Sat.A เดิม)'", "CL2-a ลบ Sat.A — ไม่มีการ์ดพอร์ต satA ใน Journal แล้ว")
    page.click("#jFilters .chip[data-jf=core]"); page.wait_for_timeout(100)   # CL2-a: เดิมกดชิป 'เก็บถาวร' (satA) → ใช้ชิป Core แทนสำหรับเคสถัดไป
    retired(f"{tag} B กรอง เก็บถาวร → ตารางเหลือไม้ satA", "CL2-a ลบ Sat.A — ไม่มีชิป 'เก็บถาวร'")
    view(page, "fam")
    check(f"{tag} B ชิปที่เลือกไม่มีในบัญชีใหม่ (core→fam) → กลับ 'ทั้งหมด'", page.evaluate("() => jFilter") == "all" and "on" in page.evaluate("() => document.querySelector('#jFilters .chip[data-jf=all]').className"))
    # main ไม่มี satA → ไม่มีชิป
    seed(page, [t for t in MAIN if t["port"] != "satA"], FAM, FAM_PORTS)
    check(f"{tag} B main ไม่มีไม้ satA → ไม่มีชิป 'เก็บถาวร' และไม่มีการ์ด satA", "satA" not in pf() and all(p["k"] != "satA" for p in new_ports(page)), json.dumps(pf()))
    # ปุ่มทุกปุ่มส่ง account
    seed(page, MAIN, FAM, FAM_PORTS); view(page, "fam")
    btns = page.evaluate("""() => [...document.querySelectorAll('#jTbody button, #jCards button, #cancelTbody button, #cancelCards button')].map(b=>b.getAttribute('onclick'))""")
    check(f"{tag} B ปุ่มในแถวทุกปุ่ม (closed/cancel · ตาราง+การ์ด · {len(btns)} ปุ่ม) ส่ง account 'fam' เป็นอาร์กิวเมนต์สุดท้าย", len(btns) >= 12 and all(re.search(r",'fam'\)$", b or "") for b in btns), json.dumps(btns))
    m0 = trades(page, "main")
    vis = lambda sel: page.evaluate("(s)=>[...document.querySelectorAll(s)].find(e=>e.offsetParent!==null)?.tagName||null", sel)
    # ลบ (ปุ่มที่มองเห็นได้) → เฉพาะ fam
    root = "#jTbody" if w >= 700 else "#jCards"
    page.evaluate("(r)=>[...document.querySelectorAll(r+' button.danger')].find(e=>e.offsetParent!==null).click()", root); page.wait_for_timeout(150)
    f1 = trades(page, "fam")
    check(f"{tag} B ★ ดู fam แล้วกดลบ → ลบเฉพาะไม้ fam ({len(trades(page,'fam'))} เหลือ) · main ไม่เปลี่ยน", len(f1) == 3 and trades(page, "main") == m0 and page.evaluate("() => acctActive") == st0["active"], json.dumps([f1, trades(page, "main")]))
    # แก้ไข
    page.evaluate("(r)=>{ const b=[...document.querySelectorAll(r+' button:not(.danger)')].find(e=>e.offsetParent!==null); b.click(); }", root); page.wait_for_timeout(120)
    fe = page.evaluate("() => ({fa:teCtx && teCtx.acct, head:document.getElementById('teHead').innerText, show:document.getElementById('teOverlay').classList.contains('show')})")
    check(f"{tag} B ★ ดู fam แล้วกดแก้ไข → หน้าต่างแก้ไม้เป็นของ fam (CL2-c: openTradeEdit · หัวแสดงบัญชี Family)", fe["fa"] == "fam" and "Family" in fe["head"] and fe["show"], json.dumps(fe, ensure_ascii=False))
    page.evaluate("() => closeTradeEdit()")
    # Missed แก้ไข — CL2-b เลิกใช้
    retired(f"{tag} B ★ ดู fam กดแก้ Missed → โมดัลเป็นของ fam (ไม้ FMISS)", "CL2-b ลบ Missed ทั้งระบบ (ไม่มีพาเนล/โมดัล Missed ใน Journal)")
    # Cancel แก้ไข
    croot = "#cancelTbody" if w >= 700 else "#cancelCards"
    page.evaluate("(r)=>[...document.querySelectorAll(r+' button')].find(e=>e.offsetParent!==null && /openCancelModal/.test(e.getAttribute('onclick'))).click()", croot); page.wait_for_timeout(100)
    check(f"{tag} B ★ ดู fam กดแก้ Cancel → โมดัลเป็นของ fam (ไม้ FCANC)", page.evaluate("() => cancelAcct") == "fam" and "FCANC" in page.evaluate("() => document.getElementById('cancelSymHint').textContent"))
    page.evaluate("() => document.getElementById('cancelOverlay').classList.remove('show')")
    # Restore (Cancel · CL2-b ไม่มี Missed แล้ว) → เฉพาะ fam
    for fn, r in (("restoreCancelled", croot),):
        page.evaluate("([r,fn])=>[...document.querySelectorAll(r+' button')].find(e=>e.offsetParent!==null && e.getAttribute('onclick').indexOf(fn)===0).click()", [r, fn]); page.wait_for_timeout(120)
    fs = trades(page, "fam")
    check(f"{tag} B ★ ดู fam กด Restore Cancel → fam: FCANC กลับ plan · FMISS (missed เก่า) ไม่ถูกแตะ · main ไม่เปลี่ยน", "fm1:missed" in fs and "fc1:plan" in fs and trades(page, "main") == m0, json.dumps([fs, trades(page, "main")]))
    # ＋ Closed นอกแผน จากแท็บ Journal → บัญชีที่ดูอยู่ — CL2-c ลบปุ่ม/ฟอร์มนี้ (7E-2 จะเปิดใหม่ที่การ์ด Core)
    retired(f"{tag} B ดู fam กด ＋ Closed นอกแผน → ฟอร์มเป็นของ fam", "CL2-c ลบฟอร์ม Add Trade + ปุ่ม ＋ Closed นอกแผน (openUnplannedClosed/tAcct/formAcct)")
    retired(f"{tag} B บันทึกแล้วไม้ไปอยู่ใน fam (closed นอกแผน) · main ไม่เปลี่ยน", "CL2-c ลบฟอร์ม Add Trade + ปุ่ม ＋ Closed นอกแผน (saveTrade) — การสร้างไม้ใหม่ผ่านฟอร์มเลิกใช้")
    # main view ลบ → เฉพาะ main
    view(page, "main")
    fam0 = trades(page, "fam")
    page.evaluate("(r)=>[...document.querySelectorAll(r+' button.danger')].find(e=>e.offsetParent!==null).click()", root); page.wait_for_timeout(120)
    check(f"{tag} B ดู main แล้วลบ → เฉพาะ main · fam ไม่เปลี่ยน", len(trades(page, "main")) == len(m0) - 1 and trades(page, "fam") == fam0)


# ───────────────────────── C) Setup ─────────────────────────
def setup_tests(page, tag):
    page.evaluate("(s)=>{ satConfigSetups = s; }", SETUPS)
    seed(page, MAIN, FAM, FAM_PORTS); view(page, "main")
    rows = lambda: page.evaluate("() => [...document.querySelectorAll('#setupBody .jSetupRow[data-setup]')].map(r=>({k:r.dataset.setup, few:r.classList.contains('few'), c:[...r.children].map(x=>x.innerText.replace(/\\s+/g,' ').trim())}))")
    r = {x["k"]: x for x in rows()}
    vis = page.evaluate("() => [...document.querySelectorAll('#setupBody .jSetupRow[data-setup]')].map(e=>{const b=e.getBoundingClientRect(); return e.offsetParent!==null && b.width>0 && b.height>0;})")
    check(f"{tag} C แถว Setup ทุกกลุ่มมองเห็นได้จริง ({len(vis)} แถว · ขนาด > 0)", len(vis) == 6 and all(vis), json.dumps(vis))
    SETUP_SEEN.append(json.dumps(sorted((k, v["c"]) for k, v in r.items()), ensure_ascii=False))
    if len(SETUP_SEEN) == 2:
        check(f"{tag} C ตัวเลขตาราง Setup ตรงกันทั้ง 1440 และ 430", SETUP_SEEN[0] == SETUP_SEEN[1], "\n".join(SETUP_SEEN))
    ff = page.evaluate("() => getComputedStyle(document.querySelector('#setupBody .jSetupRow[data-setup]')).fontFamily")
    check(f"{tag} C ตัวเลข Setup ฟอนต์ปกติ (ไม่ mono)", "mono" not in ff.lower(), ff)
    # main: core acc = m1,m2 (2) · pp = m3 (+ satA m5 'PP') = 2 · ไม่ระบุ = m4 (core no setup) · Sweep = m6,m7 · BigBar = m6 · zzz-unknown = m8
    want = {"Acc/Dist": 2, "PP": 2, "ไม่ระบุ": 1, "Sweep": 2, "BigBar": 1, "zzz-unknown": 1}
    got = {k: int(v["c"][1]) for k, v in r.items()}
    check(f"{tag} C นับกลุ่มถูก: acc/pp/ไม่ระบุ/setups หลายตัว (นับซ้ำ)/id ไม่มีชื่อแสดง id", got == want, json.dumps(got, ensure_ascii=False))
    ns = [int(x["c"][1]) for x in rows()]
    check(f"{tag} C เรียงตามจำนวนไม้มาก→น้อย", ns == sorted(ns, reverse=True), json.dumps(ns))
    check(f"{tag} C ทุกกลุ่ม < 5 ไม้ = จาง + '(น้อย)'", all(x["few"] and "(น้อย)" in x["c"][0] for x in rows()))
    # Sweep: m6 win, m7 lose → 50%
    check(f"{tag} C คอลัมน์ Win% / Avg R / P&L ถูก (Sweep: ชนะ 1 แพ้ 1 ขนาดเท่ากัน → 50% · 0R · ฿0)", r["Sweep"]["c"][2:] == ["50%", "0R", "฿0"], json.dumps(r["Sweep"], ensure_ascii=False))
    check(f"{tag} C หมายเหตุใต้ตาราง: 'ไม้ที่มีหลาย setup นับซ้ำในแต่ละกลุ่ม'", "ไม้ที่มีหลาย setup นับซ้ำในแต่ละกลุ่ม" in page.evaluate("() => document.getElementById('setupBody').innerText"))
    # ≥5 ไม้ = ไม่จาง
    many = [C(f"x{i}", "core", i % 2 == 0, sym=f"X{i}", setup="acc") for i in range(6)]
    seed(page, many, FAM, FAM_PORTS); view(page, "main")
    x = {k["k"]: k for k in rows()}
    check(f"{tag} C กลุ่ม ≥ 5 ไม้ ไม่จาง ไม่มี '(น้อย)'", not x["Acc/Dist"]["few"] and "(น้อย)" not in x["Acc/Dist"]["c"][0], json.dumps(x, ensure_ascii=False))
    # ชิปพอร์ต → กรองชุดเดียวกับตาราง
    seed(page, MAIN, FAM, FAM_PORTS); view(page, "main")
    page.click("#jFilters .chip[data-jf=satB]"); page.wait_for_timeout(100)
    ks = {k["k"] for k in rows()}
    check(f"{tag} C ชิปพอร์ต Sat → พาเนลนับเฉพาะไม้ satB (ไม่มี Acc/Dist/PP)", ks == {"Sweep", "BigBar", "zzz-unknown"}, json.dumps(sorted(ks), ensure_ascii=False))
    page.click("#jFilters .chip[data-jf=all]")
    # บัญชี fam: fam1 setups [s2] → BigBar 1 · f2 setups [] → ไม่ระบุ
    view(page, "fam")
    check(f"{tag} C บัญชี fam: BigBar 1 · ไม่ระบุ 1", {k["k"]: k["c"][1] for k in rows()} == {"BigBar": "1", "ไม่ระบุ": "1"}, json.dumps(rows(), ensure_ascii=False))
    # ว่าง
    seed(page, [], [], FAM_PORTS)
    check(f"{tag} C ไม่มีไม้ → 'ยังไม่มีไม้ปิดในช่วงนี้'", page.evaluate("() => document.getElementById('setupBody').innerText.trim()") == "ยังไม่มีไม้ปิดในช่วงนี้")
    # ช่วงเวลาคุม
    seed(page, [C("p1", "core", True, sym="P1", setup="acc", exitDate="2026-08-05"), C("p2", "core", True, sym="P2", setup="pp", exitDate="2026-09-05")], [], FAM_PORTS)
    page.evaluate("() => { jvSetYear('closed','2026'); jvSetMonth('closed','09'); }"); page.wait_for_timeout(100)
    check(f"{tag} C ช่วงเวลาพาเนล Closed (ก.ย.) คุมพาเนล Setup ด้วย", {k["k"] for k in rows()} == {"PP"}, json.dumps(rows(), ensure_ascii=False))
    page.evaluate("() => jvSetYear('closed','all')")


# ───────────────────────── E) เงื่อนไขที่ยกเลิก ─────────────────────────
def cond_tests(page, tag, w):
    seed(page, MAIN, FAM, FAM_PORTS)
    check(f"{tag} E ยังไม่มี idea → 'ยังไม่มีเงื่อนไขที่ยกเลิก'", "ยังไม่มีเงื่อนไขที่ยกเลิก" in page.evaluate("() => document.getElementById('condBody').innerText"))
    ideas = {
        "i1": {"v3": True, "asset": "XAUUSD", "bias": "Long", "week": "2026-09-27", "status": "active", "planned": True,
               "conditions": [{"id": "c1", "text": "ปิดเหนือ 4300", "active": True, "saved": True},
                              {"id": "c2", "text": "หลุด 4200 ยกเลิก", "status": "cancelled", "cancelled_at": "2026-09-25T03:00:00.000Z"}]},
        "i2": {"v3": True, "asset": "BTCUSD", "bias": "Short", "week": "2026-W39", "status": "closed", "planned": True,
               "conditions": [{"id": "c3", "text": "เบรกแนวรับ", "status": "cancelled", "cancelled_at": "2026-09-28T01:00:00.000Z"},
                              {"id": "c4", "text": "ยังรอ", "active": False, "saved": True}]},
        "i3": {"v3": True, "asset": "BRENT", "bias": "Long", "week": "2026-W38", "status": "active", "planned": True,
               "conditions": [{"id": "c5", "text": "เงื่อนไขเก่ามาก", "status": "cancelled", "cancelled_at": "2026-09-01T09:00:00.000Z"}]},
        "i4": {"asset": "OLD", "bias": "Long", "week": "2026-W30", "status": "active"},   # ไอเดียเก่าไม่มี conditions
    }
    page.evaluate("""(ideas)=>{ const db=window.firebase.__mockDb; Object.keys(ideas).forEach(id=>db.__seedDoc(['users','testuid','satIdeas',id], ideas[id])); }""", ideas)
    page.wait_for_timeout(800)
    items = page.evaluate("() => [...document.querySelectorAll('#condBody .jCondItem')].map(e=>({at:e.dataset.condAt.slice(0,10), t:e.innerText.replace(/\\s+/g,' ').trim()}))")
    check(f"{tag} E เงื่อนไข cancelled จากหลาย idea ขึ้นครบ 3 ข้อ · active/ยังรอ ไม่ขึ้น", len(items) == 3 and not any("ปิดเหนือ 4300" in x["t"] or "ยังรอ" in x["t"] for x in items), json.dumps(items, ensure_ascii=False))
    check(f"{tag} E เรียงใหม่สุดก่อน (09-28 → 09-25 → 09-01)", [x["at"] for x in items] == ["2026-09-28", "2026-09-25", "2026-09-01"], json.dumps([x["at"] for x in items]))
    first = items[0]["t"]
    lab = page.evaluate("() => [sat7dLabel('BTCUSD'), sat7dLabel('XAUUSD')]")
    check(f"{tag} E แถว: วันที่สั้น (CL1: 28 ก.ย.) · asset (sat7dLabel) · Long/Short · ข้อความ · สัปดาห์ (week แบบอื่นแสดงดิบ)", all(k in first for k in ("28 ก.ย.", lab[0], "Short", "เบรกแนวรับ", "สัปดาห์ 2026-W39")), first + " | " + json.dumps(lab, ensure_ascii=False))
    check(f"{tag} E week '2026-09-27' → 'สัปดาห์ 27 ก.ย.' · asset XAUUSD ผ่าน sat7dLabel", "สัปดาห์ 27 ก.ย." in items[1]["t"] and lab[1] in items[1]["t"], items[1]["t"])
    check(f"{tag} E หมายเหตุหัวพาเนล 'ทุกบัญชี (แผน Sat ใช้ร่วมกัน)'", "ทุกบัญชี (แผน Sat ใช้ร่วมกัน)" in page.evaluate("() => document.getElementById('condBody').innerText"))
    view(page, "fam"); page.click("#jFilters .chip[data-jf=satB]")
    same = page.evaluate("() => document.querySelectorAll('#condBody .jCondItem').length")
    check(f"{tag} E ไม่ขึ้นกับชิปบัญชี/พอร์ต (สลับ fam + ชิป Sat แล้วยังเป็น 3 ข้อ)", same == 3)
    page.click("#jFilters .chip[data-jf=all]")
    check(f"{tag} E หุบไว้เป็นค่าเริ่มต้น · กดขยายได้", page.evaluate("() => document.getElementById('jContent_cond').style.display") == "none")
    page.click("#jColBtn_cond"); page.wait_for_timeout(80)
    check(f"{tag} E กดแล้วขยาย (เห็นรายการ)", page.evaluate("() => document.getElementById('jContent_cond').offsetParent !== null"))
    check(f"{tag} E อ่านอย่างเดียว: ไม่มีการเขียน satIdeas (idea ยังตามเดิม)", page.evaluate("() => JSON.stringify(window.firebase.__mockDb.__dump()['users/testuid/satIdeas/i1'].conditions.length)") == "2")


# ───────────────────────── เลย์เอาต์ ─────────────────────────
def layout_tests(page, tag, w):
    seed(page, MAIN, FAM, FAM_PORTS); view(page, "main")
    page.evaluate("() => { document.getElementById('jContent_cond').style.display=''; }")
    sw = page.evaluate("() => document.documentElement.scrollWidth")
    check(f"{tag} เลย์เอาต์: ไม่ล้นแนวนอน (scrollWidth={sw} ≤ {w})", sw <= w + 1, str(sw))
    hs = page.evaluate("""() => { const cs=[...document.querySelectorAll('#jSum .sumCell')].map(c=>{const r=c.getBoundingClientRect(); return {t:Math.round(r.top), h:Math.round(r.height)};});
        const rows={}; cs.forEach(c=>{ (rows[c.t]=rows[c.t]||[]).push(c.h); }); return rows; }""")
    check(f"{tag} เลย์เอาต์: บล็อก A ช่องสูงเท่ากันในแถวเดียว", all(len(set(v)) == 1 for v in hs.values()) and len(hs) >= 1, json.dumps(hs))
    cols = page.evaluate("() => getComputedStyle(document.querySelector('#jSum .jSumG')).gridTemplateColumns.split(' ').length")
    check(f"{tag} เลย์เอาต์: จำนวนคอลัมน์บล็อก A = {6 if w >= 1100 else 2} ที่ {w}px (ได้ {cols})", cols == (6 if w >= 1100 else 2 if w <= 700 else 3), str(cols))
    small = page.evaluate("() => Math.min(...[...document.querySelectorAll('#jSum *')].filter(e=>e.children.length===0 && e.innerText && e.innerText.trim() && e.offsetParent!==null).map(e=>parseFloat(getComputedStyle(e).fontSize)))/16")
    check(f"{tag} เลย์เอาต์: ตัวเล็กสุดในบล็อก ≥ 0.72rem ({small:.2f})", small >= 0.719, str(small))
    bg = page.evaluate("() => getComputedStyle(document.getElementById('jSum')).backgroundColor")
    check(f"{tag} เลย์เอาต์: บล็อกใช้พื้นเข้ม token --sum-bg (rgb(22, 25, 30))", bg == "rgb(22, 25, 30)", bg)
    pw_ = page.evaluate("() => getComputedStyle(document.getElementById('jPorts').firstElementChild).backgroundColor")
    check(f"{tag} เลย์เอาต์: #jPorts ยังเป็นพื้นขาว (ไม่ใช่พื้นเข้ม)", pw_ != "rgb(22, 25, 30)", pw_)
    page.evaluate("""() => { document.querySelectorAll('body *').forEach(e=>{ if(e.children.length<6 && /สำรองข้อมูลประจำสัปดาห์/.test(e.innerText||'') && getComputedStyle(e).position==='fixed') e.style.display='none'; }); window.scrollTo(0,0); }""")
    page.wait_for_timeout(700)   # รอแอนิเมชันสไลด์แท็บจบก่อนถ่ายภาพ
    shot(page, f"7f-jsum-{w}.png", "#jSum")
    view(page, "fam")
    page.wait_for_timeout(300)
    shot(page, f"7f-fam-{w}.png", "#tabJournal")
    page.evaluate("() => document.getElementById('setupPanel').scrollIntoView()")
    shot(page, f"7f-setup-{w}.png", "#setupPanel")
    shot(page, f"7f-cond-{w}.png", "#condPanel")
    page.evaluate("() => document.querySelector('#jAcctRow').scrollIntoView()")
    shot(page, f"7f-top-{w}.png")


def ui(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    numbers_tests(pw, w, h, tag)
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        decision_tests(page, tag)
        chip_tests(page, tag, w)
        setup_tests(page, tag)
        cond_tests(page, tag, w)
        layout_tests(page, tag, w)
        check(f"{tag} console: zero error-level messages (ชุดหลัก)", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors (ชุดหลัก)", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


def main():
    with sync_playwright() as pw:
        ui(pw, 1440, 900, "1440px")
        ui(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 16 / 7F) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
