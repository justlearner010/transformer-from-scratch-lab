# User-Friendly Course PDF Publication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish polished, reproducible Week 0 and Week 1 Learning Guide and Problem Set PDFs while preserving Markdown as the machine-readable and maintainable course source.

**Architecture:** Add one reusable LaTeX preamble, one explicit PDF target registry, and deterministic build/verification scripts. Existing Markdown, tasks, Labs, and graders remain course/runtime sources; the PDFs are derived student-facing artifacts. Week 1 becomes the first complete publication-contract implementation, while Week 0 is migrated to the same template and its current clipping defect is removed.

**Tech Stack:** Python 3.12 standard library, pytest, Tectonic/XeTeX, Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`), LaTeX with `fontspec`, XeTeX CJK line breaking, `hyperref`, `fancyhdr`, `enumitem`, and `amsmath`.

---

## Scope and file map

This plan is the publication subproject of the approved Self-Learning Runtime MVP. It does not implement the Runtime state machine, Agents, manifest, or Evidence Ledger.

**Create:**

- `pdf/course-preamble.tex` - shared A4 layout, fonts, colors, headings, links, headers, footers, question and checklist macros.
- `scripts/course_pdf_targets.py` - one registry for source PDF pairs and required visible titles.
- `scripts/build_course_pdfs.py` - compile every registered target with Tectonic.
- `scripts/verify_course_pdfs.py` - verify metadata, extracted text, page bounds, and render every page to PNG.
- `tests/publication/test_pdf_contract.py` - publication registry, source, and generated-artifact contract tests.
- `resources/week-01.tex` - Week 1 Learning Guide publication source.
- `problem-sets/week-01-problem-set.tex` - Week 1 answer-free Problem Set publication source.

**Modify:**

- `.gitignore` - ignore rendered QA images under `tmp/pdfs/`.
- `pyproject.toml` - include `tests/` in pytest discovery.
- `resources/week-00.tex` - use the shared template and add Gate/evidence navigation.
- `problem-sets/week-00-problem-set.tex` - use the shared template and replace clipping-prone layout.
- `resources/week-01/materials.md` - align precise public resource ranges with the Learning Guide.
- `README.md` - expose PDFs as the primary student-facing downloads and Markdown as accessible/source alternatives.
- `docs/problem-set-pdf-design.md` - define the two-PDF publication contract and QA gate.

**Regenerate and track:**

- `resources/week-00.pdf`
- `problem-sets/week-00-problem-set.pdf`
- `resources/week-01.pdf`
- `problem-sets/week-01-problem-set.pdf`

## Task 1: Lock the publication contract with failing tests

**Files:**

- Create: `scripts/course_pdf_targets.py`
- Create: `tests/publication/test_pdf_contract.py`
- Modify: `pyproject.toml`
- Modify: `.gitignore`

- [ ] **Step 1: Extend pytest discovery and ignore rendered QA images**

Change `pyproject.toml` to:

```toml
[tool.pytest.ini_options]
testpaths = ["labs", "tests"]
pythonpath = ["."]
```

Append this exact rule to `.gitignore`:

```gitignore
tmp/pdfs/
```

- [ ] **Step 2: Create the explicit target registry**

Create `scripts/course_pdf_targets.py`:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PdfTarget:
    source: Path
    output: Path
    required_titles: tuple[str, ...]


TARGETS = (
    PdfTarget(
        Path("resources/week-00.tex"),
        Path("resources/week-00.pdf"),
        ("Week 0 Learning Guide", "先看懂信息怎样流动"),
    ),
    PdfTarget(
        Path("problem-sets/week-00-problem-set.tex"),
        Path("problem-sets/week-00-problem-set.pdf"),
        ("Week 0 Problem Set", "Part A"),
    ),
    PdfTarget(
        Path("resources/week-01.tex"),
        Path("resources/week-01.pdf"),
        ("Week 1 Learning Guide", "Attention 如何按内容读取信息"),
    ),
    PdfTarget(
        Path("problem-sets/week-01-problem-set.tex"),
        Path("problem-sets/week-01-problem-set.pdf"),
        ("Week 1 Problem Set", "Part A"),
    ),
)
```

- [ ] **Step 3: Write failing publication-contract tests**

Create `tests/publication/test_pdf_contract.py`:

