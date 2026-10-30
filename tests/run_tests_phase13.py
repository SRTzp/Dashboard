#!/usr/bin/env python3
"""UI1 — (A) แถบบัญชีแท็บแผน: 2 แถว หุ้น/Future · Hold/Plan แตะแล้วเลื่อนไปตารางบัญชี · "ใหม่" เฉพาะ >0
        (B) Journal: แถบส้ม "ข้อมูลไม่ครบ n รายการ" ต่อบัญชี + รายการ (อ่านอย่างเดียว)
เทียบตัวเลขเดิม (รายละเอียดแถบ · Heat panel) กับ index.backup-pre-UI1.html ในข้อมูลชุดเดียวกัน
ภาพเก็บที่ tests/screenshots/ui1-*.png · รัน: python3 run_tests_phase13.py (mock Firestore + fundflow stub)
"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-UI1.html"))
ENGINE = base.BROWSER_ENGINE
results = []


def retired(name, reason):
    """CL2-b — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่พิมพ์ไว้ให้ตามรอยได้ (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:1500] + "...(truncated)") if (detail and len(detail) > 1500) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def norm(t): return " ".join((t or "").split())


def fresh(pw, w, h, path=None):
    browser, context, page, ce, pe = base.launch_page(pw, w, h, path or base.DEFAULT_INDEX)
    page.wait_for_function("() => serverConfirmed && stateFromServer", timeout=5000)
    page.wait_for_timeout(500)
    return browser, context, page, ce, pe


def shot(page, name, sel=None):
    try:
        loc = page.locator(sel) if sel else None
        if loc is not None and loc.count(): loc.first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name))
    except Exception as e:
        print("shot fail", name, e)


def T(id, port, status, **kw):
    """ไม้ตัวอย่าง: USD สำหรับ satB · THB สำหรับ core (ตามสกุลของพอร์ต)"""
    d = {"id": id, "date": "2026-09-28", "sym": kw.pop("sym", "AAA"), "port": port, "bias": "Long", "entry": 100, "sl": 95, "tp": None,
         "qty": 10, "mult": 1, "cur": "THB" if port == "core" else "USD", "status": status, "unplanned": False}
    d.update(kw); return d


def seed(page, main=None, fam=None, ports=None):
    """เขียนไม้ตรงเข้า book ของสองบัญชี แล้ว render (ไม่ผ่านฟอร์ม)"""
    page.evaluate("""([m,f,ports])=>{ getBook('main').trades = m||[]; getBook('fam').trades = f||[];
        acctList.forEach(a=>{ a.ports = (ports && ports[a.id]) || ['core','satB']; });
        planAcctFilter='all'; switchTab('plan'); render(); }""", [main, fam, ports])
    page.wait_for_timeout(150)


def strip(page):
    """ต่อการ์ดบัญชี: แถวหุ้น/Future (ตัวเลขจาก data-*) + รายละเอียด Open/Plan เดิม + ผลรวมจาก summarize เดิม"""
    return page.evaluate("""() => [...document.querySelectorAll('#strip .acctCard')].map(c=>{
      const id = c.querySelector('.acctRow1').dataset.acct;
      const g = k => { const e=c.querySelector('.acctGrp[data-grp='+k+']'); return e ? {open:+e.dataset.openTh, plan:+e.dataset.planTh, nOpen:+e.dataset.nOpen, nPlan:+e.dataset.nPlan, text:e.innerText.replace(/\\s+/g,' ').trim()} : null; };
      const s = withAccount(id, ()=>{ const x=summarize(); return {open:x.tot.open, plan:x.tot.plan}; });
      const kv = [...c.querySelectorAll('.acctKV')].map(e=>e.innerText.replace(/\\s+/g,' ').trim());
      return {id, stock:g('stock'), future:g('future'), s, kv, newTxt: (c.querySelector('.acctNew')||{}).innerText||null};
    })""")


