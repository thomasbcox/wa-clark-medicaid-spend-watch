# Developer Guide: Python Environment Setup

This project uses a project-local virtual environment to ensure reliable execution on macOS (especially with Homebrew Python and PEP 668).

## Prerequisites

- macOS with Homebrew installed.
- Python 3.12 or higher.

## Initial Setup

1. **Create the virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Daily Usage

### Activation

Always work within the activated virtual environment:
```bash
source .venv/bin/activate
```

### Running the Dashboard & API

To explore the identified risk signals, start the FastAPI server:
```bash
./.venv/bin/python src/api/main.py
```
*   **Web UI**: Access the interactive dashboard at [http://127.0.0.1:8000](http://127.0.0.1:8000).
*   **API Docs**: View the Swagger/OpenAPI documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Running the Integrated Pipeline (Recommended)

To fetch data, filter for your target county, and run all analytics in one command:
```bash
./.venv/bin/python src/pipeline.py
```
This is the preferred way to ensure all benchmarks and models are synchronized.

### Running Individual Analysis Scripts

If you need to re-run specific components:
```bash
# Calculate peer group benchmarks
./.venv/bin/python src/analysis/benchmarks.py

# Run rule-based screening (Price, Volume, Concentration)
./.venv/bin/python src/analysis/rules.py

# Run ML anomaly detection (Isolation Forest)
./.venv/bin/python src/analysis/models.py
```

## Configuration

All system settings, including the target county, data source URLs, and risk thresholds, are centralized in:
**[src/config.py](file:///Users/thomasbcox/Projects/wa-clark-medicaid-spend-watch/src/config.py)**

To port the project to a new county, simply update `TARGET_COUNTY` and `TARGET_STATE` in this file.

### Deactivation

To exit the virtual environment:
```bash
deactivate
```

## Troubleshooting

If you encounter "externally-managed-environment" errors, it means you are likely trying to use the global Homebrew Python. Ensure you have activated the `.venv` or are using `./.venv/bin/python` directly.
