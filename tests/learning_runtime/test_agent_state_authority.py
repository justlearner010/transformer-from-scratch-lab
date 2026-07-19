from pathlib import Path
import re
import subprocess

import pytest

from learning_runtime.runtime import LearningRuntime
from learning_runtime.schemas import GateStatus
from learning_runtime.storage.event_ledger import EventLedger
from learning_runtime.verification.models import RawVerificationResponse
from learning_runtime.verification.validator import VerificationOutputError


def git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def complete_and_commit(repo: Path) -> None:
    answer = repo / "homework_answer/week-01/gate-00.md"
    text = re.sub(
        r"<!--.*?-->",
        "Q、K、V shape 闭合；K.T 交换 K 的最后两个维度。",
        answer.read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    text = text.replace(
        "Q、K、V shape 闭合；K.T 交换 K 的最后两个维度。\n\n## 提交自检",
        "Q、K、V shape 闭合；K.T 交换 K 的最后两个维度。\n\n"
        "![手写](attachments/gate-00/shape.jpg)\n\n## 提交自检",
        1,
    )
    answer.write_text(text, encoding="utf-8")
    image = repo / "homework_answer/week-01/attachments/gate-00/shape.jpg"
    image.write_bytes(b"synthetic-image")
    git(repo, "add", "homework_answer/week-01")
    git(repo, "commit", "-m", "answer gate zero")


class PayloadVerifier:
    def __init__(self, payload) -> None:
        from learning_runtime.verification.siliconflow import SiliconFlowVerifier
        from types import SimpleNamespace

        self.identity = SiliconFlowVerifier(SimpleNamespace(), "fixture").identity
        self.payload = payload
        self.calls = 0

    def verify(self, request):
        self.calls += 1
        return RawVerificationResponse(self.payload, "response-1", "fixture", {})


def prepare(student_repo: Path) -> LearningRuntime:
    git(student_repo, "switch", "-c", "learner/test/week-01")
    runtime = LearningRuntime(student_repo, student_repo / ".learning-os")
    runtime.start_session("week-01")
    complete_and_commit(student_repo)
    runtime.submit_answer("week-01-gate-0")
    return runtime


def passed_payload() -> dict[str, object]:
    return {
        "criteria": [{
            "criterion_id": "shape-bridge-complete",
            "status": "passed",
            "reason": "meets rubric",
            "evidence_quotes": ["K.T 交换 K 的最后两个维度"],
            "failure_mode": None,
        }]
    }


def test_only_policy_can_advance_agent_evaluation(student_repo: Path) -> None:
    runtime = prepare(student_repo)
    receipt = runtime.evaluate_current(PayloadVerifier(passed_payload()))

    assert receipt.state.current_gate == "week-01-gate-1"
    assert receipt.state.gate_status is GateStatus.ACTIVE
    assert receipt.decision.recommendation.value == "pass"
    assert [event.event_type for event in runtime.ledger.read()][-4:] == [
        "verification_recorded",
        "transition_applied",
        "policy_decided",
        "transition_applied",
    ]


def test_agent_state_field_cannot_change_pending_state(student_repo: Path) -> None:
    runtime = prepare(student_repo)
    payload = passed_payload()
    payload["gate_status"] = "passed"

    with pytest.raises(VerificationOutputError):
        runtime.evaluate_current(PayloadVerifier(payload))

    assert runtime.get_state().gate_status is GateStatus.EVIDENCE_PENDING
    assert runtime.ledger.read()[-1].event_type == "verification_failed"
