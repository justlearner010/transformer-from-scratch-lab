from learning_runtime.agent.models import PresentationKind, PresentationRequest
from learning_runtime.agent.presenter import DeterministicPresenter, SafePresenter
from learning_runtime.agent.protocol import PresenterError
from learning_runtime.schemas import ActionContract, GateStatus, LearnerState


def request(kind=PresentationKind.ACTION, student_message=None):
    action = ActionContract(
        "explain attention shapes", "week-01-gate-0", "first prerequisite",
        "write the closed shape chain", "homework_answer/week-01/gate-00.md",
        ("all shapes close", "explain K.T"), 0,
    )
    state = LearnerState(
        "transformer-from-scratch-lab", "week-01", "week-01-gate-0",
        GateStatus.ACTIVE,
    )
    return PresentationRequest(kind, action, state, student_message)


class BrokenPresenter:
    def present(self, request):
        raise PresenterError("provider unavailable")


def test_deterministic_presenter_renders_action():
    presentation = request()
    text = DeterministicPresenter().present(presentation)
    assert presentation.action.current_gate in text
    assert presentation.action.answer_path in text
    assert "/submit" in text


def test_safe_presenter_falls_back_without_changing_request():
    presentation = request(PresentationKind.EXPLANATION, "我应该做什么？")
    text = SafePresenter(BrokenPresenter(), DeterministicPresenter()).present(
        presentation
    )
    assert presentation.state.gate_status is GateStatus.ACTIVE
    assert presentation.action.action in text
