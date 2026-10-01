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


print("\n===== BEFORE CONVERSION =====")
print(df[variables].dtypes)


# Chuyển các biến sang numeric
for col in variables:
    df[col] = pd.to_numeric(df[col], errors="coerce")


print("\n===== AFTER CONVERSION =====")
print(df[variables].dtypes)


print("\n===== MISSING AFTER CONVERSION =====")
print(df[variables].isna().sum())


default_df = df[df["default_event"] == 1]
non_default_df = df[df["default_event"] == 0]


print("\n===== DEFAULT SAMPLE =====")
print(default_df.shape)


print("\n===== DEFAULT STATISTICS =====")
print(default_df[variables].describe().T)


print("\n===== NON-DEFAULT STATISTICS =====")
print(non_default_df[variables].describe().T)


print("\n===== SPECIAL VALUES =====")

for col in variables:

    print(f"\n--- {col} ---")

    for value in [0, 999, 9999]:

        count_all = (df[col] == value).sum()
        count_default = (default_df[col] == value).sum()
        count_non_default = (non_default_df[col] == value).sum()

        if count_all > 0:

            print(
                f"value={value}: "
                f"all={count_all:,}, "
                f"default={count_default:,}, "
                f"non_default={count_non_default:,}"
            )


print("\n===== RANGE =====")

for col in variables:

    print(
        f"{col}: "
        f"min={df[col].min()}, "
        f"max={df[col].max()}, "
        f"median={df[col].median()}"
    )


print("\n===== DONE =====")