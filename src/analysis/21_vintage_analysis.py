import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path


# ============================================================
# 1. PATH
# ============================================================

LOAN_LEVEL = Path(
    "data/analysis/loan_level/survival_loan_level.parquet"
)

VINTAGE_MAP = Path(
    "data/analysis/loan_level/vintage_map.parquet"
)

VINTAGE_DATA = Path(
    "data/analysis/loan_level/vintage_loan_level.parquet"
)

RESULT_DIR = Path(
    "data/results"
)

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. BUILD VINTAGE MAP
# ============================================================

print("===== BUILD VINTAGE MAP =====")

vintage_frames = []

for year in range(2016, 2027):

    max_quarter = 1 if year == 2026 else 4

    for quarter in range(1, max_quarter + 1):

        path = Path(
            f"data/standardized/{year}/orig_{year}Q{quarter}.parquet"
        )

        if not path.exists():

            print(
                "MISSING:",
                path
            )

            continue

        print(
            "Reading:",
            path
        )

        temp = pd.read_parquet(
            path,
            columns=["loan_id"]
        )

        temp["vintage_year"] = year

        vintage_frames.append(
            temp
        )


vintage_map = pd.concat(
    vintage_frames,
    ignore_index=True
)

print(
    "\nVintage map rows:",
    len(vintage_map)
)

print(
    "\nVintage distribution:"
)

print(
    vintage_map[
        "vintage_year"
    ].value_counts()
    .sort_index()
)


vintage_map.to_parquet(
    VINTAGE_MAP,
    index=False
)

print(
    "\nSaved:",
    VINTAGE_MAP
)


# ============================================================
# 3. READ LOAN-LEVEL DATA
# ============================================================

print(
    "\n===== READ LOAN LEVEL ====="
)

loan = pd.read_parquet(
    LOAN_LEVEL,
    columns=[
        "loan_id",
        "loan_age",
        "cr_event"
    ]
)

print(
    "Loan-level rows:",
    len(loan)
)


# ============================================================
# 4. JOIN VINTAGE
# ============================================================

print(
    "\n===== JOIN VINTAGE ====="
)

vintage_data = loan.merge(
    vintage_map,
    on="loan_id",
    how="left",
    validate="many_to_one"
)

print(
    "Rows after join:",
    len(vintage_data)
)

print(
    "Missing vintage:",
    vintage_data[
        "vintage_year"
    ].isna().sum()
)


# ============================================================
# 5. SAVE VINTAGE DATA
# ============================================================

vintage_data.to_parquet(
    VINTAGE_DATA,
    index=False
)

print(
    "\nSaved:",
    VINTAGE_DATA
)


# ============================================================
# 6. CLEAN
# ============================================================

vintage_data["loan_age"] = pd.to_numeric(
    vintage_data["loan_age"],
    errors="coerce"
)

vintage_data["cr_event"] = pd.to_numeric(
    vintage_data["cr_event"],
    errors="coerce"
)

vintage_data["vintage_year"] = pd.to_numeric(
    vintage_data["vintage_year"],
    errors="coerce"
)

vintage_data = vintage_data.dropna(
    subset=[
        "loan_age",
        "cr_event",
        "vintage_year"
    ]
)

vintage_data["loan_age"] = (
    vintage_data["loan_age"]
    .astype(int)
)

vintage_data["cr_event"] = (
    vintage_data["cr_event"]
    .astype(int)
)

vintage_data["vintage_year"] = (
    vintage_data["vintage_year"]
    .astype(int)
)


# ============================================================
# 7. EVENT COUNTS
#
# 0 = Censored
# 1 = Default
# 2 = Voluntary Prepayment
# ============================================================

print(
    "\n===== AGGREGATE EVENTS ====="
)

counts = (
    vintage_data
    .groupby(
        [
            "vintage_year",
            "loan_age",
            "cr_event"
        ]
    )
    .size()
    .reset_index(
        name="count"
    )
)

print(
    "Aggregated rows:",
    len(counts)
)


# ============================================================
# 8. AALEN-JOHANSEN CIF BY VINTAGE
# ============================================================

print(
    "\n===== CALCULATE VINTAGE CIF ====="
)

vintage_results = []


