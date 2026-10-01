from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter


# =========================
# 1. PATH
# =========================

INPUT = Path("data/analysis/loan_level/survival_loan_level.parquet")

OUTPUT_DIR = Path("data/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TABLE_OUTPUT = OUTPUT_DIR / "kaplan_meier_summary.csv"
FIGURE_OUTPUT = OUTPUT_DIR / "kaplan_meier_curve.png"


# =========================
# 2. LOAD DATA
# =========================

print("Loading data...")

df = pd.read_parquet(
    INPUT,
    columns=[
        "loan_id",
        "loan_age",
        "event",
        "event_type",
    ],
)

print(f"Total loans: {len(df):,}")


# =========================
# 3. DESCRIPTIVE STATISTICS
# =========================

print("\n====================================")
print("EVENT DISTRIBUTION")
print("====================================")

event_counts = df["event_type"].value_counts()

print(event_counts)

print("\nEvent rates:")

event_rates = (
    df["event_type"]
    .value_counts(normalize=True)
    .mul(100)
    .round(4)
)

print(event_rates)


# =========================
# 4. KAPLAN-MEIER
# =========================

print("\n====================================")
print("KAPLAN-MEIER")
print("====================================")

kmf = KaplanMeierFitter()

kmf.fit(
    durations=df["loan_age"],
    event_observed=df["event"],
    label="Overall survival",
)


# =========================
# 5. SURVIVAL PROBABILITY
# =========================

horizons = [12, 24, 36, 60]

survival_probability = kmf.survival_function_at_times(horizons)

summary = pd.DataFrame({
    "LoanAge_Month": horizons,
    "Survival_Probability": survival_probability.values,
})

summary["Default_Probability_1_minus_S"] = (
    1 - summary["Survival_Probability"]
)

summary["Default_Probability_pct"] = (
    summary["Default_Probability_1_minus_S"] * 100
).round(4)

summary["Survival_Probability_pct"] = (
    summary["Survival_Probability"] * 100
).round(4)


print("\nSurvival / Default probability:")

print(summary.to_string(index=False))


# =========================
# 6. SAVE TABLE
# =========================

summary.to_csv(
    TABLE_OUTPUT,
    index=False
)

print(f"\nSaved table: {TABLE_OUTPUT}")


# =========================
# 7. PLOT
# =========================

plt.figure(figsize=(10, 6))

kmf.plot_survival_function()

plt.xlabel("Loan Age (months)")
plt.ylabel("Survival Probability")
plt.title("Kaplan-Meier Survival Curve")

plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    FIGURE_OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"Saved figure: {FIGURE_OUTPUT}")


# =========================
# 8. DONE
# =========================

print("\n====================================")
print("KAPLAN-MEIER DONE")
print("====================================")