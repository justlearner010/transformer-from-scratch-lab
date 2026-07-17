# Week 1 笔记、Lab feedback 与工程 feedback

## 我的知识图更新

| 节点 | 开始时深度 | 当前证据 | 仍需达到的深度 | 是否 P0 缺口 |
| --- | --- | --- | --- | --- |
| score 行列语义 | unknown |  | D4 | 是 / 否 |
| stable softmax | unknown |  | D4 | 是 / 否 |
| `weights @ V` | unknown |  | D4 | 是 / 否 |
| Q/K/V 角色 | unknown |  | D3 | 是 / 否 |
| scaling | unknown |  | D3 | 是 / 否 |

## 我被纠正后的机制解释

- query 如何提出“读取需求”：
- key 如何参与匹配：
- value 如何决定被读取的内容：
- 为什么缩放项依赖 `d_k`：
- 为什么一行 softmax 对应一个输出 token：

## Lab feedback

| 现象 | 类别 | 原因假设 | 最小验证 | 修复后成立的性质 |
| --- | --- | --- | --- | --- |
|  | shape / transpose / scaling / 数值稳定性 / axis / weighted read / 边界 |  |  |  |

## 自主 demo：预测后验证

- 输入与目标：
- 预测 1（哪个 query 关注哪个 key）：
- 结果与解释：
- 预测 2（只改一个 V 行）：
- 结果与解释：

## 闭卷检索与下一步

- 不看代码，写出完整的数据流与 shape：
- 一种 output shape 正确但机制错误的情况：
- causal mask 应插在何处，为什么本周不实现：
- 未关闭的 P0 缺口；若没有，下一阶段可解锁什么：
