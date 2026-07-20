# Week 1 Lab：从契约实现 Attention

## 你在做什么，为什么现在做？

Week 0 分别验证了矩阵投影、点积与 softmax。本 Lab 要你把它们按明确契约
组合为单头 attention，并用失败类别区分 shape、数值稳定性与机制错误。

你将自行实现 `labs/week-01/src/attention.py` 的函数。只允许使用 NumPy；不得复制外部实现或查看隐藏评分样例。

## Micro-Lab 顺序

| 顺序 | 目标 | 解锁条件 |
| --- | --- | --- |
| 0 | shape trace | 预测后运行 shape 实验，解释 `K.T`。 |
| 1 | score probe | 构造一次不转置的反例。 |
| 2 | stable softmax | 验证极端数值与最后一维归一化。 |
| 3 | value read | 只改变 V，观察 output 而非 weights。 |
| 4 | Q/K/V projection | 完成投影函数的边界与不变性检查。 |
| 5 | compose attention | 只组装已验证组件，不重新推导它们。 |
| 6 | diagnosis + transfer | 用 inspector 解释一次真实失败。 |

每个 micro-lab 的命令和最小案例见 [micro/README.md](micro/README.md)。不要等到
最后才运行 Lab：每学习一个机制，就立即运行对应实验并记录结果。

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

## 组装完成后

完成 [Lab 后工程作业](../../resources/week-01/homework.md)，再用
[笔记模板](../../resources/week-01/notes-template.md) 记录一个真实失败与一次
“只改 V”的迁移预测。没有未解释的 P0 缺口后，才讨论 causal mask。
