import json
import os

from openai import OpenAI, OpenAIError

from learning_runtime.agent.models import PresentationRequest
from learning_runtime.agent.protocol import PresenterError
from learning_runtime.verification.siliconflow import DEFAULT_BASE_URL, DEFAULT_MODEL


class SiliconFlowPresenterError(PresenterError):
    """A recoverable conversation-provider failure."""


class SiliconFlowPresenter:
    def __init__(self, client, model: str = DEFAULT_MODEL) -> None:
        self.client = client
        self.model = model

    @classmethod
    def from_env(cls) -> "SiliconFlowPresenter":
        key = os.environ.get("SILICONFLOW_API_KEY")
        if not key:
            raise SiliconFlowPresenterError(
                "SILICONFLOW_API_KEY is not configured"
            )
        base_url = os.environ.get("SILICONFLOW_BASE_URL", DEFAULT_BASE_URL)
        model = os.environ.get("SILICONFLOW_MODEL", DEFAULT_MODEL)
        return cls(OpenAI(api_key=key, base_url=base_url), model)

    def present(self, request: PresentationRequest) -> str:
        payload = {
            "kind": request.kind.value,
            "gate": request.action.current_gate,
            "reason": request.action.reason,
            "action": request.action.action,
            "answer_path": request.action.answer_path,
            "checks": list(request.action.checks),
            "required_sections": list(request.action.required_sections),
            "student_message": request.student_message,
            "decision": (
                request.decision.recommendation.value
                if request.decision is not None else None
            ),
        }
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": (
                        "你只解释给定的当前学习动作。不得给答案、关键中间结果、"
                        "声称状态改变或要求隐式执行命令。"
                        "状态动作只能由学生输入斜杠命令。"
                    )},
                    {"role": "user", "content": json.dumps(
                        payload, ensure_ascii=False
                    )},
                ],
                temperature=0,
                max_tokens=600,
                stream=False,
                extra_body={"enable_thinking": False},
            )
            text = response.choices[0].message.content
        except OpenAIError as error:
            raise SiliconFlowPresenterError(
                "conversation provider failed"
            ) from error
        except (AttributeError, IndexError, TypeError) as error:
            raise SiliconFlowPresenterError(
                "conversation provider returned an invalid response"
            ) from error
        if not isinstance(text, str) or not text.strip():
            raise SiliconFlowPresenterError(
                "conversation provider returned empty text"
            )
        return text.strip()
