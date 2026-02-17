import requests
import zipfile
import io
import csv
import json
from tqdm import tqdm
import os

HHS_DATA_URL = "https://stopendataprod.blob.core.windows.net/datasets/medicaid-provider-spending/2026-02-09/medicaid-provider-spending.csv.zip"
NPI_LIST_PATH = "data/raw/clark_county_npis.json"
OUTPUT_PATH = "data/processed/clark_county_medicaid_spend.csv"

def main():
    if not os.path.exists(NPI_LIST_PATH):
        print(f"Error: NPI list not found at {NPI_LIST_PATH}. Run get_clark_county_npis.py first.")
        return

    with open(NPI_LIST_PATH, "r") as f:
        clark_npis = set(str(npi) for npi in json.load(f))
    
    print(f"Loaded {len(clark_npis)} NPIs for filtering.")

    print(f"Downloading and filtering HHS data (streaming)...")
    response = requests.get(HHS_DATA_URL, stream=True)
    response.raise_for_status()

    # Since it's a ZIP, we ideally want to stream the ZIP content to avoid full memory usage.
import requests
from src.config import settings

def filter_hhs_spend():
    """
    Leverage DuckDB to stream and filter HHS data directly from the remote zip file.
    This eliminates the need to download and extract the 3GB+ file locally.
    """
    conn = duckdb.connect(settings.DB_PATH)
    
    print(f"Streaming and filtering HHS data for {settings.TARGET_COUNTY}, {settings.TARGET_STATE}...")
    
    # CMS/HHS data has a specific schema. We filter for our NPIs and Target State.
    # Note: DuckDB's httpfs extension allows reading directly from URLs.
    # We use 'read_csv' with the remote URL.
    
    conn.execute("INSTALL httpfs; LOAD httpfs;")
    
    # We join with our local providers table to only keep Clark County data
    query = f"""
        INSERT INTO medicaid_spend
        SELECT 
            "Billing NPI" as billing_npi,
            "State" as state,
            "County" as county,
            "Period" as period,
            "HCPCS Code" as hcpcs_code,
            CAST("Total Medicaid Paid Amount" AS DOUBLE) as total_paid,
            CAST("Total Claims" AS INTEGER) as total_claims
        FROM read_csv('{settings.HHS_SOURCE_URL}', 
                      header=True, 
                      compression='zip',
                      timestampformat='%Y-%m-%d')
        WHERE "Billing NPI" IN (SELECT npi FROM providers)
          AND "State" = '{settings.TARGET_STATE}'
          AND "County" = '{settings.TARGET_COUNTY}'
    """
    
    # Clear existing spend to avoid duplicates if re-running
    conn.execute("DELETE FROM medicaid_spend")
    
    print("Executing remote stream & filter...")
    conn.execute(query)
    
    count = conn.execute("SELECT COUNT(*) FROM medicaid_spend").fetchone()[0]
    print(f"Ingestion complete. {count} rows added to medicaid_spend table.")
    
    conn.close()

if __name__ == "__main__":
    # Ensure DuckDB directory exists
    os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
    filter_hhs_spend()
