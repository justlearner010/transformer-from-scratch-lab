# Transformer From Scratch Lab

## Week 0 Problem Set: 先看懂信息怎样流动

### 课程位置

Week 0 不实现 attention。你要建立的是 Week 1 的前置能力：看懂 token 表、矩阵乘法、点积和 stable softmax 如何连成一条信息流。

### 提交物

- 本题集的书面解答；
- Week 0 Shape Checker Lab；
- 一个 Lab 或工程设计反馈记录；
- 闭卷信息流图。

### 使用规则

Part A 与 Part B 必须在进入 Lab 前独立完成。Part C 必须在完成 Lab 后，引用自己的输入、输出、测试或评分反馈。可写下尚未解决的问题，但不能用“我不确定”代替推导或反例。

## Part A: 概念与推导

### A1. Token 表与 shape（推导；依赖任务 0.1）

令 `X` 是三个 token 的二维表示，shape 为 `(3, 2)`；令 `W` 的 shape 为 `(2, 4)`。

1. 写出 `X @ W` 的 shape。
2. 用一句话说明输出的每一行和每一列分别代表什么。
3. 令 `X[1, 0]` 增加 1。输出矩阵的哪些元素可能变化？为什么？

### A2. 矩阵乘法不是逐元素乘法（推导；依赖任务 0.2）

给定

```text
A = [[1, 2],
     [0, 3],
     [4, 1]]

B = [[2, 1],
     [1, 0]]
```

1. 手算 `A @ B` 的第 1 行与第 3 行。
2. 写出一般元素 `(A @ B)[i, j]` 的计算规则。
3. 解释为什么这个规则允许每个 token 经过同一组权重后获得新的特征。

### A3. Dot product 与匹配分数（推导；依赖任务 0.3）

令 `u = [1, 2]`，`v = [3, -1]`，`w = [1, 1]`。

1. 计算 `u . v` 与 `u . w`。
2. 若 `u` 是一个 query，`v` 和 `w` 是两个 key，哪个 key 在这个极小例子中更匹配？
3. 解释为何这个分数还不能直接作为“读取多少信息”的权重。

### A4. Stable softmax（推导；依赖任务 0.4）

对 `z = [2, 1, 0]`：

1. 写出 softmax 的三个分量，并验证它们的和为 1。
2. 证明对任意常数 `c`，`softmax(z) = softmax(z + c)`。
3. 用第 2 问解释稳定实现为什么可以在 exponentiation 前减去最大 score。

## Part B: 使用边界与全局位置

### B1. 不合法的 shape（反例；依赖任务 0.2）

构造两个二维矩阵 shape，使它们不能相乘。

1. 明确写出左矩阵列数和右矩阵行数。
2. 写出你期望 Shape Checker 输出的错误类别和错误信息必须包含的内容。
3. 说明如果只让 NumPy 抛出原始异常，学习者会缺少哪一条机制信息。

### B2. Softmax 的错误轴（反例；依赖任务 0.4）

设 score matrix 的 shape 为 `(3, 3)`，每一行表示一个 query 对三个 key 的分数。

1. 解释沿最后一维归一化意味着谁在竞争权重。
2. 解释沿第 0 维归一化时谁在竞争权重。
3. 构造一个最小 score matrix，使这两种归一化产生显著不同的解释。

### B3. Week 0 在整体中的位置（全局连接；依赖任务 0.5）

画出下列信息流，并为每个箭头写上它在 Week 0 已经学过的操作：

```text
token table -> Q/K/V projections -> score matrix -> row-wise weights -> weighted values
```

最后用 150–200 字解释：为什么 Week 0 还没有真正实现 attention，但已经为 Week 1 的每个计算步骤准备了前置能力？

## Part C: Lab 后工程问题

### C1. Shape Checker 的契约（工程设计）

完成 Lab 后回答：为什么 `validate_matrix_shape` 与 `matrix_product_shape` 要拆成两个函数？为每个函数写出一个它单独负责的错误场景。

### C2. 一个真实错误（工程诊断）

选择一次你在 Lab 中遇到的失败，或主动注入一个错误 shape。

1. 写下输入、观察到的现象和错误类别。
2. 提出原因假设。
3. 写出验证该假设的最小测试。
4. 说明修复后你对矩阵契约的理解发生了什么变化。

### C3. 从 Lab 到 Week 1（工程迁移）

Week 1 将把 token 表分别乘以 `W_Q`、`W_K`、`W_V`。说明 Shape Checker 在这三次投影中能预先防止什么错误；再说明它不能防止什么“shape 正确但机制仍错误”的问题。

## 闭卷自检与提交清单

不看材料，用 3–5 分钟解释：

1. 一个 `(3, 2)` token 表经过 `(2, 4)` 投影后发生了什么？
2. dot product、softmax 与加权和在 Week 1 attention 中分别扮演什么角色？
3. 给出一种 shape 正确但机制错误的 attention 实现方式。

- [ ] Part A 与 Part B 已在 Lab 前完成。
- [ ] Shape Checker Lab 的公开与 hidden tests 已通过。
- [ ] Part C 引用了自己的 Lab 证据。
- [ ] 已记录一个真实错误或主动注入错误的诊断过程。
- [ ] 能闭卷画出 Week 0 到 Week 1 的信息流。
