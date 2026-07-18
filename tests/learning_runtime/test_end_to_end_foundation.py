from pathlib import Path

from learning_runtime.cli import main
from learning_runtime.schemas import GateStatus
from learning_runtime.storage.event_ledger import EventLedger
from learning_runtime.storage.learner_state import replay_state


def test_local_session_starts_submits_and_resumes_without_guessing(
    tmp_path: Path, capsys
) -> None:
    runtime_dir = tmp_path / "learning-state"
    runtime_args = ["--runtime-dir", str(runtime_dir)]

    assert main(["start", "week-01", *runtime_args]) == 0
    assert main(["status", *runtime_args]) == 0
    assert main(["next", *runtime_args]) == 0
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
        "attempt_submitted",
        "transition_applied",
    ]
    assert state.current_gate == "week-01-gate-0"
    assert state.attempt_count == 1
    assert state.gate_status is GateStatus.EVIDENCE_PENDING
    assert "当前 Gate：week-01-gate-0" in output
    assert "不会自动判定通过或失败" in output


def test_start_refuses_to_overwrite_an_existing_session(
    tmp_path: Path, capsys
) -> None:
    runtime_dir = tmp_path / "learning-state"
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
