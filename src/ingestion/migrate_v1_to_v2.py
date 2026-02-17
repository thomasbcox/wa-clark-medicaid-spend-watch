import duckdb
import pandas as pd
import os

DB_PATH = "data/processed/medicaid_watch.db"
SPEND_CSV = "data/processed/clark_county_medicaid_spend.csv"
ENTITY_CSV = "data/processed/outlier_entity_details.csv"

def migrate():
    if not os.path.exists(DB_PATH):
        print("Error: Database not initialized.")
        return

    conn = duckdb.connect(DB_PATH)
    
    print("Migrating provider details...")
    # Load enriched outliers into providers table
    if os.path.exists(ENTITY_CSV):
        enriched_df = pd.read_csv(ENTITY_CSV)
        # Map columns to schema: NPI, Name, Specialty, City, State, PostalCode, OrgType
        # Schema: npi, name, taxonomy_desc, org_type, city, state, postal_code
        providers_df = enriched_df.rename(columns={
            "NPI": "npi",
            "Name": "name",
            "Specialty": "taxonomy_desc",
            "OrgType": "org_type",
            "City": "city",
            "State": "state",
            "PostalCode": "postal_code"
        })
        # Insert or replace
        conn.execute("INSERT OR REPLACE INTO providers (npi, name, taxonomy_desc, org_type, city, state, postal_code) SELECT * FROM providers_df")
        print(f"Migrated {len(enriched_df)} providers.")

    print("Migrating medicaid spending records...")
    if os.path.exists(SPEND_CSV):
        # Read with correct headers (since our file doesn't have them, or we wrote them in later scripts)
        # Note: Phase 1 filter_hhs_data.py wrote headers.
        spend_df = pd.read_csv(SPEND_CSV)
        
        # Schema: billing_npi, servicing_npi, hcpcs_code, period, total_paid, total_claims, unique_beneficiaries
        spend_df_lite = spend_df.rename(columns={
            "BILLING_PROVIDER_NPI_NUM": "billing_npi",
            "SERVICING_PROVIDER_NPI_NUM": "servicing_npi",
            "HCPCS_CODE": "hcpcs_code",
            "CLAIM_FROM_MONTH": "period",
            "TOTAL_PAID": "total_paid",
            "TOTAL_CLAIMS": "total_claims",
            "TOTAL_UNIQUE_BENEFICIARIES": "unique_beneficiaries"
        })
        
        # Ensure 'period' is a date
        spend_df_lite["period"] = pd.to_datetime(spend_df_lite["period"]).dt.date
        
        # Cast NPIs to string for VARCHAR columns
        spend_df_lite["billing_npi"] = spend_df_lite["billing_npi"].astype(str)
        spend_df_lite["servicing_npi"] = spend_df_lite["servicing_npi"].astype(str)

        # PRE-POPULATE PROVIDERS to avoid FK violations
        print("Pre-populating providers table with unique NPIs...")
        all_billing_npis = spend_df_lite[["billing_npi"]].drop_duplicates().rename(columns={"billing_npi": "npi"})
        conn.execute("INSERT OR IGNORE INTO providers (npi) SELECT npi FROM all_billing_npis")
        
        # Schema expects: billing_npi, servicing_npi, hcpcs_code, period, total_paid, total_claims, unique_beneficiaries
        cols = ["billing_npi", "servicing_npi", "hcpcs_code", "period", "total_paid", "total_claims", "unique_beneficiaries"]
        spend_df_lite = spend_df_lite[cols]
        
        # Insert into DuckDB
        conn.execute("INSERT INTO medicaid_spend SELECT * FROM spend_df_lite")
        print(f"Migrated {len(spend_df_lite)} spending records.")
        print(f"Migrated {len(spend_df_lite)} spending records.")

    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
