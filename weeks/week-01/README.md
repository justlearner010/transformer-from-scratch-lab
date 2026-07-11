# Week 1：Attention 是如何选择信息的？

## 本周问题

一个 token 如何决定“该从哪些 token 读取多少信息”？为什么这种读取既需要相似度，也需要归一化？

## P0 机制

- token 向量、矩阵 shape 与 Q/K/V 投影（难度 2/4）
- stable softmax（难度 3/4）
- scaled dot-product attention（难度 3/4）

## 本周顺序

1. 完成 [课前引导](pre-class.md)。
2. 完成 [理论材料与阅读问题](materials.md)。
3. 独立完成 [小习题](exercises.md)。
4. 完成 `lab/` 的关卡 0–2。
5. 提交 [Homework](homework.md) 的书面答案。
6. 使用 [课后笔记模板](notes-template.md) 复盘。

本周不进入 causal mask、LayerNorm、FFN 或训练。
