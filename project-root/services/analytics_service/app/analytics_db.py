from motor.motor_asyncio import AsyncIOMotorClient
import os

# You can move this to a config file/environment variable in production
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URI)
db = client['analytics_db']
