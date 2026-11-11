"""Shared helpers: API-key lookup, streaming op scanner, output parsing and validation, pricing and budget caps."""
import datetime
import json
import os
import re
import time

try:
    import winreg
except ImportError:  # 非 Windows
    winreg = None

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root


# ───────── 密钥：只读环境变量（读不到再读用户级环境变量），任何输出都不带密钥 ─────────
def get_key(name):
    v = os.environ.get(name)
    if v:
        return v.strip()
    if winreg:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                v, _ = winreg.QueryValueEx(k, name)
                return str(v).strip() or None
        except OSError:
            return None
    return None


def scrub(text, key):
    if key and key in text:
        text = text.replace(key, "***")
    return text


# ───────── 流式扫描：数出已经完整的绘图指令（根对象深度 1，步骤 2，指令 3） ─────────
class OpScanner:
    def __init__(self):
        self.depth = 0
        self.in_str = False
        self.esc = False
        self.count = 0

    def feed(self, s):
        n = 0
        for ch in s:
            if self.in_str:
                if self.esc:
                    self.esc = False
                elif ch == "\\":
                    self.esc = True
                elif ch == '"':
                    self.in_str = False
                continue
            if ch == '"':
                self.in_str = True
            elif ch == "{":
                self.depth += 1
            elif ch == "}":
                if self.depth == 3:
                    n += 1
                self.depth -= 1
        self.count += n
        return n


# ───────── 输出解析与校验（规则与播放器里的 validateOp 一致） ─────────
COLORS = {"ink", "blue", "red", "green", "gray"}


def parse_output(text):
    t = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1).strip()
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j < i:
        return None, "no json object"
    try:
        return json.loads(t[i:j + 1]), None
    except Exception as e:  # noqa: BLE001
        return None, "json error: %s" % e


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_op(op):
    if not isinstance(op, dict):
        return "not an object"
    k = op.get("op")
    if k not in ("write", "line", "rect", "ellipse", "path", "erase"):
        return "unknown op %r" % (k,)
    if k == "erase":
        n = sum(1 for f in ("ids", "region", "all") if op.get(f))
        if n != 1:
            return "erase needs exactly one of ids/region/all"
        if op.get("ids") and not (isinstance(op["ids"], list) and all(isinstance(s, str) for s in op["ids"])):
            return "ids must be a string array"
        if op.get("region") and not all(_num((op["region"] or {}).get(f)) for f in "xywh"):
            return "region needs numeric x,y,w,h"
        return None
    if not isinstance(op.get("id"), str) or not op["id"]:
        return "missing id"
    need = {"write": ["x", "y"], "line": ["x1", "y1", "x2", "y2"], "rect": ["x", "y", "w", "h"],
            "ellipse": ["cx", "cy", "rx", "ry"], "path": []}[k]
    for f in need:
        if not _num(op.get(f)):
            return "field %s must be a number" % f
    if k == "write" and not (isinstance(op.get("text"), str) and op["text"]):
        return "missing text"
    if k == "path" and not (isinstance(op.get("d"), str) and op["d"]):
        return "missing d"
    if op.get("color") is not None and op["color"] not in COLORS:
        return "bad color %r" % (op["color"],)
    if op.get("fill") is not None and op["fill"] not in COLORS:
        return "bad fill %r" % (op["fill"],)
    for f in ("size", "width"):
        if op.get(f) is not None and not (_num(op[f]) and op[f] > 0):
            return "%s must be positive" % f
    if op.get("anchor") is not None and op["anchor"] not in ("start", "middle"):
        return "bad anchor"
    if op.get("arrow") is not None and op["arrow"] not in (True, False, "both"):
        return "bad arrow"
    return None


def validate_script(o):
    if not isinstance(o, dict) or not isinstance(o.get("steps"), list):
        return ["no steps array"]
    errs = []
    for si, st in enumerate(o["steps"]):
        if not isinstance(st, dict) or not isinstance(st.get("ops"), list):
            errs.append("step %d: ops missing" % (si + 1))
            continue
        for oi, op in enumerate(st["ops"]):
            e = validate_op(op)
            if e:
                errs.append("step %d op %d: %s" % (si + 1, oi + 1, e))
    return errs


# ───────── 价格与成本 ─────────
def is_peak(ts):
    d = datetime.datetime.utcfromtimestamp(ts)
    return d.weekday() < 5 and (1 <= d.hour < 4 or 6 <= d.hour < 10)


def price_for(cfg, ts):
    if "a" in cfg["price"]:
        return cfg["price"]["a"], None
    peak = is_peak(ts)
    return cfg["price"]["peak" if peak else "off"], peak


def cost_of(cfg, usage, ts):
    (pin, pout, pcache), peak = price_for(cfg, ts)
    inp, out = usage.get("input") or 0, usage.get("output") or 0
    cache = usage.get("cache_read") or 0
    cost = ((inp - cache) * pin + cache * pcache + out * pout) / 1e6
    return round(cost, 6), peak


def worst_case(cfg, max_tokens, est_input=3000):
    """调用前的预算检查用「典型上限」：输入 3k、输出 4k token（单次调用最多 8k 输出，超出的部分靠事后累计兜底）。"""
    p = cfg["price"].get("a") or cfg["price"]["peak"]
    return (est_input * p[0] + min(max_tokens, 4000) * p[1]) / 1e6


class Budget:
    def __init__(self, path, total_cap, caps):
        self.path, self.total_cap, self.caps = path, total_cap, caps
        self.spent = {}
        if os.path.exists(path):
            self.spent = json.load(open(path, encoding="utf-8"))

    @property
    def total(self):
        return sum(self.spent.values())

    def can_run(self, model, worst):
        if self.total + worst > self.total_cap:
            return False, "total cap %.2f would be exceeded" % self.total_cap
        if self.spent.get(model, 0) + worst > self.caps[model]:
            return False, "%s cap %.2f would be exceeded" % (model, self.caps[model])
        return True, ""

    def add(self, model, cost):
        self.spent[model] = round(self.spent.get(model, 0) + cost, 6)
        json.dump(self.spent, open(self.path, "w", encoding="utf-8", newline="\n"), indent=1)
