# Contributing to Medicaid Spend Watch

Thank you for your interest in improving Medicaid oversight in Washington!

## How to Contribute

### 1. Porting to a New County
The v2 architecture is designed to be location-agnostic. To port this to another county:
- Update the `scripts/get_county_npis.py` with the zip codes of your target county.
- Follow the ingestion pipeline in `src/ingestion/`.

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
