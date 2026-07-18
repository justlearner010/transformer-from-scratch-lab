from typing import Protocol

from learning_runtime.verification.models import (
    RawVerificationResponse,
    VerificationRequest,
    VerifierIdentity,
)


class VerificationProviderError(RuntimeError):
    """A recoverable verifier-provider failure."""


class Verifier(Protocol):
    identity: VerifierIdentity

    def verify(self, request: VerificationRequest) -> RawVerificationResponse: ...
