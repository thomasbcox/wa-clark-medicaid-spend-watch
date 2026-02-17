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

### Running the Analysis Pipeline

If you have ingested new data and want to re-run the anomaly engines:
```bash
# Calculate peer group benchmarks
./.venv/bin/python src/analysis/benchmarks.py

# Run rule-based screening (Price, Volume, Concentration)
./.venv/bin/python src/analysis/rules.py

# Run ML anomaly detection (Isolation Forest)
./.venv/bin/python src/analysis/models.py
```

### Deactivation

To exit the virtual environment:
```bash
deactivate
```

## Troubleshooting

If you encounter "externally-managed-environment" errors, it means you are likely trying to use the global Homebrew Python. Ensure you have activated the `.venv` or are using `./.venv/bin/python` directly.
