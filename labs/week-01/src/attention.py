"""Week 1 Lab：在函数契约内自行实现 attention 机制。"""

import numpy as np


def softmax(scores: np.ndarray) -> np.ndarray:
    """沿最后一维计算数值稳定的 softmax。

    输入：任意维浮点数组；最后一维是需要归一化的 score。
    输出：与输入同 shape 的浮点数组；每一行的最后一维之和为 1。
    """
    raise NotImplementedError("完成 Lab 关卡 1：实现 stable softmax")


def project_qkv(
    tokens: np.ndarray, w_query: np.ndarray, w_key: np.ndarray, w_value: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """将 token 表示投影为 Q、K、V。

    输入：tokens 为 (sequence_length, d_model)；三个权重矩阵的首维均为 d_model。
    输出：Q、K、V 的首维均保持 sequence_length。输入 tokens 不得被原地修改。
    权重 shape 或输入维度不兼容时，应抛出 ValueError。
    """
    raise NotImplementedError("完成 Lab 关卡 2：实现 Q/K/V projection")


def scaled_dot_product_attention(
    query: np.ndarray, key: np.ndarray, value: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """计算单头的 scaled dot-product attention。

    输入：query、key、value 的 shape 分别为 (n_query, d_k)、(n_key, d_k)、
    (n_key, d_v)。输出为 (n_query, d_v) 和 (n_query, n_key) 的 weights。
    若 Q/K 特征维度不一致，应抛出 ValueError。
    """
    raise NotImplementedError("完成 Lab 关卡 3：实现 scaled dot-product attention")
