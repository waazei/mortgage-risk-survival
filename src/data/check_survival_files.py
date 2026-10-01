from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/analysis")


files = sorted(
    DATA_DIR.glob("survival_*.parquet")
)


print(f"Number of files: {len(files)}")
print()


for file in files:

    try:

        df = pd.read_parquet(
            file,
            columns=[
                "loan_id",
                "loan_age",
                "event_type",
                "event"
            ]
        )

        print(
            f"{file.name}: "
            f"{len(df):,} rows | "
            f"OK"
        )

        del df

    except Exception as e:

        print(
            f"{file.name}: ERROR"
        )

        print(e)