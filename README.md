# Mortgage Default and Prepayment Survival Analysis

Project backend for processing Freddie Mac Single-Family Loan-Level data and estimating mortgage default and voluntary prepayment risk.

## Pipeline

The pipeline creates quarterly survival files, reduces performance histories to one final record per loan, prepares model data, estimates survival and competing-risk models, and validates the generated artifacts.

| Stage | Command | Output |
|---|---|---|
| Quarterly survival files | `python run_backend.py survival` | `data/analysis/survival_YYYYQn.parquet` |
| One record per loan | `python run_backend.py loan-level` | `data/analysis/loan_level/survival_loan_level.parquet` |
| Models and audit | `python run_backend.py models` | Tables, figures, and `data/results/final_audit.csv` |
| Run all stages | `python run_backend.py all` | All outputs above |

## Local dashboard

After generating the result CSV files, start the dashboard from the repository root:

```powershell
python dashboard_server.py
```

Open `http://127.0.0.1:8765` in a browser. The dashboard reads the generated results from `data/results/` and refreshes when you click the refresh button. It uses only the Python standard library and local frontend files; no separate frontend packages are required. Press `Ctrl+C` in the server terminal to stop it.

Commands should be run from the repository root. The runner stops at the first failed step and preserves its error code. Existing quarterly survival files are skipped, so the survival stage can resume after interruption. The loan-level and model stages rebuild their outputs from their inputs.

## Setup

Use Python 3.11 or newer in a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Parquet support is provided by PyArrow. Model scripts use NumPy/SciPy and lifelines; figures use Matplotlib.

## Install on another Windows computer

Create a compact source package on this computer:

```powershell
.\package-source.ps1
```

Send the generated `mortgage-risk-source-<date>.zip` file and extract it on the other computer. The ZIP contains the code, dashboard, and small `data/results/` tables and figures; it excludes raw archives and large standardized/analysis Parquet files.

Install Python 3.11 or newer, open PowerShell in the extracted project folder, then run:

```powershell
.\setup.ps1 -DashboardOnly
.\.venv\Scripts\python.exe dashboard_server.py
```

Open `http://127.0.0.1:8765` and keep the terminal open while using the dashboard. This compact package displays aggregate charts and model results. Loan ID lookup requires the separate `data/analysis/loan_level/survival_loan_level.parquet` file. Running the full analysis requires the source data below.

For a computer that will rerun the complete analysis, install all dependencies instead:

```powershell
.\setup.ps1
```

Then provide the input data under `data/` before running the pipeline. Obtain the source archives from an authorized Freddie Mac distribution, or transfer the required data separately using a method allowed for your project. Do not put raw archives or loan-level Parquet files in a public repository. The full pipeline can create tens of gigabytes of intermediate files and needs substantial disk space and time.

### Note about cloning this repository

This working repository currently tracks many generated Parquet files. A normal `git clone` may download many gigabytes even though the code itself is small. Use the source-package steps above to share the dashboard without those files. For a clean public source repository, generated datasets need to be removed from Git tracking and its history; an ignore rule alone does not remove files already tracked.

## Input data

Place the source quarterly Freddie Mac archives in `data/raw/<year>/historical_data_<year>.zip`. The current loader expects nested quarterly archives containing `orig_<year>Q<quarter>.txt` and `perf_<year>Q<quarter>.txt`. The quarterly standardization process is in `src/data/build_quarterly_parquet.py`; its inputs are the raw archives and its outputs are the paired `orig_*.parquet` / `perf_*.parquet` files under `data/standardized/<year>/`.

The development workspace has standardized quarterly Parquet files for 2016–2026 and survival Parquet outputs for 2016Q1–2026Q1. These large files are not included in the compact source package. To rebuild them from raw archives, run the standardization script first from the repository root:

```powershell
python src/data/build_quarterly_parquet.py
python run_backend.py all
```

The raw archives are large. Ensure adequate disk space and memory before rebuilding. Do not commit raw loan-level data or generated Parquet files to a public repository.

## Event and model definitions