# ───────────────────────── A) แถบบัญชี ─────────────────────────
def strip_tests(page, tag):
    # เคส 1: main = core + satB (CL2-a: ไม้ satA เดิมเปลี่ยนเป็น core) · fam = มีแต่ satB
    seed(page,
         main=[T("m1", "core", "open", sym="CCC"), T("m2", "core", "plan", sym="CCD"), T("m3", "core", "plan", sym="SSA"),
               T("m4", "satB", "open", sym="XAUUSD", qty=0.1, mult=100), T("m5", "satB", "plan", sym="S50", qty=2, mult=200, entry=900, sl=890)],
         fam=[T("f1", "satB", "open", sym="XAUUSD", qty=0.05, mult=100)])
    st = {x["id"]: x for x in strip(page)}
    for a in ("main", "fam"):
        x = st[a]; parts = [p for p in (x["stock"], x["future"]) if p]
        so, sp = sum(p["open"] for p in parts), sum(p["plan"] for p in parts)
        check(f"{tag} แถบ {a}: ผลรวม หุ้น+Future = Open/Plan เดิมของบัญชี (summarize)", abs(so - x["s"]["open"]) < 1e-6 and abs(sp - x["s"]["plan"]) < 1e-6, json.dumps(x, ensure_ascii=False))
    m = st["main"]
    check(f"{tag} แถบ main (core+satB): ทั้ง 2 แถว · หุ้น Hold 1 Plan 2 · Future Hold 1 Plan 1",
          m["stock"] and m["future"] and (m["stock"]["nOpen"], m["stock"]["nPlan"], m["future"]["nOpen"], m["future"]["nPlan"]) == (1, 2, 1, 1), json.dumps(m, ensure_ascii=False))
    check(f"{tag} แถบ main: รูปแบบข้อความ 'Hold n · ฿risk (x.xx% ถัง)' และ 'Plan n · +฿risk (y.yy% ถัง)' (7E-1: % ข้างหลัง = % ของถัง port นั้น · fmt2 = ทศนิยมสูงสุด 2 ตำแหน่ง)",
          all(__import__("re").search(r"Hold \d+ · ฿[\d,]+ \(\d+(\.\d{1,2})?% ถัง\)", p["text"]) and __import__("re").search(r"Plan \d+ · \+฿[\d,]+ \(\d+(\.\d{1,2})?% ถัง\)", p["text"]) for p in (m["stock"], m["future"])),
          json.dumps([m["stock"]["text"], m["future"]["text"]], ensure_ascii=False))
    f = st["fam"]
    check(f"{tag} แถบ fam (มีแต่ satB): แถวหุ้น 'Hold — · Plan —' (ไม่มีไม้) · Future Hold 1 · Plan —",
          f["stock"] and f["stock"]["text"].endswith("Hold — Plan —") and f["future"]["nOpen"] == 1 and "Plan —" in f["future"]["text"], json.dumps(f, ensure_ascii=False))
    # 7E-1: % ข้างหลัง Hold/Plan = % ของ "ถัง" port นั้น (หุ้น = ถัง Core · Future = ถัง Sat) — ฿ ÷ ถัง × 100 · ผลรวม ฿ ÷ ทุนรวมบัญชี = Open%/Plan% ในรายละเอียดเหมือนเดิม
    pcts = page.evaluate("""() => { const c=[...document.querySelectorAll('#strip .acctCard')][0];
        const num=(s,re)=>{ const m=s.match(re); return m?parseFloat(m[1]):0; };
        const gs=[...c.querySelectorAll('.acctGrp')];
        const tank={stock:portCapTHB('core'), future:portCapTHB('satB')}, cap=totalTHB();
        const rows=gs.map(e=>({k:e.dataset.grp, open:+e.dataset.openTh, plan:+e.dataset.planTh, po:num(e.innerText,/Hold[^(]*\\((\\d+\\.?\\d*)% ถัง\\)/), pp:num(e.innerText,/Plan[^(]*\\((\\d+\\.?\\d*)% ถัง\\)/)}));
        const kv=[...c.querySelectorAll('.acctKV b')].slice(0,2).map(e=>num(e.innerText,/([\\d.]+)%/));
        return {rows, tank, cap, kv, so: rows.reduce((a,r)=>a+r.open,0)/cap*100, sp: rows.reduce((a,r)=>a+r.plan,0)/cap*100}; }""")
    check(f"{tag} แถบ: % Hold/Plan ของแต่ละแถว = ฿ ÷ ถังของ port นั้น × 100 (คลาด ≤ 0.011) · หน่วยที่แสดง 'ถัง' (7E-1)", all(abs(r["po"] - r["open"] / pcts["tank"][r["k"]] * 100) <= 0.011 and abs(r["pp"] - r["plan"] / pcts["tank"][r["k"]] * 100) <= 0.011 for r in pcts["rows"]) and pcts["rows"], json.dumps(pcts))
    check(f"{tag} แถบ: Σ ฿ Hold/Plan ทั้ง 2 แถว ÷ ทุนรวมบัญชี = Open%/Plan% เดิมในรายละเอียดของบัญชี (คลาด ≤ 0.011 จากการปัดเศษ)", abs(pcts["so"] - pcts["kv"][0]) <= 0.011 and abs(pcts["sp"] - pcts["kv"][1]) <= 0.011, json.dumps(pcts))
    # ไม่มีไม้เลย
    seed(page, main=[], fam=[])
    st = {x["id"]: x for x in strip(page)}
    check(f"{tag} แถบ: ไม่มีไม้เลย → ผลรวม 0 = Open/Plan เดิม · Hold/Plan เป็น '—' ทุกแถว",
          all(x["s"]["open"] == 0 and x["s"]["plan"] == 0 and all(p and "Hold —" in p["text"] and "Plan —" in p["text"] for p in (x["stock"], x["future"])) for x in st.values()), json.dumps(st, ensure_ascii=False)[:300])
    # พอร์ตปิด
    seed(page, main=[T("m1", "core", "open")], fam=[T("f1", "satB", "open", qty=1)], ports={"main": ["core"], "fam": ["satB"]})
    st = {x["id"]: x for x in strip(page)}
    check(f"{tag} พอร์ตที่บัญชีปิด = ไม่แสดงแถวนั้น (main ปิด satB → ไม่มีแถว Future · fam เปิดแต่ satB → ไม่มีแถวหุ้น)",
          st["main"]["future"] is None and st["main"]["stock"] and st["fam"]["stock"] is None and st["fam"]["future"], json.dumps({k: [bool(v["stock"]), bool(v["future"])] for k, v in st.items()}))
    # "ใหม่"
    seed(page, main=[T("m1", "core", "open", date="2020-01-06")], fam=[T("f1", "satB", "open", qty=1, date=__import__("datetime").date.today().isoformat())])
    st = {x["id"]: x for x in strip(page)}
    check(f"{tag} 'ใหม่ n': ซ่อนเมื่อ 0 (main) · แสดงเมื่อ >0 (fam ใหม่ 1)", st["main"]["newTxt"] is None and st["fam"]["newTxt"] and "1" in st["fam"]["newTxt"], json.dumps([st["main"]["newTxt"], st["fam"]["newTxt"]], ensure_ascii=False))


