import duckdb
import os
from src.config import settings

def filter_hhs_spend():
    """
    Leverage DuckDB to stream and filter HHS data directly from the remote zip file.
    This eliminates the need to download and extract the 3GB+ file locally.
    """
    conn = duckdb.connect(settings.DB_PATH)
    
    print(f"Streaming and filtering HHS data for {settings.TARGET_COUNTY}, {settings.TARGET_STATE}...")
    
    # CMS/HHS data has a specific schema. 
    # Note: DuckDB's httpfs extension allows reading directly from URLs.
    conn.execute("INSTALL httpfs; LOAD httpfs;")
    
    # We join with our local providers table to only keep relevant data
    # Note: New headers for 2026 release are UPPERCASE.
    # State/County no longer in CSV, we use our local provider scope.
    query = f"""
        INSERT INTO medicaid_spend (billing_npi, state, county, period, hcpcs_code, total_paid, total_claims, unique_beneficiaries)
        SELECT 
            BILLING_PROVIDER_NPI_NUM as billing_npi,
            '{settings.TARGET_STATE}' as state,
            '{settings.TARGET_COUNTY}' as county,
            CAST(CLAIM_FROM_MONTH || '-01' AS DATE) as period,
            HCPCS_CODE as hcpcs_code,
            CAST(TOTAL_PAID AS DOUBLE) as total_paid,
            CAST(TOTAL_CLAIMS AS INTEGER) as total_claims,
            CAST(TOTAL_UNIQUE_BENEFICIARIES AS INTEGER) as unique_beneficiaries
        FROM read_csv('{settings.HHS_SOURCE_URL}', 
                      header=True)
        WHERE BILLING_PROVIDER_NPI_NUM IN (SELECT npi FROM providers)
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
