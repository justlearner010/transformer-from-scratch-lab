# Self-Learning Runtime Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic Week 1 Runtime foundation that validates the course manifest, persists an append-only learning history, enforces legal Gate transitions, and exposes `start`, `next`, `submit`, `status`, and `resume` through a local CLI.

**Architecture:** The course manifest is read-only configuration; the JSONL ledger is the audit truth; learner state is reconstructed from events; and only the state machine may apply transitions. This first sub-project deliberately excludes LLM calls and grader interpretation so the state and policy boundary can be tested before Coach, Diagnostician, and Evidence Collector are connected.

**Tech Stack:** Python 3.12+, dataclasses, enums, PyYAML, argparse, JSONL, pytest, uv.

---

## File map

- `learning_runtime/schemas.py`: shared immutable manifest, state, event, and evaluation types.
- `learning_runtime/manifest.py`: YAML loading plus field, path, ID, dependency, and rollback validation.
- `learning_runtime/storage/event_ledger.py`: append-only JSONL writes, reads, and corruption detection.
- `learning_runtime/storage/learner_state.py`: deterministic replay from events to the cached learner view.
- `learning_runtime/state_machine.py`: legal transition table and transition-event creation.
- `learning_runtime/policies.py`: P0 evidence and failure-route decisions.
- `learning_runtime/coordinator.py`: one-action student-facing projection of state and manifest.
- `learning_runtime/cli.py`: local command entry point; no student-code mutation or hidden-grader access.
- `course-manifests/week-01.yaml`: machine contract referencing existing Week 1 course files.
- `tests/learning_runtime/`: unit and end-to-end coverage for the deterministic foundation.

### Task 1: Package and CLI contract

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `.gitignore`
- Create: `learning_runtime/__init__.py`
- Create: `learning_runtime/cli.py`
- Create: `tests/learning_runtime/test_cli.py`

- [ ] **Step 1: Write the failing CLI test**

```python
from learning_runtime.cli import build_parser


def test_cli_exposes_foundation_commands() -> None:
    parser = build_parser()
    for command in ("start", "next", "submit", "status", "resume"):
        suffix = ["week-01"] if command == "start" else []
        if command == "submit":
            suffix = ["--gate", "week-01-gate-0"]
        args = parser.parse_args([command, *suffix])
        assert args.command == command
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_cli.py -q`
Expected: FAIL because `learning_runtime.cli` does not exist.

- [ ] **Step 3: Add the package entry point and private state path**

Add `pyyaml>=6.0` to project dependencies, add `learning-os = "learning_runtime.cli:main"` under `[project.scripts]`, enable uv package installation with explicit `learning_runtime*` package discovery, add `.learning-os/` to `.gitignore`, and implement an argparse parser with the five commands. `submit` must require `--gate`.

- [ ] **Step 4: Verify GREEN and lock dependencies**

Run: `uv lock && uv sync --group dev && uv run pytest tests/learning_runtime/test_cli.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .gitignore pyproject.toml uv.lock learning_runtime tests/learning_runtime/test_cli.py
git commit -m "feat: add learning runtime CLI package"
```

### Task 2: Manifest schema and Week 1 contract

**Files:**
- Create: `learning_runtime/schemas.py`
- Create: `learning_runtime/manifest.py`
- Create: `course-manifests/week-01.yaml`
- Create: `tests/learning_runtime/test_manifest.py`

- [ ] **Step 1: Write failing manifest tests**

