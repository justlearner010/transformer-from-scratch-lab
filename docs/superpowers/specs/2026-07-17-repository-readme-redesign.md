# Repository README Redesign

## Goal

Make the repository README a concise entry point for a learner arriving for the
first time, while leaving detailed curriculum rules in `docs/` and individual
week navigation pages.

## Information architecture

1. State the observable capability the repository develops: explain, implement,
   and diagnose Transformer mechanisms.
2. Provide one immediate entry link to the active Week 1 phase and a separate
   Week 0 prerequisite link.
3. Show the capability sequence from matrix foundations through independent
   reconstruction without presenting a calendar schedule.
4. Explain the evidence-based learning loop and the boundary between public
   checks, local hidden grading, and learner-owned implementation.
5. Map the four artifact roles: `weeks/`, `resources/`, `tasks/`, and `labs/`.
6. Provide the minimal setup, public-test, and Week 1 grader commands.
7. State intended audience and non-goals to prevent an expectation of a
   production-scale model-training repository.

## Boundaries

- Do not duplicate the knowledge map, detailed course design, or individual
  exercise content already owned by `docs/` and `weeks/week-01/README.md`.
- Do not introduce claims that all future weeks or features already exist.
- Keep the README answer-free and avoid exposing hidden grader cases.

## Acceptance criteria

- A new learner can identify where to start, what evidence completes a week,
  and what each top-level learning artifact directory contains.
- The active Week 1 links and documented commands resolve to the normalized
  `resources/` and `labs/` locations.
- The README remains concise enough to act as navigation rather than a second
  course-design document.
