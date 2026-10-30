#!/bin/bash
# make_verify.sh <ROUND> — สร้าง docs/reports/<ROUND>-verify.txt จากผลคำสั่ง/ล็อกของจริงเท่านั้น (ไม่พิมพ์มือ) · ≤ 60 บรรทัด
# ต้องรัน tests/runall2.sh ก่อน (ผลอยู่ที่ $RUNALL_OUT · ค่าเริ่มต้น _to_delete/runall2) · ใช้: bash tests/make_verify.sh PF3
# NEW_SUITE (ค่าเริ่มต้น = suite ใหม่ล่าสุดของรอบ) ตั้งผ่านตัวแปรแวดล้อม เช่น NEW_SUITE=phase103
R="${1:?usage: make_verify.sh <ROUND>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT" || exit 1
OUT="${RUNALL_OUT:-$ROOT/_to_delete/runall2}"
NODE=/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/playwright/driver/node
LC="$(echo "$R" | tr 'A-Z' 'a-z')"
NEW="${NEW_SUITE:-$(ls tests/run_tests_phase*.py | sed 's/.*phase\([0-9]*\)\.py/\1/' | sort -n | tail -1 | sed 's/^/phase/')}"
REP="docs/reports/${R}-verify.txt"
BK="${BK_OVERRIDE:-index.backup-pre-${R}.html}"
{
  echo "round: $R   date: $(date '+%Y-%m-%dT%H:%M:%S%z')"
  echo "index.html sha256: $(shasum -a 256 index.html | cut -d' ' -f1)"
  echo "backup $BK sha256: $(shasum -a 256 "$BK" | cut -d' ' -f1)"
  cs=$(python3 tests/check_syntax.py >/dev/null 2>&1 && echo OK || echo FAIL)
  ct=$("$NODE" tests/core_size_test.js 2>&1 | grep -E '^PASS +[0-9]+' | sed -E 's/^PASS +([0-9]+) ผ่าน · ([0-9]+) ไม่ผ่าน.*/\1 \2/')
  cp_=${ct% *}; cf_=${ct#* }; [ -z "$ct" ] && { cp_=0; cf_=?; }
  sc=$(python3 tools/sync_core_size.py --check >/dev/null 2>&1 && echo OK || echo FAIL)
  if [ "$cf_" = "?" ]; then ctot="?"; else ctot=$((cp_ + cf_)); fi
  echo "check_syntax: $cs · core_size_test: ${cp_}/${ctot} · sync_core_size --check: $sc"
  # suite ใหม่ของรอบ: นับ PASS/FAIL จากล็อกชุดเต็ม (ถ้าไม่มีล็อก = รันตรงตอนนี้ไม่ได้ → ระบุว่าไม่มี)
  lg="$OUT/logs/run_tests_${NEW}.log"; [ -f "$OUT/logs_rerun/run_tests_${NEW}.log" ] && lg="$OUT/logs_rerun/run_tests_${NEW}.log"
  if [ -f "$lg" ]; then p=$(grep -c '^PASS' "$lg"); f=$(grep -c '^FAIL' "$lg"); echo "new suite $NEW: $p/$((p+f)) checks"; else echo "new suite $NEW: no log"; fi
  if [ -s "$OUT/final.tsv" ]; then
    tot=$(wc -l < "$OUT/final.tsv" | tr -d ' '); ok=$(awk -F'\t' '$2=="ok"' "$OUT/final.tsv" | wc -l | tr -d ' ')
    full=no; [ -e "$OUT/DONE" ] && full=yes
    echo "suites run: $ok/$tot  (full run: $full)"
    bad=$(awk -F'\t' '$2!="ok"{print $1}' "$OUT/final.tsv")
    if [ -z "$bad" ]; then echo "FAIL none"; else
      for s in $bad; do
        l="$OUT/logs_rerun/$s.log"; [ -f "$l" ] || l="$OUT/logs/$s.log"
        echo "FAIL $s [after solo rerun]: $(grep '^FAIL' "$l" | head -3 | cut -c1-170 | tr '\n' '|')"
      done
    fi
  else echo "suites run: 0/0  (full run: no)"; echo "FAIL none"; fi
  n=$(grep -c '^|' "tests/${R}_retired.md" 2>/dev/null); n=$(( ${n:-0} > 2 ? n - 2 : 0 ))
  echo "expectation changes: tests/${R}_retired.md · $n entries"
  for f in tests/screenshots/${LC}-*.png; do [ -f "$f" ] && echo "screenshots: $(basename "$f") $(stat -f %z "$f")"; done
  # files changed: diff เทียบกับ backups (index + tests/_bk_<round>/)
  d=$(diff "$BK" index.html | grep -c '^>'); r=$(diff "$BK" index.html | grep -c '^<'); echo "files changed: index.html (+$d/-$r)"
  for b in tests/_bk_${LC}/*; do
    [ -f "$b" ] || continue; name=$(basename "$b"); cur="tests/$name"; [ -f "$cur" ] || continue
    d=$(diff "$b" "$cur" | grep -c '^>'); r=$(diff "$b" "$cur" | grep -c '^<')
    [ "$d$r" != "00" ] && echo "files changed: tests/$name (+$d/-$r)"
  done
  for f in tests/run_tests_phase*.py; do case "$f" in *.backup-pre-*) continue;; esac; [ -f "tests/_bk_${LC}/$(basename "$f")" ] || echo "files changed: $f (+$(wc -l < "$f" | tr -d ' ')/-0) [new]"; done
  for f in docs/weekly-impact-schema.md tests/PF3_retired.md tests/PF3b_retired.md tests/PF1_retired.md tests/runall2.sh tests/make_verify.sh "docs/reports/${R}-report.md"; do [ -f "$f" ] && echo "files changed: $f"; done
} > "$REP"
head -60 "$REP" > "$REP.tmp" && mv "$REP.tmp" "$REP"
wc -l "$REP"
