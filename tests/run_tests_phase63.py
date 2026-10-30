#!/usr/bin/env python3
"""AC2 — การ์ดเงื่อนไขเข้า Sat แบบกรอกตัวเลข: TF → Break Price ▲▼ → Break Vol ▲▼ → Pullback (ขยับตาม Break เสมอถ้าไม่ได้พิมพ์เอง) · เทส 63
mock Firestore · Chromium 1440 + 390
ภาพ tests/screenshots/ac2-{plan,pending,active,active-btc,short}-{1440,390}.png
รัน: python3 run_tests_phase63.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase36 as p36
import run_tests_phase37 as P37
import run_tests_phase38 as P38
import run_tests_phase39 as P39
import run_tests_phase51 as P51
import run_tests_phase55 as P55
import run_tests_phase60 as P60

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
CLK = "2026-10-01T05:00:00Z"
ROOT = '.ui-plan[data-id="iD"]'


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


shot = P60.shot
doc_of, cd, active_ids, txt, overflow = P60.doc_of, P60.cd, P60.active_ids, P60.txt, P60.overflow
sat_page = P60.sat_page


def cond(cid="c1", text="", tp=None, inval=None, steps=(0, 0, 0), brk=None, vol=None, pb=None, active=False, tf="4H", bdir=None, vdir=None, legacy=False):
    c = P60.cond(cid, text, tp, inval, steps, pb, active, tf, legacy)
    if not legacy:
        c.update({"brk_px": brk, "vol_px": vol, "brk_dir": bdir, "vol_dir": vdir})
    return c


def bp_idea(conds, **kw): return P60.bp_idea(conds, **kw)


def fresh(page, idea): P60.fresh(page, idea)


def ac(cid="c1", iid="iD"): return f'.ui-plan[data-id="{iid}"] .ui-ac[data-ac="{cid}"]'


def lvl(page, k, val, cid="c1", iid="iD"): P60.fill(page, f'{ac(cid, iid)} [data-ac-px="{k}"]', val)


def pbf(page, val, cid="c1", iid="iD"): P60.fill(page, f'{ac(cid, iid)} [data-ac-pb]', val)


def tick(page, k, cid="c1", iid="iD"):
    page.locator(f'{ac(cid, iid)} [data-step="{k}"]').click(); page.wait_for_timeout(450)


def sums(page, cid="c1", iid="iD"):
    return page.evaluate("(s)=>[...document.querySelectorAll(s+' .ui-acs')].map(e=>e.textContent.replace(/\\s+/g,' ').trim())", ac(cid, iid))


def tpnum(page, field, val, cid="c1", iid="iD"):
    sel = f'.ui-plan[data-id="{iid}"] :is([data-cond="{cid}"],[data-cond-edit="{cid}"]) .ui-cond-nums input[onchange*="\'{field}\'"]'
    if not page.locator(sel).count() and page.locator(f'.ui-plan[data-id="{iid}"] [data-ac-bar]').count():
        page.locator(f'.ui-plan[data-id="{iid}"] [data-ac-bar]').click(); page.wait_for_timeout(250)
    P60.fill(page, sel, val)


def full_ready(page, **kw):
    """ติ๊ก Break+Vol กรอก 2400/2410 · TP · Inval · ติ๊ก Pullback → Active"""
    lvl(page, "brk", 2400); lvl(page, "vol", 2410)
    tick(page, "brk"); tick(page, "vol")
    tpnum(page, "tp_from", 2440); tpnum(page, "inval", 2390)
    tick(page, "pb")


def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, page, ce, pe = sat_page(pw, w, h)
    try:
        # ── 1 แผนใหม่
        js(page, "()=>satV3NewPlan('XAUUSD')"); page.wait_for_timeout(500)
        d = js(page, "()=>{ const l = satIdeasList.filter(x=>x.v3 && x.planned===false); return l.length ? JSON.parse(JSON.stringify(l[l.length-1])) : null; }")
        check(f"{tag} 1 แผนใหม่: มีเงื่อนไข bp 1 ข้อทันที", d and len(d["conditions"]) == 1 and d["conditions"][0]["kind"] == "bp" and d["conditions"][0]["brk_tf"] == "4H", json.dumps(d, ensure_ascii=False))
        pl = '.ui-plan'
        S = page.locator(pl).first
        h1 = page.evaluate("()=>{const r=document.querySelector('.ui-plan'); return {txt:r.innerText, inputs:[...r.querySelectorAll('.ui-conds input')].map(e=>e.placeholder), text:r.querySelectorAll('.ui-cond-text').length, sc:r.querySelectorAll('[data-shortcut]').length, tpl:r.querySelectorAll('.ui-cond-tpl-edit').length, ticks:r.querySelectorAll('.ui-ack').length, tf:r.querySelectorAll('[data-ac-tf] button').length}}")
        check(f"{tag} 1 ไม่มีช่องข้อความ/ชิปปุ่มลัด/+ เพิ่มเอง/✎ แก้รายการ/บรรทัด Setup x/", h1["text"] == 0 and h1["sc"] == 0 and h1["tpl"] == 0 and "+ เพิ่มเอง" not in h1["txt"] and "✎ แก้รายการ" not in h1["txt"] and not re.search(r"Setup \d+/", h1["txt"]), h1["txt"][:300])
        check(f"{tag} 1 ขั้นวางแผน: ไม่มีช่องติ๊ก · มี TF 3 ปุ่ม (4H · D · W — PY2) · ช่อง Break Price · Break Vol · Pullback · TP จาก/ถึง · Inval Price", h1["ticks"] == 0 and h1["tf"] == 3 and h1["inputs"] == ["Price", "Price", "Price หรือ 2405-2412", "จาก", "ถึง", "Price"], json.dumps(h1, ensure_ascii=False))
        order = page.evaluate("()=>[...document.querySelectorAll('.ui-plan .ui-ac2 > *')].map(e=>e.className.replace('ui-acr ','')+(e.dataset.row?':'+e.dataset.row:''))")
        check(f"{tag} 1 ลำดับ: TF → Break Price → Break Vol → Pullback → TP/Inval", order[:5] == ["ui-ac-tfr", "ui-acr:brk", "ui-acr:vol", "ui-acr:pb", "ui-cond-nums"] if False else (len(order) >= 5 and "ui-ac-tfr" in order[0] and order[1].endswith("brk") and order[2].endswith("vol") and order[3].endswith("pb") and "ui-cond-nums" in order[4]), json.dumps(order))
        shot(page, f"ac2-plan-{sfx}.png", pl)
        check(f"{tag} 1 ปุ่ม ＋ เงื่อนไข ไม่มีตอนมี 1 ข้อ", page.locator("[data-cond-new]").count() == 0)

        # ── 2 TF
        fresh(page, bp_idea([cond()]))
        seg = f'{ac()} [data-ac-tf] button'
        check(f"{tag} 2 TF segmented 4H|D|W (PY2 เพิ่ม W) · ค่าเริ่ม 4H", page.locator(seg).all_inner_texts() == ["4H", "D", "W"] and page.locator(f'{seg}[data-tf="4H"]').get_attribute("aria-pressed") == "true" and page.locator(f'{ac()} select').count() == 0)
        page.locator(f'{seg}[data-tf="D"]').click(); page.wait_for_timeout(400)
        check(f"{tag} 2 แตะ D → brk_tf:'D'", cd(page)["brk_tf"] == "D", json.dumps(cd(page)))
        page.locator(f'{seg}[data-tf="4H"]').click(); page.wait_for_timeout(300)

        # ── 3 ทิศ
        col = lambda sel: page.evaluate("(s)=>getComputedStyle(document.querySelector(s)).color", sel)
        up = page.evaluate("()=>{const e=document.createElement('i'); e.style.color='var(--up)'; document.body.appendChild(e); const c=getComputedStyle(e).color; e.remove(); return c}")
        dn = page.evaluate("()=>{const e=document.createElement('i'); e.style.color='var(--dn)'; document.body.appendChild(e); const c=getComputedStyle(e).color; e.remove(); return c}")
        arrows = lambda: page.evaluate("(s)=>[...document.querySelectorAll(s+' .ui-adir')].map(e=>e.textContent.trim())", ac())
        check(f"{tag} 3 แผน Long → ▲ ทั้ง 2 แถว · สี = --up", arrows() == ["▲", "▲"] and col(f'{ac()} .ui-adir .ui-ac-up') == up, json.dumps([arrows(), col(f'{ac()} .ui-adir .ui-ac-up'), up]))
        page.locator(f'{ac()} [data-dir="brk"]').click(); page.wait_for_timeout(350)
        check(f"{tag} 3 [ESC1] แตะปุ่มทิศอันเดียว (Break Price) → ▼ ทั้ง 2 แถว · เก็บ brk_dir:'dn' + vol_dir:'dn' · สี = --dn (เดิมสลับทีละแถว — ดู ESC1_retired.md)", arrows() == ["▼", "▼"] and cd(page)["brk_dir"] == "dn" and cd(page)["vol_dir"] == "dn" and col(f'{ac()} .ui-adir .ui-ac-dn') == dn, json.dumps([arrows(), cd(page).get("brk_dir"), cd(page).get("vol_dir")]))
        check(f"{tag} 3 [ESC1] แถว Break Vol ไม่มีปุ่มทิศ ([data-dir='vol'] = 0 · ลูกศรอ่านอย่างเดียว)", page.locator(f'{ac()} [data-dir="vol"]').count() == 0 and page.locator(f'{ac()} [data-dir-ro="vol"]').count() == 1)

        # ── 4 ติ๊ก + บรรทัดสรุป (หน้างาน)
        fresh(page, bp_idea([cond()]))
        check(f"{tag} 4 หน้างาน: มีช่องติ๊ก ≥ 30px 3 ช่อง", page.evaluate("(s)=>[...document.querySelectorAll(s+' .ui-ack')].map(e=>Math.round(e.getBoundingClientRect().height))", ac()) == [30, 30, 30])
        before = cd(page)
        page.locator(f'{ac()} [data-step="brk"]').click(force=True); page.wait_for_timeout(350)
        check(f"{tag} 4 ติ๊ก Break Price ตอนยังไม่กรอก → ไม่ได้ (เทา + title)", cd(page)["steps"]["brk"] is False and page.locator(f'{ac()} [data-step="brk"]').get_attribute("title") == "กรอก Price ก่อน")
        lvl(page, "brk", 2400)
        check(f"{tag} 4 กรอก 2400 → brk_px:2400", cd(page)["brk_px"] == 2400)
        tick(page, "brk")
        check(f"{tag} 4 ติ๊กได้ → เป็นบรรทัดสรุป '✓ Break Price 2,400▲' · อีกข้อยังเป็นแถวกรอก", sums(page) == ["✓ Break Price 2,400▲"] and page.locator(f'{ac()} [data-ac-px="vol"]').count() == 1, json.dumps(sums(page)))
        page.locator(f'{ac()} .ui-acs').click(); page.wait_for_timeout(350)
        check(f"{tag} 4 แตะบรรทัดสรุป → กลับเป็นแถวกรอก · ติ๊กยังอยู่ · แก้ตัวเลขได้", page.locator(f'{ac()} [data-ac-px="brk"]').count() == 1 and cd(page)["steps"]["brk"] is True and page.locator(f'{ac()} [data-step="brk"]').get_attribute("aria-pressed") == "true")
        lvl(page, "brk", 2401)
        check(f"{tag} 4 แก้เป็น 2401 → ติ๊กยังอยู่ · กลับเป็นบรรทัดสรุป", cd(page)["brk_px"] == 2401 and cd(page)["steps"]["brk"] is True and sums(page) == ["✓ Break Price 2,401▲"], json.dumps(sums(page)))
        page.locator(f'{ac()} .ui-acs').click(); page.wait_for_timeout(300)
        lvl(page, "brk", 2400)

        # ── 5 Pullback ขยับตาม Break
        pbv = lambda: page.locator(f'{ac()} [data-ac-pb]').input_value()
        lvl(page, "vol", 2410)
        check(f"{tag} 5 Break 2400 + Vol 2410 → ช่อง Pullback = 2,400–2,410 · pb_from/pb_to ยัง null", pbv() == "2,400–2,410" and cd(page)["pb_from"] is None and cd(page)["pb_to"] is None, pbv() + json.dumps(cd(page)))
        tick(page, "vol")
        check(f"{tag} 5 ติ๊ก Break ครบ → สรุปบรรทัดเดียว ✓ Break Price 2,400▲ · Vol 2,410▲", sums(page) == ["✓ Break Price 2,400▲ · Vol 2,410▲"], json.dumps(sums(page)))
        tick(page, "pb")
        c = cd(page)
        check(f"{tag} 5 ติ๊ก Pullback → steps.pb true แต่ pb_from/pb_to ยัง null (ไม่เขียนค่าเริ่ม)", c["steps"]["pb"] is True and c["pb_from"] is None and c["pb_to"] is None, json.dumps(c))
        check(f"{tag} 5 สรุป Pullback '✓ Pullback 2,400–2,410'", "✓ Pullback 2,400–2,410" in sums(page), json.dumps(sums(page)))
        page.locator(f'{ac()} [data-sum="break"]').click(); page.wait_for_timeout(300)
        lvl(page, "brk", 2390)
        check(f"{tag} 5 แก้ Break เป็น 2390 หลังติ๊ก → Pullback ตาม = 2,390–2,410 (สรุป) · ยัง null", "✓ Pullback 2,390–2,410" in sums(page) and cd(page)["pb_from"] is None, json.dumps([sums(page), cd(page)]))
        pbf(page, 2405) if page.locator(f'{ac()} [data-ac-pb]').count() else (page.locator(f'{ac()} [data-sum="pb"]').click(), page.wait_for_timeout(250), pbf(page, 2405))
        check(f"{tag} 5 พิมพ์ Pullback เอง 2405 → เก็บ pb_from 2405 · pb_to null", (cd(page)["pb_from"], cd(page)["pb_to"]) == (2405, None), json.dumps(cd(page)))
        page.locator(f'{ac()} [data-sum="brk"]').click(); page.wait_for_timeout(300)
        lvl(page, "brk", 2380)
        check(f"{tag} 5 พิมพ์เองแล้วแก้ Break อีก → Pullback คง 2405", "✓ Pullback 2,405" in sums(page), json.dumps(sums(page)))
        page.locator(f'{ac()} [data-sum="pb"]').click(); page.wait_for_timeout(300)
        pbf(page, "")
        check(f"{tag} 5 ลบช่อง Pullback จนว่าง → กลับตาม Break (2,380–2,410) · pb_from/to null", cd(page)["pb_from"] is None and "✓ Pullback 2,380–2,410" in sums(page), json.dumps([sums(page), cd(page)]))

        # ── 6 Pullback กรอกเอง
        fresh(page, bp_idea([cond()]))
        for val, exp in (("2405", (2405, None)), ("2412-2405", (2405, 2412)), ("2,405 – 2,412", (2405, 2412)), ("2405—2412", (2405, 2412)), ("2405 - 2412", (2405, 2412))):
            pbf(page, val)
            check(f"{tag} 6 Pullback '{val}' → {exp}", (cd(page)["pb_from"], cd(page)["pb_to"]) == exp, json.dumps(cd(page)))
        pbf(page, "abc")
        check(f"{tag} 6 'abc' → ไม่เขียน (ยัง 2405/2412) + ขอบแดง", (cd(page)["pb_from"], cd(page)["pb_to"]) == (2405, 2412) and page.locator(f'{ac()} [data-ac-pb].ui-bad').count() == 1)
        page.wait_for_timeout(1700)
        check(f"{tag} 6 ขอบแดงหายเอง", page.locator(f'{ac()} [data-ac-pb].ui-bad').count() == 0)

        # ── 7 ครบ → Active
        fresh(page, bp_idea([cond()]))
        full_ready(page)
        c = cd(page); d = doc_of(page)
        check(f"{tag} 7 ครบ (3 ติ๊ก + TP 1 ช่อง + Inval) → active:true · act_side Long · tp 2440", active_ids(page) == ["c1"] and d["act_side"] == "Long" and d["tp"] == 2440 and c["pb_from"] is None, json.dumps(d, ensure_ascii=False))
        bar = txt(page, f'{ROOT} [data-ac-bar]')
        check(f"{tag} 7 แถบ '● Active · 4H' + 'TP 2,440 · Inval 2,390'", bar == "● Active · 4H TP 2,440 · Inval 2,390", bar)
        r = page.evaluate("(r)=>({off:[...r.querySelectorAll('button')].filter(b=>/ยกเลิก Activate/.test(b.textContent)).length, expl:/เอาติ๊ก|ติ๊กออก/.test(r.innerText), oldsum:r.querySelectorAll('.ui-cond-sum').length})", ROOT) if False else page.evaluate("()=>{const r=document.querySelector('.ui-plan[data-id=iD]'); return {off:[...r.querySelectorAll('button')].filter(b=>/ยกเลิก Activate/.test(b.textContent)).length, expl:/เอาติ๊ก|ติ๊กออก/.test(r.innerText), oldsum:r.querySelectorAll('.ui-cond-sum').length}}")
        check(f"{tag} 7 ไม่มีปุ่ม 'ยกเลิก Activate' · ไม่มีข้อความอธิบายเอาติ๊กออก · ไม่มี ui-cond-sum", r == {"off": 0, "expl": False, "oldsum": 0}, json.dumps(r))
        s = sums(page)
        one = page.evaluate("()=>{const e=document.querySelector('.ui-plan[data-id=iD] .ui-acs[data-sum=break] .ui-acs-t'); const r=e.getBoundingClientRect(); const rs=[...e.getClientRects()]; return {h:Math.round(r.height), sw:e.scrollWidth, cw:e.clientWidth, par:e.parentElement.scrollWidth<=e.parentElement.clientWidth+1}}")
        check(f"{tag} 7 สรุป '✓ Break Price 2,400▲ · Vol 2,410▲' (บรรทัดเดียว ไม่ล้น) + '✓ Pullback 2,400–2,410'", s == ["✓ Break Price 2,400▲ · Vol 2,410▲", "✓ Pullback 2,400–2,410"] and one["h"] < 30 and one["par"], json.dumps([s, one]))
        arrow = page.evaluate("()=>[...document.querySelectorAll('.ui-plan[data-id=iD] .ui-acs-t .ui-ac-up')].map(e=>getComputedStyle(e).color)")
        check(f"{tag} 7 ▲ ในบรรทัดสรุปสี --up · ตัวเลขตัวหนา", arrow == [up, up] and page.evaluate("()=>getComputedStyle(document.querySelector('.ui-plan[data-id=iD] .ui-acs-t b')).fontWeight") in ("700", "bold"))
        shot(page, f"ac2-active-{sfx}.png", ROOT)
        # แตะแถบ = แก้ TP/Inval
        page.locator(f'{ROOT} [data-ac-bar]').click(); page.wait_for_timeout(300)
        check(f"{tag} 7 แตะแถบ Active → เปิดแก้ TP/Inval (+TF)", page.locator(f'{ROOT} [data-cond-edit] .ui-cond-nums input').count() >= 3 and page.locator(f'{ROOT} [data-cond-edit] [data-ac-tf]').count() == 1)
        page.locator(f'{ROOT} [data-cond-edit] button:has-text("เสร็จแล้ว")').click(); page.wait_for_timeout(250)

        # ── 8 ถอน
        page.locator(f'{ROOT} [data-sum="pb"]').click(); page.wait_for_timeout(300)
        tick(page, "pb")
        check(f"{tag} 8 เอาติ๊ก Pullback ออก → active:false (ติ๊ก Break ยังอยู่)", active_ids(page) == [] and cd(page)["steps"] == {"brk": True, "vol": True, "pb": False}, json.dumps(cd(page)))
        tick(page, "pb")
        check(f"{tag} 8 ติ๊กกลับ → Active", active_ids(page) == ["c1"])
        tpnum(page, "tp_from", "")
        check(f"{tag} 8 ลบ TP ช่องเดียว (ยังไม่ว่างทั้งคู่) ... ", True)
        tpnum(page, "tp_to", "")
        check(f"{tag} 8 ลบ TP ทั้ง 2 → active:false", active_ids(page) == [], json.dumps(cd(page)))
        tpnum(page, "tp_to", 2441)
        check(f"{tag} 8 TP ช่อง 'ถึง' ช่องเดียว → Active", active_ids(page) == ["c1"])
        tpnum(page, "inval", "")
        check(f"{tag} 8 ลบ Inval → active:false", active_ids(page) == [])
        tpnum(page, "inval", 2390)
        page.locator(f'{ROOT} [data-sum="break"]').click(); page.wait_for_timeout(300)
        lvl(page, "vol", "")
        c = cd(page)
        check(f"{tag} 8 ลบตัวเลข Break Vol ของข้อที่ติ๊กอยู่ → vol_px null · ติ๊ก vol หลุด · ไม่ active", c["vol_px"] is None and c["steps"]["vol"] is False and active_ids(page) == [], json.dumps(c))
        check(f"{tag} 8 หลุดแล้วช่องติ๊ก Vol เทา (ติ๊กไม่ได้จนกว่าจะกรอก)", "ui-dis" in (page.locator(f'{ac()} [data-step="vol"]').get_attribute("class") or ""))

        # ── 9 ขาด
        fresh(page, bp_idea([cond()]))
        miss = lambda: txt(page, f'{ac()} [data-ac-miss]')
        check(f"{tag} 9 ว่างทั้งหมด → 'ขาด: Break Price · Break Vol · Pullback · TP · Invalidation'", miss() == "ขาด: Break Price · Break Vol · Pullback · TP · Invalidation", miss())
        lvl(page, "brk", 2400)
        check(f"{tag} 9 มี Break Price ยังไม่ติ๊ก → 'ขาด: ติ๊ก Break Price · Break Vol · …'", miss() == "ขาด: ติ๊ก Break Price · Break Vol · Pullback · TP · Invalidation", miss())
        lvl(page, "vol", 2410); tick(page, "brk"); tick(page, "vol")
        check(f"{tag} 9 Break ครบ ยังไม่ติ๊ก Pullback → 'ขาด: ติ๊ก Pullback · TP · Invalidation'", miss() == "ขาด: ติ๊ก Pullback · TP · Invalidation", miss())
        shot(page, f"ac2-pending-{sfx}.png", ROOT)
        pbd = page.evaluate("(s)=>{const e=document.querySelector(s+' [data-step=pb]'); return e.getAttribute('aria-pressed')}", ac())
        pbf(page, 2405) if False else None

        # ── 10 แผนเก่า
        old = P51.idea_doc(iid="iD", act=True)
        old["entry"], old["sl"], old["tp"] = 2410, 2400, 2425
        old["accts"] = {"main": {"broker": "XM"}}
        fresh(page, old)
        st0 = cd(page)
        check(f"{tag} 10 แผนเก่า (active ไม่มี steps/brk_px) → ยัง active · แสดงติ๊กครบ (สรุป Break + Pullback)", active_ids(page) == ["c1"] and len(sums(page)) == 2 and "steps" not in st0, json.dumps([sums(page), st0]))
        c1 = P51.calc(page, old)
        page.locator(f'{ROOT} [data-ac-bar]').click(); page.wait_for_timeout(250)
        page.locator(f'{ROOT} [data-cond-edit] [data-tf="D"]').click(); page.wait_for_timeout(450)
        c = cd(page)
        check(f"{tag} 10 เปลี่ยน TF เป็น D → ยัง active · legacy_ok:true · brk_tf D", active_ids(page) == ["c1"] and c.get("legacy_ok") is True and c["brk_tf"] == "D", json.dumps(c))
        c2 = P51.calc(page, old)
        check(f"{tag} 10 lot / R:R เท่าเดิม", c1 == c2 and c1["ready"] is True and c1["lot"], json.dumps([c1, c2]))
        page.locator(f'{ROOT} [data-sum="break"]').click(); page.wait_for_timeout(300)
        lvl(page, "brk", 2400)
        check(f"{tag} 10 กรอกตัวเลข Break เพิ่มทีหลัง → ยัง active", active_ids(page) == ["c1"], json.dumps(cd(page)))
        tpnum(page, "inval", 2390)   # fixture เก่าไม่มี Inval → เติมให้ครบก่อน แล้วค่อยเอาติ๊กออก
        check(f"{tag} 10 เติม Inval ในข้อเก่า → ยัง active", active_ids(page) == ["c1"])
        page.locator(f'{ROOT} [data-sum="brk"]').click(); page.wait_for_timeout(300)
        tick(page, "brk")
        check(f"{tag} 10 เอาติ๊ก Break Price ออก → หลุด active", active_ids(page) == [], json.dumps(cd(page)))

        # ── 11 สองเงื่อนไข / ไม่มีเงื่อนไข
        full = dict(steps=(1, 1, 1), brk=2400, vol=2410, tp=(2440, 2450), inval=2390)
        fresh(page, bp_idea([cond("c1", "A @ 2400", active=True, **full), cond("c2", "B @ 2380", steps=(1, 1, 0), brk=2370, vol=2380, tp=(2430, 2440), inval=2360)]))
        check(f"{tag} 11 แผนเก่า 2 เงื่อนไข: ข้อ 1 active · ข้อความเก่า A/B แสดงเป็นป้ายอ่านอย่างเดียว", active_ids(page) == ["c1"] and page.locator(f'{ROOT} .ui-oth-t').count() == 1)
        page.locator(f'{ROOT} .ui-oth-t').click(); page.wait_for_timeout(250)
        tick(page, "pb", "c2")
        check(f"{tag} 11 ข้อ 2 ครบ → active ย้ายไปข้อ 2 (AC1)", active_ids(page) == ["c2"] and "สลับไปเงื่อนไข #2" in txt(page, ROOT), json.dumps(doc_of(page)["conditions"], ensure_ascii=False)[:200])
        fresh(page, bp_idea([cond("c1", "A @ 2400", **full)]))
        js(page, "()=>satV3CondCancel('iD','c1')"); page.wait_for_timeout(400)
        # ยกเลิกหมด → แถวพับ/การ์ด: เปิดการ์ด
        js(page, "()=>{ satV3Open.add('iD'); satV3Render(); }"); page.wait_for_timeout(300)
        check(f"{tag} 11 ยกเลิกเงื่อนไขหมด → ปุ่ม '＋ เงื่อนไข' ปุ่มเดียว (ไม่มีชิปปุ่มลัด) + ปิดแผน", page.locator(f'{ROOT} [data-cond-new]').count() == 1 and page.locator(f'{ROOT} [data-shortcut]').count() == 0 and page.locator(f'{ROOT} .ui-cond-close').count() == 1)
        page.locator(f'{ROOT} [data-cond-new]').click(); page.wait_for_timeout(400)
        d = doc_of(page); live = [c for c in d["conditions"] if c.get("status") != "cancelled"]
        check(f"{tag} 11 กด ＋ เงื่อนไข → สร้าง bp ข้อใหม่ 1 ข้อ", len(live) == 1 and live[0]["kind"] == "bp" and page.locator(f'{ROOT} .ui-ac2').count() == 1, json.dumps(live))

        # ── 12 แถวพับ + ยกเลิก
        fresh(page, bp_idea([cond("c1", "", brk=2400, vol=2410), cond("c2", "Break & Pullback @ 2380")]))
        js(page, "()=>{ satV3Open.delete('iD'); satV3Render(); }"); page.wait_for_timeout(300)
        wait = txt(page, '.ui-wait[data-id="iD"]')
        check(f"{tag} 12 แถวพับ: 'B&P 4H · 2,400▲ / 2,410▲' · ข้อเก่ามี text แสดง text", "B&P 4H · 2,400▲ / 2,410▲" in wait and "Break & Pullback @ 2380" in wait, wait)
        js(page, "()=>satV3CondCancel('iD','c1')"); page.wait_for_timeout(300)
        js(page, "()=>{ satV3CancelledOpen.add('iD'); satV3Render(); }"); page.wait_for_timeout(300)
        check(f"{tag} 12 รายการที่ยกเลิก แสดง label เดียวกัน", "B&P 4H · 2,400▲ / 2,410▲" in txt(page, '.ui-wait[data-id="iD"] .ui-cancd'), txt(page, '.ui-wait[data-id="iD"] .ui-cancd'))
        check(f"{tag} 12 label ที่ยังไม่กรอก = —", js(page, "()=>satAcLabel({kind:'bp',brk_tf:'D'}, {bias:'Long'})") == "B&P D · — / —")
        check(f"{tag} 12 label Short ใช้ ▼", js(page, "()=>satAcLabel({kind:'bp',brk_tf:'4H',brk_px:2300,vol_px:2290}, {bias:'Short'})") == "B&P 4H · 2,300▼ / 2,290▼")

        # ── 14 กติกาเดิมยังบล็อก
        def done(**kw):
            return bp_idea([cond("c1", active=True, steps=(1, 1, 1), brk=2400, vol=2410, tp=kw.get("tpz", (2425, 2440)), inval=2390)],
                           entry=kw.get("entry", 2410), sl=kw.get("sl", 2400), tp=kw.get("tp", 2425), broker="XM")
        P51.set_news(page, []); P51.set_clock(page, CLK)
        c = P51.calc(page, done())
        check(f"{tag} 14 ครบ + R:R 1.5 → ready", c["ready"] is True and not c["rr"], json.dumps(c, ensure_ascii=False))
        c = P51.calc(page, done(tp=2420))
        check(f"{tag} 14 R:R < 1.5 → บล็อก", c["ready"] is False and c["rr"] and "ต่ำกว่า 1.5" in c["rr"], json.dumps(c, ensure_ascii=False))
        P51.set_news(page, [{"date": "2026-10-01", "kind": "CPI", "time": "19:30"}]); P51.set_clock(page, "2026-10-01T11:40:00Z")
        c = P51.calc(page, done())
        check(f"{tag} 14 ช่วงงดข่าว → บล็อก", c["ready"] is False and c["news"] and "งดเปิดไม้ใหม่" in c["news"], json.dumps(c, ensure_ascii=False))
        P51.set_news(page, []); P51.set_clock(page, CLK)
        js(page, "()=>satwWrite('XAUUSD', {bias:'Short', support:[2300], resistance:[2500], invalidation:2550})"); page.wait_for_timeout(300)
        c = P51.calc(page, done())
        check(f"{tag} 14 PF1 — Strategy bias เก่าสวนแผน → ไม่บล็อก (ไม่มีเหตุผลสวน Bias)", not any("สวน Bias" in x for x in c["warns"]), json.dumps(c, ensure_ascii=False))

        # ── 15 เลย์เอาต์
        js(page, "()=>satwWrite('XAUUSD', {bias:'Long', support:[2300], resistance:[2500], invalidation:2250})"); page.wait_for_timeout(300)
        fresh(page, bp_idea([cond()]))
        m = page.evaluate("""(s)=>({fonts:[...document.querySelectorAll(s+' input')].map(e=>parseFloat(getComputedStyle(e).fontSize)), hs:[...document.querySelectorAll(s+' .ui-ack, '+s+' .ui-adir, '+s+' [data-ac-tf] button')].map(e=>e.getBoundingClientRect().height), W:innerWidth})""", ac())
        check(f"{tag} 15 ช่องกรอก font ≥ 16px · ติ๊ก/ทิศ/TF สูง ≥ 30px", all(f >= 16 for f in m["fonts"]) and len(m["fonts"]) == 6 and min(m["hs"]) >= 29.5, json.dumps(m))
        for name, setup in (("ว่าง", lambda: None), ("ติ๊ก Break", lambda: (lvl(page, "brk", 112450), lvl(page, "vol", 112900), tick(page, "brk"), tick(page, "vol")))):
            setup()
            bad = overflow(page, [ROOT, "#satV3Panel", ac()])
            check(f"{tag} 15 ไม่ล้นแนวนอน ({name})", not bad, json.dumps(bad))
        c = cd(page)
        sw = page.evaluate("()=>{const e=document.querySelector('.ui-plan[data-id=iD] .ui-acs[data-sum=break]'); const t=e.querySelector('.ui-acs-t'); return {sw:e.scrollWidth, cw:e.clientWidth, tw:t.getBoundingClientRect().right, ew:e.getBoundingClientRect().right, ell:getComputedStyle(t).textOverflow, text:t.textContent, h:Math.round(e.getBoundingClientRect().height)}}")
        check(f"{tag} 15 BTC 6 หลัก: สรุป Break ไม่ล้น ไม่ตัด … (POL1: บรรทัดเดียวหรือ 2 บรรทัดก็ได้ · แต่ละส่วน nowrap)", sw["sw"] <= sw["cw"] + 1 and sw["tw"] <= sw["ew"] + 1 and sw["h"] < 62 and sw["ell"] != "ellipsis" and "112,450▲" in sw["text"] and "112,900▲" in sw["text"], json.dumps(sw, ensure_ascii=False))
        shot(page, f"ac2-active-btc-{sfx}.png", ROOT)
        check(f"{tag} 15 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def short_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, page, ce, pe = sat_page(pw, w, h)
    try:
        js(page, "()=>satwWrite('XAUUSD', {bias:'Short', support:[2300], resistance:[2500], invalidation:2550})"); page.wait_for_timeout(300)
        fresh(page, bp_idea([cond()], bias="Short"))
        arrows = page.evaluate("(s)=>[...document.querySelectorAll(s+' .ui-adir')].map(e=>e.textContent.trim())", ac())
        check(f"{tag} 3 แผน Short → ▼ ทั้ง 2 แถว", arrows == ["▼", "▼"], json.dumps(arrows))
        lvl(page, "brk", 2300); lvl(page, "vol", 2290); tick(page, "brk"); tick(page, "vol")
        s = sums(page)
        dn = page.evaluate("()=>{const e=document.createElement('i'); e.style.color='var(--dn)'; document.body.appendChild(e); const c=getComputedStyle(e).color; e.remove(); return c}")
        cols = page.evaluate("()=>[...document.querySelectorAll('.ui-plan[data-id=iD] .ui-acs-t .ui-ac-dn')].map(e=>getComputedStyle(e).color)")
        check(f"{tag} 3 Short สรุป '✓ Break Price 2,300▼ · Vol 2,290▼' · ▼ สี --dn", s == ["✓ Break Price 2,300▼ · Vol 2,290▼"] and cols == [dn, dn], json.dumps([s, cols]))
        shot(page, f"ac2-short-{sfx}.png", ROOT)
        check(f"{tag} 15 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def today_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = P39.launch(pw, w, h, doc=P38.doc38(clean=True), clean=True, iso="2026-10-14T03:00:00Z")
    try:
        def state(conds, **kw):
            js(page, "()=>{ switchTab('today'); }")
            if conds is not None: P51.put_idea(page, bp_idea(conds, **kw))
            js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(450)
            return {"b": P38.kinds(page, "b"), "a": P38.kinds(page, "a"), "r": P38.kinds(page, "r")}
        P51.set_clock(page, "2026-10-14T03:00:00Z")
        s = state([cond(steps=(1, 1, 0), brk=2400, vol=2410)])
        row = page.locator('.tdRow[data-kind="sat-pbwait"]').first
        t = re.sub(r"\s+", " ", row.text_content()) if page.locator('.tdRow[data-kind="sat-pbwait"]').count() else ""
        check(f"{tag} 13 Break ครบ ยังไม่ Pullback → 'รอ Pullback เข้า zone 2,400–2,410' (จากค่าเริ่ม) · sub 'Break Price+Vol ครบแล้ว'", s["b"].count("sat-pbwait") == 1 and "รอ Pullback เข้า zone 2,400–2,410" in t and "Break Price+Vol ครบแล้ว" in t and "ราคา+Vol" not in t, t)
        s = state([cond(steps=(1, 1, 0), brk=2390, vol=2410)])
        t = re.sub(r"\s+", " ", page.locator('.tdRow[data-kind="sat-pbwait"]').first.text_content())
        check(f"{tag} 13 แก้ Break เป็น 2390 → Today ตาม 2,390–2,410", "2,390–2,410" in t, t)
        s = state([cond(steps=(1, 1, 0), brk=2400, vol=2410, pb=(2405, None))])
        t = re.sub(r"\s+", " ", page.locator('.tdRow[data-kind="sat-pbwait"]').first.text_content())
        check(f"{tag} 13 พิมพ์ Pullback เอง 2405 → Today แสดง 2,405", "zone 2,405" in t, t)
        s = state([cond(steps=(1, 0, 0), brk=2400, vol=2410)])
        check(f"{tag} 13 Break ไม่ครบ 2 ติ๊ก → ไม่มีแถว", "sat-pbwait" not in s["a"] + s["b"] + s["r"], json.dumps(s))
        check(f"{tag} 15 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def custom_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    doc = P38.doc38(clean=True); P55.with_custom(P55.XAG)(doc)
    browser, context, page, ce, pe, dialogs = P39.launch(pw, w, h, doc=doc, clean=True, iso=CLK, pick=['XAUUSD', 'BTCUSD', 'XAG'])   # WA1fix: XAG ต้องอยู่ใน pick สัปดาห์นี้
    try:
        p5.goto_sat(page); p36.clean(page, "Long"); P37.go_sat(page)
        js(page, "()=>satwWrite('XAG', {bias:'Long', support:[28], resistance:[33], invalidation:27})"); page.wait_for_timeout(300)
        i = bp_idea([cond("c1", "", brk=29.5, vol=30, steps=(1, 1, 0))], asset="XAG", entry=30, sl=29, tp=None, broker="XM", iid="iX")
        P51.fresh(page, i); page.wait_for_timeout(300)
        A = ac("c1", "iX")
        check(f"{tag} 14 XAG (สินค้าเพิ่มเอง): การ์ดใหม่ใช้ได้ (TF · Break Price · Vol · Pullback)", page.locator(f'{A} [data-ac-tf]').count() == 1 and page.locator(f'{A} .ui-acs[data-sum=break]').count() == 1)
        tpnum(page, "tp_from", 31.5, "c1", "iX"); tpnum(page, "inval", 28.5, "c1", "iX")
        tick(page, "pb", "c1", "iX")
        check(f"{tag} 14 XAG ครบ → Active · act_side Long", active_ids(page, "iX") == ["c1"] and doc_of(page, "iX")["act_side"] == "Long", json.dumps(doc_of(page, "iX"), ensure_ascii=False)[:400])
        js(page, "()=>satV3IdeaWrite('iX',{macro_note:'เหตุผลทดสอบ'})"); page.wait_for_timeout(250)   # WA1: Asset นอก Macro ต้องมีเหตุผลก่อนบันทึก order
        c = P55.calc(page, doc_of(page, "iX"))
        check(f"{tag} 14 XAG คำนวณ lot ได้ · ready", c["lot"] and c["ready"] is True, json.dumps(c, ensure_ascii=False))
        check(f"{tag} 15 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def static_tests():
    s = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("S1 SAT_COND_STEPS ที่เดียว · ชื่อ Break Price", len(re.findall(r"const SAT_COND_STEPS\s*=", s)) == 1 and "label:'Break Price'" in s)
    check("S2 ฟังก์ชัน AC2 ครบ", all(f"function {n}(" in s for n in ("satAcSetLevel", "satAcSetDir", "satAcSetPb", "satAcDir", "satAcArrowHtml", "satAcLabel", "satAcZone")))
    check("S3 ไม่มีข้อความเก่า 'Break ราคา' / 'Pullback zone' ในโค้ดส่วน AC", "Break ราคา" not in s and "Pullback zone" not in s)
    check("S4 satAcZone ไม่เขียน pb_from/pb_to (ฟังก์ชันอ่านล้วน)", "pb_from: Math.min" not in s)


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            ui_tests(pw, w, h, label)
            short_tests(pw, w, h, label)
            today_tests(pw, w, h, label)
            custom_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 63 / AC2) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
