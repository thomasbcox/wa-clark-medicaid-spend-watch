# Product Roadmap: Medicaid Spend Watch v3.0

This roadmap outlines the evolution from a Clark County beta into a professional-grade, state-wide investigative platform.

## 🏗 Theme 1: Architecture & Portability
*Goal: Remove hardcoding and enable one-click deployment for new counties/states.*

- [ ] **Centralized Configuration**: Implement a `config/settings.py` layer to manage database paths, API keys, and target geographical scopes.
- [ ] **Pipeline Orchestration**: Introduce a master `run_pipeline.py` or `Makefile` to define the Directed Acyclic Graph (DAG) for data ingestion and analysis.
- [ ] **HHS Ingestion Efficiency**: Refactor ingestion to use DuckDB's remote CSV/Parquet streaming to filter NPIs directly from the CMS source without heavy local processing.
- [ ] **Automated Testing**: Implement `pytest` suites to validate anomaly detection math and data parsing logic.

## 🧠 Theme 2: Analytical Depth
*Goal: Increase signal reliability and reduce false positives through statistical rigor.*

- [ ] **Dynamic Thresholding**: Move from "hardcoded dollars" to "distribution-based" flags (e.g., flagging the top 1% of outliers relative to the specific county population).
- [ ] **HCPCS-Mix Clustering**: Cluster providers based on their procedure mix *before* benchmarking to ensure "Apples to Apples" peer comparison.
- [ ] **Temporal Features**: Add month-over-month spend volatility and beneficiary-to-claim ratios to the Isolation Forest model.

## 🖥 Theme 3: Investigative UX
*Goal: Transform data points into actionable evidence for investigators.*

- [ ] **Visual Spend Trends**: Integrate **Chart.js** to display spending histograms and line charts, making "Sudden Utilization" flags instantly verifiable.
- [ ] **API Maturity**: Implement full pagination and multi-variable filtering (by specialty, risk-type, and spend tier).
- [ ] **Search & State**: Add a global NPI/Name search bar and persistent state for investigator notes on specific providers.
- [ ] **Case Management**: Add lightweight "Audit/Dismiss" workflow flags to track the status of manual investigations.

## 🏛 Theme 4: Security & Ethics
- [ ] **CORS Restriction**: Tighten API access control for production environments.
- [ ] **Audit Logs**: Maintain a log of data refresh dates and analysis versioning to ensure oversight integrity.
