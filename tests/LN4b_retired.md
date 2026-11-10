# LN4b — retired / rewritten expectations (2026-11-10)

| Test | Before | After | Why |
|---|---|---|---|
| phase369 §4 "Exec badge present in the To do row" | Exec x/y always shown in the To do row | Exec badge hidden while there are no valid setups (0/0); shown again once a count exists (the next check, "tap records Missed → Exec 0/1", still asserts it) | LN4b §2 — phone To do row |
| phase369 §2 "row height fits two lines (≤96px)" at 390 | Act row = 2 lines | ≤ 112px: Act row = 3 lines (ticker · tag · status / sector+reason / details · button); Mac limit (62px) unchanged | LN4b §2 — ticker is never squeezed |
| phase369 §1 HOT "max 5 chips + +N" | `[data-ln4-hotmore]` was one button | Mac still 5 chips + `+N`; phone shows 3 + `+N` (two `+N` buttons, `.md` / `.mp`, one hidden per breakpoint); `+N` opens a full list instead of jumping to Flow | LN4b §2 |
| HOT definition | Leading + weak (outperforming but fading) + Fresh | Leading only + Fresh (weak dropped); Fresh first, then Leading by strength (RS ratio) | LN4b §2 — 22/23 sectors were HOT |
| phase370 / LN4 "text ≥ 12px" | all LN4 text ≥ 12px at 390 | HOT chips on phone are 11.5px (brief); everything else still ≥ 12px. Tap target for HOT chips 26px (brief: small chips) | LN4b §2 |
| Mac LN4 font sizes (≥ 900px) | 12 / 12.5 / 13 px | 13.5 / 13.5 / 14.5 px (one step up) — covered by phase371 | LN4b §1 |
| TODAY on phone | event chips (`[data-ln4-ev]`, hidden ≤ 560px) | one-line list `[data-ln4-evl]`, same-time grouped, `time tbc` last, max 3 + `+N ›`; Mac keeps the chips | LN4b §2 |
| To do on phone/Mac | one chip per skill/homework/unfinished item | same-kind items grouped: `living-thesis · N stocks ›` (opens the list), same for homework / unfinished | LN4b §2 |
| phase369 §1 "HOT max 5 chips then +N" (second rewrite, brief §3) | 5 chips + `+N` | ★ followed sectors first, then top 3 by strength (Fresh keeps blue tag); Mac = ★ + 3 + `+N`; phone = as many as fit ONE row (`ln4Fit`) + `+N` | LN4b §3 |
| MACRO stance glyphs | plain muted text | per-glyph colour: ▲ teal · ▼ red · ▬ grey (`.glx.u/.d/.f`) | LN4b §3 |
| TODAY events | HIGH only, no impact marker; Mac chips wrapped to extra rows | red dot HIGH / amber dot MED (LOW hidden); Mac = ONE row with `+N` (never wraps); phone = one line per event (max 3 + N) | LN4b §3 |
