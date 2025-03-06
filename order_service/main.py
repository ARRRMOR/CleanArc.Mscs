from fastapi import FastAPI
from redis_manager import connect_to_redis, close_redis
from database import engine, Base
from routers import router


app = FastAPI()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await connect_to_redis()
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()

app.include_router(router)