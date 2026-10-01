from pathlib import Path
import pandas as pd


DATA_DIR = Path("data/analysis")


files = sorted(
    DATA_DIR.glob("survival_*.parquet")
)


for file in files:

    df = pd.read_parquet(
        file,
        columns=[
            "event_type",
            "event"
        ]
    )

    # Tìm các dòng bị sai:
    # Censored phải có event = 0
    # Default / Prepayment phải có event = 1

    wrong = df[
        (
            (df["event_type"] == "Censored")
            & (df["event"] != 0)
        )
        |
        (
            (df["event_type"] != "Censored")
            & (df["event"] != 1)
        )
    ]

    if len(wrong) > 0:

        print(
            f"ERROR: {file.name} "
            f"-> {len(wrong):,} rows"
        )

    else:

        print(
            f"OK: {file.name}"
        )

    del df


print("\n====================================")
print("EVENT INDICATOR CHECK COMPLETED")
print("====================================")