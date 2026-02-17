-- sql/schema_v1.sql: Core Relational Model for Medicaid Spend Watch

-- Providers Registry
CREATE TABLE IF NOT EXISTS providers (
    npi VARCHAR PRIMARY KEY,
    name VARCHAR,
    taxonomy_desc VARCHAR,
    org_type VARCHAR, -- e.g., 'NPI-1' (Individual) or 'NPI-2' (Organization)
    city VARCHAR,
    state VARCHAR,
    postal_code VARCHAR,
    is_excluded BOOLEAN DEFAULT FALSE, -- OIG LEIE flag
    risk_score DOUBLE DEFAULT 0.0,
    auth_official_name VARCHAR,
    auth_official_title VARCHAR,
    auth_official_phone VARCHAR,
    mailing_address VARCHAR,
    mailing_city VARCHAR,
    mailing_state VARCHAR,
    mailing_zip VARCHAR,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medicaid Spending Records
-- Storing at the grain of Provider x HCPCS x Period
CREATE TABLE IF NOT EXISTS medicaid_spend (
    billing_npi VARCHAR,
    servicing_npi VARCHAR,
    hcpcs_code VARCHAR,
    period DATE,
    total_paid DOUBLE,
    total_claims INTEGER,
    unique_beneficiaries INTEGER,
    FOREIGN KEY (billing_npi) REFERENCES providers(npi)
);

-- Risk Flags and Explanations
CREATE TABLE IF NOT EXISTS risk_flags (
    npi VARCHAR,
    flag_type VARCHAR, -- e.g., 'PRICE_OUTLIER', 'TEMPORAL_SPIKE', 'LEIE_MATCH'
    flag_score DOUBLE,
    reason VARCHAR,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (npi) REFERENCES providers(npi)
);

-- OIG LEIE Exclusions List (Full Database)
CREATE TABLE IF NOT EXISTS leie_exclusions (
    last_name VARCHAR,
    first_name VARCHAR,
    mid_name VARCHAR,
    bus_name VARCHAR,
    general_specialty VARCHAR,
    specialty VARCHAR,
    upin VARCHAR,
    npi VARCHAR,
    dob VARCHAR,
    address VARCHAR,
    city VARCHAR,
    state VARCHAR,
    zip VARCHAR,
    excl_type VARCHAR,
    excl_date VARCHAR,
    rein_date VARCHAR,
    waiver_date VARCHAR,
    wvr_state VARCHAR
);

-- Indices for analytical speed
CREATE INDEX IF NOT EXISTS idx_spend_npi ON medicaid_spend(billing_npi);
CREATE INDEX IF NOT EXISTS idx_spend_hcpcs ON medicaid_spend(hcpcs_code);
CREATE INDEX IF NOT EXISTS idx_spend_period ON medicaid_spend(period);
CREATE INDEX IF NOT EXISTS idx_leie_npi ON leie_exclusions(npi);
