import requests
import zipfile
import io
import csv
import json
from tqdm import tqdm
import os

HHS_DATA_URL = "https://stopendataprod.blob.core.windows.net/datasets/medicaid-provider-spending/2026-02-09/medicaid-provider-spending.csv.zip"
NPI_LIST_PATH = "data/raw/clark_county_npis.json"
OUTPUT_PATH = "data/processed/clark_county_medicaid_spend.csv"

def main():
    if not os.path.exists(NPI_LIST_PATH):
        print(f"Error: NPI list not found at {NPI_LIST_PATH}. Run get_clark_county_npis.py first.")
        return

    with open(NPI_LIST_PATH, "r") as f:
        clark_npis = set(str(npi) for npi in json.load(f))
    
    print(f"Loaded {len(clark_npis)} NPIs for filtering.")

    print(f"Downloading and filtering HHS data (streaming)...")
    response = requests.get(HHS_DATA_URL, stream=True)
    response.raise_for_status()

    # Since it's a ZIP, we ideally want to stream the ZIP content to avoid full memory usage.
    # However, Python's zipfile doesn't support streaming from a socket easily without downloading first.
    # Given the 3.36 GB size, we'll download it to data/raw temporary file if disk space allows.
    
    tmp_zip = "data/raw/medicaid-provider-spending.csv.zip"
    total_size = int(response.headers.get('content-length', 0))
    
    with open(tmp_zip, "wb") as f, tqdm(
        desc="Downloading",
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            size = f.write(chunk)
            bar.update(size)

    print("Filtering data...")
    with zipfile.ZipFile(tmp_zip) as z:
        csv_filename = z.namelist()[0]
        with z.open(csv_filename) as f_in:
            # Wrap bytes stream in TextIOWrapper for csv reader
            f_text = io.TextIOWrapper(f_in, encoding='utf-8')
            reader = csv.DictReader(f_text)
            
            with open(OUTPUT_PATH, "w", newline='') as f_out:
                writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
                writer.writeheader()
                
                count = 0
                match_count = 0
                for row in tqdm(reader, desc="Processing rows"):
                    count += 1
                    billing_npi = str(row.get("BILLING_PROVIDER_NPI_NUM", ""))
                    servicing_npi = str(row.get("SERVICING_PROVIDER_NPI_NUM", ""))
                    
                    if billing_npi in clark_npis or servicing_npi in clark_npis:
                        writer.writerow(row)
                        match_count += 1
                
                print(f"Processed {count} rows. Found {match_count} matches for Clark County.")
                print(f"Saved filtered data to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
