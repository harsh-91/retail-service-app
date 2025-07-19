from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["user_service_db"]  # Name your DB per microservice

def get_users_collection():
    return db["users"]
