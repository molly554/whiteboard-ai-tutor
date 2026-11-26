"""Deterministic checks for the widget experiment (protocol v1.1 draft).

Mirrors the geometry of player/widgets/*.js just enough to compute what a widget shows after each operation:
  * schema      – every op is a valid v1 op or a valid widget op (kind, params, ranges)
  * expect      – the model's `expect` (what the widget will show) against the state computed from its params
  * topic/state – scenario-specific: the right widget for the topic, or no widget for an uncovered topic
Nothing here judges the narration text; `expect` is how the model commits to what the figure will show.
"""
import math

from common import validate_op

EPS = 23.5 * math.pi / 180
POS = {"winter-solstice": 0.0, "spring-equinox": 1.5 * math.pi, "summer-solstice": math.pi, "autumn-equinox": 0.5 * math.pi}
SEASON = {"winter-solstice": "winter", "spring-equinox": "spring", "summer-solstice": "summer", "autumn-equinox": "autumn"}

SD_PARTS = {"axes", "demand", "supply", "equilibrium", "readout"}
SE_PARTS = {"orbit", "labels", "zoom", "readout", "note"}
DEFAULTS = {
    "supply-demand": {"show": sorted(SD_PARTS), "demandShift": 0, "supplyShift": 0, "ask": None, "interactive": "curves"},
    "seasons": {"show": sorted(SE_PARTS), "position": "winter-solstice", "ask": None, "interactive": "earth"},
}


QUIZ_ANSWER = {"north-summer": "summer-solstice", "south-summer": "winter-solstice"}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _sign(x, tol=0.15):
    return "up" if x > tol else "down" if x < -tol else "same"


def sd_state(p):
    s, t = p["demandShift"], p["supplyShift"]
    return {"price": _sign((s - t) / 2), "quantity": _sign((s + t) / 2)}


def se_state(p):
    th = POS[p["position"]]
    d = math.degrees(math.asin(-math.sin(EPS) * math.cos(th)))
    return {"north": SEASON[p["position"]], "sun_overhead": "north" if d > 3 else "south" if d < -3 else "equator"}


def check_params(kind, params):
    errs = []
    allowed = {"supply-demand": {"show", "demandShift", "supplyShift", "ask", "interactive"},
               "seasons": {"show", "position", "ask", "interactive"}}[kind]
    for k, v in params.items():
        if k not in allowed:
            errs.append("unknown param %s" % k)
            continue
        if k == "show":
            parts = SD_PARTS if kind == "supply-demand" else SE_PARTS
            if not (isinstance(v, list) and all(isinstance(x, str) and x in parts for x in v)):
                errs.append("bad show %r" % (v,))
        elif k in ("demandShift", "supplyShift"):
            if not (_num(v) and -3 <= v <= 3):
                errs.append("%s must be a number in -3..3" % k)
        elif k == "position":
            if v not in POS:
                errs.append("bad position %r" % (v,))
        elif k == "ask":
            ok = (None, "equilibrium") if kind == "supply-demand" else (None, "north-summer", "south-summer")
            if v not in ok:
                errs.append("bad ask %r" % (v,))
        elif k == "interactive":
            ok = ("curves", "none") if kind == "supply-demand" else ("earth", "none")
            if v not in ok:
                errs.append("bad interactive %r" % (v,))
    return errs


def check_expect(kind, exp):
    if not isinstance(exp, dict):
        return "expect must be an object"
    keys = {"supply-demand": {"price": ("up", "down", "same"), "quantity": ("up", "down", "same")},
            "seasons": {"north": ("summer", "winter", "spring", "autumn"), "sun_overhead": ("north", "south", "equator")}}[kind]
    for k, v in exp.items():
        if k not in keys:
            return "unknown expect key %s" % k
        if v not in keys[k]:
            return "bad expect value %s=%r" % (k, v)
    if set(exp) != set(keys):
        return "expect needs exactly %s" % sorted(keys)
    return None


