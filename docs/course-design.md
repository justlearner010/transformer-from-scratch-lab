# 课程设计

## 材料使用原则

每个主题按以下顺序学习：

1. 观看 DeepLearning.AI 的 Transformers in Practice 对应内容。
2. 阅读 `Attention Is All You Need` 中与当周机制直接相关的小节。
3. 完成手算、shape 和反例小习题。
4. 进入 Lab；不提供实现答案。
5. 完成包含推导和机制解释的 Homework。
6. 用课后笔记纠正理解，并记录仍未解决的问题。

`The Annotated Transformer` 只在完成对应 Lab 后用于对照理解，不能作为解题前的实现参考。

## 评分原则

- P0：必须吃透。当前 P0 机制未通过，不进入下一关。
- P1：本轮必须完成。
- P2：只理解用途，留待复盘后决定是否深入。
- hidden autograder 按数值稳定性、shape/维度、mask 逻辑、组合顺序和边界输入反馈；不输出隐藏输入、期望矩阵或参考实现。
