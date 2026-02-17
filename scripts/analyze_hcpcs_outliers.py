import pandas as pd
import numpy as np
import os

DATA_PATH = "data/processed/clark_county_medicaid_spend.csv"
ENRICHED_PATH = "data/processed/outlier_entity_details.csv"
REPORT_PATH = "reports/02-outlier-hcpcs-deep-dive.md"

def main():
    if not os.path.exists(DATA_PATH) or not os.path.exists(ENRICHED_PATH):
        print("Required data files missing.")
        return

    print("Loading data...")
    df = pd.read_csv(DATA_PATH)
    enriched_df = pd.read_csv(ENRICHED_PATH)
    outlier_npis = enriched_df["NPI"].tolist()

    # Filter for outliers
    outlier_df = df[df["BILLING_PROVIDER_NPI_NUM"].isin(outlier_npis)]
    
    # Calculate Benchmarks (County Average per HCPCS)
    county_benchmarks = df.groupby("HCPCS_CODE").agg(
        avg_paid_per_claim=("TOTAL_PAID", lambda x: (x.sum() / df.loc[x.index, "TOTAL_CLAIMS"].sum())),
        total_county_claims=("TOTAL_CLAIMS", "sum")
    ).reset_index()

    print("Analyzing procedure distributions for outliers...")
    deep_dive_results = []

    for npi in outlier_npis:
        npi_name = enriched_df[enriched_df["NPI"] == npi]["Name"].values[0]
        npi_df = outlier_df[outlier_df["BILLING_PROVIDER_NPI_NUM"] == npi]
        
        # Top codes by spend for this provider
        hcpcs_spend = npi_df.groupby("HCPCS_CODE").agg(
            total_paid=("TOTAL_PAID", "sum"),
            total_claims=("TOTAL_CLAIMS", "sum"),
            unique_beneficiaries=("TOTAL_UNIQUE_BENEFICIARIES", "sum")
        ).reset_index()
        
        hcpcs_spend["paid_per_claim"] = hcpcs_spend["total_paid"] / hcpcs_spend["total_claims"]
        hcpcs_spend = hcpcs_spend.sort_values("total_paid", ascending=False)
        
        # Merge with benchmarks
        hcpcs_spend = hcpcs_spend.merge(county_benchmarks, on="HCPCS_CODE", how="left")
        hcpcs_spend["price_ratio"] = hcpcs_spend["paid_per_claim"] / hcpcs_spend["avg_paid_per_claim"]
        
        # Identify "Signature" Codes (>20% of provider spend OR >3x county avg price)
        total_provider_spend = hcpcs_spend["total_paid"].sum()
        hcpcs_spend["spend_share"] = hcpcs_spend["total_paid"] / total_provider_spend
        
        signature_codes = hcpcs_spend[
            (hcpcs_spend["spend_share"] > 0.20) | 
            ((hcpcs_spend["price_ratio"] > 2.0) & (hcpcs_spend["total_paid"] > 10000))
        ]
        
        for _, row in signature_codes.iterrows():
            deep_dive_results.append({
                "NPI": npi,
                "Name": npi_name,
                "HCPCS": row["HCPCS_CODE"],
                "TotalPaid": row["total_paid"],
                "SpendShare": row["spend_share"],
                "PaidPerClaim": row["paid_per_claim"],
                "CountyAvgPrice": row["avg_paid_per_claim"],
                "PriceRatio": row["price_ratio"]
            })

    results_df = pd.DataFrame(deep_dive_results)
    
    # Save Report
    with open(REPORT_PATH, "w") as f:
        f.write("# Outlier HCPCS Deep Dive: Clark County, WA\n\n")
        f.write("This report identifies specific procedure codes (HCPCS) that drive anomalous spending for the top 24 outliers.\n\n")
        
        f.write("## Procedure Anomalies by Provider\n\n")
        f.write("| Organization | HCPCS | Total Paid | Share of Provider Spend | Price Ratio (vs County Avg) |\n")
        f.write("|---|---|---|---|---|\n")
        
        for _, row in results_df.sort_values("TotalPaid", ascending=False).iterrows():
            f.write(f"| {row['Name']} | {row['HCPCS']} | ${row['TotalPaid']:,.2f} | {row['SpendShare']:.1%} | {row['PriceRatio']:.2f}x |\n")

        f.write("\n\n### Notable Findings\n")
        # Find highest price ratio
        max_ratio_row = results_df.loc[results_df["PriceRatio"].idxmax()]
        f.write(f"- **Highest Price Anomaly:** `{max_ratio_row['Name']}` is charging **{max_ratio_row['PriceRatio']:.2f}x** the county average for code `{max_ratio_row['HCPCS']}`.\n")
        
        # Find highest spend share
        max_share_row = results_df.loc[results_df["SpendShare"].idxmax()]
        f.write(f"- **Extreme Specialization:** `{max_share_row['Name']}` derives **{max_share_row['SpendShare']:.1%}** of its total Medicaid revenue from a single code: `{max_share_row['HCPCS']}`.\n")

    print(f"Deep dive report saved to {REPORT_PATH}")

if __name__ == "__main__":
    main()
