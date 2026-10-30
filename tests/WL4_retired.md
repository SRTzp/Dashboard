# WL4 — เทสเก่าที่แก้ความคาดหวัง (ไม่ลบเคส · ไม่ทำให้อ่อนลง)

| ชุด | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| phase8 | "RS_DEMO ไม่มี macro/news · meta.counts ไม่นับ news/macro" | `RS_DEMO.macro/news` undefined และ counts ไม่มี news/macro | `typeof RS_DEMO === 'undefined'` (ข้อมูลตัวอย่างถูกลบทั้งก้อน → ไม่มี macro/news ในนั้นแน่นอน) | WL4 ข้อ 2: เอา RS_DEMO / RS_DEMO_ON ออก (ไม่มีใครใช้แล้ว) |
| phase8 | "ไม่มีปุ่มกระดิ่ง / จุดแดง / newsDrawer / #ffMacro (…)" | `#pushBadge` ต้องมี | `#pushBadge` ต้อง **ไม่มี** (ส่วนอื่นของเคสเหมือนเดิม) | WL4: ป้าย push ล่าสุดออก |
| phase35 | "9 CAND1 (candidate): ไม่มีปุ่ม ＋ โน้ต · ชิป Screen เดิมยังอยู่ · ไม่มีส่วนโน้ต" (1440 + 430) | ชิปมี `Screen 9/15` | ชิปต้องไม่มีคำว่า `Screen` (ส่วน ไม่มีปุ่ม ＋ โน้ต / ไม่มีส่วนโน้ต เหมือนเดิม) | WL4: ชิป Screen ออกทั้งหมด |

เทสอื่นที่ seed `research` / `meta/push` (เช่น p19 · p21 · p38–p40 · p45) ไม่ต้องแก้ — ข้อมูลที่ seed ไว้ไม่มีผลแล้ว
หมายเหตุ: phase13 ล้มตั้งแต่ก่อน ST1 (ต้องใช้ `index.backup-pre-UI1.html` ที่ไม่มีอยู่) — ไม่เกี่ยวกับรอบนี้

| phase8 | "ไม่มี request ไป collection news/macro (rsLoad + วนทุกแท็บ) · ยังอ่าน research + meta/push" (1440 + 430) | ไม่มี news/macro **และต้องมี** path research* + meta/push | ไม่มี news/macro (เหมือนเดิม) **และต้องไม่มี** research* / meta/push | WL4 ข้อ 2: เลิกอ่านทั้ง 2 collection |
