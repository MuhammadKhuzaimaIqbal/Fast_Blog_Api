from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Keep track of connected clients
connected_admins = []  # only admin clients will be here

async def broadcast_to_admins(message: str):
    """Send message only to admin clients"""
    for client, role in connected_admins:
        if role == "admin":
            await client.send_text(message)

@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    Clients must provide JWT token as a query parameter:
    ws://127.0.0.1:8000/ws/notifications?token=ACCESS_TOKEN_HERE
    """
    # Decode token to get role
    from app.security import decode_access_token  

    try:
        payload = decode_access_token(token)
        role = payload.get("role")
    except:
        await websocket.close(code=1008)  # policy violation
        return

    # Only allow admins to connect
    if role != "admin":
        await websocket.close(code=1008)
        return

    await websocket.accept()
    connected_admins.append((websocket, role))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_admins.remove((websocket, role))