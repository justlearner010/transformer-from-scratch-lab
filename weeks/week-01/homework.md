# Week 1 Homework：Attention 的计算与解释

请在自己的 `answers/week-01.md` 中完成。每题必须展示推导或理由；只写结论不得分。

1. 给定一个三 token、二维 Q/K/V 的小例子，完整计算第 2 个 query 的 score、scaled score、softmax 权重和输出。
2. 证明对任意常数 `c`，`softmax(z) = softmax(z + c)`；解释这一性质怎样用于数值稳定性。
3. 某实现对 `scores` 的 axis=0 做 softmax，而不是 axis=-1。用 shape 为 `(3, 3)` 的例子解释这意味着谁在竞争权重，以及为什么不符合 self-attention。
4. 写出至少两个 hidden autograder 应检查的边界情况，并说明各自能抓住什么错误。
5. 用 150–250 字解释：“attention 为什么是内容相关的读取，而不只是平均池化？”

## 提交标准

- 五题均完成。
- 至少一题包含手算过程。
- 第 4 题不能复述题面；必须给出具体边界输入与错误类型。
