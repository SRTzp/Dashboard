# BR1 — เทสเก่าที่แก้ความคาดหวัง (ไม่ลบเคส · ไม่ทำให้อ่อนลง)

| ชุด | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| phase1 | "SAT7D_LABEL.BTCUSD ยังเป็น 'BTC' เหมือนเดิมหลังรวม" (1440 + 430) | อ่าน `SAT7D_LABEL.BTCUSD` | อ่าน `sat7dLabel('BTCUSD')` — ค่าที่คาดหวังเหมือนเดิม (`'BTC'`) | BR1: `SAT7D_LABEL` (ค่าคงที่ตอนโหลด) ถูกเลิกใช้ → `sat7dLabel(key)` อ่าน `satAssetCfg` ก่อน |
| phase24 (helper `txt`) | เคสหัวบัญชี Core (CX1) | เปิด `details[data-c-more]` ทุกครั้งที่เรียก | เปิดเฉพาะเมื่อ selector เป็นหัวบัญชี/ชิปที่ถูกพับ (`core-head`, `data-c-cashfree/l2/lshare/gate/missing`) | การเปิด details ทุกครั้งทำให้หัวสูงขึ้น → เกิด scrollbar → `small` ในการ์ดตัดบรรทัด → phase25 เคส 11 (การ์ดขยายสูง ≤ 230px) ล้มเฉียด 231.6px · แก้ที่ตัวช่วย ไม่ใช่ที่ขีดจำกัด |

เทสอื่นที่ใช้ `SAT_ASSETS` / `SAT7D_ASSETS` / `sat7dBrokerOpts` (phase2 · 14 · 15 · 34) ผ่านโดยไม่ต้องแก้ — ทั้งสามยังอยู่ (SAT_ASSETS = รายชื่อตั้งต้น 4 ตัว)
หมายเหตุ: phase13 ล้มตั้งแต่ก่อน CX1 (ต้องใช้ `index.backup-pre-UI1.html` ที่ไม่มี) — ไม่เกี่ยวกับรอบนี้
