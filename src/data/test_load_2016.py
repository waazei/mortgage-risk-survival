from pathlib import Path

from load_data import load_origination, load_performance


ZIP_FILE = Path(
    "data/raw/2016/historical_data_2016.zip"
)


print("=" * 60)
print("TEST LOAD 2016")
print("=" * 60)


print("\nDang doc Origination...")

orig = load_origination(ZIP_FILE)

print("Origination shape:", orig.shape)
print("Origination columns:")
print(orig.columns.tolist())


print("\nDang doc Performance...")

perf = load_performance(ZIP_FILE)

print("Performance shape:", perf.shape)
print("Performance columns:")
print(perf.columns.tolist())


print("\nPerformance first 5 rows:")
print(perf.head())


print("\nZero balance code:")
print(
    perf["zero_balance_code"]
    .value_counts(dropna=False)
    .sort_index()
)


print("\nLoan age:")
print(
    perf["loan_age"]
    .value_counts(dropna=False)
    .sort_index()
)


print("\nMonthly reporting period:")
print(
    perf["monthly_reporting_period"]
    .value_counts()
    .sort_index()
)


print("\nDONE")