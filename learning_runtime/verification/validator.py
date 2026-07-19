from collections.abc import Mapping

from learning_runtime.schemas import CriterionResult, CriterionStatus, Recommendation
from learning_runtime.verification.models import RawVerificationResponse, VerificationRequest


class VerificationOutputError(ValueError):
    """Raised when provider output exceeds or violates the criterion contract."""


TOP_LEVEL_KEYS = {"criteria"}
CRITERION_KEYS = {
    "criterion_id",
    "status",
    "reason",
    "evidence_quotes",
    "failure_mode",
}


def validate_response(
    raw: RawVerificationResponse, request: VerificationRequest
) -> tuple[CriterionResult, ...]:
    payload = raw.payload
    if set(payload) != TOP_LEVEL_KEYS:
        raise VerificationOutputError("invalid top-level verification fields")
    rows = payload.get("criteria")
    if not isinstance(rows, list):
        raise VerificationOutputError("criteria must be a list")
    expected = {item.criterion_id: item for item in request.rubric.criteria}
    results: list[CriterionResult] = []
    seen: set[str] = set()
    for value in rows:
        if not isinstance(value, Mapping) or set(value) != CRITERION_KEYS:
            raise VerificationOutputError("invalid criterion fields")
        criterion_id = str(value["criterion_id"])
        if criterion_id not in expected or criterion_id in seen:
            raise VerificationOutputError(f"unknown or duplicate criterion: {criterion_id}")
        seen.add(criterion_id)
        try:
            status = CriterionStatus(str(value["status"]))
        except ValueError as error:
            raise VerificationOutputError("invalid criterion status") from error
        quotes = value["evidence_quotes"]
        if not isinstance(quotes, list) or not all(isinstance(item, str) for item in quotes):
            raise VerificationOutputError("evidence_quotes must be strings")
        if status is not CriterionStatus.INSUFFICIENT_EVIDENCE:
            if not quotes or any(quote not in request.answer_text for quote in quotes):
                raise VerificationOutputError("evidence quote is not in committed answer")
        mode_raw = value["failure_mode"]
        failure_mode = None
        if mode_raw is not None:
            try:
                failure_mode = Recommendation(str(mode_raw))
            except ValueError as error:
                raise VerificationOutputError("invalid failure mode") from error
            if failure_mode.value not in expected[criterion_id].allowed_failure_modes:
                raise VerificationOutputError("failure mode is not allowed by rubric")
        if status is not CriterionStatus.FAILED and failure_mode is not None:
            raise VerificationOutputError("only failed criteria may have failure_mode")
        results.append(
            CriterionResult(
                criterion_id=criterion_id,
                status=status,
                evidence_refs=(request.evidence_id,),
                failed_node=(request.gate_id if status is CriterionStatus.FAILED else None),
                failure_mode=failure_mode,
                reason=str(value["reason"]),
            )
        )
    if seen != set(expected):
        raise VerificationOutputError("missing required criterion")
    return tuple(results)
