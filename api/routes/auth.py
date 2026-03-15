from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from beanie import PydanticObjectId

from database.models import Admin, Buyer, Manufacturer, Task
from schemas.auth import (
    AdminLogin, 
    AdminResponse,
    AdminCreate,
    AdminUpdate,
    AdminListResponse,
    LogoutResponse
)
from utils.auth import (
    create_token, 
    get_current_admin, 
    get_current_superuser
)

router = APIRouter()

# ==========================================
#  AUTHENTICATION ROUTES
# ==========================================

@router.post("/login", response_model=AdminResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login endpoint - Returns JWT token and user info"""
    print(f"[AUTH] Login attempt: {form_data.username}")
    
    admin = await Admin.find_one(Admin.username == form_data.username)
    
    if not admin or admin.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    access_token = create_token(str(admin.id), admin.username, admin.role)
    
    return {
        "username": admin.username,
        "full_name": admin.full_name,
        "role": admin.role,
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful"
    }

@router.get("/me", response_model=AdminListResponse)
async def get_me(current_admin: Admin = Depends(get_current_admin)):
    """Get current admin info"""
    return current_admin

@router.get("/verify")
async def verify_token_endpoint(current_admin: Admin = Depends(get_current_admin)):
    """Verify endpoint for frontend compatibility"""
    return {
        "status": "valid",
        "username": current_admin.username,
        "full_name": current_admin.full_name,
        "role": current_admin.role
    }

@router.post("/logout", response_model=LogoutResponse)
async def logout(current_admin: Admin = Depends(get_current_admin)):
    """Logout endpoint"""
    return {"status": "success", "message": "Successfully logged out"}

# ==========================================
#  ADMIN MANAGEMENT (Superuser Only)
# ==========================================

@router.get("/admins", response_model=List[AdminListResponse])
async def list_admins(
    current_user: Admin = Depends(get_current_superuser)
):
    """List all admins (Superuser only)"""
    return await Admin.find_all().to_list()

@router.post("/admins", response_model=AdminListResponse, status_code=201)
async def create_new_admin(
    admin_data: AdminCreate,
    current_user: Admin = Depends(get_current_superuser)
):
    """Create a new admin (Superuser only)"""
    # Check if exists
    existing = await Admin.find_one(Admin.username == admin_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_admin = Admin(**admin_data.model_dump())
    await new_admin.insert()
    return new_admin

@router.put("/admins/{admin_id}", response_model=AdminListResponse)
async def update_admin_user(
    admin_id: PydanticObjectId,
    admin_update: AdminUpdate,
    current_user: Admin = Depends(get_current_superuser)
):
    """Update admin details or password (Superuser only)"""
    admin = await Admin.get(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    update_data = admin_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(admin, field, value)
    
    await admin.save()
    return admin

@router.delete("/admins/{admin_id}", status_code=204)
async def delete_admin_user(
    admin_id: PydanticObjectId,
    current_user: Admin = Depends(get_current_superuser)
):
    """Delete an admin user (Superuser only)"""
    if admin_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    admin = await Admin.get(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    await admin.delete()
    return None

# ==========================================
#  GLOBAL STATISTICS (Admin/Superuser)
# ==========================================

@router.get("/stats")
async def get_global_stats(
    current_user: Admin = Depends(get_current_admin)
):
    """Get high-level stats for the dashboard"""
    try:
        # Using find_all().count() which is more robust in some Beanie versions
        buyer_count = await Buyer.find_all().count()
        mfr_count = await Manufacturer.find_all().count()
        task_count = await Task.find_all().count()
        
        # Optional: status breakdown for tasks
        pending_tasks = await Task.find(Task.status == "pending").count()
        
        return {
            "total_buyers": buyer_count,
            "total_manufacturers": mfr_count,
            "total_tasks": task_count,
            "tasks_detail": {
                "total": task_count,
                "pending": pending_tasks
            }
        }
    except Exception as e:
        return {
            "total_buyers": 0,
            "total_manufacturers": 0,
            "total_tasks": 0,
            "error": str(e)
        }