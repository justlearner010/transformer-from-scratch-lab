# Transformer From Scratch Lab

一个以理论理解为起点的 Transformer 自学实验室。这里的目标不是“完成一串术语和代码文件”，而是能一路说清：一个 token 的信息如何变成向量、如何选择性读取其他 token、为何不能偷看未来、如何从预测错误中更新参数，最后如何独立把这些机制组合成一个可训练的小模型。

## 你正在学习什么，为什么按这个顺序？

Transformer 的核心不是一个神秘的大模型，而是一条逐步扩展的信息处理链。我们从能看见、能手算的极小向量开始；每一周只增加一个必要能力，并把它变成下一周的前提。

| 阶段 | 你解决的问题 | 这一步给下一步什么基础 |
| --- | --- | --- |
| Week 0 | 如何精确描述一组 token 在矩阵里的形状和数值？ | 能读懂 Q/K/V 的输入输出，而不被 shape 卡住。 |
| Week 1 | 一个 token 如何依据内容选择性读取其他 token？ | 得到 attention 输出，理解“上下文混合”发生在哪里。 |
| Week 2 | 什么信息不该被读取？如何把多个机制稳定地连起来？ | 得到单层 Transformer block。 |
| Week 3 | block 怎样从“预测错了”中改变参数？ | 得到最小可训练的字符级语言模型。 |
| Week 4 | 不依赖脚手架，能否重新做出来并解释失败？ | 形成独立实现能力，并据此选择下一个大项目。 |

每一周都沿同一条链推进：**先理解本周问题，再手算一个小例子，随后做小实验、无答案 Lab、书面 Homework，最后写下自己理解发生了什么变化。** 如果某一环没有通过，不赶进度，而是回到表中明确的前置阶段补足。

## 学习闭环

```text
课前引导 → 理论材料 → 小习题 → Lab → 理论 Homework → 课后笔记
                                      ↓
                              独立字符级 demo → 更大项目
```

本仓库公开课程材料、题目、函数契约与公开 smoke tests。真正的核心评分器放在本地 `.grader/`（由 `.gitignore` 排除），只输出错误类别和引导，不泄露样例或答案。评分的目的不是替你思考，而是在你已经思考和尝试后，帮你定位“具体在哪个机制上出了错”。

## 四周高强度课程

| 周 | 主题 | 产出 |
| --- | --- | --- |
| 0 | 线性代数、softmax、导数与张量契约预备 | 预备习题与环境检查 |
| 1 | Q/K/V、缩放点积 attention、softmax | attention 理论题与 Lab 关卡 0–2 |
| 2 | causal mask、LayerNorm、FFN、残差与 block | 完整机制 Lab 与理论 Homework |
| 3 | 最小语言模型训练 | 不看答案的字符级 demo |
| 4 | 综合重构、压力测试与架构复盘 | 闭卷期末作业与大项目设计 memo |

## 正式学习材料

PDF 是学习者正式使用和对外分发的课程版本；Markdown、YAML、LaTeX、Lab 与 grader 是维护和运行课程的源文件。学习时先打开当周 Learning Guide，再完成 Problem Set，最后进入代码 Lab。

| 阶段 | Learning Guide | Problem Set | 代码与运行说明 |
| --- | --- | --- | --- |
| Week 0 | [学习指南 PDF](resources/week-00.pdf) | [题集 PDF](problem-sets/week-00-problem-set.pdf) | [Week 0 工作区](weeks/week-00/README.md) |
| Week 1 | [学习指南 PDF](resources/week-01.pdf) | [题集 PDF](problem-sets/week-01-problem-set.pdf) | [Week 1 工作区](weeks/week-01/README.md) |

从 Week 0 开始。每周建议投入 30–35 小时；由掌握度而非外部截止日期推进。PDF 只提供学习路线、题目与提交标准，不包含答案；完成后的讲评必须与题集分开发布。

## 本地运行

```bash
uv sync --group dev
uv run pytest
uv run python labs/week-01/run_grade.py
```

`pytest` 只运行公开 smoke tests；`run_grade.py` 在本地存在 `.grader/` 时才执行隐藏评分。

## Self-Learning Agent MVP

Week 1 已提供持续运行的终端学习 Agent。学生先手动创建自己的分支，然后只需一个入口；没有 session 时自动创建，已有 session 时从 Event Ledger 恢复：

```bash
git switch -c learner/<你的名字>/week-01
uv run learning-os agent week-01
```

根据 Agent 显示的作答文件完成回答并加入手写附件。学生仍必须本人提交 Git commit，然后回到 Agent 输入 `/submit`：

```bash
git add homework_answer/week-01/
git commit -m "answer: week 01 gate 0"
```

可用命令：`/submit`、`/retry`、`/status`、`/next`、`/help`、`/quit`。普通文字只用于解释当前任务，永远不会触发提交或状态变化。Agent 不创建分支、不写答案、不 commit、不 push。

对话 Qwen 只能生成显示文本；独立 Verifier 只能逐项返回 rubric 结果；`PolicyEngine` 和状态机拥有最终状态权。相同答案、附件、rubric 和 verifier 版本会复用第一次有效判定。对话记录不持久化，学习进度只从 `.learning-os/events.jsonl` 恢复。Gate 1–6 尚无 rubric，因此不会让模型自由判分。

真实模型调用只从环境变量读取凭据：

```bash
cp .env.example .env
# 在 .env 中填写新 key 后导入当前 shell；不要提交 .env
set -a && source .env && set +a
uv run pytest -m live tests/live/test_siliconflow_live.py -q
uv run pytest -m live tests/live/test_siliconflow_agent_live.py -q
```

未设置 key 时 live test 会跳过；单元测试不需要网络或真实 key。

完整边界和恢复规则见 [Runtime Foundation 说明](docs/runtime-foundation.md)。

维护者可用以下命令重建并验证所有正式 PDF：

```bash
uv run python scripts/build_course_pdfs.py
uv run python scripts/verify_course_pdfs.py
```

## 项目边界

这个仓库不追求训练大模型、复刻完整论文或尽早进入 RAG。当前目标是能独立解释并实现单层、单头 Transformer 的每个机制。
