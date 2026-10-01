from pathlib import Path
import zipfile
from io import BytesIO

import pandas as pd

from load_data import ORIG_COLUMNS, PERF_COLUMNS


RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/standardized")


ORIG_KEEP = [
    "loan_id",
    "credit_score",
    "first_payment_date",
    "original_cltv",
    "original_dti",
    "original_upb",
    "original_ltv",
    "original_interest_rate",
    "original_loan_term",
    "number_of_borrowers",
    "occupancy_status",
    "property_type",
    "loan_purpose",
    "property_state",
]

PERF_KEEP = [
    "loan_id",
    "monthly_reporting_period",
    "current_actual_upb",
    "current_delinquency_status",
    "loan_age",
    "remaining_months_to_maturity",
    "zero_balance_code",
    "zero_balance_effective_date",
    "current_interest_rate",
    "ltv",
]


def process_quarter(year, quarter):

    outer_path = (
        RAW_DIR
        / str(year)
        / f"historical_data_{year}.zip"
    )

    nested_name = f"historical_data_{year}Q{quarter}.zip"

    print(f"\nProcessing {year}Q{quarter}...")

    with zipfile.ZipFile(outer_path, "r") as outer_zip:

        nested_data = outer_zip.read(nested_name)

        with zipfile.ZipFile(
            BytesIO(nested_data), "r"
        ) as inner_zip:

            orig_file = f"orig_{year}Q{quarter}.txt"
            perf_file = f"perf_{year}Q{quarter}.txt"

            with inner_zip.open(orig_file) as f:
                orig = pd.read_csv(
                    f,
                    sep="|",
                    header=None,
                    names=ORIG_COLUMNS,
                    dtype=str,
                    usecols=ORIG_KEEP,
                )

            with inner_zip.open(perf_file) as f:
                perf = pd.read_csv(
                    f,
                    sep="|",
                    header=None,
                    names=PERF_COLUMNS,
                    dtype=str,
                    usecols=PERF_KEEP,
                )

    out_dir = OUT_DIR / str(year)
    out_dir.mkdir(parents=True, exist_ok=True)

    orig_path = out_dir / f"orig_{year}Q{quarter}.parquet"
    perf_path = out_dir / f"perf_{year}Q{quarter}.parquet"

    orig.to_parquet(orig_path, index=False)
    perf.to_parquet(perf_path, index=False)

    print(f"Origination: {orig.shape}")
    print(f"Performance: {perf.shape}")
    print(f"Saved: {out_dir}")


for year in range(2016, 2027):

    max_quarter = 1 if year == 2026 else 4

    for quarter in range(1, max_quarter + 1):

        process_quarter(year, quarter)

print("\nDONE - ALL QUARTERS")