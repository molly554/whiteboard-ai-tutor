"""被测模型、价格和思考条件。价格单位：美元 / 百万 token，取自 2026-11-10 读取的官方页面。"""

# 价格里的 cache 是「缓存命中读取」价。DeepSeek 分高峰 / 非高峰两档，其余模型只有一档。
MODELS = {
    "haiku-5.5": dict(
        vendor="anthropic", id="claude-haiku-5-5",
        price=dict(a=(0.10, 0.50, 0.01)),
        conds={"low": {"effort": "low"}, "mid": {"effort": "medium"}},
        cap=0.50, smoke_cap=0.20),
    "sonnet-5.5": dict(
        vendor="anthropic", id="claude-sonnet-5-5",
        price=dict(a=(2.00, 10.00, 0.10)),
        conds={"low": {"effort": "low"}, "mid": {"effort": "medium"}},
        cap=1.90, smoke_cap=0.30),
    "fable-5.2": dict(
        vendor="anthropic", id="claude-fable-5-2",
        price=dict(a=(8.00, 40.00, 0.20)),
        conds={"low": {"effort": "low"}, "mid": {"effort": "medium"}},
        cap=7.60, smoke_cap=0.80),
    "gemini-4-argon": dict(
        vendor="gemini", id="gemini-4-argon",
        price=dict(a=(2.00, 10.00, 0.10)),          # 11 月价；2026-12-01 起翻倍
        conds={"low": {"effort": "low"}, "mid": {"effort": "medium"}},
        cap=1.90, smoke_cap=0.30),
    "gemini-3.8-flash": dict(
        vendor="gemini", id="gemini-3.8-flash",
        price=dict(a=(0.75, 3.75, 0.075)),
        conds={"low": {"effort": "low"}, "mid": {"effort": "medium"}},
        cap=1.10, smoke_cap=0.20),
    "deepseek-flash": dict(
        vendor="deepseek", id="deepseek-flash",
        price=dict(peak=(0.30, 1.20, 0.006), off=(0.15, 0.60, 0.003)),
        conds={"low": {"thinking": "disabled", "temperature": 0.7},
               "mid": {"thinking": "enabled", "effort": "low"}},
        cap=0.50, smoke_cap=0.10),
    "deepseek-v4-pro": dict(
        vendor="deepseek", id="deepseek-v4-pro",
        price=dict(peak=(1.32, 3.96, 0.044), off=(0.66, 1.98, 0.022)),
        conds={"low": {"thinking": "disabled", "temperature": 0.7},
               "mid": {"thinking": "enabled", "effort": "low"}},
        cap=1.20, smoke_cap=0.20),
}

URLS = {
    "anthropic": "https://api.anthropic.com/v1/messages",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "deepseek": "https://api.deepseek.com/chat/completions",
}
MODEL_LIST_URLS = {
    "anthropic": "https://api.anthropic.com/v1/models?limit=1000",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/models",
    "deepseek": "https://api.deepseek.com/models",
}
KEY_ENV = {"anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY", "deepseek": "DEEPSEEK_API_KEY"}
ANTHROPIC_VERSION = "2026-10-21"

# ───────── 经 OpenRouter 调用（一个密钥覆盖全部模型）─────────
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY_URL = "https://openrouter.ai/api/v1/key"
OPENROUTER_ENDPOINTS_URL = "https://openrouter.ai/api/v1/models/%s/endpoints"
KEY_ENV["openrouter"] = "OPENROUTER_API_KEY"

# 模型名 -> (OpenRouter 模型 ID, 固定的一方服务商)。固定服务商并禁止回退，
# 否则 OpenRouter 会把 DeepSeek 路由到几十家第三方（量化精度、价格、速度各不相同）。
OR_ROUTE = {
    "haiku-5.5": ("anthropic/claude-haiku-5.5", "anthropic"),
    "sonnet-5.5": ("anthropic/claude-sonnet-5.5", "anthropic"),
    "fable-5.2": ("anthropic/claude-fable-5.2", "anthropic"),
    "gemini-4-argon": ("google/gemini-4-argon", "google-ai-studio"),
    "gemini-3.8-flash": ("google/gemini-3.8-flash", "google-ai-studio"),
    "deepseek-flash": ("deepseek/deepseek-v4.1-flash-1017", "deepseek"),
    "deepseek-v4-pro": ("deepseek/deepseek-v4-pro-0813", "deepseek"),
}
# 低 / 中思考条件在 OpenRouter 统一的 reasoning 参数里的写法
OR_REASONING = {
    "anthropic": {"low": {"effort": "low"}, "mid": {"effort": "medium"}},
    "gemini": {"low": {"effort": "low"}, "mid": {"effort": "medium"}},
    "deepseek": {"low": {"enabled": False}, "mid": {"effort": "low"}},
}

MAX_TOKENS = 8000
TOTAL_CAP = 16.00        # 主矩阵总硬上限
SMOKE_TOTAL_CAP = 1.50   # 冒烟总硬上限
SMOKE_LESSON = "r1-quadratic"
SMOKE_INTERRUPT = "r1-i1-seasons-distance"
