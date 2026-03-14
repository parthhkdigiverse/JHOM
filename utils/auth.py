"""
Authentication Utilities - MongoDB Version
"""

import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from beanie import PydanticObjectId

from database.models import Admin

# Configuration
SECRET_KEY = "unified_secret_key_2026"
ALGORITHM = "HS256"

security = HTTPBearer()

def create_token(admin_id: str, username: str, role: str) -> str:
    """Create JWT token with role"""
    payload = {
        "admin_id": str(admin_id),
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Admin:
    """Get current authenticated admin from MongoDB"""
    token = credentials.credentials
    payload = verify_token(token)
    
    admin_id = payload.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=401, detail="Token missing admin ID")
        
    admin = await Admin.get(PydanticObjectId(admin_id))
    
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")
    
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin account is disabled")
        
    return admin

async def get_current_superuser(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """Check if current admin is a superuser"""
    if current_admin.role != "superuser":
        raise HTTPException(
            status_code=403, 
            detail="Superuser access required for this operation"
        )
    return current_admin