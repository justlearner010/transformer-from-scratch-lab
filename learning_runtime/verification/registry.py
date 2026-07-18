from hashlib import sha256
import json

from learning_runtime.schemas import CriterionResult, CriterionStatus, Recommendation
from learning_runtime.storage.event_ledger import EventLedger
from learning_runtime.verification.models import EvaluationRecord, VerificationRequest


class EvaluationConflictError(RuntimeError):
    """Raised when immutable records disagree for one evaluation key."""


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def verifier_version(request: VerificationRequest) -> str:
    identity = request.verifier_identity
    raw = {
        "provider": identity.provider,
        "model": identity.model,
        "prompt_version": identity.prompt_version,
        "schema_version": identity.schema_version,
        "settings": dict(identity.settings),
    }
    return "sha256:" + sha256(_canonical(raw).encode()).hexdigest()


def evaluation_key(request: VerificationRequest) -> str:
    raw = {
        "course_id": request.course_id,
        "gate_id": request.gate_id,
        "answer_hash": request.answer_hash,
        "attachment_hashes": sorted(item.content_hash for item in request.attachments),
        "rubric_id": request.rubric.rubric_id,
        "rubric_version": request.rubric.version,
        "rubric_hash": request.rubric.content_hash,
        "verifier_version": verifier_version(request),
    }
    return "sha256:" + sha256(_canonical(raw).encode()).hexdigest()


def _result_raw(result: CriterionResult) -> dict[str, object]:
    return {
        "criterion_id": result.criterion_id,
        "status": result.status.value,
        "evidence_refs": list(result.evidence_refs),
        "failed_node": result.failed_node,
        "failure_mode": result.failure_mode.value if result.failure_mode else None,
        "reason": result.reason,
    }


class EvaluationRegistry:
    def __init__(self, ledger: EventLedger) -> None:
        self.ledger = ledger

    def lookup(self, key: str) -> EvaluationRecord | None:
        rows = [
            event.payload
            for event in self.ledger.read()
            if event.event_type == "verification_recorded"
            and event.payload.get("evaluation_key") == key
        ]
        if not rows:
            return None
        if any(_canonical(row) != _canonical(rows[0]) for row in rows[1:]):
            raise EvaluationConflictError(f"conflicting evaluation records for {key}")
        row = rows[0]
        results = tuple(
            CriterionResult(
                criterion_id=str(item["criterion_id"]),
                status=CriterionStatus(str(item["status"])),
                evidence_refs=tuple(item["evidence_refs"]),
                failed_node=item.get("failed_node"),
                failure_mode=(
                    Recommendation(str(item["failure_mode"]))
                    if item.get("failure_mode")
                    else None
                ),
                reason=str(item.get("reason", "")),
            )
            for item in row["results"]
        )
        return EvaluationRecord(
            record_id=str(row["record_id"]),
            evaluation_key=key,
            evidence_id=str(row["evidence_id"]),
            results=results,
            response_id=str(row["response_id"]),
            model=str(row["model"]),
            usage=dict(row.get("usage", {})),
            rubric_id=str(row["rubric_id"]),
            rubric_version=int(row["rubric_version"]),
            verifier_version=str(row["verifier_version"]),
        )

    def store(self, request: VerificationRequest, results, raw) -> EvaluationRecord:
        key = evaluation_key(request)
        record = EvaluationRecord(
            record_id="evaluation-" + key[-12:],
            evaluation_key=key,
            evidence_id=request.evidence_id,
            results=tuple(results),
            response_id=raw.response_id,
            model=raw.model,
            usage=dict(raw.usage),
            rubric_id=request.rubric.rubric_id,
            rubric_version=request.rubric.version,
            verifier_version=verifier_version(request),
        )
        self.ledger.append(
            "verification_recorded",
            {
                "record_id": record.record_id,
                "evaluation_key": key,
                "evidence_id": record.evidence_id,
                "results": [_result_raw(item) for item in record.results],
                "response_id": record.response_id,
                "model": record.model,
                "usage": dict(record.usage),
                "rubric_id": record.rubric_id,
                "rubric_version": record.rubric_version,
                "verifier_version": record.verifier_version,
            },
            (request.evidence_id,),
        )
        return record
