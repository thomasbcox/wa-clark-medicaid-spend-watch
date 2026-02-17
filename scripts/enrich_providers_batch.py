import requests
import duckdb
import time
from tqdm import tqdm

NPPES_API_URL = "https://npiregistry.cms.hhs.gov/api/"
DB_PATH = "data/processed/medicaid_watch.db"

def get_npi_details(npi):
    params = {"version": "2.1", "number": npi}
    try:
        response = requests.get(NPPES_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results: return None
        res = results[0]
        basic = res.get("basic", {})
        name = basic.get("organization_name") or f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip()
        taxonomies = res.get("taxonomies", [])
        primary_tax = next((t for t in taxonomies if t.get("primary")), taxonomies[0] if taxonomies else {})
        practice_addr = next((a for a in res.get("addresses", []) if a.get("address_purpose") == "LOCATION"), res.get("addresses", [{}])[0])
        
        return {
            "npi": npi,
            "name": name,
            "taxonomy_desc": primary_tax.get("desc", "Unknown"),
            "org_type": res.get("enumeration_type", "Unknown"),
            "city": practice_addr.get("city", "Unknown"),
            "state": practice_addr.get("state", "Unknown"),
            "postal_code": practice_addr.get("postal_code", "Unknown")
        }
    except Exception:
        return None

def main(batch_size=100):
    conn = duckdb.connect(DB_PATH)
    
    # Find NPIs that need enrichment
    unnamed_npis = [r[0] for r in conn.execute("SELECT npi FROM providers WHERE name IS NULL LIMIT ?", [batch_size]).fetchall()]
    
    if not unnamed_npis:
        print("All providers already enriched.")
        return

    print(f"Enriching {len(unnamed_npis)} providers...")
    for npi in tqdm(unnamed_npis):
        details = get_npi_details(npi)
        if details:
            conn.execute("""
                UPDATE providers 
                SET name = ?, taxonomy_desc = ?, org_type = ?, city = ?, state = ?, postal_code = ?, last_updated = CURRENT_TIMESTAMP
                WHERE npi = ?
            """, [details["name"], details["taxonomy_desc"], details["org_type"], details["city"], details["state"], details["postal_code"], npi])
        time.sleep(0.2) # Faster rate since we have many

    conn.close()
    print("Batch enrichment complete.")

if __name__ == "__main__":
    main()
