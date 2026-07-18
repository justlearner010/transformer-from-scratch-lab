from dataclasses import replace
from collections.abc import Sequence

from learning_runtime.schemas import Event, GateStatus, LearnerState


def replay_state(events: Sequence[Event]) -> LearnerState:
    if not events or events[0].event_type != "session_started":
        raise ValueError("first event must be session_started")

    first = events[0]
    state = LearnerState(
        course_id=str(first.payload["course_id"]),
        phase_id=str(first.payload["phase_id"]),
        current_gate=str(first.payload["current_gate"]),
        gate_status=GateStatus.ACTIVE,
        unresolved_p0_nodes=tuple(first.payload.get("unresolved_p0_nodes", [])),
        last_event_id=first.event_id,
    )

    for event in events[1:]:
        if event.event_type == "attempt_submitted":
            gate_id = str(event.payload.get("gate_id", ""))
            if gate_id != state.current_gate:
                raise ValueError(
                    f"attempt for {gate_id} does not match current Gate {state.current_gate}"
                )
            state = replace(
                state,
                attempt_count=state.attempt_count + 1,
                last_event_id=event.event_id,
            )
        elif event.event_type == "transition_applied":
            state = replace(
                state,
                current_gate=str(event.payload["current_gate"]),
                gate_status=GateStatus(str(event.payload["gate_status"])),
                attempt_count=int(event.payload.get("attempt_count", state.attempt_count)),
                hint_level=int(event.payload.get("hint_level", state.hint_level)),
                verified_evidence_ids=tuple(
                    event.payload.get(
                        "verified_evidence_ids", state.verified_evidence_ids
                    )
                ),
                unresolved_p0_nodes=tuple(
                    event.payload.get("unresolved_p0_nodes", state.unresolved_p0_nodes)
                ),
                unlocked_capability=event.payload.get(
                    "unlocked_capability", state.unlocked_capability
                ),
                last_event_id=event.event_id,
            )
        else:
            state = replace(state, last_event_id=event.event_id)
    return state
