from pydantic import BaseModel, EmailStr, BeforeValidator, Field
from typing import Optional, Annotated
from beanie import PydanticObjectId

# Custom type for robust ObjectID serialization
PyObjectId = Annotated[str, BeforeValidator(str)]

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User/Admin schemas
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: Optional[PydanticObjectId] = None
    disabled: Optional[bool] = False
    role: Optional[str] = "user"

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class AdminBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = "admin"

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class Admin(AdminBase):
    id: PyObjectId
    is_active: bool


    class Config:
        from_attributes = True

# Login schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: Optional[str] = "user"

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    username: str
    role: str
    message: Optional[str] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"

class AdminListResponse(AdminBase):
    id: PyObjectId
    is_active: bool
    password: Optional[str] = None  # Included as per user requirement

    class Config:
        from_attributes = True

# Logout schema
class LogoutResponse(BaseModel):
    status: str
    message: str