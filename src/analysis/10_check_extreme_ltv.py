import pandas as pd

path = "data/analysis/loan_level/cox_data.parquet"

df = pd.read_parquet(
    path,
    columns=[
        "loan_age",
        "default_event",
        "original_ltv",
        "original_dti",
        "credit_score",
        "original_interest_rate",
        "original_loan_term"
    ]
)

print("===== LTV > 100 =====")
x = df[df["original_ltv"] > 100]

print("Loans:", len(x))
print("Defaults:", x["default_event"].sum())

print("\n===== LTV > 150 =====")
x = df[df["original_ltv"] > 150]

print("Loans:", len(x))
print("Defaults:", x["default_event"].sum())

print("\n===== LTV > 200 =====")
x = df[df["original_ltv"] > 200]

print("Loans:", len(x))
print("Defaults:", x["default_event"].sum())

print("\n===== LTV > 300 =====")
x = df[df["original_ltv"] > 300]

print("Loans:", len(x))
print("Defaults:", x["default_event"].sum())

print("\n===== TOP 20 LTV =====")
print(
    df.nlargest(20, "original_ltv")[
        [
            "loan_age",
            "default_event",
            "original_ltv",
            "original_dti",
            "credit_score",
            "original_interest_rate",
            "original_loan_term"
        ]
    ]
)

print("\n===== DONE =====")