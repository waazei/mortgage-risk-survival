import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp
from pathlib import Path


# ============================================================
# 1. PATH
# ============================================================

INPUT_PATH = Path(
    "data/analysis/loan_level/cox_data.parquet"
)

OUTPUT_PATH = Path(
    "data/results/cox_ph_default.csv"
)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("===== LOAD DATA =====")

cols = [
    "loan_age",
    "default_event",
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term",
]

df = pd.read_parquet(
    INPUT_PATH,
    columns=cols
)

print("Rows:", len(df))
print("Defaults:", int(df["default_event"].sum()))


# ============================================================
# 3. PREPARE X
# ============================================================

features = [
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term",
]

X = df[features].to_numpy(dtype=np.float64)

event = df["default_event"].to_numpy(dtype=np.int8)
time = df["loan_age"].to_numpy(dtype=np.int64)


# ============================================================
# 4. STANDARDIZE PREDICTORS
# ============================================================
#
# Standardization is only for numerical stability.
# Hazard ratios will be reported per 1 standard deviation.
#
# HR per original unit can be recovered from the coefficient
# if needed later.
# ============================================================

means = X.mean(axis=0)
stds = X.std(axis=0, ddof=0)

X = (X - means) / stds

print("\n===== STANDARDIZATION =====")

for name, mean, std in zip(features, means, stds):
    print(f"{name}: mean={mean:.6f}, std={std:.6f}")


# ============================================================
# 5. SORT BY LOAN AGE
# ============================================================

order = np.argsort(time)

time = time[order]
event = event[order]
X = X[order]

# unique ages
unique_times = np.unique(time)

event_times = unique_times[
    np.array([
        event[time == t].sum() > 0
        for t in unique_times
    ])
]

print("\n===== EVENT TIMES =====")
print("Number of unique loan ages:", len(unique_times))
print("Number of event ages:", len(event_times))
print("First event age:", event_times[0])
print("Last event age:", event_times[-1])


# ============================================================
# 6. GROUP INFORMATION BY LOAN AGE
# ============================================================

# Because loan_age only ranges from 0 to 122,
# calculate risk sets through cumulative sums.

max_time = int(time.max())

n_times = max_time + 1
p = X.shape[1]

group_n = np.zeros(n_times, dtype=np.int64)
group_events = np.zeros(n_times, dtype=np.int64)

group_x = np.zeros((n_times, p), dtype=np.float64)
group_event_x = np.zeros((n_times, p), dtype=np.float64)

group_x2 = np.zeros((n_times, p, p), dtype=np.float64)

for t in range(n_times):

    mask = time == t

    if not np.any(mask):
        continue

    Xt = X[mask]
    et = event[mask]

    group_n[t] = len(Xt)
    group_events[t] = et.sum()

    group_x[t] = Xt.sum(axis=0)

    if et.sum() > 0:
        group_event_x[t] = Xt[et == 1].sum(axis=0)

    # sum of x'x
    group_x2[t] = Xt.T @ Xt


# ============================================================
# 7. CUMULATIVE RISK SETS
# ============================================================

# Risk set at t = all loans with loan_age >= t.
#
# Reverse cumulative sums.
# ============================================================

risk_n = np.cumsum(group_n[::-1])[::-1]

risk_x = np.cumsum(
    group_x[::-1],
    axis=0
)[::-1]

risk_x2 = np.cumsum(
    group_x2[::-1],
    axis=0
)[::-1]


# ============================================================
# 8. EVENT INFORMATION
# ============================================================

event_count = group_events
event_x = group_event_x

total_events = int(event_count.sum())

print("\n===== EVENT INFORMATION =====")
print("Total default events:", total_events)


# ============================================================
# 9. COX LOG-LIKELIHOOD
# ============================================================
#
# Breslow approximation for tied event times.
#
# l(beta)
# = sum_t [
#       sum_events x'beta
#       - d_t log(sum_risk exp(x'beta))
#   ]
#
# Gradient:
# = sum_events x
#   - d_t * weighted_mean(X_risk)
#
# ============================================================

def objective(beta):

    z = X @ beta

    # global maximum keeps exp numerically stable
    zmax = np.max(z)

    exp_z = np.exp(z - zmax)

    # weighted sums by loan age
    weighted_n = np.bincount(
        time,
        weights=exp_z,
        minlength=n_times
    )

    weighted_x = np.zeros((n_times, p))

    for j in range(p):
        weighted_x[:, j] = np.bincount(
            time,
            weights=exp_z * X[:, j],
            minlength=n_times
        )

    risk_exp = np.cumsum(
        weighted_n[::-1]
    )[::-1]

    risk_exp_x = np.cumsum(
        weighted_x[::-1],
        axis=0
    )[::-1]

    loglik = 0.0

    for t in event_times:

        d = event_count[t]

        if d == 0:
            continue

        denominator = risk_exp[t]

        if denominator <= 0:
            return 1e100

        log_denominator = (
            zmax + np.log(denominator)
        )

        loglik += (
            event_x[t] @ beta
            - d * log_denominator
        )

    return -loglik


