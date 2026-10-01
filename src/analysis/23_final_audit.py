"""Validate generated artifacts and core event coding for the project."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "data" / "results"
LOAN_PATH = ROOT / "data" / "analysis" / "loan_level" / "survival_loan_level.parquet"
REQUIRED_RESULTS = [
    "kaplan_meier_summary.csv",
    "competing_risks_cif_summary.csv",
    "cox_ph_default.csv",
    "cause_specific_cox_default.csv",
    "cause_specific_cox_prepayment.csv",
    "ph_assumption_summary.csv",
    "cif_identity_check.csv",
    "fine_gray_default.csv",
    "vintage_cif_summary.csv",
    "vintage_cif_curve.csv",
    "cox_sensitivity_complete_case.csv",
    "kaplan_meier_curve.png",
    "competing_risks_cif.png",
    "vintage_default_cif.png",
]


def main() -> int:
    checks: list[dict[str, object]] = []

    def record(name: str, passed: bool | None, detail: str, scope: str = "artifact/data integrity") -> None:
        status = "UNVERIFIED" if passed is None else ("PASS" if passed else "FAIL")
        checks.append({"check": name, "passed": "" if passed is None else bool(passed),
                       "status": status, "scope": scope, "detail": detail})
        print(f"{status} | {name} | {detail}")

    for filename in REQUIRED_RESULTS:
        path = RESULT_DIR / filename
        record(f"result:{filename}", path.is_file() and path.stat().st_size > 0,
               "present and non-empty" if path.is_file() and path.stat().st_size > 0 else "missing or empty")

    for filename in ("cause_specific_cox_default.csv", "cause_specific_cox_prepayment.csv"):
        path = RESULT_DIR / filename
        if path.is_file() and path.stat().st_size > 0:
            model = pd.read_csv(path)
            has_values = {"coefficient", "hazard_ratio_per_1_sd", "se", "converged"}.issubset(model.columns)
            finite = has_values and np.isfinite(
                model[["coefficient", "hazard_ratio_per_1_sd", "se"]].to_numpy(dtype=float)
            ).all()
            valid = bool(
                finite
                and model["converged"].astype(bool).all()
                and (model["se"] > 0).all()
                and (model["hazard_ratio_per_1_sd"] > 0).all()
                and (model["coefficient"].abs() < 5).all()
            )
            record(f"model:{filename}", valid, "finite, converged estimates with plausible standardized coefficients")

    finegray_path = RESULT_DIR / "fine_gray_default.csv"
    if finegray_path.is_file() and finegray_path.stat().st_size > 0:
        finegray = pd.read_csv(finegray_path)
        convergence_fields = {"converged", "coefficient", "SE", "HR", "CI_lower_95", "CI_upper_95"}
        if convergence_fields.issubset(finegray.columns):
            finite = np.isfinite(finegray[["coefficient", "SE", "HR", "CI_lower_95", "CI_upper_95"]].to_numpy(dtype=float)).all()
            valid = bool(finite and finegray["converged"].astype(bool).all() and (finegray["SE"] > 0).all()
                         and (finegray["HR"] > 0).all() and (finegray["CI_lower_95"] > 0).all()
                         and (finegray["CI_upper_95"] >= finegray["CI_lower_95"]).all())
            record("model:fine_gray_custom_convergence", valid,
                   "optimizer convergence and finite positive Wald intervals; this is not external validation",
                   "numerical fit diagnostics")
        else:
            record("model:fine_gray_custom_convergence", None,
                   "Existing result lacks saved convergence metadata; rerun the Fine–Gray script to record fit status.",
                   "numerical fit diagnostics")

    if LOAN_PATH.is_file():
        loan = pd.read_parquet(LOAN_PATH, columns=["loan_id", "loan_age", "event_type", "event", "cr_event"])
        event = pd.to_numeric(loan["event"], errors="coerce")
        competing = pd.to_numeric(loan["cr_event"], errors="coerce")
        valid_event = loan["event_type"].notna() & event.isin([0, 1]) & competing.isin([0, 1, 2])
        consistent = (
            ((loan["event_type"] == "Censored") & (event == 0) & (competing == 0))
            | ((loan["event_type"] == "Default") & (event == 1) & (competing == 1))
            | ((loan["event_type"] == "Voluntary Prepayment") & (event == 1) & (competing == 2))
        )
        record("loan_level:unique_loan_id", loan["loan_id"].is_unique,
               f"{loan['loan_id'].nunique():,} unique IDs / {len(loan):,} rows")
        record("loan_level:valid_time", pd.to_numeric(loan["loan_age"], errors="coerce").notna().all()
               and (pd.to_numeric(loan["loan_age"], errors="coerce") >= 0).all(), "loan_age is numeric and non-negative")
        record("loan_level:event_codes", valid_event.all(), "event in {0,1}; cr_event in {0,1,2}")
        record("loan_level:event_consistency", consistent.all(), "event_type, event, and cr_event agree")
        print("\nEvent counts:\n", loan["event_type"].value_counts(dropna=False).to_string())
    else:
        record("loan_level:dataset", False, f"missing: {LOAN_PATH}")

    cif_path = RESULT_DIR / "cif_identity_check.csv"
    if cif_path.is_file():
        cif = pd.read_csv(cif_path)
        required = {"difference_from_1"}
        if required.issubset(cif.columns) and len(cif):
            max_gap = float(np.abs(cif["difference_from_1"]).max())
            record("cif:identity", np.isfinite(max_gap) and max_gap < 0.01,
                   f"maximum |S + CIF_default + CIF_prepayment - 1| = {max_gap:.6g} (tolerance 0.01)")
        else:
            record("cif:identity", False, "identity result has no usable difference_from_1 values")

    # Keep evidence gaps visible without presenting them as failed data-integrity
    # checks or allowing a structurally clean pipeline to imply methodological validation.
    record("method:fine_gray_external_validation", None,
           "Custom implementation has no saved comparison against cmprsk::crr or another validated reference.",
           "methodological validation")
    record("model:time_varying_cox", None,
           "No fitted time-varying Cox result is present in the final outputs; quarterly data checks are not a model fit.",
           "model coverage")
    record("study:out_of_sample_validation", None,
           "No temporal holdout, calibration, discrimination, or external validation report is present.",
           "research design")

    audit_path = RESULT_DIR / "final_audit.csv"
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(checks).to_csv(audit_path, index=False)
    failed = sum(item["status"] == "FAIL" for item in checks)
    unverified = sum(item["status"] == "UNVERIFIED" for item in checks)
    passed = sum(item["status"] == "PASS" for item in checks)
    print(f"\nAudit: {passed} PASS, {failed} FAIL, {unverified} UNVERIFIED. Report: {audit_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
