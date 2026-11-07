# CG1 — changed / retired expectations

| Test | Old expectation | New expectation | Why |
|---|---|---|---|
| phase122 §11 Ask why toast | `#sdAskToast`, text `✓ Copied for idea-scout scan\nGoal…\nPaste into Claude → import → tick segments → next: pick`, no buttons, `sdAskMs`/`SD_ASK_MSG`/`sdAskT` | `#cgToast`, 3 `.cgL` lines from `CG_GUIDE.ask`, one ✕ button, `cgToastMs`/`cgToastT`; timing also checked at 40/120/200 chars | `sdAskToast` replaced by shared `showGuideToast` |
| phase49 gap-answers prompt | line 1 `idea-scout update · ตอบข้อที่ขาด #1, #2` | line 1 `idea-scout update:`, line 2 `ตอบข้อที่ขาด #1, #2`, rest shifted by one line | brief §5: extra text on line 1 moves to line 2 |
| phase47 scan prompt (draft idea) | line 1 `idea-scout scan` | `idea-scout scan:` | colon prefix |
| phase47 match prompt | line 1 `idea-scout match` | `idea-scout match:` | colon prefix |
| phase44 Export JSON message | `… แนบให้ idea-scout pick/update` | `… แนบให้ idea-scout update` (idea has companies; `pick` when none) | mode chosen automatically |
| phase44/47 `window.__ideaLastExport` | JSON | unchanged (still pure JSON); full copied text (mode line + blank line + JSON) is in new `window.__ideaLastExportCopy` | keeps old tests valid |
| phase73 trade-check prompt | contains `trade-check` | still passes; line 1 is now `idea-scout trade-check:` | colon prefix, no toast |

Pre-existing, unrelated: phase44 and phase47 each report one `[static]` FAIL for missing backup folders (`tests/_bk_id1/`, `tests/_bk_id3a/`); not touched by CG1.
