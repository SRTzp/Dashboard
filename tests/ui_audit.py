#!/usr/bin/env python3
"""UA1 — whole-app UI audit (reusable). Playwright, 390x844 / 1280x800 / 1440x900, fixtures + stress data (mock Firebase).
Visits every tab / sub-tab / sheet / form, runs 8 layout rules on the visible DOM, writes docs/reports/UA1-audit.md
+ crops (red outline) to tests/screenshots/ua1/<tag>/.
Run: python3 tests/ui_audit.py [--out docs/reports/UA1-audit.md] [--tag before|after] [--vp 390,1280,1440] [--json out.json]
Rules: 1 word broken mid-word · 2 chip/pill/button wraps · 3 horizontal overflow/clipping · 4 lone control row ·
5 duplicate message in one card · 6 font/tap below minimum · 7 overlap · 8 empty gap > 32px"""
import os, sys, json, re, argparse, collections
_ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]   # the phase modules read argv[1] as the index.html path
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase24 as P24
import run_tests_phase106 as T
import run_tests_phase120 as P120
import run_tests_phase13 as P13

js, settle = C.js, T.settle
ROOT = os.path.abspath(os.path.join(HERE, ".."))
VPS = {390: 844, 1280: 800, 1440: 900}
SHOTS = os.path.join(HERE, "screenshots", "ua1")

RULES = {1: "word broken mid-word", 2: "chip/pill/button wraps", 3: "horizontal overflow / clipped", 4: "lone control row",
         5: "duplicate message", 6: "font / tap target too small", 7: "overlap", 8: "empty gap > 32px"}

