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
        mailing_addr = next((a for a in res.get("addresses", []) if a.get("address_purpose") == "MAILING"), res.get("addresses", [{}])[0])
        
        # Authorized Official Details (Inside basic object with prefix)
        basic = res.get("basic", {})
        auth_name = f"{basic.get('authorized_official_first_name', '')} {basic.get('authorized_official_last_name', '')}".strip()
        
        return {
            "npi": npi,
            "name": name,
            "taxonomy_desc": primary_tax.get("desc", "Unknown"),
            "org_type": res.get("enumeration_type", "Unknown"),
            "city": practice_addr.get("city", "Unknown"),
            "state": practice_addr.get("state", "Unknown"),
            "postal_code": practice_addr.get("postal_code", "Unknown"),
            "auth_official_name": auth_name or None,
            "auth_official_title": basic.get("authorized_official_title_or_position"),
            "auth_official_phone": basic.get("authorized_official_telephone_number"),
            "mailing_address": mailing_addr.get("address_1"),
            "mailing_city": mailing_addr.get("city"),
            "mailing_state": mailing_addr.get("state"),
            "mailing_zip": mailing_addr.get("postal_code")
        }
    except Exception:
        return None

def main(batch_size=100):
    conn = duckdb.connect(DB_PATH)
    
    # Find NPIs that need enrichment (missing official data)
    # Prioritize flagged providers
    query = """
        SELECT p.npi FROM providers p 
        LEFT JOIN risk_flags f ON p.npi = f.npi
        WHERE p.auth_official_name IS NULL 
        GROUP BY 1 
        ORDER BY COUNT(f.flag_type) DESC 
        LIMIT ?
    """
    unnamed_npis = [r[0] for r in conn.execute(query, [batch_size]).fetchall()]
    
    if not unnamed_npis:
        print("All providers already enriched.")
        return

    print(f"Enriching {len(unnamed_npis)} providers...")
    for npi in tqdm(unnamed_npis):
        details = get_npi_details(npi)
        if details:
            conn.execute("""
                UPDATE providers 
                SET name = ?, taxonomy_desc = ?, org_type = ?, city = ?, state = ?, postal_code = ?, 
                    auth_official_name = ?, auth_official_title = ?, auth_official_phone = ?,
                    mailing_address = ?, mailing_city = ?, mailing_state = ?, mailing_zip = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE npi = ?
            """, [
                details["name"], details["taxonomy_desc"], details["org_type"], details["city"], details["state"], details["postal_code"],
                details["auth_official_name"], details["auth_official_title"], details["auth_official_phone"],
                details["mailing_address"], details["mailing_city"], details["mailing_state"], details["mailing_zip"],
                npi
            ])
        time.sleep(0.2) # Faster rate since we have many

    conn.close()
    print("Batch enrichment complete.")

if __name__ == "__main__":
    import sys
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    main(batch_size=size)
