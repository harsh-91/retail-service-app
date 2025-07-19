from pymongo import MongoClient, ASCENDING
from datetime import datetime
import os

MONGO_URI = os.getenv("INVENTORY_MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("INVENTORY_DB_NAME", "inventory_service_db")
COLL_NAME = "items"


def get_inventory_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLL_NAME]
    # Compound index: tenant_id + item_id unique per tenant
    collection.create_index([("tenant_id", ASCENDING), ("item_id", ASCENDING)], unique=True)
    return collection

def add_item(item):
    collection = get_inventory_collection()
    doc = item.dict()
    doc["last_updated"] = datetime.utcnow().isoformat()
    # enforce item_id uniqueness per tenant (compound index)
    collection.insert_one(doc)
    return doc["item_id"]

def get_item(tenant_id: str, item_id: str):
    collection = get_inventory_collection()
    doc = collection.find_one({"tenant_id": tenant_id, "item_id": item_id})
    if doc:
        doc.pop("_id", None)
    return doc

def get_all_items(tenant_id: str):
    collection = get_inventory_collection()
    result = collection.find({"tenant_id": tenant_id})
    return [{k: v for k, v in doc.items() if k != "_id"} for doc in result]

def update_item(tenant_id: str, item_id: str, item):
    collection = get_inventory_collection()
    update_data = {k: v for k, v in item.dict().items() if v is not None and k != "tenant_id"}
    if update_data:
        update_data["last_updated"] = datetime.utcnow().isoformat()
        collection.update_one({"tenant_id": tenant_id, "item_id": item_id}, {"$set": update_data})

def delete_item(tenant_id: str, item_id: str):
    collection = get_inventory_collection()
    collection.delete_one({"tenant_id": tenant_id, "item_id": item_id})

def adjust_stock(tenant_id: str, item_id: str, delta: int):
    collection = get_inventory_collection()
    item = collection.find_one({"tenant_id": tenant_id, "item_id": item_id})
    if not item:
        raise ValueError("Item not found")
    new_qty = item["quantity"] + delta
    if new_qty < 0:
        raise ValueError("Stock cannot go negative")
    collection.update_one(
        {"tenant_id": tenant_id, "item_id": item_id},
        {
            "$set": {
                "quantity": new_qty,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
    )

def get_low_stock_items(tenant_id: str):
    collection = get_inventory_collection()
    result = collection.find({
        "tenant_id": tenant_id,
        "$expr": {"$lte": ["$quantity", "$min_quantity"]}
    })
    return [{k: v for k, v in doc.items() if k != "_id"} for doc in result]
