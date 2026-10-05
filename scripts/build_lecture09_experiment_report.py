#!/usr/bin/env python3
"""Build the consolidated report, optionally regenerating its saved-data assets."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "instructor-materials/lecture-plans/lecture09-representation-experiment"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-assets", action="store_true",
                        help="regenerate tables/figures and replay the two displayed initial runs")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/pdf/lecture09-benign-overfitting-report.pdf")
    args = parser.parse_args()
    if not (SOURCE / "report.tex").exists():
        parser.error("Clone mathforai26-instructor into instructor-materials first (see the replication README).")
    if shutil.which("latexmk") is None:
        parser.error("Install a TeX distribution with latexmk, PGFPlots, standalone, fvextra, and xurl.")
    env = os.environ.copy()
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env[name] = "1"
    if args.refresh_assets:
        commands = [
            ["lecture09_nn_report_assets.py", "--activation", "tanh"],
            ["lecture09_nn_report_assets.py", "--activation", "relu"],
            ["lecture09_representation_report_assets.py"],
            ["lecture09_followup_report_assets.py"],
            ["lecture09_auxiliary_report_assets.py"],
        ]
        for script, *options in commands:
            subprocess.run([sys.executable, str(ROOT / "scripts" / script), *options],
                           cwd=ROOT, env=env, check=True)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lecture09-report-") as temporary:
        subprocess.run(
            ["latexmk", "-norc", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
             f"-outdir={temporary}", "report.tex"],
            cwd=SOURCE, env=env, check=True,
        )
        log = (Path(temporary) / "report.log").read_text(errors="replace")
        warnings = [line for line in log.splitlines()
                    if any(term in line for term in
                           ("Overfull", "undefined references", "undefined citations", "LaTeX Warning:"))]
        if warnings:
            raise RuntimeError("Resolve final-build warnings before delivery:\n" + "\n".join(warnings))
        shutil.copy2(Path(temporary) / "report.pdf", output)
    print(f"Built {output}")


if __name__ == "__main__":
    main()
