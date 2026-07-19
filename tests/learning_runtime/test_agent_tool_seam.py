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


def fill_and_commit_gate_zero(repo: Path) -> None:
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
    attachment = (
        repo / "homework_answer/week-01/attachments/gate-00/shape.jpg"
    )
    attachment.write_bytes(b"handwritten-shape")
    git(repo, "add", str(answer.relative_to(repo)))
    git(repo, "add", str(attachment.relative_to(repo)))
    git(repo, "commit", "-m", "answer gate 0")


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


def test_fake_agent_drives_runtime_without_cli(
    student_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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

    fill_and_commit_gate_zero(student_repo)
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