for vintage_year in sorted(
    vintage_data[
        "vintage_year"
    ].unique()
):

    print(
        "Processing vintage:",
        vintage_year
    )

    sub = counts[
        counts["vintage_year"]
        == vintage_year
    ].copy()

    max_age = int(
        sub["loan_age"].max()
    )

    ages = np.arange(
        0,
        max_age + 1
    )

    table = pd.DataFrame({
        "loan_age": ages
    })

    # --------------------------------------------------------
    # Event counts
    # --------------------------------------------------------

    for event_code, name in [
        (0, "censored"),
        (1, "default"),
        (2, "prepayment")
    ]:

        temp = (
            sub[
                sub["cr_event"]
                == event_code
            ]
            .groupby("loan_age")["count"]
            .sum()
        )

        table[name] = (
            table["loan_age"]
            .map(temp)
            .fillna(0)
        )

    # --------------------------------------------------------
    # Number at risk
    # --------------------------------------------------------

    total_at_age = (
        table[
            [
                "censored",
                "default",
                "prepayment"
            ]
        ]
        .sum(axis=1)
    )

    table["at_risk"] = (
        total_at_age[
            ::-1
        ]
        .cumsum()
        [::-1]
    )

    # --------------------------------------------------------
    # Aalen-Johansen
    # --------------------------------------------------------

    survival = 1.0

    cif_default = 0.0

    cif_prepayment = 0.0

    survival_list = []

    default_cif_list = []

    prepayment_cif_list = []

    for _, row in table.iterrows():

        n_risk = row["at_risk"]

        d_default = row["default"]

        d_prepay = row["prepayment"]

        if n_risk > 0:

            cif_default += (
                survival
                * d_default
                / n_risk
            )

            cif_prepayment += (
                survival
                * d_prepay
                / n_risk
            )

            survival *= (
                1
                - (
                    d_default
                    + d_prepay
                )
                / n_risk
            )

        survival_list.append(
            survival
        )

        default_cif_list.append(
            cif_default
        )

        prepayment_cif_list.append(
            cif_prepayment
        )

    table["survival"] = (
        survival_list
    )

    table["default_cif"] = (
        default_cif_list
    )

    table["prepayment_cif"] = (
        prepayment_cif_list
    )

    table["vintage_year"] = (
        vintage_year
    )

    vintage_results.append(
        table
    )


# ============================================================
# 9. COMBINE
# ============================================================

vintage_curve = pd.concat(
    vintage_results,
    ignore_index=True
)

vintage_curve = vintage_curve[
    [
        "vintage_year",
        "loan_age",
        "at_risk",
        "default",
        "prepayment",
        "censored",
        "survival",
        "default_cif",
        "prepayment_cif"
    ]
]


# ============================================================
# 10. SAVE FULL CURVE
# ============================================================

curve_path = (
    RESULT_DIR
    / "vintage_cif_curve.csv"
)

vintage_curve.to_csv(
    curve_path,
    index=False
)

print(
    "\nSaved:",
    curve_path
)


# ============================================================
# 11. PD AT 12 / 24 / 36 / 60 MONTHS
# ============================================================

target_ages = [
    12,
    24,
    36,
    60
]

summary_rows = []


for vintage_year in sorted(
    vintage_curve[
        "vintage_year"
    ].unique()
):

    sub = vintage_curve[
        vintage_curve[
            "vintage_year"
        ]
        == vintage_year
    ]

    row = {
        "vintage_year": vintage_year
    }

    for age in target_ages:

        match = sub[
            sub["loan_age"]
            == age
        ]

        if len(match) == 0:

            row[
                f"PD_{age}m"
            ] = np.nan

            row[
                f"Prepayment_CIF_{age}m"
            ] = np.nan

            row[
                f"Survival_{age}m"
            ] = np.nan

        else:

            row[
                f"PD_{age}m"
            ] = (
                match[
                    "default_cif"
                ].iloc[0]
            )

            row[
                f"Prepayment_CIF_{age}m"
            ] = (
                match[
                    "prepayment_cif"
                ].iloc[0]
            )

            row[
                f"Survival_{age}m"
            ] = (
                match[
                    "survival"
                ].iloc[0]
            )

    summary_rows.append(
        row
    )


summary = pd.DataFrame(
    summary_rows
)


# ============================================================
# 12. CONVERT TO %
# ============================================================

for age in target_ages:

    summary[
        f"PD_{age}m_pct"
    ] = (
        summary[
            f"PD_{age}m"
        ]
        * 100
    )

    summary[
        f"Prepayment_CIF_{age}m_pct"
    ] = (
        summary[
            f"Prepayment_CIF_{age}m"
        ]
        * 100
    )


# ============================================================
# 13. SAVE SUMMARY
# ============================================================

summary_path = (
    RESULT_DIR
    / "vintage_cif_summary.csv"
)

summary.to_csv(
    summary_path,
    index=False
)

print(
    "\n===== VINTAGE SUMMARY ====="
)

print(
    summary.to_string(
        index=False
    )
)

print(
    "\nSaved:",
    summary_path
)


# ============================================================
# 14. PLOT
# ============================================================

plt.figure(
    figsize=(11, 7)
)

for vintage_year in sorted(
    vintage_curve[
        "vintage_year"
    ].unique()
):

    sub = vintage_curve[
        vintage_curve[
            "vintage_year"
        ]
        == vintage_year
    ]

    plt.plot(
        sub["loan_age"],
        sub["default_cif"] * 100,
        label=str(
            vintage_year
        )
    )


plt.xlabel(
    "Loan Age (months)"
)

plt.ylabel(
    "Default CIF (%)"
)

plt.title(
    "Default CIF by Origination Vintage"
)

plt.legend(
    title="Vintage"
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()


plot_path = (
    RESULT_DIR
    / "vintage_default_cif.png"
)

plt.savefig(
    plot_path,
    dpi=150
)

plt.close()


print(
    "\nSaved:",
    plot_path
)

print(
    "\n===== VINTAGE ANALYSIS COMPLETE ====="
)