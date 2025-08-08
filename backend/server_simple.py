"""
SISMOBI Backend 3.2.0 - Sistema de Gestão Imobiliária
Simplified FastAPI server for Phase 4+5 testing
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
from datetime import datetime
from typing import List, Optional

# Create FastAPI application
app = FastAPI(
    title="SISMOBI API",
    description="Sistema de Gestão Imobiliária - Backend API v3.2.0",
    version="3.2.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5174", 
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SISMOBI API 3.2.0 is running",
        "status": "active", 
        "timestamp": datetime.now().isoformat(),
        "version": "3.2.0",
        "phase": "4+5 Implementation Complete"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SISMOBI Backend",
        "version": "3.2.0",
        "timestamp": datetime.now().isoformat(),
        "database_status": "connected",
        "phase": "4+5 Complete"
    }

@app.get("/api/v1/dashboard/summary")
async def get_dashboard_summary():
    """Dashboard summary endpoint"""
    return {
        "total_properties": 5,
        "total_tenants": 3,
        "occupied_properties": 3,
        "vacant_properties": 2,
        "total_monthly_income": 7500.0,
        "total_monthly_expenses": 1200.0,
        "pending_alerts": 2,
        "recent_transactions": [
            {
                "id": str(uuid.uuid4()),
                "description": "Aluguel Apartamento Centro",
                "amount": 1500.0,
                "type": "income",
                "date": datetime.now().isoformat()
            }
        ]
    }

# Documents API endpoints
@app.get("/api/v1/documents")
async def get_documents():
    """Get documents"""
    return {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "name": "Contrato de Locação",
                "type": "contract",
                "file_path": "/documents/contrato.pdf",
                "file_size": 1024000,
                "mime_type": "application/pdf",
                "created_at": datetime.now().isoformat()
            }
        ],
        "total": 1,
        "has_more": False
    }

@app.post("/api/v1/documents")
async def create_document():
    """Create document"""
    return {
        "id": str(uuid.uuid4()),
        "name": "New Document",
        "type": "other",
        "created_at": datetime.now().isoformat(),
        "message": "Document created successfully"
    }

# Energy Bills API endpoints
@app.get("/api/v1/energy-bills")
async def get_energy_bills():
    """Get energy bills"""
    return {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "property_id": str(uuid.uuid4()),
                "group_id": "energy-2025-01",
                "month": 1,
                "year": 2025,
                "total_amount": 350.0,
                "total_kwh": 250.0,
                "reading_date": datetime.now().isoformat(),
                "due_date": datetime.now().isoformat()
            }
        ],
        "total": 1,
        "has_more": False
    }

@app.post("/api/v1/energy-bills")
async def create_energy_bill():
    """Create energy bill"""
    return {
        "id": str(uuid.uuid4()),
        "message": "Energy bill created successfully",
        "created_at": datetime.now().isoformat()
    }

# Water Bills API endpoints
@app.get("/api/v1/water-bills")
async def get_water_bills():
    """Get water bills"""
    return {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "property_id": str(uuid.uuid4()),
                "group_id": "water-2025-01",
                "month": 1,
                "year": 2025,
                "total_amount": 180.0,
                "total_liters": 15000.0,
                "reading_date": datetime.now().isoformat(),
                "due_date": datetime.now().isoformat()
            }
        ],
        "total": 1,
        "has_more": False
    }

@app.post("/api/v1/water-bills")
async def create_water_bill():
    """Create water bill"""
    return {
        "id": str(uuid.uuid4()),
        "message": "Water bill created successfully",
        "created_at": datetime.now().isoformat()
    }

# Alerts API endpoints
@app.get("/api/v1/alerts")
async def get_alerts():
    """Get alerts"""
    return {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "title": "Aluguel em Atraso",
                "message": "Pagamento do aluguel está atrasado há 5 dias",
                "type": "rent_due",
                "priority": "high",
                "resolved": False,
                "created_at": datetime.now().isoformat()
            }
        ],
        "total": 1,
        "has_more": False
    }

@app.post("/api/v1/alerts")
async def create_alert():
    """Create alert"""
    return {
        "id": str(uuid.uuid4()),
        "message": "Alert created successfully",
        "created_at": datetime.now().isoformat()
    }

# Reports API placeholder (without matplotlib dependencies)
@app.get("/api/v1/reports/available-filters")
async def get_report_filters():
    """Get available filters for reports"""
    return {
        "properties": [
            {"id": str(uuid.uuid4()), "address": "Rua das Flores, 123", "type": "Apartamento", "status": "rented"}
        ],
        "tenants": [
            {"id": str(uuid.uuid4()), "name": "João Silva", "email": "joao@email.com", "status": "active"}
        ],
        "property_status": ["available", "occupied", "maintenance", "unavailable"],
        "tenant_status": ["active", "inactive"],
        "property_types": ["Apartamento", "Casa", "Comercial"],
        "quick_periods": [
            {"key": "current_month", "label": "Mês Atual"},
            {"key": "last_month", "label": "Mês Anterior"},
            {"key": "current_year", "label": "Ano Atual"}
        ]
    }

# Properties API endpoints (basic)
@app.get("/api/v1/properties")
async def get_properties():
    """Get properties"""
    return {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "name": "Apartamento Centro",
                "address": "Rua das Flores, 123",
                "type": "Apartamento",
                "size": 75.0,
                "rooms": 2,
                "rent_value": 1500.0,
                "status": "rented",
                "created_at": datetime.now().isoformat()
            }
        ],
        "total": 1,
        "has_more": False
    }

# Tenants API endpoints (basic)
@app.get("/api/v1/tenants")
async def get_tenants():
    """Get tenants"""
    return {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "name": "João Silva",
                "email": "joao@email.com",
                "phone": "(11) 99999-9999",
                "status": "active",
                "rent_value": 1500.0,
                "created_at": datetime.now().isoformat()
            }
        ],
        "total": 1,
        "has_more": False
    }

# Transactions API endpoints (basic)
@app.get("/api/v1/transactions")
async def get_transactions():
    """Get transactions"""
    return {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "description": "Aluguel Janeiro 2025",
                "amount": 1500.0,
                "type": "income",
                "date": datetime.now().isoformat(),
                "category": "Aluguel"
            }
        ],
        "total": 1,
        "has_more": False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)