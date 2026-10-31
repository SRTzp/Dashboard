# RG2b — expectation changes

## Done (tests/core_size_test.js, 12 cases, expected values only)
`canPlaceLadder` no longer has the f-gate, `L_SHARE_OVER`, `LAYER2_OVER`, and Winner cost no longer eats Ladder cash. Cases changed:
ชั้น 2 รวมบันไดใหม่ = 2.24% (pctFull gone → sharePct) · ประตูปิด (green) · ประตูปิด (unknown) · ไม่ส่ง gate = งด · ชั้น 2 รวมบันไดใหม่เกิน 20% · เกิน → ไม่อนุญาต · ชั้น 2 นับที่จองของบันไดเดิมด้วย · เงินสดไม่พอจอง · L รวมเกิน 30% · 7E-2b-1 l2Cap 0.25 · 7E-2b-1 shareCap 0.20 · รวมเหตุผลหลายข้อ.
Count unchanged (471 → 471 old + 31 new = 502).

## NOT done — suites whose old expectations now differ (new failures vs main, final after solo re-run)
Root causes (all intended by the brief): Winner/Sat sizes now come from the 50/30/20 pools (smaller than the old capital); no Macro size ×; Sat new-trades quota 4 (Main+Tactical together); `coreGate` removed; scope labels Winner|Ladder|Sat; Core Settings fields changed.
run_tests(5) phase3(9) phase5(+2) phase11(3) phase23(+5) phase24(65) phase25(+13) phase27(17) phase30(7) phase31(9) phase34(8) phase37(5) phase39(1; crashes on removed `coreGate`) phase42(+2) phase53(6) phase64(1) phase65(4) phase67(3) phase68(5) phase69(9) phase70(7) phase77(2) phase78(22) phase79(3) phase80(+2) phase81(+0..4) phase82(6) phase83(2) phase84(3) phase89(2) phase91(17) phase92(9) phase96(11) phase97(6) phase98(1) phase99(1) phase107(2) phase111(15)  — ≈294 failing checks in total.
