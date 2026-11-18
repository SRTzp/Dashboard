#!/usr/bin/env python3
"""LR1 A0 — the branch's hook inventory must be a SUPERSET of tests/hooks_baseline.json (additions allowed)."""
import json, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from hook_inventory import inventory, counts
base = json.load(open(os.path.join(ROOT, 'tests', 'hooks_baseline.json'), encoding='utf-8'))
cur = inventory(open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read())
fails = 0
def chk(label, missing):
    global fails
    if missing: fails += 1; print('FAIL', label, 'missing', len(missing), sorted(missing)[:30])
    else: print('PASS', label)
chk('ids', set(base['ids']) - set(cur['ids']))
chk('names', set(base['names']) - set(cur['names']))
chk('data-* attribute names', set(base['data']) - set(cur['data']))
chk('data-* literal values', {f'{k}={v}' for k, vs in base['data'].items() for v in vs if v not in cur['data'].get(k, [])})
chk('inline handler events', set(base['handlers']) - set(cur['handlers']))
chk('inline handler functions', {f'{k}:{f}' for k, fs in base['handlers'].items() for f in fs if f not in cur['handlers'].get(k, [])})
print('baseline', base.get('counts')); print('branch  ', counts(cur))
print(f'SUMMARY hooks superset: {"FAIL" if fails else "PASS"} ({fails} failing)')
sys.exit(1 if fails else 0)
