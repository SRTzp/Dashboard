#!/usr/bin/env python3
"""Bug-hunt fuzz (REPORT ONLY) — feeds malformed/empty/wrong-schema/huge JSON into every importer's pure validator/parser (+ UI check path for idea & living-thesis)
inside the fixture app (mock Firebase; external http(s) aborted). Logs: validator throws, accept-then-render crash, hostile strings reaching the DOM unescaped,
and accepted-but-malformed payloads. Output: docs/reports/bughunt-fuzz.txt   Run: python3 tests/fuzz_imports.py"""
import os, re, sys, json, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
import run_tests_phase38 as P38, run_tests_phase39 as P39
import run_tests_phase102 as P102, run_tests_phase100 as P100, run_tests_phase68 as P68, run_tests_phase103 as P103

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "reports", "bughunt-fuzz.txt")
XSS = '<img src=x onerror="window.__xss=(window.__xss||0)+1">'
def fx(n): return json.load(open(os.path.join(HERE, "fixtures", n)))
BASES = {
    "idea":   (fx("idea_semis.json"), "ideaParse"),
    "lt":     (fx("avgo_thesis_v3.json"), "ltParse"),
    "weekly": (P100.sample(), "Calc.wiValidate"),
    "stknews":(P102.stock_doc(), "Calc.stkValidate"),
    "playbook":(P68.v2obj(), "Calc.pbValidate"),
    "sector": (P103.new_doc() if hasattr(P103, "new_doc") else {}, "sdValidate"),
}
def backup_base(): return {"_meta": {"app": "trading-dashboard", "schema": 3, "uid": "x", "activeAccount": "main", "accounts": [{"id": "main", "name": "m"}]}, "doc": {"books": {"main": {"trades": [], "settings": {}}}}}
BASES["backup"] = (backup_base(), "bkRestoreParse")

