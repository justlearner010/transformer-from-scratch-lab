from hashlib import sha256
import json
from pathlib import Path

import yaml

from learning_runtime.schemas import GateDefinition
from learning_runtime.verification.models import RubricCriterion, VersionedRubric


class RubricError(ValueError):
    """Raised when a Gate rubric cannot be trusted."""


def load_rubric(repo_root: Path, gate: GateDefinition) -> VersionedRubric:
    if gate.rubric_ref is None or gate.rubric_version is None:
        raise RubricError(f"no rubric configured for {gate.gate_id}")
    root = repo_root.resolve()
    path = (root / gate.rubric_ref).resolve()
    if not path.is_relative_to(root):
        raise RubricError(f"rubric escapes repository: {gate.rubric_ref}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = raw.get("rubrics", []) if isinstance(raw, dict) else []
    matches = [row for row in rows if row.get("gate_id") == gate.gate_id]
    if len(matches) != 1:
        raise RubricError(f"rubric gate mismatch for {gate.gate_id}")
    row = matches[0]
    if int(row.get("version", -1)) != gate.rubric_version:
        raise RubricError(f"rubric version mismatch for {gate.gate_id}")
    criteria = tuple(
        RubricCriterion(
            criterion_id=str(item.get("criterion_id", "")),
            standard=str(item.get("standard", "")),
            passed_when=tuple(str(value) for value in item.get("passed_when", [])),
            failed_when=tuple(str(value) for value in item.get("failed_when", [])),
            insufficient_when=tuple(
                str(value) for value in item.get("insufficient_when", [])
            ),
            allowed_failure_modes=tuple(
                str(value) for value in item.get("allowed_failure_modes", [])
            ),
        )
        for item in row.get("criteria", [])
    )
    expected = {item.criterion_id for item in gate.required_evidence}
    actual = {item.criterion_id for item in criteria}
    if actual != expected or len(actual) != len(criteria):
        raise RubricError(f"rubric criterion mismatch for {gate.gate_id}")
    for item in criteria:
        if not all((item.standard, item.passed_when, item.failed_when, item.insufficient_when)):
            raise RubricError(f"incomplete rubric criterion: {item.criterion_id}")
        if not set(item.allowed_failure_modes) <= {"reinforce", "diagnose"}:
            raise RubricError(f"unsupported failure mode: {item.criterion_id}")
    canonical = json.dumps(row, ensure_ascii=False, sort_keys=True).encode()
    return VersionedRubric(
        rubric_id=str(row.get("rubric_id", "")),
        version=int(row["version"]),
        gate_id=str(row["gate_id"]),
        criteria=criteria,
        content_hash="sha256:" + sha256(canonical).hexdigest(),
    )
