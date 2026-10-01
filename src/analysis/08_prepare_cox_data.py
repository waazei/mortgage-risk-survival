from pathlib import Path
import pandas as pd


# =========================================================
# 1. PATH
# =========================================================

DATA_PATH = Path(
    "data/analysis/loan_level/survival_loan_level.parquet"
)

OUTPUT_PATH = Path(
    "data/analysis/loan_level/cox_data.parquet"
)


# =========================================================
# 2. LOAD DATA
# =========================================================

columns = [
    "loan_id",
    "loan_age",
    "event_type",
    "cr_event",
    "default_event",
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term",
]

df = pd.read_parquet(
    DATA_PATH,
    columns=columns
)

print("===== ORIGINAL DATA =====")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())


# =========================================================
# 3. CONVERT DATA TYPES
# =========================================================

numeric_columns = [
    "loan_age",
    "default_event",
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term",
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# =========================================================
# 4. HANDLE SPECIAL VALUES
# =========================================================

# Credit Score = 9999 -> missing
df["credit_score_missing"] = (
    df["credit_score"] == 9999
)

df.loc[
    df["credit_score"] == 9999,
    "credit_score"
] = pd.NA


# Original LTV = 999 -> missing
df["ltv_missing"] = (
    df["original_ltv"] == 999
)

df.loc[
    df["original_ltv"] == 999,
    "original_ltv"
] = pd.NA


# DTI = 999 -> missing
df["dti_missing"] = (
    df["original_dti"] == 999
)

df.loc[
    df["original_dti"] == 999,
    "original_dti"
] = pd.NA


# =========================================================
# 5. IMPUTE MISSING VALUES
# =========================================================

# Median của các giá trị hợp lệ
credit_score_median = df["credit_score"].median()
ltv_median = df["original_ltv"].median()
dti_median = df["original_dti"].median()

print("\n===== MEDIAN VALUES =====")
print("Credit Score median:", credit_score_median)
print("LTV median:", ltv_median)
print("DTI median:", dti_median)


df["credit_score"] = (
    df["credit_score"]
    .fillna(credit_score_median)
)

df["original_ltv"] = (
    df["original_ltv"]
    .fillna(ltv_median)
)

df["original_dti"] = (
    df["original_dti"]
    .fillna(dti_median)
)


# =========================================================
# 6. CREATE MISSING INDICATORS
# =========================================================

df["credit_score_missing"] = (
    df["credit_score_missing"]
    .astype("int8")
)

df["ltv_missing"] = (
    df["ltv_missing"]
    .astype("int8")
)

df["dti_missing"] = (
    df["dti_missing"]
    .astype("int8")
)


# =========================================================
# 7. CHECK REMAINING MISSING VALUES
# =========================================================

print("\n===== MISSING AFTER PROCESSING =====")

check_columns = [
    "loan_age",
    "default_event",
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term",
]

print(df[check_columns].isna().sum())


# =========================================================
# 8. CHECK SPECIAL-VALUE COUNTS
# =========================================================

print("\n===== SPECIAL VALUE COUNTS =====")

print(
    "Credit Score missing:",
    df["credit_score_missing"].sum()
)

print(
    "LTV missing:",
    df["ltv_missing"].sum()
)

print(
    "DTI missing:",
    df["dti_missing"].sum()
)


# =========================================================
# 9. CHECK DEFAULTS
# =========================================================

print("\n===== DEFAULT COUNTS =====")

print(
    df["default_event"].value_counts()
)


print("\n===== DEFAULTS WITH SPECIAL VALUES =====")

print(
    "Credit Score missing + default:",
    (
        (df["credit_score_missing"] == 1)
        & (df["default_event"] == 1)
    ).sum()
)

print(
    "LTV missing + default:",
    (
        (df["ltv_missing"] == 1)
        & (df["default_event"] == 1)
    ).sum()
)

print(
    "DTI missing + default:",
    (
        (df["dti_missing"] == 1)
        & (df["default_event"] == 1)
    ).sum()
)


# =========================================================
# 10. SELECT COX VARIABLES
# =========================================================

cox_columns = [
    "loan_id",
    "loan_age",
    "event_type",
    "cr_event",
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

cox_df = df[cox_columns].copy()


# =========================================================
# 11. SAVE
# =========================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

cox_df.to_parquet(
    OUTPUT_PATH,
    index=False
)


# =========================================================
# 12. FINAL CHECK
# =========================================================

print("\n===== FINAL COX DATA =====")

print("Rows:", len(cox_df))
print("Columns:", cox_df.columns.tolist())

print("\nSaved to:")
print(OUTPUT_PATH)

print("\n===== DONE =====")
