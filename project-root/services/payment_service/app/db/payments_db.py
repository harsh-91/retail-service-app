from pymongo import MongoClient, ASCENDING
from datetime import datetime
import os

MONGO_URI = os.getenv("PAYMENTS_MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("PAYMENTS_DB_NAME", "payment_service_db")
COLL_NAME = "payments"

def get_payments_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLL_NAME]
    # Each payment is unique per business and payment (multi-tenant)
    collection.create_index([("tenant_id", ASCENDING), ("payment_id", ASCENDING)], unique=True, sparse=True)
    return collection

def create_payment(payment):
    """
    Expects a PaymentCreate (Pydantic) model.
    """
    collection = get_payments_collection()
    doc = payment.dict()
    doc["status"] = doc.get("status", "PENDING")
    doc["created_at"] = (doc.get("created_at") or datetime.utcnow()).isoformat()
    # Generate payment_id as Mongo _id string
    result = collection.insert_one(doc)
    doc["payment_id"] = str(result.inserted_id)
    collection.update_one({"_id": result.inserted_id}, {"$set": {"payment_id": doc["payment_id"]}})
    doc.pop("_id", None)
    return doc

def get_payment(tenant_id: str, payment_id: str):
    collection = get_payments_collection()
    doc = collection.find_one({"tenant_id": tenant_id, "payment_id": payment_id})
    if doc:
        doc.pop("_id", None)
    return doc

def list_payments(tenant_id: str, user: str = None):
    collection = get_payments_collection()
    query = {"tenant_id": tenant_id}
    if user:
        query["user"] = user
    result = collection.find(query).sort("created_at", -1)
    return [{k: v for k, v in doc.items() if k != "_id"} for doc in result]

def update_payment_status(tenant_id: str, payment_id: str, status: str, received_at: datetime = None, note: str = None):
    collection = get_payments_collection()
    update_fields = {"status": status}
    if received_at:
        update_fields["received_at"] = received_at.isoformat()
    if note:
        update_fields["note"] = note
    result = collection.update_one(
        {"tenant_id": tenant_id, "payment_id": payment_id},
        {"$set": update_fields}
    )
    return result.modified_count == 1

def payment_summary(tenant_id: str, from_date: datetime, to_date: datetime):
    """
    Returns summary for the given date window.
    """
    collection = get_payments_collection()
    cursor = collection.find({
        "tenant_id": tenant_id,
        "created_at": {"$gte": from_date.isoformat(), "$lte": to_date.isoformat()}
    })
    payments = list(cursor)
    total_collections = sum(float(i.get("amount", 0)) for i in payments if i.get("status") == "RECEIVED")
    upi_count = sum(1 for i in payments if i.get("method") == "UPI")
    cash_count = sum(1 for i in payments if i.get("method") == "CASH")
    failed_count = sum(1 for i in payments if i.get("status") == "FAILED")
    from app.models.payment import PaymentOut
    return {
        "tenant_id": tenant_id,
        "from_date": from_date,
        "to_date": to_date,
        "total_collections": total_collections,
        "upi_count": upi_count,
        "cash_count": cash_count,
        "failed_count": failed_count,
        "payments": [PaymentOut(**{k: v for k, v in doc.items() if k != "_id"}) for doc in payments]
    }
