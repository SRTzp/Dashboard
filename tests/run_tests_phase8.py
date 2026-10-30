#!/usr/bin/env python3
"""F1 — แท็บ Flow: เปลี่ยนชื่อ · ถอดระบบ Macro/ข่าวทั้งหมด · แถบดำ "ผลที่ต้องทำ" · การ์ดปฏิทินข่าว ·
เพดาน Core แบบ f (ACWI/BIL + HYG/IEI · แดงตัวละ −25% · ต่ำสุด 50%) · เรียงธีม RRG · บอร์ดจดเองพับไว้ล่างสุด ·
+ งานเก็บจาก 7D.6 (open_editor คลิกชื่อสินค้า · satV3NewPlan เหลือตัวเดียว · [+ แผน] ยังทำงาน)

เทสหลัก: เพดาน Core ใน Add Trade · Port Heat · หน้าตั้งค่า Sizing ต้อง "เท่ากับ" ตัวเลขในแถบดำแท็บ Flow ทุกกรณี (0/1/2 ตัวแดง)
ทุกเคสรันที่ 1440px และ 430px · จำลอง fundflow.json ผ่าน window.__FF_JSON (ดู ff_stub.py)
ภาพเก็บที่ tests/screenshots/f1-*.png · รัน: python3 run_tests_phase8.py
"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase6 as p6

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")
os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
SRC = open(base.DEFAULT_INDEX, encoding="utf-8").read()

CAL_URL = ("https://sslecal2.investing.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,"
           "exc_previous&importance=3&features=datepicker,timezone&countries=5&calType=week&timeZone=27&lang=1")


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


# ───────────────────────── ตัวช่วย ─────────────────────────
def set_ff(page, acwi=True, hyg=True, age=1, hyg_key="HYG_IEI", ctx_up=True, drop=()):
    """ป้อน fundflow.json จำลอง (as_of = อายุ age วันทำการ) แล้วโหลด + วาดแท็บ Flow ใหม่"""
    iso = page.evaluate("""(n)=>{ for(let i=0;i<60;i++){ const d=new Date(); d.setDate(d.getDate()-i);
        const iso=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
        if(ffBizDaysSince(iso)===n) return iso; } return null; }""", age)
    r = {"ACWI_BIL": {"up": acwi, "flip_days": 3, "tf": "W"},
         hyg_key: {"up": hyg, "flip_days": 2, "tf": "W"},
         "HG_GC": {"up": ctx_up, "flip_days": 1, "tf": "W"},
         "SPHB_SPLV": {"up": ctx_up, "flip_days": 1, "tf": "D"},
         "RSP_SPY": {"up": ctx_up, "flip_days": 1, "tf": "D"}}
    if hyg_key != "HYG_IEF":
        r["HYG_IEF"] = {"up": True, "flip_days": 5, "tf": "W"}   # ตัวเดิมที่ Sat.A ยังอ่านอยู่ · ไม่เกี่ยวกับ Core
    for k in drop:
        r.pop(k, None)
    page.evaluate("(j)=>{ window.__FF_JSON=j; }", {"as_of": iso, "ratios": r})
    page.evaluate("() => ffLoadJson(true)")
    page.evaluate("() => { switchTab('flow'); renderFundflow(); }")
    page.wait_for_timeout(120)
    return iso


def clear_ff(page):
    page.evaluate("() => { window.__FF_JSON=null; ffJson=null; ffJsonAt=0; }")
    page.evaluate("() => ffLoadJson(true)")
    page.evaluate("() => { switchTab('flow'); renderFundflow(); }")
    page.wait_for_timeout(120)


def bar_cap(page):
    return page.evaluate("() => document.querySelector('#ffAction [data-ff=cap] .ffActV').textContent.trim()")


def close_overlays(page):
    page.evaluate("() => document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show'))")


def all_readouts(page):
    """CL2-d: เหลือ 2 จุดที่แสดง/ใช้เพดาน Core = แถบดำ (Flow) + ffDeployCap('core') · จุดอื่น (บรรทัด Add Trade · Heat 1R ใน Port · ตั้งค่า Sizing · szTargetRisk) ถูกลบแล้ว"""
    return {"bar": bar_cap(page), "deploy": page.evaluate("() => ffDeployCap('core')")}


def rrg_rows(page, rows, tf="D"):
    page.evaluate("""([rows,tf])=>{ const f=ffState(); f.rrgTf=tf; f.rrg=f.rrg||{}; f.rrg[tf==='W'?'rowsW':'rowsD']=rows; f.rrg.day=rrgToday(); f.rrg.err='';
        f.rrg.loading=false; ffRenderThemes(); }""", [rows, tf])


def mkrow(sym, quad, ratio=101, mom=101, dmom=0.0, days=3):
    return {"sym": sym, "name": sym + " name", "quad": quad, "ratio": ratio, "mom": mom, "dRatio": 0.0, "dMom": dmom, "days": days,
            "off52": -3.0, "rsTrend": 1.0, "date": "2026-09-25"}


def run(pw, width, height, label):
    tag = f"[{ENGINE}/{label}]"
    wide = width > 900
    px = label.replace("px", "")
    browser, context, page, console_errors, page_errors = base.launch_page(pw, width, height, base.DEFAULT_INDEX)
    cal_reqs = []
    def cal_route(route):
        cal_reqs.append(route.request.url)
        route.fulfill(status=200, content_type="text/html", body="<html><body style='margin:0'>stub calendar</body></html>")
    page.route(re.compile(r"sslecal2\.investing\.com"), cal_route)

    # ═════════ 1) เปลี่ยนชื่อแท็บ ═════════
    btn = page.evaluate("() => document.getElementById('tabBtnFlow').textContent.replace(/\\s+/g,' ').trim()")
    check(f"{tag} ปุ่มแท็บแรกชื่อ 'Flow' (ไม่ใช่ 'ตลาด')", btn.startswith("Flow") and "ตลาด" not in btn, btn)
    kb = page.evaluate("() => KB_GLOBAL.map(r=>r.join(' ')).join(' | ')")
    check(f"{tag} KB_GLOBAL: อ้างแท็บ Flow · ไม่มีปุ่มลัด N/ข่าว", "Flow" in kb and "ข่าว" not in kb and not any(r[0] == "N" for r in page.evaluate("() => KB_GLOBAL")), kb)

    # ═════════ 2–3) ถอด Macro/ข่าว ═════════
    gone = page.evaluate("""() => ['ffRenderMacro','rsMacroDoc','rsNewsAll','rsUnseenNews','rsRenderNews','rsNewsSort','openNewsFeed',
        'closeNewsFeed','rsOpenStock','wlNewsOf','wlAlertNews','wlNewsItem','FF_MACRO_ASSETS','WL_NEWS_MAX','WL_NEWS_DAYS','RS_SEV_RANK']
        .filter(n=>{ try{ return typeof eval(n)!=='undefined'; }catch(e){ return false; } })""")
    check(f"{tag} ฟังก์ชัน/ตัวแปรข่าว+macro ถูกลบครบ", gone == [], json.dumps(gone))
    check(f"{tag} RS_DEMO ไม่มี macro/news · meta.counts ไม่นับ news/macro (WL4: ไม่มี RS_DEMO เลย)",
          page.evaluate("() => typeof RS_DEMO==='undefined'"))   # WL4: RS_DEMO ถูกลบทั้งก้อน (เดิมตรวจว่าไม่มี macro/news ในนั้น)
    # [F2c แก้เคสเดิม] เดิม: satwMacroFF ต้องยังอยู่และคืน null → F2c ลบฟังก์ชันนี้แล้ว (Macro อ่านจาก satMacroOf)
    check(f"{tag} satwMacroFF ถูกลบแล้ว (F2c) และ satMacroOf ไม่ throw เมื่อไม่มี Playbook", page.evaluate("() => typeof satwMacroFF==='undefined' && satMacroOf('XAUUSD').state==='none'"))
    dom = page.evaluate("() => ({bell: !!document.getElementById('bellBtn'), dot: !!document.getElementById('bellDot'), drawer: !!document.getElementById('newsDrawer'), macro: !!document.getElementById('ffMacro'), pushBadge: !!document.getElementById('pushBadge')})")
    check(f"{tag} ไม่มีปุ่มกระดิ่ง / จุดแดง / newsDrawer / #ffMacro (WL4: ป้าย push ล่าสุดก็ไม่มีแล้ว)",
          not dom["bell"] and not dom["dot"] and not dom["drawer"] and not dom["macro"] and not dom["pushBadge"], json.dumps(dom))
    # กด N ไม่เกิดอะไร
    page.evaluate("() => { document.activeElement && document.activeElement.blur(); }")
    tab0 = page.evaluate("() => activeTab")
    page.keyboard.press("n"); page.keyboard.press("N"); page.wait_for_timeout(150)
    st = page.evaluate("() => ({tab: activeTab, overlay: document.querySelectorAll('.overlay.show').length})")
    check(f"{tag} กด N ไม่เกิดอะไร (ไม่เปิด overlay · แท็บไม่เปลี่ยน)", st["overlay"] == 0 and st["tab"] == tab0, json.dumps(st))

    # ไม่มี request ไป news/macro ตอนโหลดข้อมูลรีเสิร์ช
    page.evaluate("() => { window.__fsAccess = []; }")
    page.evaluate("() => rsLoad(true)")
    page.wait_for_timeout(250)
    for t in ["flow", "mix", "watch", "plan", "journal", "flow"]:
        page.evaluate(f"() => switchTab('{t}')")
        page.wait_for_timeout(120)
    page.evaluate("() => rsLoad(true)")
    page.wait_for_timeout(250)
    acc = page.evaluate("() => window.__fsAccess || []")
    bad = [a for a in acc if re.match(r"^(news|macro)(/|$)", a)]
    check(f"{tag} ไม่มี request ไป collection news/macro (rsLoad + วนทุกแท็บ) · WL4: ไม่อ่าน research + meta/push ด้วย (เดิม: ยังอ่าน)",
          bad == [] and not any(a.startswith("research") for a in acc) and "meta/push" not in acc, json.dumps({"bad": bad, "n": len(acc)}))

    # Watchlist / Tripwire (WL2 · Thesis จริง (fixture AVGO) + tripwire ที่มี news_id — เดิมใช้ research card)
    th = json.load(open(os.path.join(HERE, "fixtures", "avgo_thesis.json"), encoding="utf-8"))
    th["tripwires"][1]["news_id"] = "n1"
    th["tripwires"][1]["news_title"] = "หัวข้อข่าวเก่า"
    th["tripwires"][1]["level"] = "review"
    th_doc = {k: v for k, v in th.items() if k != "log"}
    page.evaluate("""(t)=>{ window.firebase.__mockDb.__seedDoc(['research','AVGO'], {ticker:'AVGO', name:'Broadcom'});
        wlCol().doc('AVGO').set({ticker:'AVGO', market:'US', port:'core', note:'', industry:'', added_at:'2026-01-01T00:00:00.000Z', thesis:t, thesis_log:[], thesis_history:[], thesis_hits:{}}); }""", th_doc)
    page.evaluate("() => rsLoad(true)")
    page.wait_for_timeout(450)
    page.evaluate("() => { switchTab('watch'); wlSetView('wl'); wlOpen('AVGO'); }")
    page.wait_for_timeout(250)
    wl = page.evaluate("""() => ({strip: !!document.querySelector('.wlNewsStrip,.wlNs'), n: !!document.querySelector('.wlNewsN'),
        subs: [...document.querySelectorAll('.wlDHead .ltTab')].map(b=>b.textContent.trim().replace(/\\d+$/,'')), txt: document.getElementById('tabWatch').innerText})""")
    check(f"{tag} Watchlist: ไม่มีแถบ 'ข่าวที่ต้องดู' / ตัวนับข่าวในแถว / แท็บ News ในหน้าหุ้น (WL2 · แท็บ สรุป มุมมอง ธุรกิจ ทำไมซื้อ ติดตาม ออกเมื่อ (VW1 เพิ่ม มุมมอง) แทน Overview/Research)",
          not wl["strip"] and not wl["n"] and wl["subs"] == ["สรุป", "มุมมอง", "ธุรกิจ", "ทำไมซื้อ", "ติดตาม", "ออกเมื่อ"] and "ข่าว" not in wl["txt"], json.dumps({k: wl[k] for k in ("strip", "n", "subs")}, ensure_ascii=False))
    page.evaluate("() => wlSetSub('exit')")
    page.wait_for_timeout(200)
    tw = page.evaluate("""() => { const w=[...document.querySelectorAll('.ltTwr')]; return {n:w.length, first:w[0]?w[0].innerText:'',
        html: w.map(x=>x.innerHTML).join(''), newsLinks: document.querySelectorAll('.ltTwr a').length}; }""")
    check(f"{tag} Tripwire ที่มี news_id: แสดงข้อความ + ระดับ 'review' ตามเดิม · ไม่มีลิงก์/ชื่อข่าว",
          tw["n"] >= 1 and th["tripwires"][1]["signal"][:12] in tw["first"] and "review" in tw["first"] and "หัวข้อข่าวเก่า" not in tw["html"] and tw["newsLinks"] == 0, json.dumps(tw, ensure_ascii=False)[:300])
    check(f"{tag} state.newsSeen เลิกใช้: ไม่มีโค้ดอ่าน (ไม่ลบ field)", "state.newsSeen" not in SRC.replace("(เช่น newsSeen", "") and "newsSeen" not in re.sub(r"/\*.*?\*/", "", SRC, flags=re.S))
    check(f"{tag} เหตุผลยกเลิก 'news' ใน Journal คงไว้", "{id:'news',     label:'เปลี่ยนใจเพราะข่าว'" in SRC)

    # ═════════ 6) เพดาน Core แบบ f — สูตรใน Calc ═════════
    f = page.evaluate("""() => ({
        r0: Calc.ffCoreCap({acwi:true,hyg:true,ageDays:0}).cap, r1: Calc.ffCoreCap({acwi:true,hyg:false,ageDays:0}).cap,
        r1b: Calc.ffCoreCap({acwi:false,hyg:true,ageDays:0}).cap, r2: Calc.ffCoreCap({acwi:false,hyg:false,ageDays:0}).cap,
        old6: Calc.ffCoreCap({acwi:false,hyg:false,ageDays:6}), old5: Calc.ffCoreCap({acwi:false,hyg:false,ageDays:5}),
        miss: Calc.ffCoreCap({acwi:false,hyg:null,ageDays:1}), miss0: Calc.ffCoreCap({acwi:true,hyg:null,ageDays:1}) })""")
    check(f"{tag} Calc.ffCoreCap: 0/1/2 ตัวแดง = 100/75/50%", (f["r0"], f["r1"], f["r1b"], f["r2"]) == (100, 75, 75, 50), json.dumps(f))
    check(f"{tag} Calc.ffCoreCap: ไฟล์เก่า 6 วันทำการ → 100% + stale · 5 วันทำการยังคิดปกติ (50%)",
          f["old6"]["cap"] == 100 and f["old6"]["stale"] is True and f["old5"]["cap"] == 50 and f["old5"]["stale"] is False, json.dumps([f["old6"], f["old5"]]))
    check(f"{tag} Calc.ffCoreCap: ไม่มี HYG/IEI → คิดจาก ACWI/BIL ตัวเดียว (แดง 75 / เขียว 100) + missing=['HYG/IEI']",
          f["miss"]["cap"] == 75 and f["miss0"]["cap"] == 100 and f["miss"]["missing"] == ["HYG/IEI"], json.dumps([f["miss"], f["miss0"]]))
    check(f"{tag} FF_RATIOS: Core = ACWI/BIL + HYG/IEI เท่านั้น · Cu/Au · SPHB/SPLV · RSP/SPY เป็นบริบท",
          page.evaluate("() => JSON.stringify([FF_RATIOS.filter(d=>d.lay==='core').map(d=>d.nm), FF_RATIOS.filter(d=>d.lay==='ctx').map(d=>d.nm)])")
          == json.dumps([["ACWI/BIL", "HYG/IEI"], ["Cu/Au", "SPHB/SPLV", "RSP/SPY"]], ensure_ascii=False, separators=(",", ":")))

    # ── เทสหลัก: ทุกจุดที่แสดงเพดาน Core = แถบดำ ทุกกรณี ──
    cases = [("0 ตัวแดง", True, True, 100), ("1 ตัวแดง (HYG/IEI)", True, False, 75),
             ("1 ตัวแดง (ACWI/BIL)", False, True, 75), ("2 ตัวแดง", False, False, 50)]
    for name, acwi, hyg, exp in cases:
        set_ff(page, acwi, hyg, age=1)
        r = all_readouts(page)
        ok = (r["bar"] == f"{exp}%" and r["deploy"] == exp)
        check(f"{tag} {name} → แถบดำ = ffDeployCap('core') = {exp}% (CL2-d: ไม่มี szTargetRisk/Port Heat/ตั้งค่า Sizing แล้ว)", ok, json.dumps(r))
    # Sat.A ไม่เปลี่ยน: ยังตามสูตรเดิม (3 ratio + SPHB) ไม่ถูกสูตร f ดึง
    set_ff(page, True, False, age=1, ctx_up=False)   # ctx แดงหมด → Sat.A เดิมลด แต่ Core (f) ต้องไม่ขยับตาม
    s = page.evaluate("""() => { const R=ffJsonData().ratios, u=k=>!!(R[k]&&R[k].up);
        return {sat: ffDeployCap('satA'), old: ffExposure([u('ACWI_BIL'),u('HYG_IEF'),u('HG_GC')], u('SPHB_SPLV')).satPct, core: ffDeployCap('core')}; }""")
    check(f"{tag} Sat.A ยังใช้สูตรเดิมทุกอย่าง (ffDeployCap('satA') = ffExposure เดิม) · Core ไม่ตามบริบท",
          s["sat"] == s["old"] and s["core"] == 75, json.dumps(s))
    # บริบทแดงหมด ไม่ลด Core
    set_ff(page, True, True, age=1, ctx_up=False)
    r = all_readouts(page)
    check(f"{tag} Cu/Au · SPHB/SPLV · RSP/SPY แดงหมด → เพดาน Core ยัง 100% ทุกจุด (บริบทไม่เข้าสูตร)",
          all(v in (100, "100%") for v in r.values()), json.dumps(r))
    reg = page.evaluate("() => document.getElementById('ffRegime').innerText")
    check(f"{tag} การ์ด Regime: ไม่มีแถว Sat.A · มีชิป Cu/Au SPHB/SPLV RSP/SPY ในแถวบริบท",
          "Sat.A" not in reg and all(x in reg for x in ["Cu/Au", "SPHB/SPLV", "RSP/SPY", "ACWI/BIL", "HYG/IEI"]), reg[:300])
    # ไฟล์เก่า 6 วันทำการ → 100% + เตือนส้ม (ทั้งที่แดง 2 ตัว)
    set_ff(page, False, False, age=6)
    r = all_readouts(page)
    warn = page.evaluate("""() => { const w=document.querySelector('#ffRegime .ffRegWarn'); return w ? {txt:w.innerText, bg:getComputedStyle(w).backgroundColor} : null; }""")
    fresh = page.evaluate("() => document.querySelector('#ffAction [data-ff=fresh]').textContent")
    check(f"{tag} ไฟล์เก่า 6 วันทำการ + แดง 2 ตัว → ทุกจุด 100% (ไม่ลดเพดาน) + เตือนส้ม",
          all(v in (100, "100%") for v in r.values()) and warn and "ไม่ลดเพดาน" in warn["txt"] and "6 วันทำการ" in warn["txt"] and "rgba(169, 110, 6" in warn["bg"], json.dumps([r, warn]))
    # [F2d แก้เคสเดิม] ช่อง 'ความสดข้อมูล' ถูกแทนด้วยป้ายขวาของบรรทัดสรุป (data-ff=fresh) 'ข้อมูล <d MMM> · เก่า N วันทำการ' สีเตือน
    check(f"{tag} ป้ายความสดบนบรรทัดสรุป = '… · เก่า 6 วันทำการ' (สีส้ม)", fresh.endswith("· เก่า 6 วันทำการ"), fresh)
    set_ff(page, False, False, age=5)
    r = all_readouts(page)
    check(f"{tag} ไฟล์ 5 วันทำการ + แดง 2 ตัว → ยังลด 50% ทุกจุด (ขอบเขต: เกิน 5 ถึงหยุดลด)", all(v in (50, "50%") for v in r.values()), json.dumps(r))
    # ไม่มี HYG_IEI ในไฟล์ (มีแต่ HYG_IEF เดิม)
    for acwi, exp in ((False, 75), (True, 100)):
        set_ff(page, acwi, True, age=1, hyg_key="HYG_IEF", drop=("HYG_IEI",))
        r = all_readouts(page)
        w = page.evaluate("() => document.getElementById('ffRegime').innerText + ' | ' + document.getElementById('ffAction').innerText")
        check(f"{tag} ไม่มี HYG_IEI ในไฟล์ (ACWI {'แดง' if not acwi else 'เขียว'}) → คิดจาก ACWI/BIL ตัวเดียว = {exp}% ทุกจุด + เตือน 'HYG/IEI ขาด'",
              all(v in (exp, f"{exp}%") for v in r.values()) and "HYG/IEI ขาด" in w, json.dumps([r, w[:200]]))
    # ยังไม่มีไฟล์ (โหมดตัวอย่าง) — ไม่ย่อขนาดไม้
    clear_ff(page)
    check(f"{tag} ยังไม่มี fundflow.json → แถบดำ '—' · ไม่ย่อขนาดไม้ (ffDeployCap=100) (CL2-d: ตัดส่วน szTargetRisk ออก)",
          bar_cap(page) == "—" and page.evaluate("() => ffDeployCap('core')") == 100, json.dumps([bar_cap(page)]))

    # ═════════ 4) แถบดำ ═════════
    set_ff(page, True, False, age=1)
    rrg_rows(page, [mkrow("SMH", "lead", dmom=1.0), mkrow("IGV", "lead", dmom=3.0), mkrow("HACK", "lead", dmom=2.0), mkrow("XLE", "lag")])
    b = page.evaluate("""() => { const bar=document.getElementById('ffAction'), cells=[...bar.querySelectorAll('.ffActCell')];
        const sum=bar.querySelector('.ffActSum'); const cs=getComputedStyle(bar);
        return {first: document.getElementById('tabFlow').firstElementChild===bar, bg: cs.backgroundColor, sum: sum.textContent,
          sumOneLine: sum.scrollHeight <= sum.clientHeight + 2 && getComputedStyle(sum).whiteSpace==='nowrap',
          cells: cells.map(c=>({k:c.dataset.ff, l:c.querySelector('.ffActL').textContent, v:(c.querySelector('.ffActV')||c.querySelector('.ffActLead')||c.querySelector('.ffActMac')||c).textContent.trim(), tag:(c.querySelector('.ffActTag')||{}).textContent||''})),
          pos: cells.map(c=>{ const r=c.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top)]; }),
          regTop: document.getElementById('ffRegime').getBoundingClientRect().top, barBottom: bar.getBoundingClientRect().bottom}; }""")
    check(f"{tag} แถบดำอยู่บนสุดของแท็บ Flow (พื้น #16191E — F2d รอบ 2 แก้จาก --dark) · เหนือการ์ด Regime", b["first"] and b["bg"] == "rgb(22, 25, 30)" and b["barBottom"] <= b["regTop"], json.dumps({k: b[k] for k in ("first", "bg", "barBottom", "regTop")}))
    # [F2d แก้เคสเดิม] 4 ช่องใหม่ Regime · ธีมนำ · เพดาน Core · Macro (ความสดข้อมูลย้ายไปเป็นป้ายบรรทัดสรุป)
    check(f"{tag} แถบดำ: บรรทัดสรุป 1 บรรทัด + 4 ช่อง (Regime · ธีมนำ · เพดาน Core · Macro)",
          b["sumOneLine"] and sorted(c["k"] for c in b["cells"]) == ["cap", "lead", "macro", "regime"]
          and sorted(c["l"] for c in b["cells"]) == sorted(["Regime", "ธีมนำ", "เพดาน Core", "Macro"]), json.dumps(b["cells"], ensure_ascii=False))
    v = {c["k"]: c for c in b["cells"]}
    # [F2c แก้เคสเดิม] ช่อง Macro ไม่มี Playbook: ป้าย 'รอ Playbook' → 'ยังไม่มี Playbook ใช้จริง'
    check(f"{tag} แถบดำ: เพดาน Core '75%' · Macro '—' + ป้าย 'ยังไม่มี Playbook ใช้จริง' · ธีมนำ 1–2 ชื่อ (เรียง Δmom: IGV · HACK) · สด",
          v["cap"]["v"] == "75%" and v["macro"]["v"] == "—" and v["macro"]["tag"] == "ยังไม่มี Playbook ใช้จริง" and v["lead"]["v"].startswith("IGV") and "HACK" in v["lead"]["v"] and page.evaluate("() => document.querySelector('#ffAction [data-ff=fresh]').textContent").endswith("· สด"), json.dumps(v, ensure_ascii=False))
    check(f"{tag} แถบดำ: บรรทัดสรุปบอกเพดาน + ตัวแดง", "75%" in b["sum"] and "HYG/IEI" in b["sum"], b["sum"])
    rrg_rows(page, [mkrow("XLE", "lag")])
    check(f"{tag} แถบดำ: ไม่มีธีมนำ → '—'", page.evaluate("() => document.querySelector('#ffAction [data-ff=lead] .ffActLead').textContent") == "—")
    rrg_rows(page, [mkrow("SMH", "lead", dmom=1.0), mkrow("IGV", "lead", dmom=3.0), mkrow("HACK", "lead", dmom=2.0)])
    if wide:
        check(f"{tag} 1440: 4 ช่องเรียงแถวเดียว", len({p[1] for p in b["pos"]}) == 1 and len({p[0] for p in b["pos"]}) == 4, json.dumps(b["pos"]))
    else:
        check(f"{tag} 430: 4 ช่อง = 2×2", len({p[1] for p in b["pos"]}) == 2 and len({p[0] for p in b["pos"]}) == 2, json.dumps(b["pos"]))

    # ═════════ 5) การ์ดปฏิทินข่าว ═════════
    page.evaluate("() => switchTab('flow')")
    page.wait_for_timeout(1200)
    pre = page.evaluate("() => ({iframes: document.querySelectorAll('iframe').length, open: document.getElementById('ffCal').open, sum: document.querySelector('#ffCal>summary').textContent.trim()})")
    check(f"{tag} ปฏิทิน: พับไว้ 1 บรรทัด 'ปฏิทินข่าว US · สำคัญสูง · สัปดาห์นี้' · ยังไม่มี iframe · ไม่มี request ไป investing",
          pre["iframes"] == 0 and not pre["open"] and pre["sum"] == "ปฏิทินข่าว US · สำคัญสูง · สัปดาห์นี้" and cal_reqs == [], json.dumps([pre, cal_reqs]))
    sumh = page.evaluate("() => document.querySelector('#ffCal>summary').getBoundingClientRect().height")
    check(f"{tag} ปฏิทินที่พับ = บรรทัดเดียว (สูง < 60px)", sumh < 60, str(sumh))
    page.screenshot(path=os.path.join(SHOTS, f"f1-flow-folded-{px}.png"), full_page=True)
    page.click("#ffCal>summary")
    page.wait_for_selector("#ffCalFrame", timeout=3000)
    page.wait_for_timeout(600)
    cal = page.evaluate("""() => { const fr=document.getElementById('ffCalFrame'), sc=document.querySelector('.ffCalScroll'), cr=document.querySelector('.ffCalCredit');
        const r=fr.getBoundingClientRect(), s=getComputedStyle(fr), cs=getComputedStyle(sc), crs=getComputedStyle(cr);
        return {src: fr.getAttribute('src'), h: Math.round(r.height), w: Math.round(r.width), minW: s.minWidth, ovx: cs.overflowX, scW: sc.clientWidth, scSW: sc.scrollWidth,
                credit: cr.textContent.trim(), crSize: parseFloat(crs.fontSize), crColor: crs.color, bodyColor: getComputedStyle(document.body).color, n: document.querySelectorAll('iframe').length,
                docW: document.documentElement.scrollWidth}; }""")
    check(f"{tag} ปฏิทิน: กางแล้วสร้าง iframe 1 ตัว · src ตรงตามสเปกทุกตัวอักษร", cal["n"] == 1 and cal["src"] == CAL_URL, json.dumps(cal)[:300])
    check(f"{tag} ปฏิทิน: request จริงไปที่ URL นั้นเพียง 1 ครั้ง (หลังกางเท่านั้น)", len(cal_reqs) == 1 and cal_reqs[0].replace("investing.com/?", "investing.com?") == CAL_URL, json.dumps(cal_reqs))
    check(f"{tag} ปฏิทิน: iframe กว้าง 100% (min-width 650) สูง 467 ในกรอบ overflow-x:auto",
          cal["h"] == 467 and cal["minW"] == "650px" and cal["ovx"] == "auto" and cal["w"] >= 650, json.dumps({k: cal[k] for k in ("h", "w", "minW", "ovx")}))
    check(f"{tag} ปฏิทิน: บรรทัด 'provided by Investing.com' ตัวเล็กสีจาง", cal["credit"] == "provided by Investing.com" and cal["crSize"] <= 11 and cal["crColor"] != cal["bodyColor"], json.dumps([cal["credit"], cal["crSize"], cal["crColor"]]))
    if not wide:
        check(f"{tag} 430: กางปฏิทินแล้วหน้าไม่ล้น (กรอบเลื่อนแนวนอนเอง: scrollWidth>clientWidth)", cal["docW"] <= width and cal["scSW"] > cal["scW"], json.dumps([cal["docW"], cal["scW"], cal["scSW"]]))
    page.click("#ffCal>summary"); page.click("#ffCal>summary"); page.wait_for_timeout(200)
    check(f"{tag} ปฏิทิน: พับ-กางซ้ำไม่สร้าง iframe ซ้ำ · ไม่ยิง request ซ้ำ", page.evaluate("() => document.querySelectorAll('iframe').length") == 1 and len(cal_reqs) == 1)
    page.screenshot(path=os.path.join(SHOTS, f"f1-flow-open-{px}.png"), full_page=True)
    page.click("#ffCal>summary")   # พับกลับ

    # ═════════ 8) เรียงธีมตามช่อง · 9) บอร์ดจดเอง ═════════
    rrg_rows(page, [mkrow("A", "lag", dmom=5), mkrow("B", "weak", dmom=1), mkrow("C", "imp", dmom=2), mkrow("D", "lead", dmom=0), mkrow("E", "lag", dmom=1), mkrow("F", "lead", dmom=4)])
    order = page.evaluate("() => [...document.querySelectorAll('#ffThemes .rrgTbl tbody tr')].map(r=>r.children[1].textContent.trim())")
    check(f"{tag} ธีม RRG เรียงตามช่อง: นำ → ดีขึ้น → อ่อนลง → ตาม", order == ["LEADING", "LEADING", "IMPROVING", "WEAKENING", "LAGGING", "LAGGING"], json.dumps(order))
    lay = page.evaluate("""() => { const d=document.getElementById('ffManualBoards'), th=document.getElementById('ffThemesHead').closest('.panel'), foot=document.querySelector('#tabFlow .ffFoot'),
        kids=[...document.getElementById('tabFlow').children];
        return {open: d.open, idx: {themes: kids.indexOf(th), manual: kids.indexOf(d), foot: kids.indexOf(foot), last: kids.length-1}, stale: !!d.querySelector('#ffStale'),
                bodyHidden: !d.querySelector('.ffManualBody').checkVisibility()}; }""")
    check(f"{tag} บอร์ดจดเอง 2 บอร์ด: พับไว้ · อยู่หลังแผนที่ธีม ล่างสุดของเนื้อหา (ก่อนบรรทัดท้าย) · ซ่อนเนื้อหา",
          (not lay["open"]) and lay["bodyHidden"] and lay["idx"]["manual"] > lay["idx"]["themes"] and lay["idx"]["manual"] == lay["idx"]["foot"] - 1, json.dumps(lay))
    boards = page.evaluate("() => [!!document.getElementById('ffBoard1'), !!document.getElementById('ffBoard2')]")
    check(f"{tag} บอร์ดจดเองยังอยู่ครบ 2 บอร์ด (ffBoard1/ffBoard2)", boards == [True, True])

    # ═════════ ภาพ + ระบบ ═════════
    set_ff(page, True, False, age=1)
    page.screenshot(path=os.path.join(SHOTS, f"f1-flow-{px}.png"), full_page=True)

    # ═════════ 11) งานเก็บจาก 7D.6 ═════════
    check(f"{tag} PF3 satV3NewPlan ไม่เหลือในแอปเลย (ไม่มีผู้เรียก · ไม่อ่าน Bias Strategy) — เหลือแค่ตัวช่วยเทสใน mock-firebase.js", SRC.count("satV3NewPlan") == 0)
    check(f"{tag} PF1: satV3NewPlan ไม่อยู่ในแอป (ไม่อ่าน Bias Strategy)", SRC.count("function satV3NewPlan(") == 0)
    p5.goto_sat(page)
    p6.setup_strategy(page, "XAUUSD", "L")
    if page.evaluate("() => !!document.querySelector('.ui-editor[data-asset=\"XAUUSD\"] .ui-factors')"):
        page.evaluate("() => satV3Pick('XAUUSD')")   # พับตัวแก้ก่อน เพื่อพิสูจน์ open_editor เปิดได้จริง
        page.wait_for_timeout(120)
    p5.open_editor(page, "XAUUSD")
    check(f"{tag} open_editor (คลิกชื่อสินค้า .ui-tile-a) เปิดตัวแก้ได้จริง ไม่ไปโดนปุ่ม [+ แผน]",
          page.evaluate("() => !!document.querySelector('.ui-editor[data-asset=\"XAUUSD\"] .ui-factors')") and page.evaluate("() => satIdeasList.filter(x=>x.v3).length") == 0)
    iid = p6.new_plan(page, "XAUUSD")
    idea = page.evaluate("(i)=>sat7dIdea(i)", iid)
    check(f"{tag} [+ แผน] ยังทำงาน (ตัวจริง): สร้างไอเดีย v3 ตามทิศ Bias · กดซ้ำไม่สร้างซ้ำ",
          idea and idea.get("v3") and idea.get("bias") == "Long" and idea.get("asset") == "XAUUSD" and idea.get("planned") is False, json.dumps(idea)[:200])
    page.click('.ui-tile[data-key="XAUUSD"] .ui-btn-pri:has-text("+ แผน")')
    page.wait_for_timeout(200)
    check(f"{tag} กด [+ แผน] ซ้ำ → ไม่สร้างร่างซ้ำ", page.evaluate("() => satIdeasList.filter(x=>x.v3 && x.asset==='XAUUSD').length") == 1)

    # ─── ระบบ ───
    for t in ["flow", "mix", "watch", "plan", "journal"]:
        try: page.evaluate(f"() => switchTab('{t}')")
        except Exception as e: check(f"{tag} switchTab {t} ไม่ throw", False, str(e))
        page.wait_for_timeout(100)
        sw = page.evaluate("() => document.documentElement.scrollWidth")
        check(f"{tag} แท็บ {t}: ไม่ล้นแนวนอน (scrollWidth={sw} ≤ {width})", sw <= width, str(sw))
    page.evaluate("() => switchTab('flow')")
    check(f"{tag} console: zero error-level messages", len(console_errors) == 0, "; ".join(console_errors[:8]))
    check(f"{tag} console: zero uncaught page errors", len(page_errors) == 0, "; ".join(page_errors[:8]))
    context.close(); browser.close()


def run_cal_fail(pw):
    """ปฏิทินโหลดไม่ขึ้น (ไม่ตอบ request) → '—' + ลิงก์ investing.com/economic-calendar · ไม่มี iframe ค้าง"""
    tag = f"[{ENGINE}/1440px/cal-fail]"
    browser, context, page, console_errors, page_errors = base.launch_page(pw, 1440, 900, base.DEFAULT_INDEX)
    held = []
    page.route(re.compile(r"sslecal2\.investing\.com"), lambda route: held.append(route))   # ค้าง ไม่ตอบ (เก็บไว้ abort ตอนจบ)
    page.evaluate("() => switchTab('flow')")
    page.click("#ffCal>summary")
    page.wait_for_selector("#ffCalFrame", timeout=3000)
    page.wait_for_timeout(int(page.evaluate("() => FF_CAL_TIMEOUT_MS")) + 1200)
    r = page.evaluate("""() => { const f=document.querySelector('.ffCalFail'); return {txt: f?f.textContent.trim():'', href: f?f.querySelector('a').href:'',
        iframes: document.querySelectorAll('iframe').length}; }""")
    check(f"{tag} โหลดไม่ขึ้น → '—' + ลิงก์เปิด investing.com/economic-calendar · ไม่ค้าง iframe",
          r["txt"].startswith("—") and r["href"] == "https://www.investing.com/economic-calendar" and r["iframes"] == 0, json.dumps(r))
    check(f"{tag} console/page error = 0", len(page_errors) == 0, "; ".join(page_errors[:5]))
    for r_ in held:
        try: r_.abort()
        except Exception: pass
    context.close(); browser.close()


def main():
    with sync_playwright() as pw:
        run(pw, 1440, 900, "1440px")
        run(pw, 430, 932, "430px")
        run_cal_fail(pw)
    n_pass = sum(1 for _, ok, _ in results if ok)
    n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 8 / F1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok:
                print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
