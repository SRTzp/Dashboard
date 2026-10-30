/* ============================================================
   mock-firebase.js — in-memory Firestore + Auth compat shim
   Good enough to load the real index.html's inline scripts and drive them
   headlessly, without any real network / Firebase project.
   Served in place of the 3 real firebasejs CDN <script src> tags via
   Playwright route interception (see run_tests.py). Idempotent: safe to
   execute 3x in a row (guarded by window.__mockFirebaseInstalled).
   ============================================================ */
(function(){
  if (window.__mockFirebaseInstalled) return;
  window.__mockFirebaseInstalled = true;

  const DELETE_SENTINEL = {__isDeleteSentinel: true};

  // path (array of strings) -> plain JS object (doc data), only for docs that exist
  const store = new Map();
  function pathKey(path){ return path.join('/'); }
  function isDocPath(path){ return path.length % 2 === 0; }

  function deepClone(v){
    if (v === DELETE_SENTINEL) return v;
    if (Array.isArray(v)) return v.map(deepClone);
    if (v && typeof v === 'object') {
      const o = {};
      Object.keys(v).forEach(k => { o[k] = deepClone(v[k]); });
      return o;
    }
    return v;
  }

  function deepMerge(target, patch){
    Object.keys(patch).forEach(k=>{
      const v = patch[k];
      if (v === DELETE_SENTINEL) { delete target[k]; return; }
      if (v && typeof v === 'object' && !Array.isArray(v) && target[k] && typeof target[k]==='object' && !Array.isArray(target[k])) {
        deepMerge(target[k], v);
      } else {
        target[k] = deepClone(v);
      }
    });
    return target;
  }

  // apply {mergeFields:[dot.path,...]} semantics: each field path is replaced WHOLESALE
  // at that exact nested location (no recursive merge below that point) — matches the
  // app's own doPersistImpl() comments about why it uses mergeFields over merge:true.
  function applyMergeFields(target, patchData, fields){
    fields.forEach(fp=>{
      const parts = fp.split('.');
      const val = parts.reduce((o,k)=> (o==null?undefined:o[k]), patchData);
      let node = target;
      for (let i=0;i<parts.length-1;i++){
        const k = parts[i];
        if (!node[k] || typeof node[k] !== 'object') node[k] = {};
        node = node[k];
      }
      const lastKey = parts[parts.length-1];
      if (val === DELETE_SENTINEL) delete node[lastKey];
      else node[lastKey] = deepClone(val);
    });
    return target;
  }

  // listeners: {kind:'doc'|'col', path:[...], cb, err}
  const listeners = [];
  function notify(){
    // fire on a new macrotask (not a same-tick microtask) — real Firestore listener callbacks
    // never fire before the page's own <script> tags have all finished executing/parsing.
    setTimeout(()=>{
      listeners.slice().forEach(L=>{
        try{
          if (L.kind==='doc') L.cb(makeDocSnap(L.path));
          else L.cb(makeColSnap(L.path));
        }catch(e){ console.error('[mock-firebase] listener callback threw:', e); }
      });
    }, 0);
  }

  function makeDocSnap(path){
    const data = store.get(pathKey(path));
    return {
      exists: data !== undefined,
      id: path[path.length-1],
      ref: makeDocRef(path),
      data: ()=> data === undefined ? undefined : deepClone(data),
      metadata: {fromCache:false, hasPendingWrites:false}
    };
  }
  function makeColSnap(path){
    const docs = [];
    store.forEach((data, key)=>{
      const p = key.split('/');
      if (p.length === path.length+1 && path.every((seg,i)=>p[i]===seg)) {
        docs.push(makeDocSnap(p));
      }
    });
    return {docs, size: docs.length, empty: docs.length===0, metadata:{fromCache:false, hasPendingWrites:false}};
  }

  let autoId = 1;

  /* ══════════════════════════════════════════════════════════════════════════
     ★ 7D.3 Phase 3 — test-only helper: simulate a Firestore security-rules denial
     (e.g. satConfig rules not deployed yet) on an exact doc or collection path.
     __denyPath(['users','testuid','satConfig','setups']) makes every get()/onSnapshot()/
     set()/update() against that path (and anything nested under it) reject with a
     permission-denied error, same shape as the real SDK (err.code==='permission-denied').
     ══════════════════════════════════════════════════════════════════════════ */
  const deniedPaths = new Set();
  function isDenied(path){
    const key = pathKey(path);
    for (const d of deniedPaths) { if (key === d || key.startsWith(d + '/')) return true; }
    return false;
  }
  function denyErr(){ const e = new Error('Missing or insufficient permissions.'); e.code = 'permission-denied'; return e; }

  /* บันทึกทุก path ที่แอปแตะ (collection/doc) ไว้ที่ window.__fsAccess — เทสใช้ยืนยันว่าไม่มี request ไป news/macro */
  function logAccess(path){ try{ (window.__fsAccess = window.__fsAccess || []).push(pathKey(path)); }catch(e){} }
  function makeDocRef(path){
    logAccess(path);
    return {
      id: path[path.length-1],
      path: pathKey(path),
      collection(name){ return makeColRef([...path, name]); },
      get(opts){ return isDenied(path) ? Promise.reject(denyErr()) : Promise.resolve(makeDocSnap(path)); },
      set(data, opts){
        if (isDenied(path)) return Promise.reject(denyErr());
        const key = pathKey(path);
        let cur = store.get(key);
        if (opts && opts.mergeFields) {
          if (!cur) { cur = {}; store.set(key, cur); }
          applyMergeFields(cur, data, opts.mergeFields);
        } else if (opts && opts.merge) {
          if (!cur) { cur = {}; store.set(key, cur); }
          deepMerge(cur, data);
        } else {
          store.set(key, deepClone(data));
        }
        notify();
        return Promise.resolve();
      },
      update(data){
        if (isDenied(path)) return Promise.reject(denyErr());
        const key = pathKey(path);
        let cur = store.get(key);
        if (!cur) return Promise.reject(new Error('mock: update() on missing doc ' + key));
        /* WL2 — ตรงกับ Firestore จริง: update({field: {…}}) = แทนที่ค่าของ field ทั้งก้อน (ไม่ merge ลงใน map เดิม) · key ที่มีจุด 'a.b' = แก้ที่ path นั้น
           (เดิม deepMerge ทำให้ map ที่ถูกแทนที่ยังเหลือ key เก่า — เช่น thesis_hits ที่ล้างด้วย {} ไม่หาย) */
        Object.keys(data).forEach(k=>{
          const v = data[k], parts = k.split('.');
          let node = cur;
          for (let i=0;i<parts.length-1;i++){ if (!node[parts[i]] || typeof node[parts[i]] !== 'object') node[parts[i]] = {}; node = node[parts[i]]; }
          const last = parts[parts.length-1];
          if (v === DELETE_SENTINEL) delete node[last]; else node[last] = deepClone(v);
        });
        notify();
        return Promise.resolve();
      },
      delete(){
        if (isDenied(path)) return Promise.reject(denyErr());
        store.delete(pathKey(path));
        notify();
        return Promise.resolve();
      },
      onSnapshot(a, b, c){
        let cb, err;
        if (typeof a === 'function') { cb = a; err = b; }
        else { cb = b; err = c; }
        if (isDenied(path)) {
          setTimeout(()=>{ try{ if (err) err(denyErr()); }catch(e){ console.error(e); } }, 0);
          return ()=>{};
        }
        const L = {kind:'doc', path, cb, err};
        listeners.push(L);
        setTimeout(()=>{ try{ cb(makeDocSnap(path)); }catch(e){ console.error(e); } }, 0);
        return ()=>{ const i = listeners.indexOf(L); if (i>=0) listeners.splice(i,1); };
      }
    };
  }

  function makeColRef(path){
    logAccess(path);
    const ref = {
      path: pathKey(path),
      doc(id){ return makeDocRef([...path, id!=null ? String(id) : ('auto'+(autoId++))]); },
      add(data){ const d = makeDocRef([...path, 'auto'+(autoId++)]); return d.set(data).then(()=>d); },
      get(){ return isDenied(path) ? Promise.reject(denyErr()) : Promise.resolve(makeColSnap(path)); },
      orderBy(){ return ref; },   // no-op chain — order not needed for these tests
      limit(){ return ref; },
      where(){ return ref; },
      onSnapshot(cb, err){
        if (isDenied(path)) {
          setTimeout(()=>{ try{ if (err) err(denyErr()); }catch(e){ console.error(e); } }, 0);
          return ()=>{};
        }
        const L = {kind:'col', path, cb, err};
        listeners.push(L);
        setTimeout(()=>{ try{ cb(makeColSnap(path)); }catch(e){ console.error(e); } }, 0);
        return ()=>{ const i = listeners.indexOf(L); if (i>=0) listeners.splice(i,1); };
      }
    };
    return ref;
  }

  const db = {
    collection(name){ return makeColRef([name]); },
    settings(){ /* no-op — real SDK config knobs (long polling etc), irrelevant to the mock */ },
    enablePersistence(){ return Promise.resolve(); },
    // test-only helpers, not part of the real SDK
    __seedDoc(path, data){ store.set(pathKey(path), deepClone(data)); },
    __getDoc(path){ const d = store.get(pathKey(path)); return d===undefined?undefined:deepClone(d); },
    __dump(){ const o={}; store.forEach((v,k)=>{ o[k]=deepClone(v); }); return o; },
    __denyPath(path){ deniedPaths.add(pathKey(path)); },
    __allowPath(path){ deniedPaths.delete(pathKey(path)); },
    /* RR1 — ยิง snapshot ซ้ำให้ทุก listener โดยข้อมูลไม่เปลี่ยน (เหมือนเสียงสะท้อน/metadata-only ของจริง) · meta = {fromCache, hasPendingWrites} */
    __ping(meta){
      listeners.slice().forEach(L=>{
        try{
          const sn = L.kind==='doc' ? makeDocSnap(L.path) : makeColSnap(L.path);
          sn.metadata = Object.assign({fromCache:false, hasPendingWrites:false}, meta||{});
          L.cb(sn);
        }catch(e){ console.error('[mock-firebase] ping threw:', e); }
      });
    }
  };

  // ---- Auth ----
  const authCbs = [];
  const authInstance = {
    currentUser: null,
    setPersistence(){ return Promise.resolve(); },
    onAuthStateChanged(cb){
      authCbs.push(cb);
      // Real Firebase never fires the first callback before the page's own <script> tags have
      // finished executing. setTimeout(0) alone isn't a strong enough guarantee for a chain of
      // several inline <script> blocks parsed back-to-back, so wait for full document readiness too.
      const fire = ()=>setTimeout(()=>cb(authInstance.currentUser), 0);
      if (document.readyState === 'complete') fire();
      else window.addEventListener('load', fire, {once:true});
      return ()=>{ const i = authCbs.indexOf(cb); if(i>=0) authCbs.splice(i,1); };
    },
    signInWithEmailAndPassword(email, pass){
      authInstance.currentUser = {uid: window.__MOCK_UID || 'testuid', email};
      authCbs.forEach(cb=>cb(authInstance.currentUser));
      return Promise.resolve({user: authInstance.currentUser});
    },
    createUserWithEmailAndPassword(email, pass){
      return authInstance.signInWithEmailAndPassword(email, pass);
    },
    signOut(){
      authInstance.currentUser = null;
      authCbs.forEach(cb=>cb(null));
      return Promise.resolve();
    }
  };

  function auth(){ return authInstance; }
  auth.Auth = {Persistence: {LOCAL:'local', SESSION:'session', NONE:'none'}};

  function firestore(){ return db; }
  firestore.FieldValue = {
    delete(){ return DELETE_SENTINEL; },
    serverTimestamp(){ return new Date().toISOString(); }
  };

  window.firebase = {
    initializeApp(){ return {}; },
    auth,
    firestore,
    __mockDb: db,
    __mockAuth: authInstance
  };
})();

