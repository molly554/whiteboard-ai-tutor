"""Extra stats for the main matrix: latency, tokens and cost split by lesson vs interruption; protocol violations and truncations."""
import collections
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "results")
ORDER = ["sonnet-5.5", "haiku-5.5", "gemini-4-argon", "gemini-3.8-flash", "deepseek-v4-pro", "deepseek-flash"]
rows = []
for ph in ("main-or", "main-ds"):
    rows += [json.loads(l) for l in open(os.path.join(RES, "runs", ph + ".jsonl"), encoding="utf-8") if l.strip()]


def pct(v, q):
    v = sorted(v)
    if not v:
        return float("nan")
    k = (len(v) - 1) * q
    f, c = int(k), min(int(k) + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


print("model | cond | kind | n | parsed | truncated | first_op p50 | p90 | end p50 | out tok | think tok | cost mean")
for m in ORDER:
    for c in ("low", "mid"):
        for kind in ("lesson", "interrupt"):
            L = [r for r in rows if r["model"] == m and r["cond"] == c and r["kind"] == kind]
            ok = [r for r in L if r["parse_ok"]]
            fo = [r["t"]["first_op"] for r in L if r["t"].get("first_op") is not None]
            print("%-16s %-3s %-9s %2d %2d %2d  %6.1f %6.1f %6.1f  %5.0f %5.0f  $%.4f" % (
                m, c, kind, len(L), len(ok), sum(1 for r in L if r["finish"] == "length"),
                pct(fo, .5), pct(fo, .9), pct([r["t"]["end"] for r in L], .5),
                statistics.mean(r["usage"]["output"] or 0 for r in L),
                statistics.mean((r["usage"].get("thinking") or 0) for r in L),
                statistics.mean(r["cost"] for r in L)))
print()
print("protocol violations (parsed runs): model cond | runs with any invalid instruction | runs where every instruction is invalid (blank board)")
for m in ORDER:
    for c in ("low", "mid"):
        L = [r for r in rows if r["model"] == m and r["cond"] == c and r["parse_ok"]]
        anyb = sum(1 for r in L if r["schema_errors"])
        allb = 0
        for r in L:
            obj = json.load(open(os.path.join(RES, "scripts", r["run_id"] + ".json"), encoding="utf-8"))
            n_ops = sum(len(s.get("ops", [])) for s in obj.get("steps", []) if isinstance(s, dict))
            if n_ops and len(r["schema_errors"]) >= n_ops:
                allb += 1
        print("%-16s %-3s  %2d / %2d   blank: %d" % (m, c, anyb, len(L), allb))
tot = collections.Counter()
for r in rows:
    tot[r["model"]] += r["cost"]
print("\ncost per model:", {k: round(v, 3) for k, v in tot.items()}, " total: %.3f" % sum(tot.values()))
smoke = 0.0
for ph in ("smoke", "smoke-ds"):
    p = os.path.join(RES, "runs", ph + ".jsonl")
    if os.path.exists(p):
        smoke += sum(json.loads(l)["cost"] for l in open(p, encoding="utf-8") if l.strip())
print("smoke cost: %.3f" % smoke)
