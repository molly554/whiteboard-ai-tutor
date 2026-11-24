"""Shared public gallery layout. Reused whenever unblind.py regenerates the pages."""

RUN = "main-or-gemini-4-argon-low-r1-pythagoras-3"
SOURCE = "https://github.com/molly554/whiteboard-ai-tutor"


def gallery_header(lang):
    zh = lang == "zh"
    other = '<a href="index.html" lang="en">English</a>' if zh else '<a href="gallery.zh.html" lang="zh-CN">中文</a>'
    play = f"player/index.html?run={RUN}&amp;sc=r1-pythagoras&amp;lang={lang}"
    title = "让 AI 把思路，<br>一笔一笔画出来。" if zh else "Watch AI explain,<br>one stroke at a time."
    intro = ("从勾股定理到四季变化，看大模型如何边解释、边写字、边画图。重放真实生成结果，也看看它们在哪里讲错、画错。" if zh else
             "From the Pythagorean theorem to the changing seasons: watch language models write, draw and explain. Replay real outputs, including the mistakes.")
    return f'''<header class="site-header">
<a class="wordmark" href="{'gallery.zh.html' if zh else 'index.html'}"><span class="brand-mark" aria-hidden="true">w.</span>Whiteboard AI Tutor</a>
<nav aria-label="{'主导航' if zh else 'Main navigation'}"><a href="{'compare.zh.html' if zh else 'compare.html'}">{'对比模型' if zh else 'Compare'}</a>{other}<a href="{SOURCE}" target="_blank" rel="noopener">GitHub ↗</a></nav>
</header>
<section class="hero" aria-labelledby="hero-title">
<div class="hero-copy"><p class="eyebrow">{'开源白板 AI 导师 · 模型评测' if zh else 'OPEN-SOURCE AI TUTOR · LLM BENCHMARK'}</p>
<h1 id="hero-title">{title}</h1><p class="hero-intro">{intro}</p>
<div class="hero-actions"><a class="button primary" href="{play}">{'▶ 观看完整讲解' if zh else '▶ Watch the explanation'}</a><a class="button secondary" href="{'compare.zh.html' if zh else 'compare.html'}">{'对比两个模型 →' if zh else 'Compare two models →'}</a></div>
<p class="demo-note">{'录制结果回放 · 无需 API 密钥 · 生成新课程需自行运行' if zh else 'Recorded demos · No API key required · Run locally to generate new lessons'}</p>
<a class="text-link" href="{SOURCE}#quickstart" target="_blank" rel="noopener">{'自己运行 ↗' if zh else 'Run it yourself ↗'}</a>
<dl class="stats"><div><dt>6</dt><dd>{'个模型' if zh else 'models'}</dd></div><div><dt>288</dt><dd>{'次生成测试' if zh else 'generation runs'}</dd></div><div><dt>64</dt><dd>{'块盲评白板' if zh else 'blind-reviewed boards'}</dd></div></dl>
</div>
<figure class="hero-preview"><div class="preview-bar"><span class="preview-dot" aria-hidden="true"></span><span>{'勾股定理 · Gemini 4 Argon' if zh else 'The Pythagorean theorem · Gemini 4 Argon'}</span><span class="preview-tag">{'3 倍速' if zh else '3× speed'}</span></div>
<video id="hero-video" controls muted playsinline loop preload="metadata" poster="results/review/boards/B62.png" aria-label="{'勾股定理白板讲解预览，原始英文内容' if zh else 'Preview of an AI whiteboard explanation of the Pythagorean theorem'}"><source src="docs/assets/pythagoras.mp4" type="video/mp4"><a href="{play}">{'在播放器中观看' if zh else 'Watch in the player'}</a></video>
<figcaption>{'真实模型输出，保留原始语言。可暂停预览，或打开完整播放器逐步查看。' if zh else 'An actual model output. Pause the preview, or open the player to explore each step.'}</figcaption></figure>
</section>
<section id="benchmark" aria-labelledby="benchmark-title"><div class="section-heading"><div><p class="eyebrow">{'同一份提示词，看看谁讲得更清楚' if zh else 'ONE FROZEN PROMPT. SIX DIFFERENT EXPLANATIONS.'}</p><h2 id="benchmark-title">{'模型评测与全部 64 块白板' if zh else 'The benchmark, and all 64 reviewed boards'}</h2></div><a class="text-link" href="{SOURCE}/blob/main/docs/METHOD.md" target="_blank" rel="noopener">{'评测方法 ↗' if zh else 'Read the method ↗'}</a></div>
<p class="lead">{'同一份提示词，八个教学场景。每张卡片保留模型原始板书，点击可重放书写过程。盲评打分时隐藏了模型名称。' if zh else 'One prompt, eight teaching scenarios. Every card shows a board exactly as the model drew it. Click to replay the writing. Model names were hidden during blind scoring.'}</p>'''


