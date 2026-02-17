import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

DATA_PATH = "data/processed/clark_county_medicaid_spend.csv"
REPORT_PATH = "reports/01-initial-clark-county-summary.md"

def main():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data not found at {DATA_PATH}")
        return

    print("Loading data...")
    df = pd.read_csv(DATA_PATH)
    
    # Cleaning: Ensure numeric types
    df["TOTAL_PAID"] = pd.to_numeric(df["TOTAL_PAID"], errors="coerce")
    df = df.dropna(subset=["TOTAL_PAID"])

    print("Analyzing spending...")
    # Group by Billing Provider
    provider_spend = df.groupby("BILLING_PROVIDER_NPI_NUM")["TOTAL_PAID"].sum().sort_values(ascending=False).reset_index()
    
    # Top 10 Providers
    top_10 = provider_spend.head(10)
    
    # Basic Stats
    total_clark_spend = df["TOTAL_PAID"].sum()
    unique_providers = df["BILLING_PROVIDER_NPI_NUM"].nunique()
    
    # Outlier detection (Z-score on total spend)
    mean_spend = provider_spend["TOTAL_PAID"].mean()
    std_spend = provider_spend["TOTAL_PAID"].std()
    provider_spend["z_score"] = (provider_spend["TOTAL_PAID"] - mean_spend) / std_spend
    outliers = provider_spend[provider_spend["z_score"] > 3]

    print(f"Total Clark County Spend (2018-2024): ${total_clark_spend:,.2f}")
    print(f"Unique Providers: {unique_providers}")
    print(f"Found {len(outliers)} providers with > 3 standard deviations from mean spend.")

    # Create reports directory if not exists
    os.makedirs("reports", exist_ok=True)

    with open(REPORT_PATH, "w") as f:
        f.write("# Initial Medicaid Spend Summary: Clark County, WA\n\n")
        f.write(f"- **Total Spend (2018-2024):** ${total_clark_spend:,.2f}\n")
        f.write(f"- **Unique Billing Providers:** {unique_providers:,}\n")
        f.write(f"- **Providers > 3σ from Mean:** {len(outliers)}\n\n")
        
        f.write("## Top 10 Billing Providers by Total Spend\n\n")
        f.write("| Rank | NPI | Total Paid | % of Total |\n")
        f.write("|---|---|---|---|\n")
        for i, row in top_10.iterrows():
            perc = (row['TOTAL_PAID'] / total_clark_spend) * 100
            f.write(f"| {i+1} | {row['BILLING_PROVIDER_NPI_NUM']} | ${row['TOTAL_PAID']:,.2f} | {perc:.2f}% |\n")
            
        f.write("\n\n*Note: High spend doesn't imply anomaly, but identifies focal points for Phase 2 investigation into entity types and procedure rates.*")

    print(f"Summary report saved to {REPORT_PATH}")

if __name__ == "__main__":
    main()
