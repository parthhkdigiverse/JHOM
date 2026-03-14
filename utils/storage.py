"""
File Storage Utilities - Local + Google Drive
"""

import os
import json
from datetime import datetime
from typing import List, Dict

# Import simple Google Drive functions
try:
    from utils.google_drive import (
        upload_json_to_drive, 
        upload_file_to_drive, 
        delete_file_from_drive
    )
    GOOGLE_DRIVE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Google Drive not available: {e}")
    GOOGLE_DRIVE_AVAILABLE = False

# Storage paths
BUYER_DRIVE = r"E:\Buyer"
MANUFACTURER_DRIVE = r"E:\manufacture"
DIRECT_DRIVE = r"E:\Direct"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Create directories
for path in [BUYER_DRIVE, MANUFACTURER_DRIVE, DIRECT_DRIVE]:
    os.makedirs(path, exist_ok=True)

def save_to_drive(folder: str, filename: str, data: dict) -> bool:
    """
    Save JSON data to local drive AND Google Drive
    """
    # Determine entity type
    entity_type = None
    if "Buyer" in folder:
        entity_type = "buyer"
    elif "manufacture" in folder:
        entity_type = "manufacturer"
    elif "Direct" in folder:
        entity_type = "direct"
    
    # Save to local drive
    local_saved = False
    try:
        file_path = os.path.join(folder, f"{filename}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved locally: {file_path}")
        local_saved = True
    
    except Exception as e:
        print(f"❌ Error saving locally: {e}")
    
    # Save to Google Drive (if available)
    if GOOGLE_DRIVE_AVAILABLE and entity_type and local_saved:
        try:
            result = upload_json_to_drive(entity_type, filename, data)
            if result.get("status") == "success":
                print(f"☁️ Saved to Google Drive: {filename}.json")
        except Exception as e:
            print(f"⚠️ Could not save to Google Drive: {e}")
    
    return local_saved

def update_drive_file(folder: str, filename: str, data: dict) -> bool:
    """Update existing JSON file on both local and Google Drive"""
    return save_to_drive(folder, filename, data)

def delete_from_drive(folder: str, filename: str) -> bool:
    """Delete file from both local drive and Google Drive"""
    
    # Determine entity type
    entity_type = None
    if "Buyer" in folder:
        entity_type = "buyer"
    elif "manufacture" in folder:
        entity_type = "manufacturer"
    elif "Direct" in folder:
        entity_type = "direct"
    
    # Delete from local
    local_deleted = False
    try:
        file_path = os.path.join(folder, f"{filename}.json")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Deleted locally: {file_path}")
            local_deleted = True
        else:
            print(f"⚠️ File not found locally: {file_path}")
    
    except Exception as e:
        print(f"❌ Error deleting locally: {e}")
    
    # Delete from Google Drive (if available)
    if GOOGLE_DRIVE_AVAILABLE and entity_type:
        try:
            delete_file_from_drive(entity_type, filename)
        except Exception as e:
            print(f"⚠️ Could not delete from Google Drive: {e}")
    
    return local_deleted

def get_all_files(folder: str) -> List[Dict]:
    """List all JSON files in folder"""
    try:
        files = []
        
        if not os.path.exists(folder):
            return files
        
        for filename in os.listdir(folder):
            if filename.endswith('.json'):
                file_path = os.path.join(folder, filename)
                file_size = os.path.getsize(file_path)
                created_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                files.append({
                    'name': filename,
                    'path': file_path,
                    'size': f"{file_size} bytes",
                    'created_at': created_time.isoformat()
                })
        
        return files
    
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return []

def save_uploaded_file(folder: str, filename: str, contents: bytes) -> str:
    """Save uploaded file to local drive"""
    file_path = os.path.join(folder, filename)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return file_path

def get_entity_folder(entity_type: str, entity_id: int = None) -> str:
    """Get folder path for entity"""
    if entity_type == "buyer":
        path = os.path.join(BUYER_DRIVE, f"buyer_{entity_id}")
    elif entity_type == "manufacturer":
        path = os.path.join(MANUFACTURER_DRIVE, f"manufacturer_{entity_id}")
    else:  # direct
        path = os.path.join(DIRECT_DRIVE, datetime.now().strftime("%Y-%m-%d"))
    
    os.makedirs(path, exist_ok=True)
    return path