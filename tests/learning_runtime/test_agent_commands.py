import pytest

from learning_runtime.agent.commands import parse_agent_input
from learning_runtime.agent.models import AgentCommand, InputKind


@pytest.mark.parametrize(
    ("raw", "kind", "command"),
    [
        ("/submit", InputKind.COMMAND, AgentCommand.SUBMIT),
        (" /status ", InputKind.COMMAND, AgentCommand.STATUS),
        ("/retry", InputKind.COMMAND, AgentCommand.RETRY),
        ("我完成了", InputKind.MESSAGE, None),
        ("请帮我 /submit", InputKind.MESSAGE, None),
        ("/unknown", InputKind.UNKNOWN_COMMAND, None),
        ("", InputKind.EMPTY, None),
    ],
)
def test_parse_agent_input_never_infers_actions(raw, kind, command):
    parsed = parse_agent_input(raw)
    assert parsed.kind is kind
    assert parsed.command is command


def test_revise_is_an_explicit_agent_command() -> None:
    parsed = parse_agent_input("/revise")

    assert parsed.kind is InputKind.COMMAND
    assert parsed.command is not None
    assert parsed.command.value == "revise"
