/* tests/core_size_test.js — เทส core-size.js ด้วยตัวเลขจาก claude/core-risk-framework.md
   รัน: node tests/core_size_test.js   (ไม่ต้องติดตั้งอะไร · ไม่แตะ index.html) */
'use strict';
var path = require('path');
var C = require(path.join(__dirname, '..', 'core-size.js'));

var pass = 0, fail = 0;
function eq(name, got, want) {
  var ok = got === want;
  if (ok) pass++; else { fail++; console.log('FAIL  ' + name + '  got=' + got + '  want=' + want); }
}
function near(name, got, want, tol) {
  var ok = typeof got === 'number' && Math.abs(got - want) <= (tol == null ? 1e-6 : tol);
  if (ok) pass++; else { fail++; console.log('FAIL  ' + name + '  got=' + got + '  want=' + want); }
}
function section(s) { console.log('— ' + s); }

/* AU1 — core-size.js no longer sizes anything (the engine does). Only poolSplit · poolFree · status remain, with their tests. */
section('status (position-health dot)');
var T = '2026-09-30';
eq('เขียว', C.status({ px: 108, pxDate: '2026-09-27', today: T, stop: 90, ema10: 104.2 }).status, 'green');
eq('เหลือง (ใต้ EMA10)', C.status({ px: 96.5, pxDate: '2026-09-27', today: T, stop: 70, ema10: 99.1 }).status, 'yellow');
eq('แดง (ใต้ Stop)', C.status({ px: 89, pxDate: '2026-09-27', today: T, stop: 90, ema10: 104 }).status, 'red');
eq('แดงก่อนเหลือง', C.status({ px: 60, pxDate: '2026-09-27', today: T, stop: 70, ema10: 99 }).status, 'red');
eq('ปิดเท่า Stop ไม่ใช่แดง', C.status({ px: 90, pxDate: '2026-09-27', today: T, stop: 90 }).status, 'green');
eq('เก่า 7 วัน ยังใช้ได้', C.status({ px: 108, pxDate: '2026-09-23', today: T, stop: 90 }).status, 'green');
eq('เก่า 8 วัน → ⚪', C.status({ px: 108, pxDate: '2026-09-22', today: T, stop: 90 }).status, 'na');
eq('ไม่มีราคา → ⚪', C.status({ pxDate: '2026-09-27', today: T, stop: 90 }).status, 'na');
eq('ไม่มีวันที่ → ⚪', C.status({ px: 108, today: T, stop: 90 }).status, 'na');
eq('ไม่มี EMA10 ข้ามข้อเหลือง', C.status({ px: 50, pxDate: '2026-09-27', today: T, stop: 40 }).status, 'green');
eq('อายุ 3 วัน', C.status({ px: 108, pxDate: '2026-09-27', today: T, stop: 90 }).age, 3);

section('poolSplit');
var ps = C.poolSplit({ total: 1000000 });
eq('poolSplit ค่าเริ่ม 50/30/20 ok', ps.ok, true);
near('poolSplit Winner 500,000', ps.winner, 500000);
near('poolSplit Ladder 300,000', ps.ladder, 300000);
near('poolSplit Sat 200,000', ps.sat, 200000);
eq('poolSplit รวม 99 → SUM_NOT_100', C.poolSplit({ total: 1e6, pct: { winner: 50, ladder: 30, sat: 19 } }).err, 'SUM_NOT_100');
eq('poolSplit ติดลบ → BAD_PCT', C.poolSplit({ total: 1e6, pct: { winner: -10, ladder: 60, sat: 50 } }).err, 'BAD_PCT');
eq('poolSplit เกิน 100 → BAD_PCT', C.poolSplit({ total: 1e6, pct: { winner: 101, ladder: 0, sat: -1 } }).err, 'BAD_PCT');
eq('poolSplit 0/100/0 ผ่าน', C.poolSplit({ total: 1e6, pct: { winner: 0, ladder: 100, sat: 0 } }).ladder, 1e6);
eq('poolSplit ไม่มียอดรวม → NO_TOTAL', C.poolSplit({ total: 0 }).err, 'NO_TOTAL');
eq('poolSplit ค่าเริ่ม DEFAULTS.poolSplit', JSON.stringify(C.DEFAULTS.poolSplit), '{"winner":50,"ladder":30,"sat":20}');

section('poolFree');
var pfW = C.poolFree({ pool: 500000, held: 200000 });
near('Winner ว่าง = ถัง − ถือ', pfW.free, 300000);
eq('ใช้เกินถัง = over (เตือน ไม่ปิด)', C.poolFree({ pool: 100000, held: 150000 }).over, true);
eq('ใช้เกินถัง ว่าง = 0', C.poolFree({ pool: 100000, held: 150000 }).free, 0);
eq('the sizing functions are gone', ['firstLot','addLot','ladder','ladderBudget','applyStopMove','layer2','vsCost','emergencyStop','classifyTier','tierBadge','ddStep','openGate','canPlaceLadder','portfolioSplit','ladderShare','accountDrop','floorLot'].filter(function (k) { return k in C; }).length, 0);

console.log('\n' + (fail === 0 ? 'PASS' : 'FAIL') + '  ' + pass + ' ผ่าน · ' + fail + ' ไม่ผ่าน');
process.exit(fail === 0 ? 0 : 1);
