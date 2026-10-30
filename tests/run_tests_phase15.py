#!/usr/bin/env python3
"""BK1 — (A) Backup ครบ schema 3 · (B) กู้คืนจากไฟล์ dashboard-backup (พรีวิว/ติ๊กหมวด/พิมพ์ กู้คืน) · (C) tile Strategy แตะได้ทั้งช่อง
mock Firestore (ไม่ต่อเน็ต) · ภาพเก็บที่ tests/screenshots/bk1-*.png · รัน: python3 run_tests_phase15.py
"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as p11
import run_tests_phase13 as p13

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
UID = "testuid"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:1500] + "...(truncated)") if (detail and len(detail) > 1500) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def T(*a, **k): return p13.T(*a, **k)


def fresh(pw, w, h):
    browser, context, page, ce, pe = p13.fresh(pw, w, h)
    # กันรอบอัตโนมัติ (Mac) ยิงเองระหว่างเทส: ตั้งว่า backup ล่าสุด = ตอนนี้
    page.evaluate("() => localStorage.setItem('bkLastBackupAt', String(Date.now()))")
    page.on("dialog", lambda d: (DIALOGS.append(d.message), d.accept()))
    return browser, context, page, ce, pe


DIALOGS = []

# ───────────────────────── ชุดข้อมูล ─────────────────────────
MAIN = [T("m1", "core", "open", sym="CCC"), T("m2", "core", "plan", sym="CCD"), T("m3", "core", "closed", sym="CCE", exit=110),
        T("m4", "satB", "open", sym="XAUUSD", qty=0.1, mult=100)]
FAM = [T("f1", "core", "open", sym="ZZZ"), T("f2", "core", "closed", sym="ZZY", exit=90)]
IDEAS = {
    "i1": {"v3": True, "asset": "XAUUSD", "bias": "Long", "week": "2026-W40", "created_at": "2026-09-28T01:00:00.000Z", "status": "active", "entry": 4300, "sl": 4250, "tp": 4400,
           "checks": {"a": True, "b": False}, "conditions": [{"id": "c1", "text": "ปิดเหนือ 4300", "active": True, "saved": True}], "setups": ["Sweep"], "accts": {"main": {"broker": "XM", "placed": True}}, "planned": True},
    "i2": {"asset": "BTCUSD", "bias": "Short", "week": "2026-W40", "created_at": "2026-09-28T02:00:00.000Z", "status": "closed", "note": "เก่า"},
    "i3": {"v3": True, "asset": "BRENT", "bias": "Long", "week": "2026-W39", "created_at": "2026-09-21T02:00:00.000Z", "status": "active", "conditions": [], "planned": False, "setups": [], "accts": {}},
}
WEEK = {"2026-W40": {"XAUUSD": {"bias": "Long", "comps": {"trend": {"v": "up", "note": "n1"}}, "invalidation": 4200, "why": "เหตุผล"}, "BTCUSD": {"bias": "Short"}},
        "2026-W39": {"XAUUSD": {"bias": "None", "why": "รอ"}}}
CONFIG = {"setups": {"XAUUSD": ["Sweep", "BigBar", "Custom X"]}, "conditionTemplates": {"items": [{"id": "t1", "text": "ปิดเหนือแนวต้าน"}, {"id": "t2", "text": "หลุดแนวรับ"}]}}
PB1 = p11.pbver(1, p11.iso(-72), x="down", b="down_flat", r="flat")
PB2 = p11.pbver(2, p11.iso(-48), x="up", b="none", r="none")


def seed_all(page):
    """ไม้ในสองบัญชี (ผ่าน saveBook → เขียนขึ้น mock server จริง) + 4 collection ย่อย"""
    page.evaluate("""([m,f,ideas,week,cfg,pb1])=>{ const db=window.firebase.__mockDb, base=['users','testuid'];
        getBook('main').trades=m; getBook('fam').trades=f; saveBook('main'); saveBook('fam');
        Object.keys(ideas).forEach(id=>db.__seedDoc([...base,'satIdeas',id], ideas[id]));
        Object.keys(week).forEach(id=>db.__seedDoc([...base,'satWeek',id], week[id]));
        Object.keys(cfg).forEach(id=>db.__seedDoc([...base,'satConfig',id], cfg[id]));
        const {id, ...pbd} = pb1; db.__seedDoc([...base,'macroPlaybook',id], pbd); }""", [MAIN, FAM, IDEAS, WEEK, CONFIG, PB1])
    page.wait_for_timeout(900)


def dump(page):
    return page.evaluate("() => window.firebase.__mockDb.__dump()")


def cols(page):
    d = dump(page)
    out = {}
    for k, v in d.items():
        m = re.match(r"users/testuid/(satIdeas|satWeek|satConfig|macroPlaybook)/(.+)$", k)
        if m: out.setdefault(m.group(1), {})[m.group(2)] = v
    return out


def user_books(page):
    return dump(page)["users/testuid"]["books"]


def canon(o): return json.dumps(o, sort_keys=True, ensure_ascii=False)


def install_spies(page):
    """เก็บชื่อเมธอดที่แอปเรียกกับ Firestore (path, method) + จำนวนครั้งดาวน์โหลด (stub bkTriggerDownload)"""
    page.evaluate("""() => {
      window.__ops = []; window.__dl = [];
      const db = window.firebase.__mockDb;
      const wrap = o => new Proxy(o, { get(t, k){ const v = t[k];
        if(typeof v !== 'function') return v;
        return (...a)=>{ const r = v.apply(t, a);
          if(['set','update','delete','add'].indexOf(String(k))>=0) window.__ops.push([String(k), t.path||'?']);
          return (r && typeof r === 'object' && r.path !== undefined && typeof r.then !== 'function') ? wrap(r) : r; }; } });
      const oc = db.collection.bind(db); db.collection = n => wrap(oc(n));
      window.__realDl = window.bkTriggerDownload;
      window.bkTriggerDownload = (json, name) => { window.__dl.push({name, json}); };
    }""")


def export_file(page):
    """bkBuild จริง → ข้อความ JSON ของไฟล์ (แทนไฟล์ที่ผู้ใช้เลือก)"""
    return page.evaluate("async () => (await bkBuild()).json")


def open_restore(page, text, fname="backup.json"):
    DIALOGS.clear()
    ok = page.evaluate("async ([t,n]) => await bkRestoreLoad(t, n)", [text, fname])
    page.wait_for_timeout(150)
    return ok


def tick(page, *keys):
    for k in keys: page.evaluate("(k)=>{ const i=document.querySelector('.bk-sheet input[data-bk=\"'+k+'\"]'); i.checked=true; }", k)


def confirm(page, word="กู้คืน"):
    page.fill("#bkRsConfirm", word)
    page.click("#bkRsGo")
    page.wait_for_timeout(1200)


def close_sheet(page):
    page.evaluate("() => { if(bkRs){ bkRs.busy=false; bkRsClose(); } document.querySelectorAll('.bk-sheet').forEach(e=>e.remove()); bkRs=null; }")


def msg(page):
    return page.evaluate("() => { const e=document.getElementById('bkRsMsg'); return e ? e.textContent : null; }")


# ───────────────────────── A) export ─────────────────────────
def export_tests(pw):
    browser, context, page, ce, pe = fresh(pw, 1440, 900)
    try:
        seed_all(page)
        d0 = cols(page)
        obj = json.loads(export_file(page))
        m = obj["_meta"]
        check("A schema 3 · app=trading-dashboard · มี exportedAt/uid/accounts/activeAccount", m["schema"] == 3 and m["app"] == "trading-dashboard" and m["uid"] == UID and len(m["accounts"]) == 2 and m["activeAccount"], json.dumps(m)[:300])
        check("A payload มีครบ 4 collection (satIdeas/satWeek/satConfig/macroPlaybook) + doc.books ทุกบัญชี + state + watchlistV2",
              all(isinstance(obj.get(k), list) for k in ["satIdeas", "satWeek", "satConfig", "macroPlaybook"]) and set(obj["doc"]["books"].keys()) == {"main", "fam"} and "state" in obj and "watchlistV2" in obj)
        def strip(lst): return {x["id"]: {k: v for k, v in x.items() if k != "id"} for x in lst}
        check("A ทุกเอกสารเก็บ field ครบตามจริง (เทียบ mock server เอกสารต่อเอกสาร ไม่กรอง)",
              all(canon(strip(obj[k])) == canon(d0[k]) for k in ["satIdeas", "satWeek", "satConfig", "macroPlaybook"]),
              canon({k: strip(obj[k]) for k in ["satIdeas"]})[:400] + " || " + canon(d0.get("satIdeas"))[:400])
        c = m["counts"]
        check("A _meta.counts ถูก: books.main {trades:4 open:2 plan:0 closed:1...} · books.fam · satIdeas 3 · satWeek 2 · satConfig 2 · macroPlaybook 1",
              c["books"]["main"]["trades"] == 4 and c["books"]["main"]["open"] == 2 and c["books"]["main"]["plan"] == 1 and c["books"]["main"]["closed"] == 1
              and c["books"]["fam"]["trades"] == 2 and c["books"]["fam"]["closed"] == 1 and c["satIdeas"] == 3 and c["satWeek"] == 2 and c["satConfig"] == 2 and c["macroPlaybook"] == 1 and "partial" not in m, json.dumps(c))
        check("A satIdeas ของทุกเอกสารมี id เท่า doc id", sorted(x["id"] for x in obj["satIdeas"]) == ["i1", "i2", "i3"])

        # ---- ดึงสด: เพิ่มเอกสารตรงเข้า server (ไม่ผ่าน listener ของแอป) แล้ว export ต้องเห็นทันที
        page.evaluate("() => window.firebase.__mockDb.__seedDoc(['users','testuid','satIdeas','iLive'], {asset:'S50', bias:'Long', week:'2026-W40', status:'active'})")
        page.evaluate("() => { satIdeasList = []; }")   # หน่วยความจำ "ยังไม่โหลด" — export ต้องไม่พึ่งตัวแปรนี้
        obj2 = json.loads(export_file(page))
        check("A export ดึงสดจาก Firestore ไม่ใช้ตัวแปรในหน่วยความจำ (satIdeasList ว่าง แต่ไฟล์ยังมี 4 รายการรวม iLive)", len(obj2["satIdeas"]) == 4 and any(x["id"] == "iLive" for x in obj2["satIdeas"]))

        # ---- ดาวน์โหลดจริง + สรุป 1 บรรทัด
        page.evaluate("() => { window.firebase.__mockDb.__dump(); }")
        # ลบ iLive ให้จำนวนกลับเป็น 3 (mock ไม่มี helper ลบ → ผ่าน API)
        page.evaluate("async () => { await window.firebase.__mockDb.collection('users').doc('testuid').collection('satIdeas').doc('iLive').delete(); }")
        page.evaluate("() => { document.querySelector('#sysOverlay').classList.add('show'); document.querySelectorAll('#sysOverlay details.setsec').forEach(d=>d.open=true); }")
        with page.expect_download() as dl:
            page.click("text=Export JSON now")
        dl_info = dl.value
        p = dl_info.path()
        f = json.load(open(p, encoding="utf-8"))
        check("A ดาวน์โหลดจริงจากปุ่ม: ชื่อ dashboard-backup-YYYY-MM-DD-HHMM.json · schema 3 · ครบ 4 collection", re.match(r"^dashboard-backup-\d{4}-\d\d-\d\d-\d{4}\.json$", dl_info.suggested_filename) and f["_meta"]["schema"] == 3 and len(f["satIdeas"]) == 3, dl_info.suggested_filename)
        page.wait_for_timeout(300)
        s = page.inner_text("#bkSummary")
        check("A ปุ่ม Export: แสดงสรุป 1 บรรทัดหลังดาวน์โหลด 'สำรองแล้ว: 2 บัญชี · 6 ไม้ · แผน Sat 3 · สัปดาห์ 2 · Playbook 1'", s.strip() == "สำรองแล้ว: 2 บัญชี · 6 ไม้ · แผน Sat 3 · สัปดาห์ 2 · Playbook 1", s)
        page.screenshot(path=os.path.join(SHOTS, "bk1-1440-settings.png"))
        page.evaluate("() => document.querySelector('#sysOverlay').classList.remove('show')")
        page.evaluate("() => localStorage.setItem('bkLastBackupAt','0')")

        # ---- ตัวอย่าง _meta เพื่อรายงาน
        open(os.path.join(SHOTS, "bk1-sample-meta.json"), "w", encoding="utf-8").write(json.dumps(m, indent=2, ensure_ascii=False))

        # ---- collection หนึ่ง get() ล้ม → partial + เตือน ไม่ throw + ยังดาวน์โหลด
        install_spies(page)
        page.evaluate("() => window.firebase.__mockDb.__denyPath(['users','testuid','satWeek'])")
        r = page.evaluate("async () => { try{ return {ret: await exportBackupNow(true)}; }catch(e){ return {threw:String(e)}; } }")
        fj = json.loads(page.evaluate("() => window.__dl.length ? window.__dl[window.__dl.length-1].json : 'null'"))
        ban = page.evaluate("() => { const b=document.getElementById('bkBanner'); return {show:b.classList.contains('show'), t:document.getElementById('bkTitle').textContent, col:getComputedStyle(document.getElementById('bkTitle')).color}; }")
        check("A satWeek get() ล้ม → export ไม่ throw · คืน true · ยังดาวน์โหลดไฟล์", r == {"ret": True} and len(page.evaluate("() => window.__dl")) == 1, json.dumps(r))
        check("A partial: _meta.partial=['satWeek'] · counts.satWeek=null · ไม่มี key satWeek · หมวดอื่นครบ", fj["_meta"]["partial"] == ["satWeek"] and fj["_meta"]["counts"]["satWeek"] is None and "satWeek" not in fj and len(fj["satIdeas"]) == 3 and len(fj["macroPlaybook"]) == 1, json.dumps(fj["_meta"])[:300])
        check("A partial: แจ้งเตือนส้ม (bkBanner) 'backup ไม่ครบ: satWeek' ไม่เงียบ", ban["show"] and "backup ไม่ครบ: satWeek" in ban["t"], json.dumps(ban))
        sm = page.evaluate("() => document.getElementById('bkSummary').textContent")
        check("A partial: สรุปใต้ปุ่มขึ้น 'สัปดาห์ ?'", "สัปดาห์ ?" in sm, sm)
        page.evaluate("() => window.firebase.__mockDb.__allowPath(['users','testuid','satWeek'])")

        # ---- รอบอัตโนมัติ (Mac) ใช้ payload ใหม่ · iOS ปิด
        page.evaluate("() => { window.__dl = []; window.bkIsMac = () => true; localStorage.setItem('bkLastBackupAt','0'); localStorage.removeItem('bkSnoozeUntil'); }")
        page.evaluate("async () => { await bkCheck(); }")
        af = json.loads(page.evaluate("() => window.__dl.length ? window.__dl[0].json : 'null'") or "null")
        atitle = page.evaluate("() => document.getElementById('bkTitle').textContent")
        check("A รอบอัตโนมัติ (Mac · อาทิตย์ 20:00 → bkCheck) ใช้ payload schema 3 เดียวกัน", af and af["_meta"]["schema"] == 3 and len(af["satIdeas"]) == 3 and "partial" not in af["_meta"], str(af)[:200])
        check("A รอบอัตโนมัติสำเร็จ: แถบ 'สำรองข้อมูลประจำสัปดาห์แล้ว'", "สำรองข้อมูลประจำสัปดาห์แล้ว" in atitle, atitle)
        page.evaluate("() => { window.__dl = []; window.bkIsMac = () => false; localStorage.setItem('bkLastBackupAt','0'); }")
        page.evaluate("async () => { await bkCheck(); }")
        check("A iOS: auto ปิดเหมือนเดิม (ไม่ดาวน์โหลด)", page.evaluate("() => window.__dl.length") == 0)
        page.evaluate("() => { window.__dl = []; window.bkIsMac = () => true; localStorage.setItem('bkLastBackupAt','0'); }")
        page.evaluate("() => window.firebase.__mockDb.__denyPath(['users','testuid','macroPlaybook'])")
        page.evaluate("async () => { await bkCheck(); }")
        atitle2 = page.evaluate("() => document.getElementById('bkTitle').textContent")
        check("A auto + collection ล้ม: แถบเตือน 'backup ไม่ครบ' ไม่ถูกทับด้วยข้อความ 'สำเร็จ'", "backup ไม่ครบ: macroPlaybook" in atitle2, atitle2)
        page.evaluate("() => window.firebase.__mockDb.__allowPath(['users','testuid','macroPlaybook'])")

        # ---- stateFromServer=false → ไม่ export
        page.evaluate("() => { window.__dl = []; stateFromServer = false; }")
        DIALOGS.clear()
        r = page.evaluate("async () => await exportBackupNow(true)")
        check("A stateFromServer=false → ไม่ export (คืน false · ไม่ดาวน์โหลด · alert บอกให้รอซิงก์)", r is False and page.evaluate("() => window.__dl.length") == 0 and any("ซิงก์" in x for x in DIALOGS), json.dumps(DIALOGS))
        r = page.evaluate("async () => await exportBackupNow(false)")
        check("A stateFromServer=false + auto → ไม่ export เงียบ ๆ", r is False and page.evaluate("() => window.__dl.length") == 0)
        page.evaluate("() => { stateFromServer = true; }")
        check("A console: ไม่มี error/uncaught ตลอดชุด export (ยกเว้น warn ที่ตั้งใจ)", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── B) restore ─────────────────────────
def to_schema2(text):
    o = json.loads(text)
    for k in ["satIdeas", "satWeek", "satConfig", "macroPlaybook", "weeklyImpact", "stockNews"]: o.pop(k, None)   # WM1/SN1
    o["_meta"]["schema"] = 2; o["_meta"].pop("counts", None)
    return json.dumps(o, ensure_ascii=False)


def trades_of(page, acct): return [t["id"] for t in user_books(page)[acct]["trades"]]


def modify_all(page):
    """เปลี่ยนข้อมูลจริงบน server + ในหน่วยความจำ: ล้างไม้สองบัญชี · แก้/ลบ/เพิ่มเอกสาร Sat"""
    page.evaluate("""async () => { const db=window.firebase.__mockDb, u=db.collection('users').doc('testuid');
        getBook('main').trades=[{id:'zz',port:'core',status:'open',sym:'ZZ',date:'2026-09-28',entry:1,sl:1,qty:1,mult:1,cur:'THB',bias:'Long'}]; getBook('fam').trades=[]; saveBook('main'); saveBook('fam');
        await u.collection('satIdeas').doc('i1').set({asset:'CHANGED'});
        await u.collection('satIdeas').doc('i2').delete();
        await u.collection('satIdeas').doc('iExtra').set({asset:'EXTRA'});
        await u.collection('satWeek').doc('2026-W40').set({x:1});
        await u.collection('satConfig').doc('setups').delete();
        await u.collection('macroPlaybook').doc('2026Q4-v001').set({schema:'macroPlaybook/v1', marker:'LIVE'});
        await u.collection('macroPlaybook').doc('2026Q4-v002').delete();
    }""")
    page.wait_for_timeout(900)


def restore_tests(pw):
    browser, context, page, ce, pe = fresh(pw, 1440, 900)
    try:
        seed_all(page)
        # v002 อยู่ในไฟล์ด้วย (สร้างก่อน export)
        page.evaluate("([id,d])=>{ const {id:_, ...x}=d; window.firebase.__mockDb.__seedDoc(['users','testuid','macroPlaybook',id], x); }", ["2026Q4-v002", PB2])
        page.wait_for_timeout(200)
        D0 = dump(page)
        FILE = export_file(page)
        install_spies(page)
        check("B ตรวจไฟล์: _meta.app ผิด → alert + ไม่เปิดพรีวิว", (lambda: (open_restore(page, json.dumps({"_meta": {"app": "other", "schema": 3}, "doc": {}})) is False and page.locator(".bk-sheet").count() == 0 and any("trading-dashboard" in x for x in DIALOGS)))())
        check("B ตรวจไฟล์: schema 1/ไม่ใช่ JSON → alert ไม่เปิดพรีวิว", (lambda: (open_restore(page, json.dumps({"_meta": {"app": "trading-dashboard", "schema": 1}})) is False and open_restore(page, "not json{") is False and page.locator(".bk-sheet").count() == 0))())

        # ---- พรีวิว
        open_restore(page, FILE, "dashboard-backup-test.json")
        rows = page.evaluate("() => [...document.querySelectorAll('.bk-sheet .bkRsRow')].map(r=>({k:r.querySelector('input').dataset.bk, dis:r.querySelector('input').disabled, chk:r.querySelector('input').checked, t:r.innerText.replace(/\\s+/g,' ')}))")
        keys = [r["k"] for r in rows]
        check("B พรีวิว: ทุกหมวดมีแถว (แต่ละบัญชี + satIdeas/satWeek/satConfig/macroPlaybook/weeklyImpact/stockNews) พร้อมตาราง 'ในไฟล์ / ตอนนี้'",
              keys == ["acct:main", "acct:fam", "satIdeas", "satWeek", "satConfig", "macroPlaybook", "weeklyImpact", "stockNews"] and all("ในไฟล์" in r["t"] and "ตอนนี้" in r["t"] for r in rows), json.dumps(rows, ensure_ascii=False)[:600])
        check("B พรีวิว: ค่าเริ่มต้นไม่ติ๊กอะไรเลย", not any(r["chk"] for r in rows))
        mrow = [r for r in rows if r["k"] == "acct:main"][0]["t"]
        check("B พรีวิว: แถวบัญชีแสดงจำนวนไม้ open/plan/closed ของไฟล์และตอนนี้ (main: open 2 · plan 1 · closed 1)", mrow.count("open 2 · plan 1 · closed 1") == 2, mrow)
        check("B พรีวิว: แถว satIdeas แสดง 3 รายการทั้งไฟล์และตอนนี้ · macroPlaybook 2 รายการ", "3 รายการ" in [r for r in rows if r["k"] == "satIdeas"][0]["t"] and "2 รายการ" in [r for r in rows if r["k"] == "macroPlaybook"][0]["t"])
        page.screenshot(path=os.path.join(SHOTS, "bk1-1440-restore-preview.png"))

        # ---- ไม่ติ๊ก = ไม่เขียน
        modify_all(page)
        before = dump(page); page.evaluate("() => { window.__ops = []; window.__dl = []; }")
        page.fill("#bkRsConfirm", "กู้คืน"); page.click("#bkRsGo"); page.wait_for_timeout(600)
        check("B ไม่ติ๊กหมวดใด (แม้พิมพ์ถูก) → ไม่เขียนอะไร · ไม่ดาวน์โหลด · แจ้งข้อความ", canon(dump(page)) == canon(before) and page.evaluate("() => window.__dl.length") == 0 and page.evaluate("() => window.__ops.length") == 0 and "ยังไม่ได้ติ๊ก" in msg(page), msg(page))
        # ---- พิมพ์ผิด
        tick(page, "acct:main", "satIdeas", "satWeek", "satConfig", "macroPlaybook")
        for wrong in ["", "กู้", "restore", "กู้คืนx"]:
            page.fill("#bkRsConfirm", wrong); page.click("#bkRsGo"); page.wait_for_timeout(300)
            if canon(dump(page)) != canon(before) or page.evaluate("() => window.__dl.length") != 0: break
        check("B พิมพ์คำยืนยันผิด (ว่าง / กู้ / restore / กู้คืนx) → ไม่เขียน ไม่ดาวน์โหลด", canon(dump(page)) == canon(before) and page.evaluate("() => window.__dl.length") == 0 and page.evaluate("() => window.__ops.length") == 0 and "พิมพ์คำว่า" in msg(page), msg(page))
        check("B พิมพ์ผิดแล้วหน้าพรีวิวยังเปิดค้าง (ยังแก้คำได้)", page.locator(".bk-sheet #bkRsConfirm").count() == 1)
        close_sheet(page)

        # ---- ดาวน์โหลด before-restore ล้ม = ไม่กู้
        open_restore(page, FILE); tick(page, "acct:main", "satIdeas")
        page.evaluate("() => { window.bkTriggerDownload = () => { throw new Error('blocked'); }; window.__ops = []; }")
        confirm(page)
        check("B ดาวน์โหลด backup ก่อนกู้ล้ม → หยุด ไม่กู้ (ข้อมูลเดิมไม่เปลี่ยน · ไม่มี set/update/delete) พร้อมข้อความ", canon(dump(page)) == canon(before) and page.evaluate("() => window.__ops.length") == 0 and "หยุด ไม่กู้" in msg(page), msg(page))
        page.evaluate("() => { window.bkTriggerDownload = (json, name) => { window.__dl.push({name, json}); }; window.__dl = []; }")
        # ---- ตอนดึงหมวดที่จะทับไม่ได้ (สำรองของตอนนี้ไม่ครบ) → หยุดเหมือนกัน
        page.evaluate("() => window.firebase.__mockDb.__denyPath(['users','testuid','satIdeas'])")
        confirm(page)
        check("B backup ก่อนกู้ดึง satIdeas ไม่ได้ (หมวดที่จะทับ) → หยุด ไม่กู้", "หยุด ไม่กู้" in msg(page) and "satIdeas" in msg(page) and page.evaluate("() => window.__dl.length") == 0, msg(page))
        page.evaluate("() => window.firebase.__mockDb.__allowPath(['users','testuid','satIdeas'])")
        close_sheet(page)

        # ---- ติ๊กบัญชีเดียว: อีกบัญชีไม่เปลี่ยน
        fam_before = canon(user_books(page)["fam"])
        open_restore(page, FILE); tick(page, "acct:main"); page.evaluate("() => { window.__ops = []; window.__dl = []; }")
        confirm(page)
        b = user_books(page)
        dl = page.evaluate("() => window.__dl")
        check("B ติ๊กบัญชี main อย่างเดียว → main กลับตามไฟล์ (4 ไม้) · fam ไม่เปลี่ยน (ยังว่างตามที่แก้ไว้) · Sat collection ไม่ถูกแตะ",
              trades_of(page, "main") == ["m1", "m2", "m3", "m4"] and canon(b["fam"]) == fam_before and b["fam"]["trades"] == [] and cols(page)["satIdeas"]["i1"] == {"asset": "CHANGED"}, str(trades_of(page, "main")))
        check("B ก่อนเขียนจริงมีดาวน์โหลด 1 ไฟล์ ชื่อ dashboard-backup-before-restore-*.json เป็นสภาพ 'ก่อนกู้' (main มี 1 ไม้ 'zz')",
              len(dl) == 1 and re.match(r"^dashboard-backup-before-restore-\d{4}-\d\d-\d\d-\d{4}\.json$", dl[0]["name"]) and [t["id"] for t in json.loads(dl[0]["json"])["doc"]["books"]["main"]["trades"]] == ["zz"], json.dumps([x["name"] for x in dl]))
        check("B state ในหน่วยความจำของบัญชีที่กู้ตรงกับไฟล์ (บัญชี active หรือไม่ก็ตาม) และแสดงสรุปผลต่อหมวด (สำเร็จ 1 · ข้าม 0 · ล้มเหลว 0)",
              page.evaluate("() => getBook('main').trades.length") == 4 and "สำเร็จ 1 · ข้าม 0 · ล้มเหลว 0" in page.inner_text(".bk-sheet [data-bk-res='acct:main']"), page.inner_text(".bk-sheet"))
        close_sheet(page)

        # ---- ไฟล์ schema 2 เก่า → กู้ได้เฉพาะบัญชี
        S2 = to_schema2(FILE)
        modify_all(page)
        open_restore(page, S2, "old-schema2.json")
        rows2 = page.evaluate("() => [...document.querySelectorAll('.bk-sheet .bkRsRow')].map(r=>({k:r.querySelector('input').dataset.bk, dis:r.querySelector('input').disabled, t:r.innerText.replace(/\\s+/g,' ')}))")
        check("B ไฟล์ schema 2: แถวบัญชีเลือกได้ · 4 หมวดใหม่ disabled + 'ไม่มีในไฟล์'", all(not r["dis"] for r in rows2 if r["k"].startswith("acct:")) and all(r["dis"] and "ไม่มีในไฟล์" in r["t"] for r in rows2 if not r["k"].startswith("acct:")), json.dumps(rows2, ensure_ascii=False)[:2000])
        sat_before = canon(cols(page)); DIALOGS.clear()
        tick(page, "acct:main", "acct:fam"); page.evaluate("() => { window.__dl = []; }")
        confirm(page)
        check("B ไฟล์ schema 2 → กู้บัญชีได้ ไม่ error (ไม้กลับ · Sat collection ไม่เปลี่ยน)", trades_of(page, "main") == ["m1", "m2", "m3", "m4"] and trades_of(page, "fam") == ["f1", "f2"] and canon(cols(page)) == sat_before and not pe, msg(page) or str(pe))
        close_sheet(page)

        # ---- satIdeas ทับตาม id + เอกสารเกินไม่ถูกลบ
        modify_all(page)
        open_restore(page, FILE); tick(page, "satIdeas"); page.evaluate("() => { window.__ops = []; }")
        confirm(page)
        c = cols(page)
        check("B satIdeas: i1 ทับกลับตามไฟล์ · i2 (ถูกลบไปแล้ว) สร้างคืน · iExtra (เกินในตอนนี้) ไม่ถูกลบ · ไม่แตะ satWeek/satConfig",
              canon(c["satIdeas"]["i1"]) == canon(IDEAS["i1"]) and canon(c["satIdeas"]["i2"]) == canon(IDEAS["i2"]) and c["satIdeas"]["iExtra"] == {"asset": "EXTRA"} and c["satWeek"]["2026-W40"] == {"x": 1} and "setups" not in c["satConfig"], canon(c["satIdeas"])[:300])
        ops = page.evaluate("() => window.__ops")
        check("B satIdeas: เขียนด้วย set เท่านั้น (ไม่มี delete/update) และเฉพาะ collection satIdeas", ops and all(o[0] == "set" and "/satIdeas/" in o[1] for o in ops), json.dumps(ops))
        close_sheet(page)

        # ---- macroPlaybook: id ซ้ำ = ข้าม ไม่เรียก update/delete
        open_restore(page, FILE); tick(page, "macroPlaybook"); page.evaluate("() => { window.__ops = []; }")
        confirm(page)
        c = cols(page); ops = page.evaluate("() => window.__ops")
        pb_ops = [o for o in ops if "macroPlaybook" in o[1]]
        check("B macroPlaybook: v001 (มีอยู่แล้ว) ข้าม — คงค่าเดิม (marker LIVE) · v002 (ยังไม่มี) สร้างตามไฟล์", c["macroPlaybook"]["2026Q4-v001"].get("marker") == "LIVE" and c["macroPlaybook"]["2026Q4-v002"]["versionNo"] == 2, canon(c["macroPlaybook"])[:300])
        check("B macroPlaybook: ไม่เรียก update/delete เลย · set เฉพาะ id ใหม่ (v002 ครั้งเดียว)", not any(o[0] in ("update", "delete") for o in ops) and [o for o in pb_ops if o[0] == "set"] == [["set", "users/testuid/macroPlaybook/2026Q4-v002"]], json.dumps(ops))
        txt = page.inner_text(".bk-sheet [data-bk-res='macroPlaybook']")
        check("B macroPlaybook: สรุปแจ้งจำนวนที่ข้าม (สำเร็จ 1 · ข้าม 1 · ล้มเหลว 0 + ข้อความ 'ข้าม 1')", "สำเร็จ 1 · ข้าม 1 · ล้มเหลว 0" in txt and "ข้าม 1 เวอร์ชัน" in txt, txt)
        close_sheet(page)

        # ---- uid ต่างกัน = เตือนแดงแต่ไปต่อได้
        o = json.loads(FILE); o["_meta"]["uid"] = "someone-else"
        modify_all(page)
        open_restore(page, json.dumps(o), "other-uid.json")
        warn = page.evaluate("() => { const w=document.querySelector('.bk-sheet .bkRsWarn.bad'); return w ? {t:w.innerText, c:getComputedStyle(w).color} : null; }")
        tick(page, "acct:main"); confirm(page)
        check("B uid ในไฟล์ ≠ uid ปัจจุบัน → เตือนแดง (ระบุ uid) แต่ไปต่อได้ (กู้ main สำเร็จ)", warn and "someone-else" in warn["t"] and trades_of(page, "main") == ["m1", "m2", "m3", "m4"], json.dumps(warn, ensure_ascii=False))
        close_sheet(page)

        # ---- บัญชีในไฟล์ที่ไม่มีในแอป = ข้าม + แจ้ง
        o = json.loads(FILE); o["doc"]["books"]["ghost"] = o["doc"]["books"]["main"]; o["_meta"]["accounts"].append({"id": "ghost", "name": "Ghost", "ports": ["core"]})
        open_restore(page, json.dumps(o), "ghost.json")
        gk = page.evaluate("() => { const i=document.querySelector('.bk-sheet input[data-bk=\"acct:ghost\"]'); return i ? i.closest('label').innerText.replace(/\\s+/g,' ') : null; }")
        n_acct = page.evaluate("() => acctList.length")
        tick(page, "acct:ghost"); confirm(page)
        gt = page.inner_text(".bk-sheet [data-bk-res='acct:ghost']")
        check("B บัญชีในไฟล์ที่ไม่มีในแอป → แสดงในพรีวิวว่า 'ไม่มีบัญชีนี้ในแอป' · ติ๊กแล้วข้าม + แจ้ง (ข้าม 1) · ไม่สร้างบัญชีใหม่", gk and "ไม่มีบัญชีนี้ในแอปตอนนี้" in gk and "ข้าม 1" in gt and "ไม่มีบัญชีนี้ในแอป" in gt and page.evaluate("() => acctList.length") == n_acct, gk + " || " + gt)
        close_sheet(page)

        # ---- ล้มเหลวบางส่วน: satWeek เขียนไม่ได้ → บอกชัด · หมวดอื่นยังสำเร็จ
        modify_all(page)
        open_restore(page, FILE); tick(page, "satIdeas", "satWeek", "satConfig")
        # deny หลังพรีวิว (พรีวิว/backup ก่อนกู้ อ่านผ่านได้ แต่เขียน satWeek ล้ม) — mock deny ปฏิเสธทั้ง get และ set จึงต้อง deny เฉพาะช่วงเขียน:
        page.evaluate("""() => { const orig = window.bkTriggerDownload; window.bkTriggerDownload = (j, n) => { orig(j, n); window.firebase.__mockDb.__denyPath(['users','testuid','satWeek']); }; }""")
        confirm(page)
        res = page.evaluate("() => bkRestoreLast")
        h = page.inner_text(".bk-sheet h3"); wt = page.inner_text(".bk-sheet [data-bk-res='satWeek']")
        check("B ล้มเหลวบางส่วน: satWeek เขียนไม่สำเร็จ → สรุปบอกชัด 'ล้มเหลว 2' + หัวข้อ 'มีบางส่วนล้มเหลว' · satIdeas/satConfig ยังสำเร็จ",
              res["satWeek"]["fail"] == 2 and res["satWeek"]["ok"] == 0 and res["satIdeas"]["ok"] == 3 and res["satConfig"]["ok"] == 2 and "ล้มเหลว" in h and "ล้มเหลว 2" in wt and page.locator(".bk-sheet .bkRsRes.bad").count() == 1, json.dumps(res, ensure_ascii=False)[:500])
        page.evaluate("() => window.firebase.__mockDb.__allowPath(['users','testuid','satWeek'])")
        close_sheet(page)
        page.evaluate("() => { window.bkTriggerDownload = (json, name) => { window.__dl.push({name, json}); }; }")

        # ---- round-trip: ทุกหมวด → ข้อมูลกลับตรงกับตอน export (ยกเว้น macroPlaybook ที่มีอยู่แล้ว)
        page.evaluate("() => { window.__dl = []; }")
        modify_all(page)
        open_restore(page, FILE, "roundtrip.json")
        tick(page, "acct:main", "acct:fam", "satIdeas", "satWeek", "satConfig", "macroPlaybook"); confirm(page)
        D1 = dump(page)
        # CL2-a: กู้คืนผ่าน cl2aStripLegacy (ตัด key/ฟิลด์ Sat.A เดิม เช่น sizing.r.satA) → ค่าที่คาดหวัง = Strip ของก้อนตอน export (ไม่ใช่ก้อนดิบเดิม)
        exp_books = page.evaluate("(b)=>Object.fromEntries(Object.entries(b).map(([k,v])=>[k,cl2aStripLegacy(v)]))", D0["users/testuid"]["books"])
        # ideas/checklistDrafts/failLog: Strip ตัดทิ้ง แล้ว buildStateFromBookRaw ใส่ [] กลับ (โค้ด CL2-b ยังอ่านอยู่) → เทียบโดยไม่นับ [] ว่างของ 3 key นี้
        drop_empty = lambda bs: {b: {k: v for k, v in bk.items() if not (k in ("ideas", "checklistDrafts", "failLog") and v == [])} for b, bk in bs.items()}
        ok_books = canon(drop_empty(D1["users/testuid"]["books"])) == canon(drop_empty(exp_books))
        ok_cols = True; bad = []
        for k, v in D0.items():
            if re.search(r"users/testuid/(satIdeas|satWeek|satConfig)/", k):
                if canon(D1.get(k)) != canon(v): ok_cols = False; bad.append(k)
        # satIdeas ที่เกิน (iExtra) ต้องยังอยู่ (ไม่ลบ) — ไม่นับเป็นความต่าง
        pb_ok = D1["users/testuid/macroPlaybook/2026Q4-v001"].get("marker") == "LIVE" and canon(D1["users/testuid/macroPlaybook/2026Q4-v002"]) == canon(D0["users/testuid/macroPlaybook/2026Q4-v002"])
        check("B round-trip: books ทุกบัญชีบน server กลับตรงกับตอน export (canonical JSON เท่ากันทั้งก้อน)", ok_books, canon(D1["users/testuid"]["books"])[:300] + " || " + canon(D0["users/testuid"]["books"])[:300])
        check("B round-trip: satIdeas/satWeek/satConfig ทุกเอกสารกลับตรงตอน export ทีละ field", ok_cols, json.dumps(bad))
        check("B round-trip: macroPlaybook — v001 (มีอยู่แล้ว) คงของเดิมไม่ถูกแตะ · v002 สร้างกลับเท่าตอน export", pb_ok)
        check("B round-trip: หน้าสรุปหลังกู้ครบ 6 หมวด ไม่มีล้มเหลว", page.locator(".bk-sheet [data-bk-res]").count() == 6 and page.locator(".bk-sheet .bkRsRes.bad").count() == 0, page.inner_text(".bk-sheet")[:400])
        check("B round-trip: ในหน่วยความจำ — ไม้ของ main/fam กลับ · syncBadge ไม่ error", page.evaluate("() => getBook('main').trades.length") == 4 and page.evaluate("() => getBook('fam').trades.length") == 2 and "error" not in page.evaluate("() => document.getElementById('syncBadge').className"))
        close_sheet(page)
        check("B ปุ่มกู้คืน bkRestoreOpen อยู่ข้างปุ่ม Export · (CL2-a: ปุ่มเดิม phase7mRestoreFromFile ถูกลบแล้ว)", page.evaluate("() => typeof phase7mRestoreFromFile === 'undefined' && !document.querySelector('button[onclick=\"phase7mRestoreFromFile()\"]') && !!document.querySelector('.btns button[onclick=\"bkRestoreOpen()\"]')"))
        check("B console: ไม่มี uncaught page error ตลอดชุด restore", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


def restore_via_file_chooser(pw):
    """ปุ่มจริง: กดปุ่ม → file chooser → เลือกไฟล์ → พรีวิวเปิด"""
    browser, context, page, ce, pe = fresh(pw, 430, 932)
    try:
        seed_all(page)
        FILE = export_file(page)
        path = os.path.join(SHOTS, "bk1-tmp-backup.json"); open(path, "w", encoding="utf-8").write(FILE)
        page.evaluate("() => { document.querySelector('#sysOverlay').classList.add('show'); document.querySelectorAll('#sysOverlay details.setsec').forEach(d=>d.open=true); }")
        with page.expect_file_chooser() as fc:
            page.click("text=Restore from backup file")
        fc.value.set_files(path)
        page.wait_for_selector(".bk-sheet .bkRsRow", timeout=4000)
        check("B ปุ่ม 'กู้คืนจากไฟล์ backup…' → เลือกไฟล์ → หน้าพรีวิวเปิด (8 แถว)", page.locator(".bk-sheet .bkRsRow").count() == 8)   # WM1/SN1: 6 → 8 แถว
        os.remove(path)
    finally:
        browser.close()


# ───────────────────────── ภาพ 430px ─────────────────────────
def restore_shots_430(pw):
    browser, context, page, ce, pe = fresh(pw, 430, 932)
    try:
        seed_all(page)
        FILE = export_file(page)
        install_spies(page)
        modify_all(page)
        o = json.loads(FILE); o["_meta"]["uid"] = "other-uid-1234"
        open_restore(page, json.dumps(o), "dashboard-backup-2026-09-28-2000.json")
        tick(page, "acct:main", "satIdeas", "macroPlaybook")
        page.fill("#bkRsConfirm", "กู้คืน")
        m = page.evaluate("""() => { const s=document.querySelector('.bk-sheet .ui-sheet'); const r=s.getBoundingClientRect();
            return {sw:s.scrollWidth, cw:s.clientWidth, left:r.left, right:r.right, vw:innerWidth, docW:document.documentElement.scrollWidth,
              minFont:Math.min(...[...s.querySelectorAll('*')].filter(e=>!e.children.length && e.textContent.trim()).map(e=>parseFloat(getComputedStyle(e).fontSize))),
              btnH:Math.min(...[...s.querySelectorAll('.bkRsBtns button')].map(b=>b.getBoundingClientRect().height))}; }""")
        check("430 หน้าพรีวิว: ไม่ล้น (sheet scrollWidth ≤ clientWidth · อยู่ในจอ · เอกสารไม่เลื่อนแนวนอน)", m["sw"] <= m["cw"] + 1 and m["left"] >= 0 and m["right"] <= m["vw"] + 1 and m["docW"] <= m["vw"] + 1, json.dumps(m))
        check("430 หน้าพรีวิว: ตัวหนังสือเล็กสุด ≥ 12px · ปุ่มสูง ≥ 40px", m["minFont"] >= 12 and m["btnH"] >= 40, json.dumps(m))
        page.screenshot(path=os.path.join(SHOTS, "bk1-430-restore-preview.png"))
        page.click("#bkRsGo"); page.wait_for_timeout(1400)
        m2 = page.evaluate("() => { const s=document.querySelector('.bk-sheet .ui-sheet'); return {sw:s.scrollWidth, cw:s.clientWidth, docW:document.documentElement.scrollWidth, vw:innerWidth}; }")
        check("430 หน้าสรุปหลังกู้: ไม่ล้น · มีผลต่อหมวด (สำเร็จ/ข้าม/ล้มเหลว)", m2["sw"] <= m2["cw"] + 1 and m2["docW"] <= m2["vw"] + 1 and "สำเร็จ" in page.inner_text(".bk-sheet") and page.locator(".bk-sheet [data-bk-res]").count() == 3, json.dumps(m2))
        page.screenshot(path=os.path.join(SHOTS, "bk1-430-restore-result.png"))
        # 1440 หน้าสรุป
    finally:
        browser.close()


# ───────────────────────── C) tile ─────────────────────────
def tile_setup(page):
    p11.seed_pb(page, [p11.pbver(1, p11.iso(-72), x="down", b="down_flat", r="flat")])
    p11.wk(page, "XAUUSD", "Long", "down", inval=4200)
    p11.wk(page, "BTCUSD", "Short", "down", inval=105000)
    page.evaluate("() => satwWrite('BRENT', {comps:{trend:{v:'up'}}})"); page.wait_for_timeout(120)
    page.evaluate("() => satwWrite('S50', {bias:'None', why:'รอสัญญาณ'})"); page.wait_for_timeout(200)
    page.evaluate("""() => { getBook('main').trades=[]; getBook('fam').trades=[]; acctList.forEach(a=>{ a.ports=['core','satB']; }); planAcctFilter='all'; switchTab('plan'); setPlanScope('future'); satV3Sel=null; satV3Render(); }""")
    page.wait_for_timeout(300)


def tile_tests(pw, w, h):
    tag = f"[{w}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        tile_setup(page)
        page.evaluate("() => { window.__picks = []; const o = window.satV3Pick; window.satV3Pick = a => { window.__picks.push(a); return o(a); }; }")
        assets_all = page.evaluate("() => SAT_ASSETS.map(a=>a.key)")
        assets = page.evaluate("() => [...document.querySelectorAll('.sumBlk .ui-tile')].map(t=>t.dataset.key)")   # WA1fix: tile ตาม pick สัปดาห์นี้ (3) · สินค้าทั้งหมดยัง 4
        check(f"{tag} tile: PF3 ไม่มีใบงดเทรดที่จาง — ไม่มี .ui-dim · ทุกใบ opacity = 1 (ทั้ง 3 ใบที่เลือกเหมือนกัน)", page.evaluate("() => document.querySelectorAll(\".sumBlk .ui-tile.ui-dim\").length") == 0 and page.evaluate("() => [...document.querySelectorAll(\".sumBlk .ui-tile\")].every(t=>getComputedStyle(t).opacity===\"1\")"))
        check(f"{tag} tile: PF1 — มี 3 tile ที่เลือก (สินค้าทั้งหมด 4) · ทุกใบ role=button tabindex=0 cursor:pointer · ไม่มีใบจาง", len(assets_all) == 4 and len(assets) == 3 and page.evaluate("() => [...document.querySelectorAll(\".sumBlk .ui-tile\")].every(t=>t.getAttribute(\"role\")===\"button\" && t.tabIndex===0 && getComputedStyle(t).cursor===\"pointer\")") and page.evaluate("() => !document.querySelector(\".sumBlk .ui-tile.ui-dim\")"))
        check(f"{tag} tile: หัวช่อง (.ui-tile-th) ไม่มี onclick ซ้อนอีกแล้ว (กันแตะซ้อน 2 ครั้ง)", page.evaluate("() => [...document.querySelectorAll('.sumBlk .ui-tile-th')].every(e=>!e.getAttribute('onclick'))"))
        for a in assets:
            for corner in ("ล่างซ้าย", "ล่างขวา"):
                page.evaluate("() => { satV3Sel = null; satV3Render(); window.__picks = []; }"); page.wait_for_timeout(120)
                page.evaluate("(a)=>document.querySelector('.sumBlk .ui-tile[data-key=\"'+a+'\"]').scrollIntoView({block:'center'})", a); page.wait_for_timeout(120)   # ที่ 430 แถบแท็บล่างเป็น fixed — เลื่อนให้ tile พ้นแถบก่อนแตะ (เหมือนผู้ใช้จริง)
                box = page.locator(f'.sumBlk .ui-tile[data-key="{a}"]').bounding_box()
                x = box["x"] + (8 if corner == "ล่างซ้าย" else box["width"] - 8); y = box["y"] + box["height"] - 8
                hit = page.evaluate("([x,y])=>{ const e=document.elementFromPoint(x,y); return e ? {tag:e.tagName, cls:e.className, btn:!!e.closest('button')} : null; }", [x, y])
                page.mouse.click(x, y); page.wait_for_timeout(220)
                st = page.evaluate("() => ({sel:satV3Sel, picks:window.__picks.slice(), ed:document.querySelector('#satV3Panel .ui-editor') ? document.querySelector('#satV3Panel .ui-editor').innerText.slice(0,80) : null})")
                check(f"{tag} tile {a}: คลิกมุม{corner} (ไม่ใช่ปุ่ม) → เปิดตัวแก้ของ asset นั้น · เรียก satV3Pick ครั้งเดียว (ไม่เปิดแล้วปิดทันที)",
                      not hit["btn"] and st["sel"] == a and st["picks"] == [a] and st["ed"], json.dumps({"hit": hit, "st": st}, ensure_ascii=False))
        # ---- + แผน
        n0 = len(cols(page).get("satIdeas", {})) if False else page.evaluate("async () => (await window.firebase.__mockDb.collection('users').doc('testuid').collection('satIdeas').get()).docs.length")
        page.evaluate("() => { satV3Sel = null; satV3Render(); window.__picks = []; }"); page.wait_for_timeout(150)
        page.click('.sumBlk .ui-tile[data-key="XAUUSD"] .ui-btn-pri'); page.wait_for_timeout(500)
        st = page.evaluate("() => ({sel:satV3Sel, picks:window.__picks.slice()})")
        n1 = page.evaluate("async () => (await window.firebase.__mockDb.collection('users').doc('testuid').collection('satIdeas').get()).docs.length")
        check(f"{tag} tile: คลิก '+ แผน' → สร้างแผนเท่านั้น (satIdeas +1) · ไม่เรียก satV3Pick · ตัวแก้ไม่เปิด/ปิด (satV3Sel ยัง null)", n1 == n0 + 1 and st["picks"] == [] and st["sel"] is None, json.dumps({"n0": n0, "n1": n1, **st}))
        # ตัวแก้เปิดอยู่ แล้วกด + แผน → ตัวแก้ต้องไม่ปิด
        page.evaluate("() => { satV3Sel = 'BTCUSD'; satV3Render(); window.__picks = []; }"); page.wait_for_timeout(150)
        page.click('.sumBlk .ui-tile[data-key="BTCUSD"] .ui-btn-pri'); page.wait_for_timeout(500)
        st = page.evaluate("() => ({sel:satV3Sel, picks:window.__picks.slice()})")
        check(f"{tag} tile: ตัวแก้เปิดอยู่แล้วกด '+ แผน' ในใบเดียวกัน → ไม่พับตัวแก้ (ไม่มีการแตะซ้อน)", st["sel"] == "BTCUSD" and st["picks"] == [], json.dumps(st))
        # ---- คีย์บอร์ด
        page.evaluate("() => { satV3Sel = null; satV3Render(); window.__picks = []; }"); page.wait_for_timeout(150)
        page.focus('.sumBlk .ui-tile[data-key="S50"]'); page.keyboard.press("Enter"); page.wait_for_timeout(200)
        s1 = page.evaluate("() => satV3Sel")
        foc = page.evaluate("() => document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.key : null")
        page.keyboard.press("Space"); page.wait_for_timeout(200)
        s2 = page.evaluate("() => satV3Sel")
        check(f"{tag} tile: คีย์บอร์ด Enter = เปิดตัวแก้ · Space = พับ (toggle เหมือนแตะ) · โฟกัสคงอยู่ที่ tile เดิมหลังวาดใหม่", s1 == "S50" and s2 is None and foc == "S50", json.dumps([s1, s2, foc]))
        page.evaluate("() => { satV3Sel = null; satV3Render(); window.__picks = []; }"); page.wait_for_timeout(150)
        page.focus('.sumBlk .ui-tile[data-key="XAUUSD"] .ui-btn-pri'); page.keyboard.press("Enter"); page.wait_for_timeout(300)
        check(f"{tag} tile: Enter บนปุ่ม '+ แผน' ไม่ทำให้ tile เปิดตัวแก้ด้วย", page.evaluate("() => satV3Sel") is None and page.evaluate("() => window.__picks.length") == 0)
        # ---- layout
        page.evaluate("() => { satV3Sel = 'XAUUSD'; satV3Render(); }"); page.wait_for_timeout(200)
        sw = page.evaluate("() => document.documentElement.scrollWidth")
        check(f"{tag} ไม่ล้นแนวนอน (scrollWidth={sw})", sw <= w + 1)
        page.evaluate("() => { satV3Sel = null; satV3Render(); }"); page.wait_for_timeout(150)
        page.evaluate("() => document.querySelectorAll('.tabSlideIn').forEach(e=>e.classList.remove('tabSlideIn'))")
        try: page.locator("#satV3Sum").screenshot(path=os.path.join(SHOTS, f"bk1-{w}-tiles.png"))
        except Exception as e: print("shot fail", e)
        check(f"{tag} console: ไม่มี error / uncaught", not ce and not pe, "; ".join((ce + pe)[:3]))
    finally:
        browser.close()


def layout_1440(pw):
    browser, context, page, ce, pe = fresh(pw, 1440, 900)
    try:
        seed_all(page)
        FILE = export_file(page)
        install_spies(page)
        open_restore(page, FILE, "dashboard-backup-x.json")
        m = page.evaluate("() => ({docW:document.documentElement.scrollWidth, vw:innerWidth, sh:document.querySelector('.bk-sheet .ui-sheet').getBoundingClientRect().width})")
        check("1440 หน้าพรีวิว: ไม่ล้น · sheet กว้างตามมาตรฐาน UI.sheet (≤ 560)", m["docW"] <= m["vw"] + 1 and m["sh"] <= 561, json.dumps(m))
        close_sheet(page)
    finally:
        browser.close()


def main():
    with sync_playwright() as pw:
        export_tests(pw)
        restore_tests(pw)
        restore_via_file_chooser(pw)
        restore_shots_430(pw)
        layout_1440(pw)
        tile_tests(pw, 1440, 900)
        tile_tests(pw, 430, 932)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 15 / BK1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:400])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
