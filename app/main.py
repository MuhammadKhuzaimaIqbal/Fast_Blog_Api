from fastapi import FastAPI
from app.routes import user,ws
from app.config import engine, Base
from app.models import user as user_model 

app =  FastAPI()

app.include_router(user.router)
app.include_router(ws.router)

@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def get_root():
    return {"message": "Welcome to FastAPI with WebSockets!"}
    