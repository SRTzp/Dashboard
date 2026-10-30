# CS1 — expectation changes (no test deleted · each row = behaviour the CS1 brief changed)

| Suite | Check / area | Change | Why |
|---|---|---|---|
| phase77 `idea()` helper | Tactical plans created by helper | now also sets `classify:'clear'` | Tactical needs Clear Trend (B3b) — same pattern PF1 used for Trend |
| phase98 | Classify options Strong/Normal/Uncertain, colours, Up/Down text | `sel_opt` maps strong/normal→clear, uncertain→unclear; expected texts "Clear Trend Up/Down", "Unclear"; Normal's blue/purple gone; Tactical TP check sets Clear Trend first | Classify = Clear Trend / Unclear |
| phase104 `fill_active` | Entry/SL/TP fill on a Tactical card | sets Clear Trend first | Tactical fields disabled until Clear Trend |
| phase106 B7 | Tactical draft "Incomplete SL/TP missing" | fixture idea has `classify:'clear'` | Unclear Tactical shows Pending "Needs Clear Trend" (new name) |
| phase107 §3 | Cand → WL form: "Tier passed"/"RS Leader" checkboxes, `Need: Tier or RS · rating`, `promoted_by ['tier','rs']` | form now has Edit Stock Evaluation; `Need: Stars · RS · Gate 5 (0/3)`; helper `ev_pass` writes RS+Gate 5 eval; promoted_by `['rs']` | Gate = ★ ≥1 + RS + Gate 5 (Part A §3) |
| phase108, phase109 | `[data-td4-pro-tier]` checkbox | replaced by `T.ev_pass(page)` / `csGateOf().rs` | same |
| phase61, phase62 | direct `td4ProSave()` calls | write a passing eval first | Move gate needs evaluation |
| phase33 §8 | WL edit modal "ตั้ง Tier…" button → plan form | button hidden; `Edit Stock Evaluation` opens the evaluation sheet | Tier is no longer set from the plan form |
| phase89 §2 (≈25 checks) | Lean plan form Tier block, Yes/No rows, Tier calc samples, Risk % editing, `บันทึกเฉพาะ Tier` | **RETIRED** (prints RETIRED) — behind `CS1_RETIRED` | Evaluation UI removed from the plan screen; star banner + read-only Risk covered by phase111 |
| phase91 §10 | Plan form editable Risk % / Tier line / buy-1 from that plan | **RETIRED** (`CS1_RETIRED`) | Risk % is read-only, derived from ★ |
| phase15, phase18 | `Export JSON ตอนนี้` / backup hint wording | English strings | Settings → English |
| phase23, phase24, phase31, phase34, phase37, phase64, phase65 | Settings labels/units (`% ของถัง Core`, `ประตู FF`, `Risk/ไม้`, `weeks`, formula line…) | expected strings → English | Settings → English (values unchanged) |
