# 课程设计

## 课程强度与节奏

这是一个自定节奏、无外部截止日期的高强度课程。每周的推荐投入为 30–35 小时；P0 机制没有通过书面题、Lab 和口头解释三重检查时，不能因为进入下一周而跳过。每周包含：课前引导、材料、按知识点拆分的练习、无答案 Lab、理论 Homework、课后 notes 和补做清单。

## 材料使用原则

每个主题按以下顺序学习：

1. 观看 DeepLearning.AI 的 Transformers in Practice 对应内容，先建立直觉。
2. 阅读 Dive into Deep Learning 对应章节，补足数学、图示和练习。
3. 阅读 `Attention Is All You Need` 中与当周机制直接相关的小节，回到原始定义。
4. 完成手算、shape、证明与反例小习题。
5. 进入 Lab；不提供实现答案。
6. 完成包含推导、错误诊断和测试设计的 Homework。
7. 用课后笔记纠正理解，并记录仍未解决的问题。

`The Annotated Transformer` 只在完成对应 Lab 后用于对照理解，不能作为解题前的实现参考。

## 每周题目梯度

- **A 类：基础计算。** 定义、shape、手算、最小 NumPy 检查。
- **B 类：推导与反例。** 证明等价性、解释缩放/归一化、构造失败案例。
- **C 类：系统诊断。** 设计 hidden test、定位训练或数值错误、比较可行设计。

Homework 必须包含 A/B/C 三类题，且至少一题要求完整推导、至少一题要求具体的边界输入或失败机制。完成后先按 rubric 自评，再向 AI 口头解释；AI 只能追问和评分，不能直接给解答。

## 四周 syllabus

| 周 | P0 知识点 | 阅读重点 | Lab 阶梯 | Homework 核心 |
| --- | --- | --- | --- | --- |
| 0 | shape、矩阵乘法、softmax、交叉熵、梯度直觉 | D2L 线性代数/微积分预备 | 环境与输入输出契约 | 手算、导数和 shape 诊断 |
| 1 | Q/K/V、scaled dot-product attention | D2L 11.1–11.3；论文 3.2.1 | stable softmax → attention | 稳定性证明、轴错误反例、hidden test 设计 |
| 2 | causal mask、LayerNorm、FFN、残差、block | D2L Transformer；论文 decoder/block | mask → self-attention → block | mask 证明、组合顺序与梯度流分析 |
| 3 | embedding、交叉熵、反向传播、生成 | D2L 训练与 Transformer 相关章节 | 闭卷独立字符级 demo | 训练失败诊断与实验报告 |
| 4 | 机制综合与工程选择 | 原论文整体回读；Lab 后对照 Annotated Transformer | 从零重构与压力测试 | 闭卷综合题和大项目设计 memo |

## 评分原则

- P0：必须吃透。当前 P0 机制未通过，不进入下一关。
- P1：本轮必须完成。
- P2：只理解用途，留待复盘后决定是否深入。
- hidden autograder 按数值稳定性、shape/维度、mask 逻辑、组合顺序和边界输入反馈；不输出隐藏输入、期望矩阵或参考实现。
