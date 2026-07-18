import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from learning_runtime.manifest import load_manifest
from learning_runtime.verification.models import VerificationRequest, VerifierIdentity
from learning_runtime.verification.rubric import load_rubric
from learning_runtime.verification.siliconflow import (
    SiliconFlowConfigError,
    SiliconFlowVerifier,
)


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = load_manifest(ROOT / "course-manifests/week-01.yaml", ROOT)
RUBRIC = load_rubric(ROOT, MANIFEST.gate("week-01-gate-0"))


class FakeCompletions:
    def __init__(self) -> None:
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        payload = {
            "criteria": [{
                "criterion_id": "shape-bridge-complete",
                "status": "passed",
                "reason": "meets rubric",
                "evidence_quotes": ["K.T 交换维度"],
                "failure_mode": None,
            }]
        }
        return SimpleNamespace(
            id="response-1",
            model=kwargs["model"],
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=8, total_tokens=18),
        )


def test_adapter_requests_json_with_deterministic_settings() -> None:
    completions = FakeCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    verifier = SiliconFlowVerifier(client, "Qwen/Qwen3.6-35B-A3B")
    request = VerificationRequest(
        course_id="course",
        gate_id="week-01-gate-0",
        evidence_id="evidence-1",
        answer_path="answer.md",
        answer_hash="sha256:answer",
        answer_text="K.T 交换维度",
        attachments=(),
        rubric=RUBRIC,
        verifier_identity=verifier.identity,
    )

    raw = verifier.verify(request)

    assert raw.response_id == "response-1"
    assert completions.kwargs["response_format"] == {"type": "json_object"}
    assert completions.kwargs["temperature"] == 0
    assert completions.kwargs["extra_body"] == {"enable_thinking": False}


def test_from_env_requires_key_without_exposing_value(monkeypatch) -> None:
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    with pytest.raises(SiliconFlowConfigError, match="SILICONFLOW_API_KEY"):
        SiliconFlowVerifier.from_env()
