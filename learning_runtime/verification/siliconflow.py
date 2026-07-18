from base64 import b64encode
import json
import mimetypes
import os
from typing import Mapping

from openai import OpenAI

from learning_runtime.verification.models import (
    RawVerificationResponse,
    VerificationRequest,
    VerifierIdentity,
)


DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "Qwen/Qwen3.6-35B-A3B"
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".webp"}


class SiliconFlowConfigError(ValueError):
    """Raised for missing provider configuration without exposing secrets."""


class SiliconFlowResponseError(ValueError):
    """Raised when provider output is empty or malformed."""


class SiliconFlowVerifier:
    def __init__(self, client, model: str = DEFAULT_MODEL) -> None:
        self.client = client
        self.model = model
        self.identity = VerifierIdentity(
            provider="siliconflow",
            model=model,
            prompt_version="gate-rubric-v1",
            schema_version="criterion-json-v1",
            settings={
                "temperature": 0,
                "enable_thinking": False,
                "max_tokens": 1200,
            },
        )

    @classmethod
    def from_env(cls) -> "SiliconFlowVerifier":
        api_key = os.environ.get("SILICONFLOW_API_KEY")
        if not api_key:
            raise SiliconFlowConfigError(
                "SILICONFLOW_API_KEY is required for live verification"
            )
        base_url = os.environ.get("SILICONFLOW_BASE_URL", DEFAULT_BASE_URL)
        model = os.environ.get("SILICONFLOW_MODEL", DEFAULT_MODEL)
        return cls(OpenAI(api_key=api_key, base_url=base_url), model)

    def verify(self, request: VerificationRequest) -> RawVerificationResponse:
        prompt = {
            "instruction": (
                "Evaluate only the supplied rubric criteria. Output JSON only. "
                "Never output gate_status, recommendation, target_gate, or evidence_refs."
            ),
            "rubric": {
                "rubric_id": request.rubric.rubric_id,
                "version": request.rubric.version,
                "criteria": [
                    {
                        "criterion_id": item.criterion_id,
                        "standard": item.standard,
                        "passed_when": list(item.passed_when),
                        "failed_when": list(item.failed_when),
                        "insufficient_when": list(item.insufficient_when),
                        "allowed_failure_modes": list(item.allowed_failure_modes),
                    }
                    for item in request.rubric.criteria
                ],
            },
            "answer": request.answer_text,
            "output_contract": {
                "criteria": [{
                    "criterion_id": "string",
                    "status": "passed | failed | insufficient_evidence",
                    "reason": "string",
                    "evidence_quotes": ["exact quote from answer"],
                    "failure_mode": "reinforce | diagnose | null",
                }]
            },
        }
        content: list[dict[str, object]] = [
            {"type": "text", "text": json.dumps(prompt, ensure_ascii=False)}
        ]
        for attachment in request.attachments:
            suffix = os.path.splitext(attachment.path)[1].lower()
            if suffix not in SUPPORTED_IMAGES:
                continue
            mime = mimetypes.types_map.get(suffix, "image/jpeg")
            encoded = b64encode(attachment.content).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{encoded}"},
            })
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=1200,
                stream=False,
                extra_body={"enable_thinking": False},
            )
            text = response.choices[0].message.content
            payload = json.loads(text)
        except (AttributeError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise SiliconFlowResponseError("invalid SiliconFlow JSON response") from error
        if not isinstance(payload, Mapping):
            raise SiliconFlowResponseError("SiliconFlow response must be a JSON object")
        usage = getattr(response, "usage", None)
        return RawVerificationResponse(
            payload=dict(payload),
            response_id=str(getattr(response, "id", "")),
            model=str(getattr(response, "model", self.model)),
            usage={
                "prompt_tokens": int(getattr(usage, "prompt_tokens", 0)),
                "completion_tokens": int(getattr(usage, "completion_tokens", 0)),
                "total_tokens": int(getattr(usage, "total_tokens", 0)),
            },
        )
