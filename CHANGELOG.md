# Changelog

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
