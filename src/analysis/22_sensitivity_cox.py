import numpy as np
import pandas as pd

from pathlib import Path
from scipy.optimize import minimize
from scipy.stats import norm


# ============================================================
# 1. PATH
# ============================================================

INPUT = Path(
    "data/analysis/loan_level/cox_data.parquet"
)

OUTPUT = Path(
    "data/results/cox_sensitivity_complete_case.csv"
)


# ============================================================
# 2. READ DATA
# ============================================================

features = [
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term"
]

columns = [
    "loan_age",
    "default_event",
    "credit_score_missing",
    "ltv_missing",
    "dti_missing"
] + features


df = pd.read_parquet(
    INPUT,
    columns=columns
)

original_rows = len(df)

print(
    "Original rows:",
    original_rows
)


# ============================================================
# 3. COMPLETE CASE
# ============================================================

missing_mask = (
    (df["credit_score_missing"] == 0)
    &
    (df["ltv_missing"] == 0)
    &
    (df["dti_missing"] == 0)
)

df = df[
    missing_mask
].copy()

print(
    "Complete-case rows:",
    len(df)
)

print(
    "Removed rows:",
    original_rows - len(df)
)


print(
    "\nDefault distribution:"
)

print(
    df["default_event"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 4. NUMERIC
# ============================================================

df["loan_age"] = pd.to_numeric(
    df["loan_age"],
    errors="coerce"
)

df["default_event"] = pd.to_numeric(
    df["default_event"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "loan_age",
        "default_event"
    ] + features
)


# ============================================================
# 5. STANDARDIZE
# ============================================================

X = df[
    features
].to_numpy(
    dtype=float
)

mean = X.mean(
    axis=0
)

std = X.std(
    axis=0
)

X = (
    X - mean
) / std


time_values = df["loan_age"].to_numpy(dtype=float)

event = df[
    "default_event"
].to_numpy(
    dtype=int
)

if not np.all(np.isfinite(time_values)) or not np.allclose(time_values, np.round(time_values)):
    raise ValueError("loan_age must contain finite whole-month values for this discrete-time Cox model")

time = np.round(time_values).astype(np.int32)


# ============================================================
# 6. DEFAULT EVENT TIMES
# ============================================================

max_age = int(time.max())
event_count_by_age = np.bincount(time[event == 1], minlength=max_age + 1)
event_covariate_sum_by_age = np.zeros((max_age + 1, X.shape[1]), dtype=float)
np.add.at(event_covariate_sum_by_age, time[event == 1], X[event == 1])
event_times = np.flatnonzero(event_count_by_age)

print(
    "\nDefault event times:",
    len(event_times)
)


# ============================================================
# 7. COX PARTIAL NEGATIVE LOG-LIKELIHOOD
# ============================================================

def neg_loglik(beta):

    eta = X @ beta

    eta = np.clip(
        eta,
        -30,
        30
    )

    exp_eta = np.exp(
        eta
    )

    weight_by_age = np.bincount(
        time,
        weights=exp_eta,
        minlength=max_age + 1,
    )
    risk_weight = np.cumsum(weight_by_age[::-1])[::-1]
    loglik = 0.0

    for t in event_times:
        d = event_count_by_age[t]
        denominator = risk_weight[t]
        numerator = event_covariate_sum_by_age[t] @ beta

        loglik += (
            numerator
            - d * np.log(
                denominator
            )
        )

    return -loglik


def gradient(beta):
    eta = np.clip(X @ beta, -30, 30)
    exp_eta = np.exp(eta)
    weight_by_age = np.bincount(time, weights=exp_eta, minlength=max_age + 1)
    weighted_x_by_age = np.zeros((max_age + 1, X.shape[1]), dtype=float)
    for j in range(X.shape[1]):
        weighted_x_by_age[:, j] = np.bincount(
            time,
            weights=exp_eta * X[:, j],
            minlength=max_age + 1,
        )
    risk_weight = np.cumsum(weight_by_age[::-1])[::-1]
    risk_weighted_x = np.cumsum(weighted_x_by_age[::-1], axis=0)[::-1]

    grad = np.zeros(X.shape[1], dtype=float)
    for t in event_times:
        grad += event_covariate_sum_by_age[t] - (
            event_count_by_age[t] * risk_weighted_x[t] / risk_weight[t]
        )
    return -grad


# ============================================================
# 8. FIT
# ============================================================

print(
    "\n===== SENSITIVITY COX ====="
)

beta0 = np.zeros(
    len(features)
)

result = minimize(
    neg_loglik,
    beta0,
    jac=gradient,
    method="L-BFGS-B",
    options={
        "maxiter": 50,
        "ftol": 1e-9
    }
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


beta = result.x


# ============================================================
# 9. NUMERICAL HESSIAN
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
    neg_loglik,
    beta
)


try:

    covariance = np.linalg.inv(
        H
    )

except np.linalg.LinAlgError:

    covariance = np.linalg.pinv(
        H
    )


se = np.sqrt(
    np.maximum(
        np.diag(covariance),
        0
    )
)


# ============================================================
# 10. HR / CI / P-VALUE
# ============================================================

hr = np.exp(
    beta
)

ci_lower = np.exp(
    beta - 1.96 * se
)

ci_upper = np.exp(
    beta + 1.96 * se
)

z = (
    beta / se
)

p_value = (
    2
    * norm.sf(
        np.abs(z)
    )
)


# ============================================================
# 11. RESULT
# ============================================================

result_table = pd.DataFrame({

    "variable": features,

    "coefficient": beta,

    "HR": hr,

    "SE": se,

    "z": z,

    "p_value": p_value,

    "CI_lower_95": ci_lower,

    "CI_upper_95": ci_upper

})


print(
    "\n===== COMPLETE-CASE SENSITIVITY ====="
)

print(
    result_table.to_string(
        index=False
    )
)


# ============================================================
# 12. SAVE
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
