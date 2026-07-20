"""可运行的 Week 1 最小机制实验；先预测，再运行并解释结果。"""

import numpy as np


def shape_trace(
    token_shape: tuple[int, int],
    query_weight_shape: tuple[int, int],
    key_weight_shape: tuple[int, int],
    value_weight_shape: tuple[int, int],
) -> dict[str, tuple[int, int]]:
    """返回一条不计算数值的 attention shape 链。"""
    sequence_length, d_model = token_shape
    for name, shape in {
        "W_Q": query_weight_shape,
        "W_K": key_weight_shape,
        "W_V": value_weight_shape,
    }.items():
        if len(shape) != 2 or shape[0] != d_model:
            raise ValueError(f"{name} must start with d_model={d_model}")
    d_query = query_weight_shape[1]
    d_key = key_weight_shape[1]
    if d_query != d_key:
        raise ValueError("Q and K must have the same feature dimension")
    d_value = value_weight_shape[1]
    return {
        "Q": (sequence_length, d_query),
        "K": (sequence_length, d_key),
        "V": (sequence_length, d_value),
        "scores": (sequence_length, sequence_length),
        "weights": (sequence_length, sequence_length),
        "output": (sequence_length, d_value),
    }


def score_probe(query: np.ndarray, key: np.ndarray) -> np.ndarray:
    """计算 Q @ K.T，保留 query 行与 key 行的配对语义。"""
    if query.ndim != 2 or key.ndim != 2 or query.shape[1] != key.shape[1]:
        raise ValueError("query and key must be two-dimensional with matching features")
    return query @ key.T


def stable_softmax_probe(scores: np.ndarray) -> np.ndarray:
    """沿最后一维稳定归一化，供 axis 与溢出实验使用。"""
    if scores.ndim < 1:
        raise ValueError("scores must have at least one dimension")
    shifted = scores - np.max(scores, axis=-1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum(axis=-1, keepdims=True)


def value_read_probe(weights: np.ndarray, values: np.ndarray) -> np.ndarray:
    """按已归一化的 weights 读取 value 行。"""
    if weights.ndim != 2 or values.ndim != 2 or weights.shape[1] != values.shape[0]:
        raise ValueError("weights columns must match value rows")
    return weights @ values


def project_qkv_probe(
    tokens: np.ndarray,
    w_query: np.ndarray,
    w_key: np.ndarray,
    w_value: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """最小 Q/K/V 投影组件。"""
    if tokens.ndim != 2:
        raise ValueError("tokens must be two-dimensional")
    weights = (w_query, w_key, w_value)
    if any(weight.ndim != 2 or weight.shape[0] != tokens.shape[1] for weight in weights):
        raise ValueError("projection weights must start with token feature dimension")
    return tuple(tokens @ weight for weight in weights)  # type: ignore[return-value]


def compose_attention(
    tokens: np.ndarray,
    w_query: np.ndarray,
    w_key: np.ndarray,
    w_value: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """只组合已验证的 projection、score、softmax 与 value-read 组件。"""
    query, key, values = project_qkv_probe(tokens, w_query, w_key, w_value)
    scores = score_probe(query, key) / np.sqrt(query.shape[-1])
    weights = stable_softmax_probe(scores)
    return value_read_probe(weights, values), weights
