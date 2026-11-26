# Changelog

## v0.4.0 — 2026-11-26

### Interactive widgets (experiment)

- Add an experimental `widget` operation (protocol v1.1 draft): a figure that the player computes from a few parameters and the student can drag. It lowers to ordinary v1 operations, so playback, the linter and the recordings are unchanged.
- Add two hand-written widgets, supply and demand and seasons, with four example lessons under **Interactive widgets (hand-written)** in the player's lesson menu. Drag a curve or the Earth, or answer a question by dragging a dot: the lesson pauses for the answer, and the explanation for each typical mistake is worked out by code.
- Record each drag and answer as a structured event and report it with the board state (Export board state), together with the widget's current parameters.
- Run the draft protocol once with three models on six tasks (54 calls, $0.37): every output parsed and passed the schema check, and the models chose the right widget, or none for a topic no widget covers. The prompt, settings, results and limits are in [docs/INTERACTIVE.md](docs/INTERACTIVE.md) ([中文](docs/INTERACTIVE.zh-CN.md)). These calls are separate from the 288 v1 runs and the leaderboard.
- The PDF preview does not support widget lessons yet; its button is disabled for them.

### 中文说明

- 新增实验性的 `widget` 操作（协议 v1.1 草稿）：由播放器根据少量参数算出整张图，学生可以拖动。它会展开成普通的 v1 操作，播放、检查脚本和已有录制不受影响。
- 新增两个手写板件（供需、四季）和四节示例课，位于播放器课程菜单的“Interactive widgets (hand-written)”分组。可以拖动曲线或地球，也可以拖一个点来回答问题；课程会暂停等待作答，针对每种典型错误的讲解由代码给出。
- 每次拖动和作答都会记录成结构化事件，随“导出白板状态”一起给出，并附板件当前的参数。
- 对该草稿协议做了一次独立的小规模实测（3 个模型、6 个任务、54 次调用、$0.37）：所有输出都能解析、通过格式检查，模型选对了板件，板件没覆盖的题也没有被硬套。提示词、设置、结果和局限见 [docs/INTERACTIVE.zh-CN.md](docs/INTERACTIVE.zh-CN.md)。这些调用不在 288 次 v1 生成和排行榜之内。
- PDF 预览暂不支持板件课程，对应按钮已置灰。

This release adds files and a small extension to the player. The frozen protocol, prompts, scores and historical leaderboard remain unchanged; replaying lessons still needs no API key or new runtime dependency.

## v0.3.0 — 2026-11-23

### Complete-lesson PDF preview

- Open PDF preview from the player in a separate tab, then use Print / Save as PDF.
- Lay out every step-end board and its full original narration on A4 landscape pages. Long explanations continue onto additional pages.
- For interrupted lessons, include the board at interruption and the student's question before the continuation steps.
- Include question, model, thinking setting, existing review ID/verdict, page numbers and a link to replay the lesson.
- Preserve the original player's playback state and speed when opening, printing, cancelling or closing the preview.
- Provide English/Chinese controls, fit-to-screen and actual-size preview, loading feedback and retry on failure. Printing is verified on desktop Chrome and Edge; saving on phones depends on the browser and system.

### 中文说明

- 播放器新增 PDF 预览入口，在独立标签页检查课件后，使用“打印 / 另存为 PDF”。
- 单节课所有步骤以 A4 横向排版，保留每步结束时的板书与完整原始讲解，长文本自动续页。
- 打断续讲先展示打断时的白板和学生追问，再展示后续步骤；附题目、模型、已有评审信息、页码与回放来源。
- 预览、打印、取消和关闭不会重置原播放器；支持中英文界面、缩放预览、加载提示和失败重试。

This release reuses the existing player renderer and recordings. It requires no model API calls, PDF service or new runtime dependency. The frozen benchmark data and historical scores remain unchanged.

## v0.2.0 — 2026-11-23

### Compare explanations

- Compare two models on the same question and thinking setting in English or Chinese.
- Inspect the original boards, blind-review verdicts, notes and per-run latency/cost side by side.
- Open each recording in its own player and return to the selected comparison.
- Copy a shareable link preserving the question, thinking setting and both models. A selectable-link fallback works when clipboard access is unavailable.
- Distinguish unreviewed combinations from the two sampled cells with no usable output.

### Find a board

- Filter the 64 reviewed boards by question, model, verdict and thinking setting.
- Restore filters from a link, switch language without losing them, and use browser back/forward navigation.
- Show a useful empty state and reset control when no boards match.

### 中文说明

- 新增中英文同题对比页，并排查看两份板书、盲评意见及单次生成指标。
- 支持单独打开回放并返回原对比，分享链接保留题目、思考档与左右模型。
- 画廊支持题目、模型、评审结果和思考档筛选，支持链接恢复与浏览器前进后退。
- 明确区分未评审组合、没有可用输出及加载失败状态。

All features reuse the existing recordings and review data. The frozen protocol, prompts, scores and historical leaderboard remain unchanged; no model API calls are required.


## v0.1.0 — 2026-11-22

### Demo and playback

- Start with a muted, pausable Pythagorean-theorem preview and clear links to the player, benchmark and local setup.
- Fit the gallery and playback controls to phone screens. Enlarge the board to scroll through fine details.
- Keep the chosen English or Chinese interface when opening a board, changing language or returning to the gallery.
- Move state export and lint tools into Advanced options; show useful loading and error states.
- Respect reduced-motion preferences when starting previews and recorded replays.
- Load gallery thumbnails lazily and reuse a compact MP4 preview.

### Project information

- Distinguish 288 generation runs from the 64 blind-reviewed boards.
- Add contextual Lynote AI Notes links to the READMEs and gallery footer.
- Add contribution guidance and a roadmap for the next model-comparison release.

The original prompts, recorded model outputs, review scores and leaderboard data are unchanged.

---

## v0.1.0 — 中文说明

- 首页增加可暂停的勾股定理动画预览，以及播放器、评测和本地运行入口。
- 修复手机布局，提供白板放大与滚动查看，中英文操作界面保持一致。
- 导出与检查工具收入高级选项，补充加载和失败状态，尊重减少动态效果的系统设置。
- 明确区分 288 次生成测试与 64 块白板盲评，增加 Lynote AI Notes 入口、贡献指南与路线图。
- 原始提示词、模型输出、盲评打分与榜单数据保持原样。
