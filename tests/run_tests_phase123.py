#!/usr/bin/env python3
"""PS1b §8 Fast-track (save without Watchlist/thesis · auto-add · ONE badge · Today pin + countdown · overdue red · add-on block · clears when done · Sat unaffected)
+ §9 share notation #45 · เทส 123 · Chromium 390/1440"""
import json
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase4 as base
import run_tests_phase120 as B
import run_tests_phase107 as T

ENGINE = base.BROWSER_ENGINE
results = []
js, settle, P13 = C.js, T.settle, B.P13


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + detail[:700]) if (detail and not ok) else ""))


def clock(page, day):
    js(page, "([d])=>{ window.__ftDay = d; ftToday = ()=>window.__ftDay; }", [day])


def tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    tr = [P13.T("tR", "core", "open", sym="RED", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20")]
    cards = {"cR": B.open_card("RED", "tR", px=100)}
    b, page, ce, pe = C.launch2(pw, w, h, tr, cards, pin_winner=True)
    try:
        B.ps_on(page); clock(page, "2026-11-10")
        # 1 save without Watchlist / thesis / screening
        B.form(page, "ZZZ"); B.fill(page, 100, 90)
        line = js(page, "()=>{ const e=document.getElementById('cnFt'); return e && e.style.display!=='none' ? e.textContent : ''; }")
        btn = js(page, "()=>document.getElementById('cnSave').textContent")
        check(f"{tag} §8 ไม่อยู่ใน Watchlist/ไม่มี thesis → ไม่ใช่กล่องแดง Not ready · มีบรรทัดอำพัน Fast-track + ปุ่ม 'Save plan (homework due)'", "Fast-track — homework due in 3 days (thesis ① ④ + screening)" == line and btn == "Save plan (homework due)" and not B.save_dis(page), [line, btn, B.errtxt(page)])
        js(page, "()=>coreNewSave()"); settle(page, 800)
        sv = js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='ZZZ'); return c && {ft:c.plan.ft, ps1:!!c.plan.ps1}; }")
        check(f"{tag} §8 บันทึกได้: plan.ft = วันที่ + due = +3 วันปฏิทิน", sv and sv["ps1"] and sv["ft"] and sv["ft"]["due"] == "2026-11-13", sv)
        wl = js(page, "()=>{ const it=wlItemOf('ZZZ'); return it ? {ft:!!it.fasttrack, ob:!!it.onboarding} : null; }")
        check(f"{tag} §8 เพิ่มเข้า Watchlist อัตโนมัติ มี fasttrack flag · ยังไม่ผ่าน screening (Unscreened)", wl and wl["ft"] and not wl["ob"], wl)
        # badge: one badge, amber
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); render(); }"); settle(page, 400)
        bd = js(page, "()=>[...document.querySelectorAll('[data-core-card] [data-ft-badge]')].map(e=>[e.textContent.trim(), e.dataset.ftBadge, getComputedStyle(e).color])")
        check(f"{tag} §8 ป้ายเดียว '⚠ Homework' (อำพัน) บนการ์ดแผน · ไม่มีแท็ก Fast-track บนการ์ด", len(bd) == 1 and bd[0][0] == "⚠ Homework" and bd[0][1] == "due" and "Fast-track" not in js(page, "()=>document.querySelector('[data-core-card]')?.parentElement.innerText||''"), bd)
        # Today pin
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
        pin = js(page, "()=>{ const p=document.querySelector('[data-ft-pinrow]'); const w=document.querySelector('[data-td-wrap]'); return p ? [p.innerText.replace(/\\s+/g,' ').trim(), w.firstElementChild===p, !!p.querySelector('[data-ft-go]'), !p.querySelector('.x,[data-td4-remx]')] : null; }")
        check(f"{tag} §8 Today: ปักบนสุด 'Homework: ZZZ — thesis + screening · due in 3 days' + 'Do it ›' · ปิด/เลื่อนไม่ได้", pin and pin[1] and pin[2] and pin[3] and pin[0].startswith("Homework ZZZ 3d thesis + screening"), pin)   # PS1c §6: one row, chips, pin
        clock(page, "2026-11-12"); js(page, "()=>todayRefresh(true)"); settle(page, 400)
        p2 = js(page, "()=>document.querySelector('[data-ft-pinrow]')?.innerText.replace(/\\s+/g,' ').trim()")
        check(f"{tag} §8 นับถอยหลัง (นาฬิกาปลอม): วัน 2 → 'due in 1 day'", p2 and "ZZZ 1d" in p2, p2)
        # overdue
        clock(page, "2026-11-15"); js(page, "()=>todayRefresh(true)"); settle(page, 400)
        od = js(page, "()=>{ const p=document.querySelector('[data-ft-pinrow]'); return p ? [p.innerText.replace(/\\s+/g,' ').trim(), p.classList.contains('od')] : null; }")
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); render(); }"); settle(page, 300)
        bo = js(page, "()=>[...document.querySelectorAll('[data-core-card] [data-ft-badge]')].map(e=>e.textContent.trim())")
        check(f"{tag} §8 เกิน 3 วัน → 'OVERDUE 2 days' แดง · ป้าย '⚠ Overdue 2d'", od and "ZZZ overdue" in od[0] and od[1] and bo == ["⚠ Overdue 2d"], [od, bo])
        rem = js(page, "()=>{ const M=tdBuild(); return td4RemList(M).map(x=>x.t); }")
        check(f"{tag} §8 นับในแบนเนอร์ Unfinished today", any("Homework ZZZ overdue 2d" in t for t in rem), rem)
        # Watchlist row badge
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); settle(page, 500)
        wb = js(page, "()=>[...document.querySelectorAll('.wlR[data-sym=ZZZ] [data-ft-badge]')].map(e=>e.textContent.trim())")
        check(f"{tag} §8 แถว Watchlist มีป้ายเดียวกัน", wb == ["⚠ Overdue 2d"], wb)
        # add-on block (open position with ft)
        js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='RED'); c.plan = Object.assign({}, c.plan, {ft:{at:'2026-11-10T00:00:00Z', due:'2026-11-13'}}); }")
        blk = js(page, "()=>coreBlkAdd(coreCardsList.find(x=>x.ticker==='RED'), null)")
        check(f"{tag} §8 Add-on / pyramid ถูกบล็อก 'Do homework first' จนกว่า homework เสร็จ", blk == "Do homework first", blk)
        # done -> everything clears
        js(page, "()=>{ const it=wlItemOf('ZZZ'); it.my_thesis={why:'w',exit:'x'}; it.onboarding={at:'2026-11-11'}; render(); }"); settle(page, 300)
        js(page, "()=>{ const it2=wlItemOf('RED'); }")
        done = js(page, "()=>{ const r=coreCardsList.find(x=>x.ticker==='RED'); const z=ftState('ZZZ'); r.plan.ft=null; return [z, coreBlkAdd(r, getBook('main').trades.find(x=>x.id==='tR')), ftList().length]; }")
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 400)
        gone = js(page, "()=>[document.querySelectorAll('[data-ft-pin]').length, [...document.querySelectorAll('[data-ft-badge]')].filter(e=>e.checkVisibility()).length]")
        check(f"{tag} §8 เสร็จ (thesis ①④ + screening) → ป้าย/Today/บล็อกหายเอง", done[0] is None and done[1] != "Do homework first" and done[2] == 0 and gone == [0, 0], [done, gone])
        # journal tag
        js(page, "()=>{ const B=getBook('main'); B.trades.push({id:'tFT', sym:'ZZZ', port:'core', bias:'Long', status:'closed', fastTrack:true, entry:100, sl:90, qty:1, date:'2026-11-01', exitDate:'2026-11-02', exit:101, cur:'USD', mult:1}); saveBook('main'); }")
        tg = js(page, "()=>ftTradeTag({fastTrack:true})")
        check(f"{tag} §8 ไม้จากแผน Fast-track มีแท็ก 'Fast-track' ใน Journal (เฉพาะ trade)", "Fast-track" in tg and ftOffTag(page) == "", tg)
        # old plan without ft unaffected
        old = js(page, "()=>[ftState('RED'), ftBadge('RED')]")
        check(f"{tag} §8 แผน/ไม้เก่า (ไม่มี ft) ไม่มีป้าย ไม่โดนบล็อก", old == [None, ""], old)
        # §9
        B.form(page, "YYY"); js(page, "()=>{ const it=wlItemOf('YYY'); }")
        B.fill(page, 100, 90)
        sm = B.sumtxt(page)
        check(f"{tag} §9 สรุปแผนแสดง #จำนวน (ไม่มี 'sh'/'หุ้น'): {sm[:60]}", sm.startswith("#") and " sh" not in sm and "หุ้น" not in sm, sm)
        js(page, "()=>coreSheetClose()")
        check(f"{tag} console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def ftOffTag(page):
    return js(page, "()=>{ localStorage.setItem('dash.ps1Off','1'); const r=ftTradeTag({fastTrack:true})+ftBadge('ZZZ'); localStorage.removeItem('dash.ps1Off'); return r; }")


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 1000), (390, 844)):
            tests(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\nPS1b phase123: {len(results) - len(bad)}/{len(results)} PASS")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
