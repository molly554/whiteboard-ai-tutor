# Widget experiment — summary

Protocol v1.1 draft (`protocol/PROTOCOL-v1.1-widgets.md`), low thinking, via OpenRouter, pinned first-party providers.
54 calls with an answer (smoke run + main run).

Total spend on these calls: **$0.368**.

Checks were recomputed from the stored outputs with the final checker; 1 call(s) differ from what the runner printed live (see the note on quizzes below).

## Per model

| model | calls | parsed | schema-valid | right widget / no widget | expected end state | `expect` correct | `expect` missing | spend |
|---|---|---|---|---|---|---|---|---|
| haiku-5.5 | 18 | 18 | 18 | 18 | 17 | 33 / 34 | 0 / 34 | $0.025 |
| gemini-3.8-flash | 18 | 18 | 18 | 18 | 18 | 42 / 42 | 6 / 48 | $0.085 |
| sonnet-5.5 | 18 | 18 | 18 | 18 | 18 | 51 / 51 | 0 / 51 | $0.257 |

## Per model and scenario

Columns: calls, schema-valid, right widget (or none when the topic is uncovered), expected end state, `expect` wrong, first op (s, median), output tokens (median), cost per call (mean). The v1 columns are the old benchmark on the nearest scenario with the same model, low thinking.

| model | scenario | calls | schema | topic | state | expect wrong | first op s | out tok | $/call | v1 first op s | v1 out tok | v1 $/call |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-5.5 | lesson: demand rises | 3 | 3 | 3 | 2 | 0 | 6.6 | 1198 | $0.0009 | 15.0 | 3709 | $0.0021 |
| haiku-5.5 | lesson: seasons | 3 | 3 | 3 | 3 | 1 | 7.7 | 1757 | $0.0012 | 13.4 | 3293 | $0.0022 |
| haiku-5.5 | teach + quiz: supply falls | 3 | 3 | 3 | 3 | 0 | 10.2 | 1838 | $0.0013 | – | – | – |
| haiku-5.5 | uncovered topic: Pythagoras | 3 | 3 | 3 | 3 | 0 | 32.3 | 6827 | $0.0036 | 23.6 | 5717 | $0.0030 |
| haiku-5.5 | interruption: supply dragged | 3 | 3 | 3 | 3 | 0 | 6.0 | 566 | $0.0006 | 6.6 | 1312 | $0.0010 |
| haiku-5.5 | interruption: Earth dragged | 3 | 3 | 3 | 3 | 0 | 7.0 | 1046 | $0.0008 | 9.5 | 2040 | $0.0013 |
| gemini-3.8-flash | lesson: demand rises | 3 | 3 | 3 | 3 | 0 | 3.8 | 644 | $0.0038 | 3.3 | 2235 | $0.0090 |
| gemini-3.8-flash | lesson: seasons | 3 | 3 | 3 | 3 | 0 | 4.1 | 882 | $0.0049 | 3.1 | 1759 | $0.0076 |
| gemini-3.8-flash | teach + quiz: supply falls | 3 | 3 | 3 | 3 | 0 | 3.6 | 611 | $0.0039 | – | – | – |
| gemini-3.8-flash | uncovered topic: Pythagoras | 3 | 3 | 3 | 3 | 0 | 3.5 | 2265 | $0.0098 | 3.3 | 2478 | $0.0099 |
| gemini-3.8-flash | interruption: supply dragged | 3 | 3 | 3 | 3 | 0 | 4.2 | 360 | $0.0030 | 3.1 | 1030 | $0.0059 |
| gemini-3.8-flash | interruption: Earth dragged | 3 | 3 | 3 | 3 | 0 | 4.5 | 260 | $0.0031 | 3.3 | 1348 | $0.0067 |
| sonnet-5.5 | lesson: demand rises | 3 | 3 | 3 | 3 | 0 | 2.1 | 688 | $0.0129 | 2.5 | 1498 | $0.0174 |
| sonnet-5.5 | lesson: seasons | 3 | 3 | 3 | 3 | 0 | 3.5 | 815 | $0.0140 | 2.8 | 1342 | $0.0161 |
| sonnet-5.5 | teach + quiz: supply falls | 3 | 3 | 3 | 3 | 0 | 4.0 | 878 | $0.0147 | – | – | – |
| sonnet-5.5 | uncovered topic: Pythagoras | 3 | 3 | 3 | 3 | 0 | 3.5 | 1443 | $0.0202 | 2.8 | 1244 | $0.0152 |
| sonnet-5.5 | interruption: supply dragged | 3 | 3 | 3 | 3 | 0 | 2.7 | 473 | $0.0121 | 2.6 | 810 | $0.0153 |
| sonnet-5.5 | interruption: Earth dragged | 3 | 3 | 3 | 3 | 0 | 4.0 | 459 | $0.0119 | 2.5 | 899 | $0.0156 |

## Failures, listed

- `haiku-5.5` w-l1 #1: end state is not the one the scenario asks for
- `haiku-5.5` w-l2 #1: step 6 op 1: north said autumn, widget shows winter; sun_overhead said equator, widget shows south

## What this does not show

- The checks are deterministic: schema, widget choice, and whether the model's `expect` matches the state its own params produce. They do not read the narration, so a step whose text disagrees with its params is not caught unless `expect` also disagrees.
- After a quiz, an operation that sets `ask` to null without a position leaves the Earth wherever the student put it. The checker assumes a correct answer (the quiz's answer position); this rule was added after seeing the first results, because one run was marked wrong for a reasonable expectation.
- Three models, three repeats per scenario, six scenarios, two widget kinds written by hand: the numbers say nothing about other topics or other models.
- The v1 columns are for orientation only: a different prompt (English, longer), different scenarios and a much easier task (parameters instead of coordinates).
- No student has used any of the resulting boards.
