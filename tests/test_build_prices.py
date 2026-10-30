#!/usr/bin/env python3
"""PX1 — ทดสอบ P2-prices-upload/scripts/build_prices.py (ไม่ใช้เน็ต · ไม่ต้องมี pandas) · รัน: python3 tests/test_build_prices.py"""
import contextlib, datetime as dt, io, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "P2-prices-upload", "scripts"))
import build_prices as B

res = []
def check(name, ok, detail=""):
    res.append(bool(ok)); print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + str(detail)[:300]) if (detail and not ok) else ""))

D = dt.date; U = lambda y, m, d, h=0: dt.datetime(y, m, d, h, 0, tzinfo=dt.timezone.utc)

# 1 to_ysym
check("1 to_ysym ('PTT','TH') → PTT.BK", B.to_ysym("PTT", "TH") == "PTT.BK")
check("1 to_ysym ('PTT.BK',None) → PTT.BK", B.to_ysym("PTT.BK", None) == "PTT.BK")
check("1 to_ysym ('avgo','US') → AVGO", B.to_ysym("avgo", "US") == "AVGO")
check("1 to_ysym ('ptt.bk','TH') ไม่ซ้ำ .BK", B.to_ysym("ptt.bk", "TH") == "PTT.BK")

# 2 weekly_closes — 2026-09-28 (จ) … 2026-10-02 (ศ) · 2026-10-05 (จ) … 2026-10-07 (พ)
def days(start, n, base=100.0, skip=()):
    out, d, v = [], start, base
    while len(out) < n:
        if d.weekday() < 5 and d not in skip:
            out.append((d, v)); v += 1
        d += dt.timedelta(days=1)
    return out
dd = days(D(2026, 9, 21), 13)           # จ 21/9 → พ 7/10
wk = B.weekly_closes(dd, U(2026, 10, 7, 9))
check("2 ข้อมูลถึงพุธ (วันนี้พุธ) → สัปดาห์ล่าสุดที่ได้ = ศุกร์ก่อน (2026-10-02)", wk and wk[-1]["closeDate"] == "2026-10-02" and len(wk) == 2, wk)
wk = B.weekly_closes(dd, U(2026, 10, 3, 23))
check("2 รันเสาร์ 06:30 ไทย (ศุกร์ 23:30 UTC) ข้อมูลถึงศุกร์ → รวมศุกร์ล่าสุด", wk[-1]["closeDate"] == "2026-10-02", wk)
dd2 = [x for x in days(D(2026, 9, 21), 13)[:10]]   # ถึงศุกร์ 2 ต.ค.
wk = B.weekly_closes(dd2, U(2026, 10, 2, 12))
check("2 วันศุกร์ก่อนปิด (12:00 UTC) → ยังตัดสัปดาห์นั้น", wk[-1]["closeDate"] == "2026-09-25", wk)
dd3 = [x for x in dd2 if x[0] != D(2026, 10, 2)]   # ศุกร์หยุด
wk = B.weekly_closes(dd3, U(2026, 10, 3, 23))
check("2 ศุกร์หยุด → closeDate = พฤหัส (2026-10-01)", wk[-1]["closeDate"] == "2026-10-01", wk)
check("2 close = ราคาวันสุดท้ายของสัปดาห์", wk[-1]["close"] == dict(dd3)[D(2026, 10, 1)])
check("2 รับ 'YYYY-MM-DD' เป็น string ได้", B.weekly_closes([("2026-09-25", 5), ("2026-10-02", 6)], U(2026, 10, 3, 23))[-1]["close"] == 6)

# 3 ema10 เทียบมือ 12 สัปดาห์
xs = [100, 102, 101, 105, 107, 106, 110, 108, 111, 115, 113, 118]
e, a = float(xs[0]), 2 / 11
hand = []
for x in xs[1:]: e = a * x + (1 - a) * e
check("3 ema10 12 สัปดาห์ ตรงค่ามือ (6 ตำแหน่ง)", round(B.ema10(xs), 6) == round(e, 6), (B.ema10(xs), e))
check("3 ema10 < 10 สัปดาห์ → None", B.ema10(xs[:9]) is None and B.ema10(xs[:10]) is not None)

# 4 check
check("4 close 0 → ไม่ผ่าน", B.check(0, 100) == (False, False))
check("4 close NaN → ไม่ผ่าน", B.check(float("nan"), 100) == (False, False))
check("4 +45% → suspect", B.check(145, 100) == (True, True))
check("4 −41% → suspect · +40% พอดี ไม่ suspect", B.check(59, 100) == (True, True) and B.check(140, 100) == (True, False))
check("4 ปกติ → (True, False)", B.check(105, 100) == (True, False))

