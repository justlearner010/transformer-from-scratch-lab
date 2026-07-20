# Week 1 Micro-Labs

每次只做一个机制：先在作答文件写预测，再运行对应命令，对照结果并解释原因。

| micro-lab | 命令 | 立即检查什么 |
| --- | --- | --- |
| `shape` | `uv run python labs/week-01/run_micro.py shape` | Q/K/V、scores、weights、output 的 shape 链 |
| `score` | `uv run python labs/week-01/run_micro.py score` | `Q @ K.T` 的每行/每列语义 |
| `softmax` | `uv run python labs/week-01/run_micro.py softmax` | 极端数值是否仍有限、每行是否和为 1 |
| `value` | `uv run python labs/week-01/run_micro.py value` | weights 如何读取 V，而非改变 weights |
| `compose` | `uv run python labs/week-01/run_micro.py compose` | 四个组件按数据流组合后的 output 与 weights |

全部公开性质测试：

```bash
uv run pytest labs/week-01/tests/test_week_01_micro_labs.py -q
```

这些实验不会替你写 Gate 答案。输出只是你提交前用来检验预测的最小证据；答案中必须
说明你预测了什么、实际观察到什么、以及它说明了哪个机制。
