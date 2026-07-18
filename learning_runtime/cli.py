import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

from learning_runtime.coordinator import Coordinator
from learning_runtime.manifest import ManifestError, load_manifest
from learning_runtime.schemas import ActionContract, GateStatus, LearnerState
from learning_runtime.state_machine import LearningStateMachine
from learning_runtime.storage.event_ledger import (
    EventLedger,
    LedgerCorruptionError,
)
from learning_runtime.storage.learner_state import replay_state
from learning_runtime.workspace.answer_workspace import AnswerWorkspace
from learning_runtime.workspace.git_guard import GitGuard


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


def _manifest_for_phase(phase: str):
    if phase != "week-01":
        raise ValueError(f"当前 MVP 只支持 week-01，收到：{phase}")
    return load_manifest(REPO_ROOT / "course-manifests/week-01.yaml", REPO_ROOT)


def _load_state(runtime_dir: Path) -> tuple[EventLedger, LearnerState]:
    ledger = EventLedger(runtime_dir / "events.jsonl")
    events = ledger.read()
    if not events:
        raise ValueError("没有可恢复的学习 session；请先运行 start week-01。")
    return ledger, replay_state(events)


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


def _start(phase: str, runtime_dir: Path) -> int:
    manifest = _manifest_for_phase(phase)
    ledger = EventLedger(runtime_dir / "events.jsonl")
    if ledger.path.exists():
        print(
            f"学习 session 已经存在：{ledger.path}；请使用 resume。",
            file=sys.stderr,
        )
        return 2
    branch = GitGuard(REPO_ROOT).assert_student_branch(
        manifest.learner_workspace.protected_branches
    )
    first_gate = manifest.gates[0]
    answer = AnswerWorkspace(REPO_ROOT, manifest).initialize(first_gate)
    ledger.append(
        "session_started",
        {
            "course_id": manifest.course_id,
            "phase_id": manifest.phase_id,
            "current_gate": first_gate.gate_id,
            "unresolved_p0_nodes": list(first_gate.knowledge_node_ids),
            "manifest_path": "course-manifests/week-01.yaml",
            "student_branch": branch,
            "answer_path": answer.artifact_path.as_posix(),
        },
    )
    state = replay_state(ledger.read())
    _render_action(Coordinator(manifest).next_action(state))
    return 0


def _status(runtime_dir: Path, *, resumed: bool = False) -> int:
    _, state = _load_state(runtime_dir)
    if resumed:
        print("已从事件账本恢复学习状态。")
    _render_state(state)
    return 0


def _next(runtime_dir: Path) -> int:
    _, state = _load_state(runtime_dir)
    manifest = _manifest_for_phase(state.phase_id)
    _render_action(Coordinator(manifest).next_action(state))
    return 0


def _submit(runtime_dir: Path, gate_id: str) -> int:
    ledger, state = _load_state(runtime_dir)
    manifest = _manifest_for_phase(state.phase_id)
    if gate_id != state.current_gate:
        raise ValueError(
            f"提交 Gate {gate_id} 与当前 Gate {state.current_gate} 不一致。"
        )
    if state.gate_status is not GateStatus.ACTIVE:
        raise ValueError(
            f"当前状态 {state.gate_status.value} 不允许再次提交。"
        )

    gate = manifest.gate(gate_id)
    guard = GitGuard(REPO_ROOT)
    guard.assert_student_branch(manifest.learner_workspace.protected_branches)
    inspection = AnswerWorkspace(REPO_ROOT, manifest).inspect(gate)
    evidence_paths = [
        inspection.artifact_path,
        *inspection.attachment_paths,
    ]
    snapshot = guard.snapshot_committed(evidence_paths)
    existing_events = ledger.read()
    observed_count = sum(
        event.event_type == "artifact_observed" for event in existing_events
    )
    evidence_id = f"evidence-{observed_count + 1:04d}"
    artifact_key = inspection.artifact_path.as_posix()
    attachments = [
        {
            "path": path.as_posix(),
            "content_hash": snapshot.content_hashes[path.as_posix()],
        }
        for path in inspection.attachment_paths
    ]
    evidence_refs = (evidence_id,)
    ledger.append(
        "artifact_observed",
        {
            "evidence_id": evidence_id,
            "type": "committed-answer",
            "source": artifact_key,
            "observation": {
                "gate_id": gate_id,
                "branch": snapshot.branch,
                "commit_sha": snapshot.commit_sha,
                "content_hash": snapshot.content_hashes[artifact_key],
                "attachments": attachments,
            },
        },
        evidence_refs,
    )
    ledger.append(
        "attempt_submitted",
        {"gate_id": gate_id, "evidence_id": evidence_id},
        evidence_refs,
    )
    state_after_attempt = replay_state(ledger.read())
    transition = LearningStateMachine(manifest).transition(
        state_after_attempt, GateStatus.EVIDENCE_PENDING
    )
    ledger.append(
        transition.event_type,
        dict(transition.payload),
        evidence_refs,
    )
    print(f"已记录 {gate_id} 的一次独立尝试：{evidence_id}。")
    print(f"证据来源：{snapshot.branch}@{snapshot.commit_sha[:12]}")
    print("当前没有 Verifier，因此不会自动判定通过或失败。")
    _render_state(replay_state(ledger.read()))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "start":
            return _start(args.phase, args.runtime_dir)
        if args.command == "next":
            return _next(args.runtime_dir)
        if args.command == "submit":
            return _submit(args.runtime_dir, args.gate)
        if args.command == "status":
            return _status(args.runtime_dir)
        if args.command == "resume":
            return _status(args.runtime_dir, resumed=True)
    except (ManifestError, LedgerCorruptionError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled command: {args.command}")
