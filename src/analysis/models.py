import duckdb
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

from src.config import settings

def run_ml_analysis():
    conn = duckdb.connect(settings.DB_PATH)
    
    print("Preparing feature matrix for ML Anomaly Detection...")
    
    # Feature Engineering at Provider level
    # total_spend, active_months, unique_codes, avg_price_per_claim, avg_peer_price_ratio
    df = conn.execute("""
        SELECT 
            s.billing_npi,
            SUM(s.total_paid) as total_paid,
            COUNT(DISTINCT s.period) as active_months,
            COUNT(DISTINCT s.hcpcs_code) as unique_codes,
            SUM(s.total_paid) / NULLIF(SUM(s.total_claims), 0) as avg_price_per_claim,
            AVG((s.total_paid / NULLIF(s.total_claims, 0)) / NULLIF(b.avg_price_per_claim, 0)) as avg_peer_price_ratio
        FROM medicaid_spend s
        JOIN providers p ON s.billing_npi = p.npi
        JOIN benchmarks b ON p.taxonomy_desc = b.taxonomy_desc AND s.period = b.period AND s.hcpcs_code = b.hcpcs_code
        GROUP BY 1
    """).df()
    
    # Clean data (remove NaN)
    df = df.fillna(0)
    
    features = ['total_paid', 'active_months', 'unique_codes', 'avg_price_per_claim', 'avg_peer_price_ratio']
    X = df[features]
    
    print(f"Training Isolation Forest on {len(df)} providers...")
    model = IsolationForest(contamination=0.02, random_state=42) # Flag top 2%
    df['anomaly_score'] = model.fit_predict(X)
    
    # IsolationForest returns -1 for outliers
    outliers = df[df['anomaly_score'] == -1]
    
    print(f"ML analysis complete. Found {len(outliers)} ML anomalies.")
    
    # Insert into risk_flags
    for _, row in outliers.iterrows():
        conn.execute("""
            INSERT INTO risk_flags (npi, flag_type, flag_score, reason)
            VALUES (?, 'ML_ISOLATION_FOREST', 1.0, 'Global multivariate outlier (High spend/High price/High volume pattern)')
        """, [str(row['billing_npi'])])
        
    conn.close()

if __name__ == "__main__":
    run_ml_analysis()
