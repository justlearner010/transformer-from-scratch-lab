from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Iterable

from learning_runtime.schemas import Event


class LedgerCorruptionError(RuntimeError):
    def __init__(self, line_number: int, reason: str) -> None:
        self.line_number = line_number
        super().__init__(f"event ledger is corrupt at line {line_number}: {reason}")


class EventLedger:
    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> list[Event]:
        if not self.path.exists():
            return []

        events: list[Event] = []
        with self.path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                try:
                    raw = json.loads(line)
                    events.append(
                        Event(
                            event_id=str(raw["event_id"]),
                            event_type=str(raw["event_type"]),
                            occurred_at=str(raw["occurred_at"]),
                            payload=dict(raw["payload"]),
                            evidence_refs=tuple(raw.get("evidence_refs", [])),
                        )
                    )
                except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                    raise LedgerCorruptionError(line_number, str(error)) from error
        return events

    def append(
        self,
        event_type: str,
        payload: dict[str, Any],
        evidence_refs: Iterable[str] = (),
        *,
        occurred_at: str | None = None,
    ) -> Event:
        existing = self.read()
        event = Event(
            event_id=f"event-{len(existing) + 1:04d}",
            event_type=event_type,
            occurred_at=occurred_at or datetime.now(timezone.utc).isoformat(),
            payload=dict(payload),
            evidence_refs=tuple(evidence_refs),
        )
        raw = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "occurred_at": event.occurred_at,
            "payload": event.payload,
            "evidence_refs": list(event.evidence_refs),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(raw, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return event
