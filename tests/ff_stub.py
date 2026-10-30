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
SET1_DEV_FLAGS = "try{ localStorage.setItem('dash.set1Open','1'); localStorage.setItem('dash.ln1Legacy','1'); }catch(e){}\n"
FF_STUB_BASE = SET1_DEV_FLAGS + FF_STUB
LN1_LEGACY_SEED = "try{ localStorage.setItem('ln1_plan_view','legacy'); }catch(e){}\n"
FF_STUB = LN1_LEGACY_SEED + FF_STUB_BASE

