from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(
        os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    )
    mongodb.database = mongodb.client[os.getenv("DATABASE_NAME", "webtoon_gallery")]
    print("Connected to MongoDB")

async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("Disconnected from MongoDB")

def get_database():
    return mongodb.database