from pathlib import Path
import re
import shutil

import pytest

from learning_runtime.manifest import load_manifest
from learning_runtime.workspace.answer_workspace import (
    AnswerWorkspace,
    AnswerWorkspaceError,
)


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = load_manifest(ROOT / "course-manifests/week-01.yaml", ROOT)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    template = repo / MANIFEST.learner_workspace.template_ref
    template.parent.mkdir(parents=True)
    shutil.copy2(ROOT / MANIFEST.learner_workspace.template_ref, template)
    return repo


def fill_answer(path: Path, *, attachment_link: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "我的独立回答与证据", text)
    if attachment_link:
        text = text.replace(
            "我的独立回答与证据\n\n## 提交自检",
            f"我的独立回答与证据\n\n![手写推导]({attachment_link})\n\n## 提交自检",
            1,
        )
    path.write_text(text, encoding="utf-8")


def replace_section(text: str, name: str, content: str) -> str:
    return re.sub(
        rf"(^## {re.escape(name)}\s*$\n)(.*?)(?=^## |\Z)",
        rf"\1{content}\n\n",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )


def test_initialize_creates_all_gate_templates_and_never_overwrites(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)
    gate = MANIFEST.gate("week-01-gate-0")

    first = workspace.initialize_all()
    first_path = repo / first.artifact_path
    original = first_path.read_text(encoding="utf-8")
    first_path.write_text(original + "\n学生自己的内容\n", encoding="utf-8")
    second = workspace.initialize_all()

    assert first.created is True
    assert second.created is False
    assert "gate_id: week-01-gate-0" in original
    assert "# Gate 0 作答" in original
    assert (repo / first.attachment_dir).is_dir()
    assert (repo / "homework_answer/week-01/gate-01.md").is_file()
    assert (repo / "homework_answer/week-01/attachments/gate-01").is_dir()
    assert first_path.read_text(encoding="utf-8").endswith("学生自己的内容\n")


def test_initialize_all_writes_each_gate_its_own_fill_in_format(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)

    workspace.initialize_all()

    gate_zero = (repo / "homework_answer/week-01/gate-00.md").read_text(
        encoding="utf-8"
    )
    gate_one = (repo / "homework_answer/week-01/gate-01.md").read_text(
        encoding="utf-8"
    )
    assert "闭卷写出 Q、K、V、QK^T、weights 和 weights@V 的 shape，再运行 shape micro-lab 对照预测。" in gate_zero
    assert "## 闭卷答案" in gate_zero
    assert "## 运行前预测" not in gate_zero
    assert "完成 shape 表，并预测只改变 V 时哪些量保持不变。" in gate_one
    assert "## 预测" in gate_one
    assert "## 推导或机制解释" not in gate_one


def test_initialize_all_upgrades_an_untouched_old_template_only(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)
    gate = MANIFEST.gate("week-01-gate-1")
    location = workspace.initialize(gate)
    path = repo / location.artifact_path
    path.write_text(
        path.read_text(encoding="utf-8").replace("template_version: 2", "template_version: 1"),
        encoding="utf-8",
    )

    workspace.initialize_all()

    assert "template_version: 2" in path.read_text(encoding="utf-8")


def test_initialize_shows_gate_specific_format_before_answer(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)
    location = workspace.initialize(MANIFEST.gate("week-01-gate-0"))

    text = (repo / location.artifact_path).read_text(encoding="utf-8")

    assert "本 Gate 提交格式" in text
    assert "闭卷答案、推导或机制解释、提交自检" in text
    assert "附件：可选" in text


def test_inspect_accepts_filled_answer_and_linked_gate_attachment(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)
    gate = MANIFEST.gate("week-01-gate-0")
    location = workspace.initialize(gate)
    attachment = repo / location.attachment_dir / "shape.jpg"
    attachment.write_bytes(b"handwritten-shape")
    fill_answer(
        repo / location.artifact_path,
        attachment_link="attachments/gate-00/shape.jpg",
    )

    inspection = workspace.inspect(gate)

    assert inspection.artifact_path == Path("homework_answer/week-01/gate-00.md")
    assert inspection.attachment_paths == (
        Path("homework_answer/week-01/attachments/gate-00/shape.jpg"),
    )


def test_inspect_rejects_wrong_gate_frontmatter(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)
    gate = MANIFEST.gate("week-01-gate-0")
    location = workspace.initialize(gate)
    path = repo / location.artifact_path
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "gate_id: week-01-gate-0", "gate_id: week-01-gate-1"
        ),
        encoding="utf-8",
    )

    with pytest.raises(AnswerWorkspaceError, match="week-01-gate-1"):
        workspace.inspect(gate)


def test_inspect_rejects_blank_template_sections(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)
    gate = MANIFEST.gate("week-01-gate-0")
    workspace.initialize(gate)

    with pytest.raises(AnswerWorkspaceError, match="闭卷答案"):
        workspace.inspect(gate)


def test_gate_zero_accepts_required_sections_without_attachment(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)
    gate = MANIFEST.gate("week-01-gate-0")
    location = workspace.initialize(gate)
    path = repo / location.artifact_path
    text = path.read_text(encoding="utf-8")
    for name, content in (
        ("闭卷答案", "shape chain"),
        ("推导或机制解释", "K.T explanation"),
        ("提交自检", "独立完成并手动提交"),
    ):
        text = replace_section(text, name, content)
    path.write_text(text, encoding="utf-8")

    inspection = workspace.inspect(gate)

    assert inspection.attachment_paths == ()


@pytest.mark.parametrize(
    "link",
    [
        "attachments/gate-00/missing.jpg",
        "../../outside.jpg",
    ],
)
def test_inspect_rejects_missing_or_escaping_attachment(
    tmp_path: Path, link: str
) -> None:
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)
    gate = MANIFEST.gate("week-01-gate-0")
    location = workspace.initialize(gate)
    fill_answer(repo / location.artifact_path, attachment_link=link)

    with pytest.raises(AnswerWorkspaceError, match="attachment"):
        workspace.inspect(gate)
