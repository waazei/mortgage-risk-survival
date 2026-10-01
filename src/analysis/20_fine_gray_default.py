import numpy as np
import pandas as pd

from pathlib import Path
from scipy.optimize import minimize


# ============================================================
# 1. INPUT
# ============================================================

INPUT = Path(
    "data/analysis/loan_level/cox_data.parquet"
)

OUTPUT = Path(
    "data/results/fine_gray_default.csv"
)


# ============================================================
# 2. READ DATA
# ============================================================

columns = [
    "loan_id",
    "loan_age",
    "default_event",
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term"
]

df = pd.read_parquet(
    INPUT,
    columns=columns
)

print("Rows:", len(df))

print("\nDefault distribution:")
print(
    df["default_event"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 3. NUMERIC CONVERSION
# ============================================================

numeric_cols = [
    "loan_age",
    "default_event",
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term"
]

for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


df = df.dropna(
    subset=numeric_cols
)


# ============================================================
# 4. STANDARDIZE 5 PREDICTORS
# ============================================================

features = [
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term"
]

X = df[features].to_numpy(
    dtype=float
)

means = X.mean(axis=0)
stds = X.std(axis=0)

X = (
    X - means
) / stds


# ============================================================
# 5. EVENT CODING
#
# default_event:
# 1 = Default
# 0 = Non-default
#
# Nhưng loan-level data hiện tại đã gộp:
# Prepayment = censored trong default_event.
#
# Vì vậy cần lấy thông tin competing event từ
# survival_loan_level.parquet.
# ============================================================

loan_level = pd.read_parquet(
    "data/analysis/loan_level/survival_loan_level.parquet",
    columns=[
        "loan_id",
        "cr_event"
    ]
)

loan_level["cr_event"] = pd.to_numeric(
    loan_level["cr_event"],
    errors="coerce"
)

df = df.merge(
    loan_level,
    on="loan_id",
    how="left",
    validate="one_to_one"
)

df["cr_event"] = df["cr_event"].fillna(0)


# ============================================================
# 6. SORT BY LOAN AGE
# ============================================================

df = df.reset_index(
    drop=True
)

order = np.argsort(
    df["loan_age"].to_numpy()
)

df = df.iloc[order].reset_index(
    drop=True
)

X = X[order]

time_values = df["loan_age"].to_numpy(dtype=float)

event = df["cr_event"].to_numpy(
    dtype=int
)

if not np.all(np.isfinite(time_values)) or not np.allclose(time_values, np.round(time_values)):
    raise ValueError("loan_age must contain finite whole-month values for this discrete-time implementation")

time = np.round(time_values).astype(np.int32)


# ============================================================
# 7. FINE-GRAY SETUP
#
# Event of interest = 1 (Default)
# Competing event = 2 (Prepayment)
#
# Fine-Gray keeps subjects with competing events
# in the subdistribution risk set.
# ============================================================

max_age = int(time.max())
default_count_by_age = np.bincount(
    time[event == 1],
    minlength=max_age + 1,
)
default_covariate_sum_by_age = np.zeros((max_age + 1, X.shape[1]), dtype=float)
np.add.at(default_covariate_sum_by_age, time[event == 1], X[event == 1])
default_times = np.flatnonzero(default_count_by_age)
prepayment_mask = event == 2

print(
    "\nNumber of default event times:",
    len(default_times)
)

print(
    "First default age:",
    default_times[0]
)

print(
    "Last default age:",
    default_times[-1]
)


# ============================================================
# 8. LOG-LIKELIHOOD
# ============================================================

def neg_log_likelihood(beta):

    eta = X @ beta

    # Numerical protection
    eta = np.clip(
        eta,
        -30,
        30
    )

    exp_eta = np.exp(eta)

    # loan_age is discrete (months). Build risk-set denominators from
    # age-level sums instead of rescanning every loan for every event age.
    weight_by_age = np.bincount(
        time,
        weights=exp_eta,
        minlength=max_age + 1,
    )
    still_observed_weight = np.cumsum(weight_by_age[::-1])[::-1]

    prepayment_weight_by_age = np.bincount(
        time[prepayment_mask],
        weights=exp_eta[prepayment_mask],
        minlength=max_age + 1,
    )
    prepayment_before_age = np.zeros(max_age + 1, dtype=float)
    if max_age > 0:
        prepayment_before_age[1:] = np.cumsum(prepayment_weight_by_age)[:-1]

    loglik = 0.0

    for t in default_times:

        # Fine-Gray subdistribution risk set:
        #
        # 1. Loans still under observation at t
        # 2. Loans that already had competing event
        #
        # Subjects who had default are removed.
        #
        d_count = default_count_by_age[t]
        denominator = still_observed_weight[t] + prepayment_before_age[t]

        if denominator <= 0:
            continue

        numerator = default_covariate_sum_by_age[t] @ beta

        loglik += (
            numerator
            - d_count
            * np.log(denominator)
        )

    return -loglik


# ============================================================
# 9. OPTIMIZATION
# ============================================================

beta0 = np.zeros(
    len(features)
)

print(
    "\n===== OPTIMIZATION ====="
)

result = minimize(
    neg_log_likelihood,
    beta0,
    method="L-BFGS-B",
    options={
        "maxiter": 50,
        "ftol": 1e-9
    }
)

if not result.success or not np.isfinite(result.fun) or not np.isfinite(result.x).all():
    raise RuntimeError(
        f"Fine-Gray optimization did not converge; refusing to save estimates: {result.message}"
    )

print(
    "Success:",
    result.success
)

print(
    "Message:",
    result.message
)

print(
    "Iterations:",
    result.nit
)


# ============================================================
# 10. COEFFICIENTS
# ============================================================

beta = result.x


# ============================================================
# 11. NUMERICAL HESSIAN
# ============================================================

def numerical_hessian(
    func,
    x,
    epsilon=1e-4
):

    n = len(x)

    H = np.zeros(
        (n, n)
    )

    for i in range(n):

        for j in range(n):

            ei = np.zeros(n)
            ej = np.zeros(n)

            ei[i] = epsilon
            ej[j] = epsilon

            f1 = func(
                x + ei + ej
            )

            f2 = func(
                x + ei - ej
            )

            f3 = func(
                x - ei + ej
            )

            f4 = func(
                x - ei - ej
            )

            H[i, j] = (
                f1
                - f2
                - f3
                + f4
            ) / (
                4 * epsilon ** 2
            )

    return H


print(
    "\nCalculating standard errors..."
)

H = numerical_hessian(
    neg_log_likelihood,
    beta
)
H = (H + H.T) / 2
if not np.isfinite(H).all() or np.linalg.eigvalsh(H).min() <= 0:
    raise RuntimeError("Fine-Gray observed information is not positive definite; refusing Wald inference")


# ============================================================
# 12. VARIANCE / STANDARD ERROR
# ============================================================

try:

    covariance = np.linalg.inv(
        H
    )

    se = np.sqrt(
        np.maximum(
            np.diag(covariance),
            0
        )
    )

except np.linalg.LinAlgError:

    print(
        "WARNING: Hessian is singular."
    )

    covariance = np.linalg.pinv(
        H
    )

    se = np.sqrt(
        np.maximum(
            np.diag(covariance),
            0
        )
    )

if not np.isfinite(se).all() or (se <= 0).any():
    raise RuntimeError("Fine-Gray produced invalid standard errors; refusing to save estimates")


# ============================================================
# 13. HAZARD RATIOS
# ============================================================

hr = np.exp(beta)

lower = np.exp(
    beta - 1.96 * se
)

upper = np.exp(
    beta + 1.96 * se
)


# ============================================================
# 14. Z / P-VALUE
# ============================================================

z = beta / se

from scipy.stats import norm

p_value = (
    2
    * norm.sf(
        np.abs(z)
    )
)


# ============================================================
# 15. RESULT TABLE
# ============================================================

result_table = pd.DataFrame({

    "variable": features,

    "coefficient": beta,

    "HR": hr,

    "SE": se,

    "z": z,

    "p_value": p_value,

    "CI_lower_95": lower,

    "CI_upper_95": upper,
    "converged": bool(result.success),
    "optimizer_message": str(result.message),
    "iterations": int(result.nit),
    "fit_n": int(len(df)),
    "implementation_status": "custom_unbenchmarked",

})


print(
    "\n===== FINE-GRAY DEFAULT ====="
)

print(
    result_table.to_string(
        index=False
    )
)


# ============================================================
# 16. SAVE
# ============================================================

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

result_table.to_csv(
    OUTPUT,
    index=False
)

print(
    "\nSaved:",
    OUTPUT
)
