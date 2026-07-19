from types import SimpleNamespace
from dataclasses import replace
import json

import pytest

from learning_runtime.agent.models import PresentationKind, PresentationRequest
from learning_runtime.agent.siliconflow import (
    SiliconFlowPresenter,
    SiliconFlowPresenterError,
)
from learning_runtime.schemas import ActionContract, GateStatus, LearnerState


class RecordingCompletions:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(
            message=SimpleNamespace(content=self.content)
        )])


class RecordingClient:
    def __init__(self, content):
        completions = RecordingCompletions(content)
        self.chat = SimpleNamespace(completions=completions)
        self.calls = completions.calls


def make_request():
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


def test_presenter_sends_grounded_text_without_tools():
    client = RecordingClient("请完成当前 Gate，并在 commit 后输入 /submit。")
    presentation = make_request()
    presentation = replace(
        presentation,
        action=replace(
            presentation.action,
            required_sections=("闭卷答案", "推导或机制解释", "提交自检"),
        ),
    )
    text = SiliconFlowPresenter(client, model="fixture").present(presentation)
    kwargs = client.calls[0]
    assert text.startswith("请完成")
    assert "tools" not in kwargs
    assert kwargs["temperature"] == 0
    assert kwargs["extra_body"] == {"enable_thinking": False}
    payload = json.loads(kwargs["messages"][1]["content"])
    assert payload["required_sections"] == [
        "闭卷答案", "推导或机制解释", "提交自检",
    ]


def test_presenter_rejects_empty_response():
    presenter = SiliconFlowPresenter(RecordingClient(""), model="fixture")
    with pytest.raises(SiliconFlowPresenterError):
        presenter.present(make_request())
