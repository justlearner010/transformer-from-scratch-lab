from learning_runtime.agent.models import PresentationKind, PresentationRequest
from learning_runtime.agent.protocol import ConversationPresenter, PresenterError


class DeterministicPresenter:
    def present(self, request: PresentationRequest) -> str:
        action = request.action
        if request.kind is PresentationKind.FEEDBACK and request.decision is not None:
            return (
                f"判定结果：{request.decision.recommendation.value}\n"
                f"原因：{request.decision.reason}\n"
                f"下一步：{request.decision.next_action}"
            )
        checks = "；".join(action.checks)
        return (
            f"当前 Gate：{action.current_gate}\n"
            f"当前任务：{action.action}\n"
            f"作答文件：{action.answer_path}\n"
            f"提交检查：{checks}\n"
            "完成并手动 commit 后输入 /submit。"
        )


class SafePresenter:
    def __init__(
        self,
        primary: ConversationPresenter,
        fallback: ConversationPresenter,
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    def present(self, request: PresentationRequest) -> str:
        try:
            text = self.primary.present(request).strip()
            if not text:
                raise PresenterError("presenter returned empty text")
            return text
        except PresenterError:
            return self.fallback.present(request)
