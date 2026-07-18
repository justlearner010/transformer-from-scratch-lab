import pytest

from learning_runtime.cli import build_parser


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
