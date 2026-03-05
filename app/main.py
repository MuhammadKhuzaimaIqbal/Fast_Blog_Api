from fastapi import FastAPI
from app.routes import user,ws
from app.config import engine, Base,get_db
from app.models import user as user_model 
import asyncio

app =  FastAPI()

app.include_router(user.router)
app.include_router(ws.router)

@app.on_event("startup")
async def create_tables_and_start_monitor():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async for db in get_db():
        asyncio.create_task(ws.monitor_revoked_tokens(db))
        break 
        
@app.get("/")
def get_root():
    return {"message": "Welcome to FastAPI with WebSockets!"}
    