```python
from pathlib import Path

from scripts.course_pdf_targets import TARGETS


ROOT = Path(__file__).resolve().parents[2]


def test_every_pdf_target_has_a_unique_source_and_output() -> None:
    sources = [target.source for target in TARGETS]
    outputs = [target.output for target in TARGETS]
    assert len(sources) == len(set(sources))
    assert len(outputs) == len(set(outputs))


def test_every_pdf_source_uses_the_shared_preamble() -> None:
    for target in TARGETS:
        source = ROOT / target.source
        assert source.exists(), f"missing source: {target.source}"
        text = source.read_text(encoding="utf-8")
        assert r"\input{../pdf/course-preamble.tex}" in text


def test_publication_outputs_use_stable_paths() -> None:
    assert {str(target.output) for target in TARGETS} == {
        "resources/week-00.pdf",
        "resources/week-01.pdf",
        "problem-sets/week-00-problem-set.pdf",
        "problem-sets/week-01-problem-set.pdf",
    }
```

- [ ] **Step 4: Run the test and verify it fails for the missing shared template and Week 1 sources**

Run:

```bash
uv run pytest tests/publication/test_pdf_contract.py -v
```

Expected: `test_every_pdf_source_uses_the_shared_preamble` fails and identifies `resources/week-01.tex` as missing.

- [ ] **Step 5: Commit the red contract test**

```bash
git add .gitignore pyproject.toml scripts/course_pdf_targets.py tests/publication/test_pdf_contract.py
git commit -m "test: define course PDF publication contract"
```

## Task 2: Add the reusable PDF template and build command

**Files:**

- Create: `pdf/course-preamble.tex`
- Create: `scripts/build_course_pdfs.py`
- Modify: `resources/week-00.tex`
- Modify: `problem-sets/week-00-problem-set.tex`

- [ ] **Step 1: Create the shared preamble**

Create `pdf/course-preamble.tex` with:

```tex
\usepackage[margin=20mm,headheight=15pt]{geometry}
\usepackage{amsmath,amssymb,mathtools}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{fontspec}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{titlesec}
\setmainfont{Arial Unicode MS}
\setmonofont{Menlo}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip = 0pt plus 1pt
\definecolor{CourseNavy}{HTML}{172554}
\definecolor{CourseBlue}{HTML}{1D4ED8}
\definecolor{CourseSlate}{HTML}{475569}
\hypersetup{
  colorlinks=true,
  linkcolor=CourseBlue,
  urlcolor=CourseBlue,
  pdftitle={Transformer From Scratch Lab},
  pdfauthor={Transformer From Scratch Lab}
}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.65em}
\setlength{\emergencystretch}{3em}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{CourseSlate}Transformer From Scratch Lab}
\fancyhead[R]{\small\color{CourseSlate}\PublicationLabel}
\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{CourseBlue}}{}{0pt}{}
\titleformat{\subsection}{\large\bfseries\color{CourseNavy}}{}{0pt}{}
\newcommand{\CourseCover}[4]{%
  \thispagestyle{empty}
  \begin{center}
  {\large\color{CourseSlate}Transformer From Scratch Lab\par}
  \vspace{12mm}
  {\Huge\bfseries\color{CourseNavy}#1\par}
  \vspace{4mm}
  {\Large #2\par}
  \vspace{14mm}
  \begin{minipage}{0.88\textwidth}
  \textbf{本周能力}\quad #3\par
  \vspace{3mm}
  \textbf{完成后解锁}\quad #4
  \end{minipage}
  \end{center}
  \vfill
  \begin{center}\small\color{CourseSlate}Evidence-gated, answer-free learning\end{center}
  \newpage
}
\newcommand{\Gate}[2]{\subsection*{#1}\textbf{通过证据：} #2\par}
\newcommand{\AnswerSpace}[1]{\par\vspace*{#1}}
\newcommand{\ChecklistItem}[1]{\item[$\square$] #1}
```

Every source must define `\PublicationLabel` before the shared preamble is loaded.

- [ ] **Step 2: Migrate both Week 0 sources to the shared preamble**

For each Week 0 source:

1. Keep `\documentclass[11pt,a4paper]{article}`.
2. Replace duplicated package, font, color, geometry, header, and macro declarations with:

```tex
\newcommand{\PublicationLabel}{Week 0 Learning Guide}
\input{../pdf/course-preamble.tex}
```

