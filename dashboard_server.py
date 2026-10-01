"""Serve the local mortgage survival dashboard and generated CSV results."""

from __future__ import annotations

import csv
import json
import mimetypes
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
RESULT_DIR = ROOT / "data" / "results"
LOAN_LEVEL_PATH = ROOT / "data" / "analysis" / "loan_level" / "survival_loan_level.parquet"
LOAN_FIELDS = [
    "loan_id", "loan_age", "monthly_reporting_period", "event_type", "event", "cr_event",
    "credit_score", "original_cltv", "original_dti", "original_ltv",
    "original_interest_rate", "original_loan_term", "current_interest_rate", "ltv",
]
HOST = "127.0.0.1"
PORT = 8765
LOAN_CACHE: dict[str, dict[str, object] | None] = {}


def read_csv(name: str) -> list[dict[str, str]]:
    path = RESULT_DIR / name
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def number(value: object) -> float | None:
    try:
        parsed = float(str(value))
        return parsed if parsed == parsed and abs(parsed) != float("inf") else None
    except (TypeError, ValueError):
        return None


def loan_samples() -> list[str]:
    if not LOAN_LEVEL_PATH.is_file():
        return []
    parquet = pq.ParquetFile(LOAN_LEVEL_PATH)
    if parquet.num_row_groups == 0:
        return []
    sample = parquet.read_row_group(0, columns=["loan_id"]).column("loan_id").slice(0, 5)
    return [str(value) for value in sample.to_pylist() if value is not None]


def find_loan(loan_id: str) -> dict[str, object] | None:
    if loan_id in LOAN_CACHE:
        return LOAN_CACHE[loan_id]
    if not LOAN_LEVEL_PATH.is_file():
        raise FileNotFoundError("Loan-level dataset is not available")

    parquet = pq.ParquetFile(LOAN_LEVEL_PATH)
    found_record: dict[str, object] | None = None
    for group_index in range(parquet.num_row_groups):
        offset = 0
        for batch in parquet.iter_batches(
            row_groups=[group_index], batch_size=524_288, columns=["loan_id"]
        ):
            ids = pc.cast(batch.column(0), pa.string())
            matches = pc.indices_nonzero(pc.equal(ids, loan_id))
            if len(matches):
                row_index = offset + matches[0].as_py()
                record = parquet.read_row_group(group_index, columns=LOAN_FIELDS).slice(row_index, 1).to_pylist()[0]
                found_record = {
                    key: (value.isoformat() if hasattr(value, "isoformat") else value)
                    for key, value in record.items()
                }
                break
            offset += batch.num_rows
        if found_record is not None:
            break

    LOAN_CACHE[loan_id] = found_record
    if len(LOAN_CACHE) > 32:
        LOAN_CACHE.pop(next(iter(LOAN_CACHE)))
    return found_record


