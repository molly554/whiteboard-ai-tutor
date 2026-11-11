"""Blind review helper: for the given board ids, find the largest erase and write where to stop so the player
can render the board just before it. Usage: python blind_pre.py B24 B43 ..."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(os.path.dirname(HERE), "results", "review")
render = {i["name"]: i for i in json.load(open(os.path.join(REV, "render_list.json"), encoding="utf-8"))}
out = []
for name in sys.argv[1:]:
    it = render[name]
    obj = json.load(open(os.path.join(os.path.dirname(HERE), "results", "scripts", it["run_id"] + ".json"), encoding="utf-8"))
    best = None
    for si, s in enumerate(obj.get("steps", [])):
        for oi, op in enumerate(s.get("ops", [])):
            if isinstance(op, dict) and op.get("op") == "erase":
                size = 999 if (op.get("all") or op.get("region")) else len(op.get("ids", []))
                if best is None or size > best[0]:
                    best = (size, si, oi)
    if best:
        out.append({"run_id": it["run_id"], "scenario": it["scenario"], "name": name, "step": best[1], "op": best[2]})
        print("%s: largest erase at step %d (removes %s objects)" % (name, best[1] + 1, "all/region" if best[0] == 999 else best[0]))
json.dump(out, open(os.path.join(REV, "pre_list.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False)
