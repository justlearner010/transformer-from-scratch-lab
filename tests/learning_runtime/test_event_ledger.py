from pathlib import Path

import pytest

from learning_runtime.storage.event_ledger import (
    EventLedger,
    LedgerCorruptionError,
)


def test_empty_ledger_has_no_events(tmp_path: Path) -> None:
    assert EventLedger(tmp_path / "events.jsonl").read() == []


def test_append_assigns_sequential_ids_without_rewriting_history(
    tmp_path: Path,
) -> None:
    path = tmp_path / "events.jsonl"
    ledger = EventLedger(path)

    first = ledger.append(
        "assignment", {"gate_id": "week-01-gate-0"}, ["evidence-0001"]
    )
    first_line = path.read_text(encoding="utf-8").splitlines()[0]
    second = ledger.append("attempt", {"gate_id": "week-01-gate-0"})

    assert first.event_id == "event-0001"
    assert second.event_id == "event-0002"
    assert first.evidence_refs == ("evidence-0001",)
    assert path.read_text(encoding="utf-8").splitlines()[0] == first_line
    assert ledger.read() == [first, second]


def test_malformed_final_line_stops_replay(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    ledger = EventLedger(path)
    ledger.append("assignment", {"gate_id": "week-01-gate-0"})
    with path.open("a", encoding="utf-8") as stream:
        stream.write('{"event_id":')

    with pytest.raises(LedgerCorruptionError) as error:
        ledger.read()

    assert error.value.line_number == 2
