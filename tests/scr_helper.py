"""PL1 Step 4 — helper ให้ suite เก่าย้าย Candidate → Watchlist ผ่าน screening modal (scrOpen/scrSave) แทนฟอร์มเดิม (td4ProSave)
promote_js: JS ที่เติม Track (ถ้า candMeta ยังไม่มี) + Proven Pass + Trend Pass + Why แล้วบันทึก"""
PROMOTE_JS = """(a)=>{ const sym = a[0], track = a[1] || 'winner', why = a[2] || 'screened', save = a[3] !== false;
  try{ ltSheetClose(); }catch(e){}
  const m = td3MetaOf(sym);
  if(!(m.track==='winner' || m.track==='ladder')){ glWrite(S=>{ const cm = Object.assign({}, S.candMeta || {}), k = wlSymKey(sym); cm[k] = Object.assign({sym:sym, market:coreMarketOf(sym), manual:true, cand_at:new Date().toISOString()}, cm[k] || {}, {track:track}); S.candMeta = cm; }); }
  scrOpen(sym); scr.proven = 'passed'; scr.trend = 'passed'; scr.why = why; if(!scr.track) scr.track = track; if(save) scrSave(); }"""


def promote(page, sym, track="winner", why="screened", save=True, wait=700):
    page.evaluate(PROMOTE_JS, [sym, track, why, save])
    page.wait_for_timeout(wait)
