import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

from learning_runtime.manifest import ManifestError
from learning_runtime.runtime import LearningRuntime, SubmissionReceipt
from learning_runtime.schemas import ActionContract, LearnerState
from learning_runtime.storage.event_ledger import LedgerCorruptionError


DEFAULT_RUNTIME_DIR = Path(".learning-os")
REPO_ROOT = Path(__file__).resolve().parents[1]


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


def _render_action(action: ActionContract) -> None:
    checks = "；".join(action.checks)
    evidence = "、".join(action.evidence_index) or "无"
    print(f"当前能力：{action.current_capability}")
    print(f"当前 Gate：{action.current_gate}")
    print(f"为什么是这一步：{action.reason}")
    print(f"你现在需要完成的一个动作：{action.action}")
    print(f"作答文件：{action.answer_path}")
    print(f"提交后会检查什么：{checks}")
    print(f"允许的提示等级：L{action.hint_level}")
    print(f"证据索引：{evidence}")


def _render_state(state: LearnerState) -> None:
    print(f"当前 Gate：{state.current_gate}")
    print(f"Gate 状态：{state.gate_status.value}")
    print(f"尝试次数：{state.attempt_count}")
    print(f"提示等级：L{state.hint_level}")
    print(f"最后事件：{state.last_event_id}")


def _render_submission(receipt: SubmissionReceipt) -> None:
    print(
        f"已记录 {receipt.state.current_gate} 的一次独立尝试："
        f"{receipt.evidence_id}。"
    )
    print(f"证据来源：{receipt.branch}@{receipt.commit_sha[:12]}")
    print("当前没有 Verifier，因此不会自动判定通过或失败。")
    _render_state(receipt.state)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runtime = LearningRuntime(REPO_ROOT, args.runtime_dir)
    try:
        if args.command == "start":
            _render_action(runtime.start_session(args.phase))
            return 0
        if args.command == "next":
            _render_action(runtime.next_action())
            return 0
        if args.command == "submit":
            _render_submission(runtime.submit_answer(args.gate))
            return 0
        if args.command == "status":
            _render_state(runtime.get_state())
            return 0
        if args.command == "resume":
            print("已从事件账本恢复学习状态。")
            _render_state(runtime.get_state())
            return 0
    except (ManifestError, LedgerCorruptionError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled command: {args.command}")
