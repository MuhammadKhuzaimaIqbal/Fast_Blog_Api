from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import List
from app.security import decode_access_token

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import get_db
from app.models.user import User
from fastapi import Depends

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Store connected clients with roles
connected_clients: List[dict] = []  # [{"ws": websocket, "role": "admin"}, ...]

async def broadcast_to_admins(message: str):
    """Send message only to admin clients"""
    for client in connected_clients:
        if client["role"] == "admin":
            await client["ws"].send_text(message)

async def disconnect_user(email: str):
    for client in connected_clients:
        if client["email"] == email:
            await client["ws"].close()

@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...),db: AsyncSession= Depends(get_db)
):
    """
    Connect with JWT token as query param: /ws/notifications?token=JWT_TOKEN
    """
    try:
        payload = decode_access_token(token)
        role = payload.get("role")
        email= payload.get("sub")
        if role not in ["user", "admin"]:
            await websocket.close(code=1008)  # policy violation
            return
        
         # 🔹 Check user in database
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            await websocket.close(code=1008)
            return

        # 🔹 Check if blocked
        if user.is_blocked:
            await websocket.close(code=1008)
            return

    except HTTPException:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    connected_clients.append({"ws": websocket, "role": role,"email":email})

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        for client in connected_clients:
            if client["ws"] == websocket:
                connected_clients.remove(client)
                break