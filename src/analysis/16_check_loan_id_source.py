import pandas as pd
from pathlib import Path


LOAN_ID = "F16Q10000190"

path = Path(
    "data/standardized/2016/orig_2016Q1.parquet"
)

print("Reading:", path)

orig = pd.read_parquet(path)

print("\n===== SEARCH LOAN ID =====")

result = orig[
    orig["loan_id"].astype(str) == LOAN_ID
]

print(
    "Number of matching origination rows:",
    len(result)
)

print("\n===== MATCHING ROWS =====")

print(
    result.to_string(index=False)
)

print("\n===== ALL COLUMNS =====")

print(
    result.columns.tolist()
)

print("\n===== DONE =====")