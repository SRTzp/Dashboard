#!/usr/bin/env python3
"""HW1c — facts-only living-thesis import + Import › on the Homework page.
Run: python3 tests/run_tests_hw1c.py"""
import sys, json, copy
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import hw1_common as H

TXT = "(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }"
VIS = "(s)=>{ const e = document.querySelector(s); if(!e) return false; const r = e.getBoundingClientRect(), c = getComputedStyle(e); return r.width>0 && r.height>0 && c.visibility!=='hidden' && c.display!=='none'; }"
SNAP = "(s)=>{ const it = wlItemOf(s); return JSON.stringify({th: it.thesis, log: it.thesis_log, hist: it.thesis_history, hits: it.thesis_hits}); }"


def facts_json(sym, **kw):
    f = copy.deepcopy(H.MOM); f["asOf"] = kw.pop("asOf", "Q3 FY26")
    o = {"schema": "living-thesis@1", "sym": sym, "mode": "facts", "date": "2026-11-20", "summary": {"biz": "AI data-center connectivity"}, "facts": f,
         "catalysts": [{"date": "2026-12-10", "event": "ZQNEWCAT Q4 results", "date_status": "confirmed"}]}
    o.update(kw); return json.dumps(o)


def imp(page, sym, text, save=True):
    js(page, "([s,t])=>{ ltImportOpen(s); document.getElementById('ltJson').value = t; ltImpCheck(); }", [sym, text]); page.wait_for_timeout(200)
    err = js(page, TXT, "#ltErr") or ""
    if save and not err:
        js(page, "()=>ltImpSave()"); page.wait_for_timeout(400)
    return err


