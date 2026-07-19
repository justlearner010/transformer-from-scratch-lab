from learning_runtime.schemas import Event, GateStatus
from learning_runtime.storage.learner_state import replay_state


def event(
    event_id: str,
    event_type: str,
    payload: dict[str, object],
    evidence_refs: tuple[str, ...] = (),
) -> Event:
    return Event(
        event_id=event_id,
        event_type=event_type,
        occurred_at="2026-07-18T10:00:00+08:00",
        payload=payload,
        evidence_refs=evidence_refs,
    )


def test_replay_requires_session_started_first() -> None:
    try:
        replay_state([event("event-0001", "attempt_submitted", {})])
    except ValueError as error:
        assert "session_started" in str(error)
    else:
        raise AssertionError("replay should reject a stream without session_started")


def test_replay_restores_attempt_and_transition_state() -> None:
    events = [
        event(
            "event-0001",
            "session_started",
            {
                "course_id": "transformer-from-scratch",
                "phase_id": "week-01",
                "current_gate": "week-01-gate-0",
                "unresolved_p0_nodes": ["matrix-shape"],
            },
        ),
        event(
            "event-0002",
            "attempt_submitted",
            {"gate_id": "week-01-gate-0"},
            ("evidence-0001",),
        ),
        event(
            "event-0003",
            "transition_applied",
            {
                "current_gate": "week-01-gate-1",
                "gate_status": "active",
                "attempt_count": 0,
                "hint_level": 0,
                "verified_evidence_ids": ["evidence-0001"],
                "unresolved_p0_nodes": ["qkv-score-semantics"],
            },
            ("evidence-0001",),
        ),
    ]

    state = replay_state(events)

    assert state.current_gate == "week-01-gate-1"
    assert state.gate_status is GateStatus.ACTIVE
    assert state.attempt_count == 0
    assert state.verified_evidence_ids == ("evidence-0001",)
    assert state.last_event_id == "event-0003"


def test_attempt_submission_never_changes_gate_status_without_state_machine() -> None:
    state = replay_state(
        [
            event(
                "event-0001",
                "session_started",
                {
                    "course_id": "transformer-from-scratch",
                    "phase_id": "week-01",
                    "current_gate": "week-01-gate-0",
                    "unresolved_p0_nodes": ["matrix-shape"],
                },
            ),
            event(
                "event-0002",
                "attempt_submitted",
                {"gate_id": "week-01-gate-0"},
            ),
        ]
    )

    assert state.attempt_count == 1
    assert state.gate_status is GateStatus.ACTIVE
