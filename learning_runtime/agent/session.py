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
from learning_runtime.schemas import GateStatus
from learning_runtime.verification.protocol import Verifier, VerificationProviderError
from learning_runtime.verification.registry import EvaluationConflictError
from learning_runtime.verification.validator import VerificationOutputError


HELP_TEXT = "可用命令：/submit /retry /revise /status /next /help /quit"


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
        state = self.runtime.get_state()
        if command is AgentCommand.SUBMIT:
            if state.gate_status is GateStatus.EVIDENCE_PENDING:
                return AgentTurn(
                    "你已经提交过这次作答，正在等待判定。\n"
                    "下一步：如果刚配置 API key，请输入 /retry 重新判定。\n"
                    "不要重复 /submit；只有系统要求补强时才修改答案并再次提交。"
                )
            try:
                self.runtime.submit_answer(state.current_gate)
            except (ValueError, KeyError) as error:
                return AgentTurn(
                    f"提交检查失败：{error}\n"
                    "请完成作答与附件，由你本人手动 commit 后再输入 /submit。"
                )
        elif command is AgentCommand.RETRY:
            if state.gate_status is not GateStatus.EVIDENCE_PENDING:
                return AgentTurn("只有 evidence_pending 状态可以 /retry。")
        elif command is AgentCommand.REVISE:
            try:
                action = self.runtime.reopen_for_revision()
            except ValueError:
                return AgentTurn("当前 Gate 不需要修订；请按当前任务继续。")
            turn = self._present(PresentationKind.ACTION, action)
            return AgentTurn(
                "已开启修订。请根据上一轮反馈修改当前作答文件，"
                "完成后由你手动 commit，再输入 /submit。\n\n"
                + turn.text
            )
        else:
            raise AssertionError(f"unhandled command: {command}")

        if self.verifier is None:
            return AgentTurn(
                "证据已记录，但 Verifier 尚未配置；配置后输入 /retry。"
            )
        try:
            receipt = self.runtime.evaluate_current(self.verifier)
        except (
            EvaluationConflictError,
            VerificationOutputError,
            VerificationProviderError,
        ) as error:
            return AgentTurn(
                "判定未完成，状态保持 evidence_pending；恢复后输入 /retry。"
                f"错误类型：{type(error).__name__}"
            )
        return self._present(
            PresentationKind.FEEDBACK,
            self.runtime.next_action(),
            decision=receipt.decision,
        )

    def _present(
        self,
        kind: PresentationKind,
        action,
        student_message: str | None = None,
        decision=None,
    ) -> AgentTurn:
        state = self.runtime.get_state()
        text = self.presenter.present(PresentationRequest(
            kind=kind,
            action=action,
            state=state,
            student_message=student_message,
            decision=decision,
        ))
        if kind is PresentationKind.ACTION:
            required = "、".join(action.required_sections)
            attachment = (
                "至少一个附件"
                if action.attachment_policy == "at-least-one"
                else "可选"
            )
            text = f"本 Gate 必填栏目：{required}\n附件：{attachment}\n\n{text}"
        return AgentTurn(text)
