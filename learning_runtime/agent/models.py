from dataclasses import dataclass
from enum import StrEnum

from learning_runtime.schemas import ActionContract, LearnerState, TransitionDecision


class PresentationKind(StrEnum):
    ACTION = "action"
    EXPLANATION = "explanation"
    FEEDBACK = "feedback"


@dataclass(frozen=True)
class PresentationRequest:
    kind: PresentationKind
    action: ActionContract
    state: LearnerState
    student_message: str | None = None
    decision: TransitionDecision | None = None


@dataclass(frozen=True)
class AgentTurn:
    text: str
    should_exit: bool = False
