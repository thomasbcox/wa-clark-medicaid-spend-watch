import duckdb
import pandas as pd
import urllib.parse

DB_PATH = "data/processed/medicaid_watch.db"

def main():
    conn = duckdb.connect(DB_PATH)
    
    # Get top flagged providers with their official data
    query = """
        SELECT 
            p.npi,
            p.name,
            p.auth_official_name,
            p.auth_official_title,
            p.mailing_address,
            COUNT(f.flag_type) as flag_count,
            SUM(s.total_paid) as total_spend
        FROM providers p
        JOIN risk_flags f ON p.npi = f.npi
        LEFT JOIN medicaid_spend s ON p.npi = s.billing_npi
        GROUP BY 1, 2, 3, 4, 5
        ORDER BY flag_count DESC, total_spend DESC
        LIMIT 20
    """
    df = conn.execute(query).df()
    
    print("\n--- CORPORATE RESEARCH LEADS (Top 20 Flagged) ---\n")
    
    for _, row in df.iterrows():
        name_enc = urllib.parse.quote(row['name'] if row['name'] else "")
        official_enc = urllib.parse.quote(row['auth_official_name'] if row['auth_official_name'] else "")
        
        print(f"Provider: {row['name']} (NPI: {row['npi']})")
        print(f"  Flags: {row['flag_count']} | Total Spend: ${row['total_spend']:,.2f}")
        print(f"  Authorized Official: {row['auth_official_name']} ({row['auth_official_title']})")
        print(f"  Mailing: {row['mailing_address']}")
        print(f"  [SOS Search]: https://ccfs.sos.wa.gov/#/search (Search for '{row['name']}')")
        if official_enc:
            print(f"  [Official Google Search]: https://www.google.com/search?q={official_enc}+{name_enc}")
        print("-" * 50)

    conn.close()

if __name__ == "__main__":
    main()
