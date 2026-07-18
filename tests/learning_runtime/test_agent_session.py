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