/* ── PF1 — ตัวช่วยเทสเท่านั้น (แอปถอดฟังก์ชันเหล่านี้แล้ว): seed Bias เก่าของ Strategy · สร้างไอเดีย v1 (การ์ด 2 ขั้น) ── */
(function(){
  window.satwSetBias = function(asset, b, extra){ return window.satwWrite(asset, Object.assign({bias: b, updated_at: new Date().toISOString()}, extra || {})); };
  /* PF1 — ตัวช่วยเทสเท่านั้น: เขียน Bias เก่าของ Strategy (ปุ่ม Bias ถอดแล้ว) แล้ววาดใหม่ · สร้างไอเดีย v1 (การ์ด 2 ขั้น) แบบ satV3NewPlan เดิมที่ถอดจากแอป */
  window.satwSetInvalidation = function(asset, val){ const n = parseFloat(val); return window.satwWrite(asset, {invalidation: isFinite(n) ? n : null, updated_at: new Date().toISOString()}); };
  window.satV3SetBias = function(asset, b){ window.satwWrite(asset, {bias: b, updated_at: new Date().toISOString()}); try{ satV3Render(); }catch(e){} };
  window.satV3NewPlan = function(asset){
    const wk = satwWeek(wpWeekKey(), asset), bias = wk && wk.bias;
    if(bias!=='Long' && bias!=='Short') return;
    const existing = satV3PlanDraftFor(asset);
    if(existing){ satV3PlanHighlight = existing.id; if(satV3IsCondIdea(existing) && existing.planned===true && !satV3Open.has(existing.id)){ satV3Open.add(existing.id); satV3Render(); } return; }
    const id = 'i' + Date.now();
    sat7dWrite('satIdeas', id, {v3: true, asset, bias, week: wpWeekKey(), created_at: new Date().toISOString(), entry: null, sl: null, tp: null, cancel_level: null,
      conditions: [satAcNewCond('c' + Date.now() + Math.floor(Math.random()*1000), '')], planned: false, setups: [], status: 'active', accts: {}});
    satV3PlanHighlight = id;
  };
})();
