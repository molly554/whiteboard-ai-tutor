# Blind review summary

## Per model and thinking condition

| model | thinking | boards | pass (lenient / strict) | content or figure wrong | figure contradicts text | layout 0 | layout mean (0-2) | incomplete | interruptions: overwrote or wiped the board |
|---|---|---|---|---|---|---|---|---|---|
| Gemini 4 Argon | low | 8 | 8 / 8 | 0 | 0 | 0 | 1.62 | 0 | 1 / 3 |
| Gemini 4 Argon | mid | 3 | 3 / 3 | 0 | 0 | 0 | 1.67 | 0 | 0 / 1 |
| Claude Haiku 5.5 | low | 8 | 6 / 6 | 1 | 2 | 0 | 1.62 | 1 | 1 / 3 |
| Claude Haiku 5.5 | mid | 3 | 3 / 3 | 0 | 0 | 0 | 1.67 | 0 | 0 / 1 |
| Gemini 3.8 Flash | low | 8 | 5 / 5 | 0 | 3 | 1 | 1.25 | 0 | 2 / 3 |
| Gemini 3.8 Flash | mid | 3 | 3 / 3 | 0 | 0 | 0 | 1.67 | 0 | 0 / 1 |
| Claude Sonnet 5.5 | low | 8 | 6 / 4 | 0 | 2 | 0 | 1.88 | 0 | 1 / 3 |
| Claude Sonnet 5.5 | mid | 3 | 1 / 1 | 0 | 2 | 0 | 2.00 | 0 | 1 / 1 |
| DeepSeek V4 Pro | low | 8 | 3 / 2 | 2 | 4 | 5 | 0.50 | 3 | 3 / 3 |
| DeepSeek V4 Pro | mid | 2 (+1 cell with no usable output) | 2 / 2 | 0 | 0 | 0 | 1.50 | 1 | 0 / 1 |
| DeepSeek V4.1 Flash | low | 8 | 2 / 2 | 3 | 5 | 4 | 0.50 | 4 | 2 / 3 |
| DeepSeek V4.1 Flash | mid | 2 (+1 cell with no usable output) | 2 / 2 | 0 | 0 | 0 | 1.50 | 0 | 0 / 1 |

## Low thinking, per scenario (one board per cell)

| model | Seasons | Pythagoras | Quadratic | Supply & demand | Photosynthesis (zh) | Interrupt 1 · seasons | Interrupt 2 · supply & demand | Interrupt 3 · arrow |
|---|---|---|---|---|---|---|---|---|
| Gemini 4 Argon | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Claude Haiku 5.5 | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Gemini 3.8 Flash | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ |
| Claude Sonnet 5.5 | ✗ | ✓ | ✓ | △ | ✓ | ✗ | ✓ | △ |
| DeepSeek V4 Pro | ✗ | ✗ | ✓ | △ | ✓ | ✗ | ✗ | ✗ |
| DeepSeek V4.1 Flash | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ |

## Linter (zero hard errors) vs blind review (lenient pass)

| | review: pass | review: fail |
|---|---|---|
| linter: clean | 18 | 5 |
| linter: hard errors | 26 | 15 |

## Every board

