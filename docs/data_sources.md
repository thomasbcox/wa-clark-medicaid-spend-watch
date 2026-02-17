# Data sources

## HHS Medicaid Provider Spending dataset
- **Source:** [HHS Open Data Portal - Medicaid Provider Spending](https://opendata.hhs.gov/datasets/medicaid-provider-spending/)
- **Content:** Provider-level spending by NPI × HCPCS code × month, covering 2018–2024
- **Coverage:** Fee-for-service, managed care, and CHIP claims from T-MSIS
- **Access:** Direct download from HHS (3.36 GB). **Note:** In v3.0, we use DuckDB's remote streaming to filter this dataset directly from the URL without local extraction.

## NPPES (National Plan and Provider Enumeration System)
- **Source:** [CMS NPPES Public Download](https://download.cms.gov/nppes/NPI_Files.html)
- **Content:** Provider demographics, taxonomy, practice locations, enumeration dates
- **Use:** Join NPIs to locations, specialties, and entity formation dates

## Washington State Business & Corporate Registry
- **Source:** [WA Secretary of State - Corporations & Charities Filing System](https://ccfs.sos.wa.gov/)
- **Content:** Entity formation dates, registered agents, officers, mailing addresses
- **Use:** Link providers to corporate entities, ownership patterns, and shell-network detection

## Optional supplementary sources
- **CMS Medicaid financial management reports:** Program-level totals for sanity checks
- **WA Health Care Authority (HCA):** State-specific Medicaid enrollment, spending, and managed-care reports
- **Local provider directories:** Hospitals, clinics, behavioral health centers in Clark County for context
