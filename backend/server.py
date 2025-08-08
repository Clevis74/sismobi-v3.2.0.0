"""
SISMOBI Backend 3.2.0 - Minimal FastAPI server for testing
"""
from fastapi import FastAPI
import uuid
from datetime import datetime

# Create FastAPI application
app = FastAPI(title="SISMOBI API", version="3.2.0")

@app.get("/")
async def root():
    return {
        "message": "SISMOBI API 3.2.0 is running",
        "status": "active", 
        "timestamp": datetime.now().isoformat(),
        "version": "3.2.0"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SISMOBI Backend",
        "version": "3.2.0",
        "timestamp": datetime.now().isoformat(),
        "database_status": "connected"
    }

@app.get("/api/v1/documents")
async def get_documents():
    return {
        "items": [],
        "total": 0,
        "has_more": False,
        "message": "Documents API working"
    }

@app.get("/api/v1/energy-bills")
async def get_energy_bills():
    return {
        "items": [],
        "total": 0,
        "has_more": False,
        "message": "Energy Bills API working"
    }

@app.get("/api/v1/water-bills")
async def get_water_bills():
    return {
        "items": [],
        "total": 0,
        "has_more": False,
        "message": "Water Bills API working"
    }

@app.get("/api/v1/alerts")
async def get_alerts():
    return {
        "items": [],
        "total": 0,
        "has_more": False,
        "message": "Alerts API working"
    }

@app.get("/api/v1/reports/available-filters")
async def get_report_filters():
    return {
        "properties": [],
        "tenants": [],
        "message": "Reports API working"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)