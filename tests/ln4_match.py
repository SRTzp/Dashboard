#!/usr/bin/env python3
"""LN4 visual match pass — renders the app screens (1440 + 390) next to the briefs' mockups → tests/screenshots/ln4-match-*.png
run: LN4RAW=dir python3 ln4_match.py"""
import sys, os
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase24 as P24
import run_tests_phase106 as T
import run_tests_phase120 as P120
js, settle = C.js, T.settle
RAW = os.environ.get('LN4RAW', '/tmp/ln4raw')
os.makedirs(RAW, exist_ok=True)


def app(pw, w, h):
    cards = {
        "ccAM": P24.card("ccAM", "main", "AMD", plan={"entry": 182.5, "stop": 170}, px=170, pxDate="2026-10-01"),
        "ccNV": P24.open_card("ccNV", "tNV", ticker="NVDA", acct="main", qty=10, entry=171.4, sl=168, tier="A", lots=[{"n": 1, "date": "2026-09-10", "px": 171.4, "qty": 10, "f": 1, "stop": 168}]),
        "ccAV": P24.card("ccAV", "main", "AVGO", plan={"entry": 341.2, "stop": 320}, px=330, pxDate="2026-10-01", track="ladder"),
    }
    b, page, ce, pe = T.launch(pw, w, h, iso=T.NOW, picks=("XAUUSD",), weekly=False)
    sh = lambda n, sel=None: (page.locator(sel).first.screenshot(path=f"{RAW}/{n}-{w}.png") if sel else page.screenshot(path=f"{RAW}/{n}-{w}.png", full_page=True))
    try:
        import run_tests_phase13 as P13
        P24.set_ff(page, P24.ff_json(True, True))
        js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }", [P13.T("tNV", "core", "open", sym="NVDA", entry=171.4, sl=168, qty=10, cur="USD", date="2026-09-10")])
        for cid, c in cards.items():
            page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
        js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 700)
        P120.ps_on(page)
        page.add_style_tag(content='*{animation:none!important;transition:none!important}')
        js(page, "()=>{ const cc=coreCardsList.find(x=>x.ticker==='AMD'); coreWrite(cc.id,{ln4:{placedAt:new Date().toISOString()}}); }"); settle(page, 400)
        T.go_today(page)
        # same sample data as today-v5.html: HOT sectors, TODAY events, To do chips, Exec
        js(page, """()=>{ const n = Date.now(); window.ln4HotSectors = ()=>[{etf:'XLK',name:'Semis',k:'lead'},{etf:'XLU',name:'Power & Grid',k:'lead'},{etf:'XLI',name:'Defense',k:'fresh'}];
          window.td3NewsModel = ()=>({hasDocs:true, now:n, list:[{id:'e1', ts:n-3600000, e:{title:'CN CPI'}, assets:['XAUUSD']},{id:'e2', ts:n+(3*3600+12*60)*1000, e:{title:'US CPI'}, assets:['XAUUSD','BTCUSD']},{id:'e3', ts:n+9*3600000, e:{title:'US PMI'}, assets:['XAUUSD']}]});
          window.ftList = ()=>[{sym:'AVGO', over:2, left:0}]; window.sk1Items = ()=>[]; }""")
        js(page, "()=>glWrite(S=>{ S.ln4 = {valid:{a:{day:'2026-09-28',sym:'AMD',at:'2026-09-28T01:00:00Z',via:'working'},b:{day:'2026-09-29',sym:'NVDA',at:'2026-09-29T01:00:00Z',via:'working'},c:{day:'2026-09-30',sym:'ETN',at:'2026-09-30T01:00:00Z',via:'working',missed:1}}}; })"); settle(page, 400)
        js(page, "()=>todayRefresh(true)"); settle(page, 500)
        sh("today")
        js(page, """()=>{ switchTab('watch'); wlSetView('cand');
          const D = {MU:[3,'Volume spike'], LRCX:[5,'Earnings spike'], VRT:[2,'Event: AI power'], DDOG:[1,'TradingView'], FTNT:[9,''], GLBE:[14,'Volume spike']};
          const day = 86400000, now = new Date('2026-10-01T05:00:00Z').getTime();
          Object.keys(D).forEach(k=>td3MetaWrite(k, Object.assign({cand_at:new Date(now - D[k][0]*day).toISOString()}, D[k][1] ? {source:D[k][1]} : {})));
          window.wlRowsAll = ()=>({wl:[], cand:Object.keys(D).map(s=>({sym:s, port:'cand', market:'US', item:null, w:null, d:null, cInfo:[]}))}); renderWatchlist(); }"""); settle(page, 600); sh("watch")
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); }"); settle(page, 600); sh("plan-list")
        js(page, "()=>coreNewOpen('main',{ticker:'AAA'})"); settle(page, 700); P120.fill(page, 182.5, 170)
        sh("core-form", ".core-sheet")
        page.screenshot(path=f"{RAW}/core-form-page-{w}.png")
        js(page, "()=>coreSheetClose()")
        iid = js(page, "()=>satV2NewPlan('XAUUSD','main')"); settle(page, 500)
        js(page, "([i])=>satV2SetDir(i,'Long')", [iid])
        for f_, v in (("entry", 2000), ("sl", 1990), ("tp", 2020)):
            js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, f_, str(v)])
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); settle(page, 700); sh("sat-form", ".ln1-form")
        js(page, "()=>{ switchTab('journal'); }"); settle(page, 1500); sh("journal")
        js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='NVDA'); coreWrite(c.id,{plan:Object.assign({}, c.plan||{entry:171.4,stop:168}, {starter:true, addon:{riskPct:0.3, frac:0.25, cond:'stop>=be'}})}); }"); settle(page, 500)
        js(page, "()=>{ switchTab('mix'); }"); settle(page, 1500); sh("port")
        js(page, "()=>{ openSettings(); }"); settle(page, 600)
        js(page, "()=>{ const e=document.getElementById('ln4SetBox'); if(e) e.scrollIntoView({block:'center'}); }"); settle(page, 300); sh("settings", "#ln4SetBox")
    finally:
        b.close()


