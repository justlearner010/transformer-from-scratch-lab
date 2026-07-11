import numpy as np

from lab.src.attention import scaled_dot_product_attention, softmax


def test_lab_exports_required_functions() -> None:
    assert callable(softmax)
    assert callable(scaled_dot_product_attention)


def test_lab_starter_accepts_the_documented_input_types() -> None:
    scores = np.array([[1.0, 2.0]])
    try:
        softmax(scores)
    except NotImplementedError:
        pass
