# Transformer Lab 正式课程 PDF 设计

## 目标

为每个 Week 生成两份正式、可打印、对学习者友好的 PDF：Learning Guide 负责说明本周目标、精确资源、Gate 与停止规则；Problem Set 负责让学习者在离开代码和 AI 提示时完成推导、反例和工程设计思考。完成后的讲评始终与这两份公开材料分开。

## 文件与发布边界

```text
resources/week-XX.pdf                    正式学习指南
resources/week-XX.tex                    学习指南 LaTeX 源文件
problem-sets/week-XX-problem-set.pdf     公开题集，只含题目和自检
problem-sets/week-XX-problem-set.tex     LaTeX 题集源文件，便于版本控制与公式复现
solutions/week-XX-review.md              完成后才创建的讲评与答案讨论
```

PDF 是学习者正式使用和对外分发的版本。Markdown、YAML、LaTeX、Lab 与 grader 仍是可维护、可测试的课程源；Runtime 不从 PDF 反向解析状态或课程定义。

任何公开 PDF 都不包含标准答案、实现代码、隐藏测试输入或期望输出。讲评文件只能在学习者完成题集、Lab 和工程性作业后打开。

## Learning Guide 固定结构

1. **封面与本周能力。** 说明本周要获得的可观察能力，以及完成后解锁的下一问题。
2. **进入条件。** 明确必须已经掌握的前置证据，并给出回退位置。
3. **Gate 路线。** 每个 Gate 都有具体通过证据，不以“读过”或“运行成功”代替理解。
4. **精确材料。** 每项资源写明链接、只读范围、跳过范围、阅读问题和完成证据。
5. **Lab 与提示协议。** 写明命令、失败后允许获得的提示层级以及何时必须回退理论 Gate。
6. **提交清单。** 汇总概念、Lab、工程证据、真实故障与闭卷迁移要求。

## Problem Set 固定结构

1. **封面与课程位置。** Week 标题、它承接的前置知识、完成后进入哪一周、学习目标和提交物。
2. **使用说明。** 允许材料的范围、必须独立完成的部分、如何标注假设和如何记录不确定性。
3. **Part A: 概念与推导。** 定义、shape、数值手算和公式推导。
4. **Part B: 边界与全局位置。** 反例、适用条件、删除或替换机制的影响、与前后模块的连接。
5. **Part C: Lab 后工程问题。** 函数契约、测试设计、真实错误解释与替代方案取舍；要求引用自己的 Lab 证据。
6. **闭卷自检。** 3–5 分钟口述提示、跨周检索问题和反设计问题。
7. **提交清单。** 概念作业、Lab、工程作业、notes、demo 或回退任务的清晰勾选项。

## Week 0 题集范围

Week 0 的 PDF 只覆盖：二维 matrix shape、矩阵乘法、dot product、stable softmax，以及它们如何预演 Week 1 attention 信息流。它不要求实现 attention，不包含 Q/K/V 的公式推导，也不进入反向传播。

Part A 包含 shape 与 softmax 手算；Part B 要求构造非法矩阵与数值不稳定反例；Part C 要求解释 shape checker 的设计和测试。最后一页要求学习者闭卷画出从 token 表到 attention 权重的预演链。

## 质量与生成规则

- 每题注明题型（推导、反例、工程设计）与依赖的 Week 0 任务；不标注虚假的预计用时。
- 题目由易到难，前题产出要成为后题的可用输入。
- 两类 PDF 共用 `pdf/course-preamble.tex`，使用 A4 页面、一致字体、标题层级、页眉页脚、可点击链接和足够的手写留白。
- 所有数学表达式必须使用 LaTeX 数学环境，例如 `$X \in \mathbb{R}^{n \times d}$`、`\[QK^\top\]`；不得把公式作为普通文本排版。
- `scripts/course_pdf_targets.py` 是正式 PDF 清单。运行 `uv run python scripts/build_course_pdfs.py` 重建全部产物。
- 运行 `uv run python scripts/verify_course_pdfs.py` 检查文件存在、A4 页面、必需标题、文本边界并渲染 PNG。
- 自动验证不能代替视觉验收。发布前必须逐页检查分页、字体、中文、链接、公式、截断、重叠和无意义空白页。

Week 0 是共享模板的迁移基线，Week 1 是首个同时包含完整 Learning Guide 与 Problem Set 的参考实现。后续周次必须复用同一发布契约，而不是另建一套公开格式。