CHECK_JS = r"""({vw, scopeSel})=>{
const phone = vw <= 500;
const out = [];
const scope = (scopeSel && document.querySelector(scopeSel)) || document.body;
const vis = e => { try{ if(!e.checkVisibility({checkVisibilityCSS:true})) return false; }catch(_){ if(!e.offsetParent && getComputedStyle(e).position!=='fixed') return false; }
  const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
const cls = e => (e.className && e.className.baseVal===undefined ? e.className : '').toString();
const path = e => { const p=[]; let n=e; while(n && n!==document.body && p.length<4){ let s=n.tagName.toLowerCase(); if(n.id) { s+='#'+n.id; p.unshift(s); break; } const c=cls(n).trim().split(/\s+/).filter(Boolean).slice(0,2).join('.'); if(c) s+='.'+c; p.unshift(s); n=n.parentElement; } return p.join(' > '); };
const txt = e => (e.innerText||e.textContent||'').replace(/\s+/g,' ').trim();
const rectOf = e => { const r=e.getBoundingClientRect(); return {x:r.left+scrollX, y:r.top+scrollY, w:r.width, h:r.height}; };
const add = (rule, e, note, extra) => { out.push(Object.assign({rule, sel:path(e), text:txt(e).slice(0,70), note, rect:rectOf(e)}, extra||{})); };
const SKIP = ['SCRIPT','STYLE','SVG','PATH','BR','OPTION','TEMPLATE','NOSCRIPT','CIRCLE','LINE','G','TEXT','TSPAN','RECT','POLYLINE','POLYGON'];
const all = [...scope.querySelectorAll('*')].filter(e=>!SKIP.includes(e.tagName.toUpperCase()) && !e.closest('svg') && !e.closest('.ua-box') && vis(e));
if(scope !== document.body) all.unshift(scope);
const leafText = e => { for(const n of e.childNodes) if(n.nodeType===3 && n.textContent.trim().length) return true; return false; };
const isChip = e => e.tagName==='BUTTON' || /(^|[\s_-])(chip|pill|badge|tag|btn|bd)([\s_-]|$)|chip|pill|badge/i.test(cls(e)) || e.getAttribute('role')==='tab';
const lineCount = e => { const tops=new Set(); for(const n of e.childNodes){ if(n.nodeType!==3||!n.textContent.trim()) continue; const r=document.createRange(); r.selectNodeContents(n); for(const q of r.getClientRects()){ if(q.width>1) tops.add(Math.round(q.top/3)); } } return tops.size; };
const inScrollX = e => { let n=e.parentElement; while(n && n!==document.body){ const ox=getComputedStyle(n).overflowX; if((ox==='auto'||ox==='scroll') && n.scrollWidth>n.clientWidth+1) return true; n=n.parentElement; } return false; };

const de = document.documentElement;
if(scope===document.body && de.scrollWidth > innerWidth+1) out.push({rule:3, sel:'html', text:'', note:'page scrollWidth '+de.scrollWidth+' > viewport '+innerWidth, rect:{x:0,y:0,w:innerWidth,h:60}});

for(const e of all){
  const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
  const own = leafText(e);
  if(own){
    for(const n of e.childNodes){ if(n.nodeType!==3) continue; const t=n.textContent; const re=/\S{3,}/g; let m, cnt=0, hit=false;
      while((m=re.exec(t)) && cnt<40){ cnt++;
        const w = m[0];
        const rg=document.createRange(); rg.setStart(n,m.index); rg.setEnd(n,m.index+w.length);
        const tops=new Set(); for(const q of rg.getClientRects()){ if(q.width>0.5) tops.add(Math.round(q.top/3)); }
        if(tops.size>1 && w.length<=24 && !/[-/–—]/.test(w) && !/[\u0E00-\u0E7F]/.test(w)){ add(1, e, 'word "'+w+'" breaks across lines'); hit=true; break; } }
      if(hit) break; }
  }
  if(own && isChip(e)){
    const tl = txt(e); const lh = parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.3;
    if(tl.length<=48 && r.height > lh*1.55 + parseFloat(cs.paddingTop)+parseFloat(cs.paddingBottom) && lineCount(e)>1) add(2, e, 'chip text wraps to '+lineCount(e)+' lines');
  }
  if(r.right > innerWidth+1 && cs.position!=='fixed' && !inScrollX(e) && r.width < innerWidth*2) add(3, e, 'extends past viewport by '+Math.round(r.right-innerWidth)+'px');
  else if((cs.overflowX==='hidden'||cs.overflowX==='clip') && e.scrollWidth > e.clientWidth+2 && own && cs.textOverflow!=='ellipsis' && e.children.length===0 && cs.whiteSpace!=='normal') add(3, e, 'text clipped (scrollWidth '+e.scrollWidth+' > '+e.clientWidth+', no ellipsis)');
  if(own){
    const fs = parseFloat(cs.fontSize); const t=txt(e);
    const caps = cs.textTransform==='uppercase' || (t.length>=2 && t===t.toUpperCase() && /[A-Z]{2}/.test(t) && t.length<24 && parseFloat(cs.letterSpacing)>0);
    let min, kind;
    if(!phone){ min=12.5; kind='Mac min'; }
    else if(caps){ min=11; kind='caps label'; }
    else if(isChip(e)){ min=13; kind='chip'; }
    else if(t.length>40 && !/(^|\s)(hint|mu|ui-hint)(\s|$)/.test(cls(e)) && !['LABEL','SMALL','SUMMARY'].includes(e.tagName)){ min=14; kind='body'; }
    else { min=13; kind='small'; }
    if(fs < min-0.01) add(6, e, kind+' font '+fs+'px < '+min, {sub:'font'});
  }
  if(phone && (e.tagName==='BUTTON'||e.tagName==='SELECT'||e.tagName==='SUMMARY'||(e.tagName==='INPUT'&&!['checkbox','radio','hidden','file'].includes(e.type))||e.getAttribute('role')==='tab')){
    if(r.height < 35.5 && !/^✓\s*all$/i.test(txt(e))) add(6, e, 'tap target height '+Math.round(r.height)+'px < 36', {sub:'tap'});
  }
}

const cardSel = '.card,.ui-card,.ln3-tdc,.ui-sheet,.core-sheet,.modal,[class*="card"],form,fieldset,.ui-pcell,.pbSh';
const cards = [...new Set([...scope.querySelectorAll(cardSel)].concat(scope.matches&&scope.matches(cardSel)?[scope]:[]))].filter(vis);

// 4 lone control row
for(const p of all){
  const kids=[...p.children].filter(vis); if(kids.length!==1) continue;
  const k=kids[0]; const pr=p.getBoundingClientRect(), kr=k.getBoundingClientRect();
  if(pr.width<220 || pr.height>70) continue;
  if(!(k.tagName==='BUTTON'||k.tagName==='SELECT'||k.tagName==='INPUT'||isChip(k)||/(^|\s)(sw|td3-sw)(\s|$)/.test(cls(k)))) continue;
  const cs=getComputedStyle(p); if(cs.display==='inline'||cs.display==='contents') continue;
  if([...p.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())) continue;
  if(kr.width <= pr.width*0.5 && !/flex-end|end|right/.test(cs.justifyContent) && cs.position!=='fixed' && cs.textAlign!=='center' && !(cs.display.includes('flex')&&/center|space-around/.test(cs.justifyContent))) add(4, k, 'only control in a row; row '+Math.round(pr.width)+'px wide, control '+Math.round(kr.width)+'px ('+Math.round(100-kr.width/pr.width*100)+'% empty)');
}

// 5 duplicate message inside one card
const seenDup = new Set();
for(const c of cards){
  const m = new Map();
  for(const e of c.querySelectorAll('*')){ if(!vis(e)||!leafText(e)||e.children.length>2) continue; const t=txt(e); if(t.length<7||/^[\d\s.,:%+\-–$฿/()]+$/.test(t)) continue; if(e.closest('select,option,textarea,input,svg')) continue;
    const key=t.toLowerCase(); if(!m.has(key)) m.set(key,[]); m.get(key).push(e); }
  for(const [k,v] of m){ if(v.length>1){
      let top=v.filter(a=>!v.some(b=>b!==a&&b.contains(a))); if(top.length<2) continue;
      // repeated list rows (same wrapper class under the common ancestor) are not "the same message twice"
      const lca=(x,y)=>{ let n=x; while(n&&!n.contains(y)) n=n.parentElement; return n; };
      const branch=(l,x)=>{ let n=x; while(n&&n.parentElement!==l) n=n.parentElement; return n; };
      top=top.filter((x,i)=>{ for(let j=0;j<top.length;j++){ if(j===i) continue; const l=lca(x,top[j]); const bx=branch(l,x), by=branch(l,top[j]); if(bx&&by&&bx!==by&&cls(bx)&&cls(bx)===cls(by)) return false; } return true; });
      if(top.length<2) continue;
      const id=k+'|'+top.map(x=>Math.round(x.getBoundingClientRect().top)).join(','); if(seenDup.has(id)) continue; seenDup.add(id);
      add(5, top[1], 'same text shown '+top.length+'× in one card: "'+k.slice(0,50)+'"'); } }
  const rr = [...c.querySelectorAll('*')].filter(e=>vis(e)&&leafText(e)&&/\bR:R\b/i.test(txt(e))&&txt(e).length<60&&e.children.length===0);
  const rid='rr'+path(c);
  if(rr.length>1 && !seenDup.has(rid) && c.querySelectorAll('.ui-pcell,.ui-plan').length<2){ seenDup.add(rid); add(5, rr[1], 'R:R shown '+rr.length+'× in one card: '+rr.map(x=>'"'+txt(x).slice(0,30)+'"').join(' / ')); }
}
for(const c of cards){
  const els=[...c.querySelectorAll('*')].filter(e=>vis(e)&&leafText(e)&&e.children.length===0&&txt(e).length<40);
  const mm=els.filter(e=>/\b(MMT|COMP)\b/.test(txt(e)));
  const rg=els.filter(e=>/\b(Risk[- ]?(on|off)|Bull|Bear|Neutral|Cautious|Defensive|Expansion|Contraction)\b/i.test(txt(e)) && !mm.includes(e));
  if(mm.length && rg.length && !seenDup.has('rg'+path(c))){
    const a=mm.map(x=>txt(x).toLowerCase()).join(' '); const hit=rg.find(x=>txt(x).toLowerCase().split(/[\s·|/]+/).some(w=>w.length>3&&a.includes(w)));
    if(hit){ seenDup.add('rg'+path(c)); add(5, hit, 'regime label "'+txt(hit).slice(0,30)+'" and MMT/COMP chip "'+txt(mm[0]).slice(0,30)+'" say the same thing'); } }
}

// 7 overlap
const inFixed = e => { for(let n=e;n&&n!==document.body;n=n.parentElement){ const p=getComputedStyle(n).position; if(p==='fixed'||p==='sticky') return true; } return false; };
const multiLine = e => getComputedStyle(e).display==='inline' && e.getClientRects().length>1;
const leaves = all.filter(e=>!inFixed(e) && (leafText(e)||['BUTTON','INPUT','SELECT'].includes(e.tagName)) && e.children.length<=3 && getComputedStyle(e).position!=='absolute');
const lr = leaves.map(e=>({e, r:e.getBoundingClientRect()}));
let ov=0;
for(let i=0;i<lr.length&&ov<12;i++){ for(let j=i+1;j<lr.length&&ov<12;j++){ const a=lr[i], b=lr[j]; if(a.e.contains(b.e)||b.e.contains(a.e)||multiLine(a.e)||multiLine(b.e)) continue;
    const ix=Math.min(a.r.right,b.r.right)-Math.max(a.r.left,b.r.left), iy=Math.min(a.r.bottom,b.r.bottom)-Math.max(a.r.top,b.r.top);
    if(ix>3&&iy>3&&ix>Math.min(a.r.width,b.r.width)*0.3){ const ar=Math.min(a.r.width*a.r.height,b.r.width*b.r.height); if(ix*iy>ar*0.3){ add(7, b.e, 'overlaps "'+txt(a.e).slice(0,30)+'" ('+Math.round(ix)+'×'+Math.round(iy)+'px)'); ov++; } } } }

// 8 empty gaps inside cards
for(const c of cards){
  const kids=[...c.children].filter(k=>vis(k)&&getComputedStyle(k).position!=='absolute'&&getComputedStyle(k).position!=='fixed'); if(kids.length<2) continue;
  const cs=getComputedStyle(c); if(cs.display.includes('flex')&&cs.flexDirection.startsWith('row')) continue; if(cs.display.includes('grid')) continue;
  if(c.closest('.overlay')) continue;   // scrolled modal: rects are not comparable
  kids.sort((a,b)=>a.getBoundingClientRect().top-b.getBoundingClientRect().top);
  for(let i=1;i<kids.length;i++){ const pb=kids[i-1].getBoundingClientRect(), nt=kids[i].getBoundingClientRect(); const gap=nt.top-pb.bottom;
    if(pb.left<nt.right&&nt.left<pb.right && gap>32.5){ add(8, kids[i], 'empty gap '+Math.round(gap)+'px above this element (card '+path(c).split(' > ').pop()+')'); break; } }
}
return out; }"""

