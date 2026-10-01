from pathlib import Path

import pandas as pd


DATA_PATH = Path(
    "data/analysis/loan_level/survival_loan_level.parquet"
)


df = pd.read_parquet(
    DATA_PATH,
    columns=[
        "original_dti",
        "default_event"
    ]
)


df["original_dti"] = pd.to_numeric(
    df["original_dti"],
    errors="coerce"
)


# Xác định DTI missing theo mã Freddie Mac
df["dti_missing"] = (
    df["original_dti"] == 999
)


print("\n===== TOTAL SAMPLE =====")
print("Total loans:", len(df))
print("Total defaults:", df["default_event"].sum())


print("\n===== DTI MISSING =====")

print(
    df["dti_missing"].value_counts()
)


print("\n===== DTI MISSING BY EVENT =====")

table = pd.crosstab(
    df["default_event"],
    df["dti_missing"]
)

print(table)


print("\n===== DTI MISSING RATE =====")

summary = (
    df.groupby("default_event")["dti_missing"]
      .mean()
      .mul(100)
)

print(summary)


print("\n===== DEFAULT RATE =====")

default_rate = (
    df.groupby("dti_missing")["default_event"]
      .mean()
      .mul(100)
)

print(default_rate)


print("\n===== DTI DISTRIBUTION WITHOUT 999 =====")

valid_dti = df.loc[
    df["original_dti"] != 999,
    "original_dti"
]

print(valid_dti.describe())


print("\n===== DONE =====")