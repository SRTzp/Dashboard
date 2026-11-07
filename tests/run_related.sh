#!/bin/bash
# run_related.sh <OUTDIR> <suite.py>... — รันเฉพาะ suite ที่ระบุ (ไม่ใช่ชุดเต็ม) แล้วเขียน logs/ + final.tsv รูปแบบเดียวกับ runall2.sh · ล้ม → รันซ้ำเดี่ยว 1 ครั้ง
# ใช้คู่กับ: RUNALL_OUT=<OUTDIR> bash tests/make_verify.sh <ROUND>  (ไม่มีไฟล์ DONE = "full run: no")
cd "$(dirname "$0")" || exit 1
OUT="$1"; shift; mkdir -p "$OUT/logs" "$OUT/logs_rerun"; : > "$OUT/final.tsv"
run_one(){ f="$1"; n="${f%.py}"; dir="$2"
  perl -e 'alarm shift; exec @ARGV' 1500 python3 -u "$f" > "$dir/$n.log" 2>&1; rc=$?
  nf=$(grep -c '^FAIL' "$dir/$n.log"); np=$(grep -c '^PASS' "$dir/$n.log"); st=ok; { [ "$rc" -ne 0 ] || [ "$nf" -ne 0 ]; } && st=fail
  printf '%s\t%s\t%s\t%s\t%s\n' "$n" "$st" "$rc" "$nf" "$np"; }
export -f run_one
printf '%s\n' "$@" | xargs -P 3 -I{} bash -c 'run_one {} "'"$OUT"'/logs"' > "$OUT/results.tsv"
cp "$OUT/results.tsv" "$OUT/final.tsv"
awk -F'\t' '$2=="fail"{print $1}' "$OUT/results.tsv" | while read -r n; do
  r=$(run_one "$n.py" "$OUT/logs_rerun"); grep -v "^$n"$'\t' "$OUT/final.tsv" > "$OUT/final.tmp"; printf '%s\n' "$r" >> "$OUT/final.tmp"; mv "$OUT/final.tmp" "$OUT/final.tsv"; done
cat "$OUT/final.tsv"