PAIRS = {"today": ("today-v5", None), "watch": ("lean-mockup", None), "core-form": ("forms-half", None), "sat-form": ("forms-half", None),
         "plan-list": ("ln4-tabs", None), "journal": ("ln4-tabs", "Journal"), "port": ("ln4-tabs", "Port"), "settings": ("ln4-tabs", "Settings")}
BRIEFS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'briefs')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')


def mocks(pw, w, h):
    b = pw.chromium.launch(); done = {}
    for name, (f, tab) in PAIRS.items():
        p = b.new_page(viewport={'width': w, 'height': h}); p.goto('file://' + os.path.abspath(os.path.join(BRIEFS, f + '.html')))
        if tab: p.get_by_text(tab, exact=True).first.click()
        p.wait_for_timeout(250); path = f"{RAW}/mock-{name}-{w}.png"; p.screenshot(path=path, full_page=True); p.close(); done[name] = path
    b.close(); return done


def compose(pw, w):
    """side-by-side: mockup | app → tests/screenshots/ln4-match-<screen>-<w>.png"""
    os.makedirs(OUT, exist_ok=True); b = pw.chromium.launch()
    for name in PAIRS:
        m, a = f"{RAW}/mock-{name}-{w}.png", f"{RAW}/{name}-{w}.png"
        pg = b.new_page(viewport={'width': w * 2 + 30, 'height': 900})
        html = f'<body style="margin:0;background:#888;display:flex;gap:30px;align-items:flex-start"><div><div style="color:#fff;font:14px sans-serif;padding:4px">mockup</div><img src="file://{m}"></div><div><div style="color:#fff;font:14px sans-serif;padding:4px">app</div><img src="file://{a}"></div></body>'
        hp = f"{RAW}/cmp-{name}-{w}.html"; open(hp, 'w').write(html); pg.goto('file://' + hp)
        pg.wait_for_timeout(300); pg.screenshot(path=f"{OUT}/ln4-match-{name}-{w}.png", full_page=True); pg.close()
    b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            app(pw, w, h); mocks(pw, w, h); compose(pw, w)
