from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import delete
from app.config import get_db
from app.models.user import User, UserRole
from app.security import get_current_user
from app.security import create_access_token
from app.models.token import BlacklistedToken
from app.schemas.user import UserCreate, UserResponse,UserLogin
from app.routes.ws import broadcast_to_admins,disconnect_user
from app .routes.ws import connected_clients

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,  
        role=user.role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    await broadcast_to_admins(f"New user registered: {new_user.email}")

    return new_user

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if db_user.is_blocked:
        raise HTTPException(status_code=403, detail="User is blocked")

    token = create_access_token({"sub": db_user.email, "role": db_user.role.value})

    return {"access_token": token, "token_type": "bearer", "role": db_user.role.value}

@router.delete("/all", status_code=200)
async def delete_all_users(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin can only delete all users")

    await db.execute(delete(User).where(User.role != UserRole.admin))
    await db.commit()
    return { "detail": "All non-admin users deleted successfully"}


@router.post("/block/{user_id}")
async def block_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(select(User).where(User.id == user_id))
    user_to_block = result.scalar_one_or_none()

    if not user_to_block:
        raise HTTPException(status_code=404, detail="User not found")

    user_to_block.is_blocked = True

    await db.commit()
    await disconnect_user(user_to_block.email)

    return {"message": "User blocked successfully"}

@router.post("/revoke-token", status_code=200)
async def revoke_token(token: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admin can revoke tokens")

    new_entry = BlacklistedToken(token=token)
    db.add(new_entry)
    await db.commit()

    to_remove = [c for c in connected_clients if c.get("token") == token]
    for c in to_remove:
        await c["ws"].close(code=1008)
        connected_clients.remove(c)

    return {"detail": "Token revoked successfully"}