| id | model | thinking | scenario | content | match | layout | complete | answers | placement | verdict | reviewer confidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B24 | Gemini 4 Argon | low | Seasons | 1 | 1 | 2 | 1 | - | - | pass | high | June/December tilt consistent, plus direct vs low-angle panel and summary |
| B62 | Gemini 4 Argon | low | Pythagoras | 1 | 1 | 2 | 1 | - | - | pass | high | two-arrangement proof, geometry and labels exact |
| B10 | Gemini 4 Argon | low | Quadratic | 1 | 1 | 2 | 1 | - | - | pass | high | completing the square tried, erased, then factoring; clean |
| B13 | Gemini 4 Argon | low | Supply & demand | 1 | 1 | 1 | 1 | - | - | pass | high | both equilibria exact; conclusion text slightly overflows its box |
| B46 | Gemini 4 Argon | low | Photosynthesis (zh) | 1 | 1 | 1 | 1 | - | - | pass | high | richest content (cell -> zoom -> light and dark reactions, inputs and outputs, prokaryote exception); title area overlapped by two labels |
| B44 | Gemini 4 Argon | low | Interrupt 1 · seasons | 1 | 1 | 2 | 1 | 1 | 0 | pass | high | best answer: 147 vs 152 million km = 3%, then angle and day length; but it wiped the existing orbit diagram to do it |
| B42 | Gemini 4 Argon | low | Interrupt 2 · supply & demand | 1 | 1 | 2 | 1 | 1 | 1 | pass | high | cold vs hot day with numbers (50 then 80 cups), same-price point and E2 exact |
| B11 | Gemini 4 Argon | low | Interrupt 3 · arrow | 1 | 1 | 1 | 1 | 1 | 1 | pass | high | E2 and the same-price point Q' both exact; shows the shortage at P1; one label crossed by D1 |
| B55 | Gemini 4 Argon | mid | Seasons | 1 | 1 | 2 | 1 | - | - | pass | high | final board: two clean panels, toward vs away; the four-position orbit diagram shown before the erase is consistent |
| B07 | Gemini 4 Argon | mid | Supply & demand | 1 | 1 | 1 | 1 | - | - | pass | high | both equilibria on the crossings; conclusion text overflows its box and the board edge |
| B41 | Gemini 4 Argon | mid | Interrupt 2 · supply & demand | 1 | 1 | 2 | 1 | 1 | 1 | pass | high | ice-cream example tied to the chart: same-price point and E2 exact, result stated |
| B04 | Claude Haiku 5.5 | low | Seasons | 0 | 0 | 2 | 0 | - | - | fail | high | the Sun is drawn outside Earth's orbit; both Earth positions tilt the same way relative to the Sun, so summer vs winter is never shown; no title |
| B01 | Claude Haiku 5.5 | low | Pythagoras | 1 | 1 | 2 | 1 | - | - | pass | low | board proof valid; narration step 3 says the tilted square has side c 'by the relation we want to show' (circular wording) |
| B18 | Claude Haiku 5.5 | low | Quadratic | 1 | 1 | 2 | 1 | - | - | pass | high | formula -> discriminant 1 -> switch to factoring; includes check |
| B58 | Claude Haiku 5.5 | low | Supply & demand | 1 | 1 | 1 | 1 | - | - | pass | high | both equilibria exact; Price label crossed by the axis arrow; last line close to the bottom edge |
| B26 | Claude Haiku 5.5 | low | Photosynthesis (zh) | 1 | 1 | 1 | 1 | - | - | pass | high | correct but thin (4 steps); cell label sits on the outline, arrow runs through another chloroplast |
| B17 | Claude Haiku 5.5 | low | Interrupt 1 · seasons | 1 | 1 | 2 | 1 | 1 | 0 | pass | high | wiped the whole orbit diagram and drew a new zoomed Earth; correct and clean, answer about July given in narration only |
| B59 | Claude Haiku 5.5 | low | Interrupt 2 · supply & demand | 1 | 1 | 1 | 1 | 1 | 1 | pass | high | fixed-price line with both points exact; D2 redrawn further right; a label crossed by D2; narration mentions a point B that is not labelled |
| B05 | Claude Haiku 5.5 | low | Interrupt 3 · arrow | 1 | 0 | 2 | 1 | 1 | 1 | fail | high | explanation right, but E2 is marked on the supply line far beyond the D2-S crossing |
| B36 | Claude Haiku 5.5 | mid | Seasons | 1 | 1 | 2 | 1 | - | - | pass | high | correct and clean but only the summer position is drawn; mentions closest in January |
| B60 | Claude Haiku 5.5 | mid | Supply & demand | 1 | 1 | 1 | 1 | - | - | pass | high | both equilibria and the shortage span exact; shortage label crossed by D1 |
| B19 | Claude Haiku 5.5 | mid | Interrupt 2 · supply & demand | 1 | 1 | 2 | 1 | 1 | 1 | pass | high | removes D2 and explains in words with a number example (10 then 20 buyers at price 5); clean, but the chart no longer shows the shift |
| B22 | Gemini 3.8 Flash | low | Seasons | 1 | 1 | 1 | 1 | - | - | pass | high | four positions, tilt and June/December labels consistent; top label crossed by an Earth; 'myth' line wording loose (distance does change slightly) |
| B54 | Gemini 3.8 Flash | low | Pythagoras | 1 | 1 | 1 | 1 | - | - | pass | high | two-arrangement proof, geometry exact; highlight box misplaced over the last sentence |
| B52 | Gemini 3.8 Flash | low | Quadratic | 1 | 1 | 2 | 1 | - | - | pass | high | formula struck out on purpose, then factoring |
| B40 | Gemini 3.8 Flash | low | Supply & demand | 1 | 0 | 1 | 1 | - | - | fail | high | E2 marked on the supply line about 39 px above the true D2-S crossing, so P2 and Q2 are read from the wrong point; labels crossed by lines |
| B06 | Gemini 3.8 Flash | low | Photosynthesis (zh) | 1 | 1 | 1 | 1 | - | - | pass | high | chloroplast with double membrane, grana, stroma, light/dark reaction sites; one label crossed by the outline |
| B20 | Gemini 3.8 Flash | low | Interrupt 1 · seasons | 1 | 0 | 0 | 1 | 1 | 0 | fail | high | 'Tilted toward Sun' label and rays placed at the Earth that leans away; two labels overprinted at the top; text runs across the orbit |
| B34 | Gemini 3.8 Flash | low | Interrupt 2 · supply & demand | 1 | 1 | 2 | 1 | 1 | 0 | pass | high | wiped the board for a concert-ticket auction (3 tickets, 3 then 7 buyers); clear |
| B02 | Gemini 3.8 Flash | low | Interrupt 3 · arrow | 1 | 0 | 2 | 1 | 1 | 1 | fail | high | explanation right, but the new equilibrium dot floats above the D2-S crossing, so P2 is drawn too high |
| B43 | Gemini 3.8 Flash | mid | Seasons | 1 | 1 | 2 | 1 | - | - | pass | high | final board shows direct vs slanted rays and takeaway; the orbit diagram shown before the erase is consistent (June toward, December away) |
| B63 | Gemini 3.8 Flash | mid | Supply & demand | 1 | 1 | 1 | 1 | - | - | pass | high | both equilibria exact, mechanism box good; D1 and D2 labels overprinted, axis labels crossed |
| B32 | Gemini 3.8 Flash | mid | Interrupt 2 · supply & demand | 1 | 1 | 2 | 1 | 1 | 1 | pass | high | umbrella-shop story in a box, E2 with P2 and Q2 exact |
| B50 | Claude Sonnet 5.5 | low | Seasons | 1 | 0 | 2 | 1 | - | - | fail | high | the axis is drawn once and never changes: in the summer step it leans away from the Sun while the text says 'north leans toward Sun', so one of the two steps contradicts the figure |
| B48 | Claude Sonnet 5.5 | low | Pythagoras | 1 | 1 | 2 | 1 | - | - | pass | high | algebra shown then erased; final board sparse, sides not labelled a and b |
| B45 | Claude Sonnet 5.5 | low | Quadratic | 1 | 1 | 2 | 1 | - | - | pass | high | formula tried and erased, then factoring |
| B30 | Claude Sonnet 5.5 | low | Supply & demand | 1 | 1 | 2 | 1 | - | - | borderline | low | new equilibrium dot about 27 px off the crossing; vertical axis arrowhead points down; no quantity labels |
| B29 | Claude Sonnet 5.5 | low | Photosynthesis (zh) | 1 | 1 | 2 | 1 | - | - | pass | high | correct and clean; chloroplast label was erased so the ovals end unlabelled |
| B03 | Claude Sonnet 5.5 | low | Interrupt 1 · seasons | 1 | 0 | 1 | 1 | 1 | 1 | fail | high | season labels swapped: 'North winter' put at the Earth leaning toward the Sun; one label crossed by the orbit; the distance facts were erased from the final board |
| B37 | Claude Sonnet 5.5 | low | Interrupt 2 · supply & demand | 1 | 1 | 2 | 1 | 1 | 0 | pass | high | wiped the board for an ice-cream shop example (10 cones, 10 then 20 buyers); clear |
| B38 | Claude Sonnet 5.5 | low | Interrupt 3 · arrow | 1 | 1 | 2 | 1 | 1 | 1 | borderline | low | E2 dot about 28 px past the true crossing: reclassified as borderline for consistency with B30 and B47 |
| B09 | Claude Sonnet 5.5 | mid | Seasons | 1 | 0 | 2 | 1 | - | - | fail | high | labels swapped: the Earth whose north end leans toward the Sun is labelled 'North: winter' and the other 'North: summer' |
| B21 | Claude Sonnet 5.5 | mid | Supply & demand | 1 | 0 | 2 | 1 | - | - | fail | high | new equilibrium dot sits on the supply line about 37 px past the true D2-S crossing; no quantity labels |
| B64 | Claude Sonnet 5.5 | mid | Interrupt 2 · supply & demand | 1 | 1 | 2 | 1 | 1 | 0 | pass | high | wiped the board for a lemonade stand example (10 cups, 3 then 15 buyers); clear |
| B39 | DeepSeek V4 Pro | low | Seasons | 0 | 0 | 0 | 0 | - | - | fail | high | every step title written on the same spot (illegible), text over the orbit, axis drawn vertical, an unexplained second red disc |
| B16 | DeepSeek V4 Pro | low | Pythagoras | 0 | 0 | 0 | 0 | - | - | fail | high | c-square is not built on the hypotenuse and has the wrong size; b-square not on leg b; figure covers the title, runs off the board; no four triangles though narration refers to them |
| B57 | DeepSeek V4 Pro | low | Quadratic | 1 | 1 | 2 | 0 | - | - | pass | high | correct, but never switches method midway as the question asked |
| B47 | DeepSeek V4 Pro | low | Supply & demand | 1 | 1 | 1 | 1 | - | - | borderline | low | E1 dot about 23 px left of the crossing, E2 exact; vertical axis arrowhead points down; title collides with the axis label; a label crossed by the supply line |
| B53 | DeepSeek V4 Pro | low | Photosynthesis (zh) | 1 | 1 | 1 | 1 | - | - | pass | high | correct, simple; two labels crossed by arrows or the cell outline |
| B25 | DeepSeek V4 Pro | low | Interrupt 1 · seasons | 1 | 0 | 0 | 1 | 1 | 0 | fail | high | June/December labels attached to the two positions where the axis leans neither toward nor away; two text blocks overprinted; bottom label runs off the board |
| B14 | DeepSeek V4 Pro | low | Interrupt 2 · supply & demand | 1 | 0 | 0 | 1 | 1 | 0 | fail | high | new heading written on top of the title; marked Q1 and Q2 do not lie on the curves at the chosen price; two different Q1 labels |
| B33 | DeepSeek V4 Pro | low | Interrupt 3 · arrow | 1 | 1 | 0 | 1 | 1 | 0 | fail | high | a grey box covers the whole chart and the explanation is written across the curves |
| B51 | DeepSeek V4 Pro | mid | Supply & demand | 1 | 1 | 1 | 0 | - | - | pass | low | geometry exact but supply and D1 are never labelled, supply is a short stub, quantity effect omitted |
| B27 | DeepSeek V4 Pro | mid | Interrupt 2 · supply & demand | 1 | 1 | 2 | 1 | 1 | 1 | pass | high | plain-words note plus a before/after table at two prices; neat |
| B15 | DeepSeek V4.1 Flash | low | Seasons | 1 | 0 | 1 | 0 | - | - | fail | low | statements correct but the figure never shows the Sun-Earth geometry; Sun drawn over the first sentence, labels crossed by arrows |
| B61 | DeepSeek V4.1 Flash | low | Pythagoras | 0 | 0 | 1 | 0 | - | - | fail | low | c-square drawn axis-aligned beside the triangle, not on the hypotenuse; right-hand square labelled c2 has the wrong size and shows no triangles; no actual argument |
| B35 | DeepSeek V4.1 Flash | low | Quadratic | 0 | 0 | 0 | 0 | - | - | fail | high | blank board: every instruction omits the op field, so nothing can be drawn |
| B31 | DeepSeek V4.1 Flash | low | Supply & demand | 0 | 0 | 0 | 0 | - | - | fail | high | blank board: every instruction uses 'type' instead of 'op', so nothing can be drawn |
| B12 | DeepSeek V4.1 Flash | low | Photosynthesis (zh) | 1 | 1 | 1 | 1 | - | - | pass | high | cell with wall, membrane, nucleus, vacuole, chloroplasts, zoom to grana; the chloroplast label is crossed by the cell wall and the zoom line |
| B23 | DeepSeek V4.1 Flash | low | Interrupt 1 · seasons | 1 | 1 | 0 | 1 | 1 | 0 | fail | high | explanation and summer/winter labels correct, but new text and two empty boxes are drawn over existing text and the orbit |
| B28 | DeepSeek V4.1 Flash | low | Interrupt 2 · supply & demand | 1 | 1 | 1 | 1 | 1 | 1 | pass | high | fixed-price line with Q1 and Q2 exact on the two curves; two labels crossed by lines |
| B56 | DeepSeek V4.1 Flash | low | Interrupt 3 · arrow | 1 | 0 | 0 | 1 | 1 | 0 | fail | high | marked points lie on neither curve, Q2 too far right; 'same P' written over P2, labels crossed by lines |
| B49 | DeepSeek V4.1 Flash | mid | Supply & demand | 1 | 1 | 1 | 1 | - | - | pass | high | both equilibria exact with P and Q guides; result text overlaps the S label; D1 and D2 same colour |
| B08 | DeepSeek V4.1 Flash | mid | Interrupt 2 · supply & demand | 1 | 1 | 2 | 1 | 1 | 1 | pass | high | same-price arrow, shortage and E2 all exact, plus a short bike story (story assumes fixed stock while the chart shows quantity rising) |
