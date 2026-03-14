from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId, operators

from database.models import Manufacturer, Admin
from schemas.manufacturer import ManufacturerCreate, ManufacturerUpdate, ManufacturerResponse
from utils.storage import save_to_drive, update_drive_file, delete_from_drive, get_all_files, MANUFACTURER_DRIVE
from utils.auth import get_current_admin

router = APIRouter()

@router.post("", response_model=ManufacturerResponse, status_code=201)
async def create_manufacturer(
    manufacturer: ManufacturerCreate, 
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new manufacturer in MongoDB"""
    
    db_mfr = Manufacturer(**manufacturer.model_dump())
    await db_mfr.insert()
    
    # Save to drive
    mfr_dict = db_mfr.model_dump()
    mfr_dict['id'] = str(db_mfr.id)
    mfr_dict['created_at'] = str(db_mfr.created_at)
    mfr_dict['updated_at'] = str(db_mfr.updated_at)
    
    save_to_drive(MANUFACTURER_DRIVE, f"manufacturer_{db_mfr.id}", mfr_dict)
    
    return db_mfr

@router.get("", response_model=List[ManufacturerResponse])
async def get_manufacturers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    city: Optional[str] = None,
    product_category: Optional[str] = None
):
    """Get all manufacturers with MongoDB filters"""
    
    query = Manufacturer.find_all()
    
    if city:
        query = query.find(operators.RegEx(Manufacturer.city, city, "i"))
    
    if product_category:
        query = query.find(operators.RegEx(Manufacturer.product_category, product_category, "i"))
    
    return await query.skip(skip).limit(limit).to_list()

@router.get("/{manufacturer_id}", response_model=ManufacturerResponse)
async def get_manufacturer(manufacturer_id: PydanticObjectId):
    """Get specific manufacturer from MongoDB"""
    
    db_mfr = await Manufacturer.get(manufacturer_id)
    if not db_mfr:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return db_mfr

@router.put("/{manufacturer_id}", response_model=ManufacturerResponse)
async def update_manufacturer(
    manufacturer_id: PydanticObjectId, 
    manufacturer: ManufacturerUpdate,
    current_admin: Admin = Depends(get_current_admin)
):
    """Update manufacturer in MongoDB"""
    
    db_mfr = await Manufacturer.get(manufacturer_id)
    if not db_mfr:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    
    # Update fields
    update_data = manufacturer.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_mfr, field, value)
    
    db_mfr.updated_at = datetime.utcnow()
    await db_mfr.save()
    
    # Update drive file
    mfr_dict = db_mfr.model_dump()
    mfr_dict['id'] = str(db_mfr.id)
    mfr_dict['created_at'] = str(db_mfr.created_at)
    mfr_dict['updated_at'] = str(db_mfr.updated_at)
    
    update_drive_file(MANUFACTURER_DRIVE, f"manufacturer_{manufacturer_id}", mfr_dict)
    
    return db_mfr

@router.delete("/{manufacturer_id}", status_code=204)
async def delete_manufacturer(
    manufacturer_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete manufacturer from MongoDB"""
    
    db_mfr = await Manufacturer.get(manufacturer_id)
    if not db_mfr:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    
    await db_mfr.delete()
    delete_from_drive(MANUFACTURER_DRIVE, f"manufacturer_{manufacturer_id}")
    
    return None

@router.get("/drive-info", include_in_schema=False)
async def get_drive_info():
    """Get drive information"""
    import os
    files = get_all_files(MANUFACTURER_DRIVE)
    
    return {
        "status": "success",
        "drive_path": MANUFACTURER_DRIVE,
        "folder_exists": os.path.exists(MANUFACTURER_DRIVE),
        "is_writable": os.access(MANUFACTURER_DRIVE, os.W_OK) if os.path.exists(MANUFACTURER_DRIVE) else False,
        "total_files": len(files),
        "files": files
    }