from collections import defaultdict
from collections.abc import Sequence

from learning_runtime.schemas import (
    CriterionResult,
    CriterionStatus,
    GateDefinition,
    Recommendation,
    TransitionDecision,
)


class PolicyEngine:
    def decide(
        self,
        gate: GateDefinition,
        results: Sequence[CriterionResult],
    ) -> TransitionDecision:
        grouped: dict[str, list[CriterionResult]] = defaultdict(list)
        for result in results:
            grouped[result.criterion_id].append(result)

        for criterion_id, criterion_results in grouped.items():
            statuses = {result.status for result in criterion_results}
            if len(statuses) > 1:
                return self._escalate(
                    gate,
                    f"conflicting evidence for {criterion_id}",
                    criterion_results,
                )

        required = {item.criterion_id: item for item in gate.required_evidence}
        missing_or_insufficient: list[str] = []
        selected: list[CriterionResult] = []
        for criterion_id, requirement in required.items():
            candidates = grouped.get(criterion_id, [])
            if not candidates:
                missing_or_insufficient.append(criterion_id)
                continue
            result = candidates[-1]
            if (
                result.status is CriterionStatus.INSUFFICIENT_EVIDENCE
                or (requirement.independent and not result.evidence_refs)
            ):
                missing_or_insufficient.append(criterion_id)
            selected.append(result)

        if missing_or_insufficient:
            return self._escalate(
                gate,
                "insufficient evidence for " + ", ".join(missing_or_insufficient),
                selected,
            )

        failures = [
            result for result in selected if result.status is CriterionStatus.FAILED
        ]
        if failures:
            modes = {result.failure_mode for result in failures}
            if None in modes or len(modes) != 1:
                return self._escalate(
                    gate, "unknown or conflicting failure route", failures
                )
            mode = modes.pop()
            if mode is Recommendation.REINFORCE:
                return self._decision(
                    Recommendation.REINFORCE,
                    gate.rollback_target,
                    failures,
                    "known P0 failure maps to a prerequisite",
                    "完成一个最小补强任务后重新提交。",
                )
            if mode is Recommendation.DIAGNOSE:
                return self._decision(
                    Recommendation.DIAGNOSE,
                    gate.gate_id,
                    failures,
                    "multiple causes remain plausible",
                    "提出原因假设并设计一个区分实验。",
                )
            return self._escalate(gate, "unsupported failure route", failures)

        if all(result.status is CriterionStatus.PASSED for result in selected):
            return self._decision(
                Recommendation.PASS,
                gate.gate_id,
                selected,
                "all required criteria have independent evidence",
                "进入下一个 Gate。",
            )
        return self._escalate(gate, "insufficient policy rule", selected)

    def _escalate(
        self,
        gate: GateDefinition,
        reason: str,
        results: Sequence[CriterionResult],
    ) -> TransitionDecision:
        return self._decision(
            Recommendation.ESCALATE,
            gate.gate_id,
            results,
            reason,
            "检查原始证据或请求人工确认。",
        )

    @staticmethod
    def _decision(
        recommendation: Recommendation,
        target_gate: str,
        results: Sequence[CriterionResult],
        reason: str,
        next_action: str,
    ) -> TransitionDecision:
        evidence_refs = tuple(
            dict.fromkeys(
                reference
                for result in results
                for reference in result.evidence_refs
            )
        )
        failed_node = next(
            (result.failed_node for result in results if result.failed_node), None
        )
        return TransitionDecision(
            recommendation=recommendation,
            target_gate=target_gate,
            failed_node=failed_node,
            reason=reason,
            evidence_refs=evidence_refs,
            policy_result="allowed",
            next_action=next_action,
        )
