from pathlib import Path

from load_data import load_performance


ZIP_FILE = Path(
    "data/raw/2026/historical_data_2026.zip"
)


print("=" * 60)
print("PERFORMANCE DATA CHECK")
print("=" * 60)


print("\nDang doc Performance...")

perf = load_performance(ZIP_FILE)


print("\nShape:")
print(perf.shape)


print("\nColumns:")
print(perf.columns.tolist())


print("\nFirst 5 rows:")
print(perf.head())


print("\nData types:")
print(perf.dtypes)


print("\nMissing values:")
print(perf.isna().sum())


print("\nUnique loan_id:")
print(perf["loan_id"].nunique())


print("\nDuplicate loan-month:")

duplicate_count = perf.duplicated(
    subset=[
        "loan_id",
        "monthly_reporting_period"
    ]
).sum()

print(duplicate_count)


print("\nMonthly reporting period:")
print(
    perf["monthly_reporting_period"]
    .value_counts()
    .sort_index()
)


print("\nLoan age:")
print(
    perf["loan_age"]
    .value_counts()
    .sort_index()
)


print("\nZero balance code:")
print(
    perf["zero_balance_code"]
    .value_counts(dropna=False)
    .sort_index()
)