# Stable Agent Verifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a SiliconFlow-backed criterion verifier whose first valid result is content-addressed and reused, while deterministic Policy and State Machine remain the only state authority.

**Architecture:** Gate 0 receives a versioned machine rubric. A provider-neutral verification service validates model JSON, stores one immutable evaluation per answer/rubric/verifier key in the existing EventLedger, and returns trusted `CriterionResult` objects. `LearningRuntime.evaluate_current()` composes the service with Policy and State Machine; SiliconFlow remains an adapter and never receives state-write authority.

**Tech Stack:** Python 3.12+, dataclasses, PyYAML, OpenAI-compatible Python SDK, hashlib, JSON, pytest, real temporary Git repositories.

---

## File map

- Create `course-manifests/rubrics/week-01.yaml`: public, answer-free Gate 0 criterion standard.
- Modify `learning_runtime/schemas.py` and `learning_runtime/manifest.py`: optional rubric reference/version on Gates.
- Create `learning_runtime/verification/models.py`: rubric, request, verifier identity, raw response, evaluation record types.
- Create `learning_runtime/verification/rubric.py`: strict rubric loader and canonical hash.
- Create `learning_runtime/verification/validator.py`: reject Agent state fields and convert raw JSON to trusted criterion results.
- Create `learning_runtime/verification/registry.py`: content-addressed evaluation lookup/store over EventLedger.
- Create `learning_runtime/verification/service.py`: cache-first verifier orchestration.
- Create `learning_runtime/verification/siliconflow.py`: environment-only SiliconFlow Chat Completions adapter.
- Modify `learning_runtime/workspace/git_guard.py`: read bytes from the recorded commit safely.
- Modify `learning_runtime/runtime.py`: add `evaluate_current()` and deterministic Policy/State Machine application.
- Add deterministic tests under `tests/learning_runtime/` and optional live test under `tests/live/`.
- Modify `.gitignore`, create `.env.example`, modify `pyproject.toml`, and update `docs/runtime-foundation.md`.

### Task 1: Versioned Gate 0 rubric contract

**Files:**
- Create: `course-manifests/rubrics/week-01.yaml`
- Create: `learning_runtime/verification/__init__.py`
- Create: `learning_runtime/verification/models.py`
- Create: `learning_runtime/verification/rubric.py`
- Modify: `learning_runtime/schemas.py`
- Modify: `learning_runtime/manifest.py`
- Modify: `course-manifests/week-01.yaml`
- Test: `tests/learning_runtime/test_rubric.py`

- [ ] **Step 1: Write failing rubric tests**

Test that Gate 0 exposes `rubric_ref` and `rubric_version`, its rubric contains exactly `shape-bridge-complete`, and the loader rejects a Gate mismatch, criterion mismatch, unsupported failure mode, or changed YAML version.

```python
rubric = load_rubric(ROOT, MANIFEST.gate("week-01-gate-0"))
assert rubric.rubric_id == "week-01-gate-0-rubric"
assert rubric.version == 1
assert tuple(item.criterion_id for item in rubric.criteria) == (
    "shape-bridge-complete",
)
assert rubric.content_hash.startswith("sha256:")
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_rubric.py -q`

Expected: FAIL because Gate rubric fields and loader do not exist.

- [ ] **Step 3: Implement frozen rubric models and loader**

Add `RubricCriterion` and `VersionedRubric` in `models.py`. `load_rubric(repo_root, gate)` reads only the configured repository-relative YAML, canonicalizes the parsed mapping with sorted JSON, computes `sha256:<hex>`, and validates Gate ID, version, exact required criterion IDs, non-empty standards/conditions, and failure modes limited to `reinforce` and `diagnose`.

Add optional fields to `GateDefinition`:

```python
rubric_ref: str | None = None
rubric_version: int | None = None
```

Gate 0 points to `course-manifests/rubrics/week-01.yaml` version 1. Gates 1–6 remain without rubric and are unavailable to the verifier.

- [ ] **Step 4: Verify GREEN and commit**

Run: `uv run pytest tests/learning_runtime/test_rubric.py tests/learning_runtime/test_manifest.py -q`

Expected: PASS.

```bash
git add course-manifests learning_runtime/schemas.py learning_runtime/manifest.py learning_runtime/verification tests/learning_runtime/test_rubric.py
git commit -m "feat: define versioned gate rubric"
```

### Task 2: Strict criterion validation and stable Evaluation Registry