Test that `load_manifest(ROOT / "course-manifests/week-01.yaml", ROOT)` returns seven unique Gate IDs, references `tasks/week-01.md`, and accepts `week-00-review` as an explicit external rollback target. Add fixtures proving that duplicate Gate IDs, missing artifact paths, cyclic dependencies, and unknown rollback targets raise `ManifestError` containing the offending value.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_manifest.py -q`
Expected: FAIL because the loader and manifest are missing.

- [ ] **Step 3: Implement immutable manifest types and validation**

Define `EvidenceRequirement`, `GateDefinition`, and `CourseManifest` frozen dataclasses. Load YAML with `yaml.safe_load`; require the top-level contract from the design; resolve every artifact and external rollback reference against the repository root; detect duplicate IDs and dependency cycles; and reject a rollback target not found in either Gate IDs or `failure_routes`.

- [ ] **Step 4: Create the Week 1 manifest**

Encode Gates 0–6 from `tasks/week-01.md`, using repository-relative source paths, P0 evidence requirements, allowed hint levels `[0, 1, 2, 3]`, explicit failure routes, `resources/week-01.pdf` and `problem-sets/week-01-problem-set.pdf` as learner publications, and `causal-mask` as the next capability. Do not copy lesson prose or answers.

- [ ] **Step 5: Verify GREEN**

Run: `uv run pytest tests/learning_runtime/test_manifest.py -q`
Expected: all manifest tests PASS.

- [ ] **Step 6: Commit**

```bash
git add learning_runtime/schemas.py learning_runtime/manifest.py course-manifests/week-01.yaml tests/learning_runtime/test_manifest.py
git commit -m "feat: define Week 1 runtime manifest"
```

### Task 3: Append-only Event Ledger and replay

**Files:**
- Create: `learning_runtime/storage/__init__.py`
- Create: `learning_runtime/storage/event_ledger.py`
- Create: `learning_runtime/storage/learner_state.py`
- Create: `tests/learning_runtime/test_event_ledger.py`
- Create: `tests/learning_runtime/test_learner_state.py`

- [ ] **Step 1: Write failing ledger tests**

Cover sequential `event-0001` IDs, immutable prior lines after append, `evidence_refs` preservation, an empty ledger, and `LedgerCorruptionError(line_number=2)` when the final JSONL line is malformed.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_event_ledger.py -q`
Expected: FAIL because the ledger is missing.

- [ ] **Step 3: Implement Event and EventLedger**

Use UTF-8 JSONL. Each append writes one complete JSON object with `event_id`, `event_type`, `occurred_at`, `payload`, and `evidence_refs`, flushes it, and calls `os.fsync`. Reads never truncate or repair malformed history.

- [ ] **Step 4: Verify ledger GREEN**

Run: `uv run pytest tests/learning_runtime/test_event_ledger.py -q`
Expected: PASS.

- [ ] **Step 5: Write failing replay tests**

Test that `session_started` creates an active Gate 0 state, `attempt_submitted` increments attempts and sets `evidence_pending`, and `transition_applied` changes the Gate/status while preserving verified evidence IDs and last event ID.

- [ ] **Step 6: Implement `replay_state(events)`**

Reject a stream whose first event is not `session_started`. Apply only known state-bearing event types and return an immutable `LearnerState`; observational events remain in the ledger without mutating state.

- [ ] **Step 7: Verify replay GREEN and commit**

Run: `uv run pytest tests/learning_runtime/test_event_ledger.py tests/learning_runtime/test_learner_state.py -q`
Expected: PASS.

```bash
git add learning_runtime/storage tests/learning_runtime/test_event_ledger.py tests/learning_runtime/test_learner_state.py
git commit -m "feat: persist and replay learning events"
```

### Task 4: State machine and policy boundary

**Files:**
- Create: `learning_runtime/state_machine.py`
- Create: `learning_runtime/policies.py`
- Create: `tests/learning_runtime/test_state_machine.py`
- Create: `tests/learning_runtime/test_policies.py`

- [ ] **Step 1: Write failing state-machine tests**

