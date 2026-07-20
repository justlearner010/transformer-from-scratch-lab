# Week 0 学习记录：从 NumPy 矩阵到一次投影

> 学习证据：Week 0 Lab 已通过关卡 1–4；下一步是用 `dot_entry` 组装完整矩阵乘积。

## 这周实际在理解什么？

我不是在背“矩阵可以相乘”的规则，而是在为 Week 1 的 \(Q=XW_Q\)、\(K=XW_K\)、\(V=XW_V\) 建立可执行的直觉：一次投影就是 token 表与权重矩阵相乘；一次输出位置来自一整行和一整列的点积。

这条路径是：

\[
\text{合法 NumPy 矩阵}
\rightarrow \text{shape}
\rightarrow \text{可乘性}
\rightarrow \text{一个输出位置}
\rightarrow \text{完整矩阵乘积}
\]

## 已经建立的概念

### 1. 一个参数不一定是一份数据

`require_matrix(value, *, name)` 中：

- `value` 是真正需要验证的候选矩阵；
- `name` 是错误信息里的标签，例如 `"left"` 或 `"right"`。

因此维度、shape 和 dtype 都属于 `value`，不是 `name`。`name` 的作用是让后续错误从“输入不合法”变成“left 的输入不合法”，从而在两个矩阵同时参与运算时仍能定位问题。

### 2. 验证矩阵时，检查顺序也是设计的一部分

我采用的顺序是：

```text
先确认是 np.ndarray
  → 再确认是二维
  → 再确认 dtype 是 numeric
  → 最后确认行数和列数都非零
```

这个顺序避免了把属性错误泄漏给调用者。例如，一个 Python list 根本没有数组的维度语义；在确认类型以前读取 `.ndim`，得到的是无关的运行时错误，而不是我定义的输入边界。

对于数组本身：

| 属性 | 回答的问题 |
| --- | --- |
| `.ndim` | 有几个维度？ |
| `.shape` | 每个维度的长度是什么？ |
| `.dtype` | 元素存储为什么类型？ |

数值 dtype 用正向判断：它是否属于 NumPy 的数值类型族，而不是只排除字符串。这样 `object`、布尔、日期时间等不适合本 Lab 的数据也不会被误放行。

### 3. 矩阵相乘由内维度决定

\[
(m,n) \times (n,p) \rightarrow (m,p)
\]

左矩阵的列数必须等于右矩阵的行数；这条相等的维度是共享维度。结果的行数来自左矩阵，结果的列数来自右矩阵。

## 我犯过的错误，以及它们说明什么

| 现象 | 实际原因 | 修正后的理解 |
| --- | --- | --- |
| 读取了 `name.ndim` | `name` 是错误标签字符串，不是矩阵。 | 数据与诊断标签应分开看。 |
| 使用了 `type(object)` 来检查输入 | `object` 是 Python 内置类型名，不是函数参数 `value`。 | 类型检查必须针对当前输入对象；`isinstance` 的表达更直接。 |
| 将错误抛成 `TypeError` | 本 Lab 的函数契约要求把无效输入统一报告为 `ValueError`。 | 除了 Python 语义，还要遵守模块之间约定的错误接口。 |
| 把输出列数取成 left 的列数 | left 的列数是共享维度，不是输出列数。 | 输出 shape 永远回到 \((m,n)\times(n,p)\rightarrow(m,p)\) 重新推导。 |
| 用两个单独元素相乘计算输出位置 | 一个输出位置不是一项乘法，而是一整行与一整列的点积。 | 必须先取对应行、对应列，再沿共享维度求和。 |
| 把 `row=1` 写成 `row-1` | NumPy 使用从零开始的索引。 | 目标位置 `(row, column)` 应直接对应输出矩阵的索引；长度本身已经越界。 |

## 第 4 关的关键图像

设：

\[
L \in \mathbb{R}^{m\times n},\qquad
R \in \mathbb{R}^{n\times p},\qquad
C=LR
\]

则：

\[
C_{i,j}=\sum_{k=0}^{n-1}L_{i,k}R_{k,j}
\]

计算 `C[row, column]` 时：

```text
left 的第 row 行
× right 的第 column 列
→ 两个长度为 n 的向量
→ 点积
→ 一个标量
```

其中 NumPy 切片的语义是：固定行、取全部列；或固定列、取全部行。这里的 `:` 表示该维度全部取出。

## 当前证据与下一步

我已通过 hidden grader 的关卡 1–4。公开 smoke test 只保证脚手架可导入；真正的机制检查应运行：

```bash
uv run pytest labs/week-00/tests -v
uv run python labs/week-00/run_grade.py
```

下一步是关卡 5：创建 shape 为 \((m,p)\) 的输出矩阵，并让每一个输出位置都复用 `dot_entry`。这里不重新实现点积，也不使用 `@`；完成后才用 NumPy 的矩阵乘法作为对照实验。

## 和 Week 1 的连接

Week 1 的 \(Q=XW_Q\) 并没有引入另一种神秘计算。它首先就是本周的矩阵投影：token 行仍然对应 token，权重矩阵改变的是每个 token 的特征表示。理解一次小矩阵的完整乘法，才有能力在 Q/K/V 的 shape 出错时从机制而不是猜测开始排查。