def dashboard_data() -> dict[str, object]:
    cif = read_csv("cif_identity_check.csv")
    km = read_csv("kaplan_meier_summary.csv")
    default_model = read_csv("cause_specific_cox_default.csv")
    prepay_model = read_csv("cause_specific_cox_prepayment.csv")
    finegray_model = read_csv("fine_gray_default.csv")
    sensitivity_model = read_csv("cox_sensitivity_complete_case.csv")
    vintage_rows = read_csv("vintage_cif_summary.csv")
    vintage_curve_rows = read_csv("vintage_cif_curve.csv")
    quarterly_quality_rows = read_csv("time_varying_data_check.csv")
    ph_rows = read_csv("ph_assumption_summary.csv")
    audit_rows = read_csv("final_audit.csv")
    known_checks = {row.get("check") for row in audit_rows}
    methodology_gaps = [
        ("model:fine_gray_custom_convergence", "Existing Fine–Gray CSV has no saved optimizer-convergence metadata; rerun the estimator to record numerical fit diagnostics.", "numerical fit diagnostics"),
        ("method:fine_gray_external_validation", "Custom implementation has no saved comparison against cmprsk::crr or another validated reference.", "methodological validation"),
        ("model:time_varying_cox", "No fitted time-varying Cox result is present in the final outputs; quarterly data checks are not a model fit.", "model coverage"),
        ("study:out_of_sample_validation", "No temporal holdout, calibration, discrimination, or external validation report is present.", "research design"),
    ]
    for check, detail, scope in methodology_gaps:
        if check not in known_checks:
            audit_rows.append({"check": check, "passed": "", "status": "UNVERIFIED", "scope": scope, "detail": detail})
    coverage = sorted(
        period
        for p in (ROOT / "data" / "analysis").rglob("survival_*.parquet")
        if (period := p.stem.removeprefix("survival_")) and re.fullmatch(r"\d{4}Q[1-4]", period)
    )

    total_loans = None
    for row in audit_rows:
        if row.get("check") == "loan_level:unique_loan_id":
            match = re.search(r"([\d,]+) unique IDs", row.get("detail", ""))
            if match:
                total_loans = int(match.group(1).replace(",", ""))
            break

    default_count = int(number(default_model[0].get("events")) or 0) if default_model else 0
    prepay_count = int(number(prepay_model[0].get("events")) or 0) if prepay_model else 0
    audit_passed = sum(row.get("status", "").upper() == "PASS" or row.get("passed", "").lower() == "true" for row in audit_rows)
    audit_failed = sum(row.get("status", "").upper() == "FAIL" or row.get("passed", "").lower() == "false" for row in audit_rows)
    audit_unverified = sum(row.get("status", "").upper() == "UNVERIFIED" for row in audit_rows)

    return {
        "updated": max((p.stat().st_mtime for p in RESULT_DIR.glob("*.csv")), default=0),
        "summary": {
            "loans": total_loans,
            "defaults": default_count,
            "prepayments": prepay_count,
            "censored": max(0, (total_loans or 0) - default_count - prepay_count),
            "pd12": next((number(row.get("default_cif")) for row in cif if row.get("loan_age_month") == "12"), None),
            "pd60": next((number(row.get("default_cif")) for row in cif if row.get("loan_age_month") == "60"), None),
        },
        "cif": [
            {
                "month": int(number(row.get("loan_age_month")) or 0),
                "survival": number(row.get("survival")),
                "default": number(row.get("default_cif")),
                "prepayment": number(row.get("prepayment_cif")),
            }
            for row in cif
        ],
        "km": [
            {
                "month": int(number(row.get("LoanAge_Month")) or 0),
                "survival": number(row.get("Survival_Probability")),
            }
            for row in km
        ],
        "models": {
            "default": default_model,
            "prepayment": prepay_model,
            "finegray": finegray_model,
            "sensitivity": sensitivity_model,
        },
        "feature_stats": [
            {
                "variable": row.get("variable", ""),
                "mean": number(row.get("mean_original")),
                "std": number(row.get("std_original")),
            }
            for row in read_csv("cox_ph_default.csv")
        ],
        "quarterly_quality": [
            {
                "period": row.get("file", "").removeprefix("survival_").removesuffix(".parquet"),
                "rows": number(row.get("rows")),
                "loans": number(row.get("loans")),
                "missing_interest_rate": number(row.get("interest_rate_missing")),
                "missing_ltv": number(row.get("ltv_missing")),
                "duplicate_loan_age": number(row.get("duplicate_loan_age")),
                "min_loan_age": number(row.get("min_loan_age")),
                "max_loan_age": number(row.get("max_loan_age")),
            }
            for row in quarterly_quality_rows
        ],
        "vintage": [
            {
                "year": int(number(row.get("vintage_year")) or 0),
                "pd12": number(row.get("PD_12m_pct")),
                "prepayment12": number(row.get("Prepayment_CIF_12m_pct")),
                "survival12": (number(row.get("Survival_12m")) or 0) * 100,
                "pd24": number(row.get("PD_24m_pct")),
                "prepayment24": number(row.get("Prepayment_CIF_24m_pct")),
                "survival24": (number(row.get("Survival_24m")) or 0) * 100,
                "pd36": number(row.get("PD_36m_pct")),
                "prepayment36": number(row.get("Prepayment_CIF_36m_pct")),
                "survival36": (number(row.get("Survival_36m")) or 0) * 100,
                "pd60": number(row.get("PD_60m_pct")),
                "prepayment60": number(row.get("Prepayment_CIF_60m_pct")),
                "survival60": (number(row.get("Survival_60m")) or 0) * 100,
            }
            for row in vintage_rows
        ],
        "vintage_curve": [
            {
                "year": int(number(row.get("vintage_year")) or 0),
                "age": int(number(row.get("loan_age")) or 0),
                "at_risk": number(row.get("at_risk")),
                "default_events": number(row.get("default")),
                "prepayment_events": number(row.get("prepayment")),
                "survival": number(row.get("survival")),
                "default_cif": number(row.get("default_cif")),
                "prepayment_cif": number(row.get("prepayment_cif")),
            }
            for row in vintage_curve_rows
        ],
        "ph": [
            {
                "variable": row.get("variable", ""),
                "p": number(row.get("p_value")),
                "r2": number(row.get("r_squared")),
            }
            for row in ph_rows
        ],
        "audit": {
            "passed": audit_passed,
            "failed": audit_failed,
            "unverified": audit_unverified,
            "total": audit_passed + audit_failed,
            "checks": audit_rows,
        },
        "coverage": coverage,
        "downloads": [
            "competing_risks_cif_summary.csv",
            "cox_ph_default.csv",
            "cause_specific_cox_default.csv",
            "cause_specific_cox_prepayment.csv",
            "fine_gray_default.csv",
            "vintage_cif_summary.csv",
            "ph_assumption_summary.csv",
            "final_audit.csv",
        ],
    }


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = unquote(parsed_url.path)
        if path == "/api/dashboard":
            self.send_json(dashboard_data())
            return
        if path == "/api/loan-samples":
            try:
                self.send_json({"loan_ids": loan_samples()})
            except Exception as exc:
                self.send_json({"loan_ids": [], "error": str(exc)})
            return
        if path == "/api/loan":
            loan_id = parse_qs(parsed_url.query).get("loan_id", [""])[0].strip()
            if not loan_id or len(loan_id) > 40 or not re.fullmatch(r"[A-Za-z0-9_-]+", loan_id):
                self.send_json({"error": "Nhập một Loan ID hợp lệ."})
                return
            try:
                record = find_loan(loan_id)
                if record is None:
                    self.send_json({"error": "Không tìm thấy khoản vay có Loan ID này."})
                    return
                self.send_json({"loan": record})
            except Exception as exc:
                self.send_json({"error": f"Không thể tra cứu dữ liệu: {exc}"})
            return
        if path.startswith("/results/"):
            relative = Path(path.removeprefix("/results/"))
            target = (RESULT_DIR / relative).resolve()
            try:
                target.relative_to(RESULT_DIR.resolve())
            except ValueError:
                self.send_error(404, "Result figure not found")
                return
            if target.is_file() and target.suffix.lower() in {".png", ".svg", ".csv"}:
                body = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
                self.send_header("Content-Length", str(len(body)))
                if target.suffix.lower() == ".csv":
                    self.send_header("Content-Disposition", f'attachment; filename="{target.name}"')
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(404, "Result figure not found")
            return
        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def send_json(self, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    print(f"Mortgage risk dashboard: http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the local dashboard server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard server stopped.")
    finally:
        server.server_close()
