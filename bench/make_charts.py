"""Draw the README leaderboard chart from results/leaderboard.json.

Three small ranked-bar panels that share one row order (blind-review pass share, time to first stroke,
cost per lesson). One hue, every bar labelled at its tip, light and dark variants.
Output: docs/assets/leaderboard-light.svg and leaderboard-dark.svg
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
THEMES = {
    "light": dict(surface="#fcfcfb", text="#0b0b0b", text2="#52514e", bar="#2a78d6", hair="#dedcd6"),
    "dark": dict(surface="#1a1a19", text="#f0efec", text2="#c3c2b7", bar="#3987e5", hair="#3a3a37"),
}
FONT = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
W, H = 900, 400
ROW0, ROWH, BARH, MAXW = 104, 42, 18, 150


def bar(x0, y, w, color, tip):
    w = max(w, 2)
    r = min(4, w)
    d = "M%.1f %.1f H%.1f Q%.1f %.1f %.1f %.1f V%.1f Q%.1f %.1f %.1f %.1f H%.1f Z" % (
        x0, y, x0 + w - r, x0 + w, y, x0 + w, y + r, y + BARH - r, x0 + w, y + BARH, x0 + w - r, y + BARH, x0)
    return '<path d="%s" fill="%s"><title>%s</title></path>' % (d, color, tip)


def draw(board, t):
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
         'aria-label="Whiteboard AI Tutor leaderboard: blind-review pass share, time to first stroke and cost per lesson for six models">' % (W, H, W, H),
         '<rect width="%d" height="%d" rx="12" fill="%s"/>' % (W, H, t["surface"]),
         '<g font-family="%s">' % FONT]
    panels = [
        (175, "Blind review: boards passed", "of the boards reviewed per model",
         lambda b: b["passed"] / b["boards"], lambda b: "%d / %d" % (b["passed"], b["boards"]), 1.0),
        (420, "Time to first stroke", "lesson, median, seconds · lower is better",
         lambda b: b["first_stroke_lesson_p50"], lambda b: "%.1f s" % b["first_stroke_lesson_p50"], 14.0),
        (665, "Cost per lesson", "US dollars, one generation · lower is better",
         lambda b: b["cost_lesson"], lambda b: "$%.4f" % b["cost_lesson"], 0.03),
    ]
    for x0, title, sub, val, lab, vmax in panels:
        o.append('<text x="%d" y="44" font-size="14" font-weight="600" fill="%s">%s</text>' % (x0, t["text"], title))
        o.append('<text x="%d" y="63" font-size="11.5" fill="%s">%s</text>' % (x0, t["text2"], sub))
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>' % (
            x0, ROW0 - 8, x0, ROW0 + ROWH * len(board) - 8, t["hair"]))
        for i, b in enumerate(board):
            y = ROW0 + i * ROWH
            w = MAXW * min(1.0, val(b) / vmax)
            o.append(bar(x0, y, w, t["bar"], "%s: %s" % (b["name"], lab(b))))
            o.append('<text x="%.1f" y="%.1f" font-size="13" fill="%s">%s</text>' % (x0 + max(w, 2) + 8, y + 13.5, t["text"], lab(b)))
    for i, b in enumerate(board):
        o.append('<text x="20" y="%.1f" font-size="14" fill="%s">%s</text>' % (ROW0 + i * ROWH + 14, t["text"], b["name"]))
    o.append('<text x="20" y="%d" font-size="11.5" fill="%s">Low-thinking setting · 288 API calls · blind review by Claude Fable 5.2 of 64 boards · small sample, see Limitations</text>' % (
        H - 22, t["text2"]))
    o.append("</g></svg>")
    return "\n".join(o) + "\n"


def main():
    board = json.load(open(os.path.join(ROOT, "results", "leaderboard.json"), encoding="utf-8"))
    os.makedirs(os.path.join(ROOT, "docs", "assets"), exist_ok=True)
    for name, t in THEMES.items():
        p = os.path.join(ROOT, "docs", "assets", "leaderboard-%s.svg" % name)
        open(p, "w", encoding="utf-8", newline="\n").write(draw(board, t))
        print("wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
