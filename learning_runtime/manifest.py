from pathlib import Path
from typing import Any

import yaml

from learning_runtime.schemas import (
    CourseManifest,
    EvidenceRequirement,
    GateDefinition,
    KnowledgeNode,
    LearnerWorkspace,
    SubmissionDefinition,
)


class ManifestError(ValueError):
    """Raised when a course manifest cannot be trusted by the Runtime."""


REQUIRED_FIELDS = {
    "course_id",
    "phase_id",
    "capability_question",
    "knowledge_nodes",
    "gates",
    "dependencies",
    "artifact_refs",
    "evidence_requirements",
    "allowed_hint_levels",
    "failure_routes",
    "completion_rule",
    "next_capability",
    "learner_workspace",
}


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError(f"{name} must be a mapping")
    return value


def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ManifestError(f"{name} must be a list")
    return value


def _validate_path(repo_root: Path, relative_path: str) -> None:
    candidate = (repo_root / relative_path).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError as error:
        raise ManifestError(f"path escapes repository: {relative_path}") from error
    if not candidate.exists():
        raise ManifestError(f"artifact path does not exist: {relative_path}")


def _validate_output_path(answer_root: str, relative_path: str) -> None:
    root = Path(answer_root)
    candidate = Path(relative_path)
    if candidate.is_absolute() or not candidate.is_relative_to(root):
        raise ManifestError(
            f"answer artifact must stay under {answer_root}: {relative_path}"
        )


