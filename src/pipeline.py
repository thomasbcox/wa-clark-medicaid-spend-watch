import os
import duckdb
from src.config import settings
from scripts.get_clark_county_npis import main as fetch_npis
from scripts.filter_hhs_data import filter_hhs_spend
from src.ingestion.ingest_leie import main as ingest_leie
from src.analysis.benchmarks import calculate_benchmarks
from src.analysis.rules import screen_providers
from src.analysis.models import run_ml_analysis

def init_db():
    print(f"Initializing database at {settings.DB_PATH}...")
    os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
    conn = duckdb.connect(settings.DB_PATH)
    
    # Run the schema if tables don't exist
    schema_path = os.path.join(settings.BASE_DIR, "sql", "schema_v1.sql")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Split by semicolon and execute
    for statement in schema_sql.split(';'):
        if statement.strip():
            conn.execute(statement)
            
    conn.close()

def main():
    print("--- STARTING MEDICAID WATCH PIPELINE (THEME 1: PORTABLE) ---")
    
    # 0. Setup
    init_db()
    
    # 1. Fetch NPIs (Scope)
    print("\n[Phase 1] Fetching NPI Scope...")
    # fetch_npis() # Optional if already have data/raw/clark_county_npis.json
    
    # 2. Ingest HHS Data (Streaming Filter)
    print("\n[Phase 2] Ingesting HHS Spend Data...")
    filter_hhs_spend()
    
    # 3. Ingest LEIE Exclusions
    print("\n[Phase 3] Ingesting LEIE Exclusion List...")
    ingest_leie()
    
    # 4. Analytics
    print("\n[Phase 4] Running Analytics...")
    calculate_benchmarks()
    screen_providers()
    run_ml_analysis()
    
    print("\n--- PIPELINE EXECUTION COMPLETE ---")
    print(f"Database ready for API at: {settings.DB_PATH}")

if __name__ == "__main__":
    main()
