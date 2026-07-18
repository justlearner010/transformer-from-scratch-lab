from dataclasses import dataclass
from pathlib import Path

from learning_runtime.coordinator import Coordinator
from learning_runtime.manifest import load_manifest
from learning_runtime.schemas import (
    ActionContract,
    CourseManifest,
    GateStatus,
    LearnerState,
)
from learning_runtime.state_machine import LearningStateMachine
from learning_runtime.storage.event_ledger import EventLedger
from learning_runtime.storage.learner_state import replay_state
from learning_runtime.workspace.answer_workspace import AnswerWorkspace
from learning_runtime.workspace.git_guard import GitGuard


@dataclass(frozen=True)
class SubmissionReceipt:
    state: LearnerState
    evidence_id: str
    branch: str
    commit_sha: str


class LearningRuntime:
    """Structured application service shared by CLI and future Agents."""

    def __init__(self, repo_root: Path, runtime_dir: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.ledger = EventLedger(runtime_dir / "events.jsonl")

    def start_session(self, phase: str) -> ActionContract:
        manifest = self._manifest(phase)
        if self.ledger.path.exists():
            raise ValueError(
                f"学习 session 已经存在：{self.ledger.path}；请使用 resume。"
            )
        branch = GitGuard(self.repo_root).assert_student_branch(
            manifest.learner_workspace.protected_branches
        )
        first_gate = manifest.gates[0]
        answer = AnswerWorkspace(self.repo_root, manifest).initialize(first_gate)
        self.ledger.append(
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
        return Coordinator(manifest).next_action(self.get_state())

    def next_action(self) -> ActionContract:
        state = self.get_state()
        return Coordinator(self._manifest(state.phase_id)).next_action(state)

    def submit_answer(self, gate_id: str) -> SubmissionReceipt:
        state = self.get_state()
        manifest = self._manifest(state.phase_id)
        if gate_id != state.current_gate:
            raise ValueError(
                f"提交 Gate {gate_id} 与当前 Gate {state.current_gate} 不一致。"
            )
        if state.gate_status is not GateStatus.ACTIVE:
            raise ValueError(
                f"当前状态 {state.gate_status.value} 不允许再次提交。"
            )

        gate = manifest.gate(gate_id)
        guard = GitGuard(self.repo_root)
        guard.assert_student_branch(manifest.learner_workspace.protected_branches)
        inspection = AnswerWorkspace(self.repo_root, manifest).inspect(gate)
        snapshot = guard.snapshot_committed(
            [inspection.artifact_path, *inspection.attachment_paths]
        )
        observed_count = sum(
            event.event_type == "artifact_observed"
            for event in self.ledger.read()
        )
        evidence_id = f"evidence-{observed_count + 1:04d}"
        artifact_key = inspection.artifact_path.as_posix()
        evidence_refs = (evidence_id,)
        self.ledger.append(
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
                    "attachments": [
                        {
                            "path": path.as_posix(),
                            "content_hash": snapshot.content_hashes[path.as_posix()],
                        }
                        for path in inspection.attachment_paths
                    ],
                },
            },
            evidence_refs,
        )
        self.ledger.append(
            "attempt_submitted",
            {"gate_id": gate_id, "evidence_id": evidence_id},
            evidence_refs,
        )
        transition = LearningStateMachine(manifest).transition(
            self.get_state(),
            GateStatus.EVIDENCE_PENDING,
        )
        self.ledger.append(
            transition.event_type,
            dict(transition.payload),
            evidence_refs,
        )
        return SubmissionReceipt(
            state=self.get_state(),
            evidence_id=evidence_id,
            branch=snapshot.branch,
            commit_sha=snapshot.commit_sha,
        )

    def get_state(self) -> LearnerState:
        events = self.ledger.read()
        if not events:
            raise ValueError("没有可恢复的学习 session；请先运行 start week-01。")
        return replay_state(events)

    def _manifest(self, phase: str) -> CourseManifest:
        if phase != "week-01":
            raise ValueError(f"当前 MVP 只支持 week-01，收到：{phase}")
        return load_manifest(
            self.repo_root / "course-manifests/week-01.yaml",
            self.repo_root,
        )
