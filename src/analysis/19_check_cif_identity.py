import pandas as pd
from pathlib import Path
from lifelines import AalenJohansenFitter, KaplanMeierFitter


# ============================================================
# 1. READ DATA
# ============================================================

INPUT = Path(
    "data/analysis/loan_level/survival_loan_level.parquet"
)

df = pd.read_parquet(
    INPUT,
    columns=[
        "loan_id",
        "loan_age",
        "cr_event"
    ]
)

df["loan_age"] = pd.to_numeric(
    df["loan_age"],
    errors="coerce"
)

df["cr_event"] = pd.to_numeric(
    df["cr_event"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "loan_age",
        "cr_event"
    ]
)

print("Rows:", len(df))

print("\nEvent distribution:")
print(
    df["cr_event"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 2. KAPLAN-MEIER
# ============================================================

km = KaplanMeierFitter()

km.fit(
    durations=df["loan_age"],
    event_observed=(df["cr_event"] != 0)
)


# ============================================================
# 3. AALEN-JOHANSEN - DEFAULT
# ============================================================

aj_default = AalenJohansenFitter()

aj_default.fit(
    durations=df["loan_age"],
    event_observed=df["cr_event"],
    event_of_interest=1
)


# ============================================================
# 4. AALEN-JOHANSEN - PREPAYMENT
# ============================================================

aj_prepay = AalenJohansenFitter()

aj_prepay.fit(
    durations=df["loan_age"],
    event_observed=df["cr_event"],
    event_of_interest=2
)


# ============================================================
# 5. FUNCTION: GET CIF AT TIME
# ============================================================

def get_cif_at_time(aj, t):

    cif = aj.cumulative_density_

    # Chỉ lấy các thời điểm <= t
    eligible = cif.index[cif.index <= t]

    # Nếu chưa có event trước thời điểm t
    if len(eligible) == 0:
        return 0.0

    # Lấy thời điểm gần nhất nhưng không vượt quá t
    last_time = eligible[-1]

    return float(
        cif.loc[last_time].iloc[0]
    )


# ============================================================
# 6. CALCULATE 12 / 24 / 36 / 60 MONTHS
# ============================================================

times = [
    12,
    24,
    36,
    60
]

rows = []

for t in times:

    # Survival probability
    survival = float(
        km.survival_function_at_times(t).iloc[0]
    )

    # Default CIF
    default_cif = get_cif_at_time(
        aj_default,
        t
    )

    # Prepayment CIF
    prepay_cif = get_cif_at_time(
        aj_prepay,
        t
    )

    # Identity:
    # S(t) + CIF_Default(t) + CIF_Prepayment(t) ≈ 1

    identity = (
        survival
        + default_cif
        + prepay_cif
    )

    rows.append({
        "loan_age_month": t,
        "survival": survival,
        "default_cif": default_cif,
        "prepayment_cif": prepay_cif,
        "sum": identity,
        "difference_from_1": identity - 1
    })


# ============================================================
# 7. RESULT TABLE
# ============================================================

result = pd.DataFrame(rows)


print("\n===== CIF IDENTITY CHECK =====")

print(
    result.to_string(
        index=False
    )
)


# ============================================================
# 8. DEFAULT CIF
# ============================================================

print("\n===== DEFAULT CIF (%) =====")

for _, r in result.iterrows():

    print(
        f"{int(r['loan_age_month'])}M: "
        f"{r['default_cif'] * 100:.6f}%"
    )


# ============================================================
# 9. PREPAYMENT CIF
# ============================================================

print("\n===== PREPAYMENT CIF (%) =====")

for _, r in result.iterrows():

    print(
        f"{int(r['loan_age_month'])}M: "
        f"{r['prepayment_cif'] * 100:.6f}%"
    )


# ============================================================
# 10. SAVE RESULT
# ============================================================

output = Path(
    "data/results/cif_identity_check.csv"
)

result.to_csv(
    output,
    index=False
)

print("\nSaved:", output)