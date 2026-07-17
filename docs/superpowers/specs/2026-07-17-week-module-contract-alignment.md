# Week Module Contract Alignment

## Goal

Make every learning week a comparable module. A learner should be able to find
the same artifact roles, names, navigation shape, runnable Lab entry point, and
evidence template regardless of the mechanism taught that week.

## Canonical artifact contract

```text
weeks/week-XX/README.md
resources/week-XX/pre-class.md
resources/week-XX/materials.md
resources/week-XX/exercises.md
resources/week-XX/homework.md
resources/week-XX/notes-template.md
tasks/week-XX.md
labs/week-XX/README.md
labs/week-XX/run_grade.py
labs/week-XX/src/
labs/week-XX/tests/
```

Formal PDFs, solution material, and learner-owned answers remain optional
supporting artifacts. They do not replace a canonical module artifact.

## Required content contracts

| Artifact | Required structure |
| --- | --- |
| Week README | why now, capability question, prior evidence and scope, dependency/importance view, ordered entry links, completion rule, next unlock |
| Pre-class | prior-knowledge retrieval or an explicit first-week readiness check, with an entry condition |
| Materials | exact source range, questions, and completion evidence |
| Exercises | named Gates before Lab, each with task and unlock condition |
| Homework | post-Lab engineering reflection, evidence requirement, submission rule |
| Notes template | knowledge update, failure record, transfer prediction, next-step decision |
| Task chain | `Gate 0…N` sequence that points to resource and Lab artifacts |
| Lab README | why now, gates, constraints/contracts, run and feedback, post-Lab evidence |

Headings may add mechanism-specific detail but may not omit the required role.

## Migration decisions

- Week 0 is legacy: its combined resource file and separate `homework/` and
  `notes/` artifacts are migrated into `resources/week-00/`; its task list is
  expressed as Gate 0…N; and its Lab README gains the same required sections as
  Week 1.
- Week 1 is partially canonical: its directory layout and Gate chain remain;
  its Week README and Lab README gain the missing standard role sections.
- Existing Week 0 PDFs and problem-set files stay where they are, with updated
  links from canonical resources when relevant.

## Verification

The alignment is complete only when both weeks have the canonical artifact
paths, required headings, valid cross-links, matching Lab entry-point commands,
and equivalent evidence-record roles. Content depth and mechanism-specific
sections may differ; unexplained artifact-format differences may not.
