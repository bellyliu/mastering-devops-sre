from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import get_settings
import redis

settings = get_settings()

# MongoDB Connection
mongodb_client: AsyncIOMotorClient = None

# Redis Connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def connect_to_mongo():
    """Connect to MongoDB"""
    global mongodb_client
    mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Import models
    from .models import User, Book
    
    # Initialize beanie with the Product document class
    await init_beanie(
        database=mongodb_client[settings.DATABASE_NAME],
        document_models=[User, Book]
    )
    print("Connected to MongoDB")


async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("Closed MongoDB connection")


def get_redis():
    """Dependency for getting Redis client"""
    return redis_client
