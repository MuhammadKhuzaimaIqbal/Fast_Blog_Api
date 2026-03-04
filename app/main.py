from fastapi import FastAPI
from app.routes import user
from app.config import engine, Base
from app.models import user as user_model 

app =  FastAPI()

app.include_router(user.router)

@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def get_root():
    return {"Hello" : "Khuzaima"}
    