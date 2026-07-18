from learning_runtime.agent.commands import parse_agent_input
from learning_runtime.agent.models import (
    AgentCommand,
    AgentTurn,
    InputKind,
    PresentationKind,
    PresentationRequest,
)
from learning_runtime.agent.protocol import ConversationPresenter
from learning_runtime.runtime import LearningRuntime
from learning_runtime.verification.protocol import Verifier


HELP_TEXT = "可用命令：/submit /retry /status /next /help /quit"


class AgentSession:
    def __init__(
        self,
        runtime: LearningRuntime,
        presenter: ConversationPresenter,
        verifier: Verifier | None,
    ) -> None:
        self.runtime = runtime
        self.presenter = presenter
        self.verifier = verifier

    def open(self, phase: str) -> AgentTurn:
        action = self.runtime.open_session(phase)
        return self._present(PresentationKind.ACTION, action)

    def handle(self, raw: str) -> AgentTurn:
        parsed = parse_agent_input(raw)
        if parsed.kind is InputKind.EMPTY:
            return AgentTurn("")
        if parsed.kind is InputKind.UNKNOWN_COMMAND:
            return AgentTurn(HELP_TEXT)
        if parsed.kind is InputKind.MESSAGE:
            return self._present(
                PresentationKind.EXPLANATION,
                self.runtime.next_action(),
                student_message=raw.strip(),
            )
        if parsed.command is AgentCommand.QUIT:
            return AgentTurn("学习进度已保存在事件账本中。", should_exit=True)
        if parsed.command is AgentCommand.HELP:
            return AgentTurn(HELP_TEXT)
        if parsed.command is AgentCommand.STATUS:
            state = self.runtime.get_state()
            return AgentTurn(
                f"当前 Gate：{state.current_gate}\n状态：{state.gate_status.value}"
            )
        if parsed.command is AgentCommand.NEXT:
            return self._present(PresentationKind.ACTION, self.runtime.next_action())
        if parsed.command is None:
            raise AssertionError("command input has no command")
        return self._handle_mutating(parsed.command)

    def _handle_mutating(self, command: AgentCommand) -> AgentTurn:
        raise NotImplementedError(command)

    def _present(
        self,
        kind: PresentationKind,
        action,
        student_message: str | None = None,
        decision=None,
    ) -> AgentTurn:
        state = self.runtime.get_state()
        return AgentTurn(self.presenter.present(PresentationRequest(
            kind=kind,
            action=action,
            state=state,
            student_message=student_message,
            decision=decision,
        )))
