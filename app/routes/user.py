from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import delete
from app.config import get_db
from app.models.user import User, UserRole
from app.security import get_current_user
from app.security import create_access_token
from app.schemas.user import UserCreate, UserResponse,UserLogin

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
     # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,  
        role=user.role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    # Get user from DB by email
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    # Check credentials
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Automatically include role in response (user/admin)
    token = create_access_token({"sub": db_user.email, "role": db_user.role.value})

    return {"access_token": token, "token_type": "bearer", "role": db_user.role.value}

@router.delete("/all", status_code=200)
async def delete_all_users(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Check if the user is admin
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin can only delete all users")

    # Delete all users
    await db.execute(delete(User).where(User.role != UserRole.admin))
    await db.commit()
    return { "detail": "All non-admin users deleted successfully"}