**Files:**
- Modify: `learning_runtime/verification/models.py`
- Create: `learning_runtime/verification/protocol.py`
- Create: `learning_runtime/verification/validator.py`
- Create: `learning_runtime/verification/registry.py`
- Create: `learning_runtime/verification/service.py`
- Test: `tests/learning_runtime/test_stable_verifier.py`

- [ ] **Step 1: Write failing authority and idempotency tests**

Use a `SequenceVerifier` that returns passed on its first call and failed on any later call. Evaluate the same `VerificationRequest` twice and assert one provider call, one `verification_recorded` event, the same record ID/results, and no duplicate semantic evaluation.

Add parameterized invalid payloads containing `gate_status`, `recommendation`, missing/duplicate/unknown criterion, bad enum, or a quote absent from the answer. Assert `VerificationOutputError` and no evaluation record.

Add a rubric-v2 copy and assert the key changes, the verifier is called again, and both immutable records remain.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_stable_verifier.py -q`

Expected: FAIL because verifier protocol, validator, registry, and service do not exist.

- [ ] **Step 3: Implement the provider-neutral contract**

Add these frozen types:

```python
@dataclass(frozen=True)
class VerifierIdentity:
    provider: str
    model: str
    prompt_version: str
    schema_version: str
    settings: Mapping[str, object]

@dataclass(frozen=True)
class VerificationAttachment:
    path: str
    content_hash: str
    content: bytes

@dataclass(frozen=True)
class VerificationRequest:
    course_id: str
    gate_id: str
    evidence_id: str
    answer_path: str
    answer_hash: str
    answer_text: str
    attachments: tuple[VerificationAttachment, ...]
    rubric: VersionedRubric
    verifier_identity: VerifierIdentity

@dataclass(frozen=True)
class RawVerificationResponse:
    payload: Mapping[str, object]
    response_id: str
    model: str
    usage: Mapping[str, int]
```

Define `Verifier` as a `Protocol` exposing `identity` and `verify(request)`.

- [ ] **Step 4: Implement strict validation and evaluation identity**

`validate_response(raw, request)` requires exact top-level and criterion key sets, exact criterion coverage, unique IDs, valid status/failure mode, and answer-contained quotes for passed/failed results. It constructs `CriterionResult` with `(request.evidence_id,)`; model-supplied state or evidence fields are impossible.

Compute `evaluation_key` from course/gate, answer hash, sorted attachment hashes, rubric identity/hash, and canonical verifier identity. Deliberately exclude evidence ID so identical content submitted again reuses the evaluation.

- [ ] **Step 5: Implement cache-first service**

`StableVerificationService.evaluate(request)` checks `EvaluationRegistry.lookup(key)` before calling the verifier. A miss validates one raw response and appends `verification_recorded`; a hit returns the stored record and appends `verification_reused` only when the new evidence ID differs. Conflicting stored records for one key raise `EvaluationConflictError`.

- [ ] **Step 6: Verify GREEN and commit**

Run: `uv run pytest tests/learning_runtime/test_stable_verifier.py -q`

Expected: PASS.

```bash
git add learning_runtime/verification tests/learning_runtime/test_stable_verifier.py
git commit -m "feat: stabilize agent criterion evaluations"
```

### Task 3: SiliconFlow adapter and credential-safe live test

**Files:**
- Create: `learning_runtime/verification/siliconflow.py`
- Create: `tests/learning_runtime/test_siliconflow_verifier.py`
- Create: `tests/live/test_siliconflow_verifier.py`
- Modify: `pyproject.toml`
- Modify: `.gitignore`
- Create: `.env.example`

- [ ] **Step 1: Write failing adapter unit tests**

Inject a fake OpenAI-compatible client and assert `chat.completions.create` receives the configured model, `response_format={"type": "json_object"}`, `temperature=0`, `extra_body={"enable_thinking": False}`, rubric/answer text, and base64 image content. Assert malformed JSON and missing API key raise sanitized errors that never contain credentials.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_siliconflow_verifier.py -q`

Expected: FAIL because the adapter does not exist.

- [ ] **Step 3: Implement SiliconFlowVerifier**

Add `openai>=1.0` to dependencies. `SiliconFlowVerifier.from_env()` reads `SILICONFLOW_API_KEY`, optional base URL/model overrides, and constructs `OpenAI(api_key=api_key, base_url=base_url)`. `verify()` sends non-streaming Chat Completions JSON mode with bounded output, parses content into a mapping, and returns response ID/model/token usage. Only `.png`, `.jpg`, `.jpeg`, and `.webp` attachments become base64 data URLs.

Add `.env` to `.gitignore`. `.env.example` contains only:

