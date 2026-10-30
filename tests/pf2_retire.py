"""PF2 — ตัวช่วยเคสที่ถูกเปลี่ยน/ถอด (ดู PF2_retired.md)"""
def retired(name, reason="changed by PF2"):
    print("RETIRED(PF2) - " + name[:140])


def seed_plans(page, keys):
    """PF2 — Today การ์ด Sat: Asset ที่เลือกต้องมีแผนใช้งาน ถึงจะเป็น state C (กติกา TD2 เดิม: ปกติ = เงียบ) · เทสเก่าที่ตั้ง pick แต่ไม่มีแผน เรียกตัวนี้หลัง launch"""
    page.evaluate("""(ks)=>{ ks.forEach(k=>{ sat7dWrite('satIdeas', 'pf2'+k, {v3:true, v2:true, sleeve:'main', asset:k, bias:'', week: wpWeekKey(), status:'active', accts:{}, setups:[], created_at:new Date().toISOString()}); }); }""", list(keys))
    page.wait_for_timeout(700)


def retired_wm1(name, reason="changed by WM1 §7"):
    print("RETIRED(WM1) - " + name[:140])


def retired_sn1(name, reason="changed by SN1 Today order"):
    print("RETIRED(SN1) - " + name[:140])


def retired_td3a(name, reason="changed by TD3a Today layout"):
    print("RETIRED(TD3a) - " + name[:140])


# TD3a — Today ไม่มี 2 คอลัมน์/tdBalance แล้ว: เคสแทน = 3 panels (Overview · Core Port · Satellite) ชิดบนเท่ากัน ไม่ล้นจอ
PANELS_JS = """()=>{ const p = document.querySelector('.td3-pn'); if(!p) return null; const k = [...p.children].map(e=>Math.round(e.getBoundingClientRect().top));
  return {n: k.length, tops: k, ow: document.documentElement.scrollWidth - innerWidth, wide: innerWidth >= 1000}; }"""


def panels_ok(o):
    return bool(o) and o["n"] == 3 and (not o["wide"] or max(o["tops"]) - min(o["tops"]) <= 1) and o["ow"] <= 0


def retired_td4a(name, reason="changed by TD4a Core panel spec"):
    print("RETIRED(TD4a) - " + name[:140])
