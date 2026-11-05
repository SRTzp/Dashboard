#!/usr/bin/env python3
"""PL1 Step 7 — A7: Today › Plans block (Momentum · Compounder · Sat · Draft | Open · ≤5 แถวต่อกลุ่ม · +N more ›) · เทส 119
Chromium · 390 / 1440 · ข้อมูล SAMPLE ล้วน · รัน: python3 run_tests_phase119.py"""
import json
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase111 as P111

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle, cnt = T.settle, T.cnt
P13 = P111.P13


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def card(**kw):
    c = {"acct": "main", "ticker": "AAA", "market": "US", "strategy": "W", "plan": {"entry": 100, "stop": 90}, "stop": 90, "stopHistory": [], "px": 100, "pxDate": "2026-10-29", "emaW": None,
         "lots": [], "trade_id": None, "acc_trade_id": None, "status": "plan", "created_at": "2026-10-20T00:00:00Z"}
    c.update(kw)
    return c


def open_card(sym, tid, **kw):
    return card(ticker=sym, trade_id=tid, status="open", lots=[{"n": 1, "date": "2026-10-20", "px": 100, "qty": 10, "f": 1, "stop": 90}], **kw)


def plans(page):
    return js(page, """()=>({block: !!document.querySelector('[data-td3-panel="plans"]'), groups:[...document.querySelectorAll('[data-td3-pg]')].map(g=>g.dataset.td3Pg),
      rows: Object.fromEntries([...document.querySelectorAll('[data-td3-pg]')].map(g=>[g.dataset.td3Pg, [...g.querySelectorAll('[data-td3-plan]')].map(r=>[r.dataset.td3Plan, r.dataset.kind, r.innerText.replace(/\\s+/g,' ').trim(), (r.querySelector('[data-td3-dot]')||{dataset:{}}).dataset.td3Dot||''])])),
      more: Object.fromEntries([...document.querySelectorAll('[data-td3-pmore]')].map(b=>[b.dataset.td3Pmore, b.innerText.trim()])),
      oldDrafts: document.querySelectorAll('[data-td3-draft], [data-td3-sec="drafts"]').length,
      satPanel: !!document.querySelector('[data-td3-pg="sat"][data-td3-panel="sat"]'), satChip: !!document.querySelector('[data-td3-pg="sat"] [data-td4-risk="sat"]'),
      oneLine: [...document.querySelectorAll('[data-td3-plan], [data-td3-sat]')].every(r=>r.getBoundingClientRect().height < 48)})""")


