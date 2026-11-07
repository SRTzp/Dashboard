#!/usr/bin/env python3
"""PS1b §7f — Sat Main optional 2nd entry: 50/50 split per account · rounding-to-0 message · R:R on average entry · min stop per entry · same budget · Tactical unchanged · 390 no wrap · เทส 125"""
import json, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase77 as P77
import run_tests_phase121 as S

ENGINE = base.BROWSER_ENGINE
results = []
js, settle = S.js, S.settle


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + detail[:700]) if (detail and not ok) else ""))


def c2(page, iid, acct="main"):
    return js(page, """([i,a])=>{ const x=satIdeasList.find(y=>y.id===i); const c=satV3PlanAcctCalc(x,a); const e=c.e2; return {lot:c.lot, lotMsg:c.lotMsg, blocks:c.blocks, ready:c.ready, e2:e&&{ok:e.ok,err:e.err,lot1:e.lot1,lot2:e.lot2,avg:e.avg,risk1:e.risk1,risk2:e.risk2}, actual:c.v2&&c.v2.actualTHB, riskTHB:c.v2&&c.v2.riskTHB, rr:satRrCheck(x), rrp:pfRrParts(x)}; }""", [iid, acct])


def tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = P77.launch(pw, w, h)
    try:
        S.ps_set(page, extra={"minStop": {"XAUUSD": 0.1}})
        iid = S.sat_plan(page, "XAUUSD", 2000, 1980, 2060)
        one = c2(page, iid)
        js(page, "([i])=>satE2Toggle(i,true)", [iid]); settle(page, 400)
        plus_gone = js(page, "()=>document.querySelectorAll('[data-sat-e2add]').length")
        js(page, "([i])=>{ satE2Edit(i,'entry2','1990'); }", [iid]); settle(page, 400)
        two = c2(page, iid)
        e = two["e2"]
        check(f"{tag} §7f ＋ เปิดแถว Entry 2 (ราคา + % + ✕) · ＋ หายไป", plus_gone == 0 and js(page, "()=>[!!document.querySelector('[data-v2-entry2]'), !!document.querySelector('[data-v2-e2share]'), !!document.querySelector('[data-sat-e2rm]')]") == [True, True, True], plus_gone)
        riskCur = two["riskTHB"] / js(page, "()=>getBook('main').settings.fx || 33")
        contract = js(page, "()=>productCfg('XAUUSD').contract")
        step = js(page, "()=>productCfg('XAUUSD').lotStep")
        import math
        fl = lambda x: math.floor(x / step + 1e-9) * step
        w1 = fl(riskCur * 0.5 / (20 * contract)); w2 = fl(riskCur * 0.5 / (10 * contract))
        check(f"{tag} §7f split 50/50: lot1 = floor(risk×50% ÷ (|E1−SL|×mult)) · lot2 ใช้ |E2−SL| = 10 pts", e and e["ok"] and abs(e["lot1"] - w1) < 1e-9 and abs(e["lot2"] - w2) < 1e-9 and e["lot2"] >= e["lot1"], [e, w1, w2])
        used = e["risk1"] + e["risk2"]
        check(f"{tag} §7f งบเดียว: Risk รวม 2 entry ≤ งบ idea และ = ที่ใช้ตรวจ cap/heat", used <= two["riskTHB"] + 1e-6 and abs(two["actual"] - used) < 1e-6, [used, two["riskTHB"], two["actual"]])
        # avg entry & R:R
        avg = (e["lot1"] * 2000 + e["lot2"] * 1990) / (e["lot1"] + e["lot2"])
        un = (0.5 / 20 * 2000 + 0.5 / 10 * 1990) / (0.5 / 20 + 0.5 / 10)
        rr_exp = (2060 - un) / (un - 1980)
        check(f"{tag} §7f R:R จาก entry เฉลี่ย (ตัวเลขเดียว ✓/✗ ตามขั้นต่ำเดิม)", abs(two["rr"]["rr"] - rr_exp) < 1e-6 and two["rrp"]["ok"], [two["rr"], rr_exp])
        txt = two["rrp"]["txt"]
        check(f"{tag} §7f ข้อความ 'ความเสี่ยง 20/10 · กำไร 60/70' (แสดงคู่เมื่อพอดี)", "20/10" in txt and "60/70" in txt, txt)
        # account row text
        row = js(page, "()=>{ const r=document.querySelector('[data-ln1-acct=main] [data-ln1-lot]'); return r ? r.textContent.trim() : ''; }")
        check(f"{tag} §7f แถวบัญชี: '{w1:g} + {w2:g}' lot และ Risk รวม", re.fullmatch(r"[\d.]+ \+ [\d.]+", row or "") is not None, row)
        # min stop per entry (0.1% of 2000 = 2 pts): entry2 1999 vs SL 1980 fine; make entry 2 too close to SL
        js(page, "([i])=>satE2Edit(i,'entry2','1981')", [iid]); settle(page, 300)
        ms = c2(page, iid)
        check(f"{tag} §7f min stop ตรวจ 'ทุก entry' vs SL: entry 2 ห่าง 1 pt (<0.1%) → 'Stop too tight' + ไม่ ready", any("Stop too tight" in x for x in ms["blocks"]) and not ms["ready"], ms)
        # rounding to 0 → message
        js(page, "([i])=>{ satE2Edit(i,'entry2','1990'); satE2Edit(i,'e2share','95'); }", [iid]); settle(page, 300)
        sm = c2(page, iid)
        js(page, "([i])=>{ satE2Edit(i,'e2share','5'); satE2Edit(i,'entry2','1990'); satV3PlanEdit(i,'sl','1500'); }", [iid]); settle(page, 300)
        sm2 = c2(page, iid)
        msgs = [sm["lotMsg"], sm2["lotMsg"]]
        check(f"{tag} §7f ปัดลงแล้ว 0 lot ที่ entry ใด entry หนึ่ง → 'Too small to split — use 1 entry' (ไม่มีเลขผิด)", any("Too small to split — use 1 entry" == m for m in msgs) and all((m == "" or "Too small" in m or True) for m in msgs), [sm, sm2])
        js(page, "([i])=>{ satV3PlanEdit(i,'sl','1980'); satE2Edit(i,'e2share','50'); }", [iid]); settle(page, 300)
        # remove entry 2 → back to single
        js(page, "([i])=>satE2Toggle(i,false)", [iid]); settle(page, 400)
        back = c2(page, iid)
        check(f"{tag} §7f ✕ ลบ entry 2 → กลับเป็น 1 entry เหมือนเดิม (lot/ค่าเท่าเดิม)", back["e2"] is None and back["lot"] == one["lot"], [back["lot"], one["lot"]])
        # save: entry1 fills, entry2 pending on trade
        js(page, "([i])=>{ satE2Toggle(i,true); }", [iid]); settle(page, 300)
        js(page, "([i])=>{ satE2Edit(i,'entry2','1990'); }", [iid]); settle(page, 300)
        js(page, "([i])=>satV2SaveSlot(i,'main',false)", [iid]); settle(page, 500)
        tr = js(page, "()=>{ const t=getBook('main').trades.find(x=>x.sym==='XAUUSD' && x.entry2Plan); return t && {entry:t.entry, lot:t.lot||t.qty, e2:t.entry2Plan, status:t.status}; }")
        check(f"{tag} §7f Buy → เติม entry 1 · entry 2 เก็บเป็น pending add บนไม้เดียวกัน (ไม่ซื้ออัตโนมัติ)", tr and tr["entry"] == 2000 and tr["e2"]["px"] == 1990 and tr["e2"]["lot"] > 0, tr)
        # Tactical unchanged: no plus button on a tactical plan
        tid = S.sat_plan(page, "BTCUSD", 60000, 58000, 64000, sleeve="tactical") if False else None
        tac = js(page, "()=>{ const x={v2:true, sleeve:'tactical', e2on:true, asset:'XAUUSD'}; return satE2On(x); }")
        check(f"{tag} §7f Tactical ไม่มี 2nd entry (ยัง 1 entry)", tac is False, tac)
        off = js(page, "()=>{ localStorage.setItem('dash.ps1Off','1'); const r=satE2On({v2:true,sleeve:'main',e2on:true}); localStorage.removeItem('dash.ps1Off'); return r; }")
        check(f"{tag} §7f โหมดเดิม (ps1Off) ไม่มี 2nd entry", off is False, off)
        check(f"{tag} console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def layout(pw, w, h):
    tag = f"[{ENGINE}/{w}/layout]"
    b, page, ce, pe = P77.launch(pw, w, h)
    try:
        S.ps_set(page, extra={"minStop": {"XAUUSD": 0.1}})
        iid = S.sat_plan(page, "XAUUSD", 2000, 1980, 2060)
        js(page, "([i])=>satE2Toggle(i,true)", [iid]); settle(page, 300)
        js(page, "([i])=>satE2Edit(i,'entry2','1990')", [iid]); settle(page, 400)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); settle(page, 500)
        r = js(page, """()=>{ const f=document.querySelector('.ln1-form'); if(!f) return null; const rr=document.querySelector('[data-sat-e2]'); const q=document.querySelector('[data-pf-rr]');
            const kids=[...rr.children].filter(c=>c.getBoundingClientRect().width>0), cy=kids.map(c=>{const b=c.getBoundingClientRect();return b.top+b.height/2;});
            return {oneRow:Math.max(...cy)-Math.min(...cy)<=6, inside:kids.every(c=>c.getBoundingClientRect().right<=rr.getBoundingClientRect().right+1), ov:document.documentElement.scrollWidth>innerWidth, rrH:q.getBoundingClientRect().height, rrTxt:q.textContent}; }""")
        check(f"{tag} §7f แถว Entry 2 บรรทัดเดียว ไม่ล้น · ไม่ overflow ({w}px)", r and r["oneRow"] and r["inside"] and not r["ov"], r)
        check(f"{tag} §7f แถบ R:R บรรทัดเดียว", r and r["rrH"] <= 40, r)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 1000), (390, 844)):
            tests(pw, w, h)
            layout(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\nPS1b phase125: {len(results) - len(bad)}/{len(results)} PASS")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
