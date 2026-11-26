"""Scenario inputs for the widget experiment (protocol v1.1 draft). Same style as scenarios.py."""
import json
import os

from common import ROOT

LESSONS = {
    "w-l1": "What happens to the price when demand rises?",
    "w-l2": "Why do we have seasons?",
    "w-l3": "Teach me how supply and demand set the price, then quiz me once on what happens to the equilibrium when supply falls.",
    "w-l4": "Why does the Pythagorean theorem work?",
}
SD_ALL = ["axes", "demand", "supply", "equilibrium", "readout"]
SE_ALL = ["orbit", "labels", "zoom", "readout", "note"]


def system_prompt():
    return open(os.path.join(ROOT, "protocol", "PROTOCOL-v1.1-widgets.md"), encoding="utf-8").read()


def _mini(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def _sd_prior():
    return {"title": "Demand and the price", "lang": "en", "steps": [
        {"title": "The axes", "say": "Price goes up the side, and quantity goes along the bottom.", "ops": [
            {"op": "write", "id": "title", "x": 60, "y": 40, "text": "Demand and the price", "size": 54},
            {"op": "widget", "id": "sd", "kind": "supply-demand", "params": {"show": ["axes"]}}]},
        {"title": "Demand", "say": "Demand slopes down: the higher the price, the less buyers want.", "ops": [
            {"op": "widget", "id": "sd", "kind": "supply-demand", "params": {"show": ["axes", "demand"]}}]},
        {"title": "Supply", "say": "Supply slopes up: the higher the price, the more sellers offer.", "ops": [
            {"op": "widget", "id": "sd", "kind": "supply-demand", "params": {"show": ["axes", "demand", "supply"]}}]},
        {"title": "Equilibrium", "say": "They cross at E: that is the market price and quantity.", "ops": [
            {"op": "widget", "id": "sd", "kind": "supply-demand", "params": {"show": SD_ALL},
             "expect": {"price": "same", "quantity": "same"}}]}]}


def _se_prior():
    return {"title": "Why do we have seasons?", "lang": "en", "steps": [
        {"title": "The orbit", "say": "The Earth goes around the Sun once a year. Its axis is tilted 23.5 degrees and always points the same way.", "ops": [
            {"op": "write", "id": "title", "x": 60, "y": 40, "text": "Why do we have seasons?", "size": 54},
            {"op": "widget", "id": "se", "kind": "seasons", "params": {"show": ["orbit", "labels", "note"], "position": "winter-solstice"}}]},
        {"title": "Winter in the north", "say": "Zoom in. Here the north pole leans away from the Sun, so it is winter in the north.", "ops": [
            {"op": "widget", "id": "se", "kind": "seasons", "params": {"show": SE_ALL},
             "expect": {"north": "winter", "sun_overhead": "south"}}]}]}


def _title_obj(text):
    return {"id": "title", "type": "write", "bbox": [60, 35, 600, 72], "color": "ink", "step": 1, "text": text}


def load_scenarios():
    sc = {}
    for sid, q in LESSONS.items():
        sc[sid] = {"kind": "lesson", "messages": [{"role": "user", "content": q}]}
    sd_state = {"demand_shift": 0, "supply_shift": 2, "equilibrium": {"price": 4, "quantity": 6}, "change": {"price": -1, "quantity": 1}}
    u1 = {"mode": "continue", "question": "Why did the price go down when I moved the blue line to the right?",
          "board": {"atStep": 4, "objects": [_title_obj("Demand and the price")],
                    "widgets": [{"id": "sd", "kind": "supply-demand",
                                 "params": {"show": SD_ALL, "demandShift": 0, "supplyShift": 2, "interactive": "curves"},
                                 "state": sd_state}],
                    "student_events": [{"widget": "sd", "event": "drag", "param": "supplyShift", "from": 0, "to": 2, "state": sd_state}]}}
    sc["w-i1"] = {"kind": "interrupt", "messages": [
        {"role": "user", "content": LESSONS["w-l1"]}, {"role": "assistant", "content": _mini(_sd_prior())}, {"role": "user", "content": _mini(u1)}]}
    se_state = {"angle_deg": 180, "sun_overhead_latitude_deg": 23.5, "season_north": "summer", "season_south": "winter",
                "noon_sun_angle_40N_deg": 74, "day_length_40N_h": 14.9}
    u2 = {"mode": "continue", "question": "Isn't the Earth closer to the Sun right now? That must be why it's hotter.",
          "board": {"atStep": 2, "objects": [_title_obj("Why do we have seasons?")],
                    "widgets": [{"id": "se", "kind": "seasons",
                                 "params": {"show": SE_ALL, "position": "summer-solstice", "interactive": "earth"}, "state": se_state}],
                    "student_events": [{"widget": "se", "event": "drag", "param": "angle", "from": 0, "to": 3.1416, "state": se_state}]}}
    sc["w-i2"] = {"kind": "interrupt", "messages": [
        {"role": "user", "content": LESSONS["w-l2"]}, {"role": "assistant", "content": _mini(_se_prior())}, {"role": "user", "content": _mini(u2)}]}
    return sc
