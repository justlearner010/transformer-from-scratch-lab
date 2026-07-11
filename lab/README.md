# Week 1 Lab：从契约实现 Attention

你将自行实现 `lab/src/attention.py` 的函数。只允许使用 NumPy；不得复制外部实现或查看隐藏评分样例。

## 关卡

| 关卡 | 目标 | 解锁条件 |
| --- | --- | --- |
| 0 | 熟悉函数契约和 shape | 公开 smoke test 可运行。 |
| 1 | 实现数值稳定的 softmax | hidden autograder 通过。 |
| 2 | 实现 scaled dot-product attention | hidden autograder 通过。 |

## 运行

```bash
uv run pytest
uv run python lab/run_grade.py
```

公开测试只检查脚手架；本地 `.grader/` 存在时，评分器才会执行隐藏检查并显示失败类别。

## 提示协议

第 1 次失败：阅读错误类别对应的思考问题。

第 2 次失败：打印相关张量的 shape 和一行数值。

第 3 次失败：回到本周理论题，不直接找实现答案。
