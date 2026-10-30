#!/usr/bin/env python3
"""node --check ผ่านไฟล์ index.html — ดึง <script> ทุกก้อนที่เป็นโค้ดของแอป (ไม่ใช่ type=module/src ภายนอก)
มาต่อกันแล้วเช็ค syntax ด้วย Node จริง ตามที่ทำมาในรอบก่อนหน้า (7D/7D.2/7D.3)
ถ้าเครื่องไม่มี node (เช่น Mac เครื่องนี้) → fallback ใช้ Chromium ของ Playwright คอมไพล์ด้วย new Function() แทน (จับ syntax error ได้เหมือนกัน · ไม่รันโค้ด)
ใช้: python3 tests/check_syntax.py [ทาง index.html]  (ค่าเริ่มต้น = ../index.html เทียบกับโฟลเดอร์นี้)
"""
import os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
index_path = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(HERE, "..", "index.html"))

html = open(index_path, encoding="utf-8").read()
scripts = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', html, re.S)
if not scripts:
    print("ไม่พบ inline <script> เลย — ตรวจ path ให้ถูก:", index_path)
    sys.exit(2)
code = "\n;\n".join(scripts)

if shutil.which("node"):
    out_path = os.path.join(HERE, "_extracted.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(code)
    r = subprocess.run(["node", "--check", out_path], capture_output=True, text=True)
    os.remove(out_path)
    ok, err = r.returncode == 0, r.stderr
else:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        err = pg.evaluate("(src)=>{ try{ new Function(src); return ''; }catch(e){ return String(e); } }", code)
        b.close()
    ok = not err

if ok:
    print("SYNTAX_OK —", index_path)
    sys.exit(0)
print("SYNTAX_FAIL —", index_path)
print(err)
sys.exit(1)
