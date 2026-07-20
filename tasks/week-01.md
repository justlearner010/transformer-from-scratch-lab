# Week 1 任务链：从匹配分数到内容读取

本任务链按知识依赖推进。P0 gate 必须通过才能解锁下一条；P1 gate 的缺口
可以在同一阶段补足，但不能被完整组合掩盖。

## Gate 0：shape trace（P0，T1 → T3）

完成 `resources/week-01/pre-class.md` 的闭卷桥接。若不能写出 `QK^T` 与
`weights @ V` 的 shape，回到 Week 0；然后立即运行 `shape` micro-lab。不要直接
进入下一机制。

## Gate 1：score probe（P0，T1 → T4）

完成材料中的对应问题后，运行 `score` micro-lab，并构造一次遗漏 `K.T` 的反例。

**解锁条件：** 能解释 `scores[i,j]` 与 `K.T` 的必要性。

## Gate 2：stable softmax（P0，T1 → T4）

预测极端数值与错误 axis 的结果，运行 `softmax` micro-lab，再完成对应练习。

**解锁条件：** 能说明减最大值和 `axis=-1` 保护的性质。

## Gate 3：value read（P0，T1 → T4）

先预测仅改变一行 V 后哪些量会变化，运行 `value` micro-lab，再记录观察结果。

**解锁条件：** 能区分匹配权重与读取内容的职责。

## Gate 4：Q/K/V projection（P1，T2 → T3）

完成 `project_qkv` 的受约束实现，并验证 shape、错误输入与不原地修改。

**解锁条件：** 能解释 Q/K/V 三个投影各自消费和保留什么。

## Gate 5：组合 Attention（P0，T3 → T5）

运行 `compose` micro-lab 后实现 `scaled_dot_product_attention`。它只能复用
projection、score、softmax 与 value-read 的已验证接口；不得把局部机制重新塞成一
段不可诊断的大函数。

## Gate 6：工程反馈与迁移（P1，T4 → T5）

完成 `resources/week-01/homework.md` 与 `resources/week-01/notes-template.md`，然后做一个独立的
attention inspector：调用已实现的公开接口，显示 Q/K/V、scores、weights、
output 的 shape 和指定一行的摘要。不得复制 Lab 内部实现。

至少做两项预测：

1. 哪个 query 更关注哪个 key；
2. 仅改变一个 V 行后，哪些量应保持不变。

记录预测、结果和解释。通过后才讨论 causal mask 位于 softmax 前的位置。
