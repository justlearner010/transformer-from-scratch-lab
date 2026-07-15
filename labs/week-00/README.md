# Week 0 Lab：用 NumPy 看见矩阵乘法

## 你在做什么，为什么现在做？

Week 1 中的 \(Q=XW_Q\)、\(K=XW_K\)、\(V=XW_V\) 都是矩阵乘法。这个 Lab 不让你提前实现 attention，而是把一次矩阵乘法拆回最小动作：先知道什么是合法矩阵，再知道 shape，再算一个位置，最后才组装整个输出。

你会直接使用小型 `numpy.ndarray`，但不是把 `@` 当作黑箱。完成本 Lab 后，你应能看着两个矩阵，预测能否相乘、输出 shape，以及任意一个输出元素从哪里来。

## 规则

- 只编辑 `src/contracts.py`；不要改公开测试或评分器。
- 每次只完成当前关卡。后面的函数必须复用前面已完成的函数。
- 关卡 5 中不能使用 `@` 或 `np.matmul`；对照实验才可以使用 `@`。
- 不要原地修改输入矩阵。
- 先用评分器的失败类别定位问题；不要索取实现答案。

## 关卡链

| 关卡 | 函数 | 此函数唯一负责什么 | 允许依赖 | 通过后你应能回答 |
| --- | --- | --- | --- | --- |
| 1 | `require_matrix` | 判断一个对象是否是可用的二维数值 `np.ndarray`。 | 无 | 向量、Python list、空矩阵为什么不能作为本 Lab 的矩阵？ |
| 2 | `matrix_shape` | 返回合法矩阵的 `(rows, columns)`。 | `require_matrix` | token 表的每一行和每一列各代表什么？ |
| 3 | `require_multipliable` | 只检查 `left × right` 的内维度是否匹配。 | `matrix_shape` | 为什么 `(2, 3)` 可以乘 `(3, 4)`，却不能乘 `(2, 4)`？ |
| 4 | `dot_entry` | 只计算结果矩阵的一个位置。 | `require_multipliable` | 输出的第 `i,j` 个位置由 left 的哪一行和 right 的哪一列构成？ |
| 5 | `matmul_from_entries` | 通过重复调用 `dot_entry` 组装完整乘积。 | `require_multipliable`、`dot_entry` | 为什么输出 shape 是 `(left_rows, right_columns)`？ |
| 6 | `describe_product` | 只解释两个 shape 的关系，不计算数值乘积。 | `matrix_shape`、`require_multipliable` | 如何让未来的自己不用读堆栈就知道哪个矩阵不对？ |

## 推荐操作顺序

```text
关卡 1：合法二维 NumPy 矩阵
  -> 关卡 2：行数、列数与 token 表
  -> 关卡 3：矩阵相乘的内维度
  -> 关卡 4：一个输出元素的点积
  -> 关卡 5：完整手写矩阵乘积
  -> 关卡 6：可读的 shape 诊断
  -> mini demo：与 NumPy @ 对照
```

每完成一关都运行评分器；它只会告诉你关卡、失败类别、思考提示与解锁状态。

```bash
uv run pytest labs/week-00/tests -v
uv run python labs/week-00/run_grade.py
```

## mini demo：把理解与 NumPy 工具连起来

六关通过后，自己创建两个兼容但非方阵的例子，以及一个不兼容例子。

对每个兼容例子：

1. 写下两个输入 shape 与预期输出 shape；
2. 用 `matmul_from_entries` 得到手写结果；
3. 再使用 `left @ right` 得到 NumPy 对照结果；
4. 验证两者一致，并记录一个输出位置来自哪一行、哪一列。

对不兼容例子：调用 `describe_product`，记录它怎样解释不匹配的内维度。

## 完成后

完成 [工程性作业](../../homework/week-00-engineering.md)，并在 [笔记模板](../../notes/week-00-template.md) 中记录一次真实的 grader 反馈和你如何定位它。之后再开始 Week 1 的 Q/K/V 投影。