def tap_tests(page, tag):
    seed(page, main=[T("m%d" % i, "core", "open" if i % 2 else "plan", sym="C%d" % i) for i in range(1, 14)],
         fam=[T("f%d" % i, "satB", "open", sym="XAUUSD", qty=0.05, mult=100) for i in range(1, 8)])
    page.evaluate("() => window.scrollTo(0,0)")
    rows_before = page.evaluate("() => document.querySelectorAll('#planSections tbody tr, #planSections .tcard').length")
    exp_before = page.evaluate("() => [...document.querySelectorAll('#strip .acctCard')].map(c=>c.classList.contains('open'))")
    sw = page.evaluate("() => (document.querySelector('#tabPlan .tabs-safe')||{}).x||0")
    page.locator('#strip .acctCard[data-priv="p-acct-fam"] button.acctJump[data-jump=hold]').first.click()
    page.wait_for_timeout(900)
    for _ in range(12):   # CL2-b: รอให้ smooth scroll นิ่งจริง (หน้าสูงบน 430px ใช้เวลาเกิน 900ms) — ไม่งั้นวัดกลางทาง
        y0 = page.evaluate("() => scrollY"); page.wait_for_timeout(150)
        if page.evaluate("() => scrollY") == y0: break
    r = page.evaluate("""() => { const s=[...document.querySelectorAll('#planSections .acctSec')].find(e=>e.dataset.acct==='fam'); const b=s.getBoundingClientRect();
        const hdr=document.querySelector('.tabs, #tabsBar'); return {top:b.top, vh:innerHeight, flash:s.classList.contains('flash'), filter:planAcctFilter,
        exp:[...document.querySelectorAll('#strip .acctCard')].map(c=>c.classList.contains('open')), overlays:document.querySelectorAll('.overlay.show, .ui-sheet-backdrop').length,
        rows:document.querySelectorAll('#planSections tbody tr, #planSections .tcard').length, sy:scrollY,
        atBottom: scrollY + innerHeight >= document.documentElement.scrollHeight - 2}; }""")
    # CL2-b: ลบแผง Ideas/Checklist ใต้ตารางแผน → หน้าสั้นลง · ถ้าเลื่อนสุดหน้าแล้วตารางยังอยู่ต่ำกว่า 60% ของจอ ถือว่าเลื่อนถึงแล้ว (เบราว์เซอร์เลื่อนต่อไม่ได้) แต่ต้องอยู่ในจอ
    check(f"{tag} แตะ Hold (fam): เลื่อนถึงตารางบัญชี fam (อยู่ในจอ · ไม่จมใต้หัว)", 0 <= r["top"] < r["vh"] and (r["top"] < r["vh"] * 0.6 or r["atBottom"]) and r["sy"] > 0, json.dumps(r))
    check(f"{tag} แตะ Hold: ไฮไลต์ ~1.5 วิ (มี flash ทันที → หายเอง)", r["flash"] and page.wait_for_timeout(1700) is None and not page.evaluate("() => !!document.querySelector('#planSections .acctSec.flash')"), json.dumps(r))
    check(f"{tag} แตะ Hold: planAcctFilter ไม่เปลี่ยน ('all') · แถบไม่ถูกกาง/พับ · ไม่มี popup · ไม่มีรายการซ้ำ",
          r["filter"] == "all" and r["exp"] == exp_before and r["overlays"] == 0 and r["rows"] == rows_before, json.dumps({"r": r, "before": exp_before, "rows0": rows_before}))
    page.evaluate("() => window.scrollTo(0,0)"); page.wait_for_timeout(200)
    page.locator('#strip .acctCard[data-priv="p-acct-main"] button.acctJump[data-jump=plan]').first.click(); page.wait_for_timeout(900)
    top = page.evaluate("() => [...document.querySelectorAll('#planSections .acctSec')].find(e=>e.dataset.acct==='main').getBoundingClientRect().top")
    check(f"{tag} แตะ Plan (main): เลื่อนถึงตารางบัญชี main", 0 <= top < page.evaluate("() => innerHeight") * 0.6, str(top))
    # แตะที่อื่นของหัวการ์ด = กาง/พับ
    page.evaluate("() => window.scrollTo(0,0)")
    page.locator('#strip .acctCard[data-priv="p-acct-main"] .acctRow1 > b').first.click(); page.wait_for_timeout(120)
    a = page.evaluate("() => document.querySelector('#strip .acctCard[data-priv=\"p-acct-main\"]').classList.contains('open')")
    page.locator('#strip .acctCard[data-priv="p-acct-main"] .acctRow1 > b').first.click(); page.wait_for_timeout(120)
    b = page.evaluate("() => document.querySelector('#strip .acctCard[data-priv=\"p-acct-main\"]').classList.contains('open')")
    check(f"{tag} แตะหัวการ์ด (ชื่อบัญชี) = กาง/พับเหมือนเดิม", a is True and b is False, f"{a},{b}")
    # ตัวกรองซ่อนบัญชีนั้น → สลับเป็น all ก่อนเลื่อน
    page.evaluate("() => { setPlanAcct('main'); }"); page.wait_for_timeout(100)
    page.evaluate("() => planJumpToAcct('fam')"); page.wait_for_timeout(700)
    ok = page.evaluate("() => ({f:planAcctFilter, has:!![...document.querySelectorAll('#planSections .acctSec')].find(e=>e.dataset.acct==='fam')})")
    check(f"{tag} ตัวกรองซ่อนบัญชีเป้าหมาย → planAcctFilter เป็น 'all' แล้วเลื่อนถึง", ok["f"] == "all" and ok["has"], json.dumps(ok))
    page.evaluate("() => setPlanAcct('all')")


