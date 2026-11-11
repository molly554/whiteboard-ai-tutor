# Method

How the numbers in the README were produced, and how to reproduce or extend them.

## 1. What was run

| | |
|---|---|
| Models | Claude Sonnet 5.5, Claude Haiku 5.5, Gemini 4 Argon, Gemini 3.8 Flash, DeepSeek V4 Pro, DeepSeek V4.1 Flash |
| Thinking | two settings per model: "low" and "mid" |
| Scenarios | 5 lessons + 3 interruptions |
| Repeats | 3 per model × setting × scenario → 288 calls, random order |
| Prompt | [`protocol/PROTOCOL.md`](../protocol/PROTOCOL.md) verbatim as the system prompt; the question as the user message |
| Output | streamed plain-text JSON; no JSON mode, structured output or tool calling; 8,000 max tokens including thinking |
| Route | Claude and Gemini through OpenRouter, pinned to the first-party provider with fallback disabled; DeepSeek direct |
| Date | 2026-11-11 |

What "low" and "mid" mean per vendor:

| Vendor | low | mid |
|---|---|---|
| Claude (via OpenRouter) | `reasoning.effort = low` | `reasoning.effort = medium` |
| Gemini (via OpenRouter) | `reasoning.effort = low` | `reasoning.effort = medium` |
| DeepSeek (direct) | thinking disabled, temperature 0.7 | thinking enabled, `reasoning_effort = low` |

These are not equal amounts of thinking. Measured thinking tokens per call at "low": Sonnet 0, Gemini 0 (reported),
DeepSeek 0, Haiku about 1,700. Gemini 4 Argon reported 0 thinking tokens on both settings and behaved the same on both.

### Scenarios

| id | kind | input |
|---|---|---|
| `r1-seasons` | lesson | "Why do we have seasons?" |
| `r1-pythagoras` | lesson | "Why does the Pythagorean theorem work?" |
| `r1-quadratic` | lesson | "Solve x² − 5x + 6 = 0. (Switch to a simpler method midway.)" |
| `r1-supply-demand` | lesson | "What happens to the price when demand rises?" |
| `r1-photosynthesis` | lesson | the same kind of question, asked in Chinese |
| `r1-i1-seasons-distance` | interruption | after step 3 of the seasons lesson: "in northern summer, isn't Earth farther from the Sun?" |
| `r1-i2-demand-simpler` | interruption | after step 5 of the supply-and-demand lesson: "can you show it a simpler way?" |
| `r1-i3-arrow-meaning` | interruption | same board: "what does this arrow mean?" (pointing at one object by id) |

For interruptions every model receives the **same** prior board: a fixed lesson script as the previous assistant
turn, and the board state exported by the player (`scenarios/state-i1.json`, `state-i2.json`). The prior lessons in
`scenarios/` were written once, by Claude Sonnet 5.5, before the benchmark.

## 2. What is recorded per call

`results/runs/*.jsonl`, one line per call:

- timings from request start: first event, first text token, **first complete drawing operation** (`first_op`), end
- token usage (input, output, thinking), and cost — the amount OpenRouter actually charged, or list price × usage for DeepSeek
- the raw output, whether it parsed, protocol violations per operation, stop reason

`first_op` is found by scanning the stream for the first closed JSON object at nesting depth 3
(root → step → operation). It is the moment a client could draw its first stroke.

## 3. Automatic checks

- **Parse.** The output must contain one JSON object (a code fence is tolerated). No repair, no retry.
- **Protocol.** Each operation is validated against section 4 of the protocol. An invalid operation is skipped by the
  player; if all are invalid the board stays blank.
- **Linter** (in the player): object leaves the board, text overlaps text, text crossed by a stroke, duplicate id,
  erase of a missing id, empty path. It replays erases, so it checks what is on the board at each moment.

The linter is a coarse filter only. Compared with the blind review on the 64 sampled boards:

| | review: pass | review: fail |
|---|---|---|
| linter: clean | 18 | 5 |
| linter: hard errors | 26 | 15 |

## 4. Blind review

1. **Sample.** For each model × scenario at low thinking, take the repeat whose linter hard-error count is the median
   of the three (48 boards). At mid thinking do the same for seasons, supply-and-demand and interruption 2 (16 boards;
   two cells had no parsable output). `python bench/aggregate.py --blind` draws the sample and writes
   `results/review/mapping.json` (random id → run) and `render_list.json`.
