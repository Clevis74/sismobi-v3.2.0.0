"""
Energy Bills management routes for SISMOBI 3.2.0
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog
import uuid
from datetime import datetime

from database import get_database
from models import EnergyBill, EnergyBillCreate, EnergyBillUpdate, MessageResponse, User
from auth import get_current_active_user
from utils import get_paginated_results, convert_objectid_to_str

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/energy-bills", tags=["energy-bills"])

@router.get("/", response_model=dict)
async def get_energy_bills(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    property_id: Optional[str] = Query(None),
    group_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None, ge=2000, le=3000),
    month: Optional[int] = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all energy bills with pagination and filters"""
    try:
        filter_dict = {}
        if property_id:
            filter_dict["property_id"] = property_id
        if group_id:
            filter_dict["group_id"] = group_id
        if year:
            filter_dict["year"] = year
        if month:
            filter_dict["month"] = month
            
        result = await get_paginated_results(
            db.energy_bills, filter_dict, page, page_size, "reading_date", -1
        )
        
        logger.info("Energy bills retrieved", count=len(result["items"]), user=current_user.email)
        return result
        
    except Exception as e:
        logger.error("Error retrieving energy bills", error=str(e), user=current_user.email)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{bill_id}", response_model=EnergyBill)
async def get_energy_bill(
    bill_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get specific energy bill by ID"""
    try:
        bill_doc = await db.energy_bills.find_one({"id": bill_id})
        if not bill_doc:
            raise HTTPException(status_code=404, detail="Energy bill not found")
        
        bill_data = convert_objectid_to_str(bill_doc)
        logger.info("Energy bill retrieved", bill_id=bill_id, user=current_user.email)
        return EnergyBill(**bill_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving energy bill", bill_id=bill_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=EnergyBill)
async def create_energy_bill(
    bill_data: EnergyBillCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new energy bill"""
    try:
        # Convert to dict and add metadata
        bill_dict = bill_data.dict()
        bill_dict.update({
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # Verify property exists
        property_doc = await db.properties.find_one({"id": bill_dict["property_id"]})
        if not property_doc:
            raise HTTPException(status_code=400, detail="Property not found")
        
        result = await db.energy_bills.insert_one(bill_dict)
        created_bill = await db.energy_bills.find_one({"_id": result.inserted_id})
        
        bill_response = convert_objectid_to_str(created_bill)
        logger.info("Energy bill created", bill_id=bill_response["id"], user=current_user.email)
        return EnergyBill(**bill_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating energy bill", error=str(e), user=current_user.email)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{bill_id}", response_model=EnergyBill)
async def update_energy_bill(
    bill_id: str,
    bill_updates: EnergyBillUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update existing energy bill"""
    try:
        # Check if bill exists
        existing_bill = await db.energy_bills.find_one({"id": bill_id})
        if not existing_bill:
            raise HTTPException(status_code=404, detail="Energy bill not found")
        
        # Prepare update data
        update_data = {k: v for k, v in bill_updates.dict().items() if v is not None}
        if update_data:
            update_data["updated_at"] = datetime.now()
            
            await db.energy_bills.update_one(
                {"id": bill_id},
                {"$set": update_data}
            )
        
        updated_bill = await db.energy_bills.find_one({"id": bill_id})
        bill_response = convert_objectid_to_str(updated_bill)
        
        logger.info("Energy bill updated", bill_id=bill_id, user=current_user.email)
        return EnergyBill(**bill_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating energy bill", bill_id=bill_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{bill_id}", response_model=MessageResponse)
async def delete_energy_bill(
    bill_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete energy bill"""
    try:
        # Check if bill exists
        existing_bill = await db.energy_bills.find_one({"id": bill_id})
        if not existing_bill:
            raise HTTPException(status_code=404, detail="Energy bill not found")
        
        # Delete bill
        await db.energy_bills.delete_one({"id": bill_id})
        
        logger.info("Energy bill deleted", bill_id=bill_id, user=current_user.email)
        return {"message": "Energy bill deleted successfully", "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting energy bill", bill_id=bill_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/group/{group_id}/summary", response_model=dict)
async def get_group_summary(
    group_id: str,
    year: Optional[int] = Query(None, ge=2000, le=3000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get summary for energy bill group"""
    try:
        filter_dict = {"group_id": group_id}
        if year:
            filter_dict["year"] = year
            
        cursor = db.energy_bills.find(filter_dict)
        bills = []
        async for bill in cursor:
            bills.append(convert_objectid_to_str(bill))
        
        if not bills:
            return {
                "group_id": group_id,
                "total_bills": 0,
                "total_amount": 0,
                "total_kwh": 0,
                "average_amount": 0,
                "average_kwh": 0,
                "bills": []
            }
        
        total_amount = sum(bill["total_amount"] for bill in bills)
        total_kwh = sum(bill["total_kwh"] for bill in bills)
        
        summary = {
            "group_id": group_id,
            "total_bills": len(bills),
            "total_amount": total_amount,
            "total_kwh": total_kwh,
            "average_amount": total_amount / len(bills),
            "average_kwh": total_kwh / len(bills),
            "bills": bills
        }
        
        logger.info("Energy bill group summary retrieved", group_id=group_id, user=current_user.email)
        return summary
        
    except Exception as e:
        logger.error("Error retrieving group summary", group_id=group_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")