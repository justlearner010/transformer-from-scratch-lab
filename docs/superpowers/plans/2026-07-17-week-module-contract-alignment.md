# Week Module Contract Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Week 0 and Week 1 conform to one reusable learning-module artifact contract.

**Architecture:** The Skill gains a generic cross-phase conformance gate. The
Transformer repository records its concrete contract in `docs/`, then migrates
Week 0 legacy artifacts and fills Week 1's missing standard sections without
changing either week's knowledge scope.

**Tech Stack:** Markdown, Git, `uv`/pytest.

---

### Task 1: Add cross-phase conformance to the reusable Skill

**Files:**
- Modify: `/Users/jay/Documents/Jay-Skill-Package/学习流程优化类/designing-engineering-learning-phases/SKILL.md`
- Modify: `/Users/jay/Documents/Jay-Skill-Package/学习流程优化类/designing-engineering-learning-phases/references/knowledge-to-task-model.md`
- Modify: `/Users/jay/Documents/Jay-Skill-Package/tests/designing-engineering-learning-phases/{scenarios,baseline,green}.md`

- [ ] Require a compatibility matrix that compares paths, granularity, names,
  required headings, links/commands, and evidence-record fields.
- [ ] Require canonical/legacy/incomplete/justified-variation classification
  before a new phase inherits a predecessor layout.
- [ ] Require a canonical artifact contract, migration/exception plan, and
  conformance gate in phase output; validate it against Scenario 5.

### Task 2: Record the Transformer module contract

**Files:**
- Create: `docs/week-module-contract.md`
- Modify: `docs/course-design.md`
- Modify: `docs/course-operating-system.md`

- [ ] Publish the exact Week artifact paths and required section roles from the
  approved design spec.
- [ ] Define optional PDFs and problem sets as supporting artifacts, not
  replacements for canonical resources.

### Task 3: Migrate Week 0 legacy artifacts

**Files:**
- Move: `resources/week-00.md` to `resources/week-00/materials.md`
- Create: `resources/week-00/pre-class.md`
- Create: `resources/week-00/exercises.md`
- Move and consolidate: `homework/week-00-*.md` into `resources/week-00/homework.md`
- Move: `notes/week-00-template.md` to `resources/week-00/notes-template.md`
- Modify: `tasks/week-00.md`, `weeks/week-00/README.md`, `labs/week-00/README.md`

- [ ] Preserve existing Week 0 learning questions, formal-PDF links, and Lab
  behavior while converting task steps to Gate 0…N and resource names to the
  canonical contract.
- [ ] Add the standard Week README and Lab README roles without duplicating the
  detailed resource content.

### Task 4: Fill Week 1 format gaps

**Files:**
- Modify: `weeks/week-01/README.md`
- Modify: `labs/week-01/README.md`
- Modify: `tasks/week-01.md`

- [ ] Preserve the Week 1 knowledge map and gates while adding any missing
  standard navigation, contract, post-Lab, and next-unlock sections.
- [ ] Keep all task/resource/Lab links on the same canonical names used by Week
  0 after migration.

### Task 5: Verify conformance and publish

**Files:**
- Test: `weeks/week-00/README.md`, `weeks/week-01/README.md`
- Test: `labs/week-00/README.md`, `labs/week-01/README.md`
- Test: `labs/week-00/tests/test_week_00_smoke.py`, `labs/week-01/tests/test_week_01_smoke.py`

- [ ] Check canonical paths, required headings, Gate naming, cross-links, and
  documented Lab commands for both weeks.
- [ ] Run `uv run pytest -q` and `git diff --check`.
- [ ] Commit and push the Skill and Transformer changes, then update their open
  PRs with the conformance result.
