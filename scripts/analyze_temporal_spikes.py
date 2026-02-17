import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_PATH = "data/processed/clark_county_medicaid_spend.csv"
ENRICHED_PATH = "data/processed/outlier_entity_details.csv"
REPORT_PATH = "reports/03-temporal-spike-analysis.md"

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
    
    # Convert dates
    outlier_df["CLAIM_FROM_MONTH"] = pd.to_datetime(outlier_df["CLAIM_FROM_MONTH"])
    
    print("Analyzing temporal trends...")
    spike_findings = []

    for npi in outlier_npis:
        npi_name = enriched_df[enriched_df["NPI"] == npi]["Name"].values[0]
        npi_ts = outlier_df[outlier_df["BILLING_PROVIDER_NPI_NUM"] == npi].groupby("CLAIM_FROM_MONTH")["TOTAL_PAID"].sum().sort_index()
        
        if len(npi_ts) < 3: continue
        
        # Calculate Rolling Mean and Spike Factor
        rolling_mean = npi_ts.rolling(window=6).mean()
        spike_factor = npi_ts / rolling_mean
        
        max_spike = spike_factor.max()
        if max_spike > 2.0:  # Spike > 2x rolling average
            spike_date = spike_factor.idxmax()
            spike_val = npi_ts[spike_date]
            
            spike_findings.append({
                "NPI": npi,
                "Name": npi_name,
                "SpikeDate": spike_date.strftime("%Y-%m"),
                "SpikeFactor": max_spike,
                "Amount": spike_val
            })

    # Save Report
    with open(REPORT_PATH, "w") as f:
        f.write("# Temporal Spike Analysis: Clark County Outliers\n\n")
        f.write("This report identifies sudden surges in Medicaid spending for the 24 identified outliers.\n\n")
        
        f.write("## Major Spending Spikes (>2x Rolling Average)\n\n")
        f.write("| Organization | Month | Spike Factor | Spend in Month |\n")
        f.write("|---|---|---|---|\n")
        
        for item in sorted(spike_findings, key=lambda x: x["SpikeFactor"], reverse=True):
            f.write(f"| {item['Name']} | {item['SpikeDate']} | {item['SpikeFactor']:.2f}x | ${item['Amount']:,.2f} |\n")

    print(f"Temporal analysis saved to {REPORT_PATH}")

if __name__ == "__main__":
    main()