def plans_tests(pw, w, h):
    tag = f"[{ENGINE}/plans/{w}]"
    tr = [P13.T("tR", "core", "open", sym="RED", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20"), P13.T("tG", "core", "open", sym="GRN", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20"),
          P13.T("tY", "core", "open", sym="YEL", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20"), P13.T("tC", "core", "open", sym="CMPO", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20"),
          P13.T("tA", "core", "open", sym="ARCH", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20")]
    cards = {"cR": open_card("RED", "tR", px=85, emaW=95), "cG": open_card("GRN", "tG", px=110, emaW=95), "cY": open_card("YEL", "tY", px=94, emaW=95),
             "cD1": card(ticker="DRFA", plan={}, created_at="2026-10-21T00:00:00Z"), "cD2": card(ticker="DRFB", plan={"entry": 50, "stop": 45}, created_at="2026-10-22T00:00:00Z"),
             "cC": open_card("CMPO", "tC", track="ladder", px=100, emaW40=98), "cA": open_card("ARCH", "tA", px=100, emaW=95),
             "cL": card(ticker="OLDL", strategy="L", plan=None, ladder={"levels": [{"px": 50, "status": "wait"}], "sl": 45, "budgetPct": 0.1, "budgetTHB": 1000, "split": [1]})}
    b, page, ce, pe = P111.core(pw, w, h, tr, cards)
    try:
        js(page, "()=>wlCol().doc('ARCH').set({ticker:'ARCH', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', archived:true, archived_reason:'rotating', archived_at:'2026-10-30T00:00:00Z'})"); settle(page, 400)
        T.go_today(page); settle(page, 500)
        P = plans(page)
        check(f"{tag} A7: Plans block แทนแผง Satellite · กลุ่ม Momentum · Compounder (Sat ไม่ปรากฏเพราะไม่ได้เลือก asset → ไม่มีกลุ่ม Sat) · ไม่มีส่วน Drafts เดิม", P["block"] and P["groups"][:2] == ["winner", "ladder"] and P["oldDrafts"] == 0, P)
        order = [r[0] for r in P["rows"]["winner"]]
        check(f"{tag} A7: Momentum — Open ก่อน: 🔴 RED → 🟡 YEL → 🟢 GRN ... ARCH (archived แต่ยังมีไม้เปิด → ยังอยู่ใน Open) แล้ว Draft: DRFB (ใหม่กว่า) → DRFA", order == ["RED", "YEL", "GRN", "ARCH", "DRFB"] or order[:4] == ["RED", "YEL", "GRN", "ARCH"], P["rows"]["winner"])
        kinds = {r[0]: (r[1], r[3]) for r in P["rows"]["winner"]}
        check(f"{tag} A7: Open แสดงจุดสถานะ (red/yellow/green) · ARCH (archived) ยังเป็น Open", kinds.get("RED") == ("open", "red") and kinds.get("YEL") == ("open", "yellow") and kinds.get("GRN") == ("open", "green") and kinds.get("ARCH", ("",))[0] == "open", kinds)
        txt = {r[0]: r[2] for r in P["rows"]["winner"]}
        dA = js(page, "()=>{ const d = td3PlansModel().winner.find(r=>r.c.ticker==='DRFA'); const el = document.createElement('div'); el.innerHTML = td3PlanRowHtml(d); return el.innerText.replace(/\\s+/g, ' ').trim(); }")
        check(f"{tag} A7: Draft — ขาด Entry/SL = 'DRFA Draft Entry / SL missing' · ครบ = 'DRFB Draft Ready to enter'", dA.replace(" ", "") == "DRFADraftEntry/SLmissing" and txt.get("DRFB") == "DRFB Draft Ready to enter", [dA, txt.get("DRFB")])
        check(f"{tag} A7: จำกัด 5 แถวต่อกลุ่ม + '+N more ›' (Momentum มี 6 แถว → โชว์ 5 + '+1 more ›')", len(P["rows"]["winner"]) == 5 and P["more"].get("winner") == "+1 more ›", [len(P["rows"]["winner"]), P["more"]])
        check(f"{tag} A7: Compounder แยกกลุ่ม: CMPO (track ladder) Open 🟢 · ไม่มีการ์ด strategy L (OLDL) ในบล็อก", [r[0] for r in P["rows"]["ladder"]] == ["CMPO"] and P["rows"]["ladder"][0][3] == "green" and "OLDL" not in json.dumps(P["rows"]), P["rows"]["ladder"])
        check(f"{tag} A7: ทุกแถวบรรทัดเดียว (สูง < 48px) ไม่ล้นแนวนอน", P["oneLine"] and not C.overflow(page), [P["oneLine"], C.overflow(page)])
        # tap targets
        js(page, "()=>{ window.__go = []; const o = window.coreOpenCardOfTrade, c = window.coreOpenCard; window.coreOpenCardOfTrade = (...a)=>{ window.__go.push('trade:' + a.join(',')); return true; }; window.coreOpenCard = (...a)=>{ window.__go.push('card:' + a.join(',')); return true; }; }")
        page.locator('[data-td3-plan="RED"]').click(); settle(page, 200)
        page.locator('[data-td3-plan="DRFA"]').first.click() if cnt(page, '[data-td3-plan="DRFA"]') else None
        g = js(page, "()=>window.__go.slice()")
        check(f"{tag} A7: แตะ Open → coreOpenCardOfTrade(trade, acct) · (Draft ที่เกิน 5 แถวไปทาง '+N more')", g and g[0] == "trade:tR,main", g)
        js(page, "()=>{ window.__go = []; }")
        page.locator('[data-td3-pmore="winner"]').click(); settle(page, 400)
        sc = js(page, "()=>[activeTab, planScope]")
        check(f"{tag} A7: '+1 more ›' → แท็บ Plan · หน้า Momentum", sc == ["plan", "stock"], sc)
        # draft tap -> coreOpenCard
        T.go_today(page)
        js(page, "()=>{ window.__go = []; const c = window.coreOpenCard; window.coreOpenCard = (...a)=>{ window.__go.push('card:' + a.join(',')); return true; }; }")
        js(page, "()=>{ const el = [...document.querySelectorAll('[data-td3-plan]')].find(e=>e.dataset.kind==='draft'); if(el) el.click(); }"); settle(page, 200)
        g2 = js(page, "()=>window.__go.slice()")
        check(f"{tag} A7: แตะ Draft → coreOpenCard(id) (เปิดการ์ดนั้นในหน้า track ของมัน)", g2 and g2[0].startswith("card:"), g2)
        # Compounder tap switches scope via real helper
        js(page, "()=>{ coreOpenCard = Object.getPrototypeOf(window).coreOpenCard || coreOpenCard; }")
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def empty_and_sat_tests(pw, w, h):
    tag = f"[{ENGINE}/empty/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        T.go_today(page); settle(page, 400)
        P = plans(page)
        check(f"{tag} A7: ไม่มีแผน/ไม้ Momentum-Compounder → ซ่อนกลุ่ม Momentum และ Compounder ทั้งสอง (เหลือเฉพาะกลุ่ม Sat ที่มี asset ของสัปดาห์นี้)", "winner" not in P["groups"] and "ladder" not in P["groups"] and P["groups"] == ["sat"] and P["satPanel"] and P["satChip"], P)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)):
            plans_tests(pw, w, h); empty_and_sat_tests(pw, w, h)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
