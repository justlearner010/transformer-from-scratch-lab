# 材料：带着 P0 问题阅读

## 精确范围

1. [DeepLearning.AI: Transformers in Practice](https://www.deeplearning.ai/courses/transformers-in-practice/)
   中 Q/K/V、scaled dot-product attention 与 softmax 的对应 lesson。
2. [Attention Is All You Need](https://arxiv.org/abs/1706.03762) 第 3.2.1 节，
   只读 Scaled Dot-Product Attention 的公式、缩放理由和文字说明；跳过
   multi-head 与后续 block 内容。

## 阅读问题与证据

| P0/P1 节点 | 必须回答的问题 | 完成证据 |
| --- | --- | --- |
| P0 score 语义 | `QK^T[i,j]` 比较的是哪两个向量？为什么一行对应一个 query 的竞争？ | 自己构造的 `(2,2)` 例子与一句行列解释。 |
| P1 scaling | 为什么缩放用 `d_k` 而不是 token 数 `n`？ | 说明 dot product 方差随特征维度增长的关系。 |
| P0 softmax | 为什么沿最后一维归一化？减去行最大值为何不改变结果？ | 一行手算与一个 `axis=0` 反例。 |
| P0 value read | V 为什么不参与匹配，却决定输出特征？ | 改变 V、不改变 Q/K 的预测。 |

每题用自己的话回答即可；不要超过 250 字。四题都完成后再进入 Gate 1。
