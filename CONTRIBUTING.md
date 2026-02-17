# Contributing to Medicaid Spend Watch

Thank you for your interest in improving Medicaid oversight in Washington!

## How to Contribute

### 1. Porting to a New County
The v3.0 architecture is designed for one-click portability. To port this to another county:
- Update `TARGET_COUNTY` and `TARGET_STATE` in **[src/config.py](file:///Users/thomasbcox/Projects/wa-clark-medicaid-spend-watch/src/config.py)**.
- Ensure the zip code scope for your county is updated in `scripts/get_county_npis.py` (or provide a JSON scope file).
- Run `python src/pipeline.py` to rebuild the jurisdictional database.

### 2. Improving Anomaly Detection
We welcome new detection modules in `src/analysis/`.
- **Peer Benchmarking**: Improve how specialties are grouped.
- **Rules**: Add new screens for improbable medical combinations.
- **ML**: Experiment with different contamination rates or models (Autoencoders, etc.).

### 3. Data Integrity
If you find that a provider is flagged unfairly due to data quirks, please open an issue with the NPI and the reason why the flag might be a false positive.

## Technical Requirements
- Python 3.12+
- DuckDB
- FastAPI (for the dashboard)

## Ethics
All contributors must adhere to the [Ethics and Safeguards](docs/ethics_and_safeguards.md). This project surfaces **signals**, not accusations.
