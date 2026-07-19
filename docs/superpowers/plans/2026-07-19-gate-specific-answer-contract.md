# Gate-Specific Answer Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Gate 0 require only `闭卷答案`, `推导或机制解释`, and `提交自检`, with attachments optional and required sections visible to the learner.

**Architecture:** Keep the shared eight-section Markdown template, but override Gate 0's machine contract in the manifest. Project the manifest's required sections through `ActionContract` so deterministic and Qwen presenters display trusted requirements without inventing them.

**Tech Stack:** YAML manifest, Python dataclasses, pytest, existing AnswerWorkspace and Agent Presenter.

---

### Task 1: Gate 0 minimal evidence contract

**Files:**
- Modify: `course-manifests/week-01.yaml`
- Modify: `tests/learning_runtime/test_manifest.py`
- Modify: `tests/learning_runtime/test_answer_workspace.py`

- [ ] **Step 1: Add failing manifest and workspace tests**

```python
def test_gate_zero_has_minimal_required_sections():
    manifest = load_manifest(MANIFEST_PATH, ROOT)
    gate = manifest.gate("week-01-gate-0")
    assert gate.submission.required_sections == (
        "闭卷答案", "推导或机制解释", "提交自检",
    )
    assert gate.submission.attachment_policy == "optional"


def replace_section(text, name, content):
    return re.sub(
        rf"(^## {re.escape(name)}\s*$\n)(.*?)(?=^## |\Z)",
        rf"\1{content}\n\n", text, flags=re.MULTILINE | re.DOTALL,
    )


def test_gate_zero_accepts_only_required_sections_without_attachment(tmp_path):
    repo = make_repo(tmp_path)
    workspace = AnswerWorkspace(repo, MANIFEST)
    gate = workspace.manifest.gate("week-01-gate-0")
    location = workspace.initialize(gate)
    path = repo / location.artifact_path
    text = path.read_text(encoding="utf-8")
    text = replace_section(text, "闭卷答案", "shape chain")
    text = replace_section(text, "推导或机制解释", "K.T explanation")
    text = replace_section(text, "提交自检", "独立完成")
    path.write_text(text, encoding="utf-8")
    inspection = workspace.inspect(gate)
    assert inspection.attachment_paths == ()
```

- [ ] **Step 2: Run and verify RED**

Run: `uv run pytest tests/learning_runtime/test_manifest.py tests/learning_runtime/test_answer_workspace.py -q`

Expected: FAIL because Gate 0 still uses all eight sections and `at-least-one`.

- [ ] **Step 3: Override only Gate 0 in the manifest**

```yaml
submission:
  artifact_path: homework_answer/week-01/gate-00.md
  required_sections:
    - 闭卷答案
    - 推导或机制解释
    - 提交自检
  attachment_policy: optional
```

- [ ] **Step 4: Run GREEN and commit**

Run: `uv run pytest tests/learning_runtime/test_manifest.py tests/learning_runtime/test_answer_workspace.py -q`

Expected: all targeted tests pass.

```bash
git add course-manifests/week-01.yaml tests/learning_runtime/test_manifest.py tests/learning_runtime/test_answer_workspace.py
git commit -m "fix: scope gate zero answer requirements"
```

### Task 2: Trusted required-section projection

**Files:**
- Modify: `learning_runtime/schemas.py`
- Modify: `learning_runtime/coordinator.py`
- Modify: `learning_runtime/agent/presenter.py`
- Modify: `learning_runtime/agent/siliconflow.py`
- Modify: `learning_runtime/cli.py`
- Modify: `tests/learning_runtime/test_coordinator.py`
- Modify: `tests/learning_runtime/test_agent_presenter.py`
- Modify: `tests/learning_runtime/test_siliconflow_presenter.py`

- [ ] **Step 1: Add failing projection tests**

```python
def test_action_contract_projects_gate_required_sections():
    state = LearnerState(
        course_id=MANIFEST.course_id,
        phase_id=MANIFEST.phase_id,
        current_gate="week-01-gate-0",
        gate_status=GateStatus.ACTIVE,
    )
    action = Coordinator(MANIFEST).next_action(state)
    assert action.required_sections == (
        "闭卷答案", "推导或机制解释", "提交自检",
    )


def test_deterministic_presenter_lists_required_sections():
    presentation = request()
    presentation = replace(
        presentation,
        action=replace(presentation.action, required_sections=("闭卷答案", "提交自检")),
    )
    text = DeterministicPresenter().present(presentation)
    assert "本 Gate 必填栏目" in text
    assert "闭卷答案" in text
    assert "提交自检" in text
```

Extend the recording-client test with:

```python
payload = json.loads(kwargs["messages"][1]["content"])
assert payload["required_sections"] == ["闭卷答案", "推导或机制解释", "提交自检"]
```

- [ ] **Step 2: Run and verify RED**

Run: `uv run pytest tests/learning_runtime/test_coordinator.py tests/learning_runtime/test_agent_presenter.py tests/learning_runtime/test_siliconflow_presenter.py -q`

Expected: FAIL because `ActionContract` has no `required_sections` and presenters omit it.

- [ ] **Step 3: Implement the typed projection**

```python
# learning_runtime/schemas.py, final ActionContract field
required_sections: tuple[str, ...] = field(default_factory=tuple)

# learning_runtime/coordinator.py, ActionContract construction
required_sections=gate.submission.required_sections,

# learning_runtime/agent/presenter.py
required = "、".join(action.required_sections) or "无"
# Include: f"本 Gate 必填栏目：{required}\n"

# learning_runtime/agent/siliconflow.py payload
"required_sections": list(request.action.required_sections),

# learning_runtime/cli.py _render_action
print("本 Gate 必填栏目：" + "、".join(action.required_sections))
```

- [ ] **Step 4: Run GREEN and full verification**

Run:

```bash
uv run pytest tests/learning_runtime/test_coordinator.py tests/learning_runtime/test_agent_presenter.py tests/learning_runtime/test_siliconflow_presenter.py -q
uv run pytest -q
uv run python scripts/verify_course_pdfs.py
git diff --check
```

Expected: all tests pass; live tests skip without a key; four PDFs verify.

- [ ] **Step 5: Commit**

```bash
git add learning_runtime/schemas.py learning_runtime/coordinator.py learning_runtime/agent/presenter.py learning_runtime/agent/siliconflow.py learning_runtime/cli.py tests/learning_runtime/test_coordinator.py tests/learning_runtime/test_agent_presenter.py tests/learning_runtime/test_siliconflow_presenter.py
git commit -m "feat: show gate-specific answer requirements"
```

### Completion audit

- [ ] Gate 0 accepts three required sections with no attachment.
- [ ] Missing required sections still fail with their names.
- [ ] A supplied invalid attachment link still fails.
- [ ] Gate 1–6 machine contracts are unchanged.
- [ ] Agent and maintenance CLI show trusted required sections.