```dotenv
SILICONFLOW_API_KEY=
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=Qwen/Qwen3.6-35B-A3B
```

- [ ] **Step 4: Add opt-in live smoke test**

Register a `live` pytest marker. The live test skips unless `SILICONFLOW_API_KEY` exists, sends one synthetic Gate 0 answer, validates criterion coverage, then evaluates the identical request through Registry twice and asserts the second result is reused.

- [ ] **Step 5: Verify GREEN and commit**

Run:

```bash
uv sync --group dev
uv run pytest tests/learning_runtime/test_siliconflow_verifier.py -q
uv run pytest tests/live/test_siliconflow_verifier.py -q
```

Expected: unit tests PASS; live test SKIP without environment Key.

```bash
git add pyproject.toml uv.lock .gitignore .env.example learning_runtime/verification/siliconflow.py tests/learning_runtime/test_siliconflow_verifier.py tests/live/test_siliconflow_verifier.py
git commit -m "feat: add siliconflow verifier adapter"
```

### Task 4: Deterministic Runtime evaluation and state test

**Files:**
- Modify: `learning_runtime/workspace/git_guard.py`
- Modify: `learning_runtime/runtime.py`
- Test: `tests/learning_runtime/test_agent_state_authority.py`

- [ ] **Step 1: Write failing end-to-end state authority tests**

Build a real temporary student repository, start Gate 0, commit a complete answer/image, submit it, and call `runtime.evaluate_current(fake_verifier)`. Assert the legal event tail is `verification_recorded`, transition to evaluating, `policy_decided`, and final `transition_applied`; passed advances to Gate 1.

Repeat with an Agent payload containing `gate_status: passed`; assert evaluation raises, no policy/final transition is appended, and replay remains `evidence_pending`.

Use the same answer/rubric/verifier in an independent pending-state fixture backed by the same Registry and assert the cached criterion result produces the same Policy recommendation without another verifier call.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_agent_state_authority.py -q`

Expected: FAIL because `LearningRuntime.evaluate_current()` does not exist.

- [ ] **Step 3: Add recorded-commit evidence reading**

Extend `GitGuard` with `read_committed(commit_sha, path) -> bytes`. Validate the SHA as 40 lowercase hex characters and the path remains inside the repository, then use argument-array `git show <sha>:<path>`. Recompute every recorded hash before building a request; mismatch raises before any policy event.

- [ ] **Step 4: Implement Runtime evaluation**

`evaluate_current(verifier)` requires `evidence_pending`, finds the latest referenced `artifact_observed`, loads Gate 0 rubric and committed bytes, builds `VerificationRequest`, and calls `StableVerificationService`. On a valid record it appends the legal evaluating transition, derives a `TransitionDecision` only through `PolicyEngine`, appends `policy_decided`, applies `LearningStateMachine.apply_decision`, and returns an `EvaluationReceipt` containing record ID, decision, and replayed state.

On provider/JSON/schema error, append a non-state `verification_failed` event and re-raise; state remains `evidence_pending`. A missing Gate rubric fails before a provider call.

- [ ] **Step 5: Verify GREEN and commit**

Run:

```bash
uv run pytest tests/learning_runtime/test_agent_state_authority.py tests/learning_runtime/test_agent_tool_seam.py -q
```

Expected: PASS.

```bash
git add learning_runtime/runtime.py learning_runtime/workspace/git_guard.py tests/learning_runtime/test_agent_state_authority.py
git commit -m "feat: enforce agent state authority"
```

### Task 5: Documentation and full verification

**Files:**
- Modify: `docs/runtime-foundation.md`
- Modify: `README.md`

- [ ] **Step 1: Document stable evaluation**

Explain criterion-only Agent output, evaluation key reuse, Gate 0-only scope, environment-only credentials, live-test command, and the rule that provider failures never produce PASS.

- [ ] **Step 2: Run complete verification**

```bash
uv run pytest -q
uv run python scripts/verify_course_pdfs.py
git diff --check
if git grep -n "SILICONFLOW_API_KEY=" -- ':!*.example'; then exit 1; fi
```

Expected: all default tests pass; live test is skipped without Key; four PDFs verify; no whitespace error; secret scan returns no matches.

- [ ] **Step 3: Commit documentation**

```bash
git add README.md docs/runtime-foundation.md
git commit -m "docs: explain stable agent verification"
```

## Explicitly deferred

- Gate 1–6 rubrics.
- Shared cross-device Registry.
- Coach and Diagnostician dialogue.
- Multi-model voting.
- OCR/PDF ingestion.
- Runtime Git writes.
- Automatic use of any credential supplied through chat.
