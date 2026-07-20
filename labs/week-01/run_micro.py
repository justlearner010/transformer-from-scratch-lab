"""Run the public check for exactly one editable Week 1 micro-lab."""
import argparse
from pathlib import Path
import subprocess
import sys


LABS = {
    "shape": "00-shape-trace",
    "score": "01-score-probe",
    "softmax": "02-stable-softmax",
    "value": "03-value-read",
    "projection": "04-qkv-projection",
    "compose": "compose",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="check one editable Week 1 micro-lab")
    parser.add_argument("name", choices=LABS)
    name = parser.parse_args().name
    check = Path(__file__).parent / "micro" / LABS[name] / "tests" / "checks.py"
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", "-q", str(check)]))


if __name__ == "__main__":
    main()
