#!/bin/bash
# runall2.sh — ชุดเต็มแบบเร็ว: base (run_tests.py) + phase 1–111 · 2 worker ขนาน (xargs -P 2) · 1 log ต่อ suite · timeout ต่อ suite 1500 วินาที
# (timeout ของ Playwright ในแต่ละเทสไม่ถูกแก้) · ไม่ fail-fast · รันจบแล้ว suite ที่ล้มจะถูกรันซ้ำ "ทีละตัวเดี่ยว" 1 ครั้ง (กัน flake จากการขนาน) และเก็บผลการรันซ้ำ
# false failure ที่รู้อยู่แล้ว (ไม่แก้): p13 เสมอ · p3 วันอาทิตย์ · p6 วันที่ 20
# ใช้: caffeinate -i -s bash tests/runall2.sh   · ผลอยู่ที่ $RUNALL_OUT (ค่าเริ่มต้น ../_to_delete/runall2): logs/*.log · results.tsv (รอบขนาน) · final.tsv (หลังรันซ้ำ) · DONE
cd "$(dirname "$0")" || exit 1
OUT="${RUNALL_OUT:-../_to_delete/runall2}"
mkdir -p "$OUT/logs" "$OUT/logs_rerun"
: > "$OUT/results.tsv"; : > "$OUT/final.tsv"; [ -e "$OUT/DONE" ] && mv "$OUT/DONE" "$OUT/DONE.$(date +%s)"
export OUT

list_suites(){ echo run_tests.py; for n in $(seq 1 111); do [ -f "run_tests_phase$n.py" ] && echo "run_tests_phase$n.py"; done; }

# หนึ่ง suite: คืน rc (timeout 1500 วินาที ด้วย perl alarm) · ล้ม = rc ≠ 0 หรือมีบรรทัด FAIL
run_one(){
  f="$1"; n="${f%.py}"; dir="$2"
  perl -e 'alarm shift; exec @ARGV' 1500 python3 "$f" > "$dir/$n.log" 2>&1; rc=$?
  nf=$(grep -c '^FAIL' "$dir/$n.log"); np=$(grep -c '^PASS' "$dir/$n.log")
  st=ok; if [ "$rc" -ne 0 ] || [ "$nf" -ne 0 ]; then st=fail; fi
  printf '%s\t%s\t%s\t%s\t%s\n' "$n" "$st" "$rc" "$nf" "$np"
}
export -f run_one

list_suites | xargs -P 2 -I{} bash -c 'run_one {} "$OUT/logs"' >> "$OUT/results.tsv"

# รันซ้ำเฉพาะที่ล้ม ทีละตัว (เดี่ยว) แล้วใช้ผลรันซ้ำเป็นผลสุดท้าย
cp "$OUT/results.tsv" "$OUT/final.tsv"
awk -F'\t' '$2=="fail"{print $1}' "$OUT/results.tsv" | while read -r n; do
  r=$(run_one "$n.py" "$OUT/logs_rerun")
  grep -v "^$n"$'\t' "$OUT/final.tsv" > "$OUT/final.tmp"; printf '%s\trerun\n' "$r" | sed 's/\trerun$//' >> "$OUT/final.tmp"; mv "$OUT/final.tmp" "$OUT/final.tsv"
done
sort -V "$OUT/final.tsv" -o "$OUT/final.tsv"
date > "$OUT/DONE"
