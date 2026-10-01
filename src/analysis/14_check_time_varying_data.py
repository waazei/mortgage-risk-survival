import pandas as pd
from pathlib import Path


BASE_PATH = Path("data/analysis")

files = sorted(
    BASE_PATH.glob("survival_*.parquet")
)

print("===== TIME-VARYING DATA CHECK =====")
print("Number of files:", len(files))

all_stats = []

for i, path in enumerate(files, start=1):

    print("\n====================================")
    print(path.name)
    print("====================================")

    df = pd.read_parquet(
        path,
        columns=[
            "loan_id",
            "loan_age",
            "monthly_reporting_period",
            "current_interest_rate",
            "ltv",
            "event",
            "event_type",
        ]
    )

    print("Rows:", len(df))
    print("Loans:", df["loan_id"].nunique())

    # --------------------------------------------------------
    # BASIC
    # --------------------------------------------------------

    print("\nLoan age:")
    print(
        df["loan_age"].describe()
    )

    # --------------------------------------------------------
    # CURRENT INTEREST RATE
    # --------------------------------------------------------

    print("\nCurrent Interest Rate:")
    print(
        df["current_interest_rate"].describe()
    )

    print(
        "Missing:",
        df["current_interest_rate"].isna().sum()
    )

    # --------------------------------------------------------
    # CURRENT LTV
    # --------------------------------------------------------

    print("\nCurrent LTV:")
    print(
        df["ltv"].describe()
    )

    print(
        "Missing:",
        df["ltv"].isna().sum()
    )

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    print("\nEvents:")
    print(
        df["event_type"].value_counts()
    )

    # --------------------------------------------------------
    # CHECK DUPLICATE LOAN-AGE
    # --------------------------------------------------------

    duplicate = (
        df.duplicated(
            subset=[
                "loan_id",
                "loan_age"
            ]
        ).sum()
    )

    print(
        "\nDuplicate loan-age rows:",
        duplicate
    )

    # --------------------------------------------------------
    # CHECK TIME ORDER
    # --------------------------------------------------------

    sample = (
        df.sort_values(
            ["loan_id", "loan_age"]
        )
        .groupby("loan_id")
        .head(100)
    )

    # --------------------------------------------------------
    # SAVE SUMMARY
    # --------------------------------------------------------

    all_stats.append({
        "file": path.name,
        "rows": len(df),
        "loans": df["loan_id"].nunique(),
        "interest_rate_missing":
            df["current_interest_rate"].isna().sum(),
        "ltv_missing":
            df["ltv"].isna().sum(),
        "duplicate_loan_age":
            duplicate,
        "min_loan_age":
            df["loan_age"].min(),
        "max_loan_age":
            df["loan_age"].max(),
    })


# ============================================================
# SUMMARY
# ============================================================

summary = pd.DataFrame(
    all_stats
)

print("\n\n====================================")
print("OVERALL SUMMARY")
print("====================================")

print(summary)

output = Path(
    "data/results/time_varying_data_check.csv"
)

output.parent.mkdir(
    parents=True,
    exist_ok=True
)

summary.to_csv(
    output,
    index=False
)

print(
    "\nSaved:",
    output
)

print("\n===== DONE =====")