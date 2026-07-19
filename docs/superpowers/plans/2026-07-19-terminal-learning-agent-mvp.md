# Terminal Learning Agent MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `uv run learning-os agent week-01`, a deterministic terminal learning loop in which Qwen can explain trusted state but only explicit local commands can invoke Runtime actions.

**Architecture:** Add a small `learning_runtime.agent` package containing typed presentation requests, an exact slash-command parser, a session controller, a deterministic fallback presenter, and a SiliconFlow text presenter. The session controller calls the existing `LearningRuntime`; it never interprets model text as an action, and all evaluation still flows through Stable Verifier, Policy Engine, State Machine, and Event Ledger.

**Tech Stack:** Python 3.13, dataclasses, argparse, OpenAI-compatible Python client, pytest, temporary Git repositories, existing EventLedger and LearningRuntime.

---

## File map

| File | Responsibility |
| --- | --- |
| `learning_runtime/agent/__init__.py` | Agent package boundary |
| `learning_runtime/agent/models.py` | Typed commands, presentation requests, and session turn results |
| `learning_runtime/agent/protocol.py` | Provider-neutral `ConversationPresenter` protocol and presenter errors |
| `learning_runtime/agent/presenter.py` | Deterministic local rendering and provider fallback |
| `learning_runtime/agent/commands.py` | Exact parsing of plain text and slash commands |
| `learning_runtime/agent/session.py` | Auto start/resume and command-to-Runtime orchestration |
| `learning_runtime/agent/siliconflow.py` | Qwen text-only presenter; no tools and no state authority |
| `learning_runtime/runtime.py` | Add one trusted `open_session()` entry point |
| `learning_runtime/cli.py` | Expose and run `learning-os agent week-01` |
| `tests/learning_runtime/test_agent_presenter.py` | Typed rendering and fallback tests |
| `tests/learning_runtime/test_agent_commands.py` | Command authority table tests |
| `tests/learning_runtime/test_agent_session.py` | Start/resume, submit/retry, recovery, and Git ownership tests |
| `tests/learning_runtime/test_siliconflow_presenter.py` | Provider request contract and malformed-response tests |
| `tests/live/test_siliconflow_agent_live.py` | Optional real text-generation smoke test |
| `README.md` | Student-facing Agent command and boundary documentation |
| `docs/runtime-foundation.md` | Runtime/Agent authority and recovery contract |

### Task 1: Typed presentation boundary and deterministic fallback

**Files:**
- Create: `learning_runtime/agent/__init__.py`
- Create: `learning_runtime/agent/models.py`
- Create: `learning_runtime/agent/protocol.py`
- Create: `learning_runtime/agent/presenter.py`
- Test: `tests/learning_runtime/test_agent_presenter.py`

- [ ] **Step 1: Write failing tests for typed, state-independent rendering**

```python
from learning_runtime.agent.models import PresentationKind, PresentationRequest
from learning_runtime.agent.presenter import DeterministicPresenter, SafePresenter
from learning_runtime.agent.protocol import PresenterError
from learning_runtime.schemas import ActionContract, GateStatus, LearnerState


def request(kind=PresentationKind.ACTION, student_message=None):
    action = ActionContract(
        current_capability="explain attention shapes",
        current_gate="week-01-gate-0",
        reason="first prerequisite",
        action="write the closed shape chain",
        answer_path="homework_answer/week-01/gate-00.md",
        checks=("all shapes close", "explain K.T"),
        hint_level=0,
    )
    state = LearnerState(
        course_id="transformer-from-scratch-lab",
        phase_id="week-01",
        current_gate="week-01-gate-0",
        gate_status=GateStatus.ACTIVE,
    )
    return PresentationRequest(kind, action, state, student_message)


class BrokenPresenter:
    def present(self, request):
        raise PresenterError("provider unavailable")


def test_deterministic_presenter_renders_action():
    presentation = request()
    text = DeterministicPresenter().present(presentation)
    assert presentation.action.current_gate in text
    assert presentation.action.answer_path in text
    assert "/submit" in text


def test_safe_presenter_falls_back_without_changing_request():
    presentation = request(PresentationKind.EXPLANATION, "我应该做什么？")
    text = SafePresenter(
        BrokenPresenter(), DeterministicPresenter()
    ).present(presentation)
    assert presentation.state.gate_status is GateStatus.ACTIVE
    assert presentation.action.action in text
```

