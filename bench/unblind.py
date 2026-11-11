"""Run only AFTER every blind score is on disk. Joins the scores with the id mapping, aggregates per model,
and regenerates the public pages:

  results/review/results.json        one row per reviewed board
  results/review/summary_review.md   tables (per model, per scenario, linter vs review, per board)
  results/leaderboard.json           review + latency + cost per model (feeds the charts)
  index.html / gallery.zh.html       gallery of every reviewed board (English / Chinese)
  audit.html                         the human-audit sheet
"""
import collections
import html
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "results", "review")
ORDER = ["gemini-4-argon", "haiku-5.5", "gemini-3.8-flash", "sonnet-5.5", "deepseek-v4-pro", "deepseek-flash"]
MODEL = {"sonnet-5.5": "Claude Sonnet 5.5", "haiku-5.5": "Claude Haiku 5.5", "gemini-4-argon": "Gemini 4 Argon",
         "gemini-3.8-flash": "Gemini 3.8 Flash", "deepseek-v4-pro": "DeepSeek V4 Pro", "deepseek-flash": "DeepSeek V4.1 Flash"}
SC_ORDER = ["r1-seasons", "r1-pythagoras", "r1-quadratic", "r1-supply-demand", "r1-photosynthesis",
            "r1-i1-seasons-distance", "r1-i2-demand-simpler", "r1-i3-arrow-meaning"]
SC = {"en": dict(zip(SC_ORDER, ["Seasons", "Pythagoras", "Quadratic", "Supply & demand", "Photosynthesis (zh)",
                                "Interrupt 1 · seasons", "Interrupt 2 · supply & demand", "Interrupt 3 · arrow"])),
      "zh": dict(zip(SC_ORDER, ["四季", "勾股定理", "解方程", "供需曲线", "光合作用", "打断1 四季", "打断2 供需", "打断3 箭头"]))}

scores = {}
for n in range(1, 10):
    p = os.path.join(REV, "scores-%d.json" % n)
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding="utf-8"))
    for k, v in d.items():
        if k.startswith("B"):
            scores[k] = v
    for k, v in (d.get("_corrections") or {}).items():
        scores[k].update(v)
zh = json.load(open(os.path.join(REV, "notes-zh.json"), encoding="utf-8"))
mapping = json.load(open(os.path.join(REV, "mapping.json"), encoding="utf-8"))
no_output = json.load(open(os.path.join(REV, "no_output.json"), encoding="utf-8"))
assert set(scores) == set(mapping)

rows = []
for bid, m in mapping.items():
    s = dict(scores[bid])
    note_en = s.pop("note")
    kind = "interrupt" if "-i" in m["scenario"] else "lesson"
    base = s["content"] == 1 and s["match"] == 1 and s["layout"] >= 1 and (kind == "lesson" or s.get("answers") == 1)
    rows.append(dict(id=bid, kind=kind, lenient=base, strict=base and not s.get("borderline"),
                     note_en=note_en, note_zh=zh.get(bid, note_en), **m, **s))
