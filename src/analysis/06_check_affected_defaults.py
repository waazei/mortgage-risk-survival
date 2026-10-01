from pathlib import Path

import pandas as pd


DATA_PATH = Path(
    "data/analysis/loan_level/survival_loan_level.parquet"
)


df = pd.read_parquet(
    DATA_PATH,
    columns=[
        "loan_id",
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


# Chỉ lấy các khoản DEFAULT có DTI = 999
affected = df[
    (df["default_event"] == 1)
    & (df["original_dti"] == 999)
].copy()


print("\n===== AFFECTED DEFAULTS =====")
print("Number of defaults:", len(affected))


print("\n===== CREDIT SCORE =====")
print(affected["credit_score"].describe())


print("\n===== LTV =====")
print(affected["original_ltv"].describe())


print("\n===== DTI =====")
print(affected["original_dti"].describe())


print("\n===== INTEREST RATE =====")
print(affected["original_interest_rate"].describe())


print("\n===== LOAN TERM =====")
print(affected["original_loan_term"].describe())


print("\n===== LOAN AGE =====")
print(affected["loan_age"].describe())


print("\n===== OTHER SPECIAL VALUES =====")

for col, value in [
    ("credit_score", 9999),
    ("original_ltv", 999),
    ("original_dti", 999)
]:

    count = (affected[col] == value).sum()

    print(
        f"{col} = {value}: {count:,}"
    )


print("\n===== CREDIT SCORE DISTRIBUTION =====")
print(
    affected["credit_score"]
    .value_counts()
    .head(20)
)


print("\n===== LTV DISTRIBUTION =====")
print(
    affected["original_ltv"]
    .value_counts()
    .head(20)
)


print("\n===== INTEREST RATE DISTRIBUTION =====")
print(
    affected["original_interest_rate"]
    .value_counts()
    .head(20)
)


print("\n===== LOAN TERM DISTRIBUTION =====")
print(
    affected["original_loan_term"]
    .value_counts()
    .head(20)
)


print("\n===== LOAN AGE DISTRIBUTION =====")
print(
    affected["loan_age"]
    .value_counts()
    .sort_index()
    .head(50)
)


print("\n===== SAMPLE OF AFFECTED DEFAULTS =====")

print(
    affected[
        [
            "loan_id",
            "credit_score",
            "original_ltv",
            "original_dti",
            "original_interest_rate",
            "original_loan_term",
            "loan_age"
        ]
    ].head(20).to_string(index=False)
)


print("\n===== DONE =====")