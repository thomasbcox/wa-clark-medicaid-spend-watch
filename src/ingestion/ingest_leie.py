import requests
import duckdb
import pandas as pd
import io
from tqdm import tqdm
import os

LEIE_URL = "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"
from src.config import settings
TMP_LEIE_CSV = str(settings.DATA_DIR / "raw" / "leie_full.csv")

def main():
    print("Downloading OIG LEIE Exclusion List...")
    # ... rest uses settings
    response = requests.get(LEIE_URL, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs("data/raw", exist_ok=True)
    with open(TMP_LEIE_CSV, "wb") as f, tqdm(
        desc="Downloading LEIE",
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            size = f.write(chunk)
            bar.update(size)

    print("Loading LEIE into DuckDB...")
    conn = duckdb.connect(settings.DB_PATH)
    
    # Clean it up: Some NPIs might be 0 or empty in the CSV
    # LEIE has its own column names: LASTNAME, FIRSTNAME, MIDNAME, BUSNAME, GENERAL, SPECIALTY, UPIN, NPI, DOB, ADDRESS, CITY, STATE, ZIP, EXCLTYPE, EXCLDATE, REINDATE, WAIVERDATE, WVRSTATE
    
    conn.execute(f"""
        INSERT INTO leie_exclusions 
        SELECT * FROM read_csv_auto('{TMP_LEIE_CSV}', normalize_names=True)
    """)
    
    # Update providers table with exclusion flags
    print("Updating provider exclusion flags...")
    conn.execute("""
        UPDATE providers 
        SET is_excluded = TRUE 
        WHERE npi IN (SELECT CAST(npi AS VARCHAR) FROM leie_exclusions WHERE npi IS NOT NULL AND npi != '0')
    """)
    
    excluded_count = conn.execute("SELECT COUNT(*) FROM providers WHERE is_excluded = TRUE").fetchone()[0]
    print(f"Ingestion complete. Found {excluded_count} matches in our provider database.")
    
    conn.close()

if __name__ == "__main__":
    main()
