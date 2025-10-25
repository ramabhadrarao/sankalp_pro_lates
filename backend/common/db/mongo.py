from motor.motor_asyncio import AsyncIOMotorClient
from common.config import MONGO_URI, MONGO_DB

mongo_client = AsyncIOMotorClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]