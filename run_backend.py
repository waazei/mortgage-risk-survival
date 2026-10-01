"""Run the reproducible data and survival-analysis pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable

STAGES = {
    "survival": ["src/data/build_survival_dataset.py"],
    "loan-level": ["src/data/build_loan_level.py"],
    "models": [
        "src/analysis/08_prepare_cox_data.py",
        "src/analysis/01_kaplan_meier.py",
        "src/analysis/02_competing_risks.py",
        "src/analysis/03_cause_specific_cox.py",
        "src/analysis/12_cox_ph_full.py",
        "src/analysis/13_check_ph_assumption.py",
        "src/analysis/19_check_cif_identity.py",
        "src/analysis/20_fine_gray_default.py",
        "src/analysis/21_vintage_analysis.py",
        "src/analysis/22_sensitivity_cox.py",
        "src/analysis/23_final_audit.py",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage",
        choices=["survival", "loan-level", "models", "all"],
        help="Run quarter survival files, aggregate loans, estimate models, or all stages in order.",
    )
    args = parser.parse_args()
    sequence = ["survival", "loan-level", "models"] if args.stage == "all" else [args.stage]

    for stage in sequence:
        for relative_script in STAGES[stage]:
            script = ROOT / relative_script
            if not script.is_file():
                print(f"Required script not found: {script}", file=sys.stderr)
                return 2
            print(f"\n{'=' * 72}\nRunning {relative_script}\n{'=' * 72}", flush=True)
            completed = subprocess.run([PYTHON, str(script)], cwd=ROOT, check=False)
            if completed.returncode:
                print(f"Stopped: {relative_script} exited with code {completed.returncode}.", file=sys.stderr)
                return completed.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
