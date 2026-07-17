# Week 1 任务链：从匹配分数到内容读取

本任务链按知识依赖推进。P0 gate 必须通过才能解锁下一条；P1 gate 的缺口
可以在同一阶段补足，但不能被完整组合掩盖。

## Gate 0：调用前置能力（P0，T1）

完成 `resources/week-01/pre-class.md` 的闭卷桥接。若不能写出 `QK^T` 与
`weights @ V` 的 shape，回到 Week 0；不要直接进入 Lab。

## Gate 1：读懂信息流（P1，T1）

完成材料中的四个问题和 `resources/week-01/exercises.md` 的 Gate 1。产物是一张 shape 表和一次
“只改 V”预测。

**解锁条件：** 能解释 Q/K/V 的不同职责。

## Gate 2：建立 score 语义（P0，T1 → T4）

完成 `resources/week-01/exercises.md` 的 Gate 2，并构造一次转置错误的反例。

**解锁条件：** 能解释 `scores[i,j]`、每行竞争关系和 `K.T` 的必要性。

## Gate 3：建立权重契约（P0，T1 → T4）

完成 `resources/week-01/exercises.md` 的 Gate 3。必须留下一个极端数值例子和一个错误 axis 的
二维例子。

**解锁条件：** 能说明 stable softmax、`axis=-1` 与 `sqrt(d_k)` 分别保护
什么性质。

## Gate 4：证明 output 是读取 V（P0，T1 → T4）

完成 `resources/week-01/exercises.md` 的 Gate 4，并先预测后验证一次只改变 V 的实验。

**解锁条件：** 能解释 weights 和 V 的职责边界，以及输出 shape 的来源。

## Gate 5：受约束实现（P0/P1，T3）

按 `labs/week-01/README.md` 依次完成：

1. Gate 0：阅读三个函数契约，运行公开 smoke tests；
2. Gate 1：`softmax`；
3. Gate 2：`project_qkv`；
4. Gate 3：`scaled_dot_product_attention`。

每次 hidden grader 失败，只记录类别、原因假设和最小验证；不得要求实现
答案或修改测试以通过。

## Gate 6：工程反馈与迁移（P0，T4 → T5）

完成 `resources/week-01/homework.md` 与 `resources/week-01/notes-template.md`，然后做一个独立的
attention inspector：调用已实现的公开接口，显示 Q/K/V、scores、weights、
output 的 shape 和指定一行的摘要。不得复制 Lab 内部实现。

至少做两项预测：

1. 哪个 query 更关注哪个 key；
2. 仅改变一个 V 行后，哪些量应保持不变。

记录预测、结果和解释。通过后才讨论 causal mask 位于 softmax 前的位置。
