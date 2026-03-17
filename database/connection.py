"""
MongoDB Connection and Beanie Initialization
"""

import os
import logging
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models import Admin, Buyer, Manufacturer, Task, CalendarEvent
from utils.mongodb_storage import init_gridfs

# Initialize logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/jhom_db")
DATABASE_NAME = "jhom_db"

async def init_db():
    """Initialize Beanie with the MongoDB client and models"""
    if not MONGODB_URL:
        logger.error("CRITICAL: MONGODB_URL environment variable is not set!")
        return False

    try:
        logger.info(f"Connecting to MongoDB: {DATABASE_NAME}...")
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Verify connection
        await client.admin.command('ping')
        
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
        
        # Initialize GridFS
        init_gridfs(client[DATABASE_NAME])
        
        logger.info(f"Successfully initialized Beanie and GridFS for database: {DATABASE_NAME}")
        return True
    except Exception as e:
        logger.error(f"FAILED to connect to MongoDB: {str(e)}")
        logger.info("TIP: Verify your MONGODB_URL and check if your IP is whitelisted in MongoDB Atlas.")
        return False

async def seed_admin():
    """Ensure admin1 exists as superuser"""
    try:
        logger.info("Seeding admin database...")
        # Avoid mass delete for now to diagnose potential issues
        # await Admin.find(Admin.username != "admin1").delete()
        
        logger.info("Looking for admin1...")
        admin1 = await Admin.find_one(Admin.username == "admin1")
        
        if not admin1:
            admin1 = Admin(
                username="admin1",
                password="admin123",  # In a real app, this should be hashed
                full_name="System Administrator",
                role="superuser",
                is_active=True
            )
            await admin1.insert()
            logger.info("Created default superuser: admin1")
        else:
            # Update role to superuser if it wasn't already
            admin1.role = "superuser"
            await admin1.save()
            logger.info("Verified admin1 as superuser")
    except Exception as e:
        logger.error(f"Error in seed_admin: {str(e)}")