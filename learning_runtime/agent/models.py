from dataclasses import dataclass
from enum import StrEnum

from learning_runtime.schemas import ActionContract, LearnerState, TransitionDecision


class PresentationKind(StrEnum):
    ACTION = "action"
    EXPLANATION = "explanation"
    FEEDBACK = "feedback"


class AgentCommand(StrEnum):
    SUBMIT = "submit"
    RETRY = "retry"
    STATUS = "status"
    NEXT = "next"
    HELP = "help"
    QUIT = "quit"


class InputKind(StrEnum):
    COMMAND = "command"
    MESSAGE = "message"
    UNKNOWN_COMMAND = "unknown_command"
    EMPTY = "empty"


@dataclass(frozen=True)
class AgentInput:
    kind: InputKind
    raw: str
    command: AgentCommand | None = None


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
