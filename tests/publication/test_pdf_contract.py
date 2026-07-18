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


def test_every_pdf_output_exists_and_is_not_empty() -> None:
    for target in TARGETS:
        output = ROOT / target.output
        assert output.exists(), f"missing output: {target.output}"
        assert output.stat().st_size > 10_000, f"unexpectedly small: {target.output}"


def test_pdf_builds_use_a_reproducible_timestamp() -> None:
    build_script = (ROOT / "scripts/build_course_pdfs.py").read_text(
        encoding="utf-8"
    )
    assert 'build_env["SOURCE_DATE_EPOCH"] = "946684800"' in build_script
