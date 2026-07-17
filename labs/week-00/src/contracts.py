"""Week 0 Lab starter: NumPy matrix operations before attention.

Implement one gate at a time. Later functions should compose the earlier
ones; this file deliberately contains no reference implementation.
"""

import numpy as np


def require_matrix(value: object, *, name: str) -> np.ndarray:
    """Validate and return one usable two-dimensional NumPy matrix.
    

    Args:
        value: Candidate matrix. It must be a numeric ``np.ndarray`` with two
            non-empty dimensions.
        name: Operand label to include in every error message.

    Returns:
        The original validated array; do not copy or mutate it.

    Raises:
        ValueError: If ``value`` is not a numeric, non-empty, two-dimensional
            NumPy array. The message must contain ``name``.
    """



    if isinstance(value,np.ndarray):
        dim = value.ndim
        if dim != 2:
            raise ValueError("维度不是2")
        else:

            
            if np.issubdtype(value.dtype,np.number):
                sh = value.shape    
                row,col = sh[0],sh[1]
                if row == 0 or col == 0:
                    raise ValueError("矩阵的行或列有空值")
                else:
                    return value;
            else:
                raise ValueError("矩阵的元素不是数字")

    else:
        raise ValueError("这个对象不是一个n维度矩阵")
    

    raise NotImplementedError("完成关卡 1：验证二维 NumPy 矩阵")


def matrix_shape(matrix: np.ndarray, *, name: str) -> tuple[int, int]:
    """Return ``(rows, columns)`` for one validated matrix.

    Reuse ``require_matrix`` rather than duplicating its boundary checks.
    Return only the shape information; do not modify the matrix.

    Raises:
        ValueError: If ``matrix`` is not accepted by ``require_matrix``.
    """
    validate_matrix = require_matrix(matrix,name=name)
    m_shape = validate_matrix.shape
    row,col = m_shape[0],m_shape[1]

    return (row,col)
    raise NotImplementedError("完成关卡 2：读取矩阵的行数与列数")


def require_multipliable(left: np.ndarray, right: np.ndarray) -> None:
    """Accept exactly the two matrices that can be multiplied as ``left × right``.

    Reuse ``matrix_shape`` for both operands. A product is valid only when the
    column count of ``left`` equals the row count of ``right``. This is a pure
    validation gate: return ``None`` after successful validation and do not
    calculate a product or mutate either input.

    Raises:
        ValueError: If either input is invalid or their inner dimensions differ.
            An incompatibility message must name both ``left`` and ``right``
            inner dimensions.
    """

    l_shape = matrix_shape(left,name="left")
    r_shape = matrix_shape(right,name="right")
    lrow = l_shape[1]
    rcol = r_shape[0]

    if lrow == rcol:
        return;
    else:
        raise ValueError("左矩阵的列数不等于右矩阵的行数，无法运算")
    raise NotImplementedError("完成关卡 3：验证矩阵乘法的内维度")


def dot_entry(left: np.ndarray, right: np.ndarray, row: int, column: int) -> float:
    """Compute one output entry at ``(row, column)`` of ``left × right``.

    Reuse ``require_multipliable``. Select exactly one row from ``left`` and
    one column from ``right`` and combine them into one scalar. Do not create a
    complete product here and do not mutate either input.

    Raises:
        ValueError: If the inputs cannot be multiplied.
        IndexError: If ``row`` or ``column`` is outside the output matrix.
    """
    require_multipliable(left,right)
    new_row = matrix_shape(left,name="left")[0]
    new_col = matrix_shape(left,name="left")[1]

    
    if (row > new_row - 1  or row < 0 or column > new_col -1  or column < 0):
        raise IndexError("所要计算的矩阵下标超过新矩阵下标值")
    else:
        left_row = left[row,:]
        right_col = right[:,column]
        res = np.dot(left_row,right_col)
        return res

    raise NotImplementedError("完成关卡 4：计算矩阵乘积的一个位置")


def matmul_from_entries(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Build the complete ``left × right`` product from individual entries.

    Reuse ``require_multipliable`` and call ``dot_entry`` once for every output
    position. Do not use ``@`` or ``np.matmul`` in this function. The returned
    array must have the expected output shape and neither input may be changed.

    Raises:
        ValueError: If the inputs cannot be multiplied.
    """
    require_multipliable(left,right)
    
    new_row = matrix_shape(left,name="left")[0]
    new_col = matrix_shape(right,name="right")[1]
    res = np.empty((new_row, new_col))


    for i in range (0,matrix_shape(left,name="left")[0]):
        for j in range (0,matrix_shape(right,name="right")[1]):
            res[i][j] = dot_entry(left,right,i,j)
    
    return res



    raise NotImplementedError("完成关卡 5：由单个位置组装完整矩阵乘积")


def describe_product(left: np.ndarray, right: np.ndarray) -> str:
    """Explain the shape relationship of a proposed matrix product.

    For compatible matrices, return a short string containing both input shapes
    and the output shape. For incompatible matrices, return a short string
    containing both input shapes and the reason they cannot multiply. This
    function is diagnostic only: it must not calculate the product or mutate
    either input.

    Raises:
        ValueError: If either input is not a usable matrix.
    """
    left_shape = (matrix_shape(left,name="left"))
    right_shape = matrix_shape(right,name="right")

    try:
        require_multipliable(left,right)
    except ValueError :
        return (f"left {left_shape} 与 right {right_shape} 不能相乘："
            f"left 的列数 {left_shape[1]} "
            f"不等于 right 的行数 {right_shape[0]}。")
    

    output_shape = (left_shape[0],right_shape[1])

    return (f"左边矩阵的shape是{left_shape},右边矩阵的shape是{right_shape},结果矩阵的shape是{output_shape}")
    raise NotImplementedError("完成关卡 6：写出矩阵乘法的可读诊断")