- [ ] **Step 2: Run the tests and verify the missing package failure**

Run: `uv run pytest tests/learning_runtime/test_agent_presenter.py -q`

Expected: collection fails with `ModuleNotFoundError: No module named 'learning_runtime.agent'`.

- [ ] **Step 3: Implement the presentation types and protocol**

```python
# learning_runtime/agent/models.py
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
```

```python
# learning_runtime/agent/protocol.py
from typing import Protocol
from learning_runtime.agent.models import PresentationRequest


class PresenterError(RuntimeError):
    pass


class ConversationPresenter(Protocol):
    def present(self, request: PresentationRequest) -> str: ...
```

- [ ] **Step 4: Implement deterministic rendering and provider fallback**

```python
# learning_runtime/agent/presenter.py
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
```

- [ ] **Step 5: Run tests and commit**

Run: `uv run pytest tests/learning_runtime/test_agent_presenter.py -q`

Expected: `2 passed`.

```bash
git add learning_runtime/agent tests/learning_runtime/test_agent_presenter.py
git commit -m "feat: define safe agent presentation boundary"
```

### Task 2: Exact command authority

**Files:**
- Modify: `learning_runtime/agent/models.py`
- Create: `learning_runtime/agent/commands.py`
- Test: `tests/learning_runtime/test_agent_commands.py`

- [ ] **Step 1: Write a table-driven failing test**

```python
import pytest

from learning_runtime.agent.commands import parse_agent_input
from learning_runtime.agent.models import AgentCommand, InputKind


@pytest.mark.parametrize(
    ("raw", "kind", "command"),
    [
        ("/submit", InputKind.COMMAND, AgentCommand.SUBMIT),
        (" /status ", InputKind.COMMAND, AgentCommand.STATUS),
        ("/retry", InputKind.COMMAND, AgentCommand.RETRY),
        ("我完成了", InputKind.MESSAGE, None),
        ("请帮我 /submit", InputKind.MESSAGE, None),
        ("/unknown", InputKind.UNKNOWN_COMMAND, None),
        ("", InputKind.EMPTY, None),
    ],
)
def test_parse_agent_input_never_infers_actions(raw, kind, command):
    parsed = parse_agent_input(raw)
    assert parsed.kind is kind
    assert parsed.command is command
```

- [ ] **Step 2: Run it and verify the missing parser failure**

Run: `uv run pytest tests/learning_runtime/test_agent_commands.py -q`

Expected: collection fails because `learning_runtime.agent.commands` does not exist.

- [ ] **Step 3: Implement exact command parsing**

```python
# additions to learning_runtime/agent/models.py
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
```

```python
# learning_runtime/agent/commands.py
from learning_runtime.agent.models import AgentCommand, AgentInput, InputKind


COMMANDS = {f"/{command.value}": command for command in AgentCommand}


def parse_agent_input(raw: str) -> AgentInput:
    stripped = raw.strip()
    if not stripped:
        return AgentInput(InputKind.EMPTY, raw)
    if stripped in COMMANDS:
        return AgentInput(InputKind.COMMAND, raw, COMMANDS[stripped])
    if stripped.startswith("/"):
        return AgentInput(InputKind.UNKNOWN_COMMAND, raw)
    return AgentInput(InputKind.MESSAGE, raw)
```

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/learning_runtime/test_agent_commands.py -q`

Expected: `7 passed`.

```bash
git add learning_runtime/agent/models.py learning_runtime/agent/commands.py tests/learning_runtime/test_agent_commands.py
git commit -m "feat: make agent commands deterministic"
```

### Task 3: Trusted auto-start/resume and read-only session loop

**Files:**
- Modify: `learning_runtime/runtime.py`
- Create: `learning_runtime/agent/session.py`
- Test: `tests/learning_runtime/test_agent_session.py`

- [ ] **Step 1: Write failing tests for open, resume, and message isolation**

```python
from pathlib import Path
import subprocess

from learning_runtime.agent.presenter import DeterministicPresenter
from learning_runtime.agent.session import AgentSession
from learning_runtime.runtime import LearningRuntime