BOTTOM_JS = r"""()=>{ const tb=document.querySelector('.tabs'); if(!tb) return null; const cs=getComputedStyle(tb); if(cs.position!=='fixed') return null;
  window.scrollTo(0, document.documentElement.scrollHeight); const top=tb.getBoundingClientRect().top;
  const els=[...document.querySelectorAll('body *')].filter(e=>!tb.contains(e)&&e!==tb&&e.getBoundingClientRect().height>0&&getComputedStyle(e).position!=='fixed'&&e.checkVisibility&&e.checkVisibility()&&(e.innerText||'').trim().length&&e.children.length===0);
  let last=null,lb=-1; for(const e of els){ const b=e.getBoundingClientRect().bottom; if(b>lb&&b<=innerHeight+2){ lb=b; last=e; } }
  window.scrollTo(0,0);
  return last && lb>top+1 ? {tabTop:top,lastBottom:lb,text:(last.innerText||'').trim().slice(0,40)} : null; }"""

LONG_SEC = "Semiconductors & Advanced Packaging Equipment Makers"
THAI = "ข้อสังเกตภาษาไทยยาวมากสำหรับทดสอบการตัดบรรทัดของข้อความในการ์ดและชิป"


def stress_cards():
    tick = ["SET:ADVANC", "SET:CPALL", "BERKSHIREB", "ABCDEFGHIJ", "AMD", "AVGO", "SET:PTTEP", "TSMC"]
    cards = {}
    for i, t in enumerate(tick):
        cid = "cc%02d" % i
        if i == 0:
            cards[cid] = P24.open_card(cid, "tS0", ticker=t, acct="main", qty=10, entry=171.4, sl=168, tier="A",
                                       lots=[{"n": 1, "date": "2026-09-10", "px": 171.4, "qty": 10, "f": 1, "stop": 168}])
        else:
            cards[cid] = P24.card(cid, "main", t, plan={"entry": 182.5 + i, "stop": 170}, px=170 + i, pxDate="2026-10-01", **({"track": "ladder"} if i % 2 else {}))
    return cards


