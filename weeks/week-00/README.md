# Week 0：先看懂信息怎样流动

## 为什么现在学这个？

Week 1 会让每个 token 根据内容读取其他 token。那会反复出现矩阵投影、点积、
softmax 与 shape；若这些只停留在术语层，后续很容易把机制错误误判成代码错误。

## 能力问题

给定一个极小 token 矩阵和权重矩阵，能否独立追踪每一步的数值来源与 shape，
并预演它们如何组成 attention？

## 当前证据、范围与非目标

- 当前证据：无机制前置周；从二维数组、矩阵乘法、点积与 stable softmax 的
  最小例子开始。
- 范围：无 batch 的 NumPy 矩阵、shape、单位置点积与行 softmax。
- 非目标：Q/K/V 的完整实现、causal mask、多头、训练与框架 API。

## 依赖与重要性视图

| 节点 | 角色 | 优先级 | 本周证据 |
| --- | --- | --- | --- |
| token 行列语义 | attention 输入的硬前置 | P0 | 画表并解释行列 |
| 矩阵乘法与 shape | Q/K/V 投影的硬前置 | P0 | 手算、边界与 Lab |
| 点积 | score 的硬前置 | P0 | 最小数值变化 |
| stable softmax | attention 权重的硬前置 | P0 | 手算与极端数值解释 |
| attention 全链路 | Week 1 的下游预演 | P1 | 箭头图与闭卷口述 |

## 学习入口与门控顺序

1. [准备检查](../../resources/week-00/pre-class.md)
2. [材料](../../resources/week-00/materials.md)
3. [Gate 任务链](../../tasks/week-00.md)
4. [Week 0 Lab](../../labs/week-00/README.md)
5. [Lab 后工程作业](../../resources/week-00/homework.md) 与
   [笔记模板](../../resources/week-00/notes-template.md)

## 你的学习资产

- [Week 0 学习记录](../../homework_answer/week-00/learning-record.md)：你已经形成的
  shape、点积、输入边界与失败诊断证据；它是 Week 1 的前置资产，不是隐藏的旧资料。
- [`labs/week-00/src/contracts.py`](../../labs/week-00/src/contracts.py)：你的可运行
  Week 0 实现；需要回顾某个机制时，优先把记录与对应 Lab 代码一起看。

正式阅读版可使用 [Week 0 Resources PDF](../../resources/week-00.pdf)，正式题集
可使用 [Week 0 Problem Set PDF](../../problem-sets/week-00-problem-set.pdf)。它们是
支持材料，不替代上面的 Gate 路径。

## 完成定义与下一步

- Lab 关卡与公开检查通过，且能解释一次 shape 或边界失败；
- 完成一个未见过的矩阵乘法/点积迁移题；
- 能在 3–5 分钟内闭卷说明 token 表、投影、点积与 softmax 如何连接；
- 没有未解释的 P0 shape 或数值稳定性缺口。

完成后进入 [Week 1：Attention 如何按内容读取信息？](../week-01/README.md)。
