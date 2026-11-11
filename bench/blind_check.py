"""Blind review helper: show the schema errors and first few raw ops of one board, by random id only.
Usage: python blind_check.py B35 [number of ops to show]"""
import json
import os
import sys

from common import validate_script

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(os.path.dirname(HERE), "results", "review")
render = {i["name"]: i for i in json.load(open(os.path.join(REV, "render_list.json"), encoding="utf-8"))}
it = render[sys.argv[1]]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
obj = json.load(open(os.path.join(os.path.dirname(HERE), "results", "scripts", it["run_id"] + ".json"), encoding="utf-8"))
errs = validate_script(obj)
print("%s: schema errors = %d" % (it["name"], len(errs)))
for e in errs[:6]:
    print("   ", e)
shown = 0
for s in obj.get("steps", []):
    for op in s.get("ops", []):
        if shown < n:
            print("   op:", json.dumps(op, ensure_ascii=False)[:260])
            shown += 1
