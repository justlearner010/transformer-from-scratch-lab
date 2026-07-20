import pytest
from pathlib import Path

from learning_runtime.agent.models import AgentTurn
from learning_runtime.cli import build_parser, run_agent_loop
from learning_runtime.env import load_project_env


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


def test_project_env_loads_missing_provider_settings_without_overwriting_shell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".env").write_text(
        "SILICONFLOW_API_KEY=local-test-key\nSILICONFLOW_MODEL=local-model\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("SILICONFLOW_MODEL", "shell-model")
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)

    load_project_env(tmp_path)

    assert __import__("os").environ["SILICONFLOW_API_KEY"] == "local-test-key"
    assert __import__("os").environ["SILICONFLOW_MODEL"] == "shell-model"
