"""Scenario inputs: 8 scenarios, identical for every model. The system prompt is protocol/PROTOCOL.md verbatim."""
import json
import os

from common import HERE, ROOT


def _load(path):
    return json.load(open(path, encoding="utf-8"))


def system_prompt():
    return open(os.path.join(ROOT, "protocol", "PROTOCOL.md"), encoding="utf-8").read()


def _mini(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def load_scenarios():
    idx = {e["id"]: e for e in _load(os.path.join(ROOT, "scenarios", "index.json"))["scripts"]}
    sc = {}
    for sid in ("r1-seasons", "r1-pythagoras", "r1-quadratic", "r1-supply-demand", "r1-photosynthesis"):
        sc[sid] = {"kind": "lesson", "messages": [{"role": "user", "content": idx[sid]["question"]}]}
    for sid, base, state_file in (
            ("r1-i1-seasons-distance", "r1-seasons", "state-i1.json"),
            ("r1-i2-demand-simpler", "r1-supply-demand", "state-i2.json"),
            ("r1-i3-arrow-meaning", "r1-supply-demand", "state-i2.json")):
        cont = _load(os.path.join(ROOT, "scenarios", sid + ".json"))
        base_script = _load(os.path.join(ROOT, "scenarios", base + ".json"))
        at = cont["atStep"]
        prior = {"title": base_script["title"], "lang": base_script["lang"], "steps": base_script["steps"][:at]}
        state = _load(os.path.join(ROOT, "scenarios", state_file))
        user2 = {"mode": "continue", "question": cont["question"],
                 "board": {"atStep": state["atStep"], "objects": state["objects"]}}
        sc[sid] = {"kind": "interrupt", "messages": [
            {"role": "user", "content": idx[base]["question"]},
            {"role": "assistant", "content": _mini(prior)},
            {"role": "user", "content": _mini(user2)}]}
    return sc
