"""Runner.
  run.py preflight [--via openrouter]   free: check keys and model IDs (and the pinned provider when going through OpenRouter)
  run.py smoke     [--via openrouter]   one lesson + one interruption per model and thinking condition
  run.py main --confirm [--via ...]     the full matrix (3 repeats by default); spends real money
Options: --models a,b   --conds low   --reps 2   --phase name (results file name; lets several processes run in parallel)
--via openrouter sends Claude and Gemini through OpenRouter (pinned to the first-party provider, no fallback);
DeepSeek always goes direct.
"""
import argparse
import json
import os
import random
import sys
import time

import httpx

import config
import providers
from common import Budget, HERE, ROOT, cost_of, get_key, parse_output, scrub, validate_script, worst_case
from scenarios import load_scenarios, system_prompt

RESULTS = os.path.join(ROOT, "results")
MOCK = bool(os.environ.get("WB_MOCK_BASE"))
DEFAULT_MODELS = [m for m in config.MODELS if m != "fable-5.2"]   # Fable 5.2 不参加主矩阵（需要时用 --models 显式指定）


def pick_models(arg):
    names = arg.split(",") if arg else list(DEFAULT_MODELS)
    for n in names:
        if n not in config.MODELS:
            sys.exit("unknown model: %s (choose from %s)" % (n, ",".join(config.MODELS)))
    return names


def route(model, via):
    """返回这个模型实际使用的通道：'openrouter' 或 None（直连）。"""
    return via if (via and config.MODELS[model]["vendor"] != "deepseek") else None


def keys_for(models, via=None):
    keys = {}
    for m in models:
        r = route(m, via)
        name = "openrouter" if r else config.MODELS[m]["vendor"]
        if name in keys:
            continue
        k = "MOCK" if MOCK else get_key(config.KEY_ENV[name])
        if not k:
            sys.exit("missing env var %s (needed for %s)" % (config.KEY_ENV[name], m))
        keys[name] = k
    return keys


def preflight_direct(models):
    ok = True
    for v in sorted({config.MODELS[m]["vendor"] for m in models}):
        k = "MOCK" if MOCK else get_key(config.KEY_ENV[v])
        print("%-10s key: %s" % (v, "present" if k else "MISSING (%s)" % config.KEY_ENV[v]))
        if not k:
            ok = False
            continue
        ids, err = providers.list_models(v, k)
        if err:
            print("           list models failed: %s" % err)
            ok = False
            continue
        for m in models:
            if config.MODELS[m]["vendor"] == v:
                mid = config.MODELS[m]["id"]
                hit = mid in ids
                print("           %-18s %s" % (mid, "found" if hit else "NOT in list"))
                ok = ok and hit
    return ok


def preflight_openrouter(models):
    ok = True
    if not MOCK:
        for m in models:
            or_id, prov = config.OR_ROUTE[m]
            try:
                r = httpx.get(config.OPENROUTER_ENDPOINTS_URL % or_id, timeout=30)
                eps = r.json().get("data", {}).get("endpoints", []) if r.status_code == 200 else []
            except Exception as e:  # noqa: BLE001
                eps = []
                print("%-18s endpoint query failed: %s" % (m, e))
            hit = prov in [e.get("tag") for e in eps]
            print("%-18s %-40s pinned provider '%s': %s" % (m, or_id, prov, "found" if hit else "NOT FOUND"))
            ok = ok and hit
    k = "MOCK" if MOCK else get_key(config.KEY_ENV["openrouter"])
    print("openrouter key: %s" % ("present" if k else "MISSING (%s)" % config.KEY_ENV["openrouter"]))
    if not k:
        return False
    if not MOCK:
        r = httpx.get(config.OPENROUTER_KEY_URL, headers={"Authorization": "Bearer " + k}, timeout=30)
        if r.status_code != 200:
            print("  key check failed: HTTP %s %s" % (r.status_code, scrub(r.text[:200], k)))
            return False
        d = r.json().get("data", {})
        print("  limit=%s  limit_remaining=%s  usage=%s  is_free_tier=%s" % (
            d.get("limit"), d.get("limit_remaining"), d.get("usage"), d.get("is_free_tier")))
    return ok


def preflight(models, via):
    via_models = [m for m in models if route(m, via)]
    direct_models = [m for m in models if not route(m, via)]
    ok = True
    if via_models:
        ok = preflight_openrouter(via_models) and ok
    if direct_models:
        ok = preflight_direct(direct_models) and ok
    return ok


