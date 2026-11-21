#!/usr/bin/env python3
"""NT1 — shared fixture: the LR5 Watch fixture + 2 AI themes (idea@1) + 1 trade idea (trade@1) + old notes on AVGO / COST + a few My ideas (users/{uid}/ideas_my)."""
import json, copy
import lr5_common as C
from re1d_common import js

TODAY = "2026-11-19"   # fake clock of lr5_common.CLK


def day(n):
    import datetime
    return (datetime.date(2026, 11, 19) + datetime.timedelta(days=n)).isoformat()


def my(i, subj, title, view=None, chart=None, ang=None, plan="", check=None, built=None, review=None, created=None, **x):
    a = {"tech": "", "sent": "", "fund": "", "macro": ""}; a.update(ang or {})
    return dict({"subject": {"type": subj[0], "key": subj[1]}, "title": title, "view": view, "chart": chart, "ang": a, "plan": plan, "checkOn": check, "builtOn": built, "review": review,
                 "created_at": (created or day(-i)) + "T05:00:00.000Z", "updated_at": (created or day(-i)) + "T05:00:00.000Z"}, **x)


def rev(result, text="", d=-1):
    return {"result": result, "text": text, "at": day(d) + "T05:00:00.000Z"}


MY = {
    "m1": my(1, ("market", "US"), "Rally narrowing to AI names", "neutral", "https://www.tradingview.com/x/AbC123/", {"tech": "Breadth falling while SPX makes highs", "sent": "AAII bulls 52%"}, "Leaders only, half size", check=day(1), built="en-idea-1"),
    "m2": my(2, ("stock", "AAPL"), "Earnings gap held", "bull", "https://example.com/chart", {"tech": "Gap above 182 held 3 days"}),
    "m3": my(3, ("sat", "XAU"), "Range before CPI", "neutral", None, {"macro": "Wait for the break after CPI"}, check=day(-2)),
    "m4": my(4, ("market", "TH"), "SET below 200-day", "bear", None, {"tech": "Foreign selling 6 weeks"}, review=rev("wrong", "Foreign buying came back", -3)),
    "m5": my(5, ("plan", "plan"), "December plan", None, None, {}, "Max 3 Momentum ideas"),
    "m6": my(6, ("market", "US"), "Breadth thrust", "bull", None, {"tech": "Many stocks above 50-day"}, review=rev("right", "Leaders worked", -5)),
    "m7": my(7, ("stock", "AVGO"), "AI networking share", "bull", None, {"fund": "Share keeps growing"}, review=rev("partly", "Only after earnings", -8)),
    "m8": my(8, ("tag", "Oil quirk"), "Odd one", "bear", None, {"macro": "OPEC"}, review=rev("wrong", "", -120)),
}


def trade_doc():
    return {"kind": "trade", "ai": {"schema": "trade@1", "id": "gold-cpi", "title": "Gold breakout after CPI", "date": "2026-11-15", "expires": "2026-12-10", "asset_hint": "XAU", "dir": "long", "tf": "D",
            "horizon": "1–2 weeks", "one_line": "Range 2,620–2,700; a hot CPI miss could break it up", "chain": [{"step": "CPI misses"}, {"step": "Yields fall"}, {"step": "Gold breaks up"}], "strength": "mid",
            "counter": ["Hot CPI instead"], "wrong_if": ["Closes below 2,620"], "alts": [], "products": [{"name": "XAUUSD", "type": "cfd", "lev": "high"}], "entry": "Break above 2,700"},
            "me": {}, "user": {"status": "watch"}, "idea_log": []}


def seed_nt1(page, my_docs=True, notes=True):
    # trade idea
    page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas').doc(i).set(d)", ["gold-cpi", trade_doc()])
    if notes:
        js(page, "()=>{ const col = wlCol(); col.doc('AVGO').update({my_notes:{cat:[{id:'nlzzzzzz1', text:'Q1 renewal rate', date:'2026-12-12'}], blk:[{id:'nlzzzzzz2', text:'Customer concentration'}]}}); }")
    if my_docs:
        for k, d in MY.items():
            page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas_my').doc(i).set(d)", [k, d])
    page.wait_for_timeout(600)


def open_nt1(pw, w, h, my_docs=True, notes=True):
    b, page, pe = C.open_watch(pw, w, h, ideas=True)
    seed_nt1(page, my_docs, notes)
    return b, page, pe


def goto_watch(page):
    js(page, "()=>{ switchTab('journal'); switchTab('watch'); }"); page.wait_for_timeout(300)
