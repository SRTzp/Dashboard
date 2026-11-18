#!/usr/bin/env python3
"""LR1 A0 — hook inventory of index.html.
Lists every id, every data-* attribute name (with literal static values), every name= attribute,
and every inline handler (on*=) with the function names it calls.
  python3 tools/hook_inventory.py [index.html]            print JSON
  python3 tools/hook_inventory.py --out tests/hooks_baseline.json [index.html]
Markup is taken from static HTML plus HTML inside JS template/string literals (the app renders via innerHTML),
so we scan the raw source text; values containing ${...} / quotes-concatenation are recorded as dynamic (not as literals).
"""
import re, sys, json, os

ATTR = re.compile(r'''(?<![\w-])(id|name|data-[\w-]+|on[a-z]+)\s*=\s*(?:"([^"]*)"|'([^']*)')''')
# escaped quotes inside JS strings: id=\"x\"
ATTR_ESC = re.compile(r'''(?<![\w-])(id|name|data-[\w-]+|on[a-z]+)\s*=\s*\\(?:"|')([^"'\\]*)\\(?:"|')''')
CALL = re.compile(r'([A-Za-z_$][\w$.]*)\s*\(')
KW = {'if','for','while','switch','return','function','event','this','catch','typeof','new','alert','confirm'}

def is_static(v):
    return v is not None and v != '' and not re.search(r'\$\{|\{\{|\+|\\|["\']\s*\+', v)

def inventory(text):
    ids, names, handlers = set(), set(), {}
    data = {}
    for rx in (ATTR, ATTR_ESC):
        for m in rx.finditer(text):
            k = m.group(1)
            v = m.group(2) if m.group(2) is not None else (m.group(3) if rx is ATTR else None)
            if v is None: continue
            if k == 'id':
                if is_static(v): ids.add(v)
            elif k == 'name':
                if is_static(v) and len(v) < 60: names.add(v)
            elif k.startswith('data-'):
                d = data.setdefault(k, set())
                if is_static(v) and len(v) < 60: d.add(v)
            elif k.startswith('on') and len(k) > 3:
                for c in CALL.findall(v):
                    base = c.split('.')[-1]
                    if base not in KW:
                        handlers.setdefault(k, set()).add(base)
    return {
        'ids': sorted(ids),
        'names': sorted(names),
        'data': {k: sorted(v) for k, v in sorted(data.items())},
        'handlers': {k: sorted(v) for k, v in sorted(handlers.items())},
    }

def counts(inv):
    return {'ids': len(inv['ids']), 'names': len(inv['names']), 'data_attrs': len(inv['data']),
            'data_values': sum(len(v) for v in inv['data'].values()),
            'handler_events': len(inv['handlers']), 'handler_functions': sum(len(v) for v in inv['handlers'].values())}

def main():
    a = sys.argv[1:]; out = None
    if a[:1] == ['--out']: out = a[1]; a = a[2:]
    src = a[0] if a else os.path.join(os.path.dirname(__file__), '..', 'index.html')
    inv = inventory(open(src, encoding='utf-8').read())
    inv['counts'] = counts(inv)
    s = json.dumps(inv, indent=1, ensure_ascii=False)
    if out: open(out, 'w', encoding='utf-8').write(s + '\n'); print('wrote', out, inv['counts'])
    else: print(s)
if __name__ == '__main__': main()
