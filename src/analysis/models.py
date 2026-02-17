import duckdb
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

DB_PATH = "data/processed/medicaid_watch.db"

def run_ml_analysis():
    conn = duckdb.connect(DB_PATH)
    
    print("Preparing feature matrix for ML Anomaly Detection...")
    
    # Feature Engineering at Provider level
    # total_spend, avg_claims_per_month, unique_codes, avg_price_per_claim
    df = conn.execute("""
        SELECT 
            billing_npi,
            SUM(total_paid) as total_paid,
            COUNT(DISTINCT period) as active_months,
            COUNT(DISTINCT hcpcs_code) as unique_codes,
            SUM(total_paid) / NULLIF(SUM(total_claims), 0) as avg_price_per_claim
        FROM medicaid_spend
        GROUP BY 1
    """).df()
    
    # Clean data (remove NaN)
    df = df.fillna(0)
    
    features = ['total_paid', 'active_months', 'unique_codes', 'avg_price_per_claim']
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