def hot_sectors():
    nm = [LONG_SEC, "Power & Grid Infrastructure and Utilities Buildout", "Defense", "Cybersecurity", "Biotech", "Homebuilders & Building Products Wholesale"]
    et = ["XLK", "XLU", "XLI", "XLC", "XBI", "XHB"]
    return [{"etf": e, "name": n, "k": "lead" if i < 3 else "fresh"} for i, (e, n) in enumerate(zip(et, nm))]


def stress_inject(page):
    js(page, """([HOT, THAI])=>{ const n = Date.now();
      window.ln4HotSectors = ()=>HOT;
      const SEC = {'SET:ADVANC':'XLK','SET:CPALL':'XLU','BERKSHIREB':'XLI','ABCDEFGHIJ':'XLC','AMD':'XLK','AVGO':'XLK','SET:PTTEP':'XBI','TSMC':'XHB'};
      window.tv1EtfOf = (sym)=>SEC[sym] || 'XLE'; window.tv1HotOf = (e)=>['XLK','XLU','XLI','XLC','XBI','XHB'].includes(e); window.tv1SecName = (e)=>(HOT.find(x=>x.etf===e)||{name:'Energy'}).name;
      window.td3NewsModel = ()=>({hasDocs:true, now:n, list:[
        {id:'e1', ts:n-3600000, e:{title:'China Consumer Price Index year-over-year (Core excluding food)'}, assets:['XAUUSD']},
        {id:'e2', ts:n+(3*3600+12*60)*1000, e:{title:'US CPI'}, assets:['XAUUSD','BTCUSD']},
        {id:'e3', ts:n+9*3600000, e:{title:'ข้อมูลเศรษฐกิจสหรัฐ '+THAI}, assets:['XAUUSD']}]});
      window.pbLatestActive = ()=>({quarter:'2026Q4', savedAt:new Date(n-4*86400000).toISOString(), view:{headline:'Real Rates Are the Tax, Hormuz Is the Swing '+THAI}, assets:{XAUUSD:{stance:'up'}, BTC:{stance:'down_flat'}, BRENT:{stance:'up_flat'}, US:{stance:'up'}}});
      window.ftList = ()=>[{sym:'SET:ADVANC', over:2, left:0},{sym:'ABCDEFGHIJ', over:1, left:0}]; window.sk1Items = ()=>[]; }""",
       [hot_sectors(), THAI])
    for t in ("AMD", "AVGO", "SET:PTTEP"):
        js(page, "([t,th])=>{ const c = coreCardsList.find(x=>x.ticker===t); if(c) coreWrite(c.id, {plan:Object.assign({}, c.plan||{}, {starter:true, addon:{riskPct:0.3, frac:0.25, cond:'stop>=be'}}), note:th}); }", [t, THAI])
    settle(page, 400)


