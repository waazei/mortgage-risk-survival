import pandas as pd

path = "data/analysis/loan_level/cox_data.parquet"

cols = [
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term"
]

df = pd.read_parquet(path, columns=cols + ["default_event"])

for col in cols:
    print("\n==============================")
    print(col)
    print("==============================")

    print("Unique:", df[col].nunique())
    print("Min:", df[col].min())
    print("Max:", df[col].max())

    print("\nTop values:")
    print(df[col].value_counts().head(15))

print("\n===== EXTREME LTV =====")
print(
    df[df["original_ltv"] > 150]
    ["original_ltv"]
    .value_counts()
    .sort_index()
    .head(50)
)

print("\n===== EXTREME LOAN TERM =====")
print(
    df[df["original_loan_term"] > 360]
    ["original_loan_term"]
    .value_counts()
    .sort_index()
)

print("\n===== EXTREME CREDIT SCORE =====")
print(
    df[df["credit_score"] < 600]
    ["credit_score"]
    .value_counts()
    .sort_index()
)

print("\n===== DONE =====")