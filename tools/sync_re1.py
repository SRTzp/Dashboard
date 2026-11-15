#!/usr/bin/env python3
"""Copy risk-engine.js and re1-adapter.js into index.html between their BEGIN/END markers (byte for byte).
    python3 tools/sync_re1.py           # write
    python3 tools/sync_re1.py --check   # exit 1 if different
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
PAIRS = [('risk-engine.js', '/* === risk-engine.js BEGIN (copy · do not edit here · edit risk-engine.js and run tools/sync_re1.py) === */\n', '/* === risk-engine.js END === */'),
         ('re1-adapter.js', '/* === re1-adapter.js BEGIN (copy · do not edit here · edit re1-adapter.js and run tools/sync_re1.py) === */\n', '/* === re1-adapter.js END === */')]
html = open(INDEX, encoding='utf-8', newline='').read(); bad = False
for fn, B, E in PAIRS:
    src = open(os.path.join(ROOT, fn), encoding='utf-8', newline='').read()
    b = html.find(B); e = html.find(E, b + len(B)) if b >= 0 else -1
    if b < 0 or e < 0: sys.exit('markers not found for ' + fn)
    if '--check' in sys.argv:
        if html[b + len(B):e] != src: bad = True
    else: html = html[:b + len(B)] + src + html[e:]
if '--check' in sys.argv: sys.exit(1 if bad else 0)
open(INDEX, 'w', encoding='utf-8', newline='').write(html); print('synced')