def unchanged_tests(pw, w, h, tag, main, fam):
    """ตัวเลขเดิม (รายละเอียดแถบ Open/Plan/Heat · panel Port) หลังแก้ = ก่อนแก้ (ไฟล์ backup) ในข้อมูลชุดเดียวกัน"""
    def grab(path):
        browser, context, page, ce, pe = fresh(pw, w, h, path)
        try:
            seed(page, main=main, fam=fam)
            page.evaluate("() => { document.querySelectorAll('#strip .acctCard').forEach(c=>c.classList.add('open')); }")
            return page.evaluate("""() => ({kv:[...document.querySelectorAll('#strip .acctDetail')].map(e=>[...e.querySelectorAll('.acctKV b')].map(b=>b.innerText.replace(/\\s+/g,'')).join('|')),   /* UI-1b: ป้าย 'ความเสี่ยงค้าง…' → 'Open' — เทียบเฉพาะค่า (ป้าย/tooltip ดู phase14) */
                ports:((document.getElementById('ports')||{innerText:''}).innerText.replace(/\\s+/g,' ')),   /* 7E-1: บล็อก Core จัดวางใหม่ — ดึงเฉพาะ ทุน · ฿ ความเสี่ยงค้าง + % ของบัญชี ที่ยังคงเดิม (เทียบรายค่าเต็มใน phase14) */
                })""")
        finally:
            browser.close()
    new, old = grab(None), grab(BACKUP)
    # CL2-d: ไม่มี Heat 1R (ช่องในแถบบัญชี/บล็อก Port) และไม่มีป้าย 'ความเสี่ยงค้าง' ในหัวตาราง (ตาราง Trading Plan → Positions) → เทียบเฉพาะที่ยังอยู่:
    #   kv = ฝั่งเก่าตัดค่าลำดับที่ 3 (Heat) ออก · ports = ตัวเลขทุกตัวของฝั่งใหม่ต้องอยู่ในฝั่งเก่า (multiset)
    from collections import Counter
    old_kv = ["|".join(v for i, v in enumerate(r.split("|")) if i != 2) for r in old["kv"]]
    import re as _re
    def _pk(t, new_fmt):
        cap = _re.search(r"ทุน (฿[\d,]+) · ([\d.,]+)% ของทุนรวม", t)
        op = _re.search(r"(฿[\d,]+) · ≈ ([\d.,]+)% ของบัญชี", t) if new_fmt else _re.search(r"Open Risk (\S+) \(([\d.,]+)%\)", t)
        return (cap.groups() if cap else None, op.groups() if op else None)
    sub = _pk(new["ports"], True) == _pk(old["ports"], False) and _pk(new["ports"], True)[1] is not None
    check(f"{tag} ตัวเลขเดิม (Open% · Plan% · panel Port) ก่อน-หลังเท่ากัน (CL2-d: ตัด Heat + ป้ายเสี่ยงค้างในหัวตารางออกจากการเทียบ · 7E-1: panel Port เทียบเฉพาะ ทุน + ฿/% ของบัญชีของความเสี่ยงค้าง)", new["kv"] == old_kv and new["kv"] and sub, json.dumps({"kv": [new["kv"], old_kv], "ports": [_pk(new["ports"], True), _pk(old["ports"], False)]}, ensure_ascii=False))


