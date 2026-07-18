from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class CriterionStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class GateStatus(StrEnum):
    READY = "ready"
    ACTIVE = "active"
    EVIDENCE_PENDING = "evidence_pending"
    EVALUATING = "evaluating"
    PASSED = "passed"
    REINFORCEMENT_REQUIRED = "reinforcement_required"
    DIAGNOSIS_REQUIRED = "diagnosis_required"
    ESCALATED = "escalated"


class Recommendation(StrEnum):
    PASS = "pass"
    REINFORCE = "reinforce"
    DIAGNOSE = "diagnose"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class EvidenceRequirement:
    criterion_id: str
    evidence_type: str
    artifact_ref: str
    priority: str
    independent: bool


@dataclass(frozen=True)
class LearnerWorkspace:
    answer_root: str
    template_ref: str
    commit_required: bool


@dataclass(frozen=True)
class SubmissionDefinition:
    artifact_path: str
    required_sections: tuple[str, ...]
    attachment_policy: str


@dataclass(frozen=True)
class GateDefinition:
    gate_id: str
    knowledge_node_ids: tuple[str, ...]
    task_layer: str
    required_evidence: tuple[EvidenceRequirement, ...]
    verifier: str
    pass_rule: str
    rollback_target: str
    escalation_conditions: tuple[str, ...]
    action: str
    checks: tuple[str, ...]
    submission: SubmissionDefinition
    rubric_ref: str | None = None
    rubric_version: int | None = None


@dataclass(frozen=True)
class CourseManifest:
    course_id: str
    phase_id: str
    capability_question: str
    knowledge_nodes: tuple[Mapping[str, Any], ...]
    gates: tuple[GateDefinition, ...]
    dependencies: Mapping[str, tuple[str, ...]]
    artifact_refs: Mapping[str, str]
    evidence_requirements: tuple[str, ...]
    allowed_hint_levels: tuple[int, ...]
    failure_routes: Mapping[str, str]
    completion_rule: str
    next_capability: str
    learner_workspace: LearnerWorkspace

    def gate(self, gate_id: str) -> GateDefinition:
        for gate in self.gates:
            if gate.gate_id == gate_id:
                return gate
        raise KeyError(gate_id)


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    occurred_at: str
    payload: Mapping[str, Any]
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class EventDraft:
    event_type: str
    payload: Mapping[str, Any]
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class LearnerState:
    course_id: str
    phase_id: str
    current_gate: str
    gate_status: GateStatus
    attempt_count: int = 0
    hint_level: int = 0
    verified_evidence_ids: tuple[str, ...] = ()
    unresolved_p0_nodes: tuple[str, ...] = ()
    last_event_id: str = ""
    unlocked_capability: str | None = None


@dataclass(frozen=True)
class CriterionResult:
    criterion_id: str
    status: CriterionStatus
    evidence_refs: tuple[str, ...] = ()
    failed_node: str | None = None
    failure_mode: Recommendation | None = None
    reason: str = ""


@dataclass(frozen=True)
class TransitionDecision:
    recommendation: Recommendation
    target_gate: str
    failed_node: str | None
    reason: str
    evidence_refs: tuple[str, ...]
    policy_result: str
    next_action: str


@dataclass(frozen=True)
class ActionContract:
    current_capability: str
    current_gate: str
    reason: str
    action: str
    answer_path: str
    checks: tuple[str, ...]
    hint_level: int
    evidence_index: tuple[str, ...] = field(default_factory=tuple)
    required_sections: tuple[str, ...] = field(default_factory=tuple)
    attachment_policy: str = "optional"
