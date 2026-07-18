from pathlib import Path

from learning_runtime.coordinator import Coordinator
from learning_runtime.manifest import load_manifest
from learning_runtime.schemas import GateStatus, LearnerState


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = load_manifest(ROOT / "course-manifests/week-01.yaml", ROOT)


def test_coordinator_returns_one_bounded_action_without_private_content() -> None:
    state = LearnerState(
        course_id=MANIFEST.course_id,
        phase_id=MANIFEST.phase_id,
        current_gate="week-01-gate-0",
        gate_status=GateStatus.ACTIVE,
        verified_evidence_ids=("evidence-0001",),
    )

    action = Coordinator(MANIFEST).next_action(state)

    assert action.current_capability == MANIFEST.capability_question
    assert action.current_gate == "week-01-gate-0"
    assert action.action
    assert action.answer_path == "homework_answer/week-01/gate-00.md"
    assert action.checks == ("shape 是否闭合", "是否能解释 K.T")
    assert action.hint_level == 0
    assert action.evidence_index == ("evidence-0001",)
    rendered = repr(action).lower()
    for forbidden in (".grader/", "solutions/", "expected output", "完整实现"):
        assert forbidden not in rendered
