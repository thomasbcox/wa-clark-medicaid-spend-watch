import duckdb
import pandas as pd

DB_PATH = "data/processed/medicaid_watch.db"

def screen_providers():
    conn = duckdb.connect(DB_PATH)
    
    print("Screening providers against simple rules...")
    
    # 1. Price Outlier Screen
    # Flag providers charging > 3x the peer group average for a specific HCPCS
    conn.execute("""
        INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
        SELECT 
            s.billing_npi,
            'PRICE_OUTLIER',
            (s.total_paid / NULLIF(s.total_claims, 0)) / b.avg_price_per_claim,
            'Charges ' || ROUND((s.total_paid / NULLIF(s.total_claims, 0)) / b.avg_price_per_claim, 1) || 'x peer average for code ' || s.hcpcs_code
        FROM medicaid_spend s
        JOIN providers p ON s.billing_npi = p.npi
        JOIN benchmarks b ON p.taxonomy_desc = b.taxonomy_desc AND s.period = b.period AND s.hcpcs_code = b.hcpcs_code
        WHERE (s.total_paid / NULLIF(s.total_claims, 0)) > 3 * b.avg_price_per_claim
          AND s.total_paid > 5000 -- Ignore small noise
    """)
    
    # 2. Extreme Concentration Screen
    # Flag providers who derive > 90% of revenue from one code (if not a highly specialized specialty)
    conn.execute("""
        INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
        WITH provider_totals AS (
            SELECT billing_npi, SUM(total_paid) as sum_paid FROM medicaid_spend GROUP BY 1
        )
        SELECT 
            s.billing_npi,
            'EXTREME_CONCENTRATION',
            (s.total_paid / pt.sum_paid),
            'Derives ' || ROUND((s.total_paid / pt.sum_paid) * 100, 1) || '% of total Medicaid revenue from code ' || s.hcpcs_code
        FROM medicaid_spend s
        JOIN provider_totals pt ON s.billing_npi = pt.billing_npi
        WHERE (s.total_paid / pt.sum_paid) > 0.90
          AND pt.sum_paid > 50000
    """)

    print(f"Risk screening complete. Flags generated: {conn.execute('SELECT COUNT(*) FROM risk_flags').fetchone()[0]}")
    conn.close()

if __name__ == "__main__":
    screen_providers()
