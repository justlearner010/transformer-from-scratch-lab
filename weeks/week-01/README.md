# Week 1：Attention 如何按内容读取信息？

## 为什么现在学这个？

Week 0 已经验证了矩阵投影、点积与 softmax 的最小前置。现在新增的不是更多
术语，而是把这些步骤按因果顺序组合成“按内容读取 value”的 attention。

## 能力问题

给定一个无 batch 维的 token 矩阵，能否独立解释、实现并诊断单头
scaled dot-product attention：每个 query 如何比较 keys、把分数稳定地
变成一行权重，并用这些权重读取 values？

本周按知识门槛推进，不按天数推进。通过一个 gate 后可立即进入下一
gate；若 P0 机制存在缺口，回到对应 gate 补足。

## 当前证据、范围与非目标

- Week 0 hidden grader 已通过矩阵验证、单位置点积、完整乘法与诊断；
  矩阵乘法作为已验证的硬前置，只做检索桥接，不重新开 Lab。
- Q/K/V 的语义、score 行列含义、稳定 softmax 与 attention 输出的掌握
  尚无直接证据，按 `unknown` 开始验证。

## 依赖与重要性视图

| 节点 | 类型 | 当前 → 目标 | 依赖角色 | 优先级与理由 | 任务层 |
| --- | --- | --- | --- | --- | --- |
| 矩阵投影与 shape | mechanism | D3 → D3 | 硬前置，已满足 | P0（全局基础）；本周仅检索 | T1 |
| Q/K/V 的角色 | concept + mechanism | unknown → D3 | scores 的硬前置 | P1：必须独立投影和解释 | T1 → T3 |
| `scores = Q @ K.T` | mechanism | unknown → D4 | 权重的硬前置 | P0：转置与行列语义决定后续计算 | T1 → T4 |
| `/sqrt(d_k)` | mechanism | unknown → D3 | score 的共前置 | P1：要说明并用性质检查验证 | T1 → T3 |
| row-wise stable softmax | mechanism + contract | unknown → D4 | 权重的硬前置 | P0：数值稳定性和 axis 错误都会破坏注意力 | T1 → T4 |
| `weights @ V` | mechanism | unknown → D4 | 输出的硬前置 | P0：定义内容读取而非仅计算分数 | T1 → T4 |
| 输入边界与不变性 | contract + diagnosis | unknown → D3 | 可信实现的支持节点 | P1：需要明确错误与不变性检查 | T3 → T4 |
| 完整 attention 组合 | integration | 未组合 → D4 | 整合节点 | P0：本周最终能力，要求独立迁移 | T3 → T5 |
| 可视化呈现 | procedure | unknown → D2 | 支持观察 | P2：只用于 demo，不单独开 Lab | T2 |
| causal mask、多头、block、训练 | orientation | D0 → D1 | 下游 | P3：只说明下一步位置 | T0 |

## 依赖图与范围

```text
Week 0 矩阵投影
  → Q/K/V
  → scores = Q @ K.T
  ├→ scores / sqrt(d_k)
  └→ row-wise stable softmax
       → weights @ V
       → 完整单头 attention
       → 独立诊断 demo
```

范围：单样本、单头、NumPy 前向计算、无 causal mask。

非目标：batch、多头、位置编码、residual、LayerNorm、FFN、训练、生成和
框架 attention API。

## 学习入口与门控顺序

1. 完成 [课前引导](../../resources/week-01/pre-class.md) 的检索桥接。
2. 阅读 [材料](../../resources/week-01/materials.md)，完成其中四个问题。
3. 依次完成 [知识门控任务](../../tasks/week-01.md) 的 Gate 1–4。
4. 通过 Gate 4 后，独立完成 [Lab](../../labs/week-01/README.md) 的 Gate 0–3。
5. 完成 [Lab 后工程作业](../../resources/week-01/homework.md)、故障诊断和自主 demo。
6. 用 [课后笔记模板](../../resources/week-01/notes-template.md) 记录真实证据，再判定是否解锁
   causal mask。

## 完成定义与下一步

- 所有 P0 Lab 检查通过，且没有未解释的 shape、axis、数值稳定性或
  `weights @ V` 缺口；
- 完成一个未见过的数值迁移题和一个主动注入的故障；
- 能在 3–5 分钟内闭卷解释输入、计算、输出、必要性和一种失败方式；
- 自主 demo 不复制 Lab 内部实现，并先预测后验证至少一个权重变化。

完成后解锁：在同一数据流中讨论 causal mask 应插入何处；是否实现 mask
留给下一阶段，而不是在本周混入。
