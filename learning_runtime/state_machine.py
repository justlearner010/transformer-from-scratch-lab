from learning_runtime.schemas import (
    CourseManifest,
    EventDraft,
    GateStatus,
    LearnerState,
    Recommendation,
    TransitionDecision,
)


class IllegalTransition(ValueError):
    """Raised before an invalid state transition can reach the ledger."""


LEGAL_TRANSITIONS = {
    GateStatus.READY: {GateStatus.ACTIVE},
    GateStatus.ACTIVE: {GateStatus.EVIDENCE_PENDING, GateStatus.ESCALATED},
    GateStatus.EVIDENCE_PENDING: {GateStatus.EVALUATING, GateStatus.ESCALATED},
    GateStatus.EVALUATING: {
        GateStatus.PASSED,
        GateStatus.REINFORCEMENT_REQUIRED,
        GateStatus.DIAGNOSIS_REQUIRED,
        GateStatus.ESCALATED,
    },
    GateStatus.REINFORCEMENT_REQUIRED: {GateStatus.ACTIVE},
    GateStatus.DIAGNOSIS_REQUIRED: {GateStatus.ACTIVE},
    GateStatus.PASSED: set(),
    GateStatus.ESCALATED: set(),
}


class LearningStateMachine:
    def __init__(self, manifest: CourseManifest) -> None:
        self.manifest = manifest

    def transition(
        self, state: LearnerState, target_status: GateStatus
    ) -> EventDraft:
        if target_status not in LEGAL_TRANSITIONS[state.gate_status]:
            raise IllegalTransition(
                f"illegal transition: {state.gate_status.value} -> "
                f"{target_status.value}"
            )
        return EventDraft(
            event_type="transition_applied",
            payload={
                "current_gate": state.current_gate,
                "gate_status": target_status.value,
                "attempt_count": state.attempt_count,
                "hint_level": state.hint_level,
                "verified_evidence_ids": list(state.verified_evidence_ids),
                "unresolved_p0_nodes": list(state.unresolved_p0_nodes),
            },
        )

    def apply_decision(
        self, state: LearnerState, decision: TransitionDecision
    ) -> EventDraft:
        if state.gate_status is not GateStatus.EVALUATING:
            raise IllegalTransition(
                f"decision requires evaluating, got {state.gate_status.value}"
            )
        if decision.policy_result != "allowed":
            raise IllegalTransition("policy did not allow this transition")

        gate_ids = [gate.gate_id for gate in self.manifest.gates]
        current_gate = state.current_gate
        target_status: GateStatus
        unlocked_capability = state.unlocked_capability
        attempt_count = state.attempt_count
        unresolved_nodes = state.unresolved_p0_nodes

        if decision.recommendation is Recommendation.PASS:
            current_index = gate_ids.index(state.current_gate)
            if current_index == len(gate_ids) - 1:
                target_status = GateStatus.PASSED
                unlocked_capability = self.manifest.next_capability
                unresolved_nodes = ()
            else:
                current_gate = gate_ids[current_index + 1]
                target_status = GateStatus.ACTIVE
                attempt_count = 0
                unresolved_nodes = self.manifest.gate(
                    current_gate
                ).knowledge_node_ids
        elif decision.recommendation is Recommendation.REINFORCE:
            current_gate = decision.target_gate
            target_status = GateStatus.REINFORCEMENT_REQUIRED
        elif decision.recommendation is Recommendation.DIAGNOSE:
            current_gate = decision.target_gate
            target_status = GateStatus.DIAGNOSIS_REQUIRED
        else:
            target_status = GateStatus.ESCALATED

        evidence_ids = tuple(
            dict.fromkeys((*state.verified_evidence_ids, *decision.evidence_refs))
        )
        return EventDraft(
            event_type="transition_applied",
            payload={
                "current_gate": current_gate,
                "gate_status": target_status.value,
                "attempt_count": attempt_count,
                "hint_level": state.hint_level,
                "verified_evidence_ids": list(evidence_ids),
                "unresolved_p0_nodes": list(unresolved_nodes),
                "unlocked_capability": unlocked_capability,
                "decision": decision.recommendation.value,
                "reason": decision.reason,
                "next_action": decision.next_action,
            },
            evidence_refs=decision.evidence_refs,
        )
