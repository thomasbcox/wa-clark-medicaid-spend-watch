# Ethics and safeguards

## Core principles

- This project **does not assert that any provider has committed fraud**.
- It identifies **anomalous spending patterns** in public data that may warrant professional review by authorized investigators (Washington Medicaid Fraud Control Division, MCO special investigation units, federal OIG).
- All analyses may be incomplete or misleading; findings are **hypotheses, not conclusions**.

## Data practices

- **No protected health information (PHI)** is used. Only public, aggregate, or de-identified data are analyzed.
- **No patient-level data:** The HHS Medicaid Provider Spending dataset is aggregated to the provider–procedure–month level and contains no individual beneficiary records.
- **Reproducibility:** All analysis code, queries, and methods are public and version-controlled so others can verify or challenge results.

## Public communication standards

- Public materials (reports, charts, media briefings) will:
  - Avoid labeling individual providers as "fraudsters" based solely on statistical anomalies.
  - Use neutral language: "higher-risk pattern," "outlier billing," "warrants further review."
  - Emphasize program integrity, stewardship of public funds, and protection of beneficiaries—not inflammatory or partisan framing.
- Provider-specific case files shared with fraud units or journalists will be clearly marked as preliminary and non-conclusive.

## Correction policy

- If credible information shows that an analysis is misleading, unfair, or based on faulty data or logic, the project will:
  - **Correct or withdraw the analysis** promptly.
  - **Document the correction** in the repo history and in a public note.
  - **Notify any parties** (media, officials, fraud units) who received the original finding.

## Accountability

- Methods, assumptions, and decision logs are maintained in `docs/` and committed to version control.
- Community feedback via GitHub Issues and Discussions is welcomed; legitimate critiques will be addressed transparently.
