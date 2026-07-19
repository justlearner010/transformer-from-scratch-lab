from learning_runtime.verification.models import EvaluationRecord, VerificationRequest
from learning_runtime.verification.protocol import Verifier
from learning_runtime.verification.registry import EvaluationRegistry, evaluation_key
from learning_runtime.verification.validator import validate_response


class StableVerificationService:
    def __init__(self, registry: EvaluationRegistry, verifier: Verifier) -> None:
        self.registry = registry
        self.verifier = verifier

    def evaluate(self, request: VerificationRequest) -> EvaluationRecord:
        if request.verifier_identity != self.verifier.identity:
            raise ValueError("request verifier identity does not match adapter")
        existing = self.registry.lookup(evaluation_key(request))
        if existing is not None:
            if existing.evidence_id != request.evidence_id:
                self.registry.ledger.append(
                    "verification_reused",
                    {
                        "record_id": existing.record_id,
                        "evaluation_key": existing.evaluation_key,
                        "evidence_id": request.evidence_id,
                    },
                    (request.evidence_id,),
                )
            return existing
        raw = self.verifier.verify(request)
        results = validate_response(raw, request)
        return self.registry.store(request, results, raw)