# ============================================================
# 10. COX GRADIENT
# ============================================================

def gradient(beta):

    z = X @ beta

    zmax = np.max(z)

    exp_z = np.exp(z - zmax)

    weighted_n = np.bincount(
        time,
        weights=exp_z,
        minlength=n_times
    )

    weighted_x = np.zeros((n_times, p))

    for j in range(p):
        weighted_x[:, j] = np.bincount(
            time,
            weights=exp_z * X[:, j],
            minlength=n_times
        )

    risk_exp = np.cumsum(
        weighted_n[::-1]
    )[::-1]

    risk_exp_x = np.cumsum(
        weighted_x[::-1],
        axis=0
    )[::-1]

    grad = np.zeros(p)

    for t in event_times:

        d = event_count[t]

        if d == 0:
            continue

        denominator = risk_exp[t]

        mean_x = (
            risk_exp_x[t] / denominator
        )

        grad += (
            event_x[t]
            - d * mean_x
        )

    return -grad


# ============================================================
# 11. OPTIMIZE
# ============================================================

print("\n===== FIT COX PH =====")
print("Using full sample.")
print("No sampling.")
print("Method: Breslow ties + L-BFGS-B")
print()

initial_beta = np.zeros(p)

result = minimize(
    objective,
    initial_beta,
    jac=gradient,
    method="L-BFGS-B",
    options={
        "maxiter": 100,
        "ftol": 1e-9,
        "gtol": 1e-7,
        "maxls": 20,
        "disp": True,
    }
)

print("\n===== OPTIMIZATION RESULT =====")

print("Success:", result.success)
print("Message:", result.message)
print("Iterations:", result.nit)
print("Function evaluations:", result.nfev)

print("\nCoefficients:")
for name, coef in zip(features, result.x):
    print(f"{name}: {coef:.8f}")


# ============================================================
# 12. NUMERICAL HESSIAN
# ============================================================
#
# Estimate Hessian of the objective numerically.
# Only 5 parameters, so this is manageable.
# ============================================================

print("\n===== CALCULATE STANDARD ERRORS =====")


def numerical_hessian(beta, eps=1e-4):

    k = len(beta)

    H = np.zeros((k, k))

    for i in range(k):

        step = np.zeros(k)
        step[i] = eps

        g_plus = gradient(beta + step)
        g_minus = gradient(beta - step)

        H[:, i] = (
            g_plus - g_minus
        ) / (2 * eps)

    return H


H = numerical_hessian(result.x)

# Hessian of negative log-likelihood should be positive definite.
H = (H + H.T) / 2

try:

    covariance = np.linalg.inv(H)

    se = np.sqrt(
        np.diag(covariance)
    )

except np.linalg.LinAlgError:

    print("Hessian inversion failed.")

    covariance = np.linalg.pinv(H)

    se = np.sqrt(
        np.maximum(
            np.diag(covariance),
            0
        )
    )


# ============================================================
# 13. HR, CI, P-VALUE
# ============================================================

from scipy.stats import norm

beta = result.x

hazard_ratio = np.exp(beta)

ci_lower = np.exp(
    beta - 1.96 * se
)

ci_upper = np.exp(
    beta + 1.96 * se
)

z_value = beta / se

p_value = 2 * norm.sf(
    np.abs(z_value)
)


# ============================================================
# 14. RESULT TABLE
# ============================================================

result_table = pd.DataFrame({

    "variable": features,

    "coefficient": beta,

    "hazard_ratio_per_1_sd": hazard_ratio,

    "se": se,

    "z": z_value,

    "p_value": p_value,

    "ci_lower_95": ci_lower,

    "ci_upper_95": ci_upper,

    "mean_original": means,

    "std_original": stds,

})


# ============================================================
# 15. PRINT RESULT
# ============================================================

print("\n===== COX PH RESULTS =====")

print(
    result_table[
        [
            "variable",
            "coefficient",
            "hazard_ratio_per_1_sd",
            "se",
            "z",
            "p_value",
            "ci_lower_95",
            "ci_upper_95",
        ]
    ].to_string(index=False)
)


# ============================================================
# 16. SAVE
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

result_table.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n===== SAVED =====")
print(OUTPUT_PATH)

print("\n===== DONE =====")