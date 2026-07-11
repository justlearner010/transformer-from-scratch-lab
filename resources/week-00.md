# Week 0 材料：看懂每一步信息如何变化

本周不泛读。每份材料都服务于任务链中的一个具体箭头；读完立刻回答问题并留下证据。

| 顺序 | 材料与链接 | 精确范围 | 带着的问题读 | 完成证据 |
| --- | --- | --- | --- |
| 1 | [D2L 2.3 Linear Algebra](https://d2l.ai/chapter_preliminaries/linear-algebra.html) | 只读 `Scalars`、`Vectors`、`Matrices`、`Tensors`、`Reduction`、`Non-Reduction Sum`、`Dot Products`、`Matrix-Vector Products`、`Matrix-Matrix Multiplication` 小节；跳过后续范数、导数与特征分解内容。 | `(3, 2) @ (2, 2)` 为什么得到 `(3, 2)`？每个输出元素从哪里来？ | 写出内维度规则，并手算一个输出元素。 |
| 2 | [D2L 4.1 Softmax Regression](https://d2l.ai/chapter_linear-classification/softmax-regression.html) | 只读 `Softmax Operation`、`Vectorization`、`Loss Function` 与 `Information Theory Basics` 小节；本周不需要实现 softmax regression。 | score 为什么必须被归一化为权重？为什么要先处理数值稳定性？ | 对 `[2, 1, 0]` 手算 softmax，并说明同加常数后为何不变。 |
| 3 | [D2L 11.1 Queries, Keys, and Values](https://d2l.ai/chapter_attention-mechanisms-and-transformers/queries-keys-values.html) | 只读开头的 `Queries, Keys, and Values` 定义、attention pooling 的直觉与 summary；不进入实现代码和后续章节。 | 点积为什么能成为匹配分数，而不是最终读取结果？ | 写出一个两 token 点积例子，并指出它还缺少哪一步才会变成读取权重。 |
| 4 | [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | 只读 abstract 和图 1；只看 encoder-decoder 的整体数据流，不读公式与第 3 节细节。 | token 的顺序信息、attention、输出预测大致位于整张图的哪里？ | 画一条从 token 到预测的粗略箭头图，并标出当前 Week 0 已经认识的部分。 |

完成四项后停止阅读，转入任务文件。若某个问题答不出，回读该项，不追加新材料。Week 1 才精读论文第 3.2.1 节的 scaled dot-product attention。
