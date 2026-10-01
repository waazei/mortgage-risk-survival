from pathlib import Path

import pandas as pd


STANDARDIZED_DIR = Path("data/standardized")
OUT_DIR = Path("data/analysis")


# ============================================================
# COLUMNS NEEDED FROM ORIGINATION DATA
# ============================================================

ORIG_COLUMNS = [
    "loan_id",
    "credit_score",
    "original_cltv",
    "original_dti",
    "original_ltv",
    "original_interest_rate",
    "original_loan_term",
]


# ============================================================
# COLUMNS NEEDED FROM PERFORMANCE DATA
# ============================================================

PERF_COLUMNS = [
    "loan_id",
    "monthly_reporting_period",
    "loan_age",
    "current_actual_upb",
    "current_delinquency_status",
    "current_interest_rate",
    "ltv",
    "zero_balance_code",
    "zero_balance_effective_date",
]


# ============================================================
# PROCESS ONE QUARTER
# ============================================================

def process_quarter(year, quarter):

    print(f"\nProcessing {year}Q{quarter}...")

    # ========================================================
    # 1. PATHS
    # ========================================================

    orig_path = (
        STANDARDIZED_DIR
        / str(year)
        / f"orig_{year}Q{quarter}.parquet"
    )

    perf_path = (
        STANDARDIZED_DIR
        / str(year)
        / f"perf_{year}Q{quarter}.parquet"
    )

    output_path = (
        OUT_DIR
        / f"survival_{year}Q{quarter}.parquet"
    )

    # ========================================================
    # 2. SKIP ALREADY COMPLETED QUARTER
    # ========================================================

    if output_path.exists():

        print(
            f"SKIP - already exists: {output_path}"
        )

        return

    # ========================================================
    # 3. READ ONLY REQUIRED COLUMNS
    # ========================================================

    orig = pd.read_parquet(
        orig_path,
        columns=ORIG_COLUMNS
    )

    perf = pd.read_parquet(
        perf_path,
        columns=PERF_COLUMNS
    )

    print(
        f"Origination rows: {len(orig):,}"
    )

    print(
        f"Performance rows: {len(perf):,}"
    )

    # ========================================================
    # 4. JOIN ORIGINATION + PERFORMANCE
    # ========================================================

    df = perf.merge(
        orig,
        on="loan_id",
        how="left",
        validate="many_to_one"
    )

    print(
        f"Joined rows: {len(df):,}"
    )

    # ========================================================
    # 5. RELEASE ORIGINAL DATAFRAMES
    # ========================================================
    #
    # Sau khi merge, orig và perf không còn cần thiết.
    # Xóa chúng để giải phóng RAM trước các bước tiếp theo.
    #

    del orig
    del perf

    # ========================================================
    # 6. CONVERT DATA TYPES
    # ========================================================

    df["loan_age"] = pd.to_numeric(
        df["loan_age"],
        errors="coerce"
    )

    df["monthly_reporting_period"] = pd.to_datetime(
        df["monthly_reporting_period"].astype(str),
        format="%Y%m",
        errors="coerce"
    )

    df["zero_balance_code"] = pd.to_numeric(
        df["zero_balance_code"],
        errors="coerce"
    )

    # ========================================================
    # 7. EVENT CODING
    # ========================================================
    #
    # 0 = Censored
    # 1 = Default
    # 2 = Voluntary Prepayment
    #
    # Freddie Mac Zero Balance Codes:
    #
    # 01 = Prepaid or Matured (Voluntary Payoff)
    # 02 = Third Party Sale
    # 03 = Short Sale or Charge Off
    # 09 = REO Disposition
    # 15 = Whole Loan Sale
    # 16 = Reperforming Loan Securitization
    # 96 = Defect prior to other termination event
    #
    # Theo framework nghiên cứu:
    #
    # Default = 02, 03, 09
    # Voluntary Prepayment = 01
    # Các trường hợp còn lại = Censored
    #

    df["event_type"] = "Censored"

    # Voluntary Prepayment
    df.loc[
        df["zero_balance_code"] == 1,
        "event_type"
    ] = "Voluntary Prepayment"

    # Default
    df.loc[
        df["zero_balance_code"].isin([2, 3, 9]),
        "event_type"
    ] = "Default"

    # ========================================================
    # 8. EVENT INDICATOR
    # ========================================================

    df["event"] = (
        df["event_type"] != "Censored"
    ).astype("int8")

    # Chuyển event_type sang category để giảm RAM
    df["event_type"] = (
        df["event_type"].astype("category")
    )

    # ========================================================
    # 9. RENAME / KEEP COLUMNS
    # ========================================================
    #
    # KHÔNG dùng:
    #
    # df = df[keep_columns]
    #
    # vì với 50-70 triệu dòng, pandas có thể phải tạo
    # một bản copy lớn và gây lỗi RAM.
    #
    # Thay vào đó, các cột không cần thiết đã được loại bỏ
    # ngay từ lúc đọc dữ liệu ở bước 3.
    #
    # Sau merge, chỉ còn các biến cần thiết.
    #

    # ========================================================
    # 10. DO NOT SORT
    # ========================================================
    #
    # Không sort loan_id + loan_age ở bước này.
    #
    # Việc sort 50-70 triệu dòng có thể tạo thêm nhiều GB
    # bộ nhớ tạm.
    #
    # Khi phân tích survival sau này, chúng ta sẽ sort/group
    # khi thực sự cần.
    #

    # ========================================================
    # 11. CREATE OUTPUT DIRECTORY
    # ========================================================

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # 12. SAVE PARQUET
    # ========================================================

    df.to_parquet(
        output_path,
        index=False
    )

    # ========================================================
    # 13. BASIC CHECK
    # ========================================================

    print("\nEvent counts:")

    print(
        df["event_type"].value_counts(
            dropna=False
        )
    )

    print(
        f"\nSaved: {output_path}"
    )

    # ========================================================
    # 14. RELEASE MEMORY
    # ========================================================

    del df


# ============================================================
# PROCESS ALL QUARTERS
# ============================================================

for year in range(2016, 2027):

    max_quarter = 1 if year == 2026 else 4

    for quarter in range(
        1,
        max_quarter + 1
    ):

        process_quarter(
            year,
            quarter
        )


print("\n====================================")
print("DONE - SURVIVAL DATASET CREATED")
print("====================================")