# Repository README Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the repository README with a concise learner-facing course entry point.

**Architecture:** Keep `README.md` as navigation and orientation. Link to the
active week, prerequisite week, resources, task chain, Lab, and detailed course
documentation instead of duplicating their content.

**Tech Stack:** Markdown, Git, `uv`/pytest.

---

### Task 1: Rewrite the repository entry point

**Files:**
- Modify: `README.md`
- Reference: `docs/superpowers/specs/2026-07-17-repository-readme-redesign.md`
- Reference: `weeks/week-01/README.md`

- [x] Replace the current README with sections for capability, current entry,
  evidence-based learning loop, capability route, directory map, local commands,
  and scope.
- [x] Link the active Week 1 navigation, Week 0 prerequisite, normalized
  `resources/week-01/`, `tasks/week-01.md`, and `labs/week-01/` locations.
- [x] Keep detailed knowledge maps, task gates, and implementation answers out
  of the README.

### Task 2: Verify navigation and repository behavior

**Files:**
- Test: `README.md`
- Test: `labs/week-01/tests/test_week_01_smoke.py`

- [x] Run `git diff --check` and ensure no stale root `lab/` command is present
  in `README.md`.
- [x] Run `uv run pytest -q` and confirm all public smoke tests pass.
- [x] Confirm all README-local relative Markdown targets exist with a path check.

### Task 3: Publish the README update

**Files:**
- Modify: `README.md`
- Create: `docs/superpowers/plans/2026-07-17-repository-readme-redesign.md`

- [ ] Commit the README and plan with `docs: rewrite repository learning entry`.
- [ ] Push `codex/week-01-attention-layout-pr` and confirm PR #2 contains the
  README update.
