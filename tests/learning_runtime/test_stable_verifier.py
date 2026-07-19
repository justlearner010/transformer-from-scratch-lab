from dataclasses import replace
from pathlib import Path

import pytest

from learning_runtime.schemas import CriterionStatus
from learning_runtime.storage.event_ledger import EventLedger
from learning_runtime.verification.models import (
    RawVerificationResponse,
    VerificationRequest,
    VerifierIdentity,
)
from learning_runtime.verification.registry import EvaluationRegistry
from learning_runtime.verification.rubric import load_rubric
from learning_runtime.verification.service import StableVerificationService
from learning_runtime.verification.validator import VerificationOutputError
from learning_runtime.manifest import load_manifest


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = load_manifest(ROOT / "course-manifests/week-01.yaml", ROOT)
RUBRIC = load_rubric(ROOT, MANIFEST.gate("week-01-gate-0"))
IDENTITY = VerifierIdentity(
    provider="fake",
    model="fixture",
    prompt_version="v1",
    schema_version="v1",
    settings={"temperature": 0},
)


class SequenceVerifier:
    identity = IDENTITY

    def __init__(self, payloads: list[dict[str, object]]) -> None:
        self.payloads = payloads
        self.calls = 0

    def verify(self, request: VerificationRequest) -> RawVerificationResponse:
        payload = self.payloads[min(self.calls, len(self.payloads) - 1)]
        self.calls += 1
        return RawVerificationResponse(payload, f"response-{self.calls}", "fixture", {})


def request(rubric=RUBRIC) -> VerificationRequest:
    return VerificationRequest(
        course_id="transformer-from-scratch",
        gate_id="week-01-gate-0",
        evidence_id="evidence-0001",
        answer_path="homework_answer/week-01/gate-00.md",
        answer_hash="sha256:answer",
        answer_text="Q、K、V shape 闭合，因为 K.T 交换 K 的最后两个维度。",
        attachments=(),
        rubric=rubric,
        verifier_identity=IDENTITY,
    )


def passed_payload() -> dict[str, object]:
    return {
        "criteria": [
            {
                "criterion_id": "shape-bridge-complete",
                "status": "passed",
                "reason": "shape 与 K.T 解释满足标准",
                "evidence_quotes": ["K.T 交换 K 的最后两个维度"],
                "failure_mode": None,
            }
        ]
    }


def test_same_evaluation_key_calls_verifier_once_and_reuses_result(
    tmp_path: Path,
) -> None:
    failed = passed_payload()
    failed["criteria"][0]["status"] = "failed"
    verifier = SequenceVerifier([passed_payload(), failed])
    ledger = EventLedger(tmp_path / "events.jsonl")
    service = StableVerificationService(EvaluationRegistry(ledger), verifier)

    first = service.evaluate(request())
    second = service.evaluate(request())

    assert verifier.calls == 1
    assert first.record_id == second.record_id
    assert first.results == second.results
    assert first.results[0].status is CriterionStatus.PASSED
    assert [event.event_type for event in ledger.read()] == [
        "verification_recorded"
    ]


def test_rubric_version_changes_evaluation_key(tmp_path: Path) -> None:
    verifier = SequenceVerifier([passed_payload()])
    service = StableVerificationService(
        EvaluationRegistry(EventLedger(tmp_path / "events.jsonl")), verifier
    )

    first = service.evaluate(request())
    second = service.evaluate(request(replace(RUBRIC, version=2)))

    assert verifier.calls == 2
    assert first.evaluation_key != second.evaluation_key


@pytest.mark.parametrize("forbidden", ["gate_status", "recommendation"])
def test_agent_state_fields_are_rejected(
    tmp_path: Path, forbidden: str
) -> None:
    payload = passed_payload()
    payload[forbidden] = "passed"
    verifier = SequenceVerifier([payload])
    ledger = EventLedger(tmp_path / "events.jsonl")

    with pytest.raises(VerificationOutputError, match="top-level"):
        StableVerificationService(EvaluationRegistry(ledger), verifier).evaluate(
            request()
        )

    assert ledger.read() == []
