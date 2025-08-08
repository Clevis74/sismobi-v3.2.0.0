"""
Documents management routes for SISMOBI 3.2.0
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog
import uuid
import os
from datetime import datetime

from database import get_database
from models import Document, DocumentCreate, DocumentUpdate, MessageResponse, User
from auth import get_current_active_user
from utils import get_paginated_results, convert_objectid_to_str

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/", response_model=dict)
async def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    property_id: Optional[str] = Query(None),
    tenant_id: Optional[str] = Query(None),
    doc_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all documents with pagination and filters"""
    try:
        filter_dict = {}
        if property_id:
            filter_dict["property_id"] = property_id
        if tenant_id:
            filter_dict["tenant_id"] = tenant_id
        if doc_type:
            filter_dict["type"] = doc_type
            
        result = await get_paginated_results(
            db.documents, filter_dict, page, page_size, "created_at", -1
        )
        
        logger.info("Documents retrieved", count=len(result["items"]), user=current_user.email)
        return result
        
    except Exception as e:
        logger.error("Error retrieving documents", error=str(e), user=current_user.email)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get specific document by ID"""
    try:
        document_doc = await db.documents.find_one({"id": document_id})
        if not document_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document_data = convert_objectid_to_str(document_doc)
        logger.info("Document retrieved", document_id=document_id, user=current_user.email)
        return Document(**document_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving document", document_id=document_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=Document)
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new document"""
    try:
        # Convert to dict and add metadata
        document_dict = document_data.dict()
        document_dict.update({
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # Verify property exists if provided
        if document_dict.get("property_id"):
            property_doc = await db.properties.find_one({"id": document_dict["property_id"]})
            if not property_doc:
                raise HTTPException(status_code=400, detail="Property not found")
                
        # Verify tenant exists if provided
        if document_dict.get("tenant_id"):
            tenant_doc = await db.tenants.find_one({"id": document_dict["tenant_id"]})
            if not tenant_doc:
                raise HTTPException(status_code=400, detail="Tenant not found")
        
        result = await db.documents.insert_one(document_dict)
        created_document = await db.documents.find_one({"_id": result.inserted_id})
        
        document_response = convert_objectid_to_str(created_document)
        logger.info("Document created", document_id=document_response["id"], user=current_user.email)
        return Document(**document_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating document", error=str(e), user=current_user.email)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: str,
    document_updates: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update existing document"""
    try:
        # Check if document exists
        existing_document = await db.documents.find_one({"id": document_id})
        if not existing_document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Prepare update data
        update_data = {k: v for k, v in document_updates.dict().items() if v is not None}
        if update_data:
            update_data["updated_at"] = datetime.now()
            
            await db.documents.update_one(
                {"id": document_id},
                {"$set": update_data}
            )
        
        updated_document = await db.documents.find_one({"id": document_id})
        document_response = convert_objectid_to_str(updated_document)
        
        logger.info("Document updated", document_id=document_id, user=current_user.email)
        return Document(**document_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating document", document_id=document_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete document"""
    try:
        # Check if document exists
        existing_document = await db.documents.find_one({"id": document_id})
        if not existing_document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete document from database
        await db.documents.delete_one({"id": document_id})
        
        # TODO: Delete actual file from storage
        # file_path = existing_document.get("file_path")
        # if file_path and os.path.exists(file_path):
        #     os.remove(file_path)
        
        logger.info("Document deleted", document_id=document_id, user=current_user.email)
        return {"message": "Document deleted successfully", "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting document", document_id=document_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    property_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    doc_type: str = "other",
    description: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Upload document file (simulated - returns metadata only)"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
            
        # Create document metadata
        document_dict = {
            "id": str(uuid.uuid4()),
            "property_id": property_id,
            "tenant_id": tenant_id,
            "name": file.filename,
            "type": doc_type,
            "file_path": f"/documents/{file.filename}",  # Simulated path
            "file_size": 0,  # Would be actual file size
            "mime_type": file.content_type or "application/octet-stream",
            "description": description,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Verify references exist
        if property_id:
            property_doc = await db.properties.find_one({"id": property_id})
            if not property_doc:
                raise HTTPException(status_code=400, detail="Property not found")
                
        if tenant_id:
            tenant_doc = await db.tenants.find_one({"id": tenant_id})
            if not tenant_doc:
                raise HTTPException(status_code=400, detail="Tenant not found")
        
        # TODO: Actually save file to storage
        # file_content = await file.read()
        # file_path = f"./uploads/{document_dict['id']}_{file.filename}"
        # with open(file_path, "wb") as f:
        #     f.write(file_content)
        # document_dict["file_size"] = len(file_content)
        
        # Save metadata to database
        result = await db.documents.insert_one(document_dict)
        created_document = await db.documents.find_one({"_id": result.inserted_id})
        
        document_response = convert_objectid_to_str(created_document)
        logger.info("Document uploaded", document_id=document_response["id"], filename=file.filename, user=current_user.email)
        return Document(**document_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error uploading document", filename=file.filename if file else "unknown", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")