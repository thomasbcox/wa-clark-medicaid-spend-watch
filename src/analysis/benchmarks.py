import duckdb
import pandas as pd

from src.config import settings

def calculate_benchmarks():
    conn = duckdb.connect(settings.DB_PATH)
    
    print("Calculating peer group benchmarks (Specialty x Month)...")
    
    # We join spend and providers to get taxonomy
    # Then calculate avg price, stddev, and count for each (taxonomy_desc, period, hcpcs_code)
    conn.execute("""
        CREATE OR REPLACE TABLE benchmarks AS
        SELECT 
            p.taxonomy_desc,
            s.period,
            s.hcpcs_code,
            AVG(s.total_paid / NULLIF(s.total_claims, 0)) AS avg_price_per_claim,
            STDDEV_SAMP(s.total_paid / NULLIF(s.total_claims, 0)) AS stddev_price_per_claim,
            SUM(s.total_claims) AS total_peer_claims,
            COUNT(DISTINCT s.billing_npi) AS peer_count
        FROM medicaid_spend s
        JOIN providers p ON s.billing_npi = p.npi
        WHERE p.taxonomy_desc IS NOT NULL
        GROUP BY 1, 2, 3
    """)
    
    print("Benchmarks table created in DuckDB.")
    conn.close()

if __name__ == "__main__":
    calculate_benchmarks()
