import argparse
from collections.abc import Sequence
from pathlib import Path


DEFAULT_RUNTIME_DIR = Path(".learning-os")


def _add_runtime_dir(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=DEFAULT_RUNTIME_DIR,
        help=argparse.SUPPRESS,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="learning-os")
    commands = parser.add_subparsers(dest="command", required=True)

    start = commands.add_parser("start", help="开始一个学习阶段")
    start.add_argument("phase")
    _add_runtime_dir(start)

    next_command = commands.add_parser("next", help="查看唯一下一步")
    _add_runtime_dir(next_command)

    submit = commands.add_parser("submit", help="提交当前 Gate 的一次尝试")
    submit.add_argument("--gate", required=True)
    _add_runtime_dir(submit)

    status = commands.add_parser("status", help="查看当前状态")
    _add_runtime_dir(status)

    resume = commands.add_parser("resume", help="从事件账本恢复状态")
    _add_runtime_dir(resume)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    build_parser().parse_args(argv)
    return 0
