#!/usr/bin/env python3
"""TX1 — My Thesis Edit ⇄ Read card · auto-growing textareas · draft autosave · readable text size (--read-fs/--read-lh) · เทส 365
Chromium · 390 + 1440 · light + dark shots · ข้อมูล SAMPLE ล้วน · รัน: python3 run_tests_phase365.py"""
import json, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase44 as P44
import run_tests_phase111 as P111

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=400): page.wait_for_timeout(ms)


DLG = {"mode": "accept", "seen": []}
CONFIRM_STUB = "window.__cf=[]; window.__cfAns=true; window.confirm=(m)=>{ window.__cf.push(m); return window.__cfAns; };"


def confirms(page): return js(page, "()=>window.__cf.slice()")
def cf_reset(page, ans=True): js(page, "(a)=>{ window.__cf=[]; window.__cfAns=a; }", ans)


def seed(page):
    page.add_init_script(CONFIRM_STUB); page.evaluate(CONFIRM_STUB)
    page.on("dialog", lambda d: DLG["seen"].append((d.type, d.message)))   # P39.launch already accepts every dialog · here we only record
    js(page, "()=>{ window.__READY_REAL = true; }")
    js(page, "()=>wlCol().doc('TXA').set({ticker:'TXA', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'})")   # ไม่มีข้อความ → Edit
    js(page, "()=>wlCol().doc('TXB').set({ticker:'TXB', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', my_thesis:{why:'saved why line one\\nsecond line', exit:'saved exit', updated_at:'2026-10-02T00:00:00Z'}, next_check_date:'2026-11-07', next_check_note:'Q3 earnings'})")
    js(page, "()=>wlCol().doc('TXC').set({ticker:'TXC', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', my_thesis:{why:'only why', exit:'', updated_at:'2026-10-02T00:00:00Z'}})")
    js(page, "()=>wlCol().doc('TXD').set({ticker:'TXD', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', archived:true, archived_reason:'broke', archived_at:'2026-10-30T00:00:00Z', my_thesis:{why:'w', exit:'x', updated_at:'2026-10-02T00:00:00Z'}})")
    settle(page, 600)


def view(page, sym):
    js(page, "(s)=>{ switchTab('watch'); wlSetView('wl'); renderWatchlist(); wlOpen(s); wlSetSub('view'); }", sym); settle(page, 600)


def mode(page, sym="TXB"): return js(page, "(s)=>{ const e=document.querySelector('[data-wl-mt=\"'+s+'\"]'); return e ? e.dataset.wlMtMode : null; }", sym)
def fs(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); if(!e) return null; const c=getComputedStyle(e); return [c.fontSize, c.lineHeight]; }", sel)
def ls(page, t): return js(page, "(t)=>{ const o={}; try{ ['why','exit','nc_date','nc_note'].forEach(k=>{ const v=localStorage.getItem('tx1.draft.'+t+'.'+k); if(v!=null) o[k]=v; }); }catch(e){ return 'ERR'; } return o; }", t)


def reload(page):
    P44.reload_keep(page)
    js(page, "()=>{ window.__READY_REAL = true; }")


def tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        seed(page)
        # ── 1 mode defaults · fields ──
        view(page, "TXA")
        check(f"{tag} 1 no saved text → Edit mode (✓ ① ④ Next check inputs · Save · Cancel)", mode(page, "TXA") == "edit" and js(page, "()=>[...document.querySelectorAll('[data-wl-mt] textarea')].length") == 2 and js(page, "()=>!!document.querySelector('[data-wl-mt-save]') && !!document.querySelector('[data-wl-mt-cancel]')"), mode(page, "TXA"))
        ta = js(page, "()=>{ const t=document.querySelector('[data-wl-mt-why]'); const c=getComputedStyle(t), l=t.closest('label').getBoundingClientRect(), r=t.getBoundingClientRect(); return {rows:t.rows, h:r.height, lh:parseFloat(c.lineHeight), fs:parseFloat(c.fontSize), w:r.width, lw:l.width}; }")
        check(f"{tag} 1 textarea: min 3 lines tall · full width of its label", ta["h"] >= 3 * ta["lh"] and ta["w"] >= ta["lw"] - 2, ta)
        ref = js(page, "()=>parseFloat(getComputedStyle(document.documentElement).fontSize) * .92")
        want = max(16.0, ref) if w <= 600 else ref
        check(f"{tag} 1 typed text size = --read-fs ({want:.2f}px; phone ≥16px)", abs(ta["fs"] - want) < .1, [ta["fs"], want])
        nci = fs(page, "[data-wl-nc-note]")
        check(f"{tag} 1 Next check / What to check inputs use the same size", abs(float(nci[0][:-2]) - want) < .1, nci)
        # ── 2 grows with content up to 60vh ──
        page.fill("[data-wl-mt-why]", "line\n" * 5); page.dispatch_event("[data-wl-mt-why]", "input")
        g5 = js(page, "()=>{ const t=document.querySelector('[data-wl-mt-why]'); return [t.offsetHeight, t.scrollHeight, t.clientHeight, getComputedStyle(t).overflowY]; }")
        check(f"{tag} 2 5 lines → box grew, no inner scrollbar", g5[0] > ta["h"] and g5[1] <= g5[2] + 1 and g5[3] == "hidden", g5)
        page.fill("[data-wl-mt-why]", "\n".join(f"row {i}" for i in range(300))); page.dispatch_event("[data-wl-mt-why]", "input")
        g300 = js(page, "()=>{ const t=document.querySelector('[data-wl-mt-why]'); return {h:t.offsetHeight, max:Math.round(innerHeight*.6), sh:t.scrollHeight, ch:t.clientHeight, oy:getComputedStyle(t).overflowY}; }")
        check(f"{tag} 2 300 lines → stops at ≈60vh then scrolls inside", abs(g300["h"] - g300["max"]) <= 4 and g300["sh"] > g300["ch"] and g300["oy"] == "auto", g300)
        page.fill("[data-wl-mt-why]", "multi\nline\npaste\n\n  kept"); page.dispatch_event("[data-wl-mt-why]", "input")
        check(f"{tag} 2 paste / line breaks kept in the draft", js(page, "()=>wlMtDraft['TXA'].why") == "multi\nline\npaste\n\n  kept")
        # ── 3 autosave → refresh → restore ──
        page.fill("[data-wl-mt-exit]", "draft exit text"); page.dispatch_event("[data-wl-mt-exit]", "input")
        check(f"{tag} 3 draft tag appears while the text differs from saved", js(page, "()=>!document.querySelector('[data-wl-mt-draft]').hidden"))
        settle(page, 1500)
        l1 = ls(page, "TXA")
        check(f"{tag} 3 ≈1 s after typing stops → localStorage holds a draft per stock + field", l1.get("exit") == "draft exit text" and l1.get("why", "").startswith("multi"), l1)
        reload(page); view(page, "TXA")
        r = js(page, "()=>({mode:(document.querySelector('[data-wl-mt]')||{dataset:{}}).dataset.wlMtMode, why:(document.querySelector('[data-wl-mt-why]')||{}).value, exit:(document.querySelector('[data-wl-mt-exit]')||{}).value, tag:(()=>{const x=document.querySelector('[data-wl-mt-draft]'); return x && !x.hidden ? x.innerText : null;})()})")
        check(f"{tag} 3 refresh without saving → Edit with the draft + amber 'Unsaved draft · Save / Discard' tag", r["mode"] == "edit" and r["exit"] == "draft exit text" and (r["why"] or "").startswith("multi") and r["tag"] and "Unsaved draft" in r["tag"] and "Discard" in r["tag"], r)
        # saved item with a draft → opens in edit with the draft
        view(page, "TXB")
        page.locator("[data-wl-mt-edit]").click(); settle(page, 300)
        page.fill("[data-wl-mt-exit]", "TXB draft exit"); page.dispatch_event("[data-wl-mt-exit]", "input"); settle(page, 1400)
        reload(page); view(page, "TXB")
        check(f"{tag} 3 saved thesis + unsaved draft → opens in Edit with the draft (not Read)", mode(page, "TXB") == "edit" and js(page, "()=>document.querySelector('[data-wl-mt-exit]').value") == "TXB draft exit")
        page.locator("[data-wl-mt-ddisc]").click(); settle(page, 400)
        check(f"{tag} 3 Discard → saved text back (Read card), draft cleared", mode(page, "TXB") == "read" and "saved exit" in js(page, "()=>document.querySelector('[data-wl-mt-rexit]').innerText") and ls(page, "TXB") == {}, [mode(page, "TXB"), ls(page, "TXB")])
        # ── 4 Save → read card + homework ──
        view(page, "TXA")
        page.fill("[data-wl-mt-why]", "why for A"); page.dispatch_event("[data-wl-mt-why]", "input")
        page.fill("[data-wl-mt-exit]", "exit for A"); page.dispatch_event("[data-wl-mt-exit]", "input")
        rd0 = js(page, "()=>wlReady('TXA')")
        page.locator("[data-wl-mt-save]").click(); settle(page, 700)
        st = js(page, "()=>({ready:wlReady('TXA'), my:wlItemOf('TXA').my_thesis, mode:document.querySelector('[data-wl-mt=TXA]').dataset.wlMtMode})")
        check(f"{tag} 4 only Save marks it done: before Save not Ready → after Save Ready, stored, Read card", rd0 is False and st["ready"] is True and st["my"]["why"] == "why for A" and st["mode"] == "read" and ls(page, "TXA") == {}, [rd0, st])
        # ── 5 read card contents ──
        view(page, "TXB")
        rc = js(page, """()=>{ const g=s=>document.querySelector(s); const c=g('[data-wl-mt]'); return {mode:c.dataset.wlMtMode, why:g('[data-wl-mt-rwhy] .wlMtTx').innerText, exit:g('[data-wl-mt-rexit] .wlMtTx').innerText, nc:g('[data-wl-mt-rnc]').innerText.replace(/\\s+/g,' ').trim(),
          edit:!!g('[data-wl-mt-edit]'), archive:!!g('[data-wl-archive]'), onb:!!g('[data-wl-onb]'), ws:getComputedStyle(g('[data-wl-mt-rwhy] .wlMtTx')).whiteSpace, fs:getComputedStyle(g('[data-wl-mt-rwhy] .wlMtTx')).fontSize,
          editRight:(()=>{const e=g('[data-wl-mt-edit]').getBoundingClientRect(), r=c.getBoundingClientRect(); return r.right-e.right < 24;})()}}""")
        check(f"{tag} 5 Read card: bordered blocks, line breaks kept (pre-wrap), Next check '07 Nov 2026 · Q3 earnings', Edit top-right, Onboarding line kept, no Archive… button", rc["mode"] == "read" and rc["why"] == "saved why line one\nsecond line" and rc["ws"] == "pre-wrap" and rc["nc"] == "Next check 07 Nov 2026 · Q3 earnings" and rc["edit"] and rc["editRight"] and rc["onb"] and not rc["archive"], rc)
        check(f"{tag} 5 Read text size = Edit text size = --read-fs", abs(float(rc["fs"][:-2]) - ref) < .1, [rc["fs"], ref])
        menu = js(page, "()=>{ wlMenu = wlSel; renderWatchlist(); return [...document.querySelectorAll('[role=menuitem]')].map(x=>x.innerText.trim()); }")
        check(f"{tag} 5 Archive… still available in the stock ⋯ menu", any("rchive" in m_ for m_ in menu), menu)
        js(page, "()=>{ wlMenu=''; renderWatchlist(); }")
        js(page, "()=>{ wlShowArch = true; }"); view(page, "TXD")
        check(f"{tag} 5 archived stock: Restore stays on the card", js(page, "()=>!!document.querySelector('[data-wl-mt] [data-wl-restore]')"))
        js(page, "()=>{ wlShowArch = false; }"); view(page, "TXC")
        e = js(page, "()=>({empty:document.querySelector('[data-wl-mt-rexit]').innerText.replace(/\\s+/g,' ').trim(), nc:document.querySelector('[data-wl-mt-rnc]').innerText.replace(/\\s+/g,' ').trim()})")
        check(f"{tag} 5 empty field → muted 'Not written yet · Write ›'", e["empty"].endswith("Not written yet · Write ›"), e)
        page.locator("[data-wl-mt-write]").click(); settle(page, 300)
        check(f"{tag} 5 'Write ›' opens Edit", mode(page, "TXC") == "edit")
        page.locator("[data-wl-mt-cancel]").click(); settle(page, 300)
        check(f"{tag} 5 Cancel (nothing changed) → back to Read with no prompt", mode(page, "TXC") == "read" and not confirms(page), confirms(page))
        # ── 6 keyboard ──
        view(page, "TXB"); page.locator("[data-wl-mt-edit]").click(); settle(page, 300)
        page.fill("[data-wl-mt-why]", "via cmd enter"); page.dispatch_event("[data-wl-mt-why]", "input")
        page.focus("[data-wl-mt-why]"); page.keyboard.press("Control+Enter"); settle(page, 700)
        check(f"{tag} 6 Ctrl/Cmd+Enter = Save", mode(page, "TXB") == "read" and js(page, "()=>wlItemOf('TXB').my_thesis.why") == "via cmd enter")
        page.locator("[data-wl-mt-edit]").click(); settle(page, 300)
        cf_reset(page); page.focus("[data-wl-mt-why]"); page.keyboard.press("Escape"); settle(page, 400)
        check(f"{tag} 6 Esc with no change → Cancel, no confirm", mode(page, "TXB") == "read" and not confirms(page), confirms(page))
        page.locator("[data-wl-mt-edit]").click(); settle(page, 300)
        page.fill("[data-wl-mt-why]", "changed but not saved"); page.dispatch_event("[data-wl-mt-why]", "input")
        cf_reset(page, False); page.focus("[data-wl-mt-why]"); page.keyboard.press("Escape"); settle(page, 400)
        check(f"{tag} 6 Esc after a change → asks to confirm; 'No' keeps editing", mode(page, "TXB") == "edit" and len(confirms(page)) == 1 and js(page, "()=>document.querySelector('[data-wl-mt-why]').value") == "changed but not saved", confirms(page))
        cf_reset(page, True); page.focus("[data-wl-mt-why]"); page.keyboard.press("Escape"); settle(page, 400)
        check(f"{tag} 6 Esc → confirm 'Yes' → Cancel; saved text unchanged; draft cleared", mode(page, "TXB") == "read" and js(page, "()=>wlItemOf('TXB').my_thesis.why") == "via cmd enter" and ls(page, "TXB") == {}, ls(page, "TXB"))
        # double-click opens Edit
        page.locator("[data-wl-mt-rwhy]").dblclick(); settle(page, 300)
        check(f"{tag} 6 double-click on the read text opens Edit", mode(page, "TXB") == "edit")
        page.locator("[data-wl-mt-cancel]").click(); settle(page, 300)
        # ── 7 leave-page prompt only with drafts ──
        seen_unload = []
        page.on("dialog", lambda d: seen_unload.append(d.type) if d.type == "beforeunload" else None)
        view(page, "TXB"); reload(page)
        n_clean = len([x for x in seen_unload if x == "beforeunload"])
        view(page, "TXB"); page.locator("[data-wl-mt-edit]").click(); settle(page, 300)
        page.fill("[data-wl-mt-why]", "dirty"); page.dispatch_event("[data-wl-mt-why]", "input")
        reload(page)
        n_dirty = len([x for x in seen_unload if x == "beforeunload"])
        check(f"{tag} 7 leave-page prompt appears only with an unsaved draft (clean reload: {n_clean} · dirty reload: {n_dirty - n_clean})", n_clean == 0 and n_dirty - n_clean >= 1, [n_clean, n_dirty])
        view(page, "TXB"); page.locator("[data-wl-mt-ddisc]").click(); settle(page, 300)
        # ── shots ──
        view(page, "TXA"); page.locator("[data-wl-mt-edit]").click() if mode(page, "TXA") == "read" else None; settle(page, 300)
        js(page, "()=>document.querySelector('[data-wl-mt]').scrollIntoView({block:'start'})")
        C.shot(page, f"tx1-thesis-edit-{w}.png")
        view(page, "TXB"); js(page, "()=>document.querySelector('[data-wl-mt]').scrollIntoView({block:'start'})")
        C.shot(page, f"tx1-thesis-read-{w}.png")
        page.emulate_media(color_scheme="dark"); settle(page, 300)
        js(page, "()=>document.querySelector('[data-wl-mt]').scrollIntoView({block:'start'})")
        C.shot(page, f"tx1-thesis-read-dark-{w}.png")
        view(page, "TXA"); page.locator("[data-wl-mt-edit]").click() if mode(page, "TXA") == "read" else None; settle(page, 300)
        page.fill("[data-wl-mt-why]", "draft\n\ntext"); page.dispatch_event("[data-wl-mt-why]", "input")
        js(page, "()=>document.querySelector('[data-wl-mt]').scrollIntoView({block:'start'})")
        C.shot(page, f"tx1-thesis-edit-dark-{w}.png")
        page.emulate_media(color_scheme="light")
        check(f"{tag} no horizontal overflow · no console/page errors", C.overflow(page) <= 0 and not [x for x in ce if "Failed to load" not in x] and not pe, [C.overflow(page), ce[:2], pe[:2]])
        page.reload() if False else None
    finally:
        b.close()


