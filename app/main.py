"""Application runner"""

from fastapi import FastAPI

from sqlalchemy import create_engine
from app.routers import postcodes

from app.core.config import config
from app.db.base import Base

from fastapi.middleware.cors import CORSMiddleware

origins = ["*",]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(postcodes.router)

# Create the database tables - Only needs to be done once then it can be commented out
Base.metadata.create_all(
    bind=create_engine(config.database.dsn, connect_args={"check_same_thread": False}),
)


@app.get("/")
async def root():
    return {"message": "Hello root!"}


@app.get("/get_coordinates")
async def read_item():
    return [
         {
            'geoCode': [48.86, 2.3522],
            'description': 'Marker 1'
        },
        {
            'geoCode': [48.85, 2.3522],
            'description': 'Marker 2'
        },
        {
            'geoCode': [48.855, 2.34],
            'description': 'Marker 3'
        }
]