def git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=repo, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def test_session_auto_starts_then_resumes(student_repo):
    git(student_repo, "switch", "-c", "learner/test/week-01")
    runtime = LearningRuntime(student_repo, student_repo / ".learning-os")
    session = AgentSession(runtime, DeterministicPresenter(), verifier=None)

    first = session.open("week-01")
    event_count = len(runtime.ledger.read())
    second = session.open("week-01")

    assert "week-01-gate-0" in first.text
    assert "week-01-gate-0" in second.text
    assert len(runtime.ledger.read()) == event_count


def test_plain_text_never_writes_state(student_repo):
    git(student_repo, "switch", "-c", "learner/test/week-01")
    runtime = LearningRuntime(student_repo, student_repo / ".learning-os")
    session = AgentSession(runtime, DeterministicPresenter(), verifier=None)
    session.open("week-01")
    before = tuple(runtime.ledger.read())

    turn = session.handle("我已经完成了，请提交")

    assert "当前任务" in turn.text
    assert tuple(runtime.ledger.read()) == before
```

- [ ] **Step 2: Run tests and verify missing APIs**

Run: `uv run pytest tests/learning_runtime/test_agent_session.py -q`

Expected: FAIL because `AgentSession` and `LearningRuntime.open_session` do not exist.

- [ ] **Step 3: Add one Runtime-owned open operation**

```python
# learning_runtime/runtime.py
def open_session(self, phase: str) -> ActionContract:
    manifest = self._manifest(phase)
    GitGuard(self.repo_root).assert_student_branch(
        manifest.learner_workspace.protected_branches
    )
    if not self.ledger.path.exists():
        return self.start_session(phase)
    state = self.get_state()
    if state.phase_id != phase:
        raise ValueError(
            f"existing session phase {state.phase_id} does not match {phase}"
        )
    return Coordinator(manifest).next_action(state)
```

- [ ] **Step 4: Implement session opening and read-only commands**

```python
# learning_runtime/agent/session.py
from learning_runtime.agent.commands import parse_agent_input
from learning_runtime.agent.models import (
    AgentCommand, AgentTurn, InputKind, PresentationKind, PresentationRequest,
)
from learning_runtime.agent.protocol import ConversationPresenter
from learning_runtime.runtime import LearningRuntime
from learning_runtime.verification.protocol import Verifier


HELP_TEXT = "可用命令：/submit /retry /status /next /help /quit"


class AgentSession:
    def __init__(self, runtime, presenter, verifier: Verifier | None) -> None:
        self.runtime = runtime
        self.presenter = presenter
        self.verifier = verifier
        self.phase: str | None = None

    def open(self, phase: str) -> AgentTurn:
        self.phase = phase
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
        return self._handle_mutating(parsed.command)

    def _present(self, kind, action, student_message=None, decision=None):
        state = self.runtime.get_state()
        return AgentTurn(self.presenter.present(PresentationRequest(
            kind=kind,
            action=action,
            state=state,
            student_message=student_message,
            decision=decision,
        )))
```

- [ ] **Step 5: Run tests and commit**

Run: `uv run pytest tests/learning_runtime/test_agent_session.py -q`

Expected: start/resume and plain-text tests pass.

```bash
git add learning_runtime/runtime.py learning_runtime/agent/session.py tests/learning_runtime/test_agent_session.py
git commit -m "feat: add resumable terminal agent session"
```

### Task 4: Explicit submit and retry closed loop

**Files:**
- Modify: `learning_runtime/agent/session.py`
- Modify: `learning_runtime/verification/protocol.py`
- Modify: `learning_runtime/verification/siliconflow.py`
- Modify: `tests/learning_runtime/test_agent_session.py`

- [ ] **Step 1: Add failing end-to-end submit and retry tests**

```python
import re

from learning_runtime.agent.presenter import DeterministicPresenter
from learning_runtime.agent.session import AgentSession
from learning_runtime.runtime import LearningRuntime
from learning_runtime.verification.models import (
    RawVerificationResponse, VerifierIdentity,
)


class PayloadVerifier:
    identity = VerifierIdentity(
        provider="fixture",
        model="fixture",
        prompt_version="gate-rubric-v1",
        schema_version="criterion-json-v1",
        settings={"temperature": 0},
    )

    def verify(self, request):
        return RawVerificationResponse(
            payload={"criteria": [{
                "criterion_id": "shape-bridge-complete",
                "status": "passed",
                "reason": "meets rubric",
                "evidence_quotes": ["K.T 交换 K 的最后两个维度"],
                "failure_mode": None,
            }]},
            response_id="fixture-response",
            model="fixture",
            usage={},
        )