def run_tasks(tasks, phase, models, total_cap, cap_key, via=None):
    os.makedirs(os.path.join(RESULTS, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(RESULTS, "runs"), exist_ok=True)
    scen = load_scenarios()
    system = system_prompt()
    keys = keys_for(models, via)
    caps = {m: config.MODELS[m][cap_key] for m in config.MODELS}
    budget = Budget(os.path.join(RESULTS, "runs", "spend-%s.json" % phase), total_cap, caps)
    out = open(os.path.join(RESULTS, "runs", "%s.jsonl" % phase), "a", encoding="utf-8", newline="\n")
    for n, (m, cond, sid, rep) in enumerate(tasks, 1):
        cfg = config.MODELS[m]
        mvia = route(m, via)
        ok, why = budget.can_run(m, worst_case(cfg, config.MAX_TOKENS))
        if not ok:
            if why.startswith("total"):
                print("STOP: %s" % why)
                break
            print("SKIP %s %s %s: %s" % (m, cond, sid, why))   # 单个模型额度用完只跳过它，不停掉其他模型
            continue
        key = keys["openrouter"] if mvia else keys[cfg["vendor"]]
        res = None
        for attempt in range(3):
            res = providers.call(cfg, cond, system, scen[sid]["messages"], key, via=mvia, model_name=m)
            if res["http"] in (429, 500, 502, 503, 529) or (res["error"] and res["http"] is None):
                time.sleep(5 * (attempt + 1))
                continue
            break
        calc, peak = cost_of(cfg, res["usage"], res["request_ts"])
        reported = res["usage"].get("cost")
        cost = reported if (mvia and reported is not None) else calc
        budget.add(m, cost)
        obj, perr = parse_output(res["text"])
        serr = validate_script(obj) if obj else []
        run_id = "%s-%s-%s-%s-%d" % (phase, m, cond, sid, rep)
        if obj:
            json.dump(obj, open(os.path.join(RESULTS, "scripts", run_id + ".json"), "w", encoding="utf-8", newline="\n"),
                      ensure_ascii=False, indent=1)
        rec = {"run_id": run_id, "via": mvia or "direct", "model": m, "cond": cond, "scenario": sid,
               "kind": scen[sid]["kind"], "rep": rep, "ts": res["request_ts"], "peak": peak,
               "http": res["http"], "error": res["error"], "finish": res["finish"], "t": res["t"],
               "ops_seen": res["ops_seen"], "usage": res["usage"], "usage_raw": res["usage_raw"],
               "cost": cost, "cost_calc": calc, "cost_reported": reported,
               "parse_ok": obj is not None, "parse_error": perr, "schema_errors": serr, "text": res["text"]}
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out.flush()
        t = res["t"]
        n_ops = sum(len(s.get("ops", [])) for s in (obj or {}).get("steps", []) if isinstance(s, dict))
        print("[%d/%d] %-16s %-4s %-24s | http=%s parse=%s schema_err=%d ops=%d | first_op=%s end=%s | out=%s think=%s | $%.4f | %s%s" % (
            n, len(tasks), m, cond, sid, res["http"], "ok" if obj else "FAIL", len(serr), n_ops,
            t.get("first_op"), t.get("end"), res["usage"]["output"], res["usage"]["thinking"], cost, res["finish"],
            (" | ERROR " + res["error"][:300].replace("\n", " ")) if res["error"] else ""), flush=True)
    out.close()
    print("\nspent per model: %s" % json.dumps(budget.spent))
    print("spent total: $%.4f (cap $%.2f)" % (budget.total, total_cap))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["preflight", "smoke", "main"])
    ap.add_argument("--models")
    ap.add_argument("--conds", default="low,mid")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--via", choices=["openrouter"])
    ap.add_argument("--phase")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    models = pick_models(a.models)
    conds = a.conds.split(",")
    if a.cmd == "preflight":
        sys.exit(0 if preflight(models, a.via) else 1)
    rnd = random.Random(20261111)
    if a.cmd == "smoke":
        tasks = [(m, c, s, 1) for m in models for c in conds for s in (config.SMOKE_LESSON, config.SMOKE_INTERRUPT)]
        rnd.shuffle(tasks)
        run_tasks(tasks, a.phase or "smoke", models, config.SMOKE_TOTAL_CAP, "smoke_cap", a.via)
    else:
        if not a.confirm:
            sys.exit("main run spends real money; add --confirm")
        sids = ["r1-seasons", "r1-pythagoras", "r1-quadratic", "r1-supply-demand", "r1-photosynthesis",
                "r1-i1-seasons-distance", "r1-i2-demand-simpler", "r1-i3-arrow-meaning"]
        tasks = [(m, c, s, r) for m in models for c in conds for s in sids for r in range(1, a.reps + 1)]
        rnd.shuffle(tasks)
        run_tasks(tasks, a.phase or "main", models, config.TOTAL_CAP, "cap", a.via)


if __name__ == "__main__":
    main()
