# RG2a — expectation changes (no test deleted · each row = behaviour the RG2a brief changed on purpose)

| Suite | Check / area | Change | Why |
|---|---|---|---|
| phase8 | `Calc.ffCoreCap` stale (6 business days, 2 red) | expected `cap` 100 → **50** (`stale:true` unchanged; 5 days still 50 / not stale) | brief #1: stale data no longer switches to 100 % |
| phase8 | "ไฟล์เก่า 6 วันทำการ + แดง 2 ตัว" every readout (bar, `ffDeployCap`) | expected 100 → **50**; warning text now `size from last known state` + `6 business days` (was `ไม่ลดเพดาน` + `6 วันทำการ`); amber colour unchanged | brief #1 + §3.2 `coreFWarn`/Flow bar wording |
| phase12 | Flow Regime chips `ACWI/BIL ↑ เขียว · 3w` / `HYG/IEI ↓ แดง · 1w` | suffix `w` → **`d`** | brief §3.2: daily ratios use the `d` suffix |
| phase28 | `coreFWarn` / sheet text at 6 business days | `⚠ Fund-flow เก่า 6 วันทำการ · ไม่ลดขนาดไม้ (100%)` → **`⚠ Regime data is 6 business days old — size from last known state`** | brief §3.2 |
| phase42 | stale warn regex + on-screen text (`[data-c-ffwarn]`) | regex → `^⚠ Regime data is \d+ business days old — size from last known state$`; on-screen must contain `size from last known state` (was `ไม่ลดขนาดไม้`) | brief §3.2 |
| phase87 | Journal Lean card child classes | `["ln3-jl1","ln3-jl2","ln3-jl3"]` → `["ln3-jl1","ln3-jl2","jPva","ln3-jl3"]` | brief §3.4: per-trade "Planned 1R · target … → got … · Stop respected" line |
| phase106 | Today (lean) child order | `["news","goals","sw","panels","other"]` → `["td3-rg","news",…]` | brief §3.2: regime verdict line at the very top of Today |

Not retired (fail the same way on `main` or need Mac-only files): see the RG2a report.
