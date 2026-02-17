# 🔍 WA Medicaid Spend Watch v2.0 (Clark County)

An open-source, civic oversight platform designed to identify statistical anomalies and risk signals in Medicaid spending.

## 🚀 Key Features
- **Relational Data Model**: Powered by **DuckDB** for lightning-fast analytical queries over multi-gigabyte datasets.
- **Enriched Provider Registry**: Combines CMS Medicaid spend data with **NPPES** metadata (Specialties, Names) and **OIG LEIE** exclusion lists.
- **Anomaly Detection Engine**:
  - **Peer Benchmarking**: Identifies outliers by comparing providers against their specific specialty peers.
  - **Rule-Based Screening**: Detects extreme price deviations (e.g., >3x peer avg) and revenue concentration.
  - **Unsupervised ML**: Uses **Isolation Forest** algorithms to surface multivariate outliers.
- **Advanced Anomaly Rules**: Z-Score price detection, Pop-up utilization screening, and Volume-outlier mills.
- **Provider Transparency**: Authorized official tracking and WA SOS research integration.
- **Exploratory Dashboard**: A lightweight FastAPI + JS frontend for journalists and watchdogs to investigate risk signals.

## 🛠 Project Structure
- `src/analysis/`: Anomaly detection engines (benchmarks, rules, ML models).
- `src/ingestion/`: Ingestion pipelines for HHS, NPPES, and OIG LEIE data.
- `sql/`: Data schemas and relational mappings.
- `web/`: Dashboard frontend.

## 🗺 Product Roadmap
See our [ROADMAP.md](ROADMAP.md) for the planned evolution toward state-wide scalability and advanced investigative features.

## 🚀 Getting Started

### 1. Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
./.venv/bin/python src/api/main.py
```
Open `http://127.0.0.1:8000` in your browser.

## ⚖ Ethics & Intent
This project surfaces **signals**, not proof of fraud. It is intended for civic oversight and to inform professional investigation. See [Ethics and Safeguards](docs/ethics_and_safeguards.md) for core principles.

## 🤝 Contributing
We welcome contributions to scale this beyond Clark County or to improve our anomaly models. See [CONTRIBUTING.md](CONTRIBUTING.md).
