"""
MongoDB Connection and Beanie Initialization
"""

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models import Admin, Buyer, Manufacturer, Task, CalendarEvent

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/jhom_db")
DATABASE_NAME = "jhom_db"

async def init_db():
    """Initialize Beanie with the MongoDB client and models"""
    client = AsyncIOMotorClient(MONGODB_URL)
    
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[
            Admin,
            Buyer,
            Manufacturer,
            Task,
            CalendarEvent
        ]
    )
    print(f"✅ Connected to MongoDB: {DATABASE_NAME}")