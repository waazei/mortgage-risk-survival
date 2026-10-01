import zipfile
from io import BytesIO

import pandas as pd


ORIG_COLUMNS = [
    "credit_score",
    "first_payment_date",
    "first_time_homebuyer_flag",
    "maturity_date",
    "msa",
    "mortgage_insurance_pct",
    "number_of_units",
    "occupancy_status",
    "original_cltv",
    "original_dti",
    "original_upb",
    "original_ltv",
    "original_interest_rate",
    "channel",
    "prepayment_penalty_flag",
    "amortization_type",
    "property_state",
    "property_type",
    "postal_code",
    "loan_id",
    "loan_purpose",
    "original_loan_term",
    "number_of_borrowers",
    "seller_name",
    "servicer_name",
    "super_conforming_flag",
    "pre_relief_loan_id",
    "special_eligibility_program",
    "relief_refinance_indicator",
    "property_valuation_method",
    "interest_only_indicator",
]


PERF_COLUMNS = [
    "loan_id",
    "monthly_reporting_period",
    "current_actual_upb",
    "current_delinquency_status",
    "loan_age",
    "remaining_months_to_maturity",
    "defect_settlement_date",
    "modification_flag",
    "zero_balance_code",
    "zero_balance_effective_date",
    "current_interest_rate",
    "current_non_interest_bearing_upb",
    "ddlpi",
    "mi_recoveries",
    "net_sale_proceeds",
    "non_mi_recoveries",
    "expenses",
    "legal_costs",
    "maintenance_preservation_costs",
    "taxes_insurance",
    "misc_expenses",
    "actual_loss_calculation",
    "modification_cost",
    "step_modification_flag",
    "deferred_payment_plan",
    "ltv",
    "mi_type",
    "deferred_upb",
    "delinquent_accrued_interest",
    "zero_balance_removal_upb",
    "repurchase_make_whole_proceeds",
    "current_actual_upb_2",
    "mortgage_insurance_cancellation_indicator",
    "servicer_name",
    "bankruptcy_cramdown_costs",
]


def read_nested_zip(zip_path):

    with zipfile.ZipFile(zip_path, "r") as outer_zip:

        nested_zip_name = outer_zip.namelist()[0]

        nested_data = outer_zip.read(nested_zip_name)

        with zipfile.ZipFile(BytesIO(nested_data), "r") as inner_zip:

            files = inner_zip.namelist()

            orig_file = [
                x for x in files
                if x.startswith("orig_")
            ][0]

            perf_file = [
                x for x in files
                if x.startswith("perf_")
            ][0]

            return inner_zip, orig_file, perf_file


def load_origination(zip_path):

    with zipfile.ZipFile(zip_path, "r") as outer_zip:

        nested_zip_name = outer_zip.namelist()[0]

        nested_data = outer_zip.read(nested_zip_name)

        with zipfile.ZipFile(BytesIO(nested_data), "r") as inner_zip:

            orig_file = [
                x for x in inner_zip.namelist()
                if x.startswith("orig_")
            ][0]

            with inner_zip.open(orig_file) as f:

                df = pd.read_csv(
                    f,
                    sep="|",
                    header=None,
                    names=ORIG_COLUMNS,
                    dtype=str
                )

    return df


def load_performance(zip_path):

    with zipfile.ZipFile(zip_path, "r") as outer_zip:

        nested_zip_name = outer_zip.namelist()[0]

        nested_data = outer_zip.read(nested_zip_name)

        with zipfile.ZipFile(BytesIO(nested_data), "r") as inner_zip:

            perf_file = [
                x for x in inner_zip.namelist()
                if x.startswith("perf_")
            ][0]

            with inner_zip.open(perf_file) as f:

                df = pd.read_csv(
                    f,
                    sep="|",
                    header=None,
                    names=PERF_COLUMNS,
                    dtype=str
                )

    return df