from pathlib import Path

from load_data import load_origination
from clean_data import clean_origination


ZIP_FILE = Path(
    "data/raw/2026/historical_data_2026.zip"
)

OUTPUT_FILE = Path(
    "data/standardized/loan_master_2026.parquet"
)


def main():

    print("Dang doc Origination...")

    orig = load_origination(ZIP_FILE)

    print("So loan raw:", len(orig))

    print("\nDang clean data...")

    loan_master = clean_origination(orig)

    print("So loan sau khi clean:", len(loan_master))

    print("\nKiem tra duplicate loan_id:")

    duplicate_count = (
        loan_master["loan_id"]
        .duplicated()
        .sum()
    )

    print("Duplicate:", duplicate_count)

    print("\nKiem tra missing:")

    print(
        loan_master[
            [
                "loan_id",
                "credit_score",
                "original_ltv",
                "original_dti",
                "original_interest_rate",
                "original_loan_term"
            ]
        ].isna().sum()
    )

    # Tao folder neu chua ton tai
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    loan_master.to_parquet(
        OUTPUT_FILE,
        index=False
    )

    print("\nDa luu:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()