"""Summary of the widget experiment: results/widgets/*.jsonl  ->  results/widgets/summary.md
Compares per model and scenario; the v1 columns come from the existing 288-call benchmark (low thinking, same models)."""
import collections
import glob
import json
import os
import statistics

from common import ROOT, parse_output
import widget_check

OUT = os.path.join(ROOT, "results", "widgets")
MODELS = ["haiku-5.5", "gemini-3.8-flash", "sonnet-5.5"]
SCEN = ["w-l1", "w-l2", "w-l3", "w-l4", "w-i1", "w-i2"]
NAMES = {"w-l1": "lesson: demand rises", "w-l2": "lesson: seasons", "w-l3": "teach + quiz: supply falls",
         "w-l4": "uncovered topic: Pythagoras", "w-i1": "interruption: supply dragged", "w-i2": "interruption: Earth dragged"}
V1_MATCH = {"w-l1": ["r1-supply-demand"], "w-l2": ["r1-seasons"], "w-l4": ["r1-pythagoras"],
            "w-i1": ["r1-i2-demand-simpler", "r1-i3-arrow-meaning"], "w-i2": ["r1-i1-seasons-distance"]}


def load(pattern):
    rows = []
    for f in sorted(glob.glob(os.path.join(OUT, pattern))):
        for ln in open(f, encoding="utf-8"):
            if ln.strip():
                rows.append(json.loads(ln))
    return rows


def med(v):
    v = [x for x in v if x is not None]
    return statistics.median(v) if v else None


def fmt(x, d=1):
    return "–" if x is None else ("%.*f" % (d, x))


def v1_baseline():
    base = collections.defaultdict(list)
    for f in glob.glob(os.path.join(ROOT, "results", "runs", "main-*.jsonl")):
        for ln in open(f, encoding="utf-8"):
            if not ln.strip():
                continue
            r = json.loads(ln)
            if r.get("cond") == "low" and r.get("http") == 200:
                base[(r["model"], r["scenario"])].append(r)
    return base


def main():
    rows = [r for r in load("wsmoke.jsonl") + load("wmain.jsonl") if r.get("http") == 200]
    changed = 0
    for r in rows:                      # recompute from the stored text with the current checker
        obj, _ = parse_output(r["text"])
        new = widget_check.check(obj, r["scenario"]) if obj else None
        if new and r["check"] and (len(new["expect_wrong"]), new["state_ok"], new["topic_ok"], new["expect_missing"]) !=                 (len(r["check"]["expect_wrong"]), r["check"]["state_ok"], r["check"]["topic_ok"], r["check"]["expect_missing"]):
            changed += 1
        r["check"] = new
    base = v1_baseline()
    L = ["# Widget experiment — summary", "",
         "Protocol v1.1 draft (`protocol/PROTOCOL-v1.1-widgets.md`), low thinking, via OpenRouter, pinned first-party providers.",
         "%d calls with an answer (smoke run + main run)." % len(rows), ""]
    tot = sum(r["cost"] or 0 for r in rows)
    L.append("Total spend on these calls: **$%.3f**." % tot)
    if changed:
        L.append("")
        L.append("Checks were recomputed from the stored outputs with the final checker; %d call(s) differ from what the runner printed live (see the note on quizzes below)." % changed)
    L += ["", "## Per model", "",
          "| model | calls | parsed | schema-valid | right widget / no widget | expected end state | `expect` correct | `expect` missing | spend |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        rs = [r for r in rows if r["model"] == m]
        if not rs:
            continue
        n = len(rs)
        pars = sum(r["parse_ok"] for r in rs)
        sch = sum(1 for r in rs if r["check"] and r["check"]["schema_ok"])
        top = sum(1 for r in rs if r["check"] and r["check"]["topic_ok"])
        sta = sum(1 for r in rs if r["check"] and r["check"]["state_ok"])
        eg = sum(r["check"]["expect_given"] for r in rs if r["check"])
        eo = sum(r["check"]["expect_ok"] for r in rs if r["check"])
        em = sum(r["check"]["expect_missing"] for r in rs if r["check"])
        er = sum(r["check"]["expect_required"] for r in rs if r["check"])
        L.append("| %s | %d | %d | %d | %d | %d | %d / %d | %d / %d | $%.3f |" % (m, n, pars, sch, top, sta, eo, eg, em, er, sum(r["cost"] or 0 for r in rs)))
    L += ["", "## Per model and scenario", "",
          "Columns: calls, schema-valid, right widget (or none when the topic is uncovered), expected end state, `expect` wrong, first op (s, median), output tokens (median), cost per call (mean). "
          "The v1 columns are the old benchmark on the nearest scenario with the same model, low thinking.", "",
          "| model | scenario | calls | schema | topic | state | expect wrong | first op s | out tok | $/call | v1 first op s | v1 out tok | v1 $/call |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for s in SCEN:
            rs = [r for r in rows if r["model"] == m and r["scenario"] == s]
            if not rs:
                continue
            ck = [r["check"] for r in rs if r["check"]]
            b = [x for sid in V1_MATCH.get(s, []) for x in base.get((m, sid), [])]
            L.append("| %s | %s | %d | %d | %d | %d | %d | %s | %s | %s | %s | %s | %s |" % (
                m, NAMES[s], len(rs), sum(c["schema_ok"] for c in ck), sum(1 for c in ck if c["topic_ok"]), sum(1 for c in ck if c["state_ok"]),
                sum(len(c["expect_wrong"]) for c in ck), fmt(med([r["t"].get("first_op") for r in rs])),
                fmt(med([r["usage"]["output"] for r in rs]), 0), "$%.4f" % (sum(r["cost"] or 0 for r in rs) / len(rs)),
                fmt(med([x["t"].get("first_op") for x in b])), fmt(med([x["usage"]["output"] for x in b]), 0),
                ("$%.4f" % (sum(x["cost"] or 0 for x in b) / len(b))) if b else "–"))
    L += ["", "## Failures, listed", ""]
    any_fail = False
    for r in rows:
        c = r["check"]
        if not c:
            continue
        issues = list(c["schema_errors"]) + list(c["expect_wrong"])
        if not c["topic_ok"]:
            issues.append("wrong widget choice for this topic (widgets used: %s, widget ops %d)" % (c["kinds"] or "none", c["widget_ops"]))
        if c["state_ok"] is False:
            issues.append("end state is not the one the scenario asks for")
        if issues:
            any_fail = True
            L.append("- `%s` %s #%d: %s" % (r["model"], r["scenario"], r["rep"], "; ".join(issues)))
    if not any_fail:
        L.append("- none")
    L += ["", "## What this does not show", "",
          "- The checks are deterministic: schema, widget choice, and whether the model's `expect` matches the state its own params produce. "
          "They do not read the narration, so a step whose text disagrees with its params is not caught unless `expect` also disagrees.",
          "- After a quiz, an operation that sets `ask` to null without a position leaves the Earth wherever the student put it. The checker assumes a correct answer (the quiz's answer position); this rule was added after seeing the first results, because one run was marked wrong for a reasonable expectation.",
          "- Three models, three repeats per scenario, six scenarios, two widget kinds written by hand: the numbers say nothing about other topics or other models.",
          "- The v1 columns are for orientation only: a different prompt (English, longer), different scenarios and a much easier task (parameters instead of coordinates).",
          "- No student has used any of the resulting boards."]
    open(os.path.join(OUT, "summary.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
