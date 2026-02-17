# wa-clark-medicaid-spend-watch
Civic project exploring possibly anomalous Medicaid provider spending in Washington, starting with Clark County. Uses only public data, aims to inform oversight and media, not make legal determinations.

## Current Status (Phase 1 Complete)
We have successfully processed the 2018-2024 HHS Medicaid Provider Spending dataset for Clark County, WA.

**Key Findings:**
- **Total Clark County Medicaid Spend:** ~$909,471,032.89
- **Unique Providers Identified:** 1,828
- **Statistical Outliers:** 24 providers identified with spending > 3 standard deviations from the mean.

**Data Pipeline:**
1. **NPI Identification**: Scraped [CMS NPPES API](scripts/get_clark_county_npis.py) for all NPIs associated with 25 Clark County zip codes.
2. **Filtering**: Streamed the 3.36 GB HHS dataset to extract 1,010,363 relevant records using [filter_hhs_data.py](scripts/filter_hhs_data.py).
3. **Initial Profiling**: Generated summary statistics in [reports/01-initial-clark-county-summary.md](reports/01-initial-clark-county-summary.md).

## Getting Started
See [README-dev.md](README-dev.md) for environment setup and data intake instructions.
