# 互动板件（实验）

[English](INTERACTIVE.md) · [简体中文](INTERACTIVE.zh-CN.md)

> **状态：实验。** 与冻结的 v1 评测分开：v1 的提示词、操作、录制、评分和排行榜都没有改动，下面的数字也不属于它们。
> 板件是手写的。板件协议是一份草稿（[`protocol/PROTOCOL-v1.1-widgets.md`](../protocol/PROTOCOL-v1.1-widgets.md)，英文）。

## 想法

v1 里模型写的是绝对坐标，最常见的失败是图和自己的文字对不上（点画在交点旁边，季节标在错的地球上）。此外，静态的画也是学生
能得到的全部：他们只能靠打字来打断。

**板件**是由播放器画出并保持自洽的图形。模型只选种类和参数，每个坐标、标注、辅助线和读数都由播放器算出：

```json
{ "op": "widget", "id": "sd", "kind": "supply-demand",
  "params": { "show": ["axes", "demand", "supply", "equilibrium"], "demandShift": 2 },
  "expect": { "price": "up", "quantity": "up" } }
```

图形既然是少数几个参数的函数，学生就可以通过拖动来改变这些参数，结果还能作为结构化事件回报给模型。

## 背景

把图形定义成少数几个参数的函数，再让学生拖动来改变参数，这个思路来自 *Declarative Dragging*
（Joshua Horowitz、Andrew Blinn、Jeffrey Heer，UIST 2026；[项目主页](https://declarative-dragging.github.io/)，
DOI 10.1145/3830398.3830556）及其配套库 Dragology（MIT）。本仓库没有使用它们的任何代码：这里的板件是针对两个主题手写的，
拖动只是把指针位置映射成一个参数。

## 试一试

在播放器里打开四节 **Interactive widgets (hand-written)** 课程之一：

| 课程 | 内容 |
|---|---|
| Supply & demand: drag the curves（供需：拖动曲线） | 六步讲解；结束后可拖动红线或蓝线，看均衡点、价格和数量怎么变 |
| Supply & demand: predict the equilibrium（供需：预测均衡点） | 两道题。课程暂停，把圆点拖到你认为的新均衡点；每种典型错误都有对应的讲解 |
| Seasons: drag the Earth（四季：拖动地球） | 拖动地球绕轨道转；放大图显示太阳直射在哪里，以及北纬 40° 正午的太阳高度 |
| Seasons: where is it summer?（四季：哪里是夏天） | 两道题（“北半球的夏天”“南半球的夏天”）；答对之前放大图保持隐藏 |

URL 里的 `?s=w2-predict-equilibrium.en`（以及 `w1-supply-demand.en`、`w3-seasons.en`、`w4-seasons-ask.en`）用来选择课程；
加上 `&lang=zh` 可切换成中文界面（板书和讲解仍是英文）。反馈和数字都由代码算出，不调用任何模型。

## 工作原理

```
widget 操作 ──展开──▶ 普通的 v1 操作（坐标由代码算出）
                     └─ 与白板上现有对象做对比：
                         新 id      → 用常规的手写动画画出
                         内容变化   → 就地替换（数值参数带补间动画）
                         id 消失    → 移除
播放空闲 ──▶ 板件的“手柄”可以拖动
拖动 / 作答 ──▶ 一个参数改变 → 重新展开；松手时记录一条结构化事件
```

- **v1 不受影响。** 板件展开成 `write` / `line` / `ellipse` / `path` 操作，所以播放器、检查脚本和录制照常工作。
  但把 `widget` 暴露给模型，实验条件就和 v1 不同，因此它有自己的草稿协议和自己的结果目录。
- **手柄。** 手柄是把指针映射到某一个参数的区域（曲线的平移量、地球在轨道上的位置、一个点的位置）。参数范围和吸附由板件决定。
- **提问。** 带 `ask` 的步骤会让课程暂停。学生的答案会和一小组预期答案（正确答案和典型错误）比对，连续型的答案则按区域判断，
  然后显示对应的讲解。不会发给任何模型。
- **事件。** 每次拖动或作答都会追加到 `student_events`，并连同板件当前的参数和状态摘要一起由 `getState()` 给出（和学生打断时
  发送的“白板状态”是同一份）：

```json
{ "widget": "sd", "kind": "supply-demand", "event": "drag", "param": "demandShift", "from": 2, "to": -1.5,
  "state": { "demand_shift": -1.5, "supply_shift": 0, "equilibrium": { "price": 4.25, "quantity": 4.25 },
             "change": { "price": -0.75, "quantity": -0.75 } } }
```

- **四季按四个四分之一圈划分**，分别以冬至、春分、夏至、秋分为中心（大致是 6–8 月为北半球的夏天）。页面上写明了这一点。
  轨道画成圆形：真实的日地距离大约变化 3%。

文件：`player/widgets/`（运行时和两个板件）、`scenarios/interactive.json` 与 `scenarios/widgets/`（课程；用单独的索引，
`scenarios/index.json` 不变）、`protocol/PROTOCOL-v1.1-widgets.md`。PDF 预览暂不支持这些课程，对应按钮是灰的。

## 模型能驱动它吗？一次小规模实测

**设置**（全部在本仓库里）：

| | |
|---|---|
| 提示词 | [`protocol/PROTOCOL-v1.1-widgets.md`](../protocol/PROTOCOL-v1.1-widgets.md)（英文）：v1 协议加上 `widget` 操作、两种板件和一个例子，原文发送 |
| 模型 | Claude Haiku 5.5、Gemini 3.8 Flash、Claude Sonnet 5.5，经 OpenRouter 固定到一方服务商，不允许回退 |
| 日期与设置 | 2026-11-26；低思考；输出上限 8000 token；沿用 v1 的运行器约定（`bench/run_widgets.py`） |
| 任务 | 6 个，每个跑三次：供需讲解、四季讲解、带提问的讲解、一个**没有**板件覆盖的题（勾股定理）、两个学生拖动板件后的打断 |
| 样本 | 54 次调用（6 次冒烟调用复用为对应任务的第 1 次），共 **$0.37** |
| 评审 | 只做确定性检查（`bench/widget_check.py`）：格式、选对板件（或不用板件）、任务要求的终态，以及模型自己写的 `expect` 与它的参数算出的状态是否一致。没有人工或模型评审 |

**结果**（`results/widgets/summary.md` 有完整表格、分场景数字和失败清单）：

| 模型 | 能解析 | 格式合法 | 选对板件 / 不用 | 达到预期终态 | `expect` 一致 | 漏写 `expect` | 花费 |
|---|---|---|---|---|---|---|---|
| Claude Haiku 5.5 | 18/18 | 18/18 | 18/18 | 17/18 | 33/34 | 0/34 | $0.025 |
| Gemini 3.8 Flash | 18/18 | 18/18 | 18/18 | 18/18 | 42/42 | 6/48 | $0.085 |
| Claude Sonnet 5.5 | 18/18 | 18/18 | 18/18 | 18/18 | 51/51 | 0/51 | $0.257 |

- 没有板件覆盖的题，9 次全部退回普通操作，没有一次硬套板件。
- 36 份讲解类输出都能在播放器里重放，没有警告，也没有检查脚本的错误。
- 与同一模型在 v1 低思考下的运行对比（提示词和场景都不同，仅供参考），板件的输出更短：供需讲解的输出 token，
  Haiku 3,709 → 1,198，Gemini 2,235 → 644，Sonnet 1,498 → 688。
- 两个失败：一次 Haiku 的旁白说“把需求线拖回起点”，却把平移量设成了 −2（它的 `expect` 与这个参数一致，只有终态检查抓到了）；
  另一次 Haiku 在提问之后声明了错误的季节。

**这些数字不能说明什么**

- 检查不读旁白。旁白和参数矛盾的步骤，只有 `expect` 也矛盾时才会被抓到。
- 三个模型、两个手写板件、每个任务三次。说明不了其他知识点、其他模型，也说明不了板件数量多得多的情形。
- 任务比 v1 容易得多（选参数，而不是算坐标），所以这些数字不能和 v1 排行榜比较。
- 有一条检查规则是看到第一批结果后才加的：提问之后，如果某个操作把 `ask` 设为 null 又没有给位置，就假定学生答对了。
  它改变了一次调用的判定，已写在 `summary.md` 里。
- 另外手工读了三份打断的输出，它们都回答了学生看到的现象；这只是抽查，不是评分。
- 没有学生用过这些课程。这里没有任何内容说明拖动能帮助人学习。

## 局限

- 板件是手写、手审的，它依赖的每个定义都要只写一遍：四季板件用同一个“夏天”的定义来做读数和判题，否则两者可能互相矛盾。
- 目前只有两个板件；一套通用的积木（坐标轴、函数线、交点、附着标注）能让模型自己组合图形，但会把“组合得对不对”的问题带回来。
- 拖动的开销只在一台桌面电脑上测过（约 30 个对象，每次指针移动的中位数约 4 毫秒）。手机、低配电脑和触屏输入都没有测。
  手指放在白板上时，页面不会滚动。
- 动画是通过结束状态和脚本模拟的拖动检查的，没有实时观看。
- 学生对白板本身的编辑（移动或删除对象、撤销）是另一个问题，在 [#3](https://github.com/molly554/whiteboard-ai-tutor/issues/3)
  里跟踪；上面的事件只描述板件的参数。

## 复现

```bash
python bench/run_widgets.py preflight --via openrouter           # 免费：检查密钥、模型 ID、固定的服务商
python bench/run_widgets.py smoke --via openrouter               # 6 次调用，几美分
python bench/run_widgets.py main --confirm --via openrouter --skip wsmoke   # 再跑 48 次，约 $0.34
python bench/aggregate_widgets.py                                # 生成 results/widgets/summary.md
```

运行器有总硬上限（$0.60）和单模型上限，并把每次调用追加写入 `results/widgets/*.jsonl`。
`bench/mock_server.py` 在这里同样可用（`WB_MOCK_BASE=http://127.0.0.1:8899`，`--phase wmock`），可以不花钱地测试流程。
费用是 OpenRouter 对每次调用报告的金额。

相关：[#7](https://github.com/molly554/whiteboard-ai-tutor/issues/7) 提议加入 `mark_intersection` 之类的高层操作。
板件是通向同一个失败点的另一条路（让播放器而不是模型去算整张图的位置），两者可以在同样的场景上比较。
