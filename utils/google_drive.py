"""
Google Drive Integration - OAuth (Your Personal Drive)
Complete Working Solution - No Storage Issues
"""

import os
import io
import pickle
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError

# ==================== CONFIGURATION ====================

OAUTH_CREDENTIALS_FILE = "oauth_credentials.json"
TOKEN_FILE = "token.pickle"

# ✅ Update with YOUR folder IDs from YOUR Google Drive
GOOGLE_DRIVE_FOLDERS = {
    "buyer": "1lWT7dvoGoKbafQxDRvJMlYEUNWrZlMWt",
    "manufacturer": "1BgQwBD5wxgfGGYSE8e6Hoo1k7OnrKeH7",
    "direct": "1ES1JEZ97EGq21Qnf6_Cg_znxudwErdYi"
}

SCOPES = ['https://www.googleapis.com/auth/drive']

# ==================== AUTHENTICATION ====================

def get_drive_service():
    """Get authenticated Google Drive service"""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(OAUTH_CREDENTIALS_FILE):
                print(f"❌ {OAUTH_CREDENTIALS_FILE} not found!")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(OAUTH_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

# ==================== UPLOAD JSON ====================

def upload_json_to_drive(entity_type: str, filename: str, data: dict) -> dict:
    """Upload JSON to Google Drive"""
    try:
        service = get_drive_service()
        if not service:
            return {"status": "error", "message": "Authentication failed"}
        
        folder_id = GOOGLE_DRIVE_FOLDERS.get(entity_type)
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        
        file_metadata = {'name': f"{filename}.json", 'parents': [folder_id]}
        media = MediaIoBaseUpload(io.BytesIO(json_content.encode('utf-8')), mimetype='application/json')
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        return {
            "status": "success",
            "file_id": file.get('id'),
            "file_name": f"{filename}.json",
            "web_link": file.get('webViewLink')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==================== UPLOAD FILE ====================

def upload_file_to_drive(entity_type: str, entity_id: int, file_path: str, file_name: str) -> dict:
    """Upload file to Google Drive"""
    try:
        service = get_drive_service()
        if not service:
            return {"status": "error", "message": "Authentication failed"}
        
        folder_id = GOOGLE_DRIVE_FOLDERS.get(entity_type)
        
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(file_path, mimetype=mime_type)
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        print(f"✅ Uploaded to Drive: {file.get('webViewLink')}")
        
        return {
            "status": "success",
            "file_id": file.get('id'),
            "file_name": file_name,
            "web_link": file.get('webViewLink')
        }
    except Exception as e:
        print(f"❌ Drive upload error: {e}")
        return {"status": "error", "message": str(e)}

# ==================== DELETE FILE ====================

def delete_file_from_drive(file_id: str) -> dict:
    """Delete file from Google Drive"""
    try:
        service = get_drive_service()
        if not service:
            return {"status": "error", "message": "Authentication failed"}
        
        service.files().delete(fileId=file_id).execute()
        return {"status": "success", "message": "Deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==================== LIST FILES ====================

def list_drive_files(entity_type: str) -> list:
    """List files in folder"""
    try:
        service = get_drive_service()
        if not service:
            return []
        
        folder_id = GOOGLE_DRIVE_FOLDERS.get(entity_type)
        query = f"'{folder_id}' in parents and trashed=false"
        
        results = service.files().list(
            q=query,
            fields='files(id, name, webViewLink, size, createdTime)',
            orderBy='createdTime desc'
        ).execute()
        
        return results.get('files', [])
    except Exception as e:
        print(f"❌ List error: {e}")
        return []

# ==================== CHECK CONNECTION ====================

def check_drive_connection() -> dict:
    """Check Google Drive connection"""
    try:
        if not os.path.exists(OAUTH_CREDENTIALS_FILE):
            return {
                "status": "error",
                "message": f"Place {OAUTH_CREDENTIALS_FILE} in project folder",
                "credentials_found": False
            }
        
        service = get_drive_service()
        if not service:
            return {"status": "error", "message": "Authentication failed"}
        
        about = service.about().get(fields="user, storageQuota").execute()
        user = about.get('user', {}).get('emailAddress', 'Unknown')
        quota = about.get('storageQuota', {})
        
        used_gb = int(quota.get('usage', 0)) / (1024**3)
        total_gb = int(quota.get('limit', 0)) / (1024**3)
        
        folder_status = {}
        for entity_type, folder_id in GOOGLE_DRIVE_FOLDERS.items():
            try:
                folder = service.files().get(fileId=folder_id, fields='name').execute()
                folder_status[entity_type] = f"✅ {folder.get('name')}"
            except:
                folder_status[entity_type] = "❌ Not found"
        
        return {
            "status": "success",
            "message": "Connected to YOUR Google Drive ✅",
            "user": user,
            "storage_used_gb": round(used_gb, 2),
            "storage_total_gb": round(total_gb, 2),
            "folders": folder_status
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==================== FIRST RUN ====================

if __name__ == "__main__":
    print("="*70)
    print("🔐 GOOGLE DRIVE AUTHENTICATION")
    print("="*70)
    print("\nThis will open browser for Google login...")
    input("Press ENTER to continue...")
    
    result = check_drive_connection()
    
    print("\n" + "="*70)
    if result['status'] == 'success':
        print("✅ SUCCESS!")
        print(f"   User: {result['user']}")
        print(f"   Storage: {result['storage_used_gb']}GB / {result['storage_total_gb']}GB")
        print("\n   Folders:")
        for entity, status in result['folders'].items():
            print(f"   {entity}: {status}")
    else:
        print("❌ FAILED")
        print(f"   {result['message']}")
    print("="*70)