# Agent Tool Seam Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove a deterministic Fake Agent can drive the learning Runtime through structured Python tools without invoking or parsing the CLI.

**Architecture:** Extract the session workflow from `cli.py` into a focused `LearningRuntime` application service. The Fake Agent and CLI both call that service; existing Manifest, Workspace, Git, Ledger, Coordinator, and State Machine components remain unchanged and authoritative.

**Tech Stack:** Python 3.12+, frozen dataclasses, pathlib, pytest, real temporary Git repositories, uv.

---

## File map

- Create `learning_runtime/runtime.py`: agent-facing session application service and structured submission receipt.
- Create `tests/learning_runtime/test_agent_tool_seam.py`: deterministic Fake Agent acceptance test with a real temporary student repository.
- Modify `learning_runtime/cli.py`: thin terminal adapter over `LearningRuntime`.
- Modify `tests/learning_runtime/test_end_to_end_foundation.py`: preserve the public CLI contract after extraction.
- Modify `docs/runtime-foundation.md`: state the exact boundary between Runtime, Fake Agent, and future LLM Agent.

### Task 1: Agent-facing LearningRuntime

**Files:**
- Create: `tests/learning_runtime/test_agent_tool_seam.py`
- Create: `learning_runtime/runtime.py`

- [ ] **Step 1: Write the failing Fake Agent acceptance test**

Add a test-only deterministic driver that never imports or calls CLI behavior:

```python
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

import pytest

from learning_runtime.runtime import LearningRuntime, SubmissionReceipt
from learning_runtime.schemas import ActionContract, GateStatus
from learning_runtime.storage.event_ledger import EventLedger


def git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def fill_and_commit_gate_zero(repo: Path) -> tuple[Path, Path]:
    answer = repo / "homework_answer/week-01/gate-00.md"
    text = re.sub(
        r"<!--.*?-->",
        "我的独立回答与证据",
        answer.read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    text = text.replace(
        "我的独立回答与证据\n\n## 提交自检",
        "我的独立回答与证据\n\n"
        "![手写推导](attachments/gate-00/shape.jpg)\n\n"
        "## 提交自检",
        1,
    )
    answer.write_text(text, encoding="utf-8")
    attachment = repo / "homework_answer/week-01/attachments/gate-00/shape.jpg"
    attachment.write_bytes(b"handwritten-shape")
    git(repo, "add", str(answer.relative_to(repo)))
    git(repo, "add", str(attachment.relative_to(repo)))
    git(repo, "commit", "-m", "answer gate 0")
    return answer, attachment


@dataclass
class FakeAgent:
    runtime: LearningRuntime
    action: ActionContract | None = None

    def begin(self) -> ActionContract:
        self.action = self.runtime.start_session("week-01")
        return self.action

    def submit_current(self) -> SubmissionReceipt:
        assert self.action is not None
        return self.runtime.submit_answer(self.action.current_gate)
```

The test must:

```python
def test_fake_agent_drives_runtime_without_cli(student_repo, monkeypatch):
    git(student_repo, "switch", "-c", "learner/test/week-01")
    runtime = LearningRuntime(student_repo, student_repo / ".learning-os")
    monkeypatch.setattr(
        "learning_runtime.cli.main",
        lambda *_args, **_kwargs: pytest.fail("Fake Agent called CLI"),
    )
    agent = FakeAgent(runtime)

    action = agent.begin()
    assert action.current_gate == "week-01-gate-0"
    assert action.answer_path == "homework_answer/week-01/gate-00.md"

    answer, attachment = fill_and_commit_gate_zero(student_repo)
    status_before = git(student_repo, "status", "--porcelain")
    head_before = git(student_repo, "rev-parse", "HEAD")
    receipt = agent.submit_current()

    assert receipt.state.gate_status is GateStatus.EVIDENCE_PENDING
    assert receipt.evidence_id == "evidence-0001"
    assert receipt.branch == "learner/test/week-01"
    assert receipt.commit_sha == head_before
    assert git(student_repo, "status", "--porcelain") == status_before
    assert git(student_repo, "rev-parse", "HEAD") == head_before

    events = EventLedger(student_repo / ".learning-os/events.jsonl").read()
    assert [event.event_type for event in events] == [
        "session_started",
        "artifact_observed",
        "attempt_submitted",
        "transition_applied",
    ]
    observation = events[1].payload["observation"]
    assert observation["branch"] == receipt.branch
    assert observation["commit_sha"] == receipt.commit_sha
    assert observation["content_hash"].startswith("sha256:")
    assert observation["attachments"][0]["content_hash"].startswith("sha256:")
```

