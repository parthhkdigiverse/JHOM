"""
File Upload Routes - MongoDB/Beanie Version
"""

import sys
import os
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId

from utils.storage import get_entity_folder, save_uploaded_file, MAX_FILE_SIZE
from utils.google_drive import upload_file_to_drive, check_drive_connection, list_drive_files
from utils.auth import get_current_admin
from database.models import Admin

router = APIRouter()

@router.post("/buyer/{buyer_id}")
async def upload_buyer_doc(
    buyer_id: PydanticObjectId, 
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin)
):
    """Upload document for buyer - MongoDB ID version"""
    try:
        contents = await file.read()
        
        if len(contents) > MAX_FILE_SIZE:
            return JSONResponse(status_code=400, content={"error": "File too large (max 50MB)"})
        
        # Save to local drive (using string version of ID)
        folder = get_entity_folder("buyer", str(buyer_id))
        filepath = save_uploaded_file(folder, file.filename, contents)
        
        # Upload to Google Drive
        drive_result = upload_file_to_drive("buyer", str(buyer_id), filepath, file.filename)
        
        return {
            "status": "success",
            "message": "Document uploaded to local and Google Drive",
            "file_name": file.filename,
            "local_path": filepath,
            "file_size_kb": f"{len(contents)/1024:.2f}",
            "google_drive": drive_result
        }
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/manufacturer/{manufacturer_id}")
async def upload_manufacturer_doc(
    manufacturer_id: PydanticObjectId, 
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin)
):
    """Upload document for manufacturer - MongoDB ID version"""
    try:
        contents = await file.read()
        
        if len(contents) > MAX_FILE_SIZE:
            return JSONResponse(status_code=400, content={"error": "File too large (max 50MB)"})
        
        # Save to local drive
        folder = get_entity_folder("manufacturer", str(manufacturer_id))
        filepath = save_uploaded_file(folder, file.filename, contents)
        
        # Upload to Google Drive
        drive_result = upload_file_to_drive("manufacturer", str(manufacturer_id), filepath, file.filename)
        
        return {
            "status": "success",
            "message": "Document uploaded to local and Google Drive",
            "file_name": file.filename,
            "local_path": filepath,
            "file_size_kb": f"{len(contents)/1024:.2f}",
            "google_drive": drive_result
        }
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/direct")
async def upload_direct_doc(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin)
):
    """Upload document directly"""
    try:
        contents = await file.read()
        
        if len(contents) > MAX_FILE_SIZE:
            return JSONResponse(status_code=400, content={"error": "File too large (max 50MB)"})
        
        # Save to local drive
        folder = get_entity_folder("direct")
        filepath = save_uploaded_file(folder, file.filename, contents)
        
        # Upload to Google Drive
        drive_result = upload_file_to_drive("direct", None, filepath, file.filename)
        
        return {
            "status": "success",
            "message": "Document uploaded to local and Google Drive",
            "file_name": file.filename,
            "local_path": filepath,
            "file_size_kb": f"{len(contents)/1024:.2f}",
            "google_drive": drive_result
        }
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/google-drive/status")
async def get_google_drive_status(
    current_admin: Admin = Depends(get_current_admin)
):
    """Check Google Drive connection status"""
    return check_drive_connection()

@router.get("/google-drive/files/{entity_type}")
async def list_google_drive_files(
    entity_type: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """List files from Google Drive"""
    if entity_type not in ["buyer", "manufacturer", "direct"]:
        raise HTTPException(status_code=400, detail="Invalid entity_type")
    
    files = list_drive_files(entity_type)
    return {
        "status": "success",
        "entity_type": entity_type,
        "total_files": len(files),
        "files": files
    }