def gallery_filters(lang):
    zh = lang == 'zh'
    return f'''<div id="boards" class="boards-heading"><h2>{'查找评审白板' if zh else 'Find a reviewed board'}</h2><p>{'按题目、模型、评审结果和思考档筛选，也可打开同题对比。' if zh else 'Filter by question, model, verdict and thinking setting, or compare two models on one question.'}</p></div>
<div id="board-filters" class="board-filters" hidden>
<label class="filter-field"><span>{'题目' if zh else 'Question'}</span><select id="filter-sc"></select></label>
<label class="filter-field"><span>{'模型' if zh else 'Model'}</span><select id="filter-model"></select></label>
<label class="filter-field"><span>{'评审结果' if zh else 'Verdict'}</span><select id="filter-verdict"></select></label>
<label class="filter-field"><span>{'思考档' if zh else 'Thinking setting'}</span><select id="filter-cond"></select></label>
<button id="reset-filters" class="button secondary" type="button">{'清除筛选' if zh else 'Reset filters'}</button>
</div><p id="filter-count" class="filter-count" role="status" aria-live="polite">{'共 64 块评审白板' if zh else '64 reviewed boards'}</p>
<div id="empty-boards" class="empty-boards" hidden><h3>{'没有符合条件的白板' if zh else 'No boards match these filters'}</h3><p>{'试试其他筛选条件，或清除筛选查看全部 64 块白板。' if zh else 'Try another selection, or reset the filters to see all 64 boards.'}</p><button id="empty-reset" class="button secondary" type="button">{'查看全部白板' if zh else 'Show all boards'}</button></div>'''