def popups(pw, w, h):
    tag = f"[{ENGINE}/popups/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        seed(page); view(page, "TXB")
        ref = js(page, "()=>{ const c=getComputedStyle(document.querySelector('[data-wl-mt-rwhy] .wlMtTx')); return [c.fontSize, c.lineHeight]; }") if mode(page, "TXB") == "read" else None
        # reference = Watchlist stock-data body (.ltMd) — compare with the token itself
        tok = js(page, "()=>{ const d=document.createElement('div'); d.className='ltMd'; document.body.appendChild(d); const c=getComputedStyle(d); const r=[c.fontSize,c.lineHeight]; d.remove(); return r; }")
        check(f"{tag} reference .ltMd (Watchlist stock-data body) = --read-fs/--read-lh", abs(float(tok[0][:-2]) - 15.64) < .05 and abs(float(tok[1][:-2]) / float(tok[0][:-2]) - 1.65) < .01, tok)
        # Macro Playbook asset popup (Brent)
        js(page, """()=>{ window.pbVerById = ()=>({assets:{BRENT:{stance:'bull', confidence:'med', why:'Supply tight, demand holds up — long enough text to wrap onto several lines in the popup body.', posture:'Hold core, add on dips', change_if:'OPEC adds more than 1M bpd', if_alt:'Fade rallies', drivers:[]}}, view:{pillars:[]}}); pbAssetSheet('v1','BRENT'); }"""); settle(page, 400)
        pb = js(page, """()=>{ const o={}; ['.pbSecV','.pbSecK'].forEach(s=>{ const e=document.querySelector('.pb-sheet '+s); if(e){ const c=getComputedStyle(e); o[s]=[c.fontSize,c.lineHeight]; } }); const sh=document.querySelector('.pb-sheet .ui-sheet'); o.w=sh.getBoundingClientRect().width; o.sx=document.documentElement.scrollWidth-innerWidth; return o; }""")
        check(f"{tag} Brent popup body = Watchlist reference size/line-height", pb[".pbSecV"] == tok, [pb, tok])
        check(f"{tag} popup labels not smaller than 12px · desktop width ≤ 720 · no horizontal scroll", float(pb[".pbSecK"][0][:-2]) >= 12 and pb["w"] <= 721 and pb["sx"] <= 0, pb)
        C.shot(page, f"tx1-brent-{w}.png")
        js(page, "()=>pbSheetClose()")
        js(page, """()=>{ window.stkLists=()=>({wl:['AAA'],cand:['CCC']}); window.stkLatest=()=>({id:'e1', period_start:'2026-11-02', period_end:'2026-11-06', asof:'2026-11-07T10:00:00+07:00', sources:{}, stocks:{
            AAA:{coverage:'ok', status:'review', headline_th:'AAA headline sample text', happened_th:'Fact sample paragraph that is long enough to wrap in the panel body.', why_th:'Interpretation sample paragraph that is long enough to wrap too.', monitor_th:'Monitor sample', groups:['watchlist']},
            CCC:{coverage:'ok', status:'info', happened_th:'Another fact', groups:['candidate']}}}); stkExp.add('AAA'); stkOpenView(); }"""); settle(page, 500)
        sk = js(page, """()=>{ const o={}; [['.stkB','body'],['.stkB div:not(.stkK)','text'],['.stkHl','headline'],['.stkK','label']].forEach(([s,n])=>{ const e=document.querySelector((document.querySelector('.stk-panel')?'.stk-panel ':'.stk-sheet ')+s); if(e){ const c=getComputedStyle(e); o[n]=[c.fontSize,c.lineHeight]; } }); o.sx=document.documentElement.scrollWidth-innerWidth; return o; }""")
        check(f"{tag} news panel/sheet body (.stkB) = Watchlist reference size/line-height", sk.get("body") == tok, [sk, tok])
        check(f"{tag} news headline/labels not smaller than 12.5px · no horizontal scroll", float(sk["label"][0][:-2]) >= 12.5 and (not sk.get("headline") or float(sk["headline"][0][:-2]) >= float(tok[0][:-2]) - .01) and sk["sx"] <= 0, sk)
        C.shot(page, f"tx1-news-{w}.png")
        page.emulate_media(color_scheme="dark"); settle(page, 300)
        C.shot(page, f"tx1-news-dark-{w}.png")
        js(page, "()=>stkCloseView()")
        js(page, """()=>{ window.pbVerById = ()=>({assets:{BRENT:{stance:'bull', why:'Supply tight, demand holds up.', posture:'Hold core', change_if:'OPEC adds more than 1M bpd', drivers:[]}}, view:{pillars:[]}}); pbAssetSheet('v1','BRENT'); }"""); settle(page, 400)
        C.shot(page, f"tx1-brent-dark-{w}.png")
        check(f"{tag} no console/page errors", not [x for x in ce if "Failed to load" not in x] and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def blocked(pw, w, h):
    tag = f"[{ENGINE}/lsblocked/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        seed(page)
        stacks = []; page.on("pageerror", lambda e: stacks.append(str(e.stack or e)))   # (backup-reminder bkDue elsewhere also reads localStorage unguarded — pre-existing, not TX1)
        js(page, """()=>{ const bad=()=>{ throw new Error('blocked'); }; try{ Storage.prototype.setItem=bad; Storage.prototype.getItem=bad; Storage.prototype.removeItem=bad; }catch(e){} }""")
        view(page, "TXA")
        page.fill("[data-wl-mt-why]", "no storage why"); page.dispatch_event("[data-wl-mt-why]", "input")
        page.fill("[data-wl-mt-exit]", "no storage exit"); page.dispatch_event("[data-wl-mt-exit]", "input"); settle(page, 1400)
        page.locator("[data-wl-mt-save]").click(); settle(page, 700)
        check(f"{tag} localStorage blocked → typing, autosave timer, Save all still work (no crash)", mode(page, "TXA") == "read" and js(page, "()=>wlItemOf('TXA').my_thesis.why") == "no storage why" and not [x for x in stacks if "wlMt" in x or "wlOnb" in x], stacks[:2])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)):
            tests(pw, w, h); popups(pw, w, h); blocked(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
    sys.exit(1 if bad else 0)
