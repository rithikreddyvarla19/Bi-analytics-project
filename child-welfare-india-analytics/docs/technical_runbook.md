# Technical Runbook

## Purpose

This runbook explains how to set up, run, validate, and troubleshoot the Child Welfare Support Services Analytics - India project.

## Prerequisites

- Python 3.11 or newer recommended.
- Ability to install Python packages from `requirements.txt`.
- Jupyter support if running notebooks interactively.

## Environment Setup

From the project root:

```bash
pip install -r requirements.txt
```

Optional virtual environment setup:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Full Pipeline Run

Run these commands from the project root:

```bash
python src/generate_synthetic_data.py
python src/clean_validate_data.py
python src/kpi_metrics.py
python src/create_visuals.py
```

## Expected Outputs

### Raw Data

`data/raw/synthetic_child_welfare_cases_raw.csv`

Expected record count: 10,000 rows plus header.

### Processed Data

`data/processed/child_welfare_cases_clean.csv`

Expected clean record count: 9,771 rows plus header for the current random seed.

### Quality Outputs

- `data/processed/data_quality_summary.json`
- `data/processed/data_quality_issues.csv`

### KPI Outputs

- `data/processed/kpi_summary.json`
- `data/processed/kpi_summary_table.csv`

### Visual Outputs

Charts are generated in `visuals/`:

- `monthly_case_trends.png`
- `state_wise_case_volume.png`
- `referral_source_breakdown.png`
- `risk_level_distribution.png`
- `follow_up_completion_rate.png`
- `average_response_time_by_state.png`
- `service_type_utilization.png`
- `outcome_category_comparison.png`
- `support_amount_distribution_by_state.png`

## Reproducibility

The synthetic data generator uses a fixed NumPy random seed. Re-running the full pipeline should reproduce the same data and KPI outputs unless the generation or cleaning logic is changed.

## Validation Commands

Compile Python files:

```bash
python -m py_compile src/generate_synthetic_data.py src/clean_validate_data.py src/kpi_metrics.py src/create_visuals.py
```

Validate notebook JSON:

```bash
python -m json.tool notebooks/01_data_cleaning.ipynb
python -m json.tool notebooks/02_eda.ipynb
python -m json.tool notebooks/03_kpi_reporting.ipynb
```

## Data Quality Checks

The cleaning script validates:

- Unique case IDs.
- Expected state names.
- Valid referral dates.
- Non-negative support amounts.
- Standardized case status values.
- Expected date range.

Review the output file:

```bash
cat data/processed/data_quality_summary.json
```

On Windows PowerShell:

```powershell
Get-Content data\\processed\\data_quality_summary.json
```

## Troubleshooting

### Missing package error

Run:

```bash
pip install -r requirements.txt
```

### Raw file not found

Run the generator first:

```bash
python src/generate_synthetic_data.py
```

### Processed file not found

Run the cleaning script:

```bash
python src/clean_validate_data.py
```

### Charts not updating

Run the KPI and visual scripts after cleaning:

```bash
python src/kpi_metrics.py
python src/create_visuals.py
```

### Notebook paths fail

Open notebooks from the `notebooks/` folder or ensure the notebook working directory resolves `Path('..')` to the project root.

## Maintenance Notes

- Keep generated data clearly labeled as synthetic.
- Update documentation when changing KPI definitions.
- Re-run the full pipeline after editing generation or cleaning logic.
- Avoid adding sensitive or real-world case data to this repository.