def layout_tests(page, tag, w, h):
    seed(page, main=[T("m1", "core", "open"), T("m2", "core", "plan"), T("m4", "satB", "open", qty=0.1, mult=100)],
         fam=[T("f1", "satB", "open", qty=0.05, mult=100, date=__import__("datetime").date.today().isoformat())])
    sw = page.evaluate("() => document.documentElement.scrollWidth")
    check(f"{tag} แถบบัญชี: ไม่ล้นแนวนอน (scrollWidth={sw} ≤ {w})", sw <= w)
    g = page.evaluate("""() => { const c=[...document.querySelectorAll('#strip .acctCard')].map(e=>e.getBoundingClientRect());
        const btn=[...document.querySelectorAll('#strip button.acctJump')].map(e=>e.getBoundingClientRect().height);
        const fs=[]; document.querySelectorAll('#strip .acctCard *').forEach(e=>{ if(e.children.length===0 && e.textContent.trim() && e.offsetParent!==null){ fs.push(parseFloat(getComputedStyle(e).fontSize)); } });
        const ffam=getComputedStyle(document.querySelector('#strip .acctGrp')).fontFamily; const bg=getComputedStyle(document.querySelector('#strip .acctCard')).backgroundColor;
        return {sameRow: Math.abs(c[0].top-c[1].top)<2, stacked: c[1].top>=c[0].bottom-1, minBtn:Math.min(...btn), minFs:Math.min(...fs), ffam, bg}; }""")
    rem = page.evaluate("() => parseFloat(getComputedStyle(document.documentElement).fontSize)")
    if w >= 900: check(f"{tag} MacBook: การ์ดสองบัญชีวางคู่กันในแถวเดียว", g["sameRow"], json.dumps(g))
    else: check(f"{tag} มือถือ: การ์ดเรียงลงมา · ปุ่ม Hold/Plan สูง ≥ 36px", g["stacked"] and g["minBtn"] >= 36, json.dumps(g))
    check(f"{tag} แถบบัญชี: ตัวเล็กสุด ≥ 0.72rem · ฟอนต์ปกติ (ไม่ใช่ mono) · พื้นขาว", g["minFs"] >= rem * 0.72 - 0.05 and "mono" not in g["ffam"].lower() and g["bg"] in ("rgb(255, 255, 255)",), json.dumps(g))