or:

```tex
\newcommand{\PublicationLabel}{Week 0 Problem Set}
\input{../pdf/course-preamble.tex}
```

3. Replace the handwritten title block with `\CourseCover`.
4. Replace the Problem Set's clipping-prone submission/checklist `tabular` with:

```tex
\begin{itemize}[leftmargin=8mm]
\ChecklistItem{Part A 与 Part B 已在 Lab 前完成。}
\ChecklistItem{Shape Checker 的公开与 hidden tests 已通过。}
\ChecklistItem{Part C 引用了自己的 Lab 证据。}
\ChecklistItem{已记录一个真实错误或主动注入错误的诊断过程。}
\ChecklistItem{能闭卷画出 Week 0 到 Week 1 的信息流。}
\end{itemize}
```

- [ ] **Step 3: Add the deterministic build script**

Create `scripts/build_course_pdfs.py`:

```python
from pathlib import Path
import shutil
import subprocess
import sys

from course_pdf_targets import TARGETS


ROOT = Path(__file__).resolve().parents[1]


def build() -> None:
    tectonic = shutil.which("tectonic")
    if tectonic is None:
        raise SystemExit("tectonic is required to build course PDFs")

    for target in TARGETS:
        source = ROOT / target.source
        output = ROOT / target.output
        if not source.exists():
            raise SystemExit(f"missing PDF source: {target.source}")
        subprocess.run(
            [tectonic, "--outdir", str(output.parent), str(source)],
            cwd=ROOT,
            check=True,
        )
        if not output.exists() or output.stat().st_size == 0:
            raise SystemExit(f"PDF was not generated: {target.output}")
        print(f"built {target.output}")


if __name__ == "__main__":
    try:
        build()
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)
```

- [ ] **Step 4: Run the contract test again**

Run:

```bash
uv run pytest tests/publication/test_pdf_contract.py -v
```

Expected: still FAIL only because the two Week 1 TeX sources do not exist.

- [ ] **Step 5: Compile the Week 0 sources directly and confirm the CJK line wraps**

Run:

```bash
tectonic --outdir resources resources/week-00.tex
tectonic --outdir problem-sets problem-sets/week-00-problem-set.tex
```

Expected: both commands exit `0` and rewrite the corresponding PDFs.

- [ ] **Step 6: Commit the shared publication foundation**

```bash
git add pdf/course-preamble.tex scripts/build_course_pdfs.py resources/week-00.tex resources/week-00.pdf problem-sets/week-00-problem-set.tex problem-sets/week-00-problem-set.pdf
git commit -m "feat: add shared course PDF template"
```

## Task 3: Create the Week 1 Learning Guide

**Files:**

- Create: `resources/week-01.tex`
- Modify: `resources/week-01/materials.md`

- [ ] **Step 1: Normalize Week 1 resource scope in Markdown**

Update `resources/week-01/materials.md` so the public resource list has these four bounded entries:

1. DeepLearning.AI Transformers in Practice: only the Q/K/V, scaled dot-product attention, and softmax lessons; the student records the visible lesson title because login-specific lesson numbering can vary.
2. D2L Queries, Keys, and Values: definitions and attention-pooling intuition, no implementation copying.
3. D2L Attention Scoring Functions: dot-product scoring, scaling, and masked softmax portions relevant to single-head attention.
4. Attention Is All You Need section 3.2.1: formula, scaling rationale, and value-weighted output; skip multi-head and block sections.

Every entry must keep the table fields `精确范围`, `带着的问题读`, and `完成证据`.

- [ ] **Step 2: Create the Week 1 Learning Guide source**

Create `resources/week-01.tex` with this fixed content contract:

1. Define `\PublicationLabel` as `Week 1 Learning Guide`, load the shared preamble,
   and use `\CourseCover` with the approved capability and causal-mask unlock text.
2. `开始之前` reproduces the closed-book Week 0 shape bridge from
   `resources/week-01/pre-class.md` and states that a learner who cannot explain
   `K.T` returns to Week 0.
3. `本周路线` lists Gate 0-6 from `tasks/week-01.md`, including the rollback
   target and one observable evidence item for every Gate.
4. `精确阅读材料` contains all four normalized entries from Step 1 with their
   actual URLs, bounded reading ranges, reading questions, and completion evidence.
