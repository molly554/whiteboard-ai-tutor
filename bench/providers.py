"""三家的流式调用。Gemini 和 DeepSeek 走 OpenAI 兼容接口，Claude 走原生 Messages 接口。
每次调用返回统一结构：文本、停止原因、用量、各阶段耗时（相对请求发出时刻，单位秒）。"""
import json
import os
import time

import httpx

from common import OpScanner, scrub
import config


def _url(vendor, kind="chat"):
    mock = os.environ.get("WB_MOCK_BASE")
    if vendor == "openrouter":
        return (mock + "/openrouter/chat/completions") if mock else config.OPENROUTER_URL
    if mock:
        return {
            ("anthropic", "chat"): mock + "/anthropic/v1/messages",
            ("gemini", "chat"): mock + "/gemini/chat/completions",
            ("deepseek", "chat"): mock + "/deepseek/chat/completions",
            ("anthropic", "list"): mock + "/anthropic/v1/models",
            ("gemini", "list"): mock + "/gemini/models",
            ("deepseek", "list"): mock + "/deepseek/models",
        }[(vendor, kind)]
    return config.URLS[vendor] if kind == "chat" else config.MODEL_LIST_URLS[vendor]


def _headers(vendor, key):
    if vendor == "anthropic":
        return {"x-api-key": key, "anthropic-version": config.ANTHROPIC_VERSION, "content-type": "application/json"}
    return {"Authorization": "Bearer " + key, "content-type": "application/json"}


def build_request(cfg, cond, system, messages, max_tokens):
    v = cfg["vendor"]
    if v == "anthropic":
        return {
            "model": cfg["id"], "max_tokens": max_tokens, "stream": True,
            "system": system, "messages": messages,
            "output_config": {"effort": cond["effort"]},
        }
    body = {
        "model": cfg["id"], "stream": True, "stream_options": {"include_usage": True},
        "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}] + messages,
    }
    if v == "gemini":
        body["reasoning_effort"] = cond["effort"]
    else:  # deepseek
        body["thinking"] = {"type": cond["thinking"]}
        if cond["thinking"] == "enabled":
            body["reasoning_effort"] = cond["effort"]
        if "temperature" in cond:
            body["temperature"] = cond["temperature"]
    return body


def build_request_or(model_name, cfg, cond, cond_name, system, messages, max_tokens):
    or_id, provider = config.OR_ROUTE[model_name]
    body = {
        "model": or_id, "stream": True, "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}] + messages,
        "reasoning": config.OR_REASONING[cfg["vendor"]][cond_name],
        "provider": {"order": [provider], "allow_fallbacks": False},
    }
    if "temperature" in cond:
        body["temperature"] = cond["temperature"]
    return body


def _sse(resp):
    for line in resp.iter_lines():
        if line and line.startswith("data:"):
            yield line[5:].strip()


def call(cfg, cond_name, system, messages, key, max_tokens=config.MAX_TOKENS, via=None, model_name=None):
    v = "openrouter" if via == "openrouter" else cfg["vendor"]
    cond = cfg["conds"][cond_name]
    if v == "openrouter":
        body = build_request_or(model_name, cfg, cond, cond_name, system, messages, max_tokens)
    else:
        body = build_request(cfg, cond, system, messages, max_tokens)
    res = {"text": "", "finish": None, "error": None, "http": None, "t": {}, "ops_seen": 0,
           "usage": {"input": None, "output": None, "thinking": None, "cache_read": 0, "cost": None}, "usage_raw": {},
           "request_ts": time.time()}
    scanner = OpScanner()
    t0 = time.perf_counter()

    def mark(name):
        if name not in res["t"]:
            res["t"][name] = round(time.perf_counter() - t0, 3)

    def add_text(piece):
        mark("first_text")
        res["text"] += piece
        scanner.feed(piece)
        if scanner.count >= 1:
            mark("first_op")

    try:
        with httpx.Client(timeout=httpx.Timeout(240.0, connect=20.0)) as client:
            with client.stream("POST", _url(v), headers=_headers(v, key), json=body) as r:
                res["http"] = r.status_code
                mark("headers")
                if r.status_code != 200:
                    r.read()
                    res["error"] = scrub(r.text[:800], key)
                    res["t"]["end"] = round(time.perf_counter() - t0, 3)
                    return res
                for data in _sse(r):
                    mark("first_event")
                    if data == "[DONE]":
                        break
                    ev = json.loads(data)
                    if v == "anthropic":
                        _anthropic_event(ev, res, mark, add_text)
                    else:
                        _compat_event(ev, res, mark, add_text)
    except Exception as e:  # noqa: BLE001
        res["error"] = scrub("%s: %s" % (type(e).__name__, e), key)
    res["t"]["end"] = round(time.perf_counter() - t0, 3)
    res["ops_seen"] = scanner.count
    _normalize_usage(v, res)
    return res


