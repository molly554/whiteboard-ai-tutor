"""Runner for the widget experiment (protocol v1.1 draft). Results go to results/widgets/, apart from the v1 results.
  run_widgets.py preflight --via openrouter          free: keys, model IDs, pinned providers
  run_widgets.py smoke  --via openrouter             1 lesson + 1 interruption per model (a few cents)
  run_widgets.py main --confirm --via openrouter     6 scenarios x reps per model, low thinking
Options: --models a,b  --reps 3  --phase name
Budget: hard total cap and per-model caps below; a call that could exceed a cap is skipped (the v1 runner works the same way).
"""
import argparse
import json
import os
import random
import sys
import time

import config
import providers
import run as v1
import widget_check
import widget_scenarios
from common import Budget, cost_of, parse_output, worst_case

OUT = os.path.join(v1.ROOT, "results", "widgets")
COND = "low"
TOTAL_CAP = 0.60
SMOKE_CAP = 0.15
CAPS = {"haiku-5.5": 0.10, "gemini-3.8-flash": 0.20, "sonnet-5.5": 0.40}
DEFAULT_MODELS = ["haiku-5.5", "gemini-3.8-flash", "sonnet-5.5"]
SCENARIOS = ["w-l1", "w-l2", "w-l3", "w-l4", "w-i1", "w-i2"]
SMOKE = ["w-l1", "w-i1"]


def run_tasks(tasks, phase, models, total_cap, via):
    os.makedirs(os.path.join(OUT, "scripts"), exist_ok=True)
    scen = widget_scenarios.load_scenarios()
    system = widget_scenarios.system_prompt()
    keys = v1.keys_for(models, via)
    caps = {m: CAPS.get(m, 0.05) for m in config.MODELS}
    budget = Budget(os.path.join(OUT, "spend-%s.json" % phase), total_cap, caps)
    out = open(os.path.join(OUT, "%s.jsonl" % phase), "a", encoding="utf-8", newline="\n")
    for n, (m, sid, rep) in enumerate(tasks, 1):
        cfg = config.MODELS[m]
        mvia = v1.route(m, via)
        ok, why = budget.can_run(m, worst_case(cfg, config.MAX_TOKENS, est_input=4500))
        if not ok:
            if why.startswith("total"):
                print("STOP: %s" % why)
                break
            print("SKIP %s %s: %s" % (m, sid, why))
            continue
        key = keys["openrouter"] if mvia else keys[cfg["vendor"]]
        res = None
        for attempt in range(3):
            res = providers.call(cfg, COND, system, scen[sid]["messages"], key, via=mvia, model_name=m)
            if res["http"] in (429, 500, 502, 503, 529) or (res["error"] and res["http"] is None):
                time.sleep(5 * (attempt + 1))
                continue
            break
        calc, peak = cost_of(cfg, res["usage"], res["request_ts"])
        reported = res["usage"].get("cost")
        cost = reported if (mvia and reported is not None) else calc
        budget.add(m, cost)
        obj, perr = parse_output(res["text"])
        chk = widget_check.check(obj, sid) if obj else None
        run_id = "%s-%s-%s-%d" % (phase, m, sid, rep)
        if obj:
            json.dump(obj, open(os.path.join(OUT, "scripts", run_id + ".json"), "w", encoding="utf-8", newline="\n"),
                      ensure_ascii=False, indent=1)
        rec = {"run_id": run_id, "via": mvia or "direct", "model": m, "cond": COND, "scenario": sid, "kind": scen[sid]["kind"],
               "rep": rep, "ts": res["request_ts"], "http": res["http"], "error": res["error"], "finish": res["finish"],
               "t": res["t"], "usage": res["usage"], "cost": cost, "parse_ok": obj is not None, "parse_error": perr,
               "check": chk, "text": res["text"]}
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out.flush()
        c = chk or {}
        print("[%d/%d] %-16s %-6s | http=%s parse=%s schema_err=%d widget_ops=%d v1_ops=%d expect %d/%d wrong=%d | topic=%s state=%s | first_op=%s end=%s | in=%s out=%s think=%s | $%.4f%s" % (
            n, len(tasks), m, sid, res["http"], "ok" if obj else "FAIL", len(c.get("schema_errors", [])), c.get("widget_ops", 0),
            c.get("v1_ops", 0), c.get("expect_ok", 0), c.get("expect_given", 0), len(c.get("expect_wrong", [])),
            c.get("topic_ok"), c.get("state_ok"), res["t"].get("first_op"), res["t"].get("end"),
            res["usage"]["input"], res["usage"]["output"], res["usage"]["thinking"], cost,
            (" | ERROR " + res["error"][:200].replace("\n", " ")) if res["error"] else ""), flush=True)
    out.close()
    print("\nspent per model: %s" % json.dumps(budget.spent))
    print("spent total: $%.4f (cap $%.2f)" % (budget.total, total_cap))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["preflight", "smoke", "main"])
    ap.add_argument("--models")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--via", choices=["openrouter"])
    ap.add_argument("--phase")
    ap.add_argument("--skip", help="phase whose finished calls (http 200) are reused instead of repeated")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    names = a.models.split(",") if a.models else DEFAULT_MODELS
    for n in names:
        if n not in config.MODELS:
            sys.exit("unknown model: %s" % n)
    if a.cmd == "preflight":
        sys.exit(0 if v1.preflight(names, a.via) else 1)
    rnd = random.Random(20261126)
    if a.cmd == "smoke":
        tasks = [(m, s, 1) for m in names for s in SMOKE]
        rnd.shuffle(tasks)
        run_tasks(tasks, a.phase or "wsmoke", names, SMOKE_CAP, a.via)
    else:
        if not a.confirm:
            sys.exit("main run spends real money; add --confirm")
        tasks = [(m, s, r) for m in names for s in SCENARIOS for r in range(1, a.reps + 1)]
        if a.skip:
            done = set()
            for ln in open(os.path.join(OUT, a.skip + ".jsonl"), encoding="utf-8"):
                if ln.strip():
                    d = json.loads(ln)
                    if d.get("http") == 200:
                        done.add((d["model"], d["scenario"], d["rep"]))
            tasks = [t for t in tasks if t not in done]
            print("reusing %d finished calls from %s; %d left to run" % (len(done), a.skip, len(tasks)))
        rnd.shuffle(tasks)
        run_tasks(tasks, a.phase or "wmain", names, TOTAL_CAP, a.via)


if __name__ == "__main__":
    main()
