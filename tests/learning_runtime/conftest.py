from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]


def git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture
def student_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    repo = tmp_path / "student-repo"
    repo.mkdir()
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    for raw_path in tracked:
        if not raw_path:
            continue
        relative = Path(raw_path.decode())
        destination = repo / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)

    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Runtime Test")
    git(repo, "config", "user.email", "runtime@example.com")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "course baseline")
    monkeypatch.setattr("learning_runtime.cli.REPO_ROOT", repo)
    return repo
