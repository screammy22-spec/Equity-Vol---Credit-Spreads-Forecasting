# Do Bond Markets Forecast Equity Volatility? Evidence from a Large Issuer-Level Panel

**Author:** Jonathan Chung · University of Cambridge · [ycc44@cam.ac.uk](mailto:ycc44@cam.ac.uk)

---

## Overview

This repository contains the code, data pipeline, and paper for a study that asks whether **credit-spread variables improve out-of-sample forecasts of firm-level equity volatility** beyond what autoregressive and equity-market predictors already capture.

We estimate a **HAR-X panel model** (Heterogeneous Autoregressive model with exogenous regressors) on a large issuer-level panel of US corporate bond issuers. The model uses **Ridge regression** with walk-forward expanding-window evaluation and entity demeaning to absorb firm fixed effects.

### Key Finding

Adding five credit-spread variables to the forecasting model raises the out-of-sample R² from **+1.19%** (AR + Equity only) to **+2.03%** (Full model) — a statistically significant improvement confirmed by Diebold–Mariano and Clark–West tests (p < 0.01). Credit spreads carry information about future equity volatility that is **not already captured** by equity-market variables.

---

## Data

| Item | Description |
|---|---|
| **Source** | Open Source Asset Pricing (bonds) + LSEG Datastream (equity, Worldscope accounting) |
| **Sample** | Feb 2003 – Aug 2022 (235 months) |
| **Panel** | 3,305 unique issuers · 288,628 issuer-month observations |
| **Target** | Δlog(σ) — monthly change in log realised equity volatility |
| **Benchmark** | Random walk: ŷ = log(σ_t), i.e. Δ̂ = 0 |

The raw data file (`final_data_modified.csv`) is excluded from the repository via `.gitignore` due to WRDS licensing restrictions. The variable definitions are documented in `variable_summary_updated.xlsx`.

---

## Model

### Specification

```
Δlog(σ_{j,t+1}) = α_j + Σ β_k · AR_k(j,t) + Σ γ_m · X_{j,t,m} + ε_{j,t}
```

Level prediction: `ŷ_{j,t+1} = log(σ_{j,t}) + predicted Δ`

### Features (16 total)

| Group | Features | Description |
|---|---|---|
| **AR (6)** | `dm_lag1`, `dm_lag3`, `dm_lag6`, `dm_lag12`, `dlv_lag1`, `dlv_lag3` | Autoregressive lags of demeaned log-volatility and log-volume |
| **Credit (5)** | `f_CS`, `var95`, `cs_6m_delta`, `f_rating`, `exretnc` | Credit spread level, 95th-percentile VaR, 6-month spread momentum, credit rating, excess bond returns |
| **Equity (5)** | `DY`, `WC08316`, `VO`, `WC09904`, `P` | Dividend yield, operating profit margin, trading volume, price-to-sales, stock price level |

Features were selected via Clark & McCracken (2012) one-at-a-time screening from an initial candidate set of 400+ variables.

### Estimation

- **Estimator:** RidgeCV with leave-one-out cross-validation (closed-form)
- **Preprocessing:** Entity demeaning (firm fixed effects), RobustScaler, ±3σ winsorisation
- **Evaluation:** Walk-forward expanding window (minimum 80 training dates)
- **Metric:** Out-of-sample R² vs random walk benchmark

---

## Results

### Ablation Study

| Model | Features | R²_OOS (All) | R²_OOS (SIC 36xx) |
|---|---|---|---|
| AR Only | 6 | +0.65% | +0.02% |
| AR + Credit | 11 | +1.79% | +1.28% |
| AR + Equity | 11 | +1.19% | +0.73% |
| **Full Model** | **16** | **+2.03%** | **+1.62%** |
| Credit Only | 5 | +0.55% | +0.29% |

### Marginal Contributions

- **Credit marginal** (Full − AR+Equity): **+0.84 pp**
- **Equity marginal** (Full − AR+Credit): **+0.25 pp**
- Credit contributes roughly **3× more** than equity to the full model

### Statistical Significance (Full vs AR+Equity)

| Test | Sample | t-stat | p-value |
|---|---|---|---|
| Diebold–Mariano (NW HAC, 4 lags) | All | 2.89 | 0.002 |
| Clark–West (NW HAC, 4 lags) | All | 3.52 | <0.001 |
| Diebold–Mariano (NW HAC, 4 lags) | SIC 36xx | 2.53 | 0.006 |
| Clark–West (NW HAC, 4 lags) | SIC 36xx | 2.77 | 0.003 |

---

## Repository Structure

