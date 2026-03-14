from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId, operators

from database.models import Buyer, Admin
from schemas.buyer import BuyerCreate, BuyerUpdate, BuyerResponse
from utils.storage import save_to_drive, update_drive_file, delete_from_drive, get_all_files, BUYER_DRIVE
from utils.auth import get_current_admin

router = APIRouter()

@router.post("", response_model=BuyerResponse, status_code=201)
async def create_buyer(
    buyer: BuyerCreate, 
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new buyer in MongoDB"""
    
    db_buyer = Buyer(**buyer.model_dump())
    await db_buyer.insert()
    
    # Save to drive
    buyer_dict = db_buyer.model_dump()
    buyer_dict['id'] = str(db_buyer.id)
    buyer_dict['created_at'] = str(db_buyer.created_at)
    buyer_dict['updated_at'] = str(db_buyer.updated_at)
    
    save_to_drive(BUYER_DRIVE, f"buyer_{db_buyer.id}", buyer_dict)
    
    return db_buyer

@router.get("", response_model=List[BuyerResponse])
async def get_buyers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    country: Optional[str] = None,
    city: Optional[str] = None,
    payment_terms: Optional[str] = None
):
    """Get all buyers with MongoDB filters"""
    
    query = Buyer.find_all()
    
    if country:
        query = query.find(operators.RegEx(Buyer.country, country, "i"))
    
    if city:
        query = query.find(operators.RegEx(Buyer.city, city, "i"))
    
    if payment_terms:
        if payment_terms.upper() not in ["FOB", "CIF"]:
            raise HTTPException(status_code=400, detail='Terms must be "FOB" or "CIF"')
        query = query.find(Buyer.payment_terms == payment_terms.upper())
    
    return await query.skip(skip).limit(limit).to_list()

@router.get("/{buyer_id}", response_model=BuyerResponse)
async def get_buyer(buyer_id: PydanticObjectId):
    """Get specific buyer from MongoDB"""
    
    db_buyer = await Buyer.get(buyer_id)
    if not db_buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return db_buyer

@router.put("/{buyer_id}", response_model=BuyerResponse)
async def update_buyer(
    buyer_id: PydanticObjectId, 
    buyer: BuyerUpdate,
    current_admin: Admin = Depends(get_current_admin)
):
    """Update buyer in MongoDB"""
    
    db_buyer = await Buyer.get(buyer_id)
    if not db_buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    # Update fields
    update_data = buyer.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_buyer, field, value)
    
    db_buyer.updated_at = datetime.utcnow()
    await db_buyer.save()
    
    # Update drive file
    buyer_dict = db_buyer.model_dump()
    buyer_dict['id'] = str(db_buyer.id)
    buyer_dict['created_at'] = str(db_buyer.created_at)
    buyer_dict['updated_at'] = str(db_buyer.updated_at)
    
    update_drive_file(BUYER_DRIVE, f"buyer_{buyer_id}", buyer_dict)
    
    return db_buyer

@router.delete("/{buyer_id}", status_code=204)
async def delete_buyer(
    buyer_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete buyer from MongoDB"""
    
    db_buyer = await Buyer.get(buyer_id)
    if not db_buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    await db_buyer.delete()
    delete_from_drive(BUYER_DRIVE, f"buyer_{buyer_id}")
    
    return None

@router.get("/drive-info", include_in_schema=False)
async def get_drive_info():
    """Get drive information"""
    import os
    files = get_all_files(BUYER_DRIVE)
    
    return {
        "status": "success",
        "drive_path": BUYER_DRIVE,
        "folder_exists": os.path.exists(BUYER_DRIVE),
        "is_writable": os.access(BUYER_DRIVE, os.W_OK) if os.path.exists(BUYER_DRIVE) else False,
        "total_files": len(files),
        "files": files
    }