5. `进入 Lab 前的证据` requires the Q/K/V shape table, score-row explanation,
   stable-softmax extreme input, axis counterexample, and `weights @ V` prediction.
6. `Lab 与提示协议` includes the exact commands
   `uv run pytest labs/week-01/tests -v` and
   `uv run python labs/week-01/run_grade.py`, plus the existing first-, second-,
   and third-failure rules from `labs/week-01/README.md`.
7. `完成与提交清单` requires all P0 checks, one real or seeded failure, a
   3-5 minute closed-book explanation, and the independent attention inspector.
8. End the document after the checklist; do not include solutions, hidden inputs,
   expected hidden outputs, or implementation code.

- [ ] **Step 3: Compile the Learning Guide**

Run:

```bash
tectonic --outdir resources resources/week-01.tex
```

Expected: exit `0` and create `resources/week-01.pdf`.

- [ ] **Step 4: Run the publication contract test**

Run:

```bash
uv run pytest tests/publication/test_pdf_contract.py -v
```

Expected: only the missing Week 1 Problem Set source still fails.

- [ ] **Step 5: Commit the Week 1 Learning Guide**

```bash
git add resources/week-01/materials.md resources/week-01.tex resources/week-01.pdf
git commit -m "feat: publish Week 1 learning guide PDF"
```

## Task 4: Create the Week 1 Problem Set

**Files:**

- Create: `problem-sets/week-01-problem-set.tex`
- Create: `problem-sets/week-01-problem-set.pdf`

- [ ] **Step 1: Author the answer-free Problem Set source**

Create `problem-sets/week-01-problem-set.tex` using the shared preamble and this fixed progression:

```text
Cover: capability, Week 0 prerequisite, submissions, no-answer rule
Part A: Q/K/V and shape bridge
Part B: score semantics, transpose, and scaling
Part C: stable row-wise softmax and axis counterexample
Part D: weights @ V and full attention data flow
Part E: post-Lab contract, boundary, and seeded-failure diagnosis
Independent transfer: attention inspector predictions and observations
Closed-book check and submission checklist
```

Every Part must include visible dependency labels, evidence requirements, and adequate `\AnswerSpace` for written work. The PDF must not include reference implementations, hidden inputs, expected hidden outputs, or solutions.

- [ ] **Step 2: Compile the Problem Set**

Run:

```bash
tectonic --outdir problem-sets problem-sets/week-01-problem-set.tex
```

Expected: exit `0` and create `problem-sets/week-01-problem-set.pdf`.

- [ ] **Step 3: Run the contract test and all public tests**

Run:

```bash
uv run pytest tests/publication/test_pdf_contract.py -v
uv run pytest -q
```

Expected: publication tests pass; full suite passes.

- [ ] **Step 4: Commit the Week 1 Problem Set**

```bash
git add problem-sets/week-01-problem-set.tex problem-sets/week-01-problem-set.pdf
git commit -m "feat: publish Week 1 problem set PDF"
```

## Task 5: Add automated PDF verification and visual QA output

**Files:**

- Create: `scripts/verify_course_pdfs.py`
- Modify: `tests/publication/test_pdf_contract.py`

- [ ] **Step 1: Extend contract tests to require built artifacts**

Add:

```python
def test_every_pdf_output_exists_and_is_not_empty() -> None:
    for target in TARGETS:
        output = ROOT / target.output
        assert output.exists(), f"missing output: {target.output}"
        assert output.stat().st_size > 10_000, f"unexpectedly small: {target.output}"
```

- [ ] **Step 2: Create metadata, text, bounds, and rendering verification**

Create `scripts/verify_course_pdfs.py` with functions that:

1. Require `pdfinfo`, `pdftotext`, and `pdftoppm` via `shutil.which`.
2. Run `pdfinfo` and require A4 page size plus at least two pages.
3. Run `pdftotext -layout` and require every target's `required_titles`.
4. Run `pdftotext -bbox`, parse XHTML with `xml.etree.ElementTree`, and reject any word whose coordinates are outside its page by more than one point.
5. Remove only the target-specific render directory under `tmp/pdfs/`, recreate it using the PDF output filename stem, and run `pdftoppm -png -r 140` for every page.
6. Print the rendered directory and page count for human visual inspection.

Use this exact public entry point:

