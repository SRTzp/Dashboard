"""ตัวช่วยกลางของชุดทดสอบ — จำลอง fetch('fundflow.json') ที่เปิดหน้าแบบ file:// (Chrome บล็อก fetch ไปที่ file://)
  window.__FF_JSON = null    → ตอบ HTTP 404 จำลอง (แอปเข้าโหมด "ข้อมูลตัวอย่าง" เหมือนยังไม่มีไฟล์) · ไม่มี console error
  window.__FF_JSON = {...}   → ตอบไฟล์นั้นเป็น fundflow.json (ตั้งก่อนเรียก ffLoadJson(true))
ทุก launcher เรียก context.add_init_script(FF_STUB) หลัง new_context"""
FF_STUB = r"""
(() => {
  const realFetch = window.fetch.bind(window);
  window.__FF_JSON = null;
  window.fetch = function(u, o){
    const url = String((u && u.url) || u);
    if(/(^|\/)fundflow\.json(\?|$)/.test(url)){
      if(window.__FF_JSON) return Promise.resolve(new Response(JSON.stringify(window.__FF_JSON), {status:200, headers:{'content-type':'application/json'}}));
      return Promise.resolve(new Response('', {status:404}));
    }
    return realFetch(u, o);
  };
})();
"""

# LN1 — หน้าแผน Sat มีสวิตช์ Lean/แบบเดิม (ค่าเริ่ม Lean) · เทสเก่าทั้งหมดเขียนไว้กับหน้าแบบเดิม (PV2c) → seed โหมด "แบบเดิม" ที่นี่ที่เดียว
# phase80 (เทส LN1) ใช้ FF_STUB_BASE เมื่อต้องการค่าเริ่ม Lean จริง: ff_stub.FF_STUB = ff_stub.FF_STUB_BASE ก่อน launch
# SET1 — แฟลกนักพัฒนา (ผู้ใช้จริงไม่มี): dash.set1Open=1 กางการ์ด Settings ทั้งหมด · dash.ln1Legacy=1 ให้ตรวจโหมดเดิมของหน้าแผน Sat ได้ (ปกติบังคับ Lean) · phase110 ล้างทั้งสองตัว
SET1_DEV_FLAGS = "try{ if(window.top!==window) throw 0; localStorage.setItem('dash.set1Open','1'); localStorage.setItem('dash.ps1Off','1'); }catch(e){}\n"   # PS1 - older suites run the pre-PS1 paths; PS1 suites call localStorage.removeItem('dash.ps1Off')
FF_STUB_BASE = SET1_DEV_FLAGS + FF_STUB
FF_STUB = FF_STUB_BASE   # AU3: the app is always Lean; the legacy-mode seed is gone


# PL1·A5 — กฎ Ready (Watchlist + ① Why buy + ④ Wrong if) บล็อกการเปิดแผนใหม่ · suite เก่าที่ไม่ได้ทดสอบกฎนี้เปิดแผนจาก ticker อะไรก็ได้
# → ผ่าน init script นี้ stub wlReady()/wlReadyMsg() หลังโหลดหน้า · suite ที่ทดสอบกฎจริง (phase116) ตั้ง window.__READY_REAL = true ตอนรัน
READY_STUB = "window.addEventListener('load', function(){ var o = window.wlReady; if(typeof o === 'function'){ window.wlReady = function(s){ return window.__READY_REAL ? o(s) : true; }; } });\n"
FF_STUB = FF_STUB + READY_STUB
FF_STUB_BASE = FF_STUB_BASE + READY_STUB

# AU1 — test-only setters. The old Sat form handlers that wrote single fields (satV2SetDir / satV3PlanEdit / satV2Edit / satV2SetSleeve) were deleted with the hidden Sat strategy panel;
# several legacy suites still use them to seed plans, so they live here (the app no longer has them).
AU1_SHIM = r"""(function(){
  window.satV2SetDir = function(id, dir){ var i = sat7dIdea(id); if(!i || !i.v2 || (dir!=='Long' && dir!=='Short' && dir!=='') || (i.bias||'')===dir) return; satV3IdeaWrite(id, {bias: dir}); };
  window.satV3PlanEdit = function(id, f, v){ if(['entry','sl','tp','cancel_level'].indexOf(f) >= 0){ var n = parseFloat(v); v = isFinite(n) ? n : null; } else v = String(v==null ? '' : v); var p = {}; p[f] = v; sat7dWrite('satIdeas', id, p); };
  window.satV2Edit = function(id, f, v){ var i = sat7dIdea(id); if(!i || !i.v2) return; if(f==='tf'){ var t = String(v==null ? '' : v).trim().slice(0, 8); if(t) sat7dWrite('satIdeas', id, {tf: t}); else satV3Render({force:true}); return; } if(f==='setup_note'){ sat7dWrite('satIdeas', id, {setup_note: String(v==null ? '' : v).trim().slice(0, SAT_V2_NOTE_MAX)}); } };
  window.satV2SetSleeve = function(id, sv){ var i = sat7dIdea(id); if(!i || !i.v2 || (sv!=='main' && sv!=='tactical') || satV2Sleeve(i)===sv) return; if(sv==='tactical' && !satIsPicked(i.asset)) return; var a0 = (sat7dAccts()[0] || {}).id, cfg = satV2Cfg(a0), old = satV2Sleeve(i), oldTf = old==='tactical' ? cfg.tfTac : cfg.tfMain, tf = String(i.tf || '').trim(); sat7dWrite('satIdeas', id, {sleeve: sv, tf: (!tf || tf===oldTf) ? (sv==='tactical' ? cfg.tfTac : cfg.tfMain) : tf}); };
})();
"""
FF_STUB = FF_STUB + AU1_SHIM
FF_STUB_BASE = FF_STUB_BASE + AU1_SHIM

# AU1 — satV3SaveReadyAccounts (old "save every Ready account" helper, no UI caller) lives here for the news-window suite (phase51)
AU1_SHIM2 = r"""window.satV3IdeaDelete = function(ideaId){ var c = sat7dCol('satIdeas'); if(!c) return; return c.doc(ideaId).delete().catch(function(e){ console.warn('satV3IdeaDelete', e); }); };
window.satV3SaveReadyAccounts = function(ideaId){ var idea = sat7dIdea(ideaId); if(!idea) return; if(idea.v2) satV3IdeaWrite(ideaId, {counter_trend: ln4VerifyOf(idea).counter === true}); sat7dAccts().forEach(function(a){ var s = (idea.accts||{})[a.id] || {}; if(s.trade_id || s.skip) return; if(satV3PlanAcctCalc(idea, a.id).ready) satV3SaveSlot(idea.id, a.id); }); };
"""
FF_STUB = FF_STUB + AU1_SHIM2
FF_STUB_BASE = FF_STUB_BASE + AU1_SHIM2