- `event=0`: right-censored at the last observed performance record.
- `event=1`: a terminal event (default or voluntary payoff).
- `cr_event=0/1/2`: censored / default / voluntary prepayment.
- Freddie Mac zero-balance codes 02, 03, and 09 are treated as default; code 01 is voluntary prepayment. Other codes are censored under the current study definition.
- The cause-specific Cox model estimates cause-specific hazards. Aalen–Johansen cumulative incidence is the primary estimate of default probability in the presence of prepayment as a competing event.
- The Kaplan–Meier output treats both default and prepayment as events; interpret it as all-cause termination survival, not default probability.
- Fine–Gray is implemented directly in `src/analysis/20_fine_gray_default.py`. Its estimates and uncertainty calculations should be reported with that implementation limitation disclosed and checked against a validated reference implementation before high-stakes use.
- The final audit reports separate `UNVERIFIED` method/design items: no external Fine–Gray benchmark, no fitted time-varying Cox model, and no out-of-sample validation. If an older Fine–Gray CSV lacks optimizer metadata, its numerical convergence is also unverified until that estimator is rerun. These items are not reported as passes. Quarterly time-varying-data checks only describe the panel; they are not evidence that a time-varying model was fitted.
- The dashboard's Research Review page records a literature map, limits on economic interpretation, a bounded connection to the 2008 crisis, and oral-defense prompts. It does not replace reading and synthesizing the papers or the group's required AI-use log and presentation.
- This sample begins in 2016 and has no 2008 crisis-period observations or macroeconomic/home-price covariates in the fitted Cox tables. Results therefore describe associations in the observed sample; they cannot identify causal channels or explain the 2008 crisis.

The loan-level dataset retains the last observed row for censored loans and the first observed terminal-event row for loans with a terminal event. Model covariates are prepared in `08_prepare_cox_data.py`; missing credit score, original LTV, and DTI use median imputation plus missingness indicators. Event type is retained in the Cox input so the cause-specific models can distinguish defaults from prepayments. Complete-case sensitivity results are generated separately.

## Outputs and audit

Model outputs are written to `data/results/`. The final audit checks required result tables and figures, unique loan IDs, time/event coding consistency, Cox convergence fields, custom Fine–Gray numerical convergence metadata when available, and CIF identity. Fine–Gray now refuses to save if optimization fails or the observed information is not positive definite; this does not replace reference-implementation benchmarking. The audit writes a machine-readable `final_audit.csv` with `PASS`, `FAIL`, and `UNVERIFIED` statuses. Unverified method/design items remain visible but do not cause a data-integrity failure exit code. Passing these checks does not establish causal validity or replace independent methodological review.

## Research evidence and interpretation

The dashboard has a Research Review subpage under Risk Analysis. Starting papers include Cox (1972, [DOI](https://doi.org/10.1111/j.2517-6161.1972.tb00899.x)); Deng, Quigley & Van Order (1996, [DOI](https://doi.org/10.1016/0166-0462(95)02116-7)); their 1999 mortgage-termination competing-risk study ([eScholarship](https://escholarship.org/uc/item/96r560pg)); Fine & Gray (1999, [DOI](https://doi.org/10.1080/01621459.1999.10474144)); An & Qi (2012, [DOI](https://doi.org/10.1080/10835547.2012.12091323)); and the [Financial Crisis Inquiry Report](https://www.govinfo.gov/features/financial-crisis-inquiry-report) for the 2008-crisis governance context. The project still needs a student-authored synthesis and properly formatted references for the course submission.

## Current evidence gaps

- **Fine–Gray:** custom estimator only; its coefficients are provisional until compared on the same observations and event/censoring conventions against `cmprsk::crr` (or another validated implementation), including standard errors and convergence behavior.
- **Time-varying Cox:** not fitted. The existing quarterly checks report observation counts and data-quality fields, not model estimates. A defensible fit needs correctly ordered start/stop intervals and covariates observed before each interval's risk time.
- **Validation:** the audit is primarily artifact, coding, and internal-identity validation. No temporal holdout, calibration, discrimination, or independent external validation is currently available.
- **Presentation:** the dashboard now supplies a literature map and defense prompts, but the group still must produce its own synthesis, financial interpretation, cross-review, slides, AI-use log, and live code defense.

## Repository layout

```text
data/raw/             Source archives (not committed)
data/standardized/    Quarterly origination and performance Parquet
data/analysis/        Quarterly and loan-level analysis datasets
data/results/         Model tables, diagnostics, and figures
src/data/             Loading, cleaning, and dataset construction
src/analysis/         Survival, competing-risk, and sensitivity analyses
run_backend.py        Ordered pipeline runner
```
