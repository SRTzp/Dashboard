#!/usr/bin/env python3
"""PX1 · ราคาปิดสัปดาห์ + EMA10 (รายสัปดาห์) ของหุ้น Core → Firestore users/{uid}/prices/{ySym} + _meta

อ่านการ์ด users/{uid}/coreCards (status plan/open) → ดึง yfinance รายวัน 2 ปี → แท่งสัปดาห์ (จบศุกร์) → เขียนกลับ
env: FIREBASE_SA (JSON service account ทั้งก้อน) · FIREBASE_UID
ห้ามพิมพ์ค่า secret / ห้ามพิมพ์ JSON กุญแจ ใน log (สคริปต์นี้ไม่พิมพ์ env เลย)
ฟังก์ชันล้วน (ไม่แตะเน็ต · ไม่ต้องมี pandas): to_ysym · weekly_closes · ema10 · check · run
"""
import datetime as dt
import json
import math
import os
import sys

VER = 1
SPAN = 10


def to_ysym(ticker, market=None):
    """TH (market=='TH' หรือลงท้าย .BK) → XXX.BK · US → ตัวใหญ่"""
    t = ''.join(str(ticker or '').split()).upper()
    if not t:
        return ''
    if str(market or '').upper() == 'TH' or t.endswith('.BK'):
        return (t[:-3] if t.endswith('.BK') else t) + '.BK'
    return t


def _rows(daily):
    """รับ list[(date, close)] หรือ pandas Series (index=วันที่) → [(date, float)] เรียงวัน · ตัดค่าว่าง"""
    items = daily.items() if hasattr(daily, 'items') else daily
    out = []
    for d, v in items:
        if isinstance(d, dt.datetime):        # รวม pandas.Timestamp
            d = d.date()
        elif isinstance(d, str):
            d = dt.date.fromisoformat(d[:10])
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        out.append((d, f))
    out.sort(key=lambda x: x[0])
    return out


def _friday_of(d):
    return d + dt.timedelta(days=(4 - d.weekday()) % 7)


def weekly_closes(daily, now_utc):
    """รวมรายวัน → แท่งสัปดาห์จบศุกร์ (เก่า→ใหม่) · ตัดสัปดาห์ที่ยังไม่จบ
    สัปดาห์จบเมื่อ วันนี้(UTC) > ศุกร์ของสัปดาห์นั้น หรือ เป็นวันศุกร์และเลย 22:00 UTC (หลังปิดทั้ง US/TH)
    คืน [{'closeDate':'YYYY-MM-DD' (วันซื้อขายสุดท้ายจริงของสัปดาห์), 'close':float}]"""
    weeks = {}
    for d, c in _rows(daily):
        weeks[_friday_of(d)] = (d, c)          # วันสุดท้ายของสัปดาห์ทับตัวก่อนหน้า
    today = now_utc.date()
    out = []
    for fri in sorted(weeks):
        done = today > fri or (today == fri and now_utc.hour >= 22)
        if done:
            d, c = weeks[fri]
            out.append({'closeDate': d.isoformat(), 'close': c})
    return out


def ema10(closes):
    """EMA span=10 แบบ ewm(adjust=False) (ตรง TradingView) · ข้อมูล < 10 ค่า → None"""
    xs = [float(x) for x in closes]
    if len(xs) < SPAN:
        return None
    a = 2.0 / (SPAN + 1)
    e = xs[0]
    for x in xs[1:]:
        e = a * x + (1 - a) * e
    return e


def check(close, prev=None):
    """(ok, suspect) · close ≤ 0 / NaN → ไม่ผ่าน · เปลี่ยนจากสัปดาห์ก่อน > 40% → suspect"""
    try:
        c = float(close)
    except (TypeError, ValueError):
        return False, False
    if math.isnan(c) or c <= 0:
        return False, False
    suspect = False
    if prev is not None:
        try:
            p = float(prev)
            if p > 0 and abs(c / p - 1) > 0.40:
                suspect = True
        except (TypeError, ValueError):
            pass
    return True, suspect


def pick_tickers(cards):
    """การ์ด plan/open → {ySym: ticker} ตัดซ้ำ (หลายบัญชี = 1 ตัว)"""
    seen = {}
    for c in cards:
        if str(c.get('status')) not in ('plan', 'open'):
            continue
        y = to_ysym(c.get('ticker'), c.get('market'))
        if y and y not in seen:
            seen[y] = str(c.get('ticker') or '').strip().upper()
    return seen


def run(cards, fetch, write, now):
    """fetch(ySym)->daily (list/Series) หรือ raise · write(docId, dict) · now = datetime UTC
    คืน exit code: 1 ถ้าล้มทุกตัว (มีอย่างน้อย 1 ตัวให้ดึง) ไม่งั้น 0"""
    syms = pick_tickers(cards)
    ok, failed = [], []
    for y, tk in syms.items():
        try:
            wk = weekly_closes(fetch(y), now)
            if not wk:
                raise ValueError('no completed week')
            last = wk[-1]
            prev = wk[-2]['close'] if len(wk) > 1 else None
            good, suspect = check(last['close'], prev)
            if not good:
                raise ValueError('bad close')
            e = ema10([w['close'] for w in wk])
            write(y, {'sym': tk, 'ySym': y, 'close': round(last['close'], 4), 'closeDate': last['closeDate'],
                      'ema10w': None if e is None else round(e, 4), 'weeks': len(wk), 'suspect': suspect, 'src': 'yfinance'})
            ok.append(y)
        except Exception as ex:           # ตัวที่ดึงไม่ได้ → ไม่เขียนทับ doc เดิม · ทำตัวอื่นต่อ
            failed.append({'ySym': y, 'why': str(ex)[:120]})
    write('_meta', {'runAt': now.isoformat(), 'ok': ok, 'failed': failed, 'n': len(syms), 'ver': VER})
    print(f'prices: ok {len(ok)}/{len(syms)}' + (' · failed ' + ','.join(f['ySym'] for f in failed) if failed else ''))
    return 1 if (syms and not ok) else 0


def _yf_fetch(ysym):
    import yfinance as yf
    df = yf.download(ysym, interval='1d', period='2y', auto_adjust=False, progress=False)
    if df is None or len(df) == 0:
        raise ValueError('no data')
    s = df['Close']
    if hasattr(s, 'columns'):           # yfinance รุ่นใหม่คืน DataFrame หลายระดับ
        s = s.iloc[:, 0]
    return s.dropna()


def main():
    import firebase_admin
    from firebase_admin import credentials, firestore
    uid = os.environ.get('FIREBASE_UID', '').strip()
    sa = os.environ.get('FIREBASE_SA', '').strip()
    if not uid or not sa:
        print('ไม่พบ FIREBASE_UID / FIREBASE_SA (ตรวจ Secrets)')
        return 1
    firebase_admin.initialize_app(credentials.Certificate(json.loads(sa)))
    db = firestore.client()
    base = db.collection('users').document(uid)
    cards = [d.to_dict() or {} for d in base.collection('coreCards').stream()]

    def write(doc_id, data):
        data = dict(data)
        if doc_id == '_meta':
            data['runAt'] = firestore.SERVER_TIMESTAMP
        else:
            data['at'] = firestore.SERVER_TIMESTAMP
        base.collection('prices').document(doc_id).set(data)

    return run(cards, _yf_fetch, write, dt.datetime.now(dt.timezone.utc))


if __name__ == '__main__':
    sys.exit(main())
