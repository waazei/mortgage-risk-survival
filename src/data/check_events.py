from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/analysis")


files = sorted(
    DATA_DIR.glob("survival_*.parquet")
)


total_censored = 0
total_prepayment = 0
total_default = 0


for file in files:

    df = pd.read_parquet(
        file,
        columns=[
            "event_type",
            "event"
        ]
    )

    counts = df["event_type"].value_counts()

    censored = counts.get("Censored", 0)
    prepayment = counts.get("Voluntary Prepayment", 0)
    default = counts.get("Default", 0)

    total_censored += censored
    total_prepayment += prepayment
    total_default += default

    print(
        f"{file.name} | "
        f"Censored={censored:,} | "
        f"Prepayment={prepayment:,} | "
        f"Default={default:,}"
    )

    del df


print("\n====================================")
print("TOTAL")
print("====================================")

print(f"Censored: {total_censored:,}")
print(f"Prepayment: {total_prepayment:,}")
print(f"Default: {total_default:,}")

print("\nDONE")