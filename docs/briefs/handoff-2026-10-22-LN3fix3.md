# Handoff — Trading Dashboard orchestrator (22 Oct 2026 · after LN3fix2, LN3fix3 sent)

> Start-of-chat file for the new orchestrator chat. **Communicate in English from now on** (user request 22 Oct). UI text in the app is Thai today — an English UI round (EN1) is queued after LN3fix3.
> Older history: `claude/handoff-2026-10-17-PV2.md` (RR2 → LN3fix2, very detailed). This file is the current state.

## Role
- You are the **orchestrator** for SRTp's Trading Dashboard. You do not edit `index.html` yourself.
- Loop: discuss + mockup with the user → write a brief for **Claude Code (CC)** on the user's Mac → user pastes CC's report → you **verify on the cloud** (full test run + screenshots) → update this handoff.
- User standing rules: answer simply · ask when ambiguous · Objective = Simple · Clear · Easy to use · Effective · show "original vs proposed" (pros/cons) when changing things · token-efficient, concise · big outputs: outline first.
- Brief rules: brief stored in **2 places** (Mac `docs/briefs/` + Project `claude/`) and **compare sha256** · mockups in Mac `docs/mockups/` + Project `claude/mockups/` · every CC command ends with **"ไม่ push ไม่ลบไฟล์"** (no push, no deletion) · temp files → `_to_delete/`, never rm · old tests: only change expected values, never delete/weaken cases, never leave them failing · full suite once at the end, one suite at a time.
- Mockups must fit the screen (check 300/320/390 mobile and 1280/1440 Mac for horizontal overflow) — the user cares a lot.

## Environment
- Mac folder: `/Users/peach/Documents/Dashboard` (device_bash: `$HOME/mnt/Dashboard`). Not a git repo.
- Single-file app `index.html` (Firebase/Firestore, GitHub Pages). `core-size.js` copied into index (`tools/sync_core_size.py --check`).
- Tests: `tests/run_tests.py` (base) + `tests/run_tests_phaseN.py` (now up to 92; LN3fix3 adds 93–94) · `tests/check_syntax.py` · `node tests/core_size_test.js` (471 after LN3fix2).
- **Lesson:** `device_commit_files` with `stagedPath` once reported "written" but the Mac kept the old file → always re-check sha256 on the Mac; if stale, SendUserFile then commit by `fileUuid` (force).

## Cloud verification procedure
1. On Mac: `tar czf _to_delete/<x>.tgz --exclude=./.venv-fundflow --exclude=./_to_delete --exclude='./tests/_bk_*/*' --exclude='./tests/screenshots/*' --exclude='./backups' --exclude='*/__pycache__' .` and `tar czf _to_delete/<x>shots.tgz tests/screenshots/<round>-*` → stage both → extract into a fresh cloud dir.
2. `cmp index.backup-pre-<ROUND>.html` with the previously verified index (keep the previous verified copy!) · sha256 of index/core-size vs Mac.
3. `python3 tests/check_syntax.py` · `node tests/core_size_test.js` · `python3 tools/sync_core_size.py --check` · if core-size changed, also run the **previous** core_size_test.js against the new core-size (backward compat).
4. Full run in 3 parallel groups, resumable (container restarts happen — resume from done.txt). Scripts (recreate in /tmp):
```bash
# run_grp2.sh  D L phases...
D=$1; L=$2; shift 2; cd $D; mkdir -p $L
for p in "$@"; do
  if [ "$p" = base ]; then timeout 1500 python3 tests/run_tests.py > $L/base.log 2>&1
  else timeout 1500 python3 tests/run_tests_phase$p.py > $L/phase$p.log 2>&1; fi
  echo "$p rc=$?" >> $L/done.txt
done
# full.sh  D L   (skips phases already in done.txt; edit 92 → last phase)
D=$1; L=$2; mkdir -p $L; touch $L/done.txt; done=$(awk '{print $1}' $L/done.txt | tr '\n' ' ')
rem=""; for p in base $(seq 94 -1 1); do echo " $done " | grep -q " $p " || rem="$rem $p"; done
G1="";G2="";G3="";i=0; for p in $rem; do case $((i%3)) in 0) G1="$G1 $p";; 1) G2="$G2 $p";; 2) G3="$G3 $p";; esac; i=$((i+1)); done
bash run_grp2.sh $D $L $G1 & bash run_grp2.sh $D $L $G2 & bash run_grp2.sh $D $L $G3 & wait; echo ALLDONE >> $L/done.txt
# summ.sh  L   (prints only failing suites)
cd $1; for f in *.log; do s=$(grep -E "PASS: *[0-9]+ *FAIL: *[0-9]+|สรุป: PASS" $f | tail -n1); fl=$(echo "$s" | grep -oE "FAIL:? *[0-9]+" | grep -oE "[0-9]+"); if [ -z "$s" ]; then echo "$f NOSUMMARY: $(tail -n1 $f | cut -c1-150)"; elif [ "$fl" != "0" ]; then echo "$f $s"; grep -E "^ *FAIL -" $f | cut -c1-140; fi; done
```
   Run with `nohup bash full.sh <dir> <logdir> &` and poll `wc -l done.txt` (≈ 60–90 min total).
