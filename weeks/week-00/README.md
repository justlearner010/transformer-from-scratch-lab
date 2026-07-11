# Week 0：进入 Transformer 前的数学与训练契约

本周不是可跳过的热身。目标是让后续的 attention、mask、训练错误都能被定位到具体的矩阵、概率或梯度问题。

## P0 清单

- shape 与矩阵乘法的内维度规则；
- 向量点积、矩阵乘法与转置；
- stable softmax 与交叉熵；
- 链式法则的局部梯度直觉；
- NumPy 的广播和输入不变性检查。

## 学习顺序

1. 阅读 D2L 的线性代数、微积分与 attention 预备内容。
2. 完成 A 类手算、B 类稳定性证明和 C 类 shape 错误诊断题。
3. 运行 Lab 环境与函数契约检查。
4. 写一份“我最容易在哪些 shape 上出错”的预警笔记。

## 通过门槛

闭卷写出 `(n, d_model) @ (d_model, d_k)`、`QK^T` 和 attention 输出的 shape；并能解释 softmax 为何必须数值稳定。
