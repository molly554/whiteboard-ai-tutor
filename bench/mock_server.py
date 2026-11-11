"""Local mock of the three streaming APIs: lets you test the runner (parsing, timing, cost, budget caps) for free."""
import http.server
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANNED = json.dumps(json.load(open(os.path.join(ROOT, "scenarios", "r1-quadratic.json"), encoding="utf-8")),
                    ensure_ascii=False, separators=(",", ":"))


def chunks(s, n=37):
    return [s[i:i + n] for i in range(0, len(s), n)]


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _sse(self, lines, delay=0.004):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for ln in lines:
            self.wfile.write((ln + "\n\n").encode("utf-8"))
            self.wfile.flush()
            time.sleep(delay)

    def do_GET(self):
        vendor = self.path.split("/")[1]
        if vendor == "openrouter":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            return self.wfile.write(json.dumps({"data": {"limit": 16, "limit_remaining": 16, "usage": 0}}).encode())
        ids = {"anthropic": ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-fable-5-2"],
               "gemini": ["models/gemini-4-argon", "models/gemini-3.8-flash"],
               "deepseek": ["deepseek-flash", "deepseek-v4-pro"]}[vendor]
        body = json.dumps({"data": [{"id": i} for i in ids]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n) or b"{}")
        vendor = self.path.split("/")[1]
        if req.get("model") == "claude-fable-5-2" and False:
            pass
        if vendor == "anthropic":
            L = ["event: message_start\ndata: " + json.dumps({"type": "message_start", "message": {"usage": {"input_tokens": 1500, "output_tokens": 1}}}),
                 "data: " + json.dumps({"type": "content_block_start", "index": 0, "content_block": {"type": "thinking"}})]
            time.sleep(0.25)
            L.append("data: " + json.dumps({"type": "content_block_delta", "delta": {"type": "thinking_delta", "thinking": "..."}}))
            L.append("data: " + json.dumps({"type": "content_block_start", "index": 1, "content_block": {"type": "text"}}))
            for c in chunks(CANNED):
                L.append("data: " + json.dumps({"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": c}}))
            L.append("data: " + json.dumps({"type": "message_delta", "delta": {"stop_reason": "end_turn"},
                                            "usage": {"output_tokens": 1200, "output_tokens_details": {"thinking_tokens": 300}}}))
            L.append("data: " + json.dumps({"type": "message_stop"}))
            return self._sse(L)
        if vendor == "openrouter":   # 模拟 OpenRouter：SSE 注释行 + reasoning 字段 + usage.cost
            L = [": OPENROUTER PROCESSING", "data: " + json.dumps({"choices": [{"delta": {"reasoning": "hmm"}}]})]
            for c in chunks(CANNED):
                L.append("data: " + json.dumps({"choices": [{"delta": {"content": c}}]}))
            L.append("data: " + json.dumps({"choices": [{"delta": {}, "finish_reason": "stop"}]}))
            L.append("data: " + json.dumps({"choices": [], "usage": {
                "prompt_tokens": 1500, "completion_tokens": 1200, "cost": 0.0123,
                "completion_tokens_details": {"reasoning_tokens": 300}, "prompt_tokens_details": {"cached_tokens": 0}}}))
            L.append("data: [DONE]")
            return self._sse(L)
        text = "```json\n" + CANNED + "\n```" if vendor == "deepseek" else CANNED
        L = []
        if vendor == "deepseek" and req.get("thinking", {}).get("type") == "enabled":
            L.append("data: " + json.dumps({"choices": [{"delta": {"reasoning_content": "hmm"}}]}))
        for c in chunks(text):
            L.append("data: " + json.dumps({"choices": [{"delta": {"content": c}}]}))
        L.append("data: " + json.dumps({"choices": [{"delta": {}, "finish_reason": "stop"}]}))
        if vendor == "gemini":      # 模拟「思考 token 没算进 completion」的情况
            usage = {"prompt_tokens": 1500, "completion_tokens": 900, "total_tokens": 2700}
        else:
            usage = {"prompt_tokens": 1500, "completion_tokens": 1100, "prompt_cache_hit_tokens": 1000,
                     "prompt_cache_miss_tokens": 500, "completion_tokens_details": {"reasoning_tokens": 200}}
        L.append("data: " + json.dumps({"choices": [], "usage": usage}))
        L.append("data: [DONE]")
        self._sse(L)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
