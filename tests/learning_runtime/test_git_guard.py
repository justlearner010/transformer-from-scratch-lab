from hashlib import sha256
from pathlib import Path
import subprocess

import pytest

from learning_runtime.workspace.git_guard import GitEvidenceError, GitGuard


def git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Runtime Test")
    git(repo, "config", "user.email", "runtime@example.com")
    (repo / "README.md").write_text("course\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "course baseline")
    return repo


def test_protected_branch_is_rejected_without_changing_git_state(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    guard = GitGuard(repo)
    before = git(repo, "status", "--porcelain")

    with pytest.raises(GitEvidenceError, match="main"):
        guard.assert_student_branch(("main", "master"))

    assert git(repo, "status", "--porcelain") == before


def test_untracked_and_staged_answers_are_not_committed_evidence(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    git(repo, "switch", "-c", "learner/test/week-01")
    answer = repo / "homework_answer/week-01/gate-00.md"
    answer.parent.mkdir(parents=True)
    answer.write_text("answer v1\n", encoding="utf-8")
    guard = GitGuard(repo)

    with pytest.raises(GitEvidenceError, match="not tracked"):
        guard.snapshot_committed([Path("homework_answer/week-01/gate-00.md")])

    git(repo, "add", "homework_answer/week-01/gate-00.md")
    with pytest.raises(GitEvidenceError, match="not committed"):
        guard.snapshot_committed([Path("homework_answer/week-01/gate-00.md")])


def test_committed_answer_returns_branch_commit_and_sha256(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    git(repo, "switch", "-c", "learner/test/week-01")
    answer = repo / "homework_answer/week-01/gate-00.md"
    answer.parent.mkdir(parents=True)
    answer.write_bytes(b"answer v1\n")
    git(repo, "add", "homework_answer/week-01/gate-00.md")
    git(repo, "commit", "-m", "answer attempt 1")

    snapshot = GitGuard(repo).snapshot_committed(
        [Path("homework_answer/week-01/gate-00.md")]
    )

    assert snapshot.branch == "learner/test/week-01"
    assert snapshot.commit_sha == git(repo, "rev-parse", "HEAD")
    assert snapshot.content_hashes == {
        "homework_answer/week-01/gate-00.md": "sha256:"
        + sha256(b"answer v1\n").hexdigest()
    }


def test_modified_answer_is_rejected_but_unrelated_dirty_file_is_ignored(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    git(repo, "switch", "-c", "learner/test/week-01")
    answer = repo / "homework_answer/week-01/gate-00.md"
    answer.parent.mkdir(parents=True)
    answer.write_text("answer v1\n", encoding="utf-8")
    git(repo, "add", "homework_answer/week-01/gate-00.md")
    git(repo, "commit", "-m", "answer attempt 1")
    (repo / "scratch.txt").write_text("unrelated\n", encoding="utf-8")
    guard = GitGuard(repo)
    before = git(repo, "status", "--porcelain")

    guard.snapshot_committed([Path("homework_answer/week-01/gate-00.md")])
    assert git(repo, "status", "--porcelain") == before

    answer.write_text("answer v2\n", encoding="utf-8")
    dirty_before = git(repo, "status", "--porcelain")
    with pytest.raises(GitEvidenceError, match="not committed"):
        guard.snapshot_committed([Path("homework_answer/week-01/gate-00.md")])
    assert git(repo, "status", "--porcelain") == dirty_before
