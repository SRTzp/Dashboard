#!/bin/bash
# TS1 — one regression run. Exit code 0 only if EVERYTHING passes. One summary line per suite.
#   bash tests/run_regression.sh            full run (node + every browser suite, 4 in parallel)
#   bash tests/run_regression.sh --quick    node + the core browser suites (Today · Plan board · plan forms ×3 strategies · Cancel · Journal · Port risk · Settings · snapshot)
#   JOBS=2 bash tests/run_regression.sh     fewer parallel browsers
# Logs: $REG_OUT (default: a temp folder, path printed at the end). Suites that need Playwright/Chromium: pip install playwright && python3 -m playwright install chromium
cd "$(dirname "$0")" || exit 1
ROOT="$(cd .. && pwd)"
QUICK=0; [ "$1" = "--quick" ] && QUICK=1
JOBS="${JOBS:-4}"
OUT="${REG_OUT:-$(mktemp -d "${TMPDIR:-/tmp}/regression.XXXXXX")}"; mkdir -p "$OUT/logs"
: > "$OUT/summary.tsv"
START=$(date +%s)

# ---- fast checks (sequential): name | command
FAST=(
  "check_syntax|python3 tests/check_syntax.py"
  "sync_re1|python3 tools/sync_re1.py --check"
  "sync_ps1|python3 tools/sync_ps1.py --check"
  "sync_core_size|python3 tools/sync_core_size.py --check"
  "sync_pv1|python3 tools/sync_pv1.py --check"
  "rrg_verify (app rrgCompute == pandas)|python3 tests/rrg_verify_test.py"
  "rrg_close_cut (ET 16:15 fake clock)|node tests/rrg_close_cut_test.js"
  "rrg_data_check selftest (offline)|python3 scripts/rrg_data_check.py --selftest"
  "node risk_engine|node tests/risk_engine_test.js"
  "node re1_adapter|node tests/re1_adapter_test.js"
  "node re1c_live|node tests/re1c_live_test.js"
  "node core_size|node tests/core_size_test.js"
  "node ps1_size|node tests/ps1_size_test.js"
  "node ps1b_size|node tests/ps1b_size_test.js"
  "node pv1_posview|node tests/pv1_posview_test.js"
  "hooks superset (LR1 A0)|python3 tests/hooks_test.py"
  "node aw1 (wrapper → run_tests_aw1.py)|node tests/aw1_test.js"
)
# ---- browser suites (python): the core set, then the rest
CORE="run_tests_pv1 run_tests_re1d run_tests_re1c run_tests_re1c2 run_tests_re1b run_tests_ts1 run_tests_ts1b run_tests_phase364 run_tests_phase374 run_tests_phase375 run_tests_phase372 run_tests_phase370"
REST="run_tests run_tests_phase1 run_tests_phase2 run_tests_phase10 run_tests_phase19 run_tests_phase20 run_tests_phase35 run_tests_phase49 run_tests_phase50 run_tests_phase51 run_tests_phase57 run_tests_phase363 run_tests_phase_sw2 run_tests_phase122 run_tests_phase365 run_tests_phase366 run_tests_phase367 run_tests_phase373 run_tests_phase_cg1 run_tests_phase_ht1 run_tests_sh1 run_tests_sh2 run_tests_lr1 run_tests_lr2 run_tests_lr3 run_tests_lrf run_tests_lrf2 run_tests_ef1b run_tests_lr4 run_tests_lr5a"
if [ $QUICK = 1 ]; then BROWSER="$CORE"; else BROWSER="$CORE $REST"; fi

line() { # name rc seconds log
  local st=PASS; [ "$2" != 0 ] && st=FAIL
  local extra; extra=$(grep -E '^(SUMMARY|PASS [0-9]+/|FAIL [0-9]+/|TS1 settings|=+ .*(pass|fail))' "$4" 2>/dev/null | tail -1 | cut -c1-90)
  [ -z "$extra" ] && extra="$(grep -c '^PASS' "$4" 2>/dev/null) checks pass · $(grep -c '^FAIL' "$4" 2>/dev/null) fail"
  printf '%-4s %-48s %4ss  %s\n' "$st" "$1" "$3" "$extra"
  printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$OUT/summary.tsv"
}
for item in "${FAST[@]}"; do
  name="${item%%|*}"; cmd="${item#*|}"; s=$(date +%s)
  ( cd "$ROOT" && eval "$cmd" ) > "$OUT/logs/$(echo "$name" | tr ' /()→' '_____').log" 2>&1; rc=$?
  line "$name" $rc $(( $(date +%s)-s )) "$OUT/logs/$(echo "$name" | tr ' /()→' '_____').log"
done

run_one() { # suite
  local n="$1" s; s=$(date +%s)
  ( cd "$ROOT/tests" && perl -e 'alarm shift; exec @ARGV' 900 python3 -u "$n.py" ) > "$OUT/logs/$n.log" 2>&1; rc=$?
  nf=$(grep -c '^FAIL' "$OUT/logs/$n.log"); [ "$rc" = 0 ] && [ "$nf" != 0 ] && rc=1
  echo "$n $rc $(( $(date +%s)-s ))" > "$OUT/logs/$n.res"
}
export -f run_one; export OUT ROOT
echo "$BROWSER" | tr ' ' '\n' | xargs -P "$JOBS" -I{} bash -c 'run_one {}'
for n in $BROWSER; do read -r a rc t < "$OUT/logs/$n.res"; line "$n" "$rc" "$t" "$OUT/logs/$n.log"; done

FAILS=$(awk -F'\t' '$2!=0' "$OUT/summary.tsv" | wc -l | tr -d ' '); TOTAL=$(wc -l < "$OUT/summary.tsv" | tr -d ' ')
echo "----"
echo "regression: $((TOTAL-FAILS))/$TOTAL ok · $FAILS failing · $(( $(date +%s)-START ))s · logs: $OUT/logs"
[ "$FAILS" = 0 ] && exit 0 || exit 1
