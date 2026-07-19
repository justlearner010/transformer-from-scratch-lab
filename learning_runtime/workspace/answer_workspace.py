from dataclasses import dataclass
from pathlib import Path
import re

import yaml

from learning_runtime.schemas import CourseManifest, GateDefinition


class AnswerWorkspaceError(ValueError):
    """Raised when an answer artifact is missing or structurally invalid."""


@dataclass(frozen=True)
class AnswerLocation:
    artifact_path: Path
    attachment_dir: Path
    created: bool


@dataclass(frozen=True)
class AnswerInspection:
    artifact_path: Path
    attachment_paths: tuple[Path, ...]


FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SECTION = re.compile(r"^##\s+(.+?)\s*$\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


class AnswerWorkspace:
    def __init__(self, repo_root: Path, manifest: CourseManifest) -> None:
        self.repo_root = repo_root.resolve()
        self.manifest = manifest

    def initialize(self, gate: GateDefinition) -> AnswerLocation:
        artifact_relative = Path(gate.submission.artifact_path)
        artifact = self._inside_repo(artifact_relative)
        attachment_relative = (
            artifact_relative.parent / "attachments" / artifact_relative.stem
        )
        attachment_dir = self._inside_repo(attachment_relative)
        attachment_dir.mkdir(parents=True, exist_ok=True)

        created = not artifact.exists()
        if created:
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(self._render_template(gate), encoding="utf-8")
        return AnswerLocation(artifact_relative, attachment_relative, created)

    def initialize_all(self) -> AnswerLocation:
        """Prepare one non-overwriting fill-in file for every Gate in a phase."""
        locations = [self.initialize(gate) for gate in self.manifest.gates]
        return locations[0]

    def inspect(self, gate: GateDefinition) -> AnswerInspection:
        artifact_relative = Path(gate.submission.artifact_path)
        artifact = self._inside_repo(artifact_relative)
        if not artifact.is_file():
            raise AnswerWorkspaceError(f"answer artifact is missing: {artifact_relative}")
        text = artifact.read_text(encoding="utf-8")
        frontmatter_match = FRONTMATTER.search(text)
        if frontmatter_match is None:
            raise AnswerWorkspaceError(f"answer frontmatter is missing: {artifact_relative}")
        try:
            metadata = yaml.safe_load(frontmatter_match.group(1))
        except yaml.YAMLError as error:
            raise AnswerWorkspaceError(f"invalid answer frontmatter: {error}") from error
        actual_gate = str((metadata or {}).get("gate_id", ""))
        if actual_gate != gate.gate_id:
            raise AnswerWorkspaceError(
                f"answer gate_id {actual_gate!r} does not match {gate.gate_id}"
            )

        sections = {name: body for name, body in SECTION.findall(text)}
        invalid_sections = [
            name
            for name in gate.submission.required_sections
            if not self._has_student_content(sections.get(name, ""))
        ]
        if invalid_sections:
            raise AnswerWorkspaceError(
                "answer sections are blank: " + ", ".join(invalid_sections)
            )

        attachment_relative_dir = (
            artifact_relative.parent / "attachments" / artifact_relative.stem
        )
        attachment_dir = self._inside_repo(attachment_relative_dir)
        attachment_paths: list[Path] = []
        attachment_body = sections.get("手写与其他附件", "")
        for target in MARKDOWN_LINK.findall(attachment_body):
            if target.startswith(("http://", "https://", "#")):
                continue
            target_without_anchor = target.split("#", 1)[0]
            resolved = (artifact.parent / target_without_anchor).resolve()
            if not resolved.is_relative_to(attachment_dir):
                raise AnswerWorkspaceError(
                    f"attachment escapes Gate directory: {target}"
                )
            if not resolved.is_file():
                raise AnswerWorkspaceError(f"attachment is missing: {target}")
            attachment_paths.append(resolved.relative_to(self.repo_root))

        if (
            gate.submission.attachment_policy == "at-least-one"
            and not attachment_paths
        ):
            raise AnswerWorkspaceError(
                f"at least one attachment is required for {gate.gate_id}"
            )
        return AnswerInspection(artifact_relative, tuple(attachment_paths))

    def _inside_repo(self, relative_path: Path) -> Path:
        candidate = (self.repo_root / relative_path).resolve()
        if not candidate.is_relative_to(self.repo_root):
            raise AnswerWorkspaceError(f"path escapes repository: {relative_path}")
        return candidate

    def _render_template(self, gate: GateDefinition) -> str:
        template = self._inside_repo(
            Path(self.manifest.learner_workspace.template_ref)
        ).read_text(encoding="utf-8")
        required = "、".join(gate.submission.required_sections)
        attachment = (
            "至少一个附件"
            if gate.submission.attachment_policy == "at-least-one"
            else "可选"
        )
        format_notice = (
            "> **本 Gate 提交格式**\n>\n"
            f"> 必填栏目：{required}\n>\n"
            f"> 附件：{attachment}\n\n"
        )
        sections = list(gate.submission.required_sections)
        if "手写与其他附件" not in sections:
            submit_index = sections.index("提交自检")
            sections.insert(submit_index, "手写与其他附件")
        answer_sections = "\n\n".join(
            f"## {section}\n\n{self._section_prompt(section, required=section in gate.submission.required_sections)}"
            for section in sections
        )
        gate_number = str(int(gate.gate_id.rsplit("-", 1)[-1]))
        rendered = (
            template.replace("{{course_id}}", self.manifest.course_id)
            .replace("{{phase_id}}", self.manifest.phase_id)
            .replace("{{gate_id}}", gate.gate_id)
            .replace("{{gate_number}}", gate_number)
            .replace("{{gate_action}}", gate.action)
            .replace("{{gate_checks}}", "；".join(gate.checks))
            .replace("{{answer_sections}}", answer_sections)
        )
        return rendered.replace("\n# Gate", f"\n{format_notice}# Gate", 1)

    @staticmethod
    def _section_prompt(section: str, *, required: bool) -> str:
        prompts = {
            "提交自检": "<!-- 请填写：是否先独立作答、是否已手动 commit -->",
            "手写与其他附件": "<!-- 可选：填写本 Gate 附件的仓库相对链接；没有附件可留空 -->",
        }
        if section in prompts:
            return prompts[section]
        qualifier = "请独立填写" if required else "可选填写"
        return f"<!-- {qualifier} -->"

    @staticmethod
    def _has_student_content(body: str) -> bool:
        without_comments = HTML_COMMENT.sub("", body)
        return bool(without_comments.strip())
