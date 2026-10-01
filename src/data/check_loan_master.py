import pandas as pd


FILE = "data/standardized/loan_master_2026.parquet"


df = pd.read_parquet(FILE)


print("=" * 60)
print("LOAN MASTER")
print("=" * 60)

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nDuplicate loan_id:")
print(df["loan_id"].duplicated().sum())

print("\nOrigination vintage:")
print(df["origination_vintage"].value_counts().sort_index())