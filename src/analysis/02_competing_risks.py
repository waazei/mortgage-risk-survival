from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import AalenJohansenFitter


INPUT = Path(
    "data/analysis/loan_level/survival_loan_level.parquet"
)

OUTPUT_DIR = Path("data/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TABLE_OUTPUT = OUTPUT_DIR / "competing_risks_cif_summary.csv"
FIGURE_OUTPUT = OUTPUT_DIR / "competing_risks_cif.png"


print("Loading data...")

df = pd.read_parquet(
    INPUT,
    columns=["loan_id", "loan_age", "cr_event"]
)

print(f"Total loans: {len(df):,}")


# ============================================================
# COMPETING RISKS EVENTS
# ============================================================

print("\n====================================")
print("COMPETING RISKS EVENTS")
print("====================================")

print(
    df["cr_event"]
    .value_counts()
    .sort_index()
)

print("\nMapping:")
print("0 = Censored")
print("1 = Default")
print("2 = Voluntary Prepayment")


# ============================================================
# AALEN-JOHANSEN
# ============================================================

print("\n====================================")
print("AALEN-JOHANSEN")
print("====================================")


ajf = AalenJohansenFitter()

ajf.fit(
    durations=df["loan_age"],
    event_observed=df["cr_event"],
    event_of_interest=1,
)


# ============================================================
# GET CIF TABLE
# ============================================================

cif_table = ajf.cumulative_density_.copy()

print("\nCIF table:")
print(cif_table.head())


# ============================================================
# DEFAULT CIF AT 12 / 24 / 36 / 60 MONTHS
# ============================================================

horizons = [12, 24, 36, 60]

cif_values = []

for month in horizons:

    available = cif_table.loc[
        cif_table.index <= month
    ]

    if len(available) == 0:
        value = 0.0
    else:
        value = available.iloc[-1, 0]

    cif_values.append(value)


summary = pd.DataFrame({
    "LoanAge_Month": horizons,
    "Default_CIF": cif_values
})


summary["Default_PD_pct"] = (
    summary["Default_CIF"] * 100
).round(6)


# ============================================================
# PRINT RESULT
# ============================================================

print("\n====================================")
print("DEFAULT CIF / PD")
print("====================================")

print(
    summary.to_string(index=False)
)


# ============================================================
# SAVE TABLE
# ============================================================

summary.to_csv(
    TABLE_OUTPUT,
    index=False
)

print(
    f"\nSaved table: {TABLE_OUTPUT}"
)


# ============================================================
# PLOT
# ============================================================

plt.figure(figsize=(10, 6))

ajf.plot()

plt.xlabel("Loan Age (months)")
plt.ylabel("Default Cumulative Incidence")
plt.title(
    "Default Cumulative Incidence Function"
)

plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    FIGURE_OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print(
    f"Saved figure: {FIGURE_OUTPUT}"
)


print("\n====================================")
print("COMPETING RISKS DONE")
print("====================================")