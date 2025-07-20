# services/your_service/app/db/db.py

from pymongo import MongoClient
import os

def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("SERVICE_DB_NAME", "your_service_db")
    client = MongoClient(mongo_uri)
    return client[db_name]
