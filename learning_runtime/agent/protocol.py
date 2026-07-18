from typing import Protocol

from learning_runtime.agent.models import PresentationRequest


class PresenterError(RuntimeError):
    """A recoverable conversation-provider failure."""


class ConversationPresenter(Protocol):
    def present(self, request: PresentationRequest) -> str: ...
