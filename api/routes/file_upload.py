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
        drive_result = {"status": "skipped"}
        
        return {
            "status": "success",
            "file_name": file.filename,
            "file_url": f"/api/upload/file/buyer/{buyer_id}/{file.filename}"
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
            "file_name": file.filename,
            "file_url": f"/api/upload/file/manufacturer/{manufacturer_id}/{file.filename}"
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
            "file_name": file.filename,
            "file_url": f"/api/upload/file/direct/{file.filename}"
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

from fastapi.responses import FileResponse
import os

BASE_UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")


@router.get("/file/buyer/{buyer_id}/{filename}")
async def get_buyer_file(buyer_id: str, filename: str):
    file_path = os.path.join(
        BASE_UPLOAD_FOLDER,
        "buyers",
        f"buyer_{buyer_id}",
        filename
    )

    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})

    return FileResponse(file_path)


@router.get("/file/manufacturer/{manufacturer_id}/{filename}")
async def get_manufacturer_file(manufacturer_id: str, filename: str):
    file_path = os.path.join(
        BASE_UPLOAD_FOLDER,
        "manufacturers",
        f"manufacturer_{manufacturer_id}",
        filename
    )

    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})

    return FileResponse(file_path)


@router.get("/file/direct/{filename}")
async def get_direct_file(filename: str):
    file_path = os.path.join(
        BASE_UPLOAD_FOLDER,
        "direct",
        filename
    )

    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})

    return FileResponse(file_path)

@router.get("/list/{entity_type}")
async def list_files(entity_type: str):
    base = os.path.join(os.getcwd(), "uploads")

    folder_map = {
        "buyer": "buyers",
        "manufacturer": "manufacturers",
        "direct": "direct"
    }

    if entity_type not in folder_map:
        return {"files": []}

    folder_path = os.path.join(base, folder_map[entity_type])

    files_data = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            files_data.append({
                "name": file,
                "size": str(os.path.getsize(file_path)) + " bytes",
                "created_at": str(os.path.getctime(file_path)),
                "url": "/api/upload/file/" + file_path.split("uploads/")[1].replace("\\", "/")
            })

    return {"files": files_data}