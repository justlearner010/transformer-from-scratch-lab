# Week 1 Lab：从契约实现 Attention

## 你在做什么，为什么现在做？

Week 0 分别验证了矩阵投影、点积与 softmax。本 Lab 要你把它们按明确契约
组合为单头 attention，并用失败类别区分 shape、数值稳定性与机制错误。

你将自行实现 `labs/week-01/src/attention.py` 的函数。只允许使用 NumPy；不得复制外部实现或查看隐藏评分样例。

## 关卡

| 关卡 | 目标 | 解锁条件 |
| --- | --- | --- |
| 0 | 熟悉函数契约和 shape | 公开 smoke test 可运行。 |
| 1 | 实现数值稳定的 softmax | hidden autograder 的数值稳定性与轴检查通过。 |
| 2 | 实现 Q/K/V 投影 | hidden autograder 的 shape、输入不变性和错误输入检查通过。 |
| 3 | 实现 scaled dot-product attention | hidden autograder 的缩放、权重与输出性质检查通过。 |
| 4 | 完成故障诊断 | 根据 grader 的类别报告定位一个故意注入的错误，并写下原因与修复验证。 |

## 给你的约束

- 只编辑 `src/attention.py`；不要修改公开测试或评分器。
- `softmax`、`project_qkv` 与 attention 的输入输出、shape 与异常边界以函数
  docstring 为准；后续关卡必须消费先前实现的契约。
- 只使用 NumPy；不调用框架 attention API，不查看隐藏评分样例。

## 运行与反馈

```bash
uv run pytest labs/week-01/tests -v
uv run python labs/week-01/run_grade.py
```

公开测试只检查脚手架；本地 `.grader/` 存在时，评分器才会执行隐藏检查并显示失败类别。

## 提示协议

第 1 次失败：阅读错误类别对应的思考问题。

第 2 次失败：打印相关张量的 shape 和一行数值。

第 3 次失败：回到本周理论题，不直接找实现答案。

## Lab 完成后

完成 [Lab 后工程作业](../../resources/week-01/homework.md)，再用
[笔记模板](../../resources/week-01/notes-template.md) 记录一个真实失败与一次
“只改 V”的迁移预测。没有未解释的 P0 缺口后，才讨论 causal mask。