```python
def main() -> None:
    for target in TARGETS:
        verify_target(target)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run build and automated verification**

Run:

```bash
uv run python scripts/build_course_pdfs.py
uv run python scripts/verify_course_pdfs.py
```

Expected: all four PDFs build; all metadata/text/bounds checks pass; four render directories are reported.

- [ ] **Step 4: Inspect every rendered page**

Open every PNG under:

```text
tmp/pdfs/week-00/
tmp/pdfs/week-00-problem-set/
tmp/pdfs/week-01/
tmp/pdfs/week-01-problem-set/
```

Reject publication for clipped text, overlapping lines, black squares, unreadable formulas, orphan headings, dense pages without visual hierarchy, excessive blank pages, or answer spaces split from their questions.

- [ ] **Step 5: Fix source layout and repeat build, automated verification, and complete visual inspection**

Run the two scripts after every correction. Do not reuse renders from a prior build.

- [ ] **Step 6: Commit verification tooling**

```bash
git add scripts/verify_course_pdfs.py tests/publication/test_pdf_contract.py
git commit -m "test: verify rendered course PDFs"
```

## Task 6: Make PDFs the primary public course entry

**Files:**

- Modify: `README.md`
- Modify: `docs/problem-set-pdf-design.md`

- [ ] **Step 1: Add a public learning-material table to README**

Add a section after `从这里开始`:

```markdown
## 正式学习材料

| 阶段 | Learning Guide | Problem Set | 代码 Lab |
| --- | --- | --- | --- |
| Week 0 | [PDF](resources/week-00.pdf) | [PDF](problem-sets/week-00-problem-set.pdf) | [Lab](labs/week-00/README.md) |
| Week 1 | [PDF](resources/week-01.pdf) | [PDF](problem-sets/week-01-problem-set.pdf) | [Lab](labs/week-01/README.md) |

PDF 是面向学习者的正式版本；`weeks/`、`resources/week-XX/` 和 `tasks/`
保留为可访问、可维护且供 Learning Runtime 读取的课程源。
```

- [ ] **Step 2: Update the PDF design document**

Document:

- Learning Guide and Problem Set responsibilities;
- Markdown/YAML as source and PDF as derived publication;
- stable paths and naming;
- shared template and build command;
- render and bounds QA gate;
- solutions released separately after completion;
- Week 0 legacy migration and Week 1 reference status.

- [ ] **Step 3: Verify README links and publication consistency**

Run:

```bash
test -s resources/week-00.pdf
test -s resources/week-01.pdf
test -s problem-sets/week-00-problem-set.pdf
test -s problem-sets/week-01-problem-set.pdf
rg -n 'resources/week-0[01]\.pdf|problem-sets/week-0[01]-problem-set\.pdf' README.md
uv run pytest -q
uv run python scripts/verify_course_pdfs.py
git diff --check
```

Expected: four files are nonempty, four README links are present, all tests and PDF checks pass, and the diff check emits no errors.

- [ ] **Step 4: Commit the public entry points**

```bash
git add README.md docs/problem-set-pdf-design.md
git commit -m "docs: make course PDFs the public learning entry"
```

## Task 7: Final completion audit

**Files:** no new files.

- [ ] **Step 1: Run the complete build and test suite from a clean generated state**

Run:

```bash
uv run python scripts/build_course_pdfs.py
uv run pytest -q
uv run python scripts/verify_course_pdfs.py
git diff --check
```

Expected: four PDFs build, all tests pass, all automated PDF checks pass, and no whitespace errors are reported.

- [ ] **Step 2: Inspect all latest rendered PNGs and record page counts**

Inspect every rendered page, not only covers. Record the page count for each PDF in the completion report and report any accepted layout tradeoff explicitly.

- [ ] **Step 3: Confirm repository boundaries**

Run:

```bash
git status --short
git diff --submodule=log
```

Expected: `homework_answer/` remains untracked and untouched; only publication-plan files and generated PDFs belong to this work.

- [ ] **Step 4: Commit any final source/PDF synchronization corrections**

If Step 2 required corrections:

```bash
git add pdf scripts tests resources problem-sets README.md docs/problem-set-pdf-design.md pyproject.toml .gitignore
git commit -m "fix: finalize user-friendly course PDFs"
```

If there are no corrections, do not create an empty commit.