def app(pw, w, h):
    b, page, ce, pe = T.launch(pw, w, h, iso=T.NOW, picks=("XAUUSD", "BTCUSD", "USDJPY"), weekly=True)
    page.add_style_tag(content='*{animation:none!important;transition:none!important;caret-color:transparent!important}')
    js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }",
       [P13.T("tS0", "core", "open", sym="SET:ADVANC", entry=171.4, sl=168, qty=10, cur="USD", date="2026-09-10")])
    for cid, c in stress_cards().items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    P24.set_ff(page, P24.ff_json(True, True))
    js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 700)
    P120.ps_on(page)
    stress_inject(page)
    return b, page, ce, pe


def close_all(page):
    js(page, """()=>{ try{ coreSheetClose(); }catch(e){} try{ pbSheetClose(); }catch(e){} try{ closeSettings&&closeSettings(); }catch(e){}
      try{ const o=document.getElementById('ltOverlay'); if(o){ o.classList.remove('show'); o.style.display=''; } }catch(e){}
      document.querySelectorAll('.ui-sheet-backdrop,.pb-sheet').forEach(e=>e.remove()); document.querySelectorAll('.overlay.show').forEach(e=>e.classList.remove('show')); window.scrollTo(0,0); }""")
    settle(page, 150)


def screens():
    L = []
    def add(name, fn, scope=None, wait=600, post=None): L.append(dict(name=name, fn=fn, scope=scope, wait=wait, post=post))
    add("Today · Daily", "()=>{ switchTab('today'); td3SetMode('d'); todayRefresh(true); }")
    add("Today · Weekend", "()=>{ switchTab('today'); td3SetMode('w'); todayRefresh(true); }")
    add("Today · Daily (news row clicked)", "()=>{ switchTab('today'); td3SetMode('d'); todayRefresh(true); const r=document.querySelector('[data-td3-news] [onclick]'); if(r) r.click(); }")
    add("Flow", "()=>{ switchTab('flow'); }", wait=900)
    add("Watch · Ideas", "()=>{ switchTab('watch'); wlSetView('idea'); }")
    add("Watch · Candidates", """()=>{ switchTab('watch'); wlSetView('cand');
        const D = {'SET:ADVANC':[3,'Volume spike'], 'BERKSHIREB':[5,'Earnings spike'], 'ABCDEFGHIJ':[2,'Event: AI power'], DDOG:[1,'TradingView'], FTNT:[9,''], 'SET:PTTEP':[14,'Volume spike']};
        const now = new Date('2026-10-01T05:00:00Z').getTime();
        Object.keys(D).forEach(k=>td3MetaWrite(k, Object.assign({cand_at:new Date(now - D[k][0]*86400000).toISOString()}, D[k][1] ? {source:D[k][1]} : {})));
        window.wlRowsAll = ()=>({wl:[], cand:Object.keys(D).map(s=>({sym:s, port:'cand', market:s.startsWith('SET')?'TH':'US', item:null, w:null, d:null, cInfo:[]}))}); renderWatchlist(); }""")
    add("Watch · Watchlist", "()=>{ switchTab('watch'); wlSetView('wl'); renderWatchlist(); }")
    add("Plan · Core list", "()=>{ switchTab('plan'); setPlanScope('stock'); render(); }")
    add("Plan · Core new form", "()=>{ switchTab('plan'); setPlanScope('stock'); coreNewOpen('main',{ticker:'SET:ADVANC'}); }", scope=".core-sheet", wait=700, post="fill")
    add("Plan · Sat list", "()=>{ switchTab('plan'); setPlanScope('future'); render(); }")
    add("Journal", "()=>{ switchTab('journal'); }", wait=1500)
    add("Port", "()=>{ switchTab('mix'); }", wait=1500)
    add("Settings", "()=>{ openSettings(); }", wait=800)
    add("TradingView import sheet", "()=>{ switchTab('watch'); wlSetView('cand'); tv1ImportOpen(); }", scope="#ltModal")
    add("Idea import sheet", "()=>{ switchTab('watch'); wlSetView('idea'); ideaImportOpen(); }", scope="#ltModal")
    add("Idea new sheet", "()=>{ switchTab('watch'); wlSetView('idea'); ideaNewOpen(); }", scope="#ltModal")
    add("Playbook history", "()=>{ switchTab('flow'); pbOpenHistory(); }", scope=".pb-sheet .ui-sheet")
    add("Playbook paste", "()=>{ switchTab('flow'); pbOpenPaste(); }", scope=".pb-sheet .ui-sheet")
    add("Playbook asset sheet", "()=>{ switchTab('flow'); pbAssetSheet(pbList[0].id,'XAUUSD'); }", scope=".pb-sheet .ui-sheet")
    return L


