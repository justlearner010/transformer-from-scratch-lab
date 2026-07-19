import os
from pathlib import Path

import pytest

from learning_runtime.manifest import load_manifest
from learning_runtime.storage.event_ledger import EventLedger
from learning_runtime.verification.models import VerificationRequest
from learning_runtime.verification.registry import EvaluationRegistry
from learning_runtime.verification.rubric import load_rubric
from learning_runtime.verification.service import StableVerificationService
from learning_runtime.verification.siliconflow import SiliconFlowVerifier


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.live
@pytest.mark.skipif(
    not os.environ.get("SILICONFLOW_API_KEY"),
    reason="SILICONFLOW_API_KEY is not configured",
)
def test_live_result_is_recorded_and_reused(tmp_path: Path) -> None:
    manifest = load_manifest(ROOT / "course-manifests/week-01.yaml", ROOT)
    rubric = load_rubric(ROOT, manifest.gate("week-01-gate-0"))
    verifier = SiliconFlowVerifier.from_env()
    request = VerificationRequest(
        course_id=manifest.course_id,
        gate_id="week-01-gate-0",
        evidence_id="live-synthetic-evidence",
        answer_path="synthetic.md",
        answer_hash="sha256:live-synthetic-answer-v1",
        answer_text=(
            "若 Q、K 均为 (2, 3)，K.T 为 (3, 2)，所以 Q@K.T 为 (2, 2)。"
            "K.T 交换 K 的 token 轴与特征轴，使每个 query 能与每个 key 点积。"
            "weights 为 (2, 2)，若 V 为 (2, 4)，weights@V 为 (2, 4)。"
        ),
        attachments=(),
        rubric=rubric,
        verifier_identity=verifier.identity,
    )
    ledger = EventLedger(tmp_path / "events.jsonl")
    service = StableVerificationService(EvaluationRegistry(ledger), verifier)

    first = service.evaluate(request)
    second = service.evaluate(request)

    assert first.record_id == second.record_id
    assert {item.criterion_id for item in first.results} == {
        "shape-bridge-complete"
    }
    assert [event.event_type for event in ledger.read()] == [
        "verification_recorded"
    ]
