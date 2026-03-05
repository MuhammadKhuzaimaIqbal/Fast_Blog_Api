from pydantic import BaseModel, EmailStr,ConfigDict
from typing import Optional
from app.models.user import UserRole  

class UserCreate(BaseModel):
    name: Optional[str] 
    email: EmailStr     
    password: str
    role: Optional[UserRole] = UserRole.user  

class UserResponse(BaseModel):
    id : int
    name: Optional[str]
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str