json.dump(rows, open(os.path.join(REV, "results.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)


def verdict(r):
    return "borderline" if (r["lenient"] and not r["strict"]) else ("pass" if r["lenient"] else "fail")


# ───────── leaderboard.json: review + latency + cost (low-thinking lessons) ─────────
runs = []
for ph in ("main-or", "main-ds"):
    runs += [json.loads(l) for l in open(os.path.join(ROOT, "results", "runs", ph + ".jsonl"), encoding="utf-8") if l.strip()]


def pct(v, q):
    v = sorted(v)
    k = (len(v) - 1) * q
    f, c = int(k), min(int(k) + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


board = []
for m in ORDER:
    sel = [r for r in rows if r["model"] == m]
    low = [r for r in runs if r["model"] == m and r["cond"] == "low"]
    les = [r for r in low if r["kind"] == "lesson"]
    itr = [r for r in low if r["kind"] == "interrupt"]
    fo = lambda L: [r["t"]["first_op"] for r in L if r["t"].get("first_op") is not None]
    board.append(dict(
        model=m, name=MODEL[m], boards=len(sel), passed=sum(r["lenient"] for r in sel), passed_strict=sum(r["strict"] for r in sel),
        mismatch=sum(1 for r in sel if r["match"] == 0), layout_mean=round(sum(r["layout"] for r in sel) / len(sel), 2),
        first_stroke_lesson_p50=round(pct(fo(les), .5), 1), first_stroke_lesson_p90=round(pct(fo(les), .9), 1),
        first_stroke_interrupt_p50=round(pct(fo(itr), .5), 1), total_lesson_p50=round(pct([r["t"]["end"] for r in les], .5), 1),
        cost_lesson=round(sum(r["cost"] for r in les) / len(les), 4), cost_interrupt=round(sum(r["cost"] for r in itr) / len(itr), 4),
        parsed_low=sum(1 for r in low if r["parse_ok"]), calls_low=len(low)))
json.dump(board, open(os.path.join(ROOT, "results", "leaderboard.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ───────── summary_review.md ─────────
out = ["# Blind review summary", "", "## Per model and thinking condition", "",
       "| model | thinking | boards | pass (lenient / strict) | content or figure wrong | figure contradicts text | layout 0 | layout mean (0-2) | incomplete | interruptions: overwrote or wiped the board |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for m in ORDER:
    for c in ("low", "mid"):
        sel = [r for r in rows if r["model"] == m and r["cond"] == c]
        if not sel:
            continue
        it = [r for r in sel if r["kind"] == "interrupt"]
        miss = sum(1 for x in no_output if x["model"] == m and x["cond"] == c)
        out.append("| %s | %s | %d%s | %d / %d | %d | %d | %d | %.2f | %d | %d / %d |" % (
            MODEL[m], c, len(sel), (" (+%d cell with no usable output)" % miss) if miss else "",
            sum(r["lenient"] for r in sel), sum(r["strict"] for r in sel), sum(1 for r in sel if r["content"] == 0),
            sum(1 for r in sel if r["match"] == 0), sum(1 for r in sel if r["layout"] == 0),
            sum(r["layout"] for r in sel) / len(sel), sum(1 for r in sel if r["pedagogy"] == 0),
            sum(1 for r in it if r.get("placement") == 0), len(it)))
out += ["", "## Low thinking, per scenario (one board per cell)", "",
        "| model | " + " | ".join(SC["en"][s] for s in SC_ORDER) + " |", "|---|" + "---|" * len(SC_ORDER)]
MARK = {"pass": "✓", "borderline": "△", "fail": "✗"}
for m in ORDER:
    cells = []
    for sc in SC_ORDER:
        r = [x for x in rows if x["model"] == m and x["cond"] == "low" and x["scenario"] == sc]
        cells.append(MARK[verdict(r[0])] if r else "-")
    out.append("| %s | %s |" % (MODEL[m], " | ".join(cells)))
tp = sum(1 for r in rows if r["hard_n"] == 0 and r["lenient"])
fp = sum(1 for r in rows if r["hard_n"] == 0 and not r["lenient"])
fn = sum(1 for r in rows if r["hard_n"] > 0 and r["lenient"])
tn = sum(1 for r in rows if r["hard_n"] > 0 and not r["lenient"])
out += ["", "## Linter (zero hard errors) vs blind review (lenient pass)", "", "| | review: pass | review: fail |", "|---|---|---|",
        "| linter: clean | %d | %d |" % (tp, fp), "| linter: hard errors | %d | %d |" % (fn, tn)]
out += ["", "## Every board", "",
        "| id | model | thinking | scenario | content | match | layout | complete | answers | placement | verdict | reviewer confidence | note |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in sorted(rows, key=lambda r: (ORDER.index(r["model"]), r["cond"], SC_ORDER.index(r["scenario"]))):
    out.append("| %s | %s | %s | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s |" % (
        r["id"], MODEL[r["model"]], r["cond"], SC["en"][r["scenario"]], r["content"], r["match"], r["layout"], r["pedagogy"],
        r.get("answers", "-"), r.get("placement", "-"), verdict(r), r["conf"], r["note_en"]))
open(os.path.join(REV, "summary_review.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("\n".join(out[2:out.index("## Every board")]))

# ───────── human-audit sample: every low-confidence or borderline board + one pass and one fail per model ─────────
rnd = random.Random(20261112)
audit = [r for r in rows if r["conf"] == "low" or r.get("borderline")]
for m in ["sonnet-5.5", "haiku-5.5", "gemini-4-argon", "gemini-3.8-flash", "deepseek-v4-pro", "deepseek-flash"]:
    for want in (True, False):
        pool = [r for r in rows if r["model"] == m and r["lenient"] == want and r not in audit]
        if pool:
            audit.append(rnd.choice(pool))
audit = audit[:20]
rnd.shuffle(audit)
json.dump([r["id"] for r in audit], open(os.path.join(REV, "audit_ids.json"), "w", encoding="utf-8", newline="\n"))

# ───────── pages ─────────
Q = {e["id"]: e["question"] for e in json.load(open(os.path.join(ROOT, "scenarios", "index.json"), encoding="utf-8"))["scripts"]}
T = {"en": dict(title="Whiteboard AI Tutor · LLM benchmark gallery (Claude, Gemini, DeepSeek)", h1="Whiteboard AI Tutor — every reviewed board",
                lead="One frozen prompt, six models, eight teaching scenarios. Each card is a board exactly as the model drew it. "
                     "Click a board to watch it being written. Verdicts come from a blind review (model names hidden until scoring was done).",
                board="Leaderboard", m="Model", p="Blind review: pass", fs="First stroke (lesson, p50)", c="Cost per lesson",
                sec="{name} — {p} of {n} boards pass", verdicts={"pass": "pass", "borderline": "borderline", "fail": "fail"},
                q="Question", rub="content {c} · figure matches text {m} · layout {l}/2 · complete {p}",
                rub_i=" · answers the student {a} · keeps the board intact {pl}", play="▶ watch it being written",
                think={"low": "low thinking", "mid": "medium thinking"}, other='<a href="gallery.zh.html">中文</a>',
                audit_h1="Human audit sheet ({n} boards)",
                audit_lead="Below each board is the reviewer model's verdict. Note the ids of the boards where you disagree. "
                           "Model names are folded so you can judge blind.", reveal="which model?", foot="Data, code and method: see the README in the repository."),
     "zh": dict(title="白板 AI 导师评测 · 全部评审板（Claude、Gemini、DeepSeek）", h1="Whiteboard AI Tutor · 白板 AI 导师 —— 全部评审板",
                lead="同一份冻结的提示词，六个模型，八个教学场景。每张卡片是模型原样画出的板书，点击可以看书写过程。结论来自盲评（打分完成前看不到模型名）。",
                board="排行榜", m="模型", p="盲评通过", fs="第一笔（讲解，p50）", c="单个知识点成本",
                sec="{name} —— {n} 块里通过 {p} 块", verdicts={"pass": "通过", "borderline": "边界", "fail": "不通过"},
                q="问题", rub="内容无错 {c} · 图文一致 {m} · 版面 {l}/2 · 讲解完整 {p}",
                rub_i=" · 回答了问题 {a} · 没有乱放或擦掉整板 {pl}", play="▶ 看书写过程",
                think={"low": "低思考", "mid": "中思考"}, other='<a href="index.html">English</a>',
                audit_h1="", audit_lead="", reveal="", foot="数据、代码和方法见仓库 README。")}
CSS = """:root{color-scheme:light}body{font-family:-apple-system,'Segoe UI','Microsoft YaHei',Helvetica,Arial,sans-serif;background:#f3f1ec;margin:0;color:#1c1c1b}
.wrap{max-width:1500px;margin:0 auto;padding:26px 24px 60px}h1{font-size:26px;margin:0 0 6px}h2{font-size:18px;margin:34px 0 10px}
.lead{color:#52514e;max-width:900px;line-height:1.55}.top{display:flex;justify-content:space-between;align-items:baseline;gap:16px}
table.lb{border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px #0001;margin-top:8px}
table.lb th,table.lb td{padding:8px 16px;text-align:left;border-bottom:1px solid #eeece7;font-size:14px}table.lb td.n{text-align:right;font-variant-numeric:tabular-nums}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:14px}
.card{background:#fff;border-radius:10px;padding:12px;box-shadow:0 1px 4px #0002}.card img{width:100%;aspect-ratio:16/9;border:1px solid #e4e2dc;border-radius:6px;display:block}
.meta{font-size:13px;margin:7px 0 3px}.small{font-size:12px;color:#66655f;margin:3px 0}.note{font-size:13px;line-height:1.45;margin:6px 0 4px}
.v{display:inline-block;padding:1px 8px;border-radius:9px;font-size:12px;font-weight:600}.v.pass{background:#e2f3e6;color:#1d6a35}.v.fail{background:#fde7e7;color:#9b1c1c}.v.borderline{background:#fbf0cf;color:#7a5c00}
a{color:#1f4fd8;text-decoration:none}a:hover{text-decoration:underline}details{display:inline}"""


def card(r, lang, reveal=True):
    t = T[lang]
    play = "player/?run=%s&sc=%s" % (r["run_id"], r["scenario"])
    v = verdict(r)
    who = "%s · %s" % (MODEL[r["model"]], t["think"][r["cond"]])
    if not reveal:
        who = "<details><summary>%s</summary>%s</details>" % (t["reveal"], who)
    rub = t["rub"].format(c=r["content"], m=r["match"], l=r["layout"], p=r["pedagogy"])
    if r["kind"] == "interrupt":
        rub += t["rub_i"].format(a=r.get("answers"), pl=r.get("placement"))
    return ('<div class="card"><div class="meta"><b>%s</b> · %s <span class="v %s">%s</span></div><div class="small">%s: %s</div>'
            '<a href="%s"><img src="results/review/boards/%s.png" alt="%s"></a><div class="note">%s</div>'
            '<div class="small">%s</div><div class="small">%s · <a href="%s">%s</a></div></div>') % (
        r["id"], SC[lang][r["scenario"]], v, t["verdicts"][v], t["q"], html.escape(Q.get(r["scenario"], "")), play, r["id"],
        html.escape(SC[lang][r["scenario"]]), html.escape(r["note_" + lang]), rub, who, play, t["play"])


def gallery(lang, fname):
    t = T[lang]
    desc = {"en": "Open-source AI tutor that teaches on a whiteboard: it writes, draws, erases and takes interruptions. "
                  "Benchmark of Claude, Gemini and DeepSeek on 288 lessons, blind-reviewed. Replay every board.",
            "zh": "开源的白板 AI 导师：边讲边写字、画图、擦除，可以被打断。Claude、Gemini、DeepSeek 六个模型 288 节课的评测，盲评打分，每块板都能重放。"}[lang]
    p = ['<!DOCTYPE html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
         '<meta name="description" content="%s"><title>%s</title><style>%s</style></head><body><div class="wrap">' % (lang, desc, t["title"], CSS),
         '<div class="top"><h1>%s</h1><div>%s</div></div><p class="lead">%s</p>' % (t["h1"], t["other"], t["lead"]),
         '<h2>%s</h2><table class="lb"><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (t["board"], t["m"], t["p"], t["fs"], t["c"])]
    for b in board:
        p.append('<tr><td><a href="#%s">%s</a></td><td class="n">%d / %d</td><td class="n">%.1f s</td><td class="n">$%.4f</td></tr>' % (
            b["model"], b["name"], b["passed"], b["boards"], b["first_stroke_lesson_p50"], b["cost_lesson"]))
    p.append("</table>")
    for m in ORDER:
        sel = sorted([r for r in rows if r["model"] == m], key=lambda r: (r["cond"], SC_ORDER.index(r["scenario"])))
        p.append('<h2 id="%s">%s</h2><div class="grid">' % (m, t["sec"].format(name=MODEL[m], p=sum(r["lenient"] for r in sel), n=len(sel))))
        p += [card(r, lang) for r in sel] + ["</div>"]
    p.append('<p class="small" style="margin-top:30px">%s</p></div></body></html>' % t["foot"])
    open(os.path.join(ROOT, fname), "w", encoding="utf-8", newline="\n").write("\n".join(p))


gallery("en", "index.html")
gallery("zh", "gallery.zh.html")
t = T["en"]
p = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
     '<title>Whiteboard AI Tutor · human audit sheet</title><style>%s</style></head><body><div class="wrap">' % CSS,
     "<h1>%s</h1><p class='lead'>%s</p><div class='grid'>" % (t["audit_h1"].format(n=len(audit)), t["audit_lead"])]
p += [card(r, "en", reveal=False) for r in audit] + ["</div></div></body></html>"]
open(os.path.join(ROOT, "audit.html"), "w", encoding="utf-8", newline="\n").write("\n".join(p))
print("\nwrote index.html, gallery.zh.html, audit.html, results/leaderboard.json  (audit boards: %d)" % len(audit))
