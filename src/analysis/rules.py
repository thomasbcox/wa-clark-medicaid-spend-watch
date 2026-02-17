import duckdb
import pandas as pd

from src.config import settings

def screen_providers():
    conn = duckdb.connect(settings.DB_PATH)
    
    print("Screening providers against simple rules...")
    conn.execute("DELETE FROM risk_flags")
    
    # 1. Price Outlier Screen (Z-score based)
    conn.execute("""
        INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
        SELECT 
            s.billing_npi,
            'PRICE_Z_SCORE_OUTLIER',
            ((s.total_paid / NULLIF(s.total_claims, 0)) - b.avg_price_per_claim) / NULLIF(b.stddev_price_per_claim, 0),
            'High Price Evidence: Billed avg $' || ROUND(s.total_paid / s.total_claims, 2) || 
            ' for code ' || s.hcpcs_code || ' which is ' || 
            ROUND(((s.total_paid / s.total_claims) - b.avg_price_per_claim) / NULLIF(b.stddev_price_per_claim, 0), 1) || 
            ' std devs above the peer average of $' || ROUND(b.avg_price_per_claim, 2)
        FROM medicaid_spend s
        JOIN providers p ON s.billing_npi = p.npi
        JOIN benchmarks b ON p.taxonomy_desc = b.taxonomy_desc AND s.period = b.period AND s.hcpcs_code = b.hcpcs_code
        WHERE ((s.total_paid / NULLIF(s.total_claims, 0)) - b.avg_price_per_claim) > ? * b.stddev_price_per_claim
          AND s.total_paid > 20000 
          AND b.peer_count >= ?
    """, [settings.Z_SCORE_THRESHOLD, settings.MIN_PEER_COUNT])
    
    # 2. Extreme Concentration Screen
    conn.execute("""
        INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
        WITH provider_totals AS (
            SELECT billing_npi, SUM(total_paid) as sum_paid FROM medicaid_spend GROUP BY 1
        )
        SELECT 
            s.billing_npi,
            'EXTREME_CONCENTRATION',
            (s.total_paid / pt.sum_paid),
            'Concentration Evidence: A single code (' || s.hcpcs_code || ') accounts for ' || 
            ROUND((s.total_paid / pt.sum_paid) * 100, 1) || '% of total revenue ($' || 
            ROUND(s.total_paid/1000, 1) || 'k out of $' || ROUND(pt.sum_paid/1000, 1) || 'k)'
        FROM medicaid_spend s
        JOIN provider_totals pt ON s.billing_npi = pt.billing_npi
        JOIN providers p ON s.billing_npi = p.npi
        WHERE (s.total_paid / pt.sum_paid) > ?
          AND pt.sum_paid > ?
          AND p.taxonomy_desc NOT IN ('Ambulance', 'Clinical Medical Laboratory', 'End‑Stage Renal Disease (ESRD) Treatment Facility', 'Interpreter', 'Transportation Broker', 'Non-emergency Medical Transport (NEMT)')
          AND p.name NOT LIKE '%TRANSPORT%'
    """, [settings.EXTREME_CONCENTRATION_THRESHOLD, settings.MIN_CONCENTRATION_SPEND])

    # 3. New Entrant (Sudden Utilization) Screen
    conn.execute("""
        INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
        WITH first_month AS (
            SELECT billing_npi, MIN(period) as min_p, SUM(total_paid) as first_month_spend 
            FROM medicaid_spend GROUP BY 1
        )
        SELECT 
            billing_npi,
            'SUDDEN_UTILIZATION',
            1.0,
            'Utilization Spike: Provider billed $' || ROUND(first_month_spend/1000, 0) || 
            'k in their first recorded month (' || CAST(min_p AS VARCHAR) || '), exceeding the $' || 
            CAST(? / 1000 AS VARCHAR) || 'k monitoring limit.'
        FROM first_month
        WHERE min_p > '2020-01-01'
          AND first_month_spend > ?
    """, [settings.SUDDEN_UTILIZATION_LIMIT, settings.SUDDEN_UTILIZATION_LIMIT])

    # 4. Volume Outlier (Claim Mill) Screen
    conn.execute("""
        INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
        SELECT 
            s.billing_npi,
            'VOLUME_OUTLIER',
            s.total_claims / (b.total_peer_claims / b.peer_count),
            'Volume Evidence: Billed ' || s.total_claims || ' claims for code ' || s.hcpcs_code || 
            ', which is ' || ROUND(s.total_claims / (b.total_peer_claims / b.peer_count), 1) || 
            'x more than the peer average (' || ROUND(b.total_peer_claims / b.peer_count, 1) || ')'
        FROM medicaid_spend s
        JOIN providers p ON s.billing_npi = p.npi
        JOIN benchmarks b ON p.taxonomy_desc = b.taxonomy_desc AND s.period = b.period AND s.hcpcs_code = b.hcpcs_code
        WHERE s.total_claims > ? * (b.total_peer_claims / b.peer_count)
          AND s.total_claims > ?
          AND b.peer_count >= 5
    """, [settings.VOLUME_OUTLIER_MULTIPLIER, settings.MIN_VOLUME_CLAIMS])

    # 5. Dynamic Percentile Outlier Screen (Theme 2 Enhancement)
    # Flag the top 1% of spenders within their specialty x code peer group
    print("Running dynamic percentile screening...")
    conn.execute("""
        INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
        WITH peer_ranks AS (
            SELECT 
                s.billing_npi,
                s.total_paid,
                s.hcpcs_code,
                p.taxonomy_desc,
                PERCENT_RANK() OVER (PARTITION BY p.taxonomy_desc, s.period, s.hcpcs_code ORDER BY s.total_paid) as rank_pct
            FROM medicaid_spend s
            JOIN providers p ON s.billing_npi = p.npi
        )
        SELECT 
            billing_npi,
            'PERCENTILE_OUTLIER',
            rank_pct,
            'Statistical Persistence: This provider is in the top ' || 
            ROUND((1 - rank_pct) * 100, 2) || '% of all ' || taxonomy_desc || 
            ' providers for code ' || hcpcs_code || ' by total spend.'
        FROM peer_ranks
        WHERE rank_pct >= 0.99
          AND total_paid > 50000 -- Floor to avoid low-value noise
    """)

    # 6. Claim Mill Detection (beneficiary ratio)
    print("Running Claim Mill (Patient Ratio) screening...")
    conn.execute("""
        INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
        SELECT 
            billing_npi,
            'CLAIM_MILL_RATIO',
            CAST(total_claims AS DOUBLE) / NULLIF(unique_beneficiaries, 0),
            'Patient Density Risk: Billed ' || total_claims || ' claims to only ' || 
            unique_beneficiaries || ' patients for code ' || hcpcs_code || 
            ' (' || ROUND(CAST(total_claims AS DOUBLE) / NULLIF(unique_beneficiaries, 0), 1) || ' claims/patient)'
        FROM medicaid_spend
        WHERE unique_beneficiaries > 0 
          AND (CAST(total_claims AS DOUBLE) / unique_beneficiaries) > 20 -- Arbitrary initial threshold for review
          AND total_paid > 10000
    """)

    print(f"Risk screening complete. Total flags: {conn.execute('SELECT COUNT(*) FROM risk_flags').fetchone()[0]}")
    conn.close()

if __name__ == "__main__":
    screen_providers()
