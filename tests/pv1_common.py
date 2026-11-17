"""PV1 shared fixture: the user's real stored NVDA Compounder card (A0) on top of the RE-C1 fixture. Account value 3.5M + 45,000 USD × 33.76 = 5,019,200."""
import json, copy
import re1d_common as K
from re1d_common import js, doc_c, cards, tr, launch, check, results, refresh, seed, no_overflow, rows, txt

NVDA_CARD = json.loads('{"emaW":null,"plan":{"risk":1,"entry":158,"stop":110,"ps1":{"ideaEff":0.75,"date":"2026-11-12","bucket":"ladder","typed":1,"v":1,"rows":[{"px":158,"riskPct":0.5,"qty":11},{"riskPct":0.5,"px":140,"qty":18}],"avgEntry":146.82758620689654,"qty":29,"leftPct":0.03164488364679641,"cashLimited":false,"sizePct":2.864003825310806,"div":33.76,"lot":1,"avgStop":110,"E":5019200,"riskMoney":36055.68,"stops":[{"pct":100,"px":110}],"maxSizePct":12.5,"tag":"75% size: regime","trimmed":false,"Edate":"2026-11-06","mult":{"f":0.75,"dd":1},"riskPct":0.7183551163532036},"ft":{"at":"2026-11-12T13:41:56.936Z","due":"2026-11-15"}},"ticker":"NVDA","trade_id":"h_nvda","market":"US","acct":"main","created_at":"2026-11-12T13:41:56.936Z","stopHistory":[],"status":"open","px":162.85,"track":"ladder","stop":110,"pxDate":"2026-11-13","strategy":"W","ln4":{"placedLv":{"0":"2026-11-13T03:05:39.227Z"}},"lots":[{"layer":"base","qty":11,"stop":110,"f":0.75,"n":1,"risk":1,"px":158,"date":"2026-11-13"}],"updated_at":"2026-11-13T03:05:45.177Z","log":[],"pxSrc":"auto","_pxSuspect":false}')


def doc_pv():
    d = doc_c(equity=5019200)
    m = d["books"]["main"]; st = m["settings"]; st["fx"] = 33.76; st["capital"] = {"core": 3500000, "satB": 45000, "option": 0}
    m["trades"] = [tr(id="h_nvda", sym="NVDA", cur="USD", qty=11, entry=158, sl=110, posGroup="h_nvda", sl0=110, date="2026-11-13", openedAt="2026-11-13")]
    return d


def cards_pv():
    return {"cN": copy.deepcopy(NVDA_CARD)}


def doc_sat(extra_core=True):
    """NVDA fixture + one Satellite holding (BTCUSD long 0.02 lot @60000, stop 59000, mult 1) + one planned XAUUSD."""
    d = doc_pv(); m = d["books"]["main"]
    m["trades"] += [tr(id="h1", sym="BTCUSD", port="satB", cur="USD", status="open", qty=0.02, entry=60000, sl=59000, mult=1, posGroup="h1", sl0=59000, date="2026-11-14")]
    return d


SAT_JS = """()=>{ sat7dWrite('satIdeas','bi',{id:'bi',v3:true,v2:true,asset:'BTCUSD',bias:'Long',entry:60000,sl:59000,tp:63000,status:'active',accts:{main:{trade_id:'h1'}},week:wpWeekKey(),setups:[]});
  sat7dWrite('satIdeas','xp',{id:'xp',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],pb_acct:'main'}); }"""