def check(obj, sid):
    """Returns a dict of counts and flags for one model output."""
    r = {"schema_errors": [], "steps": 0, "widget_ops": 0, "v1_ops": 0, "expect_required": 0, "expect_given": 0,
         "expect_ok": 0, "expect_missing": 0, "expect_wrong": [], "notes": [], "kinds": [], "ask_ops": 0,
         "topic_ok": None, "state_ok": None}
    if not isinstance(obj, dict) or not isinstance(obj.get("steps"), list):
        r["schema_errors"].append("no steps array")
        return r
    r["steps"] = len(obj["steps"])
    wid = {}                       # widget id -> {"kind", "params"}
    prior = INTERRUPT_STATE.get(sid)
    if prior:
        wid[prior["id"]] = {"kind": prior["kind"], "params": dict(prior["params"])}
    history = []                   # (kind, params after op, had ask)
    for si, st in enumerate(obj["steps"], 1):
        if not isinstance(st, dict) or not isinstance(st.get("ops"), list):
            r["schema_errors"].append("step %d: ops missing" % si)
            continue
        if not (isinstance(st.get("say"), str) and st["say"].strip()):
            r["notes"].append("step %d: no narration" % si)
        n_w = 0
        for oi, op in enumerate(st["ops"], 1):
            where = "step %d op %d" % (si, oi)
            if isinstance(op, dict) and op.get("op") == "widget":
                r["widget_ops"] += 1
                n_w += 1
                kind, i = op.get("kind"), op.get("id")
                if kind not in DEFAULTS:
                    r["schema_errors"].append("%s: unknown widget kind %r" % (where, kind))
                    continue
                if not (isinstance(i, str) and i):
                    r["schema_errors"].append("%s: widget needs an id" % where)
                    continue
                params = op.get("params", {})
                if not isinstance(params, dict):
                    r["schema_errors"].append("%s: params must be an object" % where)
                    continue
                pe = check_params(kind, params)
                r["schema_errors"] += ["%s: %s" % (where, e) for e in pe]
                if i in wid and wid[i]["kind"] != kind:
                    r["schema_errors"].append("%s: id %s is already a %s widget" % (where, i, wid[i]["kind"]))
                    continue
                cur = wid.setdefault(i, {"kind": kind, "params": dict(DEFAULTS[kind])})
                if kind not in r["kinds"]:
                    r["kinds"].append(kind)
                if not pe:
                    # a quiz (ask) ends when a later op sets ask to null: the board is then wherever the student left the Earth;
                    # we assume a correct answer, which puts the Earth at the answer position of that quiz
                    if kind == "seasons" and "ask" in params and params["ask"] is None and "position" not in params and cur["params"].get("ask") in QUIZ_ANSWER:
                        cur["params"]["position"] = QUIZ_ANSWER[cur["params"]["ask"]]
                    cur["params"].update(params)
                    if "ask" in params and params["ask"]:
                        r["ask_ops"] += 1
                p = cur["params"]
                asking = bool(p.get("ask"))
                visible = ("equilibrium" in p["show"]) if kind == "supply-demand" else bool({"zoom", "readout"} & set(p["show"]))
                history.append((kind, dict(p), asking, bool(params.get("ask"))))
                if visible and not asking:
                    r["expect_required"] += 1
                    if "expect" not in op:
                        r["expect_missing"] += 1
                if "expect" in op:
                    r["expect_given"] += 1
                    ee = check_expect(kind, op["expect"])
                    if ee:
                        r["schema_errors"].append("%s: %s" % (where, ee))
                    elif not pe:
                        want = sd_state(p) if kind == "supply-demand" else se_state(p)
                        bad = {k: (op["expect"][k], want[k]) for k in want if op["expect"][k] != want[k]}
                        if bad:
                            r["expect_wrong"].append("%s: %s" % (where, "; ".join("%s said %s, widget shows %s" % (k, a, b) for k, (a, b) in bad.items())))
                        else:
                            r["expect_ok"] += 1
            else:
                r["v1_ops"] += 1
                e = validate_op(op)
                if e:
                    r["schema_errors"].append("%s: %s" % (where, e))
        if n_w > 1:
            r["notes"].append("step %d: %d widget ops (one allowed)" % (si, n_w))
    r["schema_ok"] = not r["schema_errors"]
    topic_and_state(r, sid, history)
    return r


# state the interruption scenarios start from (must match widget_scenarios.py)
INTERRUPT_STATE = {
    "w-i1": {"id": "sd", "kind": "supply-demand", "params": {**DEFAULTS["supply-demand"], "supplyShift": 2}},
    "w-i2": {"id": "se", "kind": "seasons", "params": {**DEFAULTS["seasons"], "position": "summer-solstice"}},
}


def topic_and_state(r, sid, history):
    kinds = set(r["kinds"])
    if sid == "w-l1":
        r["topic_ok"] = kinds == {"supply-demand"}
        last = [h for h in history if h[0] == "supply-demand"]
        r["state_ok"] = bool(last) and last[-1][1]["demandShift"] > 0 and last[-1][1]["supplyShift"] == 0
    elif sid == "w-l2":
        r["topic_ok"] = kinds == {"seasons"}
        pos = {h[1]["position"] for h in history if h[0] == "seasons"}
        r["state_ok"] = {"summer-solstice", "winter-solstice"} <= pos
    elif sid == "w-l3":
        r["topic_ok"] = kinds == {"supply-demand"}
        asks = [h for h in history if h[0] == "supply-demand" and h[3] and h[1]["ask"] == "equilibrium"]
        r["state_ok"] = bool(asks) and asks[-1][1]["supplyShift"] < 0 and asks[-1][1]["demandShift"] == 0
        if asks and abs(asks[-1][1]["supplyShift"]) < 1.5:
            r["notes"].append("ask with a shift smaller than 1.5")
    elif sid == "w-l4":
        r["topic_ok"] = r["widget_ops"] == 0       # an uncovered topic must fall back to ordinary operations
        r["state_ok"] = r["v1_ops"] > 0
    else:                                          # interruptions: any widget op must keep to the existing widget
        r["topic_ok"] = len(kinds) <= 1 and (not kinds or kinds == {INTERRUPT_STATE[sid]["kind"]})
        r["state_ok"] = r["steps"] > 0
