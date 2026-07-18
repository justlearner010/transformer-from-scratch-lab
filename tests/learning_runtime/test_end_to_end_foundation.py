from pathlib import Path
import re
import subprocess

from learning_runtime.cli import main
from learning_runtime.runtime import LearningRuntime
from learning_runtime.schemas import GateStatus
from learning_runtime.storage.event_ledger import EventLedger
from learning_runtime.storage.learner_state import replay_state


def git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def fill_gate_zero(repo: Path) -> tuple[Path, Path]:
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
    return answer, attachment


def test_start_allows_a_student_to_work_on_main_without_creating_a_branch(
    student_repo: Path, capsys
) -> None:
    runtime_dir = student_repo / ".learning-os"

    assert main(["start", "week-01", "--runtime-dir", str(runtime_dir)]) == 0

    assert (runtime_dir / "events.jsonl").exists()
    assert (student_repo / "homework_answer/week-01/gate-00.md").exists()
    assert (student_repo / "homework_answer/week-01/gate-06.md").exists()
    assert "当前 Gate：week-01-gate-0" in capsys.readouterr().out


def test_committed_student_answer_becomes_observed_evidence(
    student_repo: Path, capsys
) -> None:
    runtime_dir = student_repo / ".learning-os"
    runtime_args = ["--runtime-dir", str(runtime_dir)]

    assert main(["start", "week-01", *runtime_args]) == 0
    answer = student_repo / "homework_answer/week-01/gate-00.md"
    assert answer.exists()
    assert (student_repo / "homework_answer/week-01/gate-01.md").exists()
    assert main(["status", *runtime_args]) == 0
    assert main(["next", *runtime_args]) == 0

    # The untouched template is not an answer and must not create an attempt.
    assert main(["submit", "--gate", "week-01-gate-0", *runtime_args]) == 2
    assert [
        event.event_type
        for event in EventLedger(runtime_dir / "events.jsonl").read()
    ] == ["session_started"]

    answer, attachment = fill_gate_zero(student_repo)
    # A complete but uncommitted answer is still not provenance.
    assert main(["submit", "--gate", "week-01-gate-0", *runtime_args]) == 2
    assert [
        event.event_type
        for event in EventLedger(runtime_dir / "events.jsonl").read()
    ] == ["session_started"]

    git(student_repo, "add", str(answer.relative_to(student_repo)))
    git(student_repo, "add", str(attachment.relative_to(student_repo)))
    git(student_repo, "commit", "-m", "answer gate 0")
    assert (
        main(
            [
                "submit",
                "--gate",
                "week-01-gate-0",
                *runtime_args,
            ]
        )
        == 0
    )
    assert main(["resume", *runtime_args]) == 0

    events_path = runtime_dir / "events.jsonl"
    events = EventLedger(events_path).read()
    state = replay_state(events)
    output = capsys.readouterr().out

    assert events_path.exists()
    assert [item.event_type for item in events] == [
        "session_started",
        "artifact_observed",
        "attempt_submitted",
        "transition_applied",
    ]
    observed = events[1]
    assert observed.payload["evidence_id"] == "evidence-0001"
    assert observed.payload["observation"]["branch"] == "main"
    assert observed.payload["observation"]["commit_sha"] == git(
        student_repo, "rev-parse", "HEAD"
    )
    assert observed.payload["observation"]["content_hash"].startswith("sha256:")
    assert observed.payload["observation"]["attachments"] == [
        {
            "path": "homework_answer/week-01/attachments/gate-00/shape.jpg",
            "content_hash": observed.payload["observation"]["attachments"][0][
                "content_hash"
            ],
        }
    ]
    assert observed.evidence_refs == ("evidence-0001",)
    assert events[2].evidence_refs == ("evidence-0001",)
    assert events[3].evidence_refs == ("evidence-0001",)
    assert state.current_gate == "week-01-gate-0"
    assert state.attempt_count == 1
    assert state.gate_status is GateStatus.EVIDENCE_PENDING
    assert "当前 Gate：week-01-gate-0" in output
    assert "作答文件：homework_answer/week-01/gate-00.md" in output
    assert (
        "已记录 week-01-gate-0 的一次独立尝试：evidence-0001"
        in output
    )
    assert "证据来源：main@" in output
    assert "不会自动判定通过或失败" in output


def test_start_refuses_to_overwrite_an_existing_session(
    student_repo: Path, capsys
) -> None:
    runtime_dir = student_repo / ".learning-os"
    arguments = [
        "start",
        "week-01",
        "--runtime-dir",
        str(runtime_dir),
    ]

    assert main(arguments) == 0
    assert main(arguments) == 2

    assert len(EventLedger(runtime_dir / "events.jsonl").read()) == 1
    assert "已经存在" in capsys.readouterr().err


def test_open_session_backfills_missing_gate_templates(
    student_repo: Path,
) -> None:
    runtime_dir = student_repo / ".learning-os"
    runtime = LearningRuntime(student_repo, runtime_dir)
    runtime.start_session("week-01")
    missing = student_repo / "homework_answer/week-01/gate-06.md"
    missing.unlink()

    runtime.open_session("week-01")

    assert missing.is_file()