def passed_verifier():
    return PayloadVerifier()


def prepared_agent_session(student_repo, verifier, presenter=None):
    git(student_repo, "switch", "-c", "learner/test/week-01")
    runtime = LearningRuntime(student_repo, student_repo / ".learning-os")
    session = AgentSession(
        runtime,
        presenter or DeterministicPresenter(),
        verifier,
    )
    session.open("week-01")
    return runtime, session


def complete_answer_without_commit(student_repo):
    answer = student_repo / "homework_answer/week-01/gate-00.md"
    text = re.sub(
        r"<!--.*?-->",
        "Q、K、V shape 闭合；K.T 交换 K 的最后两个维度。",
        answer.read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    text = text.replace(
        "Q、K、V shape 闭合；K.T 交换 K 的最后两个维度。\n\n## 提交自检",
        "Q、K、V shape 闭合；K.T 交换 K 的最后两个维度。\n\n"
        "![手写](attachments/gate-00/shape.jpg)\n\n## 提交自检",
        1,
    )
    answer.write_text(text, encoding="utf-8")
    image = student_repo / "homework_answer/week-01/attachments/gate-00/shape.jpg"
    image.write_bytes(b"synthetic-image")


def complete_and_commit(student_repo):
    complete_answer_without_commit(student_repo)
    git(student_repo, "add", "homework_answer/week-01")
    git(student_repo, "commit", "-m", "answer gate zero")


def test_submit_requires_student_commit_then_advances_with_verifier(student_repo):
    runtime, session = prepared_agent_session(student_repo, passed_verifier())
    complete_answer_without_commit(student_repo)
    head_before = git(student_repo, "rev-parse", "HEAD")

    rejected = session.handle("/submit")
    assert "commit" in rejected.text.lower()
    assert git(student_repo, "rev-parse", "HEAD") == head_before

    git(student_repo, "add", "homework_answer/week-01")
    git(student_repo, "commit", "-m", "answer gate zero")
    accepted = session.handle("/submit")

    assert runtime.get_state().current_gate == "week-01-gate-1"
    assert "pass" in accepted.text.lower()


def test_missing_verifier_stays_pending_and_retry_is_explicit(student_repo):
    runtime, session = prepared_agent_session(student_repo, verifier=None)
    complete_and_commit(student_repo)

    pending = session.handle("/submit")
    assert runtime.get_state().gate_status.value == "evidence_pending"
    assert "/retry" in pending.text

    session.verifier = passed_verifier()
    completed = session.handle("/retry")
    assert runtime.get_state().current_gate == "week-01-gate-1"
    assert "pass" in completed.text.lower()
```

- [ ] **Step 2: Run only the new tests and verify failure**

Run: `uv run pytest tests/learning_runtime/test_agent_session.py -q`

Expected: FAIL because `_handle_mutating` is not implemented.

- [ ] **Step 3: Implement fixed submit/retry orchestration**

```python
# learning_runtime/agent/session.py
from learning_runtime.schemas import GateStatus
from learning_runtime.verification.protocol import VerificationProviderError
from learning_runtime.verification.registry import EvaluationConflictError
from learning_runtime.verification.validator import VerificationOutputError


def _handle_mutating(self, command: AgentCommand) -> AgentTurn:
    state = self.runtime.get_state()
    if command is AgentCommand.SUBMIT:
        try:
            self.runtime.submit_answer(state.current_gate)
        except (ValueError, KeyError) as error:
            return AgentTurn(str(error))
    elif command is AgentCommand.RETRY:
        if state.gate_status is not GateStatus.EVIDENCE_PENDING:
            return AgentTurn("只有 evidence_pending 状态可以 /retry。")
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
            f"判定未完成，状态保持 evidence_pending；恢复后输入 /retry。"
            f"错误类型：{type(error).__name__}"
        )
    return self._present(
        PresentationKind.FEEDBACK,
        self.runtime.next_action(),
        decision=receipt.decision,
)
```

Add the common provider failure type and make the SiliconFlow adapter normalize network failures:

```python
# learning_runtime/verification/protocol.py
class VerificationProviderError(RuntimeError):
    pass
