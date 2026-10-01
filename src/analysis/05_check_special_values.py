from pathlib import Path

import pandas as pd


DATA_PATH = Path(
    "data/analysis/loan_level/survival_loan_level.parquet"
)


df = pd.read_parquet(
    DATA_PATH,
    columns=[
        "credit_score",
        "original_ltv",
        "original_dti",
        "original_interest_rate",
        "original_loan_term",
        "default_event",
        "loan_age"
    ]
)


variables = [
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term"
]


# Chuyển sang numeric
for col in variables:
    df[col] = pd.to_numeric(df[col], errors="coerce")


print("\n===== ORIGINAL SAMPLE =====")
print("Total loans:", len(df))
print("Default:", df["default_event"].sum())


# Xác định các giá trị không có giá trị quan sát được
special_mask = (
    (df["credit_score"] == 9999)
    | (df["original_ltv"] == 999)
    | (df["original_dti"] == 999)
)


special_df = df[special_mask]


print("\n===== SPECIAL VALUE SAMPLE =====")
print("Loans affected:", len(special_df))
print("Defaults affected:", special_df["default_event"].sum())


print("\n===== SPECIAL VALUES BY VARIABLE =====")

for col, value in [
    ("credit_score", 9999),
    ("original_ltv", 999),
    ("original_dti", 999),
]:

    mask = df[col] == value

    print(
        f"{col} = {value}: "
        f"loans={mask.sum():,}, "
        f"defaults={df.loc[mask, 'default_event'].sum():,}"
    )


# Tạo dữ liệu sau khi chuyển mã đặc biệt thành missing
cox_df = df.copy()

cox_df.loc[cox_df["credit_score"] == 9999, "credit_score"] = pd.NA
cox_df.loc[cox_df["original_ltv"] == 999, "original_ltv"] = pd.NA
cox_df.loc[cox_df["original_dti"] == 999, "original_dti"] = pd.NA


# Chỉ kiểm tra, chưa lưu file
complete_mask = cox_df[variables].notna().all(axis=1)

complete_df = cox_df[complete_mask]


print("\n===== COX COMPLETE-CASE CHECK =====")
print("Loans remaining:", len(complete_df))
print("Defaults remaining:", complete_df["default_event"].sum())


print("\n===== REMOVED FROM COX =====")
print("Loans removed:", len(df) - len(complete_df))
print(
    "Defaults removed:",
    df["default_event"].sum() - complete_df["default_event"].sum()
)


print("\n===== DONE =====")