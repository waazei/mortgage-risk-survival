import pandas as pd
from pathlib import Path


path = Path(
    "data/analysis/survival_2016Q1.parquet"
)

print("Reading:", path)

df = pd.read_parquet(
    path,
    columns=[
        "loan_id",
        "monthly_reporting_period",
        "loan_age",
        "current_interest_rate",
        "ltv",
        "event_type",
    ]
)

print("\n===== BASIC =====")
print("Rows:", len(df))
print("Loans:", df["loan_id"].nunique())


# ============================================================
# DUPLICATE LOAN + LOAN AGE
# ============================================================

dup_mask = df.duplicated(
    subset=["loan_id", "loan_age"],
    keep=False
)

dup = df.loc[
    dup_mask
].sort_values(
    ["loan_id", "loan_age", "monthly_reporting_period"]
)

print("\n===== DUPLICATE LOAN + LOAN AGE =====")

print(
    "Duplicate rows:",
    len(dup)
)

print(
    "Affected loans:",
    dup["loan_id"].nunique()
)


# ============================================================
# SHOW EXAMPLES
# ============================================================

print("\n===== EXAMPLES =====")

print(
    dup.head(50).to_string(index=False)
)


# ============================================================
# CHECK DUPLICATE LOAN + REPORTING DATE
# ============================================================

dup_date = df.duplicated(
    subset=[
        "loan_id",
        "monthly_reporting_period"
    ],
    keep=False
)

print(
    "\nDuplicate loan + reporting date:",
    dup_date.sum()
)


# ============================================================
# CHECK SAME LOAN AGE BUT DIFFERENT REPORTING DATE
# ============================================================

if len(dup) > 0:

    example_loan = dup.iloc[0]["loan_id"]

    print(
        "\n===== ONE LOAN IN DETAIL ====="
    )

    loan_detail = df[
        df["loan_id"] == example_loan
    ].sort_values(
        "monthly_reporting_period"
    )

    print(
        loan_detail.to_string(index=False)
    )


print("\n===== DONE =====")