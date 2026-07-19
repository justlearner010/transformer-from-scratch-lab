# Week 0 Lab：Shape Checker

## 你在做什么，为什么现在做？

Week 1 的 Q、K、V 都是矩阵乘法，attention score 也是矩阵乘法。若你只能等 NumPy 报错，再猜哪里不对，后面会把机制问题误认为代码问题。

本 Lab 要你写一个小而严格的 shape checker：它不计算 attention，只检查两个二维矩阵是否能相乘，并把错误解释成“左边需要什么、右边实际给了什么”。完成后，你应能在写 Week 1 前预测每一次矩阵乘法的输出 shape。

## 关卡

| 关卡 | 你实现的行为 | hidden autograder 检查 | 解锁条件 |
| --- | --- | --- | --- |
| 0 | 阅读 `src/contracts.py` 的函数契约 | 导入、签名和公开测试 | 能运行测试与评分器。 |
| 1 | 验证二维 shape 的合法性 | 非二维、零/负维度、错误输入类型 | 所有边界输入被清晰拒绝。 |
| 2 | 判断能否相乘并返回输出 shape | 内维度相等/不等、非方阵 | 结果正确且不依赖实际矩阵数值。 |
| 3 | 输出可解释诊断 | 错误类别、左右内维度、可行动提示 | 不只抛出原始 NumPy 异常。 |
| 4 | 自主 mini demo | 自选两个正确与一个错误例子 | 能在不看测试的情况下解释三个结果。 |

## 给你的约束

- 只编辑 `src/contracts.py`；不要改测试或评分器。
- 不要实际创建大矩阵；本 Lab 只操作 shape tuple。
- 对合法输入，`matrix_product_shape` 返回 `(left_rows, right_columns)`。
- 对不合法输入，抛出 `ValueError`；错误消息必须包含 `left` 或 `right`，并说明问题属于维度数、维度值或内维度。

## 运行与反馈

```bash
uv run pytest labs/week-00/tests -v
uv run python labs/week-00/run_grade.py
```

公开测试只验证脚手架能运行。评分器存在时会报告 `shape/维度` 或 `边界输入` 类别和一个思考提示。先根据提示自己修；不要索取参考实现。

## Lab 完成后

立刻完成 [工程性作业](../../resources/week-00/homework.md)，再用
[笔记模板](../../resources/week-00/notes-template.md) 记录一个真实错误或你为
预防错误做的检查。随后开始 Week 1。
