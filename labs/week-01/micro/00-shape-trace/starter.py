"""Micro-lab 0: complete one attention shape chain yourself."""


def complete_shape_chain(
    token_shape: tuple[int, int],
    query_weight_shape: tuple[int, int],
    key_weight_shape: tuple[int, int],
    value_weight_shape: tuple[int, int],
) -> dict[str, tuple[int, int]]:
    """Return Q, K, V, scores, weights, and output shapes; reject invalid Q/K."""
    raise NotImplementedError("完成 shape trace：先写预测，再让每一步 shape 闭合")
