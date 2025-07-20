from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta, timezone

import os

MONGO_URI = os.getenv("SALES_MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("SALES_DB_NAME", "sales_service_db")
COLL_NAME = "sales"

def get_sales_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLL_NAME]
    # Compound index: tenant_id + sale_id (if you provide your own) or just use _id per doc
    collection.create_index([("tenant_id", ASCENDING), ("sale_id", ASCENDING)], unique=True, sparse=True)
    return collection

def add_sale(sale):
    """
    Expects a Pydantic SaleCreate model.
    Auto-calculates total_price, timestamps, and generates sale_id if not set.
    """
    collection = get_sales_collection()
    doc = sale.dict()
    doc["total_price"] = sale.quantity * sale.price_per_unit
    doc["timestamp"] = datetime.now(timezone.utc)
    # Generate a sale_id if not present (assign string from Mongo _id)
    result = collection.insert_one(doc)
    doc["sale_id"] = str(result.inserted_id)
    # Also add `sale_id` to the document for easier queries
    collection.update_one({"_id": result.inserted_id}, {"$set": {"sale_id": doc["sale_id"]}})
    doc.pop("_id", None)
    return doc

def get_sale(tenant_id: str, sale_id: str):
    collection = get_sales_collection()
    doc = collection.find_one({"tenant_id": tenant_id, "sale_id": sale_id})
    if doc:
        doc.pop("_id", None)
    return doc

def list_sales(tenant_id: str, user: str = None, limit: int = 100):
    collection = get_sales_collection()
    query = {"tenant_id": tenant_id}
    if user:
        query["user"] = user
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    return [{k: v for k, v in doc.items() if k != "_id"} for doc in cursor]

def mark_udhaar_paid(tenant_id: str, sale_id: str, amount_received: float, payment_method: str):
    """
    Mark an udhaar (credit) sale as paid/partially paid.
    """
    collection = get_sales_collection()
    ts = datetime.now(timezone.utc)
    result = collection.update_one(
        {"tenant_id": tenant_id, "sale_id": sale_id, "is_udhaar": True},
        {"$set": {
            "udhaar_paid": True,
            "udhaar_paid_on": ts,
            "payment_method": payment_method,
            "amount_received": amount_received,
        }}
    )
    return result.modified_count == 1

def attach_gst_invoice(tenant_id, sale_id, gst_invoice, pdf_url):
    """
    Attach GST invoice data and PDF link to sale record.
    """
    collection = get_sales_collection()
    collection.update_one(
        {"tenant_id": tenant_id, "sale_id": sale_id},
        {"$set": {
            "gst_invoice": gst_invoice,
            "invoice_pdf_url": pdf_url
        }}
    )

def record_invoice_share(tenant_id, sale_id, whatsapp):
    """
    Log invoice sharing event.
    """
    collection = get_sales_collection()
    collection.update_one(
        {"tenant_id": tenant_id, "sale_id": sale_id},
        {"$set": {"invoice_shared_on": {"whatsapp": whatsapp, "time": datetime.datetime.now(timezone.utc)}}}
    )

def get_sales_summary(tenant_id: str, from_date: datetime, to_date: datetime):
    """
    Returns a summary of sales, credit/udhaar, and collections for a date window.
    """
    collection = get_sales_collection()
    match = {
        "tenant_id": tenant_id,
        "timestamp": {"$gte": from_date.isoformat(), "$lte": to_date.isoformat()}
    }
    sales = list(collection.find(match))
    total_sales = sum(s.get("total_price", 0) for s in sales)
    total_udhaar = sum(s.get("total_price", 0) for s in sales if s.get("is_udhaar"))
    total_collections = sum(s.get("amount_received", 0) for s in sales if s.get("udhaar_paid"))
    return {
        "tenant_id": tenant_id,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "total_sales": total_sales,
        "total_udhaar": total_udhaar,
        "collections": total_collections,
        "sales_count": len(sales)
    }

def top_customers(tenant_id: str, limit: int = 5):
    """
    Returns top customers by total sales or udhaar.
    """
    collection = get_sales_collection()
    pipeline = [
        {"$match": {"tenant_id": tenant_id, "customer_id": {"$ne": None}}},
        {"$group": {"_id": "$customer_id", "total_sales": {"$sum": "$total_price"}}},
        {"$sort": {"total_sales": -1}},
        {"$limit": limit}
    ]
    return list(collection.aggregate(pipeline))

# --- Inventory helpers ---
def inventory_exists(tenant_id, establishment_id, item_id, user):
    # In production, check an inventory_service DB/collection
    # For demo: always allow sale (simulate found)
    return True

def get_available_stock(tenant_id, establishment_id, item_id, user):
    # In production: fetch stock value from inventory_service
    # Here, just return 5 as a demo
    return 5

def deduct_inventory(tenant_id, establishment_id, item_id, qty, user):
    # In prod: decrement inventory count for the item
    pass

_pending_inventory = []

def set_pending_inventory_deduction(tenant_id, establishment_id, item_id, qty, user):
    _pending_inventory.append({
        "tenant_id": tenant_id,
        "establishment_id": establishment_id,
        "item_id": item_id,
        "qty": qty,
        "user": user,
        "pending": True,
        "time": datetime.utcnow().isoformat()
    })

_customer_credit_limits = {}  # (tenant_id, establishment_id, customer_id) -> float

def get_customer_udhaar_total(tenant_id, establishment_id, customer_id):
    collection = get_sales_collection()
    match = {
        "tenant_id": tenant_id,
        "establishment_id": establishment_id,
        "customer_id": customer_id,
        "is_udhaar": True,
        "udhaar_paid": {"$ne": True}
    }
    sales = list(collection.find(match))
    return sum(s.get("total_price", 0) for s in sales)

def get_customer_credit_limit(tenant_id, establishment_id, customer_id):
    return _customer_credit_limits.get((tenant_id, establishment_id, customer_id), 1000.0)

def set_customer_credit_limit(tenant_id, establishment_id, customer_id, limit, user):
    _customer_credit_limits[(tenant_id, establishment_id, customer_id)] = limit
    return {"status": "ok", "new_limit": limit}

