# WT1 — เคสที่แก้ความคาดหวัง/อินพุต (tests)

เคสที่ใช้ `#wlAddTier` (dropdown A/B ในโมดัล Watchlist) อยู่ในชุดเดียวคือ **phase29 · section_B_watch (B2)** — ชุดอื่นไม่ขัดกับ brief · ไม่มีเคสที่ลบ/ปล่อยล้ม · จำนวนเคส phase29 เท่าเดิม (175 → 175: แก้ความคาดหวัง 6 เคส + เคสที่ไม่เกี่ยว 1 เคสคงเดิม) · สำเนาไฟล์เทสเดิม: `backups/run_tests_phase29.backup-pre-WT1.py`

| ชุด | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| phase29 | B2 โมดัลเพิ่ม: ช่อง Tier | `#wlAddTier` = 'ยังไม่ตั้ง' · มี 3 ตัวเลือก | ไม่มี `#wlAddTier` · ส่วน Tier (`#wlAddTierBox`) ซ่อน | brief ข้อ 3: โมดัลเพิ่มหุ้นใหม่ไม่มีส่วน Tier |
| phase29 | B2 เพิ่มใหม่ + ตั้ง A (NEWT) | เลือก A ในโมดัล → doc `tier:'A'` · `tier_set_at` = วันนี้ | เพิ่มใหม่ → doc **ไม่มี** `tier`/`tier_set_at` | `wlAddSave` ไม่เขียนฟิลด์ Tier อีกแล้ว · ตั้ง Tier ผ่านปุ่ม "บันทึกเฉพาะ Tier" (ครอบคลุมใน phase33 เคส 1–3) |
| phase29 | B2 โมดัลแก้ไข WLA แสดง Tier | dropdown = 'A' · `#wlAddTierSince` มี 'ตั้งเมื่อ 2026-01-05' | บรรทัดสถานะ `#wlAddTierSt` มี 'Tier A' + '2026-01-05' (doc เก่า = 'A · Fortress (เดิม)') · ไม่มี dropdown | brief ข้อ 3: แทน dropdown ด้วยบรรทัดสถานะ |
| phase29 | B2 เปลี่ยนเป็น B | เลือก B ใน dropdown → `tier:'B'` · `tier_set_at` = วันนี้ | seed `tier:'B'` + `tier_set_at` ลง doc ตรง ๆ → โมดัลแก้ไขแสดง 'Tier B' | ไม่มี dropdown ให้เลือกแล้ว (brief อนุญาต seed ตรง ๆ) |
| phase29 | B2 เลือก 'ยังไม่ตั้ง' | dropdown '' + บันทึก → ลบ `tier`/`tier_set_at` | กดลิงก์ `ล้าง Tier` (`#wlAddTierClr`) → ลบฟิลด์ (ทั้ง 6 · phase33 เคส 8 ตรวจครบ 6) | brief ข้อ 3 |
| phase29 | B2 แก้ Note อย่างเดียว · เพิ่มใหม่ไม่ตั้ง Tier (NEWU) | — | ไม่เปลี่ยน (ผ่านเหมือนเดิม) | — |
| phase29 | B2 ชิปในรายการ/หัวรายละเอียด (`[data-wl-tier="A"]` · `ทบทวน`) | — | ไม่เปลี่ยน (ยังผ่าน — ชิปยังมี `data-wl-tier`) | ชิปแบบสั้นคง A/B · แบบ long เปลี่ยนข้อความเป็น `A · Fortress` ฯลฯ แต่ phase29 ตรวจด้วย selector ไม่ใช่ข้อความ |
