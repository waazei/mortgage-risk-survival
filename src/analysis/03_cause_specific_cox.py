"""Fit cause-specific Cox models for default and voluntary prepayment."""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm


INPUT = Path("data/analysis/loan_level/cox_data.parquet")
OUTPUT_DIR = Path("data/results")
FEATURES = [
    "credit_score",
    "original_ltv",
    "original_dti",
    "original_interest_rate",
    "original_loan_term",
]
CAUSES = {
    1: ("Default", "cause_specific_cox_default.csv"),
    2: ("Voluntary Prepayment", "cause_specific_cox_prepayment.csv"),
}


def fit_one_cause(time: np.ndarray, cause: np.ndarray, X: np.ndarray, label: str) -> pd.DataFrame:
    """Fit Breslow partial likelihood using age-grouped risk-set sums."""
    max_age = int(time.max())
    n_features = X.shape[1]
    event_count = np.bincount(time[cause == 1], minlength=max_age + 1)
    event_x = np.zeros((max_age + 1, n_features), dtype=float)
    np.add.at(event_x, time[cause == 1], X[cause == 1])
    event_ages = np.flatnonzero(event_count)
    if not len(event_ages):
        raise ValueError(f"No events found for cause: {label}")

    def risk_sums(beta: np.ndarray, need_second_moment: bool = False):
        eta = np.clip(X @ beta, -40, 40)
        eta_max = float(eta.max())
        weights = np.exp(eta - eta_max)
        by_age = np.bincount(time, weights=weights, minlength=max_age + 1)
        risk0 = np.cumsum(by_age[::-1])[::-1]
        by_age_x = np.empty((max_age + 1, n_features), dtype=float)
        for j in range(n_features):
            by_age_x[:, j] = np.bincount(
                time, weights=weights * X[:, j], minlength=max_age + 1
            )
        risk1 = np.cumsum(by_age_x[::-1], axis=0)[::-1]
        if not need_second_moment:
            return eta_max, risk0, risk1, None
        by_age_xx = np.empty((max_age + 1, n_features, n_features), dtype=float)
        for j in range(n_features):
            for k in range(j, n_features):
                values = np.bincount(
                    time,
                    weights=weights * X[:, j] * X[:, k],
                    minlength=max_age + 1,
                )
                by_age_xx[:, j, k] = values
                by_age_xx[:, k, j] = values
        risk2 = np.cumsum(by_age_xx[::-1], axis=0)[::-1]
        return eta_max, risk0, risk1, risk2

    def objective(beta: np.ndarray) -> float:
        eta_max, risk0, _, _ = risk_sums(beta)
        loglik = 0.0
        for age in event_ages:
            loglik += event_x[age] @ beta - event_count[age] * (
                eta_max + np.log(risk0[age])
            )
        return -float(loglik)

    def gradient(beta: np.ndarray) -> np.ndarray:
        _, risk0, risk1, _ = risk_sums(beta)
        grad = np.zeros(n_features, dtype=float)
        for age in event_ages:
            grad += event_x[age] - event_count[age] * risk1[age] / risk0[age]
        return -grad

    print(f"\nFitting cause-specific Cox: {label}", flush=True)
    result = minimize(
        objective,
        np.zeros(n_features),
        jac=gradient,
        method="L-BFGS-B",
        options={"maxiter": 200, "ftol": 1e-10, "gtol": 1e-7},
    )
    if not result.success:
        raise RuntimeError(f"Cox optimization failed for {label}: {result.message}")

    beta = result.x
    _, risk0, risk1, risk2 = risk_sums(beta, need_second_moment=True)
    information = np.zeros((n_features, n_features), dtype=float)
    for age in event_ages:
        mean_x = risk1[age] / risk0[age]
        covariance = risk2[age] / risk0[age] - np.outer(mean_x, mean_x)
        information += event_count[age] * covariance
    covariance = np.linalg.pinv(information, hermitian=True)
    se = np.sqrt(np.maximum(np.diag(covariance), 0))
    if not np.isfinite(se).all() or (se <= 0).any():
        raise RuntimeError(f"Invalid standard errors for {label}; information matrix is unstable")

    z = beta / se
    return pd.DataFrame({
        "variable": FEATURES,
        "coefficient": beta,
        "hazard_ratio_per_1_sd": np.exp(beta),
        "se": se,
        "z": z,
        "p_value": 2 * norm.sf(np.abs(z)),
        "ci_lower_95": np.exp(beta - 1.96 * se),
        "ci_upper_95": np.exp(beta + 1.96 * se),
        "events": int(event_count.sum()),
        "converged": bool(result.success),
    })


def main() -> None:
    columns = ["loan_age", "cr_event", *FEATURES]
    print(f"Loading {INPUT} ...", flush=True)
    df = pd.read_parquet(INPUT, columns=columns)
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=columns)
    time_values = df["loan_age"].to_numpy(dtype=float)
    if (time_values < 0).any() or not np.allclose(time_values, np.round(time_values)):
        raise ValueError("loan_age must contain non-negative whole-month values")

    time = np.round(time_values).astype(np.int32)
    event_type = df["cr_event"].to_numpy(dtype=np.int8)
    X = df[FEATURES].to_numpy(dtype=float)
    means = X.mean(axis=0)
    stds = X.std(axis=0)
    if (stds == 0).any() or not np.isfinite(stds).all():
        raise ValueError("A model predictor has zero or invalid standard deviation")
    X = (X - means) / stds

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for code, (label, filename) in CAUSES.items():
        result = fit_one_cause(time, (event_type == code).astype(np.int8), X, label)
        result.to_csv(OUTPUT_DIR / filename, index=False)
        print(f"Saved {OUTPUT_DIR / filename}", flush=True)


if __name__ == "__main__":
    main()
