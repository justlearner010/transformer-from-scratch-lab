# Shape Trace：你要实现的契约

只修改同目录的 `starter.py` 中 `complete_shape_chain()`。

## 合法输入

四个参数都是二维 shape：

```text
token_shape         = (sequence_length, d_model)
query_weight_shape  = (d_model, d_q)
key_weight_shape    = (d_model, d_k)
value_weight_shape  = (d_model, d_v)
```

函数应返回 `Q`、`K`、`V`、`scores`、`weights`、`output` 的 shape 字典。

## 必须主动拒绝的输入

以下情况必须 `raise ValueError`，不要等 Python 自己在后续计算中报错：

| 输入 | 为什么不合法 |
| --- | --- |
| `token_shape=(3, 4)`，`W_Q=(3, 2)` | `W_Q` 的输入维度不是 `d_model=4`，所以 `X @ W_Q` 不可乘。 |
| `token_shape=(3, 4)`，`W_K=(5, 2)` | `W_K` 的输入维度不是 `d_model=4`。 |
| `token_shape=(3, 4)`，`W_V=(4,)` | 权重必须是二维矩阵，不能是一维向量。 |
| `W_Q=(4, 2)`，`W_K=(4, 3)` | Q 与 K 的最后一维不同，`Q @ K.T` 不成立。 |

运行检查：

```bash
uv run python labs/week-01/run_micro.py shape
```