2. **Render.** The player draws each finished board to a 1280 × 720 PNG named by its random id.
3. **Review blind.** `python bench/blind_view.py <scenario>` prints only the random ids and each board's narration.
   The reviewer reads the image and the narration and scores:

   | field | values | meaning |
   |---|---|---|
   | `content` | 0 / 1 | no scientific or mathematical error on the board (0 also for a blank board) |
   | `match` | 0 / 1 | the figure agrees with the text and labels |
   | `layout` | 0 / 1 / 2 | 2 clean · 1 visible overlap or misplacement but readable · 0 unreadable or covered |
   | `pedagogy` | 0 / 1 | complete and sensibly paced |
   | `answers` | 0 / 1 | interruptions: the student's question is answered |
   | `placement` | 0 / 1 | interruptions: nothing existing is overwritten and the board is not wiped |
   | `conf` | high / low | reviewer confidence |
   | `borderline` | flag | a marked point is 20–35 px (at 1280 px width) off the true intersection |

   Pass = `content` 1, `match` 1, `layout` ≥ 1 (and `answers` 1 for interruptions). "Lenient" counts borderline
   boards as pass, "strict" as fail.
4. **Scores to disk first.** `results/review/scores-1.json` … `scores-4.json` were written before the mapping was
   opened. `scores-5.json` holds three corrections made after looking at six boards just before their largest erase
   (`python bench/blind_pre.py`), still before unblinding.
5. **Unblind.** `python bench/unblind.py` joins scores and mapping and regenerates the tables, `index.html` and
   `audit.html`.
6. **Human audit.** `audit.html` shows 18 boards: all low-confidence or borderline ones, plus one random pass and
   one random fail per model. The audit has not been carried out yet; treat the review as provisional.

Reviewer: Claude Fable 5.2. It was not one of the tested models, but it comes from the same vendor as two of them.
Geometry was checked from pixel positions in the rendered image (for example, whether the marked equilibrium lies on
the intersection of the two drawn lines, or which way a drawn axis leans relative to the Sun).

## 5. Reproduce

```bash
python serve.py                                   # player, linter and gallery at http://localhost:8811/
pip install -r requirements.txt

python bench/run.py preflight --via openrouter    # free
python bench/run.py smoke --via openrouter
python bench/run.py main --confirm --via openrouter --phase main-or --models haiku-5.5,sonnet-5.5,gemini-4-argon,gemini-3.8-flash
python bench/run.py main --confirm --via openrouter --phase main-ds --models deepseek-flash,deepseek-v4-pro
```

Lint every run (browser console on `http://localhost:8811/player/`):

```js
await __wb.lintToFile(['main-or'], 'lint/lint-main-or.json');
await __wb.lintToFile(['main-ds'], 'lint/lint-main-ds.json');
```

Aggregate, sample, render, review, unblind:

```bash
python bench/aggregate.py --blind                 # tables + blind sample
```
```js
await __wb.renderFromFile('results/review/render_list.json', 'review/boards');
```
```bash
python bench/blind_view.py                        # ids per scenario
python bench/blind_view.py r1-seasons             # narration, no model names
#   ... write results/review/scores-N.json ...
python bench/unblind.py                           # tables, gallery, audit sheet, leaderboard.json
python bench/stats.py                             # lesson vs interruption latency and cost
python bench/make_charts.py                       # docs/assets/leaderboard-*.svg
```

README animations:

```js
await __wb.captureRun('<run id>', '<scenario id>', 'hero', {dt: 450, w: 800});
```
```bash
python bench/make_apng.py hero docs/assets/hero.png 3
```

## 6. Add a model or a scenario

- **Model:** add an entry to `MODELS` in `bench/config.py` (vendor, model id, list prices, the two thinking settings,
  budget caps) and, for OpenRouter, to `OR_ROUTE`. A new vendor needs a request builder and a stream parser in
  `bench/providers.py`.
- **Scenario:** add an entry to `scenarios/index.json`. An interruption also needs the prior lesson script, the step
  it interrupts, and a board state exported from the player ("Export board state").

## 7. Cost

| | USD |
|---|---|
| Main matrix, 288 calls | 3.84 |
| Smoke tests | 0.99 |
| **Total** | **4.83** |

Per model in the main matrix: Gemini 4 Argon 1.18, Claude Sonnet 5.5 0.89, Gemini 3.8 Flash 0.75, DeepSeek V4 Pro 0.72,
DeepSeek V4.1 Flash 0.21, Claude Haiku 5.5 0.09. OpenRouter charged exactly list price × usage.
