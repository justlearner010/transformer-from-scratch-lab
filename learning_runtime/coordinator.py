from learning_runtime.schemas import (
    ActionContract,
    CourseManifest,
    GateStatus,
    LearnerState,
)


class Coordinator:
    """Projects trusted state into one bounded learner action."""

    def __init__(self, manifest: CourseManifest) -> None:
        self.manifest = manifest

    def next_action(self, state: LearnerState) -> ActionContract:
        gate = self.manifest.gate(state.current_gate)
        if state.gate_status is GateStatus.EVIDENCE_PENDING:
            reason = "已经记录一次尝试，但尚无验证结果；不能推断通过或失败。"
        elif state.gate_status is GateStatus.ESCALATED:
            reason = "规则或证据不足，状态转换已经停止。"
        else:
            dependencies = self.manifest.dependencies.get(state.current_gate, ())
            reason = (
                "前置 Gate 已满足，现在需要为当前能力留下独立证据。"
                if dependencies
                else "这是本阶段的第一个前置能力检查。"
            )
        return ActionContract(
            current_capability=self.manifest.capability_question,
            current_gate=gate.gate_id,
            reason=reason,
            action=gate.action,
            checks=gate.checks,
            hint_level=state.hint_level,
            evidence_index=state.verified_evidence_ids,
        )
