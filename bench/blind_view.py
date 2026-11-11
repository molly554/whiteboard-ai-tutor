"""Blind review helper: lists boards by random id and prints their narration. Never prints model names, thinking conditions or run ids.
Usage: python blind_view.py             list the board ids per scenario
       python blind_view.py <scenario>  print the step-by-step narration of every board in that scenario"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(os.path.dirname(HERE), "results", "review")
render = json.load(open(os.path.join(REV, "render_list.json"), encoding="utf-8"))
by = collections.defaultdict(list)
for it in render:
    by[it["scenario"]].append(it)

if len(sys.argv) < 2:
    for sc in sorted(by):
        print("%-26s %s" % (sc, " ".join(sorted(i["name"] for i in by[sc]))))
    sys.exit(0)

sc = sys.argv[1]
for it in sorted(by[sc], key=lambda i: i["name"]):
    obj = json.load(open(os.path.join(os.path.dirname(HERE), "results", "scripts", it["run_id"] + ".json"), encoding="utf-8"))
    steps = obj.get("steps", [])
    n_ops = sum(len(s.get("ops", [])) for s in steps)
    erases = []
    for s in steps:
        for op in s.get("ops", []):
            if isinstance(op, dict) and op.get("op") == "erase":
                erases.append("all" if op.get("all") else ("region" if op.get("region") else ",".join(op.get("ids", []))))
    print("== %s  steps=%d ops=%d erase=%s" % (it["name"], len(steps), n_ops, erases if erases else "none"))
    for i, s in enumerate(steps, 1):
        say = (s.get("say") or "").replace("\n", " ")
        print("   %d. [%s] %s" % (i, (s.get("title") or "")[:40], say[:230]))