Read the Ledger and assert the exact event sequence plus branch, commit SHA, answer hash, and attachment hash in `artifact_observed`.

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
uv run pytest tests/learning_runtime/test_agent_tool_seam.py -q
```

Expected: collection fails because `learning_runtime.runtime.LearningRuntime` does not exist.

- [ ] **Step 3: Implement the minimal structured Runtime service**

Create `learning_runtime/runtime.py` with:

```python
from dataclasses import dataclass
from pathlib import Path

from learning_runtime.coordinator import Coordinator
from learning_runtime.manifest import load_manifest
from learning_runtime.schemas import (
    ActionContract,
    GateStatus,
    LearnerState,
)
from learning_runtime.state_machine import LearningStateMachine
from learning_runtime.storage.event_ledger import EventLedger
from learning_runtime.storage.learner_state import replay_state
from learning_runtime.workspace.answer_workspace import AnswerWorkspace
from learning_runtime.workspace.git_guard import GitGuard


@dataclass(frozen=True)
class SubmissionReceipt:
    state: LearnerState
    evidence_id: str
    branch: str
    commit_sha: str


class LearningRuntime:
    def __init__(self, repo_root: Path, runtime_dir: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.ledger = EventLedger(runtime_dir / "events.jsonl")

    def start_session(self, phase: str) -> ActionContract:
        manifest = self._manifest(phase)
        if self.ledger.path.exists():
            raise ValueError(
                f"学习 session 已经存在：{self.ledger.path}；请使用 resume。"
            )
        branch = GitGuard(self.repo_root).assert_student_branch(
            manifest.learner_workspace.protected_branches
        )
        first_gate = manifest.gates[0]
        answer = AnswerWorkspace(self.repo_root, manifest).initialize(first_gate)
        self.ledger.append(
            "session_started",
            {
                "course_id": manifest.course_id,
                "phase_id": manifest.phase_id,
                "current_gate": first_gate.gate_id,
                "unresolved_p0_nodes": list(first_gate.knowledge_node_ids),
                "manifest_path": "course-manifests/week-01.yaml",
                "student_branch": branch,
                "answer_path": answer.artifact_path.as_posix(),
            },
        )
        return Coordinator(manifest).next_action(self.get_state())

    def next_action(self) -> ActionContract:
        state = self.get_state()
        return Coordinator(self._manifest(state.phase_id)).next_action(state)

    def submit_answer(self, gate_id: str) -> SubmissionReceipt:
        state = self.get_state()
        manifest = self._manifest(state.phase_id)
        if gate_id != state.current_gate:
            raise ValueError(
                f"提交 Gate {gate_id} 与当前 Gate {state.current_gate} 不一致。"
            )
        if state.gate_status is not GateStatus.ACTIVE:
            raise ValueError(
                f"当前状态 {state.gate_status.value} 不允许再次提交。"
            )

        gate = manifest.gate(gate_id)
        guard = GitGuard(self.repo_root)
        guard.assert_student_branch(manifest.learner_workspace.protected_branches)
        inspection = AnswerWorkspace(self.repo_root, manifest).inspect(gate)
        snapshot = guard.snapshot_committed(
            [inspection.artifact_path, *inspection.attachment_paths]
        )
        evidence_id = "evidence-" + str(
            sum(
                event.event_type == "artifact_observed"
                for event in self.ledger.read()
            )
            + 1
        ).zfill(4)
        artifact_key = inspection.artifact_path.as_posix()
        evidence_refs = (evidence_id,)
        self.ledger.append(
            "artifact_observed",
            {
                "evidence_id": evidence_id,
                "type": "committed-answer",
                "source": artifact_key,
                "observation": {
                    "gate_id": gate_id,
                    "branch": snapshot.branch,
                    "commit_sha": snapshot.commit_sha,
                    "content_hash": snapshot.content_hashes[artifact_key],
                    "attachments": [
                        {
                            "path": path.as_posix(),
                            "content_hash": snapshot.content_hashes[path.as_posix()],
                        }
                        for path in inspection.attachment_paths
                    ],
                },
            },
            evidence_refs,
        )
        self.ledger.append(
            "attempt_submitted",
            {"gate_id": gate_id, "evidence_id": evidence_id},
            evidence_refs,
        )
        state_after_attempt = self.get_state()
        transition = LearningStateMachine(manifest).transition(
            state_after_attempt,
            GateStatus.EVIDENCE_PENDING,
        )
        self.ledger.append(
            transition.event_type,
            dict(transition.payload),
            evidence_refs,
        )
        return SubmissionReceipt(
            state=self.get_state(),
            evidence_id=evidence_id,
            branch=snapshot.branch,
            commit_sha=snapshot.commit_sha,
        )

    def get_state(self) -> LearnerState:
        events = self.ledger.read()
        if not events:
            raise ValueError("没有可恢复的学习 session；请先运行 start week-01。")
        return replay_state(events)

    def _manifest(self, phase: str):
        if phase != "week-01":
            raise ValueError(f"当前 MVP 只支持 week-01，收到：{phase}")
        return load_manifest(
            self.repo_root / "course-manifests/week-01.yaml",
            self.repo_root,
        )
```

Move the existing workflow without changing its rules:

- `_manifest_for_phase` becomes `_manifest(phase)` on the service;
- `_load_state` becomes `get_state()` and always replays the service Ledger;
- `start_session` validates branch, initializes the current Gate, appends `session_started`, then returns `ActionContract`;
- `next_action` replays state and returns `Coordinator.next_action`;
- `submit_answer` performs all answer/Git checks before events, appends `artifact_observed`, `attempt_submitted`, and `transition_applied`, then returns `SubmissionReceipt`;
- `get_state` always replays Ledger and never caches authority.

Do not add model calls, grading, retries, prompts, Git writes, or new Gate statuses.

- [ ] **Step 4: Run the test and verify GREEN**

Run:

```bash
uv run pytest tests/learning_runtime/test_agent_tool_seam.py -q
```

Expected: `1 passed`.

- [ ] **Step 5: Commit the Agent tool seam**

```bash
git add learning_runtime/runtime.py tests/learning_runtime/test_agent_tool_seam.py
git commit -m "feat: expose learning runtime to agents"
```

### Task 2: Make CLI a thin adapter

**Files:**
- Modify: `learning_runtime/cli.py`
- Modify: `tests/learning_runtime/test_end_to_end_foundation.py`

- [ ] **Step 1: Strengthen the existing CLI regression assertion**

Keep the real end-to-end flow and add assertions that the CLI output still includes the structured receipt projected as text:

```python
assert "已记录 week-01-gate-0 的一次独立尝试：evidence-0001" in output
assert "证据来源：learner/test/week-01@" in output
```

- [ ] **Step 2: Run the CLI regression before refactoring**

Run:

```bash
uv run pytest tests/learning_runtime/test_end_to_end_foundation.py -q
```

Expected: PASS, establishing the behavior that extraction must preserve.

- [ ] **Step 3: Replace workflow logic with LearningRuntime calls**

In `main`, construct:

```python
runtime = LearningRuntime(REPO_ROOT, args.runtime_dir)
```

Then route commands as follows:

```python
if args.command == "start":
    _render_action(runtime.start_session(args.phase))
    return 0
if args.command == "next":
    _render_action(runtime.next_action())
    return 0
if args.command == "submit":
    receipt = runtime.submit_answer(args.gate)
    _render_submission(receipt)
    return 0
if args.command == "status":
    _render_state(runtime.get_state())
    return 0
if args.command == "resume":
    print("已从事件账本恢复学习状态。")
    _render_state(runtime.get_state())
    return 0
```

Delete duplicated Manifest, Workspace, Git, Ledger, and State Machine workflow imports and private helpers from `cli.py`. Keep parser and rendering functions only.

- [ ] **Step 4: Verify CLI and Agent paths together**

Run:

```bash
uv run pytest tests/learning_runtime/test_agent_tool_seam.py tests/learning_runtime/test_end_to_end_foundation.py tests/learning_runtime/test_cli.py -q
```

Expected: all tests pass with the same Runtime serving both adapters.

- [ ] **Step 5: Commit the thin CLI adapter**

```bash
git add learning_runtime/cli.py tests/learning_runtime/test_end_to_end_foundation.py
git commit -m "refactor: drive cli through learning runtime"
```

### Task 3: Document and verify the Agent-ready milestone

**Files:**
- Modify: `docs/runtime-foundation.md`

- [ ] **Step 1: Update the boundary documentation**

Document these three distinct layers:

```text
LearningRuntime = deterministic tools and authority
Fake Agent      = CI proof that an agent can call those tools without CLI
LLM Agent v0    = next milestone: model loop + tool schemas + minimal Verifier
```

State explicitly that passing the Fake Agent test proves interface readiness, not teaching quality or answer correctness.

- [ ] **Step 2: Run complete verification**

Run:

```bash
uv run pytest -q
uv run python scripts/verify_course_pdfs.py
git diff --check
```

Expected: all tests pass; four PDFs verify; no whitespace errors.

- [ ] **Step 3: Commit documentation**

```bash
git add docs/runtime-foundation.md
git commit -m "docs: mark agent tool seam milestone"
```

## Explicitly deferred to Agent v0

- Real LLM provider integration and API credentials.
- Tool schema serialization for a specific provider SDK.
- Prompt/persona design and conversational coaching.
- Semantic or rubric-based answer verification.
- Automatic PASS, REINFORCE, or DIAGNOSE decisions.
- Runtime-authored Git branches or commits.
