import requests
import json
import time
from tqdm import tqdm

CLARK_COUNTY_ZIPS = [
    "98601", "98604", "98606", "98607", "98622", "98629", "98642", "98660",
    "98661", "98662", "98663", "98664", "98665", "98666", "98667", "98668",
    "98671", "98674", "98675", "98682", "98683", "98684", "98685", "98686", "98687"
]

NPPES_API_URL = "https://npiregistry.cms.hhs.gov/api/"

def get_npis_for_zip(zip_code):
    npis = set()
    skip = 0
    limit = 200
    
    while True:
        params = {
            "version": "2.1",
            "postal_code": zip_code,
            "limit": limit,
            "skip": skip
        }
        try:
            response = requests.get(NPPES_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            if not results:
                break
                
            for res in results:
                npis.add(res["number"])
                
            if len(results) < limit or skip >= 1000:
                break
                
            skip += limit
            time.sleep(0.5)  # Respectful rate limiting
        except Exception as e:
            print(f"Error fetching zip {zip_code}: {e}")
            break
            
    return npis

def main():
    all_npis = set()
    print(f"Fetching NPIs for {len(CLARK_COUNTY_ZIPS)} zip codes in Clark County...")
    
    for zip_code in tqdm(CLARK_COUNTY_ZIPS):
        zip_npis = get_npis_for_zip(zip_code)
        all_npis.update(zip_npis)
        
    output_path = "data/raw/clark_county_npis.json"
    with open(output_path, "w") as f:
        json.dump(list(all_npis), f)
        
    print(f"Saved {len(all_npis)} unique NPIs to {output_path}")

if __name__ == "__main__":
    main()