def mutations(base):
    yield "empty", ""
    yield "whitespace", "   \n "
    yield "null", "null"; yield "array", "[]"; yield "number", "123"; yield "string", '"x"'; yield "{}", "{}"
    yield "truncated", json.dumps(base)[: max(5, len(json.dumps(base)) // 2)]
    yield "garbage", "not json at all {{{"
    yield "wrong-schema", json.dumps({**base, "schema": "other@9"}) if isinstance(base, dict) else "{}"
    yield "no-schema", json.dumps({k: v for k, v in base.items() if k != "schema"})
    yield "fenced", "```json\n" + json.dumps(base) + "\n```"
    yield "huge-300KB", json.dumps({**base, "pad": "A" * 300_000})
    yield "huge-5MB", json.dumps({**base, "pad": "A" * 5_000_000})
    yield "deep-nest", '{"a":' * 5000 + "1" + "}" * 5000
    yield "proto-pollution", json.dumps(base)[:-1] + ', "__proto__": {"polluted": 1}, "constructor": {"prototype": {"polluted2": 1}}}'
    for k in list(base.keys()):
        if k == "schema": continue
        for tag, val in (("null", None), ("num", 12345), ("array", [None, 1, "x"]), ("obj", {}), ("str-xss", XSS), ("neg", -1), ("huge-str", "Z" * 200000), ("nan-str", "NaN")):
            yield f"{k}={tag}", json.dumps({**base, k: val})
    # nested: swap each value inside first-level dict children to null (one pass)
    for k, v in base.items():
        if isinstance(v, dict):
            for k2 in list(v.keys())[:6]:
                yield f"{k}.{k2}=null", json.dumps({**base, k: {**v, k2: None}})
                yield f"{k}.{k2}=xss", json.dumps({**base, k: {**v, k2: XSS}})
        if isinstance(v, list) and v:
            yield f"{k}[0]=null", json.dumps({**base, k: [None] + v[1:]})
            yield f"{k}=[[]]", json.dumps({**base, k: [[]]})

CALL = """([fn, text])=>{
  const f = fn.startsWith('Calc.') ? Calc[fn.slice(5)].bind(Calc) : window[fn];
  let r; try{ r = f===undefined ? {__nofn:1} : (fn==='ltParse'? f(text, null) : fn==='sdValidate' ? f(text,'AVGO') : fn==='Calc.pbValidate' ? f(text, new Date('2026-10-01T05:00:00Z')) : fn==='Calc.wiValidate' ? f(text, {}) : f(text)); }
  catch(e){ return {threw:String(e&&e.message||e).slice(0,160)}; }
  const err = r && (r.err || (r.errors&&r.errors.length) || (r.ok===false)); 
  return {accepted: !err, keys: r? Object.keys(r).slice(0,6):[] , nofn: r&&r.__nofn};
}"""

def main():
    issues = {}
    def log(kind, name, mut, detail=""):
        issues.setdefault((kind, name), []).append(mut + (f" :: {detail}" if detail else ""))
    with sync_playwright() as pw:
        doc = P38.doc38(clean=False)
        browser, ctx, page, ce, pe, dlg = P39.launch(pw, 1024, 800, doc=doc, clean=False, extra=None)
        page.route(re.compile(r"^https?://"), lambda r: r.fallback() if re.search(r"gstatic\.com/firebasejs|fonts\.(googleapis|gstatic)|fundflow\.json|er-api|twelvedata", r.request.url) else r.abort())
        page.on("dialog", lambda d: d.dismiss())
        total = 0
        for name, (base, fn) in BASES.items():
            seen_err = len(pe)
            for mut, text in mutations(base):
                total += 1
                try: r = page.evaluate(CALL, [fn, text])
                except Exception as ex: log("eval-crash", name, mut, str(ex)[:120]); continue
                if r.get("nofn"): log("function-missing", name, fn); break
                if r.get("threw"): log("validator-throws", name, mut, r["threw"]); continue
                if r.get("accepted") and re.match(r"^(empty|whitespace|null|array|number|string|garbage|truncated|wrong-schema|no-schema|deep-nest)", mut):
                    log("accepted-bad-input", name, mut)
                if r.get("accepted") and re.search(r"=(null|num|array|obj|neg)$|=\[\[\]\]$|\[0\]=null|\.[^=]+=null$", mut):
                    log("accepted-wrong-type-field", name, mut)
                if r.get("accepted") and mut.startswith("huge-") and name in ("idea", "lt") and "300KB" not in mut and "5MB" not in mut:
                    log("accepted-huge-field", name, mut)
                if r.get("accepted") and mut in ("huge-300KB", "huge-5MB") and name in ("idea", "lt"):
                    log("size-limit-bypass", name, mut)
            for m in pe[seen_err:]: log("uncaught", name, m[:140])
        # UI path: idea + living thesis modals, check then save into MOCK db, then re-render whole app
        for name, opener, ta, chk, sv in (("idea", "ideaImportOpen()", "#ideaJson", "ideaImpCheck()", "ideaImpSave()"), ("lt", "ltImportOpen('AVGO')", "#ltJson", "ltImpCheck()", "ltImpSave()")):
            base = BASES[name][0]
            cases = [("xss-name", {**base, "name": XSS, "sym": base.get("sym", "AVGO")}), ("null-chain", {**base, "chain": None}), ("segments-null", {**base, "chain": {"segments": [None, 5, "x"]}}),
                     ("summary-null-items", {**base, "summary": {**(base.get("summary") or {}), "bullets": [None]}} if name == "lt" else {**base, "idea": {"x": XSS}})]
            for cn, obj in cases:
                try:
                    page.evaluate(f"()=>{opener}"); page.wait_for_timeout(120)
                    if not page.locator(ta).count(): log("modal-missing", name, cn); continue
                    page.fill(ta, json.dumps(obj)); before = len(pe)
                    page.evaluate(f"()=>{chk}"); page.wait_for_timeout(100)
                    err = page.evaluate("()=>(document.querySelector('[data-idea-err],.ltErr')||{}).textContent||''")
                    if not err:
                        page.evaluate(f"()=>{{ try{{ {sv} }}catch(e){{ window.__svErr=String(e) }} }}"); page.wait_for_timeout(400)
                        page.evaluate("()=>render()"); page.wait_for_timeout(200)
                        for sw in ("watch", "plan", "today"):
                            page.evaluate(f"()=>switchTab('{sw}')"); page.wait_for_timeout(150)
                        log("ui-accepted-and-saved", name, cn, f"newPageErrors={len(pe)-before}")
                    for m in pe[before:]: log("ui-uncaught-after-import", name, cn, m[:120])
                    if page.evaluate("()=>window.__xss||0"): log("XSS-executed", name, cn)
                    page.evaluate("()=>{const o=document.getElementById('ltOverlay'); if(o) o.classList.remove('show')}")
                except Exception as ex: log("ui-crash", name, cn, str(ex)[:120])
        browser.close()
    lines = []
    for (kind, name), muts in sorted(issues.items()):
        lines.append(f"[{kind}] {name}: {len(muts)} cases — e.g. {'; '.join(muts[:5])}")
    open(OUT, "w").write(f"# fuzz_imports — {total} validator calls, {len(lines)} issue groups\n" + "\n".join(lines) + "\n")
    print(open(OUT).read()[:3000])
if __name__ == "__main__": main()
