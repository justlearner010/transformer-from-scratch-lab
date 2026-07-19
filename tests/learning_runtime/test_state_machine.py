from pathlib import Path

import pytest

from learning_runtime.manifest import load_manifest
from learning_runtime.schemas import (
    GateStatus,
    LearnerState,
    Recommendation,
    TransitionDecision,
)
from learning_runtime.state_machine import IllegalTransition, LearningStateMachine


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = load_manifest(ROOT / "course-manifests/week-01.yaml", ROOT)


def state(gate: str, status: GateStatus) -> LearnerState:
    return LearnerState(
        course_id=MANIFEST.course_id,
        phase_id=MANIFEST.phase_id,
        current_gate=gate,
        gate_status=status,
    )


def decision(
    recommendation: Recommendation,
    target_gate: str,
) -> TransitionDecision:
    return TransitionDecision(
        recommendation=recommendation,
        target_gate=target_gate,
        failed_node=None,
        reason="verified by deterministic criteria",
        evidence_refs=("evidence-0001",),
        policy_result="allowed",
        next_action="continue",
    )


def test_active_to_evidence_pending_to_evaluating_is_legal() -> None:
    machine = LearningStateMachine(MANIFEST)
    active = state("week-01-gate-0", GateStatus.ACTIVE)

    pending = machine.transition(active, GateStatus.EVIDENCE_PENDING)
    evaluating = machine.transition(
        state("week-01-gate-0", GateStatus.EVIDENCE_PENDING),
        GateStatus.EVALUATING,
    )

    assert pending.payload["gate_status"] == "evidence_pending"
    assert evaluating.payload["gate_status"] == "evaluating"


def test_active_cannot_jump_directly_to_passed() -> None:
    machine = LearningStateMachine(MANIFEST)
    with pytest.raises(IllegalTransition, match="active.*passed"):
        machine.transition(
            state("week-01-gate-0", GateStatus.ACTIVE), GateStatus.PASSED
        )


def test_pass_advances_to_the_next_gate_with_evidence_refs() -> None:
    machine = LearningStateMachine(MANIFEST)
    draft = machine.apply_decision(
        state("week-01-gate-0", GateStatus.EVALUATING),
        decision(Recommendation.PASS, "week-01-gate-0"),
    )

    assert draft.event_type == "transition_applied"
    assert draft.payload["current_gate"] == "week-01-gate-1"
    assert draft.payload["gate_status"] == "active"
    assert draft.payload["decision"] == "pass"
    assert draft.evidence_refs == ("evidence-0001",)


def test_final_gate_pass_unlocks_only_the_next_capability() -> None:
    machine = LearningStateMachine(MANIFEST)
    draft = machine.apply_decision(
        state("week-01-gate-6", GateStatus.EVALUATING),
        decision(Recommendation.PASS, "week-01-gate-6"),
    )

    assert draft.payload["current_gate"] == "week-01-gate-6"
    assert draft.payload["gate_status"] == "passed"
    assert draft.payload["unlocked_capability"] == "causal-mask"
