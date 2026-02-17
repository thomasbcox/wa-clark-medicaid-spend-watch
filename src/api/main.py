from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import duckdb
import os

app = FastAPI(title="Medicaid Spend Watch API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join("data", "processed", "medicaid_watch.db")

def get_db():
    return duckdb.connect(DB_PATH)

@app.get("/api/summary")
def get_summary():
    conn = get_db()
    total_spend = conn.execute("SELECT SUM(total_paid) FROM medicaid_spend").fetchone()[0]
    total_providers = conn.execute("SELECT COUNT(*) FROM providers").fetchone()[0]
    total_flags = conn.execute("SELECT COUNT(*) FROM risk_flags").fetchone()[0]
    conn.close()
    return {
        "total_spend": total_spend,
        "total_providers": total_providers,
        "total_flags": total_flags
    }

@app.get("/api/flagged-providers")
def get_flagged_providers(limit: int = 20):
    conn = get_db()
    # Join providers with risk_flags and get total spend
    query = """
        SELECT 
            p.npi,
            p.name,
            p.taxonomy_desc,
            COUNT(f.flag_type) as flag_count,
            MAX(p.risk_score) as risk_score,
            (SELECT SUM(total_paid) FROM medicaid_spend WHERE billing_npi = p.npi) as total_spend
        FROM providers p
        JOIN risk_flags f ON p.npi = f.npi
        GROUP BY 1, 2, 3
        ORDER BY flag_count DESC, total_spend DESC
        LIMIT ?
    """
    results = conn.execute(query, [limit]).df().to_dict(orient="records")
    conn.close()
    return results

@app.get("/api/provider/{npi}")
def get_provider_detail(npi: str):
    conn = get_db()
    provider = conn.execute("SELECT * FROM providers WHERE npi = ?", [npi]).df().to_dict(orient="records")
    if not provider:
        conn.close()
        raise HTTPException(status_code=44, detail="Provider not found")
    
    flags = conn.execute("SELECT * FROM risk_flags WHERE npi = ?", [npi]).df().to_dict(orient="records")
    spend_trend = conn.execute("""
        SELECT period, SUM(total_paid) as spend 
        FROM medicaid_spend 
        WHERE billing_npi = ? 
        GROUP BY 1 ORDER BY 1
    """, [npi]).df().to_dict(orient="records")
    
    conn.close()
    return {
        "details": provider[0],
        "flags": flags,
        "spend_trend": spend_trend
    }

# Serve static files for the dashboard
if os.path.exists("web"):
    app.mount("/", StaticFiles(directory="web", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
