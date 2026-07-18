from dataclasses import dataclass


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
