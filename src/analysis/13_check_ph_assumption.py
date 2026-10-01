import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.stats import linregress


# ============================================================
# 1. PATH
# ============================================================

DATA_PATH = Path(
    "data/analysis/loan_level/cox_data.parquet"
)

COX_RESULT_PATH = Path(
    "data/results/cox_ph_default.csv"
)

OUTPUT_CSV = Path(
    "data/results/schoenfeld_residuals.csv"
)

OUTPUT_SUMMARY = Path(
    "data/results/ph_assumption_summary.csv"
)

OUTPUT_PLOT_DIR = Path(
    "data/results/ph_plots"
)

OUTPUT_PLOT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. VARIABLES
# ============================================================

features = [
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term",
]


# ============================================================
# 3. LOAD COX RESULTS
# ============================================================

print("===== LOAD COX RESULTS =====")

cox_result = pd.read_csv(
    COX_RESULT_PATH
)

beta = cox_result["coefficient"].to_numpy(
    dtype=np.float64
)

means = cox_result["mean_original"].to_numpy(
    dtype=np.float64
)

stds = cox_result["std_original"].to_numpy(
    dtype=np.float64
)

print("Coefficients:")
for name, b in zip(features, beta):
    print(f"{name}: {b:.8f}")


# ============================================================
# 4. LOAD DATA
# ============================================================

print("\n===== LOAD DATA =====")

cols = [
    "loan_age",
    "default_event",
] + features

df = pd.read_parquet(
    DATA_PATH,
    columns=cols
)

print("Rows:", len(df))
print("Defaults:", int(df["default_event"].sum()))


# ============================================================
# 5. STANDARDIZE X
# ============================================================

X = df[features].to_numpy(
    dtype=np.float64
)

X = (
    X - means
) / stds

time = df["loan_age"].to_numpy(
    dtype=np.int64
)

event = df["default_event"].to_numpy(
    dtype=np.int8
)


# ============================================================
# 6. CALCULATE LINEAR PREDICTOR
# ============================================================

print("\n===== CALCULATE RISK SCORES =====")

eta = X @ beta

# Numerical stabilization
eta_max = np.max(eta)

exp_eta = np.exp(
    eta - eta_max
)


# ============================================================
# 7. RISK-SET SUMS
# ============================================================

print("\n===== CALCULATE RISK SETS =====")

max_time = int(time.max())

n_times = max_time + 1
p = len(features)

# Sum exp(beta'x)
group_s0 = np.bincount(
    time,
    weights=exp_eta,
    minlength=n_times
)

# Sum exp(beta'x) * X
group_s1 = np.zeros(
    (n_times, p),
    dtype=np.float64
)

for j in range(p):

    group_s1[:, j] = np.bincount(
        time,
        weights=exp_eta * X[:, j],
        minlength=n_times
    )


# Risk set = loan_age >= t

risk_s0 = np.cumsum(
    group_s0[::-1]
)[::-1]

risk_s1 = np.cumsum(
    group_s1[::-1],
    axis=0
)[::-1]


# ============================================================
# 8. SCHOENFELD RESIDUALS
# ============================================================

print("\n===== CALCULATE SCHOENFELD RESIDUALS =====")

event_idx = np.where(
    event == 1
)[0]

event_times = time[event_idx]

event_X = X[event_idx]

residuals = np.zeros_like(
    event_X
)

for i, t in enumerate(event_times):

    expected_x = (
        risk_s1[t] /
        risk_s0[t]
    )

    residuals[i] = (
        event_X[i] -
        expected_x
    )


# ============================================================
# 9. CREATE RESIDUAL DATAFRAME
# ============================================================

residual_df = pd.DataFrame(
    residuals,
    columns=[
        f"{x}_schoenfeld"
        for x in features
    ]
)

residual_df["loan_age"] = event_times

# log time is commonly useful for PH diagnostics
residual_df["log_loan_age"] = np.log(
    residual_df["loan_age"] + 1
)


# ============================================================
# 10. TEST RESIDUAL TREND OVER TIME
# ============================================================

print("\n===== PH TEST =====")

summary = []

for feature in features:

    residual_col = (
        f"{feature}_schoenfeld"
    )

    y = residual_df[
        residual_col
    ].to_numpy()

    x = residual_df[
        "log_loan_age"
    ].to_numpy()

    result = linregress(
        x,
        y
    )

    summary.append({

        "variable": feature,

        "slope": result.slope,

        "intercept": result.intercept,

        "r_value": result.rvalue,

        "r_squared": result.rvalue ** 2,

        "p_value": result.pvalue,

        "std_error": result.stderr,

    })

    print(
        f"\n{feature}"
    )

    print(
        f"Slope: {result.slope:.8f}"
    )

    print(
        f"R-squared: "
        f"{result.rvalue ** 2:.8f}"
    )

    print(
        f"p-value: "
        f"{result.pvalue:.8e}"
    )

    if result.pvalue < 0.05:

        print(
            "=> Evidence of time-varying effect "
            "(PH may be violated)."
        )

    else:

        print(
            "=> No statistically significant "
            "residual trend detected."
        )


summary_df = pd.DataFrame(
    summary
)


# ============================================================
# 11. SAVE RESIDUALS
# ============================================================

residual_df.to_csv(
    OUTPUT_CSV,
    index=False
)

summary_df.to_csv(
    OUTPUT_SUMMARY,
    index=False
)


# ============================================================
# 12. PLOTS
# ============================================================

print("\n===== CREATE PLOTS =====")

for feature in features:

    residual_col = (
        f"{feature}_schoenfeld"
    )

    plt.figure(
        figsize=(8, 5)
    )

    plt.scatter(
        residual_df["loan_age"],
        residual_df[residual_col],
        s=3,
        alpha=0.25
    )

    # Smooth linear trend
    x = residual_df[
        "loan_age"
    ].to_numpy()

    y = residual_df[
        residual_col
    ].to_numpy()

    slope, intercept = np.polyfit(
        x,
        y,
        1
    )

    x_line = np.linspace(
        x.min(),
        x.max(),
        100
    )

    y_line = (
        intercept +
        slope * x_line
    )

    plt.plot(
        x_line,
        y_line,
        linewidth=2
    )

    plt.axhline(
        0,
        linestyle="--"
    )

    plt.xlabel(
        "Loan Age (months)"
    )

    plt.ylabel(
        "Schoenfeld Residual"
    )

    plt.title(
        f"Schoenfeld Residuals: {feature}"
    )

    plt.tight_layout()

    output_path = (
        OUTPUT_PLOT_DIR /
        f"schoenfeld_{feature}.png"
    )

    plt.savefig(
        output_path,
        dpi=150
    )

    plt.close()


# ============================================================
# 13. FINAL
# ============================================================

print("\n===== SAVED =====")

print(
    "Residuals:",
    OUTPUT_CSV
)

print(
    "Summary:",
    OUTPUT_SUMMARY
)

print(
    "Plots:",
    OUTPUT_PLOT_DIR
)

print("\n===== DONE =====")