def comparison_page(lang):
    zh = lang == 'zh'
    title = '同题对比 · Whiteboard AI Tutor' if zh else 'Compare models · Whiteboard AI Tutor'
    other = 'compare.html' if zh else 'compare.zh.html'
    gallery = 'gallery.zh.html' if zh else 'index.html'
    return f'''<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{'并排比较同一道题的两份 AI 白板讲解，查看原始板书、盲评意见与独立回放。' if zh else 'Compare two AI whiteboard explanations of the same question. Inspect original boards, review notes and independent replays.'}"><title>{title}</title><link rel="stylesheet" href="docs/assets/gallery.css"><link rel="stylesheet" href="docs/assets/compare.css"><script type="module" src="docs/assets/compare.js"></script></head>
<body><main class="wrap compare-page"><header class="site-header"><a class="wordmark" href="{gallery}"><span class="brand-mark" aria-hidden="true">w.</span>Whiteboard AI Tutor</a><nav aria-label="{'主导航' if zh else 'Main navigation'}"><a class="browse-nav" href="{gallery}#boards">{'全部白板' if zh else 'All boards'}</a><a id="language-link" href="{other}">{'English' if zh else '中文'}</a><a href="{SOURCE}" target="_blank" rel="noopener">GitHub ↗</a></nav></header>
<div class="compare-heading"><p class="eyebrow">{'同一份提示词 · 同一题目 · 同一思考档' if zh else 'SAME PROMPT · SAME QUESTION · SAME THINKING SETTING'}</p><h1>{'同一道题，看看两个模型怎么讲。' if zh else 'One question. Two explanations.'}</h1><p>{'并排查看原始板书与评审意见，再分别打开回放，看看推导是怎样一步步画出来的。' if zh else 'Inspect original boards and review notes side by side. Open each replay in its own player to see how the explanation unfolds.'}</p></div>
<section aria-label="{'模型对比' if zh else 'Model comparison'}"><noscript><p>{'请启用 JavaScript 使用模型对比，或返回画廊查看全部白板。' if zh else 'Enable JavaScript to compare models, or return to the gallery to browse all boards.'} <a href="{gallery}#boards">{'查看白板' if zh else 'Browse boards'}</a></p><style>#loading{{display:none}}</style></noscript>
<div id="loading" class="load-state" role="status">{'正在加载评审数据…' if zh else 'Loading the reviewed boards…'}</div>
<div id="load-error" class="load-state" role="alert" hidden><h2>{'评审数据未能加载' if zh else 'The review data could not be loaded'}</h2><p>{'请检查网络后重试，或返回画廊查看白板。' if zh else 'Check your connection and retry, or browse the gallery.'}</p><button id="retry-load" class="button secondary" type="button">{'重新加载' if zh else 'Try again'}</button> <a href="{gallery}#boards">{'返回画廊' if zh else 'Back to the gallery'}</a></div>
<div id="comparison-content" hidden><div class="compare-toolbar">
<label class="field question-field"><span>{'选择题目' if zh else 'Choose a question'}</span><select id="sc"></select></label>
<label class="field thinking-field"><span>{'思考档' if zh else 'Thinking setting'}</span><select id="cond"><option value="low">{'低思考档' if zh else 'Low thinking'}</option><option value="mid">{'中思考档' if zh else 'Medium thinking'}</option></select></label>
<button id="share-comparison" class="button primary share-button" type="button">{'复制对比链接' if zh else 'Copy comparison link'}</button>
<div class="share-area"><p id="share-status" role="status" aria-live="polite"></p><label id="share-fallback" hidden><span>{'对比链接' if zh else 'Comparison link'}</span><input id="share-url" type="text" readonly></label></div>
</div>
<div class="question-summary"><div><h2 id="question-title"></h2><p id="comparison-setting"></p></div><a id="browse-question" class="text-link" href="{gallery}#boards">{'查看这道题的全部白板 →' if zh else 'Browse all boards for this question →'}</a></div>
<p id="sample-notice" class="sample-notice" hidden>{'中思考档只评审了四季、供需曲线和“换个简单讲法”三个场景。部分抽样单元没有可用输出，不能视为已评分的白板。' if zh else 'The medium-thinking review covers only seasons, supply and demand, and the simpler-explanation interruption. Some sampled cells had no usable output and have no reviewed board.'}</p>
<div class="comparison-grid"><article class="compare-card"><header class="model-picker"><span class="model-letter" aria-hidden="true">A</span><label class="field"><span>{'左侧模型' if zh else 'Model A'}</span><select id="a"></select></label></header><div id="board-a" class="board-content"></div></article><article class="compare-card"><header class="model-picker"><span class="model-letter" aria-hidden="true">B</span><label class="field"><span>{'右侧模型' if zh else 'Model B'}</span><select id="b"></select></label></header><div id="board-b" class="board-content"></div></article></div>
<p class="method-note">{'这些是既有的盲评记录，不是实时生成，也不是同题全部重复实验的平均结果。“边界”计入宽松通过数，但不计入严格通过数。延迟与成本是各自这一次生成的记录，成本按 2026-11-11 标价计算。原始白板与讲解保留模型输出时的语言。' if zh else 'These are existing blind-review records, not live generations or averages across all repeats. Borderline boards count as passes under the lenient rubric, but not the strict one. Latency and cost describe each recorded run; prices are dated 2026-11-11. Original boards and narration keep their recorded language.'} <a href="{SOURCE}/blob/main/docs/METHOD.md" target="_blank" rel="noopener">{'查看评测方法 ↗' if zh else 'Read the method ↗'}</a></p>
</div>{gallery_footer(lang)}</main></body></html>'''


def gallery_footer(lang):
    zh = lang == "zh"
    return f'''</section><footer class="site-footer"><div><span class="footer-label">{'继续整理你的学习资料' if zh else 'KEEP LEARNING WITH YOUR OWN MATERIALS'}</span><p>{'将 PDF、课程录音和视频整理成学习笔记、闪卡与测验。' if zh else 'Turn PDFs, lectures and videos into study notes, flashcards and quizzes.'}</p><a class="button secondary" href="https://lynote.ai/ai-notes" target="_blank" rel="noopener">{'试试 Lynote AI Notes ↗' if zh else 'Explore Lynote AI Notes ↗'}</a></div><div class="footer-project"><b>Whiteboard AI Tutor</b><p>{'开源协议、播放器与评测数据。' if zh else 'Open protocol, player and benchmark data.'}</p><a href="{SOURCE}" target="_blank" rel="noopener">GitHub ↗</a><span> · MIT</span></div></footer>'''