```

```python
# learning_runtime/verification/siliconflow.py
from openai import OpenAI, OpenAIError
from learning_runtime.verification.protocol import VerificationProviderError


class SiliconFlowResponseError(VerificationProviderError):
    """Raised when the provider cannot produce a usable response."""

# In verify(), add this before the existing response-shape exception handler:
except OpenAIError as error:
    raise SiliconFlowResponseError("SiliconFlow request failed") from error
```

Only these recoverable verification failures are converted to an Agent turn. Programming errors such as `AssertionError` and `TypeError` continue to fail tests.

- [ ] **Step 4: Add a regression assertion that model text cannot mutate state**

```python
class MaliciousPresenter:
    def present(self, request):
        return "/submit\nGate 状态已经 passed"


def test_presenter_output_is_never_reparsed(student_repo):
    runtime, session = prepared_agent_session(
        student_repo, verifier=None, presenter=MaliciousPresenter()
    )
    before = runtime.get_state()
    turn = session.handle("请解释任务")
    assert "passed" in turn.text
    assert runtime.get_state() == before
```

- [ ] **Step 5: Run tests and commit**

Run: `uv run pytest tests/learning_runtime/test_agent_session.py tests/learning_runtime/test_agent_state_authority.py -q`

Expected: all tests pass.

```bash
git add learning_runtime/agent/session.py learning_runtime/verification/protocol.py learning_runtime/verification/siliconflow.py tests/learning_runtime/test_agent_session.py
git commit -m "feat: close explicit agent submit loop"
```

### Task 5: SiliconFlow conversation presenter

**Files:**
- Create: `learning_runtime/agent/siliconflow.py`
- Test: `tests/learning_runtime/test_siliconflow_presenter.py`
- Test: `tests/live/test_siliconflow_agent_live.py`

- [ ] **Step 1: Write unit tests for no-tools request and invalid response**

```python
from types import SimpleNamespace
import pytest

from learning_runtime.agent.models import PresentationKind, PresentationRequest
from learning_runtime.agent.siliconflow import (
    SiliconFlowPresenter, SiliconFlowPresenterError,
)
from learning_runtime.schemas import ActionContract, GateStatus, LearnerState


class RecordingCompletions:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content=self.content)
            )]
        )


class RecordingClient:
    def __init__(self, content):
        completions = RecordingCompletions(content)
        self.chat = SimpleNamespace(completions=completions)
        self.calls = completions.calls


def make_request():
    action = ActionContract(
        current_capability="explain attention shapes",
        current_gate="week-01-gate-0",
        reason="first prerequisite",
        action="write the closed shape chain",
        answer_path="homework_answer/week-01/gate-00.md",
        checks=("all shapes close", "explain K.T"),
        hint_level=0,
    )
    state = LearnerState(
        course_id="transformer-from-scratch-lab",
        phase_id="week-01",
        current_gate="week-01-gate-0",
        gate_status=GateStatus.ACTIVE,
    )
    return PresentationRequest(PresentationKind.ACTION, action, state)


def test_presenter_sends_grounded_text_without_tools():
    client = RecordingClient(content="请完成当前 Gate，并在 commit 后输入 /submit。")
    presenter = SiliconFlowPresenter(client, model="fixture")
    text = presenter.present(make_request())
    kwargs = client.calls[0]
    assert text.startswith("请完成")
    assert "tools" not in kwargs
    assert kwargs["temperature"] == 0
    assert kwargs["extra_body"] == {"enable_thinking": False}


def test_presenter_rejects_empty_response():
    presenter = SiliconFlowPresenter(RecordingClient(content=""), model="fixture")
    with pytest.raises(SiliconFlowPresenterError):
        presenter.present(make_request())
```

- [ ] **Step 2: Run unit tests and verify missing adapter failure**

Run: `uv run pytest tests/learning_runtime/test_siliconflow_presenter.py -q`

Expected: collection fails because `learning_runtime.agent.siliconflow` does not exist.

- [ ] **Step 3: Implement the isolated text presenter**

```python
# learning_runtime/agent/siliconflow.py
import json
import os
from openai import OpenAI, OpenAIError

