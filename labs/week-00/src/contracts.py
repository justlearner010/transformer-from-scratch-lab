"""Week 0 Lab starter code: shape contracts before attention."""


def validate_matrix_shape(shape: tuple[int, ...], *, name: str) -> tuple[int, int]:
    """Validate one two-dimensional matrix shape.

    Args:
        shape: Candidate shape supplied as a tuple of integer dimensions.
        name: Either ``"left"`` or ``"right"``; use it in any ValueError message.

    Returns:
        The validated ``(rows, columns)`` shape.

    Raises:
        ValueError: If shape is not two-dimensional or contains a non-positive dimension.
    """
    raise NotImplementedError("完成关卡 1：验证二维矩阵 shape")


def matrix_product_shape(
    left_shape: tuple[int, ...], right_shape: tuple[int, ...]
) -> tuple[int, int]:
    """Return the output shape of a valid two-dimensional matrix product.

    First validate both operands with ``validate_matrix_shape``. If the left
    column count differs from the right row count, raise ValueError that names
    the incompatible inner dimensions. Do not create NumPy arrays here.
    """
    raise NotImplementedError("完成关卡 2：推导矩阵乘法输出 shape")
