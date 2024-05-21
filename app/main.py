"""Application runner"""

from fastapi import FastAPI

from sqlalchemy import create_engine
from app.routers import postcodes

from app.core.config import config
from app.db.base import Base


app = FastAPI()
app.include_router(postcodes.router)

# Create the database tables - Only needs to be done once then it can be commented out
Base.metadata.create_all(
    bind=create_engine(config.database.dsn, connect_args={"check_same_thread": False}),
)


@app.get("/")
async def root():
    return {"message": "Hello root!"}
