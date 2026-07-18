from pathlib import Path
import os
import shutil
import subprocess
import sys

from course_pdf_targets import TARGETS


ROOT = Path(__file__).resolve().parents[1]


def build() -> None:
    tectonic = shutil.which("tectonic")
    if tectonic is None:
        raise SystemExit("tectonic is required to build course PDFs")

    build_env = os.environ.copy()
    build_env["SOURCE_DATE_EPOCH"] = "946684800"

    for target in TARGETS:
        source = ROOT / target.source
        output = ROOT / target.output
        if not source.exists():
            raise SystemExit(f"missing PDF source: {target.source}")
        subprocess.run(
            [tectonic, "--outdir", str(output.parent), str(source)],
            cwd=ROOT,
            env=build_env,
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
