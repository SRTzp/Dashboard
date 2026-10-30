# HD1 — retired / updated expectations

ไม่มีเคสถูกลบหรือผ่อนปรน — แก้เฉพาะวิธีคลิก/ตำแหน่งที่ brief เปลี่ยน

| suite | เคส | เปลี่ยนเพราะ |
|---|---|---|
| phase83 | 2 เลือกบัญชีหลัก / Family (3 จุด คลิก `[data-ln3-acc=…]`) | ที่ Mac ≥900px ตัวควบคุมย้ายเข้า header และอาจแสดงเป็นรูปย่อ (ปุ่มเดิมถูกซ่อน แต่ยังเป็น node เดียวกัน) → เปลี่ยน `.click()` เป็น `.dispatch_event('click')` บน node เดิม · ค่าที่ตรวจเท่าเดิม |

หมายเหตุ: `.planScope` / `[data-ln3-accsw]` ที่ Mac ≥900px และมือถือ ≤480px (Lean) อยู่ใน `#hdrSub` แล้ว — node เดิม ไม่ clone
