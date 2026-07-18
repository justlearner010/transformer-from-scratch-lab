from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from learning_runtime.manifest import ManifestError, load_manifest


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "course-manifests/week-01.yaml"


def load_raw_manifest() -> dict[str, object]:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))


def write_manifest(tmp_path: Path, raw: dict[str, object]) -> Path:
    path = tmp_path / "manifest.yaml"
    path.write_text(
        yaml.safe_dump(raw, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def test_week_01_manifest_references_existing_course_contracts() -> None:
    manifest = load_manifest(MANIFEST_PATH, ROOT)

    assert manifest.course_id == "transformer-from-scratch"
    assert manifest.phase_id == "week-01"
    assert len(manifest.gates) == 7
    assert len({gate.gate_id for gate in manifest.gates}) == 7
    assert manifest.artifact_refs["task_chain"] == "tasks/week-01.md"
    assert manifest.failure_routes["week-00-review"] == (
        "weeks/week-00/README.md"
    )
    assert manifest.gates[0].rollback_target == "week-00-review"


def test_week_01_manifest_defines_the_committed_answer_contract() -> None:
    manifest = load_manifest(MANIFEST_PATH, ROOT)

    assert manifest.learner_workspace.answer_root == "homework_answer"
    assert manifest.learner_workspace.template_ref == (
        "resources/week-01/answer-template.md"
    )
    gate = manifest.gate("week-01-gate-0")
    assert gate.submission.artifact_path == "homework_answer/week-01/gate-00.md"
    assert gate.submission.attachment_policy == "at-least-one"


def test_duplicate_gate_id_is_rejected(tmp_path: Path) -> None:
    raw = load_raw_manifest()
    raw["gates"][1]["gate_id"] = raw["gates"][0]["gate_id"]

    with pytest.raises(ManifestError, match="week-01-gate-0"):
        load_manifest(write_manifest(tmp_path, raw), ROOT)


def test_missing_artifact_path_is_rejected(tmp_path: Path) -> None:
    raw = load_raw_manifest()
    raw["artifact_refs"]["task_chain"] = "tasks/does-not-exist.md"

    with pytest.raises(ManifestError, match="tasks/does-not-exist.md"):
        load_manifest(write_manifest(tmp_path, raw), ROOT)


def test_cyclic_gate_dependencies_are_rejected(tmp_path: Path) -> None:
    raw = load_raw_manifest()
    raw["dependencies"]["week-01-gate-0"] = ["week-01-gate-1"]

    with pytest.raises(ManifestError, match="cycle"):
        load_manifest(write_manifest(tmp_path, raw), ROOT)


def test_unknown_rollback_target_is_rejected(tmp_path: Path) -> None:
    raw = deepcopy(load_raw_manifest())
    raw["gates"][0]["rollback_target"] = "unknown-week"

    with pytest.raises(ManifestError, match="unknown-week"):
        load_manifest(write_manifest(tmp_path, raw), ROOT)


def test_missing_answer_template_is_rejected(tmp_path: Path) -> None:
    raw = load_raw_manifest()
    raw["learner_workspace"]["template_ref"] = "resources/missing-template.md"

    with pytest.raises(ManifestError, match="resources/missing-template.md"):
        load_manifest(write_manifest(tmp_path, raw), ROOT)


def test_answer_artifact_cannot_escape_answer_root(tmp_path: Path) -> None:
    raw = load_raw_manifest()
    raw["gates"][0]["submission"]["artifact_path"] = "notes/gate-00.md"

    with pytest.raises(ManifestError, match="notes/gate-00.md"):
        load_manifest(write_manifest(tmp_path, raw), ROOT)


def test_duplicate_answer_artifact_path_is_rejected(tmp_path: Path) -> None:
    raw = load_raw_manifest()
    raw["gates"][1]["submission"]["artifact_path"] = raw["gates"][0][
        "submission"
    ]["artifact_path"]

    with pytest.raises(ManifestError, match="gate-00.md"):
        load_manifest(write_manifest(tmp_path, raw), ROOT)


def test_unknown_attachment_policy_is_rejected(tmp_path: Path) -> None:
    raw = load_raw_manifest()
    raw["gates"][0]["submission"]["attachment_policy"] = "always-grade"

    with pytest.raises(ManifestError, match="always-grade"):
        load_manifest(write_manifest(tmp_path, raw), ROOT)