def sat_states(page):
    js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); settle(page, 500)
    page.add_style_tag(content='.ui-plan-cta.ui-sticky{position:static!important;margin-top:10px}')
    states = [("valid long", "Long", 2000, 1990, 2020), ("SL wrong side", "Long", 2000, 2010, 2020),
              ("TP wrong side", "Long", 2000, 1990, 1980), ("short valid", "Short", 2000, 2010, 1980),
              ("empty fields", "Long", "", "", ""), ("big numbers 12,345.67", "Long", 12345.67, 12300.5, 12400.99)]
    for asset in ("XAUUSD", "USDJPY"):
        for nm, d, e, s, t in states:
            iid = js(page, "([a])=>satV2NewPlan(a,'main')", [asset]); settle(page, 400)
            js(page, "([i,d])=>satV2SetDir(i,d)", [iid, d])
            for f_, v in (("entry", e), ("sl", s), ("tp", t)):
                if v != "": js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, f_, str(v)])
            js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); settle(page, 500)
            yield "Plan · Sat form · %s (%s)" % (nm, asset)


def run_checks(page, w, scope):
    sc = None
    if scope:
        if not (page.locator(scope).count() and page.locator(scope).first.is_visible()):
            return None, []
        sc = scope
    f = page.evaluate(CHECK_JS, {"vw": w, "scopeSel": sc})
    if not sc and not page.evaluate("()=>!!document.querySelector('.overlay.show,.ui-sheet-backdrop')"):
        bb = page.evaluate(BOTTOM_JS)
        if bb:
            f.append({"rule": 7, "sel": ".tabs", "text": bb["text"], "note": "last content '%s' under the fixed tab bar at scroll bottom (%.0f > %.0f)" % (bb["text"], bb["lastBottom"], bb["tabTop"]), "rect": {"x": 0, "y": 0, "w": 0, "h": 0}})
    return sc or "body", f