```
├── src/credit_spread_vol/         # Installable Python package
│   ├── __init__.py                #   Public API & version
│   ├── data.py                    #   Data loading & issuer-level aggregation
│   ├── features.py                #   Feature construction & ablation groups
│   ├── model.py                   #   Walk-forward RidgeCV engine
│   ├── testing.py                 #   DM / CW hypothesis tests (NW HAC)
│   └── plotting.py                #   Publication-quality figure utilities
│
├── scripts/
│   ├── run_ablation.py            # Run 5-group ablation study
│   ├── run_tests.py               # DM & CW tests (4 comparisons A–D)
│   ├── generate_paper_assets.py   # All figures (1–7) & tables (1–7)
│   ├── variable_screening.py      # Clark & McCracken one-at-a-time screening
│   └── log_transform_evidence.py  # Log-transform justification plots
│
├── slurm/
│   ├── slurm_ablation.sh          # HPC job: run ablation
│   ├── slurm_post_ablation.sh     # HPC job: hypothesis tests + figures
│   └── slurm_screening.sh         # HPC job: variable screening
│
├── paper/
│   ├── main.tex                   # Full paper (LaTeX)
│   ├── slides.tex                 # Presentation slides (Beamer)
│   └── references.bib             # Bibliography
│
├── results/
│   ├── final_ablation/            # Model predictions & ablation summary
│   ├── paper/                     # Publication-quality figures (PDF & PNG)
│   └── variable_screening/        # Screening results (400+ candidates)
│
├── final_data_modified.csv        # Raw panel data (git-ignored)
├── variable_summary_updated.xlsx  # Variable definitions & sources
├── pyproject.toml                 # Project metadata & dependencies
├── CITATION.cff                   # Citation metadata
└── LICENSE                        # MIT License
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/ScreaM835/CME_Group_Model.git
cd CME_Group_Model

# Create virtual environment and install the package
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Requirements

- Python ≥ 3.10
- Access to `final_data_modified.csv` (WRDS-sourced panel data)

Dependencies (installed automatically): numpy, pandas, scikit-learn, scipy, openpyxl, matplotlib.

---

## Package API

The `credit_spread_vol` package exposes the full research pipeline:

```python
from credit_spread_vol import (
    # Data
    load_data, aggregate_to_issuer, load_and_prepare,
    # Features
    build_features, ABLATION_GROUPS,
    # Model
    walk_forward, r2_oos, ALPHAS, MIN_TRAIN,
    # Testing
    newey_west_se, compute_dm_cw, compute_dm_cw_vs_rw,
)
```

| Module | Key exports | Description |
|---|---|---|
| `data` | `load_data`, `aggregate_to_issuer`, `load_and_prepare` | Load CSV, aggregate bonds to issuer-month level |
| `features` | `build_features`, `ABLATION_GROUPS`, `FULL_COLS` | AR lags, entity demeaning, 5 ablation groups |
| `model` | `walk_forward`, `r2_oos`, `ALPHAS`, `MIN_TRAIN` | Expanding-window RidgeCV with predictions & coefficients |
| `testing` | `newey_west_se`, `compute_dm_cw`, `compute_dm_cw_vs_rw` | Diebold–Mariano & Clark–West with Newey–West HAC SEs |
| `plotting` | `apply_paper_style`, `nice_label`, `save_fig` | Matplotlib rcParams, LaTeX labels, dual PNG+PDF export |

---

## Reproducing the Results

### Running Locally

```bash
# Step 1: Run the ablation study (≈10 min on 4 cores)
python scripts/run_ablation.py

# Step 2: Run hypothesis tests (regenerates sub-model predictions)
python scripts/run_tests.py --regen

# Step 3: Generate all figures and tables for the paper
python scripts/generate_paper_assets.py
```

### Running on HPC (SLURM)

```bash
# Run ablation on cluster
sbatch slurm/slurm_ablation.sh

# After ablation completes, run post-processing
sbatch slurm/slurm_post_ablation.sh
```

### Hypothesis Test Comparisons

`run_tests.py` performs four comparisons with Diebold–Mariano and Clark–West tests:

| ID | Comparison | Paper reference |
|---|---|---|
| A | Full model vs Random Walk | Table 2 |
| B | Full model vs AR-only | Table 2 |
| C | AR + Credit vs AR-only | Table 2 |
| D | Full model vs AR + Equity | Table 3 |

---

## Figures

All figures are generated by `scripts/generate_paper_assets.py`:

| Figure | Description |
|---|---|
| Fig 1 | Cumulative R²_OOS over time |
| Fig 2 | Ablation bar chart (5 model variants) |
| Fig 3 | Ridge coefficient paths across expanding windows |
| Fig 4a/b | Top-10 feature importance (All sectors / SIC 36xx) |
| Fig 5a/b | Date-level R² distribution and rolling average |
| Fig 6 | 16×16 feature correlation matrix |
| Fig 7 | Sector-level R²_OOS performance |

---

## Citation

```bibtex
@misc{chung2026bond,
  author       = {Chung, Jonathan},
  title        = {Do Bond Markets Forecast Equity Volatility? Evidence from a Large Issuer-Level Panel},
  year         = {2026},
  howpublished = {\url{https://github.com/ScreaM835/CME_Group_Model}},
}
```

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
