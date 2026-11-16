"""TS1 — check-level retirement. A check is listed here ONLY when the feature / text it asserts was removed or redesigned on purpose
(job + evidence named). A retired check is printed as RETIRED (never PASS, never counted); every other check in the suite still runs and counts.
Suite-level retirements live in tests/_retired/ (see its README)."""
import sys

RULES = {
    "run_tests_phase35": [
        ("#satHeatHint ชี้ไปที่ช่อง Sat ใน 'Legacy limits'", "the old Sat RPT / DD block (#satRiskSec incl. #satHeatHint) and the Legacy limits rows were removed from Settings: TS1 §2 (hidden since RE1-C1 ae5da2b)"),
    ],
    "run_tests_phase122": [
        ("§10 โหมดเดิม (ps1Off)", "dev flag dash.ps1Off (old sizing paths) retired: RE1-C1 33b4a2f 'ps1Off retired', RE-D bb9a831 removed the branch"),
    ],
    "run_tests_phase370": [
        ("settings: switch stays on the right", "account switch moved to the top bar (AW1 89307d3 'AW1 §1-3: account switch in the top bar')"),
    ],
    "run_tests_phase372": [
        ("single merged port chip", "Today status card now shows the Risk room chip (AW1 c1b63c3 §5-6) and the Act risk strip (RE1-C2 d2cfe1e); the merged port chip no longer exists"),
        ("room present once", "Risk room is in the Act risk strip / Risk room chip (RE1-C2 d2cfe1e · AW1 c1b63c3), not in the old status-card chip"),
    ],
}


def skip(module, name):
    for sub, why in RULES.get(module, ()):
        if sub in name:
            print("RETIRED - " + name + "  :: " + why)
            return True
    return False