def crop(page, f, path_png):
    r = f["rect"]
    try:
        page.evaluate("""([r])=>{ document.querySelectorAll('.ua-box').forEach(e=>e.remove()); if(!r.w) return; const d=document.createElement('div'); d.className='ua-box';
          d.style.cssText=`position:absolute;left:${r.x-2}px;top:${r.y-2}px;width:${r.w+4}px;height:${r.h+4}px;outline:2px solid #ff0000;pointer-events:none;z-index:2147483647`; document.body.appendChild(d); }""", [r])
        H = page.evaluate("()=>document.documentElement.scrollHeight"); W = page.viewport_size["width"]
        x0 = max(0, r["x"] - 120); y0 = max(0, r["y"] - 60)
        ww = min(W - x0, max(r["w"] + 240, 360)); hh = min(H - y0, r["h"] + 120)
        if ww < 10 or hh < 10: return False
        page.screenshot(path=path_png, full_page=True, clip={"x": x0, "y": y0, "width": ww, "height": hh})
        return True
    except Exception:
        return False
    finally:
        try: page.evaluate("()=>document.querySelectorAll('.ua-box').forEach(e=>e.remove())")
        except Exception: pass


def audit(vps, tag, shots=True, limit_crops=500):
    outdir = os.path.join(SHOTS, tag); os.makedirs(outdir, exist_ok=True)
    findings = []; visited = collections.OrderedDict(); ncrop = [0]
    with sync_playwright() as pw:
        for w in vps:
            h = VPS[w]
            b, page, ce, pe = app(pw, w, h)
            seen = {}; n6 = [0]
            def visit(name, scope):
                sc, fl = run_checks(page, w, scope)
                if sc is None:
                    visited.setdefault(name, {})[w] = "NOT OPENED"; return
                visited.setdefault(name, {})[w] = "ok"
                for f in fl:
                    key = (w, f["rule"], f["sel"], f["text"], f["note"][:60])
                    if key in seen:
                        seen[key]["also"] = seen[key].get("also", 0) + 1; continue
                    seen[key] = f; f.update(screen=name, vp=w, shot="")
                    r6 = f["rule"] == 6
                    if r6: n6[0] += 1
                    if shots and ncrop[0] < limit_crops and (not r6 or n6[0] <= 25):
                        fn = "%s-%d-r%d-%03d.png" % (re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"), w, f["rule"], len(findings))
                        if crop(page, f, os.path.join(outdir, fn)):
                            f["shot"] = "tests/screenshots/ua1/%s/%s" % (tag, fn); ncrop[0] += 1
                    findings.append(f)
            try:
                for s in screens():
                    close_all(page)
                    try:
                        js(page, s["fn"]); settle(page, s["wait"])
                        if s.get("post") == "fill":
                            P120.fill(page, 182.5, 170); settle(page, 300)
                        visit(s["name"], s["scope"])
                    except Exception as ex:
                        visited.setdefault(s["name"], {})[w] = "ERROR " + str(ex)[:80]
                    close_all(page)
                try:
                    js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); coreNewOpen('main',{ticker:'ABCDEFGHIJ'}); }"); settle(page, 700)
                    P120.fill(page, 182.5, 182.5); settle(page, 300)
                    visit("Plan · Core new form (error: stop = entry)", ".core-sheet")
                except Exception as ex:
                    visited.setdefault("Plan · Core new form (error)", {})[w] = "ERROR " + str(ex)[:80]
                close_all(page)
                try:
                    for nm in sat_states(page):
                        visit(nm, None)
                except Exception as ex:
                    visited.setdefault("Plan · Sat forms", {})[w] = "ERROR " + str(ex)[:80]
                try:
                    js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); const c=coreCardsList.find(x=>x.ticker==='SET:ADVANC'); if(c&&window.coreOpenCard) coreOpenCard(c.id); }"); settle(page, 700)
                    visit("Plan · Core open card", None)
                except Exception:
                    pass
                for m in pe:
                    findings.append({"rule": 0, "screen": "console", "vp": w, "sel": "", "text": m[:80], "note": "uncaught exception", "rect": {"x": 0, "y": 0, "w": 0, "h": 0}, "shot": ""})
            finally:
                b.close()
    return findings, visited


