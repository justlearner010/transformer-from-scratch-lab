import pytest

from learning_runtime.agent.models import AgentTurn
from learning_runtime.cli import build_parser, run_agent_loop


@pytest.mark.parametrize(
    ("arguments", "command"),
    [
        (["start", "week-01"], "start"),
        (["next"], "next"),
        (["submit", "--gate", "week-01-gate-0"], "submit"),
        (["status"], "status"),
        (["resume"], "resume"),
    ],
)
def test_cli_exposes_foundation_commands(
    arguments: list[str], command: str
) -> None:
    args = build_parser().parse_args(arguments)
    assert args.command == command


def test_submit_requires_a_gate() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["submit"])


class FakeAgentSession:
    def __init__(self):
        self.handled = []

    def open(self, phase):
        return AgentTurn(f"opened {phase}")

    def handle(self, raw):
        self.handled.append(raw)
        return AgentTurn(raw, should_exit=raw == "/quit")


def test_cli_exposes_agent_phase():
    args = build_parser().parse_args(["agent", "week-01"])
    assert args.command == "agent"
    assert args.phase == "week-01"


def test_run_agent_exits_on_quit():
    session = FakeAgentSession()
    inputs = iter(["/status", "/quit"])
    output = []
    result = run_agent_loop(
        session, "week-01", input_fn=lambda _: next(inputs),
        output_fn=output.append,
    )
    assert result == 0
    assert session.handled == ["/status", "/quit"]
