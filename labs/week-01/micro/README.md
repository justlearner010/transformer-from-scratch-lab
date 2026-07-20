# Week 1 Micro-Labs

每次只做一个机制：先在作答文件写预测，再运行对应命令，对照结果并解释原因。

| micro-lab | 命令 | 立即检查什么 |
| --- | --- | --- |
| `shape` | [00-shape-trace/starter.py](00-shape-trace/starter.py) | Q/K/V、scores、weights、output 的 shape 链；错误案例见同目录 README |
| `score` | `01-score-probe/starter.py` | `Q @ K.T` 的每行/每列语义 |
| `softmax` | `02-stable-softmax/starter.py` | 极端数值是否仍有限、每行是否和为 1 |
| `value` | `03-value-read/starter.py` | weights 如何读取 V，而非改变 weights |
| `projection` | `04-qkv-projection/starter.py` | Q/K/V 的投影 shape 与输入边界 |
| `compose` | `compose/starter.py` | 已完成组件组合后的 output 与 weights |

全部公开性质测试：

```bash
uv run pytest labs/week-01/tests/test_week_01_micro_labs.py -q
```

每个 `starter.py` 都故意留空，必须由你只完成当前文件。运行命令会执行当前 micro-lab
自己的公开检查；通过后再写 Gate 证据。`compose/starter.py` 只能调用前面五个 starter，
不能把局部机制重新写成一段大函数。
