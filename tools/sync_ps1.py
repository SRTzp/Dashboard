#!/usr/bin/env python3
"""Copy ps1-size.js into index.html between the PS1 BEGIN/END markers (byte for byte).
    python3 tools/sync_ps1.py           # write
    python3 tools/sync_ps1.py --check   # exit 1 if different
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX, SRC = os.path.join(ROOT, 'index.html'), os.path.join(ROOT, 'ps1-size.js')
B = "/* === ps1-size.js BEGIN (copy · do not edit here · edit ps1-size.js and run tools/sync_ps1.py) === */\n"
E = "/* === ps1-size.js END === */"
html = open(INDEX, encoding='utf-8', newline='').read(); src = open(SRC, encoding='utf-8', newline='').read()
b = html.find(B); e = html.find(E, b + len(B)) if b >= 0 else -1
if b < 0 or e < 0: sys.exit('markers not found in index.html')
cur = html[b + len(B):e]
if '--check' in sys.argv: sys.exit(0 if cur == src else 1)
open(INDEX, 'w', encoding='utf-8', newline='').write(html[:b + len(B)] + src + html[e:]); print('synced')
