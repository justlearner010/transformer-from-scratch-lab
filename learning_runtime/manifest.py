from pathlib import Path
from typing import Any

import yaml

from learning_runtime.schemas import (
    CourseManifest,
    EvidenceRequirement,
    GateDefinition,
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
    knowledge_nodes = tuple(_require_mapping(row, "knowledge_node") for row in node_rows)
    node_ids = {str(node.get("node_id")) for node in knowledge_nodes}
    if "None" in node_ids or len(node_ids) != len(knowledge_nodes):
        raise ManifestError("knowledge node IDs must be present and unique")

    gate_rows = _require_list(root["gates"], "gates")
    gates: list[GateDefinition] = []
    seen_gate_ids: set[str] = set()
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
            )
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
        knowledge_nodes=knowledge_nodes,
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
    )