def counts(findings):
    c = collections.Counter()
    for f in findings: c[(f["rule"], f["vp"])] += 1
    return c


def write_report(findings, visited, tag, out):
    vps = sorted({f["vp"] for f in findings} | {w for v in visited.values() for w in v})
    L = ["# UA1 audit (%s)" % tag, "", "Generated by `python3 tests/ui_audit.py`. Viewports 390×844 · 1280×800 · 1440×900; fixtures + stress data.", "",
         "## Screens visited", "", "| screen | " + " | ".join(map(str, vps)) + " |", "|---|" + "---|" * len(vps)]
    for n, d in visited.items(): L.append("| %s | %s |" % (n, " | ".join(d.get(v, "–") for v in vps)))
    c = counts(findings)
    L += ["", "## Counts per rule", "", "| rule | " + " | ".join(map(str, vps)) + " | total |", "|---|" + "---|" * (len(vps) + 1)]
    for r, nm in RULES.items():
        row = [c.get((r, v), 0) for v in vps]; L.append("| %d %s | %s | %d |" % (r, nm, " | ".join(map(str, row)), sum(row)))
    L += ["", "## Findings", "", "| # | screen | vp | rule | element | text | note | crop |", "|---|---|---|---|---|---|---|---|"]
    for i, f in enumerate(sorted(findings, key=lambda f: (f["rule"], f["screen"], f["vp"])), 1):
        L.append("| %d | %s | %d | %d | `%s` | %s | %s | %s |" % (i, f["screen"], f["vp"], f["rule"], f["sel"].replace("|", "/")[-70:], f["text"].replace("|", "/")[:40], (f["note"].replace("|", "/")[:130] + (" (+%d more screens)" % f["also"] if f.get("also") else "")), ("![](../../%s)" % f["shot"]) if f["shot"] else ""))
    open(out, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "reports", "UA1-audit.md"))
    ap.add_argument("--tag", default="before")
    ap.add_argument("--vp", default="390,1280,1440")
    ap.add_argument("--json", default="")
    ap.add_argument("--noshots", action="store_true")
    a = ap.parse_args(_ARGV)
    vps = [int(x) for x in a.vp.split(",")]
    fl, vis = audit(vps, a.tag, shots=not a.noshots)
    if a.json: json.dump({"findings": fl, "visited": vis}, open(a.json, "w"), ensure_ascii=False)
    write_report(fl, vis, a.tag, a.out)
    c = counts(fl)
    print("UA1 audit", a.tag, "findings:", len(fl))
    for r, nm in RULES.items(): print("  rule %d %-32s %s  total %d" % (r, nm, {v: c.get((r, v), 0) for v in vps}, sum(c.get((r, v), 0) for v in vps)))
    print("screens not ok:", [(n, d) for n, d in vis.items() if any(x != "ok" for x in d.values())])