def _anthropic_event(ev, res, mark, add_text):
    t = ev.get("type")
    if t == "message_start":
        res["usage_raw"].update(ev.get("message", {}).get("usage", {}) or {})
    elif t == "content_block_start":
        if (ev.get("content_block") or {}).get("type") == "thinking":
            mark("first_thinking")
    elif t == "content_block_delta":
        d = ev.get("delta") or {}
        if d.get("type") == "text_delta":
            add_text(d.get("text", ""))
        elif d.get("type") == "thinking_delta":
            mark("first_thinking")
    elif t == "message_delta":
        res["usage_raw"].update(ev.get("usage", {}) or {})
        res["finish"] = (ev.get("delta") or {}).get("stop_reason") or res["finish"]
    elif t == "error":
        res["error"] = json.dumps(ev.get("error"), ensure_ascii=False)[:500]


def _compat_event(ev, res, mark, add_text):
    if ev.get("usage"):
        res["usage_raw"] = ev["usage"]
    if ev.get("error"):
        res["error"] = json.dumps(ev["error"], ensure_ascii=False)[:500]
    ch = ev.get("choices") or []
    if ch:
        d = ch[0].get("delta") or {}
        if d.get("reasoning_content") or d.get("reasoning") or d.get("reasoning_details"):
            mark("first_thinking")
        if d.get("content"):
            add_text(d["content"])
        if ch[0].get("finish_reason"):
            res["finish"] = ch[0]["finish_reason"]


def _normalize_usage(vendor, res):
    u, raw = res["usage"], res["usage_raw"]
    if vendor == "anthropic":
        u["input"] = raw.get("input_tokens")
        u["output"] = raw.get("output_tokens")
        u["thinking"] = (raw.get("output_tokens_details") or {}).get("thinking_tokens")
        u["cache_read"] = raw.get("cache_read_input_tokens") or 0
    elif vendor == "openrouter":
        u["input"], u["output"] = raw.get("prompt_tokens"), raw.get("completion_tokens")
        u["thinking"] = (raw.get("completion_tokens_details") or {}).get("reasoning_tokens")
        u["cache_read"] = (raw.get("prompt_tokens_details") or {}).get("cached_tokens") or 0
        u["cost"] = raw.get("cost")          # OpenRouter 返回的实际扣费（美元）
    else:
        prompt, comp = raw.get("prompt_tokens"), raw.get("completion_tokens")
        u["input"], u["output"] = prompt, comp
        u["thinking"] = (raw.get("completion_tokens_details") or {}).get("reasoning_tokens")
        if vendor == "gemini" and None not in (prompt, comp, raw.get("total_tokens")):
            extra = raw["total_tokens"] - prompt - comp       # 兼容接口可能没把思考 token 算进 completion
            if extra > 0:
                u["output"] = comp + extra
                u["thinking"] = u["thinking"] if u["thinking"] is not None else extra
        if vendor == "deepseek":
            u["cache_read"] = raw.get("prompt_cache_hit_tokens") or 0


def list_models(vendor, key):
    r = httpx.get(_url(vendor, "list"), headers=_headers(vendor, key), timeout=30.0)
    if r.status_code != 200:
        return None, scrub(r.text[:300], key)
    ids = [m.get("id", "").replace("models/", "") for m in (r.json().get("data") or [])]
    return ids, None
