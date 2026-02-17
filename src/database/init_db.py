import duckdb
import os

DB_PATH = "data/processed/medicaid_watch.db"
SCHEMA_PATH = "sql/schema_v1.sql"

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    conn = duckdb.connect(DB_PATH)
    
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    
    # Execute DDL
    conn.execute(schema_sql)
    print("Database schema applied successfully.")
    
    # List tables to verify
    tables = conn.execute("SHOW TABLES").fetchall()
    print(f"Tables created: {[t[0] for t in tables]}")
    conn.close()

if __name__ == "__main__":
    init_db()
