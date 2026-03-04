from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import List
from app.security import decode_access_token

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Store connected clients with roles
connected_clients: List[dict] = []  # [{"ws": websocket, "role": "admin"}, ...]

async def broadcast_to_admins(message: str):
    """Send message only to admin clients"""
    for client in connected_clients:
        if client["role"] == "admin":
            await client["ws"].send_text(message)

@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    Connect with JWT token as query param: /ws/notifications?token=JWT_TOKEN
    """
    try:
        payload = decode_access_token(token)
        role = payload.get("role")
        if role not in ["user", "admin"]:
            await websocket.close(code=1008)  # policy violation
            return
    except HTTPException:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    connected_clients.append({"ws": websocket, "role": role})

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove({"ws": websocket, "role": role})