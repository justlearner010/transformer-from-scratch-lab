from dataclasses import dataclass
from typing import Mapping

from learning_runtime.schemas import CriterionResult


@dataclass(frozen=True)
class RubricCriterion:
    criterion_id: str
    standard: str
    passed_when: tuple[str, ...]
    failed_when: tuple[str, ...]
    insufficient_when: tuple[str, ...]
    allowed_failure_modes: tuple[str, ...]


@dataclass(frozen=True)
class VersionedRubric:
    rubric_id: str
    version: int
    gate_id: str
    criteria: tuple[RubricCriterion, ...]
    content_hash: str


@dataclass(frozen=True)
class VerifierIdentity:
    provider: str
    model: str
    prompt_version: str
    schema_version: str
    settings: Mapping[str, object]


@dataclass(frozen=True)
class VerificationAttachment:
    path: str
    content_hash: str
    content: bytes


@dataclass(frozen=True)
class VerificationRequest:
    course_id: str
    gate_id: str
    evidence_id: str
    answer_path: str
    answer_hash: str
    answer_text: str
    attachments: tuple[VerificationAttachment, ...]
    rubric: VersionedRubric
    verifier_identity: VerifierIdentity


@dataclass(frozen=True)
class RawVerificationResponse:
    payload: Mapping[str, object]
    response_id: str
    model: str
    usage: Mapping[str, int]


@dataclass(frozen=True)
class EvaluationRecord:
    record_id: str
    evaluation_key: str
    evidence_id: str
    results: tuple[CriterionResult, ...]
    response_id: str
    model: str
    usage: Mapping[str, int]
    rubric_id: str
    rubric_version: int
    verifier_version: str
