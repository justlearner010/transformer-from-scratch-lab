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
