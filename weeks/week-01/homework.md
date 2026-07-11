# Week 1 Homework：Attention 的计算与解释

请在自己的 `answers/week-01.md` 中完成。每题必须展示推导或理由；只写结论不得分。

1. 给定一个三 token、二维 Q/K/V 的小例子，完整计算第 2 个 query 的 score、scaled score、softmax 权重和输出。
2. 证明对任意常数 `c`，`softmax(z) = softmax(z + c)`；由此推导稳定实现的计算形式。
3. 某实现对 `scores` 的 axis=0 做 softmax，而不是 axis=-1。用一个具体 `(3, 3)` 例子说明谁在竞争权重，以及为什么不符合 self-attention。
4. 推导缩放项 `sqrt(d_k)` 的作用：假设 Q、K 元素独立、均值为 0、方差为 1，讨论 dot product 的方差如何随 `d_k` 变化。
5. 设计三个 hidden autograder 测试：一个测试极端数值、一个测试轴、一个测试 Q/K 维度不匹配。每项给出输入、应检查的性质和能抓住的错误。
6. 给出一个“输出 shape 正确但机制错误”的 attention 实现反例，并说明仅看 shape 为什么不够。
7. 用 250–350 字回答：“attention 为什么是内容相关的读取，而不只是平均池化？”必须引用一个自己构造的数值例子。

## 提交标准

- 七题均完成；第 1、2、4 题必须展示完整推导。
- 第 5 题必须包含具体数组，而不是抽象描述。
- 第 7 题必须用自己的数值例子支撑解释。
- 完成后按 `notes-template.md` 写出一个真实错误或预防该错误的测试设计。
