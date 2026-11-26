# Interactive widgets (experiment)

[English](INTERACTIVE.md) · [简体中文](INTERACTIVE.zh-CN.md)

> **Status: experiment.** Separate from the frozen v1 benchmark: the v1 prompt, operations, recordings, scores and
> leaderboard are unchanged, and none of the numbers below are part of them. The widgets are written by hand.
> The widget protocol is a draft ([`protocol/PROTOCOL-v1.1-widgets.md`](../protocol/PROTOCOL-v1.1-widgets.md)).

## The idea

In v1 the model writes absolute coordinates, and the most common failure is a figure that disagrees with its own
caption (a dot beside the intersection, a season label on the wrong Earth). A static drawing is also all the student
gets: they can only interrupt by typing.

A **widget** is a figure that the player draws and keeps consistent by itself. The model only chooses the kind and its
parameters; the player computes every coordinate, label, guide line and readout:

```json
{ "op": "widget", "id": "sd", "kind": "supply-demand",
  "params": { "show": ["axes", "demand", "supply", "equilibrium"], "demandShift": 2 },
  "expect": { "price": "up", "quantity": "up" } }
```

Because the figure is a function of a few parameters, the student can change those parameters by dragging, and the
result can be reported back to the model as a structured event.

## Background

Defining a figure as a function of a few parameters, and letting the student change those parameters by dragging, follows
*Declarative Dragging* (Joshua Horowitz, Andrew Blinn and Jeffrey Heer, UIST 2026;
[project page](https://declarative-dragging.github.io/), DOI 10.1145/3830398.3830556) and its library Dragology (MIT).
This repository uses none of their code. The widgets here are written by hand for two topics, and a drag simply maps the
pointer to one parameter.

## Try it

In the player, open one of the four **Interactive widgets (hand-written)** lessons:

| Lesson | What happens |
|---|---|
| Supply & demand: drag the curves | A six-step lesson; at the end drag the red or blue curve and watch the equilibrium, prices and quantities change |
| Supply & demand: predict the equilibrium | Two questions. The lesson pauses; drag a dot to where you think the new equilibrium is. Each wrong answer gets the explanation for that specific mistake |
| Seasons: drag the Earth | Drag the Earth around its orbit; the zoom shows where the Sun is overhead and how high it stands at noon at 40°N |
| Seasons: where is it summer? | Two questions ("summer in the north", "summer in the south"); the zoom stays hidden until the answer is right |

`?s=w2-predict-equilibrium.en` (and `w1-supply-demand.en`, `w3-seasons.en`, `w4-seasons-ask.en`) selects a lesson from
the URL. The feedback and the numbers are computed by code; no model is called.

## How it works

```
widget op ──expand──▶ ordinary v1 operations (coordinates computed by code)
                     └─ diffed against what is on the board:
                         new id       → drawn with the usual handwriting animation
                         changed spec → replaced in place (numeric params are tweened)
                         gone id      → removed
playback idle ──▶ the widget's handles become draggable
drag / answer  ──▶ one parameter changes → expand again; on release a structured event is recorded
```

- **v1 is untouched.** A widget lowers to `write` / `line` / `ellipse` / `path` operations, so the player, the linter
  and the recordings work as before. Exposing `widget` to a model is still a different condition from v1, which is why
  it has its own draft protocol and its own results folder.
- **Handles.** A handle is a region that maps the pointer to one parameter (a curve's shift, the Earth's position on its
  orbit, a dot's position). The widget decides the range and any snapping.
- **Questions.** A step with `ask` pauses the lesson. The student's answer is matched against a small set of expected
  answers (the right one and the typical mistakes), or against a region for continuous answers, and the matching
  explanation is shown. Nothing is sent to a model.
- **Events.** Each drag or answer is appended to `student_events` and reported by `getState()` together with the
  widget's current parameters and a state summary (the same "board state" that is sent when a student interrupts):

```json
{ "widget": "sd", "kind": "supply-demand", "event": "drag", "param": "demandShift", "from": 2, "to": -1.5,
  "state": { "demand_shift": -1.5, "supply_shift": 0, "equilibrium": { "price": 4.25, "quantity": 4.25 },
             "change": { "price": -0.75, "quantity": -0.75 } } }
```

- **Seasons are split into four quarter-turns** centred on the solstices and equinoxes (roughly June–August = summer in
  the north). The page says so. The orbit is drawn as a circle: the real Earth–Sun distance varies by about 3 %.

Files: `player/widgets/` (runtime and the two widgets), `scenarios/interactive.json` and `scenarios/widgets/` (the
lessons; a separate index so that `scenarios/index.json` is unchanged), `protocol/PROTOCOL-v1.1-widgets.md`.
The PDF preview does not support these lessons yet, so its button is disabled for them.

## Can a model drive it? A small run

**Setup** (everything is in this repository):

| | |
|---|---|
| Prompt | [`protocol/PROTOCOL-v1.1-widgets.md`](../protocol/PROTOCOL-v1.1-widgets.md), in English: the v1 protocol plus the `widget` operation, both widget kinds and one example, sent verbatim |
| Models | Claude Haiku 5.5, Gemini 3.8 Flash, Claude Sonnet 5.5, through OpenRouter pinned to the first-party providers, no fallback |
| Date and settings | 2026-11-26; low thinking; output cap 8,000 tokens; same runner conventions as v1 (`bench/run_widgets.py`) |
| Tasks | 6, each three times: a supply-and-demand lesson, a seasons lesson, a lesson with a quiz, a topic **no** widget covers (Pythagorean theorem), and two interruptions after the student dragged a widget |
| Sample | 54 calls (a 6-call smoke run is reused as repeat 1 of its tasks), **$0.37** in total |
| Review | Deterministic checks only (`bench/widget_check.py`): schema, the right widget (or none), the end state the task asks for, and whether the model's own `expect` agrees with the state its parameters produce. No human or model review |

**Results** (`results/widgets/summary.md` has the full tables, per-scenario figures and a list of the failures):

| Model | Parsed | Schema-valid | Right widget / none | Expected end state | `expect` agrees | `expect` missing | Spend |
|---|---|---|---|---|---|---|---|
| Claude Haiku 5.5 | 18/18 | 18/18 | 18/18 | 17/18 | 33/34 | 0/34 | $0.025 |
| Gemini 3.8 Flash | 18/18 | 18/18 | 18/18 | 18/18 | 42/42 | 6/48 | $0.085 |
| Claude Sonnet 5.5 | 18/18 | 18/18 | 18/18 | 18/18 | 51/51 | 0/51 | $0.257 |

- All nine runs on the uncovered topic fell back to ordinary operations; none forced a widget.
- All 36 lesson outputs replay in the player with no warnings and no linter errors.
- Against the v1 runs of the same models at low thinking (different prompt and scenarios, so for orientation only), the
  widget outputs were shorter: for the supply-and-demand lesson 3,709 → 1,198 output tokens (Haiku), 2,235 → 644
  (Gemini), 1,498 → 688 (Sonnet).
- Two failures: one Haiku run said "drag the demand curve back to where it started" but set the shift to −2 (its
  `expect` was consistent with that parameter, so only the end-state check caught it); another Haiku run declared the
  wrong season after a quiz.

**What this does not show**

- The checks do not read the narration. A step whose text disagrees with its parameters is caught only if `expect`
  disagrees too.
- Three models, two hand-written widgets, three repeats per task. It says nothing about other topics, other models, or a
  catalogue with many more widgets.
- The tasks are much easier than v1 (choose parameters instead of computing coordinates), so these numbers must not be
  compared with the v1 leaderboard.
- One checker rule was added after seeing the first results: after a quiz, an operation that sets `ask` to null without a
  position assumes the student answered correctly. It changed the verdict of one call and is noted in `summary.md`.
- Three interruption outputs were read by hand and answered what the student saw; that is a spot check, not a score.
- No student has used these lessons. Nothing here says that dragging helps people learn.

## Limitations

- Widgets are written and reviewed by hand, and every definition they rely on has to be written down once: the seasons
  widget uses one definition of "summer" for its readout and for judging the quiz, otherwise the two could disagree.
- Only two widgets exist; a general set of building blocks (axes, function lines, intersections, attached labels) would
  let a model compose figures, but it brings back the problem of getting the composition right.
- Dragging cost was measured on one desktop (median about 4 ms per pointer move for about 30 objects). Phones and slow
  machines were not tested, and neither was touch input. The board does not scroll the page while a finger is on it.
- The animation was checked through its end states and scripted drags, not by watching it in real time.
- Student edits that change the board itself (moving or deleting objects, undo) are a different question, tracked in
  [#3](https://github.com/molly554/whiteboard-ai-tutor/issues/3); the events above only describe widget parameters.

## Reproduce

```bash
python bench/run_widgets.py preflight --via openrouter           # free: keys, model ids, pinned providers
python bench/run_widgets.py smoke --via openrouter               # 6 calls, a few cents
python bench/run_widgets.py main --confirm --via openrouter --skip wsmoke   # 48 more calls, about $0.34
python bench/aggregate_widgets.py                                # results/widgets/summary.md
```

The runner has a hard total cap ($0.60) and per-model caps, and appends every call to `results/widgets/*.jsonl`.
`bench/mock_server.py` works here too (`WB_MOCK_BASE=http://127.0.0.1:8899`, `--phase wmock`) to test the plumbing for
free. Costs are the amounts OpenRouter reported for each call.

Related: [#7](https://github.com/molly554/whiteboard-ai-tutor/issues/7) proposes higher-level operations such as
`mark_intersection`. Widgets are a different route to the same failure (the player, not the model, computes positions
for a whole figure), so the two can be compared on the same scenarios.
