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
<nav aria-label="{'主导航' if zh else 'Main navigation'}">{other}<a href="{SOURCE}" target="_blank" rel="noopener">GitHub ↗</a></nav>
</header>
<section class="hero" aria-labelledby="hero-title">
<div class="hero-copy"><p class="eyebrow">{'开源白板 AI 导师 · 模型评测' if zh else 'OPEN-SOURCE AI TUTOR · LLM BENCHMARK'}</p>
<h1 id="hero-title">{title}</h1><p class="hero-intro">{intro}</p>
<div class="hero-actions"><a class="button primary" href="{play}">{'▶ 观看完整讲解' if zh else '▶ Watch the explanation'}</a><a class="button secondary" href="#benchmark">{'查看模型评测 ↓' if zh else 'Explore the benchmark ↓'}</a></div>
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


def gallery_footer(lang):
    zh = lang == "zh"
    return f'''</section><footer class="site-footer"><div><span class="footer-label">{'继续整理你的学习资料' if zh else 'KEEP LEARNING WITH YOUR OWN MATERIALS'}</span><p>{'将 PDF、课程录音和视频整理成学习笔记、闪卡与测验。' if zh else 'Turn PDFs, lectures and videos into study notes, flashcards and quizzes.'}</p><a class="button secondary" href="https://lynote.ai/ai-notes" target="_blank" rel="noopener">{'试试 Lynote AI Notes ↗' if zh else 'Explore Lynote AI Notes ↗'}</a></div><div class="footer-project"><b>Whiteboard AI Tutor</b><p>{'开源协议、播放器与评测数据。' if zh else 'Open protocol, player and benchmark data.'}</p><a href="{SOURCE}" target="_blank" rel="noopener">GitHub ↗</a><span> · MIT</span></div></footer>'''
