import requests
import pandas as pd
import json
import time
from tqdm import tqdm
import os

NPPES_API_URL = "https://npiregistry.cms.hhs.gov/api/"
OUTLIER_NPIS = [
    1669411377, 1700809829, 1689892473, 1396023164, 1699707968, 
    1790021517, 1376939678, 1811925308, 1285685578, 1093864589, 
    1992759427, 1831258995, 1528285038, 1487811048, 1962453860, 
    1851328447, 1356357784, 1356487318, 1407870108, 1912055138, 
    1609061969, 1134178999, 1396134185, 1346504172
]

def get_npi_details(npi):
    params = {
        "version": "2.1",
        "number": npi
    }
    try:
        response = requests.get(NPPES_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        if not results:
            return None
            
        res = results[0]
        basic = res.get("basic", {})
        
        # Determine Name (Org vs Individual)
        name = basic.get("organization_name")
        if not name:
            fname = basic.get("first_name", "")
            lname = basic.get("last_name", "")
            name = f"{fname} {lname}".strip()
            
        # Extract Taxonomy
        taxonomies = res.get("taxonomies", [])
        primary_tax = next((t for t in taxonomies if t.get("primary")), taxonomies[0] if taxonomies else {})
        specialty = primary_tax.get("desc", "Unknown")
        
        # Extract Address
        addresses = res.get("addresses", [])
        practice_addr = next((a for a in addresses if a.get("address_purpose") == "LOCATION"), addresses[0] if addresses else {})
        city = practice_addr.get("city", "Unknown")
        state = practice_addr.get("state", "Unknown")
        postal = practice_addr.get("postal_code", "Unknown")
        
        return {
            "NPI": npi,
            "Name": name,
            "Specialty": specialty,
            "City": city,
            "State": state,
            "PostalCode": postal,
            "OrgType": res.get("enumeration_type", "Unknown")
        }
    except Exception as e:
        print(f"Error fetching NPI {npi}: {e}")
        return None

def main():
    print(f"Enriching {len(OUTLIER_NPIS)} outlier NPIs...")
    enriched_data = []
    
    for npi in tqdm(OUTLIER_NPIS):
        details = get_npi_details(npi)
        if details:
            enriched_data.append(details)
        time.sleep(0.5)
        
    df = pd.DataFrame(enriched_data)
    output_path = "data/processed/outlier_entity_details.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved enriched details to {output_path}")

if __name__ == "__main__":
    main()
