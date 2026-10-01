from pathlib import Path
import pandas as pd


DATA_PATH = Path(
    "data/analysis/loan_level/cox_data.parquet"
)


# =========================================================
# 1. LOAD DATA
# =========================================================

columns = [
    "loan_age",
    "default_event",
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term",
    "credit_score_missing",
    "ltv_missing",
    "dti_missing",
]

df = pd.read_parquet(
    DATA_PATH,
    columns=columns
)

print("===== COX DATA =====")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())


# =========================================================
# 2. EVENT CHECK
# =========================================================

print("\n===== EVENT =====")

print(
    df["default_event"].value_counts()
)

print(
    "\nDefault rate:",
    df["default_event"].mean()
)


# =========================================================
# 3. LOAN AGE
# =========================================================

print("\n===== LOAN AGE =====")

print(
    df["loan_age"].describe()
)


# =========================================================
# 4. PREDICTOR DISTRIBUTIONS
# =========================================================

predictors = [
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term",
]

print("\n===== PREDICTOR DISTRIBUTIONS =====")

for col in predictors:

    print("\n---", col, "---")

    print(
        df[col].describe()
    )


# =========================================================
# 5. CHECK EXTREME VALUES
# =========================================================

print("\n===== EXTREME VALUES =====")

for col in predictors:

    print("\n---", col, "---")

    print(
        "Min:",
        df[col].min()
    )

    print(
        "Max:",
        df[col].max()
    )

    print(
        "99%:",
        df[col].quantile(0.99)
    )

    print(
        "99.9%:",
        df[col].quantile(0.999)
    )


# =========================================================
# 6. CHECK MISSING INDICATORS
# =========================================================

print("\n===== MISSING INDICATORS =====")

missing_cols = [
    "credit_score_missing",
    "ltv_missing",
    "dti_missing",
]

for col in missing_cols:

    print(
        col,
        ":",
        df[col].sum()
    )


# =========================================================
# 7. DEFAULT BY MISSING INDICATOR
# =========================================================

print("\n===== DEFAULT RATE BY MISSING STATUS =====")

for col in missing_cols:

    print("\n---", col, "---")

    print(
        df.groupby(col)["default_event"]
        .agg(
            loans="count",
            defaults="sum",
            default_rate="mean"
        )
    )


# =========================================================
# 8. CHECK ZERO / NEGATIVE VALUES
# =========================================================

print("\n===== NON-POSITIVE VALUES =====")

for col in predictors:

    count = (
        df[col] <= 0
    ).sum()

    print(
        col,
        ":",
        count
    )


# =========================================================
# 9. CHECK DATA TYPES
# =========================================================

print("\n===== DATA TYPES =====")

print(
    df.dtypes
)


print("\n===== DONE =====")