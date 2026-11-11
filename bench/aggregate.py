"""Aggregate the main matrix per model x condition: parse rate, linter hard-error rate, latency, tokens, cost.
Usage: python aggregate.py [--blind]     (--blind also draws the blind-review sample and writes the id mapping)"""
import collections
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "results")
PHASES = ["main-or", "main-ds"]
LESSONS = ["r1-seasons", "r1-pythagoras", "r1-quadratic", "r1-supply-demand", "r1-photosynthesis"]
INTERRUPTS = ["r1-i1-seasons-distance", "r1-i2-demand-simpler", "r1-i3-arrow-meaning"]
MID_SCENARIOS = ["r1-seasons", "r1-supply-demand", "r1-i2-demand-simpler"]
ORDER = ["haiku-5.5", "sonnet-5.5", "gemini-4-argon", "gemini-3.8-flash", "deepseek-flash", "deepseek-v4-pro"]


def load():
    rows, lint = [], {}
    for ph in PHASES:
        p = os.path.join(RES, "runs", ph + ".jsonl")
        if os.path.exists(p):
            rows += [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
        lp = os.path.join(RES, "lint", "lint-%s.json" % ph)
        if os.path.exists(lp):
            for r in json.load(open(lp, encoding="utf-8")):
                lint[r["run_id"]] = r
    return rows, lint


def pct(vals, q):
    vals = sorted(vals)
    if not vals:
        return None
    k = (len(vals) - 1) * q
    f, c = int(k), min(int(k) + 1, len(vals) - 1)
    return vals[f] + (vals[c] - vals[f]) * (k - f)


def fmt(x, nd=1):
    return "-" if x is None else ("%.*f" % (nd, x))


def main():
    rows, lint = load()
    for r in rows:
        r["parsed"] = r["http"] == 200 and r["parse_ok"]
        lr = lint.get(r["run_id"])
        r["hard_n"] = len(lr.get("hard", [])) if (lr and r["parsed"]) else None
        r["ops_n"] = lr.get("ops") if lr else None
    groups = collections.defaultdict(list)
    for r in rows:
        groups[(r["model"], r["cond"])].append(r)

    out_rows = []
    for m in ORDER:
        for c in ("low", "mid"):
            L = groups.get((m, c), [])
            if not L:
                continue
            parsed = [r for r in L if r["parsed"]]
            clean = [r for r in parsed if r["hard_n"] == 0]
            fo = [r["t"]["first_op"] for r in L if r["http"] == 200 and r["t"].get("first_op") is not None]
            en = [r["t"]["end"] for r in L if r["http"] == 200]
            out = [r["usage"]["output"] for r in L if r["usage"].get("output")]
            th = [(r["usage"].get("thinking") or 0) for r in L if r["http"] == 200]
            costs = [r["cost"] for r in L]
            ops = [r["ops_n"] for r in parsed if r["ops_n"] is not None]
            les = [r for r in L if r["kind"] == "lesson"]
            itr = [r for r in L if r["kind"] == "interrupt"]

            def clean_rate(S):
                return (sum(1 for r in S if r["parsed"] and r["hard_n"] == 0) / len(S)) if S else None

            out_rows.append(dict(
                model=m, cond=c, n=len(L), parse_rate=len(parsed) / len(L),
                clean_rate=len(clean) / len(L), clean_lesson=clean_rate(les), clean_interrupt=clean_rate(itr),
                first_op_p50=pct(fo, .5), first_op_p90=pct(fo, .9), end_p50=pct(en, .5), end_p90=pct(en, .9),
                out_mean=statistics.mean(out) if out else None, think_mean=statistics.mean(th) if th else None,
                cost_mean=statistics.mean(costs), cost_total=sum(costs), ops_mean=statistics.mean(ops) if ops else None,
                lint_missing=sum(1 for r in parsed if r["hard_n"] is None)))
    json.dump(out_rows, open(os.path.join(RES, "summary.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

    lines = ["| model | thinking | calls | parsed | linter-clean | lessons linter-clean | interruptions linter-clean | first stroke p50 / p90 (s) | total p50 (s) | output tokens | thinking tokens | cost per call | subtotal |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in out_rows:
        pr = lambda x: "-" if x is None else "%d%%" % round(100 * x)
        lines.append("| %s | %s | %d | %s | %s | %s | %s | %s / %s | %s | %s | %s | $%.4f | $%.2f |" % (
            s["model"], s["cond"], s["n"], pr(s["parse_rate"]), pr(s["clean_rate"]), pr(s["clean_lesson"]),
            pr(s["clean_interrupt"]), fmt(s["first_op_p50"]), fmt(s["first_op_p90"]), fmt(s["end_p50"]),
            fmt(s["out_mean"], 0), fmt(s["think_mean"], 0), s["cost_mean"], s["cost_total"]))
    open(os.path.join(RES, "summary.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("\nlint missing for parsed runs:", sum(s["lint_missing"] for s in out_rows))
    print("total runs: %d, total cost: $%.3f" % (len(rows), sum(r["cost"] for r in rows)))

    fails = collections.Counter()
    for r in rows:
        if not r["parsed"]:
            why = "http %s" % r["http"] if r["http"] != 200 else ("parse: " + (r["parse_error"] or "")[:40])
            fails[(r["model"], r["cond"], why[:48])] += 1
    print("\nfailures:")
    for k, v in sorted(fails.items()):
        print("  x%d %s" % (v, k))

    if "--blind" in sys.argv:
        blind(rows, lint)


def blind(rows, lint):
    rnd = random.Random(20261112)
    by = collections.defaultdict(list)
    for r in rows:
        if r["parsed"] and r["hard_n"] is not None:
            by[(r["model"], r["cond"], r["scenario"])].append(r)
    picks, missing = [], []
    for m in ORDER:
        for sc in LESSONS + INTERRUPTS:
            L = sorted(by.get((m, "low", sc), []), key=lambda r: (r["hard_n"], r["rep"]))
            (picks if L else missing).append((m, "low", sc, L[len(L) // 2] if L else None))
        for sc in MID_SCENARIOS:
            L = sorted(by.get((m, "mid", sc), []), key=lambda r: (r["hard_n"], r["rep"]))
            (picks if L else missing).append((m, "mid", sc, L[len(L) // 2] if L else None))
    ids = ["B%02d" % i for i in range(1, len(picks) + 1)]
    rnd.shuffle(ids)
    mapping, render = {}, []
    for bid, (m, c, sc, r) in zip(ids, picks):
        mapping[bid] = {"model": m, "cond": c, "scenario": sc, "run_id": r["run_id"], "hard_n": r["hard_n"],
                        "cost": r["cost"], "first_op": r["t"].get("first_op")}
        render.append({"run_id": r["run_id"], "scenario": sc, "name": bid})
    render.sort(key=lambda x: x["name"])
    os.makedirs(os.path.join(RES, "review"), exist_ok=True)
    json.dump(render, open(os.path.join(RES, "review", "render_list.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False)
    json.dump(mapping, open(os.path.join(RES, "review", "mapping.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    json.dump([{"model": m, "cond": c, "scenario": sc} for (m, c, sc, _) in missing],
              open(os.path.join(RES, "review", "no_output.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print("\nblind boards: %d  (no usable output for %d model x scenario cells)" % (len(render), len(missing)))


if __name__ == "__main__":
    main()
