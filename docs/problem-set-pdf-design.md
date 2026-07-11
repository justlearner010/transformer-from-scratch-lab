# Transformer Lab Problem Set PDF 设计

## 目标

为每个 Week 生成一份正式、可打印的题集 PDF。题集采用 CS70 风格的分层组织：资源引导、练习问题、独立完成的 Homework 和完成后的讲评严格分开。PDF 的作用是让学习者在离开代码和 AI 提示时，完成推导、反例和工程设计思考。

## 文件与发布边界

```text
problem-sets/week-XX-problem-set.pdf     公开题集，只含题目和自检
problem-sets/week-XX-problem-set.tex     LaTeX 题集源文件，便于版本控制与公式复现
solutions/week-XX-review.md              完成后才创建的讲评与答案讨论
```

同一 PDF 不包含标准答案、实现代码、隐藏测试输入或期望输出。讲评文件只能在学习者完成题集、Lab 和工程性作业后打开。

## PDF 固定结构

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
- PDF 使用清晰标题层级、页码、连续题号和足够的手写留白。
- 所有数学表达式必须使用 LaTeX 数学环境，例如 `$X \in \mathbb{R}^{n \times d}$`、`\[QK^\top\]`；不得把公式作为普通文本排版。
- 生成后必须渲染为 PNG 检查分页、字体、中文、表格、书写空间和公式；只在视觉检查通过后发布。
