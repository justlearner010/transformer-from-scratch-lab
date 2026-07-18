# Week 1 材料：带着 P0 问题阅读

本周不追求读完一套课程。每份材料只负责建立一段 attention 信息流；完成对应
问题后立即停止阅读并回到 Gate。

| 材料 | 精确范围 | 带着的问题读 | 完成证据 |
| --- | --- | --- | --- |
| [DeepLearning.AI: Transformers in Practice](https://www.deeplearning.ai/courses/transformers-in-practice/) | Module 2 `LLM internals and attention` 中的 `Attention`（8 分钟）、`Visualization: Decoder-Only Transformers`（10 分钟）和 `Visualization: Interpretable Attention Heads`（10 分钟）。只用于建立直觉；不把可视化当成公式或实现答案。 | 一个 token 的表示何时开始依赖其他 token？attention head 的显示结果与 Q/K/V 计算之间还缺什么机制解释？ | 写下课程页面显示的三个 lesson 名称，并画一条 token 表到 attention output 的粗略箭头图。 |
| [D2L 11.1 Queries, Keys, and Values](https://d2l.ai/chapter_attention-mechanisms-and-transformers/queries-keys-values.html) | 只读 11.1.1 的 Q/K/V 定义、attention pooling 公式与图 11.1.1，再读 11.1.2 Summary；跳过框架代码与 11.1.3 Exercises。 | query、key、value 为什么不是三份同义 embedding？匹配权重和被读取内容分别由谁决定？ | 用自己的两个 key-value 对构造一个 query，并用一句话分别解释 Q、K、V。 |
| [D2L 11.3 Attention Scoring Functions](https://d2l.ai/chapter_attention-mechanisms-and-transformers/attention-scoring-functions.html) | 读本节导言、11.3.1 Dot Product Attention、11.3.2.1 Masked Softmax Operation 的归一化语义，以及 11.3.3 Scaled Dot Product Attention 的公式 (11.3.6) 和 shape 说明；跳过 batch 实现代码、additive attention 与练习。 | 为什么 score 沿 key 维竞争？为什么缩放依赖特征维度 $d_k$？公式的输出宽度为何来自 V？ | 写出 $QK^\top$、weights、weights $@ V$ 的 shape，并构造一个错误 axis 反例。 |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | 只读 3.2.1 Scaled Dot-Product Attention 的公式、缩放理由和文字说明；跳过 3.2.2 Multi-Head Attention、后续 block 与训练内容。 | 论文为什么用 $\sqrt{d_k}$ 缩放？Q/K 参与匹配而 V 决定输出，如何在公式中体现？ | 用自己的 $(2,2)$ 数值例子解释一次 score、softmax 和 value 加权；不复制论文代码或外部实现。 |

## 阅读后的四项 P0/P1 证据

1. **P0 score 语义：**解释 `QK.T[i,j]` 比较哪两个向量，以及为什么一行对应
   一个 query 对所有 keys 的竞争。
2. **P1 scaling：**说明缩放使用 `d_k` 而不是 token 数 `n` 的原因。
3. **P0 softmax：**手算一行权重，解释 `axis=-1` 与减去行最大值分别保护什么。
4. **P0 value read：**预测只改变 V 的一行时，scores、weights 与 output 中哪些
   量保持不变、哪些量可能改变。

每项用自己的例子回答；四项完成后转入概念 Gate，不追加材料。
