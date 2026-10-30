#!/usr/bin/env python3
"""CL2-a §5.1 — สร้าง tests/seed.json ใหม่จาก tests/seed.pre-CL2a.json
ทำเหมือน cl2aStripLegacy() ใน index.html ทุกข้อ (ฟังก์ชันบริสุทธิ์ · ไม่แก้ของเดิม) แล้วใส่ธง cl2aResetAt/cl2aSatCleanAt ที่ root ของเอกสาร
phase19 ตรวจว่าผลของสคริปต์นี้ = ผลของ cl2aStripLegacy() ตัวจริงในแอป (กันสองสูตรเพี้ยนกัน)
ใช้: python3 tools/cl2a_seed.py   (อ่าน tests/seed.pre-CL2a.json → เขียน tests/seed.json · ไม่ทับ seed.pre-CL2a.json)"""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.join(HERE, "..", "tests")
DROP_KEYS = ["weeklyPlan", "sbPlan", "sbProducts", "ideas", "checklistDrafts", "failLog", "watchlist",
             "tabsOffsetV2", "satBNoteV1", "phase7mV1"]
DROP_PATHS = [["settings", "capital", "satA"], ["settings", "capital", "satA_archived"], ["settings", "posSize", "satA"],
              ["settings", "limits", "port", "satA"], ["settings", "sizing", "r", "satA"], ["settings", "sizing", "cap", "satA"],
              ["settings", "satBVol"], ["settings", "satBVolV2"], ["settings", "satBLowRisk"], ["settings", "szCapSatA25"],
              ["watchSortMode", "satA"]]


def del_path(o, path):
    if not isinstance(o, dict) or path[0] not in o:
        return
    if len(path) == 1:
        del o[path[0]]
    else:
        del_path(o[path[0]], path[1:])


def strip_legacy(book):
    if not isinstance(book, dict):
        return {}
    out = copy.deepcopy(book)
    for k in DROP_KEYS:
        out.pop(k, None)
    if isinstance(out.get("trades"), list):
        out["trades"] = [t for t in out["trades"] if isinstance(t, dict) and t.get("port") in ("core", "satB")]
    for p in DROP_PATHS:
        del_path(out, p)
    return out


def reset_book(book):
    s = strip_legacy(book)
    if not s:
        return {}
    s["trades"] = []
    return s


def build_seed(doc, now="2026-09-30T00:00:00.000Z"):
    out = copy.deepcopy(doc)
    out["books"] = {k: strip_legacy(v) for k, v in (doc.get("books") or {}).items()}
    out["cl2aResetAt"] = now
    out["cl2aSatCleanAt"] = now
    return out


if __name__ == "__main__":
    src = os.path.join(TESTS, "seed.pre-CL2a.json")
    dst = os.path.join(TESTS, "seed.json")
    doc = json.load(open(src, encoding="utf-8"))
    json.dump(build_seed(doc), open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("wrote", dst)