def run(pw, w, h):
    tag = "[%s]" % w; phone = w < 1024
    b, page, pe = H.open_hw(pw, w, h)
    try:
        # ---- 1 · facts-only on a stock WITH a full thesis (COST)
        before = json.loads(js(page, SNAP, "COST"))
        err = imp(page, "COST", facts_json("COST", asOf="Q4 FY26"), save=False)
        check(f"{tag} facts-only on COST: valid, no 'No sections'", err == "" and "No sections" not in err, err)
        prev = js(page, TXT, "#ltPrev") or ""
        check(f"{tag} preview: Fact Sheet only + thesis unchanged", "Fact Sheet only" in prev and "unchanged" in prev, prev)
        js(page, "()=>ltImpSave()"); page.wait_for_timeout(400)
        after = json.loads(js(page, SNAP, "COST"))
        toast = js(page, "()=>[...document.querySelectorAll('body *')].map(e=>e.children.length?'':e.textContent).filter(t=>t.indexOf('Fact Sheet updated')===0)[0]||''")
        check(f"{tag} toast names what changed", toast == "Fact Sheet updated (Q4 FY26) · missing: cash, exposure, more · made for momentum, shown as Compounder · your notes and the AI thesis are unchanged", toast)
        check(f"{tag} sheet closed by itself", js(page, "()=>ltImp === null && !document.getElementById('ltOverlay').classList.contains('show')"))
        keep = ["summary", "sections", "kpi", "tripwires", "evidence", "tier_inputs", "sources", "gaps", "date", "terms"]
        check(f"{tag} COST: summary/sections/kpi/tripwires/evidence untouched", all(before["th"].get(k) == after["th"].get(k) for k in keep))
        check(f"{tag} COST: facts replaced", after["th"]["facts"]["asOf"] == "Q4 FY26")
        check(f"{tag} COST: log +1 'facts updated (Q4 FY26)'", len(after["log"]) == len(before["log"]) + 1 and after["log"][-1]["new"] == "facts updated (Q4 FY26)", after["log"][-1:])
        check(f"{tag} COST: new catalyst added once, old kept", len(after["th"]["catalysts"]) == len(before["th"]["catalysts"]) + 1)
        check(f"{tag} COST: history/hits untouched", before["hist"] == after["hist"] and before["hits"] == after["hits"])
        js(page, "()=>ltSheetClose()")
        imp(page, "COST", facts_json("COST", asOf="Q4 FY26"))
        a2 = json.loads(js(page, SNAP, "COST"))
        check(f"{tag} COST: same catalyst is not duplicated", len(a2["th"]["catalysts"]) == len(after["th"]["catalysts"]))
        js(page, "()=>ltSheetClose()")
        # ---- 2 · facts-only on a stock WITHOUT a thesis (WHSE)
        err = imp(page, "WHSE", facts_json("WHSE"))
        check(f"{tag} WHSE: facts-only accepted", err == "", err)
        st = js(page, "()=>{ const it = wlItemOf('WHSE'); return {raw: it.thesis, th: wlThesisOf(it), f: !!ltFacts(it), n: ltCats(it).length, stale: ltStaleWhy(it).length, hot: ltHot(it).length}; }")
        check(f"{tag} WHSE: stored minimal thesis mode=facts, wlThesisOf = none", st["raw"]["mode"] == "facts" and "sections" not in st["raw"] and st["th"] is None and st["f"] and set(st["raw"]) >= {"facts", "summary", "catalysts", "mode"}, st)
        check(f"{tag} WHSE: reads as 'no AI thesis' (no catalysts/stale/hot)", st["n"] == 0 and st["stale"] == 0 and st["hot"] == 0, st)
        check(f"{tag} WHSE: sheet closed by itself", js(page, "()=>ltImp === null"))
        js(page, "()=>ltSheetClose()")
        H.go(page, "WHSE", "ladder")
        body = js(page, "()=>document.querySelector('[data-hw1-page]').innerText") or ""
        check(f"{tag} WHSE: Homework shows the Fact Sheet (full), no 'No sections'", js(page, "()=>document.querySelector('[data-hw1-facts]').dataset.hw1Facts") == "full" and "No sections" not in body)
        js(page, "()=>{ wlMtIn('WHSE','why','I believe this', null); }")
        check(f"{tag} WHSE: Compare with thesis hidden", not js(page, VIS, "[data-hw1-cmp-btn]"))
        js(page, "()=>{ hwBack(); wlOpen('WHSE'); wlMenu = 'WHSE'; renderWatchlist(); }"); page.wait_for_timeout(250)
        menu = js(page, TXT, ".ltMenu") or ""
        check(f"{tag} WHSE: ⋯ menu has no 'Full thesis', keeps Import/Edit/Archive", "Full thesis" not in menu and "Import JSON" in menu and "Import thesis" not in menu and "Edit" in menu, menu)
        check(f"{tag} WHSE: Today reminder treats it as missing", js(page, "()=>wlThesisOf(wlItemOf('WHSE')) === null && !(wlItems.filter(x=>wlThesisOf(x)).some(x=>x.ticker==='WHSE'))"))
        js(page, "()=>{ wlMenu=''; renderWatchlist(); }")
        # ---- 3 · invalid facts-only -> error, nothing changes
        bad = json.loads(facts_json("AAPL")); del bad["facts"]["biz"]
        b0 = js(page, SNAP, "AAPL")
        err = imp(page, "AAPL", json.dumps(bad))
        check(f"{tag} invalid facts-only -> error naming the problem", "facts.biz" in err and "nothing else" in err, err)
        check(f"{tag} invalid facts-only -> nothing saved, sheet stays open with the error", js(page, SNAP, "AAPL") == b0 and js(page, "()=>!!ltImp && document.getElementById('ltOverlay').classList.contains('show')"))
        js(page, "()=>ltSheetClose()")
        err = imp(page, "AAPL", json.dumps({"schema": "living-thesis@1", "sym": "AAPL", "summary": {}}), save=False)
        check(f"{tag} no sections and no facts -> still 'No sections'", err == "No sections", err)
        err = imp(page, "AAPL", facts_json("PLTR"), save=False)
        check(f"{tag} facts-only for another stock -> bound error", "not AAPL" in err, err)
        js(page, "()=>ltSheetClose()")
        # ---- 4 · full JSON unchanged behaviour
        full = H.C.thesis_fields("AVGO")["thesis"]; full = dict(full); full["sym"] = "ZZ"; full["log"] = []
        p = js(page, "(t)=>ltParse(t,'ZZ')", json.dumps(full))
        check(f"{tag} full JSON parses as before (th with sections, not factsOnly)", "err" not in p and not p.get("factsOnly") and "sections" in p["th"], p.get("err"))
        # ---- 5 · Import › from the Homework page
        H.go(page, "ZZ", "ladder")
        H.fill(page, "why", "ZQDRAFT keep me") if not phone else (js(page, "()=>hw1SegSet('ZZ','mine')"), H.fill(page, "why", "ZQDRAFT keep me"))
        if phone: js(page, "()=>hw1SegSet('ZZ','facts')"); page.wait_for_timeout(150)
        fb = js(page, TXT, "[data-hw1-facts]") or ""
        check(f"{tag} fallback: 'No Fact Sheet yet' + 2 numbered steps", "No Fact Sheet yet" in fb and "1. Copy the command and run it in Claude: living-thesis facts ZZ" in fb and "2. Paste the JSON it gives you: Import JSON ›" in fb, fb)
        check(f"{tag} fallback: no other import button or link", js(page, "()=>document.querySelectorAll('[data-hw1-page] [data-hw1-import]').length") == 0 and js(page, "()=>document.querySelectorAll('[data-hw1-import-link]').length") == 1)
        js(page, "()=>{ window.__cp = null; Object.defineProperty(navigator, 'clipboard', {value:{writeText:(t)=>{ window.__cp = t; return Promise.resolve(); }}, configurable:true}); document.querySelector('[data-hw1-copycmd]').click(); }"); page.wait_for_timeout(300)
        check(f"{tag} command chip copies 'living-thesis facts ZZ' + toast Copied", js(page, "()=>window.__cp") == "living-thesis facts ZZ compounder" and js(page, "()=>[...document.querySelectorAll('body *')].some(e=>!e.children.length && e.textContent==='Copied')"))
        if phone: check(f"{tag} phone: chip and Import JSON › >= 44px", js(page, "()=>[...document.querySelectorAll('[data-hw1-copycmd],[data-hw1-import-link]')].every(b=>b.getBoundingClientRect().height >= 44)"))
        js(page, "()=>document.querySelector('[data-hw1-import-link]').click()"); page.wait_for_timeout(250)
        check(f"{tag} link opens the import sheet bound to ZZ", "ZZ" in (js(page, TXT, "#ltModal h3") or "") and js(page, "()=>ltImp && ltImp.bound") == "ZZ")
        js(page, "()=>ltSheetClose()")
        js(page, "(t)=>{ ltImportOpen('ZZ'); document.getElementById('ltJson').value = t; ltImpCheck(); ltImpSave(); }", facts_json("ZZ")); page.wait_for_timeout(400)
        check(f"{tag} after import: still on the Homework page", js(page, "()=>!!document.querySelector('[data-hw1-page=\"ZZ\"]') && hw1On()"))
        check(f"{tag} after import: draft kept", js(page, "()=>wlItemOf('ZZ') && (hw1Vals(wlItemOf('ZZ')).why||'').indexOf('ZQDRAFT') === 0"))
        page.wait_for_timeout(200)
        check(f"{tag} after import: Fact Sheet shown, header button is 'Update ›' with tooltip", js(page, "()=>document.querySelector('[data-hw1-facts]').dataset.hw1Facts") == "full" and js(page, "()=>{ const b = document.querySelector('.hw1-fh [data-hw1-import]'); return !!b && b.innerText.trim() === 'Update ›' && b.title === 'Paste a newer living-thesis JSON'; }"))
        check(f"{tag} after import: the numbered steps are gone", js(page, "()=>!document.querySelector('[data-hw1-nofacts]') && !document.querySelector('[data-hw1-import-link]')"))
        js(page, "()=>document.querySelector('.hw1-fh [data-hw1-import]').click()"); page.wait_for_timeout(200)
        check(f"{tag} Update › opens the sheet bound to ZZ", js(page, "()=>ltImp && ltImp.bound") == "ZZ")
        js(page, "()=>ltSheetClose()")
        if phone:
            check(f"{tag} phone: Facts tab holds the Import ›", js(page, "()=>document.querySelector('[data-hw1-page]').dataset.hw1Show") in ("facts", "mine"))
        check(f"{tag} no console / page errors", not pe, pe)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY HW1c: {len(results) - len(bad)}/{len(results)} pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
