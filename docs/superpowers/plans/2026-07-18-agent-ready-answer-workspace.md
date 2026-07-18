# Agent-Ready Answer Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a student initialize one Markdown answer per Gate and submit it only after the answer and linked attachments are committed on the student's own branch.

**Architecture:** Keep the deterministic runtime as an Agent tool boundary, not an Agent simulation. A generic template and Manifest submission metadata drive `AnswerWorkspace`; a read-only `GitGuard` proves provenance; CLI only composes those tools and appends artifact evidence before the existing state transition.

**Tech Stack:** Python 3.12+, dataclasses, PyYAML, pathlib, subprocess Git, hashlib, pytest, uv.

---

## Reuse boundary

The future Agent directly reuses `load_manifest`, `AnswerWorkspace`, `GitGuard`, `EventLedger`, `PolicyEngine`, and `LearningStateMachine`. It may replace `cli.py` and `Coordinator` wording. This plan does not add LLM orchestration, new state statuses, OCR, grading, branch creation, or Git writes.

### Task 1: Minimal submission contract in the Manifest

**Files:**
- Modify: `learning_runtime/schemas.py`
- Modify: `learning_runtime/manifest.py`
- Modify: `course-manifests/week-01.yaml`
- Create: `resources/week-01/answer-template.md`
- Modify: `tests/learning_runtime/test_manifest.py`

- [ ] **Step 1: Write failing contract tests**

Add tests asserting that the loaded Manifest exposes:

```python
assert manifest.learner_workspace.answer_root == "homework_answer"
assert manifest.learner_workspace.template_ref == "resources/week-01/answer-template.md"
assert manifest.gate("week-01-gate-0").submission.artifact_path == (
    "homework_answer/week-01/gate-00.md"
)
assert manifest.gate("week-01-gate-0").submission.attachment_policy == "at-least-one"
```

Add mutated-manifest tests rejecting a template path that does not exist, an artifact path outside `homework_answer/`, duplicate artifact paths, and an unsupported attachment policy.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_manifest.py -q`
Expected: FAIL because the schema has no learner workspace or submission definition.

- [ ] **Step 3: Implement the minimal schema**

Add frozen dataclasses:

```python
@dataclass(frozen=True)
class LearnerWorkspace:
    answer_root: str
    template_ref: str
    protected_branches: tuple[str, ...]
    commit_required: bool

@dataclass(frozen=True)
class SubmissionDefinition:
    artifact_path: str
    required_sections: tuple[str, ...]
    attachment_policy: str
```

Attach them to `CourseManifest` and `GateDefinition`. The loader validates repository-relative paths, path containment, uniqueness, and policies `optional` or `at-least-one`.

- [ ] **Step 4: Add one answer-free template and Gate paths**

The generic template contains frontmatter tokens `{{course_id}}`, `{{phase_id}}`, `{{gate_id}}`, `{{gate_number}}`, plus the eight agreed headings and `<!-- 请填写 -->` placeholders. Gate 0 uses `at-least-one`; Gates 1–6 use `optional`.

- [ ] **Step 5: Verify GREEN and commit**

Run: `uv run pytest tests/learning_runtime/test_manifest.py -q`
Expected: PASS.

```bash
git add learning_runtime/schemas.py learning_runtime/manifest.py course-manifests/week-01.yaml resources/week-01/answer-template.md tests/learning_runtime/test_manifest.py
git commit -m "feat: define committed answer contract"
```

### Task 2: Reusable Answer Workspace tool

**Files:**
- Create: `learning_runtime/workspace/__init__.py`
- Create: `learning_runtime/workspace/answer_workspace.py`
- Create: `tests/learning_runtime/test_answer_workspace.py`

- [ ] **Step 1: Write failing initialization tests**

Using `tmp_path`, prove that `AnswerWorkspace(repo_root, manifest).initialize(gate)` creates only the current Gate file and attachment directory, expands all template tokens, and returns `created=True`. Write custom content, call it again, and assert bytes are unchanged with `created=False`.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_answer_workspace.py -q`
Expected: FAIL because `AnswerWorkspace` is missing.

- [ ] **Step 3: Implement initialization**

Add frozen `AnswerLocation(artifact_path, attachment_dir, created)`. Resolve every path under the repository root, create parent directories, use `Path.write_text` only when the artifact does not exist, and never overwrite a student file.

- [ ] **Step 4: Write failing inspection tests**

Cover wrong frontmatter Gate, blank placeholder sections, Gate 0 without an attachment, a missing linked attachment, a link escaping the Gate attachment directory, and a valid Markdown plus `.jpg` attachment. The valid result must return the artifact path and exact attachment paths without judging answer correctness.

- [ ] **Step 5: Implement structural inspection**

Add frozen `AnswerInspection(artifact_path, attachment_paths)`. Parse frontmatter with `yaml.safe_load`, find `##` section bodies, reject empty or placeholder-only required sections, extract local Markdown links, ignore `http(s)` links, and enforce attachment containment and policy.

