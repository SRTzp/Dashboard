#!/usr/bin/env python3
"""Copy core-size.js into index.html between the BEGIN/END markers (the copy must match byte for byte).

    python3 tools/sync_core_size.py           # write core-size.js into index.html
    python3 tools/sync_core_size.py --check   # exit 1 if the copy differs
    python3 tools/sync_core_size.py --extract # rebuild core-size.js from index.html
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX, SRC = os.path.join(ROOT, 'index.html'), os.path.join(ROOT, 'core-size.js')
B = "/* === core-size.js BEGIN (สำเนา · ห้ามแก้ที่นี่ · แก้ที่ core-size.js แล้วคัดลอกใหม่) === */\n"
E = "/* === core-size.js END === */"


def read(p):
    with open(p, encoding='utf-8', newline='') as f: return f.read()


def write(p, s):
    with open(p, 'w', encoding='utf-8', newline='') as f: f.write(s)


def split(html):
    b = html.find(B); e = html.find(E, b + len(B)) if b >= 0 else -1
    if b < 0 or e < 0 or html.count(B) != 1 or html.count(E) != 1:
        sys.exit('✗ BEGIN/END markers not found exactly once in index.html')
    return html[:b + len(B)], html[b + len(B):e], html[e:]


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    head, copy, tail = split(read(INDEX))
    if arg == '--extract':
        write(SRC, copy); print('✓ wrote core-size.js from index.html'); return
    src = read(SRC)
    if arg == '--check':
        if copy == src: print('✓ index.html copy matches core-size.js'); return
        sys.exit('✗ index.html copy differs from core-size.js — run tools/sync_core_size.py')
    if copy == src: print('✓ already in sync'); return
    write(INDEX, head + src + tail); print('✓ copied core-size.js into index.html')


if __name__ == '__main__':
    main()