# ───────────────────────── B) Journal ─────────────────────────
def journal_tests(page, tag, w):
    inc = lambda: page.evaluate("() => journalIncomplete().map(g=>({a:g.a.id, n:g.items.length, sym:g.items.map(i=>i.sym+':'+i.miss.map(m=>m.label).join('+'))}))")
    good_closed = T("c_ok", "core", "closed", sym="OKC", exitPrice=110, exitDate="2026-09-20")
    good_missed = T("ms_ok", "core", "missed", sym="OKM", missedTag="x", missedDate="2026-09-10")
    good_cancel = T("cn_ok", "core", "cancelled", sym="OKN", cancelNote="เปลี่ยนใจ", cancelDate="2026-09-11")
    # ไม้เก่าครบทุกช่องบังคับ แต่ไม่มี field F2c → ต้องไม่ถูกนับ · ไม้ใหม่มี F2c ครบ ก็ไม่ถูกนับเพราะ F2c
    old_no_f2c = T("old1", "satB", "closed", sym="XAUUSD", exitPrice=101, qty=0.1, mult=100)
    new_f2c = T("new1", "satB", "closed", sym="XAUUSD", exitPrice=101, qty=0.1, mult=100, trend_state="up", macro_state="with", driver="P1")
    bad_main = [T("b1", "core", "closed", sym="NOEXIT", exitDate="2026-09-25"),                     # closed ไม่มี exit price
                T("b2", "core", "missed", sym="NOWHY", missedDate="2026-09-12"),                      # missed ไม่มีเหตุผล
                T("b3", "core", "cancelled", sym="NOWHY2", cancelDate="2026-09-13", cancelNote="  ")]  # cancelled ไม่มีเหตุผล (ช่องว่างล้วน)
    bad_fam = [T("b4", "core", "closed", sym="NOQTY", qty=0, exitPrice=105, exitDate="2026-09-26")]
    plan_incomplete = T("p1", "core", "plan", sym="PLANX", entry=0)   # plan ไม่อยู่ใน Journal → ไม่ตรวจ
    seed(page, main=[good_closed, good_missed, good_cancel, old_no_f2c, new_f2c, plan_incomplete] + bad_main, fam=bad_fam)
    page.evaluate("() => switchTab('journal')"); page.wait_for_timeout(200)
    r = inc()
    d = {x["a"]: x for x in r}
    check(f"{tag} Journal: นับถูก แยกบัญชี — main 2 (exit/เหตุผลยกเลิก · ไม้ missed ไม่ถูกนับแล้ว CL2-b) · fam 1 (qty)", set(d) == {"main", "fam"} and d["main"]["n"] == 2 and d["fam"]["n"] == 1, json.dumps(r, ensure_ascii=False))
    check(f"{tag} Journal: ช่องที่ขาดระบุถูก (Exit Price · เหตุผลที่ยกเลิก · Qty · ไม้ missed ไม่มีในรายการ)",
          sorted(d["main"]["sym"]) == sorted(["NOEXIT:Exit Price", "NOWHY2:เหตุผลที่ยกเลิก"]) and d["fam"]["sym"] == ["NOQTY:Qty"], json.dumps(r, ensure_ascii=False))
    check(f"{tag} Journal: ไม้ไม่มี field F2c ไม่ถูกนับ · ไม้ที่มี F2c ไม่ถูกนับ · ไม้ plan ไม่ถูกนับ",
          not any(s.startswith(("XAUUSD", "OKC", "OKM", "OKN", "PLANX")) for x in r for s in x["sym"]), json.dumps(r, ensure_ascii=False))
    ban = page.evaluate("() => [...document.querySelectorAll('#jIncomplete .jIncHead')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
    check(f"{tag} Journal: แถบส้ม 1 บรรทัดต่อบัญชี 'ข้อมูลไม่ครบ n รายการ'", len(ban) == 2 and any("ข้อมูลไม่ครบ 2 รายการ" in b for b in ban) and any("ข้อมูลไม่ครบ 1 รายการ" in b for b in ban), json.dumps(ban, ensure_ascii=False))
    col = page.evaluate("() => { const h=document.querySelector('#jIncomplete .jIncHead span:last-of-type'); const s=document.querySelector('#jIncomplete .jIncHead'); return [getComputedStyle(s).color, getComputedStyle(document.querySelector('#jIncomplete .jInc')).borderLeftColor, getComputedStyle(document.documentElement).getPropertyValue('--amber').trim()]; }")
    check(f"{tag} Journal: แถบเตือนใช้สีส้ม (--amber)", col[0] == col[1] and col[0] != "rgb(0, 0, 0)", json.dumps(col))
    # กาง → รายการ
    page.locator('#jIncomplete .jInc[data-acct="main"] .jIncHead').click(); page.wait_for_timeout(100)
    rows = page.evaluate("() => [...document.querySelectorAll('#jIncomplete .jInc[data-acct=\"main\"] .jIncRow')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
    check(f"{tag} Journal: กางแล้วเห็นรายการ วันที่ · symbol · ช่องที่ขาด (ไม่มีชื่อบัญชีในแถว — หัวกลุ่มบอกอยู่แล้ว)", len(rows) == 2 and all("ขาด:" in x and "บัญชีหลัก" not in x for x in rows) and any("2026-09-25" in x and "NOEXIT" in x for x in rows), json.dumps(rows, ensure_ascii=False))
    shot(page, f"ui1-journal-{w}.png", "#jIncomplete")
    # อ่านอย่างเดียว
    page.evaluate("() => { dirtyBooks.clear(); window.__sets=0; }")
    page.evaluate("() => { renderJournal(); renderJournal(); }")
    check(f"{tag} Journal: render คำเตือนอ่านอย่างเดียว (ไม่เขียนข้อมูล · dirtyBooks ว่าง)", page.evaluate("() => dirtyBooks.size") == 0)
    # แตะแถว → เปิดตัวแก้ + โฟกัสช่องที่ขาด
    page.locator('#jIncomplete .jIncRow[data-tid="b1"]').click(); page.wait_for_timeout(300)
    f1 = page.evaluate("() => ({ov:document.getElementById('teOverlay').classList.contains('show'), ae:document.activeElement && document.activeElement.id})")
    check(f"{tag} Journal: แตะแถว closed → เปิดหน้าต่างแก้ไม้ (openTradeEdit) · โฟกัสช่อง Exit Price", f1["ov"] and f1["ae"] == "tExitPrice", json.dumps(f1))
    page.evaluate("() => closeTradeEdit()"); page.wait_for_timeout(100)
    retired(f"{tag} Journal: แตะแถว missed → เปิดโมดัลเหตุผล · โฟกัสช่องแท็ก", "CL2-b ลบ Missed ทั้งระบบ (ไม่มีแถว missed ใน 'ข้อมูลไม่ครบ' · ไม่มี #missedOverlay)")
    page.evaluate("() => { switchTab('journal'); }")
    # แตะแถวของอีกบัญชี (fam) → เปิดตัวแก้ของบัญชีนั้น
    page.locator('#jIncomplete .jInc[data-acct="fam"] .jIncHead').click(); page.wait_for_timeout(100)
    page.locator('#jIncomplete .jIncRow[data-tid="b4"]').click(); page.wait_for_timeout(300)
    f3 = page.evaluate("() => ({ov:document.getElementById('teOverlay').classList.contains('show'), ae:document.activeElement && document.activeElement.id, acct:teCtx && teCtx.acct})")
    check(f"{tag} Journal: แตะแถวบัญชี fam → เปิดตัวแก้ของ fam · โฟกัสช่อง Qty", f3["ov"] and f3["acct"] == "fam" and f3["ae"] == "tQty", json.dumps(f3))
    page.evaluate("() => closeTradeEdit()"); page.wait_for_timeout(100)
    # แก้ครบ → คำเตือนหายเอง
    page.evaluate("""() => { const B=getBook('main'); B.trades.find(t=>t.id==='b1').exitPrice=104; B.trades.find(t=>t.id==='b2').missedReason='พลาดเพราะงาน'; B.trades.find(t=>t.id==='b3').cancelTag='t1'; render(); }""")
    r2 = {x["a"]: x["n"] for x in inc()}
    ban2 = page.evaluate("() => [...document.querySelectorAll('#jIncomplete .jInc')].map(e=>e.dataset.acct)")
    check(f"{tag} Journal: แก้ครบใน main → คำเตือนของ main หายเอง · fam ยังอยู่", r2 == {"fam": 1} and ban2 == ["fam"], json.dumps([r2, ban2]))
    page.evaluate("() => { getBook('fam').trades.find(t=>t.id==='b4').qty=3; render(); }")
    check(f"{tag} Journal: ครบทุกไม้ → ไม่มีแถบเลย (#jIncomplete ว่าง)", page.evaluate("() => document.getElementById('jIncomplete').innerHTML.trim()") == "" and inc() == [])
    seed(page, main=[good_closed, good_missed, good_cancel, old_no_f2c, new_f2c], fam=[])
    page.evaluate("() => switchTab('journal')"); page.wait_for_timeout(150)
    check(f"{tag} Journal: ไม้ครบ (รวมไม้เก่าที่ไม่มี field F2c) → ไม่มีแถบ", page.evaluate("() => document.getElementById('jIncomplete').innerHTML.trim()") == "")
    sw = page.evaluate("() => document.documentElement.scrollWidth")
    seed(page, main=bad_main, fam=bad_fam); page.evaluate("() => switchTab('journal')"); page.wait_for_timeout(150)
    page.locator('#jIncomplete .jInc[data-acct="main"] .jIncHead').click(); page.wait_for_timeout(100)
    sw2 = page.evaluate("() => document.documentElement.scrollWidth")
    mf = page.evaluate("""() => { const o=[]; document.querySelectorAll('#jIncomplete *').forEach(e=>{ if(e.children.length===0 && e.textContent.trim() && e.offsetParent!==null){ o.push(parseFloat(getComputedStyle(e).fontSize)); } }); return Math.min(...o) / parseFloat(getComputedStyle(document.documentElement).fontSize); }""")
    check(f"{tag} Journal แถบเตือน: ไม่ล้นแนวนอน (scrollWidth={sw2} ≤ {w}) · ตัวเล็กสุด ≥ 0.72rem ({mf:.2f})", sw2 <= w and mf >= 0.719, f"{sw},{sw2},{mf}")


def ui(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        strip_tests(page, tag)
        tap_tests(page, tag)
        layout_tests(page, tag, w, h)
        seed(page, main=[T("m1", "core", "open"), T("m2", "core", "plan"), T("m4", "satB", "open", qty=0.1, mult=100)],
             fam=[T("f1", "satB", "open", qty=0.05, mult=100, date=__import__("datetime").date.today().isoformat()), T("f2", "satB", "plan", qty=0.05, mult=100)])
        page.evaluate("() => window.scrollTo(0,0)")
        shot(page, f"ui1-strip-{w}.png", "#strip")
        journal_tests(page, tag, w)
        check(f"{tag} console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()
    if w == 1440:
        unchanged_tests(pw, w, h, tag,
                        [T("m1", "core", "open"), T("m2", "core", "plan"), T("m3", "core", "plan", sym="SSA"), T("m4", "satB", "open", qty=0.1, mult=100)],
                        [T("f1", "satB", "open", qty=0.05, mult=100)])


def main():
    with sync_playwright() as pw:
        ui(pw, 1440, 900, "1440px")
        ui(pw, 430, 932, "430px")
        ui(pw, 932, 430, "932x430")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 13 / UI1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
