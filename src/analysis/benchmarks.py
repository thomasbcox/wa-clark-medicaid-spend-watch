import duckdb
import pandas as pd

DB_PATH = "data/processed/medicaid_watch.db"

def calculate_benchmarks():
    conn = duckdb.connect(DB_PATH)
    
    print("Calculating peer group benchmarks (Specialty x Month)...")
    
    # We join spend and providers to get taxonomy
    # Then calculate avg total_paid per claim for each (taxonomy_desc, period)
    conn.execute("""
        CREATE OR REPLACE TABLE benchmarks AS
        SELECT 
            p.taxonomy_desc,
            s.period,
            s.hcpcs_code,
            AVG(s.total_paid / NULLIF(s.total_claims, 0)) AS avg_price_per_claim,
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
