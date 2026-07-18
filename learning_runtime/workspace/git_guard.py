from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import subprocess
from typing import Mapping, Sequence


class GitEvidenceError(ValueError):
    """Raised when an artifact cannot be tied to the current commit."""


@dataclass(frozen=True)
class GitSnapshot:
    branch: str
    commit_sha: str
    content_hashes: Mapping[str, str]


class GitGuard:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()

    def assert_student_branch(self, protected_branches: tuple[str, ...]) -> str:
        branch = self._text("branch", "--show-current")
        if not branch:
            raise GitEvidenceError("detached HEAD cannot own student answers")
        if branch in protected_branches:
            raise GitEvidenceError(
                f"protected branch {branch!r} cannot own student answers"
            )
        return branch

    def snapshot_committed(self, paths: Sequence[Path]) -> GitSnapshot:
        if not paths:
            raise GitEvidenceError("at least one evidence path is required")
        relative_paths = tuple(self._relative(path) for path in paths)
        for relative_path in relative_paths:
            tracked = subprocess.run(
                ["git", "ls-files", "--error-unmatch", "--", relative_path],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
            )
            if tracked.returncode != 0:
                raise GitEvidenceError(f"evidence is not tracked: {relative_path}")

        status = self._text("status", "--porcelain", "--", *relative_paths)
        if status:
            changed = ", ".join(
                line[3:] if len(line) > 3 else line for line in status.splitlines()
            )
            raise GitEvidenceError(f"evidence is not committed: {changed}")

        commit_sha = self._text("rev-parse", "HEAD")
        branch = self._text("branch", "--show-current")
        hashes: dict[str, str] = {}
        for relative_path in relative_paths:
            committed_bytes = self._bytes("show", f"HEAD:{relative_path}")
            hashes[relative_path] = "sha256:" + sha256(committed_bytes).hexdigest()
        return GitSnapshot(branch, commit_sha, hashes)

    def read_committed(self, commit_sha: str, path: Path) -> bytes:
        if re.fullmatch(r"[0-9a-f]{40}", commit_sha) is None:
            raise GitEvidenceError("invalid committed evidence SHA")
        relative_path = self._relative(path)
        return self._bytes("show", f"{commit_sha}:{relative_path}")

    def _relative(self, path: Path) -> str:
        candidate = (self.repo_root / path).resolve()
        if not candidate.is_relative_to(self.repo_root):
            raise GitEvidenceError(f"evidence path escapes repository: {path}")
        return candidate.relative_to(self.repo_root).as_posix()

    def _text(self, *arguments: str) -> str:
        return subprocess.run(
            ["git", *arguments],
            cwd=self.repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _bytes(self, *arguments: str) -> bytes:
        return subprocess.run(
            ["git", *arguments],
            cwd=self.repo_root,
            check=True,
            capture_output=True,
        ).stdout