from learning_runtime.agent.models import PresentationRequest
from learning_runtime.agent.protocol import PresenterError
from learning_runtime.verification.siliconflow import DEFAULT_BASE_URL, DEFAULT_MODEL


class SiliconFlowPresenterError(PresenterError):
    pass


class SiliconFlowPresenter:
    def __init__(self, client, model: str = DEFAULT_MODEL) -> None:
        self.client = client
        self.model = model

    @classmethod
    def from_env(cls):
        key = os.environ.get("SILICONFLOW_API_KEY")
        if not key:
            raise SiliconFlowPresenterError("SILICONFLOW_API_KEY is not configured")
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
                        "声称状态改变或要求隐式执行命令。状态动作只能由学生输入斜杠命令。"
                    )},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                temperature=0,
                max_tokens=600,
                stream=False,
                extra_body={"enable_thinking": False},
            )
            text = response.choices[0].message.content
        except OpenAIError as error:
            raise SiliconFlowPresenterError("conversation provider failed") from error
        except (AttributeError, IndexError, TypeError) as error:
            raise SiliconFlowPresenterError("conversation provider failed") from error
        if not isinstance(text, str) or not text.strip():
            raise SiliconFlowPresenterError("conversation provider returned empty text")
        return text.strip()
```

- [ ] **Step 4: Add the opt-in live smoke test**

```python
import os
import pytest

from learning_runtime.agent.models import PresentationKind, PresentationRequest
from learning_runtime.agent.siliconflow import SiliconFlowPresenter
from learning_runtime.schemas import ActionContract, GateStatus, LearnerState


def make_live_request():
    return PresentationRequest(
        PresentationKind.ACTION,
        ActionContract(
            current_capability="explain attention shapes",
            current_gate="week-01-gate-0",
            reason="first prerequisite",
            action="write the closed shape chain",
            answer_path="homework_answer/week-01/gate-00.md",
            checks=("all shapes close", "explain K.T"),
            hint_level=0,
        ),
        LearnerState(
            course_id="transformer-from-scratch-lab",
            phase_id="week-01",
            current_gate="week-01-gate-0",
            gate_status=GateStatus.ACTIVE,
        ),
    )


@pytest.mark.live
@pytest.mark.skipif(
    not os.environ.get("SILICONFLOW_API_KEY"),
    reason="SILICONFLOW_API_KEY is not configured",
)
def test_live_presenter_returns_non_empty_bounded_text():
    text = SiliconFlowPresenter.from_env().present(make_live_request())
    assert text.strip()
    assert len(text) <= 4000
```

- [ ] **Step 5: Run unit/live selection and commit**

Run: `uv run pytest tests/learning_runtime/test_siliconflow_presenter.py tests/live/test_siliconflow_agent_live.py -q`

Expected without a key: unit tests pass and live test skips.

```bash
git add learning_runtime/agent/siliconflow.py tests/learning_runtime/test_siliconflow_presenter.py tests/live/test_siliconflow_agent_live.py
git commit -m "feat: add bounded siliconflow conversation presenter"
```

### Task 6: CLI REPL, documentation, and full verification

**Files:**
- Modify: `learning_runtime/cli.py`
- Modify: `tests/learning_runtime/test_cli.py`
- Modify: `README.md`
- Modify: `docs/runtime-foundation.md`

- [ ] **Step 1: Write failing CLI parser and loop tests**

```python
from learning_runtime.agent.models import AgentTurn
from learning_runtime.cli import build_parser, run_agent_loop


class FakeAgentSession:
    def __init__(self):
        self.handled = []

    def open(self, phase):
        return AgentTurn(f"opened {phase}")

    def handle(self, raw):
        self.handled.append(raw)
        return AgentTurn(raw, should_exit=raw == "/quit")


def test_cli_exposes_agent_phase():
    args = build_parser().parse_args(["agent", "week-01"])
    assert args.command == "agent"
    assert args.phase == "week-01"


def test_run_agent_exits_on_quit():
    fake_agent_session = FakeAgentSession()
    inputs = iter(["/status", "/quit"])
    output = []
    result = run_agent_loop(
        fake_agent_session,
        "week-01",
        input_fn=lambda _: next(inputs),
        output_fn=output.append,
    )
    assert result == 0
    assert fake_agent_session.handled == ["/status", "/quit"]
