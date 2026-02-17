# Product Roadmap: Medicaid Spend Watch v3.0

This roadmap outlines the evolution from a Clark County beta into a professional-grade, state-wide investigative platform.

## 🏗 Theme 1: Architecture & Portability
*Goal: Remove hardcoding and enable one-click deployment for new counties/states.*

- [x] **Centralized Configuration**: Implement a `src/config.py` layer to manage database paths and target scope.
- [x] **Pipeline Orchestration**: Created `src/pipeline.py` to define the full Directed Acyclic Graph (DAG).
- [x] **HHS Ingestion Efficiency**: Leveraged DuckDB remote CSV streaming to filter multi-GB sources instantly.
- [x] **Automated Testing**: Integrated `pytest` suite to validate detection math.

## 🧠 Theme 2: Analytical Depth
*Goal: Increase signal reliability and reduce false positives through statistical rigor.*

- [x] **Dynamic Thresholding**: Implemented `PERCENT_RANK()` based top 1% flags for intra-specialty comparison.
- [x] **Claim-to-Beneficiary Ratios**: Added "Claim Mill" detection using patient density metrics.
- [x] **Temporal Features**: Integrated `spend_volatility` and Growth metrics into a refined Isolation Forest model.

## 🖥 Theme 3: Investigative UX
*Goal: Transform data points into actionable evidence for investigators.*

- [ ] **Visual Spend Trends**: Integrate **Chart.js** to display spending histograms and line charts, making "Sudden Utilization" flags instantly verifiable.
- [ ] **API Maturity**: Implement full pagination and multi-variable filtering (by specialty, risk-type, and spend tier).
- [ ] **Search & State**: Add a global NPI/Name search bar and persistent state for investigator notes on specific providers.
- [ ] **Case Management**: Add lightweight "Audit/Dismiss" workflow flags to track the status of manual investigations.

## 🏛 Theme 4: Security & Ethics
- [ ] **CORS Restriction**: Tighten API access control for production environments.
- [ ] **Audit Logs**: Maintain a log of data refresh dates and analysis versioning to ensure oversight integrity.
