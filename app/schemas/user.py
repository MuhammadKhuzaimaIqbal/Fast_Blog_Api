from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole  # import your enum here

class UserCreate(BaseModel):
    name: Optional[str] 
    email: EmailStr     # validates email format
    password: str
    role: Optional[UserRole] = UserRole.user  # optional in request, defaults to user


class UserResponse(BaseModel):
    id : int
    name: Optional[str]
    email: EmailStr
    role: UserRole

class Config:
        orm_mode = True  # allows SQLAlchemy model objects to be converted automatically