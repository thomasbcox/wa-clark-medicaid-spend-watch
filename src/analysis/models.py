import duckdb
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

from src.config import settings

def run_ml_analysis():
    conn = duckdb.connect(settings.DB_PATH)
    
    print("Preparing feature matrix for ML Anomaly Detection...")
    
    # Feature Engineering at Provider level (Theme 2: Analytical Depth)
    # We now add:
    # - spend_volatility: fluctuation in monthly payments
    # - beneficiary_ratio: patient density (claims per unique beneficiary)
    df = conn.execute("""
        WITH provider_monthly AS (
            SELECT 
                billing_npi,
                period,
                SUM(total_paid) as monthly_paid,
                SUM(total_claims) as monthly_claims,
                SUM(unique_beneficiaries) as monthly_beneficiaries
            FROM medicaid_spend
            GROUP BY 1, 2
        ),
        provider_stats AS (
            SELECT 
                billing_npi,
                STDDEV(monthly_paid) as spend_volatility,
                SUM(monthly_claims) / NULLIF(SUM(monthly_beneficiaries), 0) as beneficiary_ratio
            FROM provider_monthly
            GROUP BY 1
        )
        SELECT 
            s.billing_npi,
            SUM(s.total_paid) as total_paid,
            COUNT(DISTINCT s.period) as active_months,
            COUNT(DISTINCT s.hcpcs_code) as unique_codes,
            SUM(s.total_paid) / NULLIF(SUM(s.total_claims), 0) as avg_price_per_claim,
            AVG((s.total_paid / NULLIF(s.total_claims, 0)) / NULLIF(b.avg_price_per_claim, 0)) as avg_peer_price_ratio,
            MAX(st.spend_volatility) as spend_volatility,
            MAX(st.beneficiary_ratio) as beneficiary_ratio
        FROM medicaid_spend s
        JOIN providers p ON s.billing_npi = p.npi
        JOIN benchmarks b ON p.taxonomy_desc = b.taxonomy_desc AND s.period = b.period AND s.hcpcs_code = b.hcpcs_code
        LEFT JOIN provider_stats st ON s.billing_npi = st.billing_npi
        GROUP BY 1
    """).df()
    
    # Clean data (remove NaN)
    df = df.fillna(0)
    
    features = [
        'total_paid', 
        'active_months', 
        'unique_codes', 
        'avg_price_per_claim', 
        'avg_peer_price_ratio',
        'spend_volatility',
        'beneficiary_ratio'
    ]
    X = df[features]
    
    print(f"Training Isolation Forest on {len(df)} providers with enhanced temporal features...")
    model = IsolationForest(contamination=0.03, random_state=42) # Increased to 3% for deeper signals
    df['anomaly_score'] = model.fit_predict(X)
    
    # IsolationForest returns -1 for outliers
    outliers = df[df['anomaly_score'] == -1]
    
    print(f"ML analysis complete. Found {len(outliers)} refined ML anomalies.")
    
    # Insert into risk_flags
    for _, row in outliers.iterrows():
        conn.execute("""
            INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
            VALUES (?, 'ML_ISOLATION_FOREST', 1.0, 'Global multivariate outlier (High spend/High price/High volume pattern)')
        """, [str(row['billing_npi'])])
        
    conn.close()

if __name__ == "__main__":
    run_ml_analysis()
