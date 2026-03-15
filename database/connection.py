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
    if not MONGODB_URL:
        print("❌ CRITICAL: MONGODB_URL environment variable is not set!")
        return False

    try:
        print(f"📡 Connecting to MongoDB: {DATABASE_NAME}...")
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
        print(f"✅ Successfully initialized Beanie for database: {DATABASE_NAME}")
        return True
    except Exception as e:
        print(f"❌ FAILED to connect to MongoDB: {str(e)}")
        print("💡 TIP: Verify your MONGODB_URL and check if your IP is whitelisted in MongoDB Atlas.")
        return False

async def seed_admin():
    """Ensure admin1 exists as superuser and remove other default users"""
    # 1. Remove other default users if they exist
    # (e.g., user1, or any other user that shouldn't be there by default)
    # We only want admin1 to remain as the primary entry point
    await Admin.find(Admin.username != "admin1").delete()
    
    # 2. Ensure admin1 exists
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
        print("👤 Created default superuser: admin1")
    else:
        # Update role to superuser if it wasn't already
        admin1.role = "superuser"
        await admin1.save()
        print("👤 Verified admin1 as superuser")