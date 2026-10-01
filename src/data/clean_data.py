import pandas as pd


def clean_origination(df):
    """
    Lam sach du lieu Origination.
    Khong thay doi raw data.
    """

    df = df.copy()

    # -----------------------------
    # 1. Chuan hoa chuoi
    # -----------------------------

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.strip()

    # -----------------------------
    # 2. Chuyen cac gia tri dac biet
    # thanh missing
    # -----------------------------

    missing_values = [
        "",
        " ",
        "999",
        "9999",
        "999999"
    ]

    df = df.replace(missing_values, pd.NA)

for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].astype("string")

    # -----------------------------
    # 3. Chuyen cac bien so sang numeric
    # -----------------------------

    numeric_columns = [
        "credit_score",
        "original_cltv",
        "original_dti",
        "original_upb",
        "original_ltv",
        "original_interest_rate",
        "original_loan_term",
        "number_of_borrowers"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # -----------------------------
    # 4. Chuyen ngay thang
    # -----------------------------

    df["first_payment_date"] = pd.to_datetime(
        df["first_payment_date"],
        format="%Y%m",
        errors="coerce"
    )

    df["maturity_date"] = pd.to_datetime(
        df["maturity_date"],
        format="%Y%m",
        errors="coerce"
    )

    # -----------------------------
    # 5. Tao origination vintage
    # -----------------------------

    df["origination_vintage"] = (
        df["first_payment_date"]
        .dt.year
    )

    return df