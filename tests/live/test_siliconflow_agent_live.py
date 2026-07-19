import os

import pytest

from learning_runtime.agent.models import PresentationKind, PresentationRequest
from learning_runtime.agent.siliconflow import SiliconFlowPresenter
from learning_runtime.schemas import ActionContract, GateStatus, LearnerState


def make_live_request():
    return PresentationRequest(
        PresentationKind.ACTION,
        ActionContract(
            "explain attention shapes", "week-01-gate-0", "first prerequisite",
            "write the closed shape chain", "homework_answer/week-01/gate-00.md",
            ("all shapes close", "explain K.T"), 0,
        ),
        LearnerState(
            "transformer-from-scratch-lab", "week-01", "week-01-gate-0",
            GateStatus.ACTIVE,
        ),
    )


@pytest.mark.live
@pytest.mark.skipif(
    not os.environ.get("SILICONFLOW_API_KEY"),
    reason="SILICONFLOW_API_KEY is not configured",
)
def test_live_presenter_returns_non_empty_bounded_text():
    text = SiliconFlowPresenter.from_env().present(make_live_request())
    assert text.strip()
    assert len(text) <= 4000
