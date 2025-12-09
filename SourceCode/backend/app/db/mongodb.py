import os
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    client: AsyncIOMotorClient = None

db = MongoDB()

async def get_database():
    return db.client.get_database("myapp_db")

async def connect_to_mongo():
    host = os.getenv("MONGODB_HOST", "192.168.0.36")
    port = os.getenv("MONGODB_PORT", "27017")
    user = os.getenv("MONGODB_USER", "root")
    password = os.getenv("MONGODB_PASSWORD", "pass123#")
    db_name = os.getenv("MONGODB_DB", "admin")
    
    # URL encode password if needed, but for now simple f-string
    import urllib.parse
    encoded_password = urllib.parse.quote_plus(password)
    
    mongo_url = f"mongodb://{user}:{encoded_password}@{host}:{port}/{db_name}"
    db.client = AsyncIOMotorClient(mongo_url)
    print("Connected to MongoDB")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")