- [ ] **Step 6: Verify GREEN and commit**

Run: `uv run pytest tests/learning_runtime/test_answer_workspace.py -q`
Expected: PASS.

```bash
git add learning_runtime/workspace/answer_workspace.py learning_runtime/workspace/__init__.py tests/learning_runtime/test_answer_workspace.py
git commit -m "feat: add student answer workspace tool"
```

### Task 3: Read-only Git provenance tool

**Files:**
- Create: `learning_runtime/workspace/git_guard.py`
- Create: `tests/learning_runtime/test_git_guard.py`

- [ ] **Step 1: Write failing Git integration tests**

Create a temporary Git repository with local user configuration. Cover protected branch rejection, untracked evidence, staged-but-uncommitted evidence, committed evidence, modification after commit, and an unrelated dirty file. Capture `git status --porcelain` before and after each Git Guard call and assert it never changes.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_git_guard.py -q`
Expected: FAIL because `GitGuard` is missing.

- [ ] **Step 3: Implement Git Guard**

Add:

```python
@dataclass(frozen=True)
class GitSnapshot:
    branch: str
    commit_sha: str
    content_hashes: Mapping[str, str]
```

Implement `GitGuard.assert_student_branch(protected_branches) -> str` and `GitGuard.snapshot_committed(paths) -> GitSnapshot`. Use `subprocess.run` with argument arrays and `shell=False`. Read only `branch --show-current`, `rev-parse HEAD`, `ls-files --error-unmatch`, `status --porcelain -- <paths>`, and `show HEAD:<path>`. Compute `sha256:` hashes from committed bytes. Never invoke add, commit, checkout, switch, reset, restore, clean, or push.

- [ ] **Step 4: Verify GREEN and commit**

Run: `uv run pytest tests/learning_runtime/test_git_guard.py -q`
Expected: PASS.

```bash
git add learning_runtime/workspace/git_guard.py tests/learning_runtime/test_git_guard.py
git commit -m "feat: verify committed answer provenance"
```

### Task 4: Wire committed answers into the temporary CLI

**Files:**
- Modify: `learning_runtime/schemas.py`
- Modify: `learning_runtime/coordinator.py`
- Modify: `learning_runtime/cli.py`
- Create: `tests/learning_runtime/conftest.py`
- Modify: `tests/learning_runtime/test_coordinator.py`
- Modify: `tests/learning_runtime/test_end_to_end_foundation.py`
- Modify: `README.md`
- Modify: `docs/runtime-foundation.md`

- [ ] **Step 1: Build a real student-repository fixture**

Copy the tracked project into `tmp_path`, initialize Git, commit the course baseline, and switch to `learner/test/week-01`. Monkeypatch `learning_runtime.cli.REPO_ROOT` to that repository. This fixture exercises real Git without modifying the development worktree.

- [ ] **Step 2: Write failing CLI tests**

Prove `start` rejects `main` without creating a ledger, creates only Gate 0 on a learner branch, and prints the answer path. Prove blank or uncommitted answers do not append `attempt_submitted`. Fill all sections, add a Gate 0 image, manually commit through test Git commands, then assert `submit` appends `artifact_observed`, `attempt_submitted`, and `transition_applied` with branch, commit SHA, artifact hash, and attachment hash.

- [ ] **Step 3: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_end_to_end_foundation.py -q`
Expected: FAIL because CLI does not initialize or inspect answers.

- [ ] **Step 4: Implement minimal CLI composition**

Before `start`, call `GitGuard.assert_student_branch`; then initialize the current Gate answer and include its path in the `session_started` payload. Before `submit`, call `AnswerWorkspace.inspect` and `GitGuard.snapshot_committed`; append one `artifact_observed` event with a deterministic next `evidence-NNNN` ID, then append the attempt and existing state transition using that evidence reference. Failures return code 2 before any state-bearing event.

Extend `ActionContract` with `answer_path: str` and render it in `next`. Do not add Agent messages or new state statuses.

- [ ] **Step 5: Verify GREEN**

Run: `uv run pytest tests/learning_runtime/test_end_to_end_foundation.py tests/learning_runtime/test_coordinator.py -q`
Expected: PASS.

- [ ] **Step 6: Run full regression and document the boundary**

Run:

```bash
uv run pytest -q
uv run python scripts/verify_course_pdfs.py
git diff --check
```

Document the manual student workflow: create branch, start, fill Markdown, add attachment, manually commit, then submit. State that CLI is replaceable and the Workspace/Git/Ledger/Policy interfaces are the Agent migration seam.

- [ ] **Step 7: Commit**

```bash
git add learning_runtime tests/learning_runtime README.md docs/runtime-foundation.md
git commit -m "feat: require committed answers for submission"
```

## Explicitly deferred

- Seven independently authored Gate templates.
- OCR or semantic grading of handwriting.
- Template migration and answer auto-upgrade.
- Runtime-created branches or commits.
- Agent orchestration and conversational hint wording.
- PASS/REINFORCE/DIAGNOSE routing from actual grader evidence.
