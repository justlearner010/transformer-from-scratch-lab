from pathlib import Path

from learning_runtime.manifest import load_manifest
from learning_runtime.policies import PolicyEngine
from learning_runtime.schemas import (
    CriterionResult,
    CriterionStatus,
    Recommendation,
)


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = load_manifest(ROOT / "course-manifests/week-01.yaml", ROOT)
GATE = MANIFEST.gate("week-01-gate-3")


def result(
    criterion_id: str,
    status: CriterionStatus,
    *,
    failure_mode: Recommendation | None = None,
    evidence: tuple[str, ...] = ("evidence-0001",),
) -> CriterionResult:
    return CriterionResult(
        criterion_id=criterion_id,
        status=status,
        evidence_refs=evidence,
        failed_node="stable-softmax" if status is CriterionStatus.FAILED else None,
        failure_mode=failure_mode,
        reason="controlled fixture",
    )


def test_all_required_independent_evidence_allows_pass() -> None:
    decision = PolicyEngine().decide(
        GATE,
        [
            result("stable-softmax-finite-output", CriterionStatus.PASSED),
            result(
                "row-sums-equal-one",
                CriterionStatus.PASSED,
                evidence=("evidence-0002",),
            ),
        ],
    )
    assert decision.recommendation is Recommendation.PASS


def test_one_mapped_p0_failure_routes_to_reinforcement() -> None:
    decision = PolicyEngine().decide(
        GATE,
        [
            result(
                "stable-softmax-finite-output",
                CriterionStatus.FAILED,
                failure_mode=Recommendation.REINFORCE,
            ),
            result("row-sums-equal-one", CriterionStatus.PASSED),
        ],
    )
    assert decision.recommendation is Recommendation.REINFORCE
    assert decision.target_gate == GATE.rollback_target


def test_ambiguous_failure_requires_diagnosis() -> None:
    decision = PolicyEngine().decide(
        GATE,
        [
            result(
                "stable-softmax-finite-output",
                CriterionStatus.FAILED,
                failure_mode=Recommendation.DIAGNOSE,
            ),
            result("row-sums-equal-one", CriterionStatus.PASSED),
        ],
    )
    assert decision.recommendation is Recommendation.DIAGNOSE
    assert decision.target_gate == GATE.gate_id


def test_missing_required_evidence_escalates_without_guessing_failure() -> None:
    decision = PolicyEngine().decide(
        GATE,
        [
            result(
                "stable-softmax-finite-output",
                CriterionStatus.INSUFFICIENT_EVIDENCE,
                evidence=(),
            )
        ],
    )
    assert decision.recommendation is Recommendation.ESCALATE
    assert "insufficient" in decision.reason


def test_conflicting_results_escalate() -> None:
    decision = PolicyEngine().decide(
        GATE,
        [
            result("stable-softmax-finite-output", CriterionStatus.PASSED),
            result(
                "stable-softmax-finite-output",
                CriterionStatus.FAILED,
                failure_mode=Recommendation.REINFORCE,
            ),
        ],
    )
    assert decision.recommendation is Recommendation.ESCALATE
    assert "conflicting" in decision.reason


def test_unmapped_failure_escalates() -> None:
    decision = PolicyEngine().decide(
        GATE,
        [result("stable-softmax-finite-output", CriterionStatus.FAILED)]
    )
    assert decision.recommendation is Recommendation.ESCALATE
