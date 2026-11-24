#!/usr/bin/env python3
"""UX3 · US (NYSE) trading calendar — no network, stdlib only.
holidays(year) · is_session(d) · prev_session(d) · last_completed_session(now_utc) · sessions_behind(as_of, now_utc)
A session counts as completed from 16:15 ET (same cut as the app's rrgProvCut). Half-days (13:00 close) are treated like full days.
The JS twin lives in index.html (ux3*) — both are tested against tests/fixtures/us_calendar.json."""
import datetime as dt
from zoneinfo import ZoneInfo

ET = ZoneInfo('America/New_York')
CLOSE_MIN = 16 * 60 + 15


def _nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1)
    d += dt.timedelta(days=(wd - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def _last_weekday(y, m, wd):
    d = dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)


def _easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mo, da = divmod(h + l - 7 * m + 114, 31)
    return dt.date(y, mo, da + 1)


def _observed(d):
    """Saturday → Friday · Sunday → Monday"""
    if d.weekday() == 5:
        return d - dt.timedelta(days=1)
    if d.weekday() == 6:
        return d + dt.timedelta(days=1)
    return d


def holidays(y):
    s = set()
    ny = dt.date(y, 1, 1)
    if ny.weekday() != 5:                       # a Saturday 1 Jan is NOT moved to the Friday before (that is 31 Dec of the year before)
        s.add(_observed(ny))
    s.add(_nth_weekday(y, 1, 0, 3))             # MLK
    s.add(_nth_weekday(y, 2, 0, 3))             # Presidents
    s.add(_easter(y) - dt.timedelta(days=2))    # Good Friday
    s.add(_last_weekday(y, 5, 0))               # Memorial
    if y >= 2022:
        s.add(_observed(dt.date(y, 6, 19)))     # Juneteenth
    s.add(_observed(dt.date(y, 7, 4)))
    s.add(_nth_weekday(y, 9, 0, 1))             # Labor
    s.add(_nth_weekday(y, 11, 3, 4))            # Thanksgiving
    s.add(_observed(dt.date(y, 12, 25)))
    if y == 2025:
        s.add(dt.date(2025, 1, 9))              # one-off: national day of mourning
    return s


def is_session(d):
    return d.weekday() < 5 and d not in holidays(d.year)


def prev_session(d):
    d -= dt.timedelta(days=1)
    while not is_session(d):
        d -= dt.timedelta(days=1)
    return d


def last_completed_session(now_utc):
    et = now_utc.astimezone(ET)
    d = et.date()
    if is_session(d) and et.hour * 60 + et.minute >= CLOSE_MIN:
        return d
    return prev_session(d)


def sessions_behind(as_of, now_utc):
    """how many completed sessions are newer than as_of ('YYYY-MM-DD' or date) · 0 = up to date · None = unreadable"""
    try:
        a = dt.date.fromisoformat(str(as_of)[:10])
    except ValueError:
        return None
    last = last_completed_session(now_utc)
    n, d = 0, last
    while d > a:
        n += 1
        d = prev_session(d)
        if n > 400:
            break
    return n