# 5 run
NOW = U(2026, 10, 3, 23)
SERIES = {k: [(D(2026, 7, 6) + dt.timedelta(days=7 * i + j), 50 + i + (0 if k != "BBB" else 1)) for i in range(13) for j in range(5)] for k in ("AAA", "BBB", "CCC")}
cards = [{"ticker": "AAA", "market": "US", "status": "open"}, {"ticker": "BBB", "market": "US", "status": "plan"}, {"ticker": "CCC", "market": "US", "status": "open"},
         {"ticker": "OLD", "market": "US", "status": "closed"}, {"ticker": "AAA", "market": "US", "status": "open"}]
calls, writes = [], {}
def fetch(y):
    calls.append(y)
    if y == "BBB": raise RuntimeError("boom")
    return SERIES[y]
def write(i, d): writes[i] = d
rc = B.run(cards, fetch, write, NOW)
check("5 ตัวที่ 2 fetch error → เขียนตัว 1, 3 + _meta.failed มีตัว 2", rc == 0 and "AAA" in writes and "CCC" in writes and [f["ySym"] for f in writes["_meta"]["failed"]] == ["BBB"] and writes["_meta"]["ok"] == ["AAA", "CCC"], json.dumps(list(writes)))
check("5 ไม่เขียน doc ตัวที่ 2", "BBB" not in writes)
check("5 การ์ด closed ไม่ถูกดึง · ticker ซ้ำ 2 บัญชี → fetch ครั้งเดียว", "OLD" not in calls and calls.count("AAA") == 1, calls)
w = writes["AAA"]
check("5 doc: sym/ySym/close/closeDate/ema10w/weeks/suspect/src ครบ", all(k in w for k in ("sym", "ySym", "close", "closeDate", "ema10w", "weeks", "suspect", "src")) and w["src"] == "yfinance" and w["weeks"] == 13 and w["closeDate"] == "2026-10-02" and w["suspect"] is False, w)
check("5 _meta: runAt/ok/failed/n/ver", set(writes["_meta"]) >= {"runAt", "ok", "failed", "n", "ver"} and writes["_meta"]["n"] == 3 and writes["_meta"]["ver"] == 1)
w2 = {}
rc = B.run(cards, lambda y: (_ for _ in ()).throw(RuntimeError("x")), lambda i, d: w2.__setitem__(i, d), NOW)
check("5 ล้มหมด → exit code 1 (ยังเขียน _meta)", rc == 1 and "_meta" in w2 and list(w2) == ["_meta"])
th = {}; B.run([{"ticker": "PTT", "market": "TH", "status": "open"}], lambda y: (th.setdefault("y", y), SERIES["AAA"])[1], lambda i, d: th.setdefault("w", {}).__setitem__(i, d), NOW)
check("5 การ์ด TH 'PTT' → ดึง/เขียนเป็น PTT.BK (sym = PTT)", th["y"] == "PTT.BK" and th["w"]["PTT.BK"]["sym"] == "PTT")

# 6 ไม่พิมพ์ secret
SECRET = "SUPER-SECRET-KEY-123"
os.environ["FIREBASE_SA"] = json.dumps({"private_key": SECRET}); os.environ["FIREBASE_UID"] = "uid-xyz-789"
buf, err = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
    B.run(cards, fetch, write, NOW); B.main.__globals__["os"].environ.get("FIREBASE_SA")
out = buf.getvalue() + err.getvalue()
check("6 stdout/stderr ไม่มีค่า FIREBASE_SA / UID", SECRET not in out and "uid-xyz-789" not in out and "private_key" not in out, out)
src = open(os.path.join(HERE, "..", "P2-prices-upload", "scripts", "build_prices.py"), encoding="utf-8").read()
check("6 โค้ดไม่ print ตัวแปร env / ค่า sa (มีแต่ชื่อ secret ในข้อความเตือน)", not any("print" in ln and ("environ" in ln or "{sa" in ln or ", sa" in ln or "(sa" in ln) for ln in src.splitlines() if not ln.strip().startswith("#")))

n_ok = sum(res); print(f"\n==== SUMMARY (test_build_prices) ====\nPASS: {n_ok}  FAIL: {len(res) - n_ok}  TOTAL: {len(res)}")
sys.exit(0 if n_ok == len(res) else 1)