def _validate_dependencies(
    gate_ids: set[str], dependencies: dict[str, tuple[str, ...]]
) -> None:
    for gate_id, prerequisites in dependencies.items():
        if gate_id not in gate_ids:
            raise ManifestError(f"unknown dependency owner: {gate_id}")
        for prerequisite in prerequisites:
            if prerequisite not in gate_ids:
                raise ManifestError(f"unknown dependency target: {prerequisite}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(gate_id: str) -> None:
        if gate_id in visiting:
            raise ManifestError(f"dependency cycle includes {gate_id}")
        if gate_id in visited:
            return
        visiting.add(gate_id)
        for prerequisite in dependencies.get(gate_id, ()):
            visit(prerequisite)
        visiting.remove(gate_id)
        visited.add(gate_id)

    for gate_id in gate_ids:
        visit(gate_id)


def load_manifest(path: Path, repo_root: Path) -> CourseManifest:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ManifestError(f"cannot load manifest {path}: {error}") from error

    root = _require_mapping(raw, "manifest")
    missing = sorted(REQUIRED_FIELDS - root.keys())
    if missing:
        raise ManifestError(f"missing manifest fields: {', '.join(missing)}")

    workspace_raw = _require_mapping(root["learner_workspace"], "learner_workspace")
    answer_root = str(workspace_raw.get("answer_root", ""))
    template_ref = str(workspace_raw.get("template_ref", ""))
    _validate_path(repo_root, template_ref)
    learner_workspace = LearnerWorkspace(
        answer_root=answer_root,
        template_ref=template_ref,
        commit_required=bool(workspace_raw.get("commit_required", False)),
    )

    artifact_refs_raw = _require_mapping(root["artifact_refs"], "artifact_refs")
    artifact_refs: dict[str, str] = {}
    for name, relative_path in artifact_refs_raw.items():
        if not isinstance(name, str) or not isinstance(relative_path, str):
            raise ManifestError("artifact_refs must map strings to strings")
        _validate_path(repo_root, relative_path)
        artifact_refs[name] = relative_path

    failure_routes_raw = _require_mapping(root["failure_routes"], "failure_routes")
    failure_routes: dict[str, str] = {}
    for name, relative_path in failure_routes_raw.items():
        if not isinstance(name, str) or not isinstance(relative_path, str):
            raise ManifestError("failure_routes must map strings to strings")
        _validate_path(repo_root, relative_path)
        failure_routes[name] = relative_path

    node_rows = _require_list(root["knowledge_nodes"], "knowledge_nodes")
    knowledge_nodes: list[KnowledgeNode] = []
    allowed_types = {
        "fact", "concept", "mechanism", "procedure", "contract", "diagnosis",
        "integration", "operation",
    }
    for row_value in node_rows:
        row = _require_mapping(row_value, "knowledge_node")
        required = {
            "node_id", "primary_type", "importance", "importance_reason",
            "dependency_role", "target_depth",
        }
        missing_node_fields = sorted(required - row.keys())
        if missing_node_fields:
            raise ManifestError(
                "knowledge_node missing fields: " + ", ".join(missing_node_fields)
            )
        primary_type = str(row["primary_type"])
        if primary_type not in allowed_types:
            raise ManifestError(f"unsupported knowledge node type: {primary_type}")
        importance = str(row["importance"])
        dependency_role = str(row["dependency_role"])
        target_depth = str(row["target_depth"])
        if importance not in {"P0", "P1", "P2", "P3"}:
            raise ManifestError(f"unsupported knowledge node importance: {importance}")
        if dependency_role not in {"hard", "soft", "corequisite", "downstream", "integration"}:
            raise ManifestError(f"unsupported dependency role: {dependency_role}")
        if target_depth not in {"D0", "D1", "D2", "D3", "D4", "D5"}:
            raise ManifestError(f"unsupported target depth: {target_depth}")
        knowledge_nodes.append(KnowledgeNode(
            node_id=str(row["node_id"]),
            primary_type=primary_type,
            secondary_type=(str(row["secondary_type"]) if row.get("secondary_type") else None),
            importance=importance,
            importance_reason=str(row["importance_reason"]),
            dependency_role=dependency_role,
            target_depth=target_depth,
        ))
    node_ids = {node.node_id for node in knowledge_nodes}
    if not node_ids or len(node_ids) != len(knowledge_nodes) or "" in node_ids:
        raise ManifestError("knowledge node IDs must be present and unique")

    gate_rows = _require_list(root["gates"], "gates")
    gates: list[GateDefinition] = []
    seen_gate_ids: set[str] = set()
    seen_artifact_paths: set[str] = set()
    for row_value in gate_rows:
        row = _require_mapping(row_value, "gate")
        gate_id = str(row.get("gate_id", ""))
        if not gate_id or gate_id in seen_gate_ids:
            raise ManifestError(f"duplicate or missing gate ID: {gate_id}")
        seen_gate_ids.add(gate_id)

        gate_node_ids = tuple(str(item) for item in _require_list(
            row.get("knowledge_node_ids"), f"{gate_id}.knowledge_node_ids"
        ))
        unknown_nodes = sorted(set(gate_node_ids) - node_ids)
        if unknown_nodes:
            raise ManifestError(
                f"{gate_id} references unknown nodes: {', '.join(unknown_nodes)}"
            )

        requirements: list[EvidenceRequirement] = []
        for requirement_value in _require_list(
            row.get("required_evidence"), f"{gate_id}.required_evidence"
        ):
            requirement = _require_mapping(requirement_value, "evidence requirement")
            artifact_ref = str(requirement.get("artifact_ref", ""))
            _validate_path(repo_root, artifact_ref)
            requirements.append(
                EvidenceRequirement(
                    criterion_id=str(requirement.get("criterion_id", "")),
                    evidence_type=str(requirement.get("type", "")),
                    artifact_ref=artifact_ref,
                    priority=str(requirement.get("priority", "")),
                    independent=bool(requirement.get("independent", False)),
                )
            )

        submission_raw = _require_mapping(
            row.get("submission"), f"{gate_id}.submission"
        )
        artifact_path = str(submission_raw.get("artifact_path", ""))
        _validate_output_path(answer_root, artifact_path)
        if artifact_path in seen_artifact_paths:
            raise ManifestError(f"duplicate answer artifact path: {artifact_path}")
        seen_artifact_paths.add(artifact_path)
        attachment_policy = str(submission_raw.get("attachment_policy", ""))
        if attachment_policy not in {"optional", "at-least-one"}:
            raise ManifestError(f"unsupported attachment policy: {attachment_policy}")
        submission = SubmissionDefinition(
            artifact_path=artifact_path,
            required_sections=tuple(
                str(item)
                for item in _require_list(
                    submission_raw.get("required_sections"),
                    f"{gate_id}.submission.required_sections",
                )
            ),
            attachment_policy=attachment_policy,
        )
        if not submission.required_sections:
            raise ManifestError(f"{gate_id} requires at least one answer section")

        gates.append(
            GateDefinition(
                gate_id=gate_id,
                knowledge_node_ids=gate_node_ids,
                task_layer=str(row.get("task_layer", "")),
                required_evidence=tuple(requirements),
                verifier=str(row.get("verifier", "")),
                pass_rule=str(row.get("pass_rule", "")),
                rollback_target=str(row.get("rollback_target", "")),
                escalation_conditions=tuple(
                    str(item)
                    for item in _require_list(
                        row.get("escalation_conditions"),
                        f"{gate_id}.escalation_conditions",
                    )
                ),
                action=str(row.get("action", "")),
                checks=tuple(
                    str(item)
                    for item in _require_list(row.get("checks"), f"{gate_id}.checks")
                ),
                submission=submission,
                rubric_ref=(
                    str(row["rubric_ref"]) if row.get("rubric_ref") else None
                ),
                rubric_version=(
                    int(row["rubric_version"])
                    if row.get("rubric_version") is not None
                    else None
                ),
            )
        )

        if gates[-1].rubric_ref:
            _validate_path(repo_root, gates[-1].rubric_ref)
        if bool(gates[-1].rubric_ref) != (gates[-1].rubric_version is not None):
            raise ManifestError(
                f"{gate_id} must define rubric_ref and rubric_version together"
            )

    gate_ids = {gate.gate_id for gate in gates}
    for gate in gates:
        if gate.rollback_target not in gate_ids and gate.rollback_target not in failure_routes:
            raise ManifestError(
                f"unknown rollback target for {gate.gate_id}: {gate.rollback_target}"
            )

    dependencies_raw = _require_mapping(root["dependencies"], "dependencies")
    dependencies = {
        str(gate_id): tuple(str(item) for item in _require_list(items, str(gate_id)))
        for gate_id, items in dependencies_raw.items()
    }
    _validate_dependencies(gate_ids, dependencies)

    return CourseManifest(
        course_id=str(root["course_id"]),
        phase_id=str(root["phase_id"]),
        capability_question=str(root["capability_question"]),
        knowledge_nodes=tuple(knowledge_nodes),
        gates=tuple(gates),
        dependencies=dependencies,
        artifact_refs=artifact_refs,
        evidence_requirements=tuple(
            str(item)
            for item in _require_list(root["evidence_requirements"], "evidence_requirements")
        ),
        allowed_hint_levels=tuple(
            int(item)
            for item in _require_list(root["allowed_hint_levels"], "allowed_hint_levels")
        ),
        failure_routes=failure_routes,
        completion_rule=str(root["completion_rule"]),
        next_capability=str(root["next_capability"]),
        learner_workspace=learner_workspace,
    )
