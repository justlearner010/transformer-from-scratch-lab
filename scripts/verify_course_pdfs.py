from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

from course_pdf_targets import PdfTarget, TARGETS


ROOT = Path(__file__).resolve().parents[1]
RENDER_ROOT = ROOT / "tmp" / "pdfs"
PAGE_SIZE_PATTERN = re.compile(
    r"Page size:\s+([0-9.]+) x ([0-9.]+) pts"
)
PAGE_COUNT_PATTERN = re.compile(r"Pages:\s+(\d+)")


def require_tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is not None:
        return executable

    if name == "pdftotext":
        pdftoppm = shutil.which("pdftoppm")
        if pdftoppm is not None:
            wrapper = Path(pdftoppm)
            candidates = (
                wrapper.with_name("pdftotext"),
                wrapper.parents[2]
                / "native"
                / "poppler"
                / "poppler"
                / "bin"
                / "pdftotext",
            )
            for candidate in candidates:
                if candidate.is_file() and candidate.stat().st_mode & 0o111:
                    return str(candidate)

    raise SystemExit(f"{name} is required to verify course PDFs")


def run_text(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def verify_metadata(pdf: Path, pdfinfo: str) -> int:
    metadata = run_text([pdfinfo, str(pdf)])
    page_count_match = PAGE_COUNT_PATTERN.search(metadata)
    page_size_match = PAGE_SIZE_PATTERN.search(metadata)
    if page_count_match is None or page_size_match is None:
        raise SystemExit(f"unable to read page metadata: {pdf.relative_to(ROOT)}")

    page_count = int(page_count_match.group(1))
    width = float(page_size_match.group(1))
    height = float(page_size_match.group(2))
    if page_count < 2:
        raise SystemExit(f"expected at least two pages: {pdf.relative_to(ROOT)}")
    if abs(width - 595.28) > 1 or abs(height - 841.89) > 1:
        raise SystemExit(
            f"expected A4 pages, got {width} x {height}: {pdf.relative_to(ROOT)}"
        )
    return page_count


def verify_required_text(
    pdf: Path, target: PdfTarget, pdftotext: str
) -> None:
    extracted = run_text([pdftotext, "-layout", str(pdf), "-"])
    for title in target.required_titles:
        if title not in extracted:
            raise SystemExit(
                f"missing required text {title!r}: {pdf.relative_to(ROOT)}"
            )


def verify_word_bounds(pdf: Path, pdftotext: str) -> None:
    bbox_path = RENDER_ROOT / f"{pdf.stem}-bbox.xhtml"
    bbox_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [pdftotext, "-bbox", str(pdf), str(bbox_path)],
        cwd=ROOT,
        check=True,
    )

    root = ET.parse(bbox_path).getroot()
    pages = root.findall(".//{*}page")
    if not pages:
        raise SystemExit(f"no bbox pages extracted: {pdf.relative_to(ROOT)}")

    violations: list[str] = []
    tolerance = 1.0
    for page_number, page in enumerate(pages, start=1):
        width = float(page.attrib["width"])
        height = float(page.attrib["height"])
        for word in page.findall(".//{*}word"):
            x_min = float(word.attrib["xMin"])
            y_min = float(word.attrib["yMin"])
            x_max = float(word.attrib["xMax"])
            y_max = float(word.attrib["yMax"])
            if (
                x_min < -tolerance
                or y_min < -tolerance
                or x_max > width + tolerance
                or y_max > height + tolerance
            ):
                violations.append(
                    f"page {page_number}: {word.text!r} "
                    f"({x_min}, {y_min}, {x_max}, {y_max})"
                )
    bbox_path.unlink()
    if violations:
        details = "\n".join(violations[:10])
        raise SystemExit(
            f"text outside page bounds in {pdf.relative_to(ROOT)}:\n{details}"
        )


def render_pages(pdf: Path, pdftoppm: str) -> Path:
    render_dir = RENDER_ROOT / pdf.stem
    if render_dir.exists():
        shutil.rmtree(render_dir)
    render_dir.mkdir(parents=True)
    subprocess.run(
        [pdftoppm, "-png", "-r", "140", str(pdf), str(render_dir / "page")],
        cwd=ROOT,
        check=True,
    )
    if not list(render_dir.glob("page-*.png")):
        raise SystemExit(f"no pages rendered: {pdf.relative_to(ROOT)}")
    return render_dir


def verify_target(
    target: PdfTarget, *, pdfinfo: str, pdftotext: str, pdftoppm: str
) -> None:
    pdf = ROOT / target.output
    if not pdf.exists() or pdf.stat().st_size == 0:
        raise SystemExit(f"missing PDF: {target.output}")

    page_count = verify_metadata(pdf, pdfinfo)
    verify_required_text(pdf, target, pdftotext)
    verify_word_bounds(pdf, pdftotext)
    render_dir = render_pages(pdf, pdftoppm)
    print(
        f"verified {target.output}: {page_count} pages; "
        f"renders at {render_dir.relative_to(ROOT)}"
    )


def main() -> None:
    pdfinfo = require_tool("pdfinfo")
    pdftotext = require_tool("pdftotext")
    pdftoppm = require_tool("pdftoppm")
    for target in TARGETS:
        verify_target(
            target,
            pdfinfo=pdfinfo,
            pdftotext=pdftotext,
            pdftoppm=pdftoppm,
        )


if __name__ == "__main__":
    main()
