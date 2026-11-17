#!/usr/bin/env python3
"""Copy pos-view.js into index.html between the PV1 BEGIN/END markers (byte for byte).
    python3 tools/sync_pv1.py           # write
    python3 tools/sync_pv1.py --check   # exit 1 if different
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX, SRC = os.path.join(ROOT, 'index.html'), os.path.join(ROOT, 'pos-view.js')
B = "/* === pos-view.js BEGIN (copy · do not edit here · edit pos-view.js and run tools/sync_pv1.py) === */\n"
E = "/* === pos-view.js END === */"
html = open(INDEX, encoding='utf-8', newline='').read(); src = open(SRC, encoding='utf-8', newline='').read()
b = html.find(B); e = html.find(E, b + len(B)) if b >= 0 else -1
if b < 0 or e < 0: sys.exit('markers not found in index.html')
cur = html[b + len(B):e]
if '--check' in sys.argv: sys.exit(0 if cur == src else 1)
open(INDEX, 'w', encoding='utf-8', newline='').write(html[:b + len(B)] + src + html[e:]); print('synced')