```

- [ ] **Step 2: Run CLI tests and verify failure**

Run: `uv run pytest tests/learning_runtime/test_cli.py -q`

Expected: FAIL because the parser has no `agent` command and `run_agent_loop` is missing.

- [ ] **Step 3: Add the CLI command and injectable REPL**

```python
# learning_runtime/cli.py
def run_agent_loop(session, phase, input_fn=input, output_fn=print) -> int:
    output_fn(session.open(phase).text)
    while True:
        try:
            raw = input_fn("learning-os> ")
        except (EOFError, KeyboardInterrupt):
            output_fn("\n学习进度已保存在事件账本中。")
            return 0
        turn = session.handle(raw)
        if turn.text:
            output_fn(turn.text)
        if turn.should_exit:
            return 0
```

Add `agent = commands.add_parser("agent", help="启动稳定学习 Agent")`, its required `phase`, and `--runtime-dir`. In `main`, construct `DeterministicPresenter`, attempt `SiliconFlowPresenter.from_env()` and `SiliconFlowVerifier.from_env()` independently, wrap the text provider with `SafePresenter`, construct `AgentSession`, then call `run_agent_loop`. A missing key must leave `verifier=None` and retain the deterministic Presenter.

Use this exact wiring:

```python
# imports in learning_runtime/cli.py
from learning_runtime.agent.presenter import DeterministicPresenter, SafePresenter
from learning_runtime.agent.protocol import PresenterError
from learning_runtime.agent.session import AgentSession
from learning_runtime.agent.siliconflow import SiliconFlowPresenter
from learning_runtime.verification.siliconflow import (
    SiliconFlowConfigError, SiliconFlowVerifier,
)


# in build_parser()
agent = commands.add_parser("agent", help="启动稳定学习 Agent")
agent.add_argument("phase")
_add_runtime_dir(agent)


def build_agent_session(runtime: LearningRuntime) -> AgentSession:
    fallback = DeterministicPresenter()
    try:
        primary = SiliconFlowPresenter.from_env()
        presenter = SafePresenter(primary, fallback)
    except PresenterError:
        presenter = fallback
    try:
        verifier = SiliconFlowVerifier.from_env()
    except SiliconFlowConfigError:
        verifier = None
    return AgentSession(runtime, presenter, verifier)


# first branch inside main()'s try block
if args.command == "agent":
    return run_agent_loop(build_agent_session(runtime), args.phase)
```

- [ ] **Step 4: Update student-facing documentation**

Document exactly:

```bash
git switch -c learner/<你的名字>/week-01
uv run learning-os agent week-01
```

Document the six slash commands, student-owned commit requirement, automatic recovery, no long-term transcript storage, presenter/verifier separation, `.env` loading, deterministic offline tests, and opt-in live tests. Remove any wording that says an Agent loop is still the next milestone.

- [ ] **Step 5: Run focused and full verification**

Run:

```bash
uv run pytest tests/learning_runtime/test_cli.py tests/learning_runtime/test_agent_session.py -q
uv run pytest -q
uv run python scripts/verify_course_pdfs.py
git diff --check
if git grep -nE 'sk-[A-Za-z0-9]{20,}'; then exit 1; fi
```

Expected:

- focused tests pass;
- full suite passes with live tests skipped when no key is set;
- four course PDFs render and verify;
- no whitespace errors;
- no API-key-shaped string exists in tracked files.

- [ ] **Step 6: Commit final integration**

```bash
git add learning_runtime/cli.py tests/learning_runtime/test_cli.py README.md docs/runtime-foundation.md
git commit -m "feat: expose terminal learning agent"
```

### Final completion audit

- [ ] `uv run learning-os agent week-01` is the only new student entry point.
- [ ] Plain language cannot call Runtime mutation methods.
- [ ] Presenter receives no tool definitions and its text is never reparsed.
- [ ] `/submit` requires committed evidence; `/retry` requires `evidence_pending`.
- [ ] Missing conversation provider degrades to local rendering.
- [ ] Missing verifier leaves committed evidence pending and recoverable.
- [ ] Restart derives the same action from Event Ledger, not chat history.
- [ ] The Agent performs no Git writes.
- [ ] Default tests are offline; live tests are explicit and credential-gated.
- [ ] Gate 1–6, Coach, Diagnostician, multi-Agent, Web UI, and transcript persistence remain outside this plan.