Prove `active -> evidence_pending -> evaluating` is legal; `active -> passed` is rejected; PASS advances to the next Gate; the final Gate unlocks the next capability; and every transition event includes the decision plus evidence references.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_state_machine.py -q`
Expected: FAIL because `LearningStateMachine` is missing.

- [ ] **Step 3: Implement the transition table**

Represent statuses with `GateStatus`. Raise `IllegalTransition` before creating an event. Only `transition_applied` events may change Gate status; no Coach or policy method receives a writable state object.

- [ ] **Step 4: Verify state-machine GREEN**

Run: `uv run pytest tests/learning_runtime/test_state_machine.py -q`
Expected: PASS.

- [ ] **Step 5: Write failing policy tests**

Cover: all required criteria passed -> PASS; one mapped P0 failure -> REINFORCE; an ambiguous diagnostic failure -> DIAGNOSE; any `insufficient_evidence`, conflicting evidence, or unknown failure route -> ESCALATE. Assert `unknown` never equals `failed`.

- [ ] **Step 6: Implement `PolicyEngine.decide`**

Return a frozen `TransitionDecision` with recommendation, target Gate, failed node, reason, evidence refs, policy result, and one next action. The engine must reject a requested PASS if any required criterion lacks independent evidence.

- [ ] **Step 7: Verify GREEN and commit**

Run: `uv run pytest tests/learning_runtime/test_state_machine.py tests/learning_runtime/test_policies.py -q`
Expected: PASS.

```bash
git add learning_runtime/state_machine.py learning_runtime/policies.py tests/learning_runtime/test_state_machine.py tests/learning_runtime/test_policies.py
git commit -m "feat: enforce evidence-gated transitions"
```

### Task 5: Coordinator and working local session

**Files:**
- Create: `learning_runtime/coordinator.py`
- Modify: `learning_runtime/cli.py`
- Create: `tests/learning_runtime/test_coordinator.py`
- Create: `tests/learning_runtime/test_end_to_end_foundation.py`

- [ ] **Step 1: Write failing coordinator tests**

Assert the coordinator returns exactly one action with `current_capability`, `current_gate`, `reason`, `action`, `checks`, `hint_level`, and `evidence_index`; it must not expose `.grader/`, solutions, expected outputs, or a complete implementation.

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/learning_runtime/test_coordinator.py -q`
Expected: FAIL because the coordinator is missing.

- [ ] **Step 3: Implement the deterministic coordinator**

Map the active Gate to its manifest task reference and evidence requirements. Emit one action only. The coordinator reads manifest plus replayed state and has no method for changing state or writing learner artifacts.

- [ ] **Step 4: Write the failing end-to-end CLI test**

In a temporary runtime directory, run `start week-01`, `status`, `next`, `submit --gate week-01-gate-0`, and `resume`. Assert an events file is created, status is restored from the ledger, submit leaves the state at `evidence_pending`, and a second `start` refuses to overwrite the session.

- [ ] **Step 5: Implement CLI session commands**

Use `.learning-os/events.jsonl` by default and allow a test-only `--runtime-dir`. `start` validates the manifest before writing. `submit` requires the current Gate and only records an attempt; it does not infer pass/fail. `resume` and `status` replay the ledger. `next` prints the coordinator contract in Chinese.

- [ ] **Step 6: Verify GREEN and commit**

Run: `uv run pytest tests/learning_runtime/test_coordinator.py tests/learning_runtime/test_end_to_end_foundation.py -q`
Expected: PASS.

```bash
git add learning_runtime/coordinator.py learning_runtime/cli.py tests/learning_runtime/test_coordinator.py tests/learning_runtime/test_end_to_end_foundation.py
git commit -m "feat: run a local evidence-gated session"
```

### Task 6: Documentation and full verification

**Files:**
- Modify: `README.md`
- Create: `docs/runtime-foundation.md`

- [ ] **Step 1: Document the boundary**

Add a README section with `uv run learning-os start week-01`, `next`, `submit`, `status`, and `resume`. State explicitly that this foundation records attempts but cannot yet verify Lab evidence or diagnose failures; those are the next sub-project.

- [ ] **Step 2: Document data ownership and recovery**

Explain manifest (read-only rules), student artifacts (user-owned), `.learning-os/events.jsonl` (private audit truth), replay behavior, corruption stop behavior, and why PDF is not a Runtime input.

- [ ] **Step 3: Run the complete verification suite**

Run:

```bash
uv run pytest -q
uv run python scripts/verify_course_pdfs.py
uv run learning-os start week-01 --runtime-dir /tmp/learning-os-foundation-check
uv run learning-os next --runtime-dir /tmp/learning-os-foundation-check
git diff --check
```

Expected: all tests pass; four PDFs verify; the CLI returns one Week 1 Gate action; no tracked `.learning-os/` state exists.

- [ ] **Step 4: Commit**

```bash
git add README.md docs/runtime-foundation.md
git commit -m "docs: explain runtime foundation workflow"
```

## Deferred to the next sub-project

- Evidence Collector command allowlist and artifact hashes.
- Public-test and hidden-grader adapters.
- Criterion-level Verifier and seeded failure fixtures.
- Coach hint ladder and Diagnostician recommendation schema.
- Real PASS, REINFORCE, DIAGNOSE, and ESCALATE CLI submissions.
- Multi-Agent versus modular single-Agent baseline experiment.

This deferral is intentional: the foundation must first prove that state cannot be advanced by conversation, missing evidence, or an Agent recommendation.
