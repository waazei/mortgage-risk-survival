from pathlib import Path
import pandas as pd


DATA_DIR = Path("data/analysis")
OUT_DIR = DATA_DIR / "loan_level"

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "survival_loan_level.parquet"


COLUMNS = [
    "loan_id",
    "credit_score",
    "original_cltv",
    "original_dti",
    "original_ltv",
    "original_interest_rate",
    "original_loan_term",
    "monthly_reporting_period",
    "loan_age",
    "current_interest_rate",
    "ltv",
    "event_type",
    "event",
]


files = sorted(DATA_DIR.glob("survival_*.parquet"))

print(f"Found {len(files)} quarterly files.")


# ============================================================
# STATE OF EACH LOAN
# ============================================================

loan_state = {}


for i, file in enumerate(files, start=1):

    print(
        f"\n[{i}/{len(files)}] Processing {file.name}"
    )

    df = pd.read_parquet(
        file,
        columns=COLUMNS
    )

    # --------------------------------------------------------
    # Sort by loan and loan age
    # --------------------------------------------------------

    df.sort_values(
        ["loan_id", "loan_age"],
        inplace=True
    )

    # --------------------------------------------------------
    # LAST OBSERVATION OF EACH LOAN IN THIS QUARTER
    # --------------------------------------------------------

    last = (
        df.groupby("loan_id", sort=False)
        .tail(1)
        .copy()
    )

    # --------------------------------------------------------
    # FIRST TERMINAL EVENT OF EACH LOAN IN THIS QUARTER
    # --------------------------------------------------------

    events = df[df["event"] == 1].copy()

    if len(events) > 0:

        events.sort_values(
            ["loan_id", "loan_age"],
            inplace=True
        )

        events = (
            events.groupby("loan_id", sort=False)
            .head(1)
            .copy()
        )

    # --------------------------------------------------------
    # UPDATE LOAN STATE
    # --------------------------------------------------------

    # First update with the latest observation
    for row in last.itertuples(index=False):

        loan_id = row.loan_id

        # If loan already has a terminal event,
        # do NOT overwrite it.
        if loan_id in loan_state:

            old_row = loan_state[loan_id]

            if old_row.event == 1:
                continue

        loan_state[loan_id] = row


    # --------------------------------------------------------
    # TERMINAL EVENT HAS PRIORITY
    # --------------------------------------------------------

    for row in events.itertuples(index=False):

        loan_id = row.loan_id

        # If this loan already has a terminal event,
        # keep the first one.
        if loan_id in loan_state:

            old_row = loan_state[loan_id]

            if old_row.event == 1:
                continue

        # Save terminal event
        loan_state[loan_id] = row


    print(
        f"Loans currently tracked: {len(loan_state):,}"
    )

    del df
    del last
    del events


# ============================================================
# CONVERT TO DATAFRAME
# ============================================================

print("\nCreating final loan-level dataset...")


result = pd.DataFrame.from_records(
    list(loan_state.values()),
    columns=COLUMNS
)


# ============================================================
# EVENT CODING
# ============================================================

result["default_event"] = (
    result["event_type"] == "Default"
).astype("int8")


result["cr_event"] = 0


result.loc[
    result["event_type"] == "Default",
    "cr_event"
] = 1


result.loc[
    result["event_type"] == "Voluntary Prepayment",
    "cr_event"
] = 2


result["cr_event"] = result["cr_event"].astype("int8")


# ============================================================
# BASIC CHECK
# ============================================================

print("\nEvent distribution:")

print(
    result["event_type"]
    .value_counts(dropna=False)
)


print("\nCR event distribution:")

print(
    result["cr_event"]
    .value_counts(dropna=False)
)


print(
    f"\nTotal loans: {len(result):,}"
)


# ============================================================
# SAVE
# ============================================================

result.to_parquet(
    OUTPUT,
    index=False
)


print("\n====================================")
print("DONE")
print("====================================")

print(
    f"Saved: {OUTPUT}"
)