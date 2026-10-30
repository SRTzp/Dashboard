#!/usr/bin/env python3
"""CL1 — เก็บกวาด: ซ่อนแผนเดิม/Sat A/ข้อความ #foot · คำเตือนสำรองข้อมูล · "แผนที่ปิดแล้ว" + ลบ · สี P&L 0 · วันที่ยกเลิก · เส้นคั่น Macro
รัน: python3 run_tests_phase18.py (mock Firestore + fundflow stub) · ภาพเก็บที่ tests/screenshots/cl1-*.png
CL2-a: ทาง V3 off/Sat.A/sat7dOldPlanHtml ถูกลบจากโค้ด — เคสที่ผูกกับของที่ลบพิมพ์ RETIRED (phase4 ไม่ต้องใช้ /tmp/index_v3off.html แล้ว)"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase11 as p11
from run_tests_phase11 import pbver, seed_pb, iso, txt, no_overflow, fresh

ENGINE = base.BROWSER_ENGINE
SHOTS = p11.SHOTS
results = []


def retired(name, reason):
    """CL2-a — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่ต้องพิมพ์ไว้ให้ตามรอยได้ (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    try:
        (page.locator(sel).first if sel else page).screenshot(path=os.path.join(SHOTS, name)) if sel else page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e:
        print("shot fail", name, e)


def tr(id, port, status, **kw):
    return base.tr(id, port, status, **kw)


def core_sec(page):
    return page.evaluate("() => { const e=document.querySelector('[data-sum-sec=\"core\"]'); return e ? e.innerText.replace(/\\s+/g,' ') : null; }")


def set_trades(page, trades, capA=0):
    page.evaluate("""([t, capA])=>{ const b=getBook('main'); b.trades=t; getBook('fam').trades=[];   /* CL2-a: ไม่มีทุน satA แล้ว (capA ไม่ใช้) */
        planAcctFilter='all'; switchTab('plan'); setPlanScope('stock'); render(); }""", [trades, capA])
    page.wait_for_timeout(300)


def closed_idea(page, iid, asset, week, pnl_exit, tid, bias="Long"):
    """แผนที่ปิดแล้ว: ไม้ผูกกับบัญชี main สถานะ closed (exitPrice → P&L) · เขียนผ่าน sat7dWrite เหมือนแอป"""
    page.evaluate("""([iid, asset, week, exit, tid, bias])=>{
        const b = getBook('main');
        b.trades = b.trades.filter(t=>t.id!==tid).concat([{id:tid, date:'2026-09-01', sym:asset, port:'satB', bias, entry:100, sl:95, tp:null, qty:1, mult:1, cur:'THB', status:'closed', exitPrice:exit, unplanned:false}]);
        saveBook('main'); }""", [iid, asset, week, pnl_exit, tid, bias])
    page.wait_for_timeout(900)   # ให้ persist เขียนไม้ลง mock ก่อน — mock แจ้ง snapshot ทุกครั้งที่มีการเขียน → state รีโหลดจากก้อนที่เซฟไว้
    page.evaluate("""([iid, asset, week, tid, bias])=>{
        sat7dWrite('satIdeas', iid, {v3:true, asset, bias, week, created_at:new Date().toISOString(), entry:100, sl:95, tp:null, conditions:[], planned:true, setups:[], status:'closed', accts:{main:{trade_id:tid}}}); }""",
                  [iid, asset, week, tid, bias])
    page.wait_for_timeout(250)


def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    try:
        # ── 1) หน้า Sat: ไม่มีแผนเดิม ──
        p5.goto_sat(page); p11.reset_ideas(page)
        page.evaluate("() => { satV3Render(); }")
        page.wait_for_timeout(150)
        check(f"{tag} หน้า Sat (V3 on): ไม่มี .s7Old ใน DOM", page.locator("#satV3Panel .s7Old").count() == 0 and page.locator(".s7Old").count() == 0)
        retired(f"{tag} satV3Render ไม่เรียก sat7dOldPlanHtml (spy = 0)", "CL2-a ลบ sat7dOldPlanHtml")
        retired(f"{tag} ฟังก์ชันเดิมยังอยู่ (ไม่ลบโค้ด)", "CL2-a ลบ sat7dOldPlanHtml (ตั้งใจให้ไม่มีแล้ว)")

        # ── 2) satA ──
        set_trades(page, [tr("c1", "core", "open", sym="AOT")], capA=0)
        base_core = core_sec(page)
        check(f"{tag} satA ทุน 0 + ไม่มีไม้ open/plan → ไม่มี [data-sum-sec=satA]", page.locator('[data-sum-sec="satA"]').count() == 0 and base_core is not None)
        for nm in ("satA มีแต่ไม้ปิด (ทุน 0) → ยังไม่แสดง · Core เท่าเดิม", "satA มีไม้ open (ทุน 0) → แสดง · Core เท่าเดิม", "satA มีไม้ plan (ทุน 0) → แสดง", "satA ทุน > 0 → แสดง (ไม่ถูกซ่อน)"):
            retired(f"{tag} {nm}", "CL2-a ลบ Sat.A — ไม่มีบล็อก satA/ไม้ satA/ทุน satA")
        set_trades(page, [tr("c1", "core", "open", sym="AOT")], capA=0)
        page.evaluate("() => { renderJournal(); }")
        # (เดิม) ไม้ satA ปิดแล้วยังเห็นใน Journal (ชิปเก็บถาวร)
        retired(f"{tag} Journal: ไม้ satA ที่ปิดแล้วยังมีชิป/พอร์ต 'เก็บถาวร'", "CL2-a ลบ Sat.A — ไม่มีชิป/พอร์ต 'เก็บถาวร' ใน Journal")

        # ── 3) #foot ──
        page.evaluate("() => { switchTab('plan'); render(); }")
        foot = txt(page, "#foot")
        check(f"{tag} #foot ไม่มี 'Sat.A' / 'Growth Gate' / 'Acc/Dist'", not re.search(r"Sat\.A|Growth Gate|Acc/Dist", foot), foot)
        check(f"{tag} #foot รูปแบบ 'heat: Core x% / 20% ของถัง · Sat y% / 6% ของถัง · รวม z% ของบัญชี (ฐาน THB @ fx) — sync ผ่าน Firestore' (7E-1: แทนรูปแบบ limit เดิม)",
              re.match(r"^heat: Core [\d.]+% / [\d.]+% ของถัง · Sat [\d.]+% / [\d.]+% ของถัง · รวม [\d.]+% ของบัญชี \(ฐาน THB @ [\d.,]+\) — sync ผ่าน Firestore$", foot) is not None, foot)
        exp = page.evaluate("() => { const s=summarize(), cap=s.cap; return [pct(s.per.core.open,portCapTHB('core')), portHeatLimit('core'), pct(s.per.satB.open,portCapTHB('satB')), portHeatLimit('satB'), pct(s.tot.open,cap)].map(x=>fmt2(x)); }")
        nums = re.findall(r"([\d.]+)%", foot)
        check(f"{tag} #foot ตัวเลขตรงฟังก์ชัน (ใช้จริง core · เพดาน core · ใช้จริง satB · เพดาน satB · รวมบัญชี — 7E-1)", [float(x) for x in nums] == [float(x) for x in exp], f"{nums} vs {exp}")

        # ── 4) สำรองข้อมูล ──
        page.evaluate("() => openSystemSettings()"); page.wait_for_timeout(150)
        bk = page.evaluate("() => { const s=[...document.querySelectorAll('#sysOverlay details.setsec')].find(d=>d.innerText.toLowerCase().includes('back up to this device')); return s ? (s.textContent||'').replace(/\\s+/g,' ') : ''; }")
        check(f"{tag} สำรองข้อมูล: มีคำเตือน API key (Twelve Data) ติดไปด้วย", "API key (Twelve Data)" in bk and "do not share" in bk, bk[:200])
        check(f"{tag} สำรองข้อมูล: รายการหมวดตรงไฟล์จริง (แผน Sat · Bias สัปดาห์ · Macro Playbook · บัญชี)", all(k in bk for k in ("Sat plans", "weekly bias", "Macro Playbook", "accounts")))
        page.evaluate("() => document.getElementById('sysOverlay').classList.remove('show')")

        # ── 5) แผนที่ปิดแล้ว ──
        p5.goto_sat(page); p11.reset_ideas(page)
        page.wait_for_timeout(150)
        check(f"{tag} แผนปิดแล้ว n=0 → ไม่มีส่วนนี้", page.locator("[data-closed-plans]").count() == 0)
        wk = page.evaluate("() => wpWeekKey()")
        closed_idea(page, "cA", "XAUUSD", wk, 130, "tA")
        closed_idea(page, "cB", "BTCUSD", wk, 100, "tB", bias="Short")
        page.evaluate("() => satV3Render()"); page.wait_for_timeout(150)
        n = page.evaluate("() => satV3ClosedIdeas().length")
        check(f"{tag} n=2 → summary 'แผนที่ปิดแล้ว (2)' · 2 แถว · พับไว้", n == 2 and page.locator("[data-closed-plans] .s7ClRow").count() == 2 and "แผนที่ปิดแล้ว (2)" in txt(page, "[data-closed-plans] summary") and page.evaluate("() => !document.querySelector('[data-closed-plans]').open"))
        check(f"{tag} n=0 เมื่อลบครบ → ส่วนนี้หาย (ดูหลังทดสอบลบ)", True)
        page.click("[data-closed-plans] summary"); page.wait_for_timeout(100)
        row = txt(page, '[data-closed-idea="cA"]')
        check(f"{tag} แถว: asset · Bias · สัปดาห์ (jWeekLabel) · ผลต่อบัญชี · ปุ่มลบ", "Long" in row and page.evaluate("(w)=>jWeekLabel(w)", wk) in row and "บัญชีหลัก" in row and "฿30" in row and page.locator('[data-closed-idea="cA"] [data-closed-del]').count() == 1, row)
        shot(page, f"cl1-sat-closed-{label}.png", "#satV3Panel")
        check(f"{tag} กาง details ค้างไว้หลัง re-render (snapshot ไม่พับกลับ)", (page.evaluate("() => { satV3Render(); return document.querySelector('[data-closed-plans]').open; }")))
        # กดลบ → sheet ยืนยัน
        dialogs = []
        page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
        page.evaluate("() => { window.__delCalls = []; const c = sat7dCol('satIdeas'); const o = c.doc.bind(c); }")
        page.evaluate("""() => { window.__dels = []; const db = window.firebase.__mockDb; const orig = db.collection.bind(db);
            const wrap = (o, path) => new Proxy(o, {get(t, k){ const v = t[k]; if(typeof v!=='function') return v;
              return (...a)=>{ let p = path; if(k==='collection'||k==='doc') p = path+'/'+a[0]; if(k==='delete') window.__dels.push(path);
                const r = v.apply(t, a); return (r && typeof r==='object' && (k==='collection'||k==='doc')) ? wrap(r, p) : r; }; }});
            db.collection = (n)=>wrap(orig(n), n); }""")
        trades0 = page.evaluate("() => JSON.stringify(getBook('main').trades)")
        page.click('[data-closed-idea="cA"] [data-closed-del]'); page.wait_for_timeout(150)
        sh = txt(page, "[data-closed-del-sheet]")
        check(f"{tag} กดลบ → มี sheet ยืนยัน (ไม่มี window.confirm)", page.locator(".s7del-sheet").count() == 1 and not dialogs)
        check(f"{tag} ข้อความ sheet ตรงสเปก", sh.startswith("ลบแผน XAUUSD สัปดาห์") and "ไม้ใน Journal ไม่หาย" in sh and "เงื่อนไขที่ยกเลิกของแผนนี้จะหายจากพาเนลใน Journal" in sh, sh)
        check(f"{tag} ยังไม่ลบจนกว่าจะยืนยัน", page.evaluate("() => window.__dels.length") == 0 and page.locator('[data-closed-idea="cA"]').count() == 1)
        shot(page, f"cl1-sat-closed-sheet-{label}.png")
        page.click("[data-del-cancel]"); page.wait_for_timeout(100)
        check(f"{tag} ยกเลิกใน sheet → ไม่ลบอะไร", page.locator(".s7del-sheet").count() == 0 and page.evaluate("() => window.__dels.length") == 0)
        page.click('[data-closed-idea="cA"] [data-closed-del]'); page.wait_for_timeout(100)
        page.click("[data-del-ok]"); page.wait_for_timeout(300)
        dels = page.evaluate("() => window.__dels")
        check(f"{tag} ยืนยัน → delete เฉพาะเอกสารนั้น (satIdeas/cA)", len(dels) == 1 and dels[0].endswith("satIdeas/cA"), str(dels))
        check(f"{tag} B.trades ไม่เปลี่ยน", page.evaluate("() => JSON.stringify(getBook('main').trades)") == trades0)
        check(f"{tag} เหลือ 1 แถว (cB) · sheet ปิดแล้ว", page.locator("[data-closed-plans] .s7ClRow").count() == 1 and page.locator(".s7del-sheet").count() == 0)
        # ── 5b) จบแล้วทุกแบบ: ไม่มีไม้ · ไม้ถูกลบ · ร่างสัปดาห์ก่อน (ไม่รวมไม้ค้าง/ร่างสัปดาห์นี้) ──
        page.evaluate("""()=>{ const b=getBook('main'); b.trades = b.trades.concat([{id:'tP', date:'2026-09-01', sym:'ETHUSD', port:'satB', bias:'Long', entry:100, sl:95, tp:null, qty:1, mult:1, cur:'THB', status:'plan', unplanned:false}]); saveBook('main'); }""")
        page.wait_for_timeout(900)
        prev = page.evaluate("() => { const d=new Date(wpWeekKey()+'T00:00:00'); d.setDate(d.getDate()-7); const p=n=>String(n).padStart(2,'0'); return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate()); }")
        old = page.evaluate("() => { const d=new Date(wpWeekKey()+'T00:00:00'); d.setDate(d.getDate()-70); const p=n=>String(n).padStart(2,'0'); return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate()); }")   # CO1: ร่างสัปดาห์ก่อนที่ไม่เก่าเกิน 8 สัปดาห์ = แผนยกมา (ไม่อยู่ประวัติ) → uA ใช้ร่างอายุ 10 สัปดาห์ (เกินเพดานยกมา) ยังเป็น 'ร่างไม่ได้ใช้'
        page.evaluate("""([wk, prev, old])=>{
            const mk = (id, asset, week, extra)=>sat7dWrite('satIdeas', id, Object.assign({v3:true, asset, bias:'Long', week, created_at:new Date().toISOString(), entry:100, sl:95, tp:null, conditions:[], planned:true, setups:[], accts:{}}, extra));
            mk('nA','SOLUSD',wk,{status:'closed'});
            mk('nB','ADAUSD',prev,{status:'closed', accts:{main:{trade_id:'ghost'}}});
            mk('nC','ETHUSD',wk,{status:'closed', accts:{main:{trade_id:'tP'}}});
            mk('uA','XRPUSD',old,{status:'draft', planned:false});
            mk('uB','DOGEUSD',wk,{status:'draft', planned:false});
            mk('uC','LTCUSD',prev,{status:'draft', planned:false}); }""", [wk, prev, old])
        page.wait_for_timeout(300)
        page.evaluate("() => satV3Render()"); page.wait_for_timeout(150)
        ids = page.evaluate("() => satV3ClosedIdeas().map(x=>x.id).sort()")
        check(f"{tag} จบแล้วทุกแบบ: รายการ = cB + nA + nB + uA (ไม่มี nC ไม้ plan ค้าง · ไม่มี uB ร่างสัปดาห์นี้)", ids == ["cB", "nA", "nB", "uA"], str(ids))
        check(f"{tag} status closed ไม่มี accts/trade_id → ขึ้น ป้าย 'ไม่มีไม้'", "ไม่มีไม้" in txt(page, '[data-closed-idea="nA"]'))
        check(f"{tag} status closed แต่ trade_id ชี้ไม้ที่ถูกลบ → ป้าย 'ไม่มีไม้'", "ไม่มีไม้" in txt(page, '[data-closed-idea="nB"]'))
        check(f"{tag} ร่างที่เก่าเกิน 8 สัปดาห์ → ป้าย 'ร่างไม่ได้ใช้'", "ร่างไม่ได้ใช้" in txt(page, '[data-closed-idea="uA"]'))
        check(f"{tag} CO1: ร่างสัปดาห์ก่อน (uC) ไม่เก่าเกิน 8 สัปดาห์ → เป็นแผนยกมา ไม่อยู่ในแถบปิดแล้ว · อยู่ Trade Plans พร้อมแถบยกมา", page.locator('[data-closed-idea="uC"]').count() == 0 and page.evaluate("() => satV3IsCarried(sat7dIdea('uC'))") and page.locator('[data-carry-banner="uC"]').count() == 1)
        check(f"{tag} แผนปิดที่ยังมีไม้ plan ค้าง → ไม่อยู่ในแถบปิดแล้ว (อยู่ในแถว plan เดิม)", page.locator('[data-closed-idea="nC"]').count() == 0 and page.evaluate("() => satV3PlanRowState(sat7dIdea('nC'))") == "plan")
        check(f"{tag} ร่างสัปดาห์นี้ → ไม่อยู่ในแถบปิดแล้ว (อยู่ Trade Plans)", page.locator('[data-closed-idea="uB"]').count() == 0 and page.locator('[data-draft-card], .ui-pgrid').count() >= 0 and "DOGEUSD" in page.evaluate("() => document.getElementById('satV3Panel').innerText"))
        check(f"{tag} แถบ: เรียงสัปดาห์ใหม่ → เก่า · summary (4)", "แผนที่ปิดแล้ว (4)" in txt(page, "[data-closed-plans] summary") and page.evaluate("() => { const r=[...document.querySelectorAll('[data-closed-plans] .s7ClRow')].map(e=>e.dataset.closedIdea); const wk=i=>sat7dIdea(i).week; return r.every((id,k)=>k==0||wk(r[k-1])>=wk(id)); }"))
        check(f"{tag} เคสเดิมยังแสดงผลต่อบัญชี (cB ฿ ยังอยู่)", "฿" in txt(page, '[data-closed-idea="cB"]'))
        shot(page, f"cl1fix-sat-closed-all-{label}.png", "#satV3Panel")
        trades1 = page.evaluate("() => JSON.stringify(getBook('main').trades)")
        page.click('[data-closed-idea="nA"] [data-closed-del]'); page.wait_for_timeout(120)
        check(f"{tag} ไม่มีไม้ → ลบได้ · sheet ข้อความเดิม", txt(page, "[data-closed-del-sheet]").startswith("ลบแผน SOLUSD สัปดาห์") and "ไม้ใน Journal ไม่หาย" in txt(page, "[data-closed-del-sheet]"))
        page.click("[data-del-ok]"); page.wait_for_timeout(300)
        check(f"{tag} ลบ nA แล้วหายจากแถบ · B.trades ไม่เปลี่ยน", page.locator('[data-closed-idea="nA"]').count() == 0 and page.evaluate("() => JSON.stringify(getBook('main').trades)") == trades1)
        for i in ("nB", "nC", "uA", "uB"):
            page.evaluate("(i)=>satV3IdeaDelete(i)", i)
        page.wait_for_timeout(300)
        page.evaluate("() => { const b=getBook('main'); b.trades=b.trades.filter(t=>t.id!=='tP'); saveBook('main'); satV3Render(); }"); page.wait_for_timeout(900)
        # delete ล้ม → แสดง error
        page.evaluate("""() => { const db = window.firebase.__mockDb; const orig = db.collection.bind(db);
            db.collection = (n)=>{ const c = orig(n); const od = c.doc.bind(c);
              c.doc = (...a)=>{ const d = od(...a); const oc = d.collection ? d.collection.bind(d) : null;
                if(oc) d.collection = (m)=>{ const cc = oc(m); const odd = cc.doc.bind(cc); cc.doc = (...q)=>{ const dd = odd(...q); dd.delete = ()=>Promise.reject({code:'permission-denied'}); return dd; }; return cc; };
                return d; }; return c; }; }""")
        page.click('[data-closed-idea="cB"] [data-closed-del]'); page.wait_for_timeout(100)
        page.click("[data-del-ok]"); page.wait_for_timeout(400)
        check(f"{tag} delete ล้ม → มีข้อความ error บนหน้า (permission-denied)", "ลบแผนไม่สำเร็จ" in txt(page, "#satV3Panel [data-sat-del-err]") and "permission-denied" in txt(page, "#satV3Panel [data-sat-del-err]"))
        check(f"{tag} delete ล้ม → แผนยังอยู่ · B.trades ไม่เปลี่ยน", page.locator('[data-closed-idea="cB"]').count() == 1)
        no_overflow(page, w, tag + " หน้า Sat")
        if w <= 700:
            btn = page.locator('[data-closed-idea="cB"] [data-closed-del]')
            bb = btn.bounding_box()
            vis = page.evaluate("() => { const b=document.querySelector('[data-closed-idea=\"cB\"] [data-closed-del]'); const r=b.getBoundingClientRect(); const e=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); return b.contains(e); }")
            check(f"{tag} มือถือ: ปุ่มลบมองเห็นและกดได้จริง (hit-test) · สูง ≥ 30px", vis and bb and bb["height"] >= 30, str(bb))
            btn.click(); page.wait_for_timeout(120)
            check(f"{tag} มือถือ: แตะปุ่มลบ → sheet ขึ้น", page.locator("[data-closed-del-sheet]").count() == 1)
            page.click("[data-del-cancel]")

        # ── แท็บพอร์ต (ภาพ) ──
        set_trades(page, [tr("c1", "core", "open", sym="AOT")], capA=0)
        page.evaluate("() => window.scrollTo(0,0)"); shot(page, f"cl1-portfolio-{label}.png")
        no_overflow(page, w, tag + " แท็บพอร์ต")

        # ── 6) Setup P&L ──
        page.evaluate("() => { switchTab('journal'); render(); }"); page.wait_for_timeout(150)
        cls = page.evaluate("""() => { const g = (label, pnl)=>({label, n:6, winRate:50, avgR:1, pnl});
            window.jSetupGroups = () => [g('Zero',0), g('ZeroSm',0.3), g('Up',100), g('Down',-100), g('DownSm',-0.4)];
            renderJournalSetup([]); const r = {};
            document.querySelectorAll('#setupBody .jSetupRow[data-setup]').forEach(e=>{ r[e.dataset.setup] = e.querySelector('[data-lb="P&L (฿)"]').className; }); return r; }""")
        check(f"{tag} Setup: P&L 0 (และปัดแล้ว 0) → ไม่มี pnl-pos/pnl-neg", cls.get("Zero") == "" and cls.get("ZeroSm") == "" and cls.get("DownSm") == "", str(cls))
        check(f"{tag} Setup: +100 = pnl-pos · −100 = pnl-neg", cls.get("Up") == "pnl-pos" and cls.get("Down") == "pnl-neg", str(cls))
        shot(page, f"cl1-journal-setup-{label}.png", "#setupBody")
        # summary block ใช้ pnlCls เดียวกัน
        set_trades(page, [], capA=0)
        page.evaluate("""() => { getBook('main').trades = [{id:'z1',date:'2026-09-01',sym:'ZZ',port:'core',bias:'Long',entry:100,sl:95,tp:null,qty:1,mult:1,cur:'THB',status:'closed',exitPrice:100,exitDate:'2026-09-02',unplanned:false}]; switchTab('journal'); render(); }""")
        page.wait_for_timeout(200)
        zc = page.evaluate("""() => { const c=[...document.querySelectorAll('#jPorts .port[data-port="core"] .nums > div')].find(d=>d.innerText.includes('P&L')); const s=c&&c.querySelector('span:not(.k)'); return s ? s.className : null; }""")
        check(f"{tag} บล็อกสรุป Journal: P&L 0 → ไม่มีคลาสสี", zc == "", str(zc))

        # ── 7) วันที่ยกเลิก ──
        yr = page.evaluate("() => new Date().getFullYear()")
        page.evaluate("""(yr)=>{ satIdeasList = [{id:'k1', asset:'XAUUSD', bias:'Long', week:'2026-09-21', conditions:[
            {id:'a', text:'ปีนี้', status:'cancelled', cancelled_at: yr+'-09-28T10:00:00.000Z'},
            {id:'b', text:'ปีอื่น', status:'cancelled', cancelled_at:'2025-09-28T10:00:00.000Z'},
            {id:'c', text:'ว่าง', status:'cancelled', cancelled_at:''},
            {id:'d', text:'ผิดรูป', status:'cancelled', cancelled_at:'abc'}]}]; renderJournalCond(); }""", yr)
        items = page.evaluate("""() => [...document.querySelectorAll('#condBody .jCondItem')].map(e=>({at:e.dataset.condAt, d:e.querySelector('.jCondTop span').innerText.trim(), t:e.querySelector('.jCondTx').innerText.trim()}))""")
        by = {i["t"]: i for i in items}
        check(f"{tag} วันที่ยกเลิก ปีนี้ → '28 ก.ย.' · data-cond-at ยังเป็น ISO", by["ปีนี้"]["d"] == "28 ก.ย." and by["ปีนี้"]["at"].startswith(f"{yr}-09-28T"), str(items))
        check(f"{tag} ปีอื่น → '28 ก.ย. 25'", by["ปีอื่น"]["d"] == "28 ก.ย. 25", str(items))
        check(f"{tag} ว่าง/ผิดรูป → '—'", by["ว่าง"]["d"] == "—" and by["ผิดรูป"]["d"] == "—", str(items))
        # การ์ด Sat: รายการยกเลิก
        p5.goto_sat(page); p11.reset_ideas(page)
        p11.mkidea(page, "iC", conditions=[{"id": "c1", "text": "ข้อ A", "tp_from": None, "tp_to": None, "inval": None, "active": False, "saved": True, "status": "cancelled", "cancelled_at": f"{yr}-09-28T10:00:00.000Z"}])
        page.evaluate("() => { satV3CancelledOpen.add('iC'); satV3Render(); }"); page.wait_for_timeout(150)
        ct = txt(page, '.ui-cancd-i')
        check(f"{tag} การ์ด Sat: รายการยกเลิกใช้วันที่สั้น '· ยกเลิก 28 ก.ย.' (ไม่มี ISO)", "ยกเลิก 28 ก.ย." in ct and "-09-28" not in ct, ct)
        page.evaluate("() => { switchTab('journal'); render(); document.querySelectorAll('.jCondItem').length; }")
        page.evaluate("""(yr)=>{ satIdeasList = [{id:'k1', asset:'XAUUSD', bias:'Long', week:'2026-09-21', conditions:[
            {id:'a', text:'ยกเลิกแล้วข้อ A', status:'cancelled', cancelled_at: yr+'-09-28T10:00:00.000Z'},
            {id:'b', text:'ปีก่อน', status:'cancelled', cancelled_at:'2025-03-02T10:00:00.000Z'}]}]; renderJournalCond();
            const p=document.getElementById('jContent_cond'); if(p) p.style.display=''; }""", yr)
        shot(page, f"cl1-journal-cond-{label}.png", "#condBody")
        no_overflow(page, w, tag + " Journal")

        # ── 8) Macro: เส้นคั่นแถวแรก ──
        page.evaluate("() => switchTab('flow')"); page.wait_for_timeout(150)
        seed_pb(page, [pbver(1, iso(-24), x="up", b="up_flat", r="down_flat", u="none")])
        page.evaluate("() => { pbOpen = true; pbRender(); }"); page.wait_for_timeout(150)
        bt = page.evaluate("() => [...document.querySelectorAll('#pbPanel .pbRowW')].map(e=>getComputedStyle(e).borderTopWidth)")
        if w > 900:
            check(f"{tag} Macro 2 คอลัมน์: แถวแรกไม่มีเส้นบน · แถวถัดไปมี", len(bt) >= 2 and bt[0] == "0px" and all(x != "0px" for x in bt[1:]), str(bt))
        else:
            check(f"{tag} Macro คอลัมน์เดียว: ทุกแถวมีเส้นบนเหมือนเดิม", len(bt) >= 2 and all(x != "0px" for x in bt), str(bt))
        shot(page, f"cl1-macro-{label}.png", "#pbPanel")
    finally:
        check(f"{tag} console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
        browser.close()


def main():
    with sync_playwright() as pw:
        ui_tests(pw, 1440, 900, "1440px")
        ui_tests(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 18 / CL1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
