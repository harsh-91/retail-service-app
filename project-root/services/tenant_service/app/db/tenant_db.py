from pymongo import MongoClient
from datetime import datetime

def get_tenant_collection():
    from os import getenv
    db_name = getenv("TENANT_DB_NAME", "tenant_service_db")
    mongo_uri = getenv("TENANT_MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    return client[db_name]["tenants"]

def add_tenant(data):
    col = get_tenant_collection()
    doc = data.dict()
    doc["created_at"] = datetime.utcnow().isoformat()
    col.insert_one(doc)

def get_tenant(tenant_id):
    col = get_tenant_collection()
    doc = col.find_one({"tenant_id": tenant_id})
    if doc:
        doc.pop("_id", None)
    return doc