5. **Accepted cloud failures** (not code bugs): p13 (no backup-pre-UI1) · p14 430 '+ แผน' · p22 ＋ button and `_extracted.js` (no `_to_delete` in cloud copy) · p25 232px · p37 0.1 flake · p40/p47/p66 backup-folder checks · p82 TradingView image cannot load from cloud (ERR_TUNNEL) · p39 can flake in parallel → re-run alone · p3 fails on Sundays Thai time (re-run with TZ=Pacific/Honolulu) · p6 'ยกเลิก 20' on the 20th of a month.
6. View screenshots (montage with PIL, read the image) — compare with mockups.

## Status
- Verified ✅ on cloud: RR2 · PV2a/b/c · LN1 · LN2 · LN3 · LN3fix · **LN3fix2** (index sha `b064af2b…`, core-size `aa370406…`; full run only accepted failures; old core tests 442 pass on new core-size). User deployed LN3fix2 and is using it.
- **LN3fix3 brief written 22 Oct** → `docs/briefs/LN3fix3-brief.md` + `claude/LN3fix3-brief.md`, mockups `ln3fix3-mac-mockup.html`, `ln3fix3-plan-mockup.html`. **Waiting for CC's report** — the user will paste it into the new chat. Then verify (keep a copy of the LN3fix2 index as the previous verified version: sha `b064af2b…`).

## What LN3 → LN3fix3 decided (keep consistent)
- **Lean view everywhere** (`localStorage ln1_plan_view` = lean | legacy, one switch in Settings › Display; old tests seed legacy via `tests/ff_stub.py`).
- **Sat plan:** Strategy card per asset (chart full image + TradingView link · Trend ▲ Up / ▼ Down + Flat · Macro · Zone ▲ / Zone ▼ (replaced support/resistance, auto-migrated) · Shift). Trend flips unlimited but need a reason (trend_log). Against Macro = full size + required reason. Main form pulls Zone by direction (checkbox, warn only). Tactical has its own Zone. Plan rows "Entry · SL"; "แผน & ไม้ที่ถือ" replaces Positions (open rows expanded, unplanned trades red tag). Mobile: asset tab bar; Mac: tiles in 2 columns; tapping a plan row switches the Strategy card (no scroll on mobile).
- **Core plan Lean:** one summary box (Risk Core x% / 20%), card rows, ⋯ menu (close/edit/cancel/delete/lots/stop history/emergency stop). **Accelerator lot (ไม้เร่ง):** tick when adding; own SL and own risk budget (default 0.35%, "≈1/3 of Base budget" by risk); stopped out = sell only the accelerator lots; Base keeps its SL. Base budget per stock (user wants ≈1.0%), first-lot risk default 0.6, add-on default = half of previous lot's risk, >50% of previous lot = warning only (not for accelerator). Per-stock money cap default 15% (max 25). `maxLots` counts Base lots only. W/L shown as **Winners / Ladder**. Account labels show market (`หลัก · US+TH`).
- **Mac layout (≥1000px):** 2 columns on every tab; Watch list 355px; Journal table; Flow RRG open.
- **LN3fix3 (pending):** Lean Macro box (only "เปลี่ยนเมื่อ" + My opinion text + small links) · zone order follows Trend + B&P (Break & Pullback) checkbox inline next to the opposite zone · new-week prompt (keep/remove assets; Trend/Zone/Shift/opinion reset, Macro kept; Trend must be picked before + แผน) · Macro re-check reminder after 30 days · Today/Flow/Watch Mac polish.

## Next round queued: EN1 — English UI (decided 22 Oct, write the brief after LN3fix3 is verified)
- Goal: all headings, section titles, field labels, buttons, tabs, badges, hints, warnings, empty states, dialogs and other non-content UI text in **English**.
- **Language switch, English default:** one EN/TH string table; Settings › Display › Language (EN | TH); stored per device like `ln1_plan_view`. Thai stays available.
- **Old tests:** seed `TH` in `tests/ff_stub.py` (same trick as the legacy seed) so the ~94 Thai-expectation suites keep passing unchanged; new tests check EN.
- **Not translated (content):** user-typed text (ideas, reasons, My opinion, notes, journal comments, account names) and imported research (thesis cards, Macro Playbook JSON text, Watch articles).
- **Dates:** follow the UI language → English dates/months under EN (e.g. `Wed 22 Oct`, `20–26 Oct`).
- Suggested process: CC first extracts every UI string into the table (no behaviour change, TH output identical — verify with the full suite), then adds the EN column + switch; mockups not needed — give CC a short glossary for key terms (Strategy, Zone ▲/▼, B&P, Trend Shift, Main/Tactical, Base/Accelerator, Winners/Ladder, Open Risk, Focus, Today task names, etc.) and ask for a screenshot of every tab at 390 + 1440 in EN.

## User to-dos after deploy (remind once)
- Settings › Core: Base budget **1.0**, first-lot risk **0.6**, accelerator budget **0.35**, per-stock cap **15**, max Base lots as used (e.g. 3), consider lowering first-lot cap Tier A (default 15% = same as per-stock cap).
- Settings › Sat: "ขนาดไม้เมื่อสวน Macro" = **1** (currently 0.6).

## Open ideas (not scheduled)
- Today: the duplicate "XAU เติมไม้ 2 ได้" row is included in LN3fix3 §5.4.
- Journal stats by layer (Base vs accelerator) beyond the filter chip — later, after real data.
