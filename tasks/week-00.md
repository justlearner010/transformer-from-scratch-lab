# Week 0 任务链：从 token 表到 attention 预演

按 Gate 推进，而不是按天数推进。每一关的产物为下一关提供输入；不能用运行
结果替代手算、预测与解释。

## Gate 0：准备与定位

完成 [准备检查](../resources/week-00/pre-class.md)。

**解锁条件：** 环境可运行，能读出二维 shape，并知道 Week 0 是 Week 1 的
前置而非 attention 实现周。

## Gate 1：token 是行

画出三个二维 token 的 `(3, 2)` 表，标注每行和每列的含义。

**解锁条件：** 能区分改变一行与改变一列分别影响什么。

## Gate 2：投影是矩阵乘法

选择一个 `(2, 2)` 矩阵与 token 表相乘；先检查内维度，再手算一个输出元素。

**解锁条件：** 能预测 `(3, 2) @ (2, 2)` 的 shape 与一个元素的来源。

## Gate 3：匹配是点积

任选两行计算点积；改变一个数并解释分数如何变化。

**解锁条件：** 能说明点积是匹配分数，尚不是读取结果。

## Gate 4：读取比例来自 softmax

对一行三分数手算 stable softmax，验证每行和为 1，并说明同加常数为何不变。

**解锁条件：** 能说明数值稳定处理与归一化轴各保护什么性质。

## Gate 5：预演 attention

画出 `token 表 → 投影 → 两两点积 → 每行 softmax → 加权和`，为每个箭头
标出对应 Gate。完成 [概念练习](../resources/week-00/exercises.md) 的五题。

**进入 Lab：** 不看笔记说清五步的输入、输出和 shape。

## Gate 6：受约束实现

完成 [Week 0 Lab](../labs/week-00/README.md) 的关卡，记录一次真实或主动注入的
shape/边界失败。

## Gate 7：工程反馈与迁移

完成 [Lab 后工程作业](../resources/week-00/homework.md) 和
[笔记模板](../resources/week-00/notes-template.md)。用自己的输入验证一个可相乘
和一个不可相乘例子，并说明它们如何影响 Week 1 的 Q/K/V。

**完成规则：** 未关闭的 shape、点积或 stable softmax 缺口会阻止进入 Week 1。
