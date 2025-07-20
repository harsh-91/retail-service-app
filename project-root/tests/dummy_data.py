import requests
import random
from faker import Faker
from datetime import datetime, timedelta

API_BASE = "http://localhost:8001"  # Change port/service as needed

fake = Faker()
Faker.seed(42)
random.seed(42)

NUM_TENANTS = 10
USERS_PER_TENANT = (3, 5)
ITEMS_PER_TENANT = (10, 15)
SALES_PER_TENANT = (20, 30)

ROLES = [["admin"], ["manager"], ["staff"], ["manager", "staff"]]
PAYMENT_METHODS = ["CASH", "UPI", "CREDIT"]

def create_tenant(idx):
    return {
        "tenant_id": f"tenant{idx+1:02d}",
        "business_name": fake.company(),
        "owner_name": fake.name(),
        "gst_number": fake.bothify(text="##AAAA####A1Z1"),
        "address": fake.address(),
        "email": fake.company_email(),
        "phone": fake.phone_number()
    }

def create_user(tenant_id, role):
    uname = fake.user_name()
    return {
        "tenant_id": tenant_id,
        "username": uname,
        "password": "Test@1234",
        "mobile": fake.msisdn(),
        "email": fake.email(),
        "business_name": fake.company(),
        "full_name": fake.name(),
        "language_pref": random.choice(["en", "hi"]),
        "device_model": fake.word() + random.choice(["A2", "Note", "Pro"]),
        "device_type": random.choice(["Android", "iOS"]),
        "roles": role,
    }

def create_item(tenant_id):
    return {
        "tenant_id": tenant_id,
        "item_id": fake.unique.bothify(text="sku-####"),
        "item_name": fake.word() + " " + fake.color_name(),
        "quantity": random.randint(50, 200),
        "price_per_unit": round(random.uniform(25, 350), 2)
    }

def create_sale(tenant_id, user, item):
    qty = random.randint(1, min(item["quantity"], 10))
    total_price = round(qty * item["price_per_unit"], 2)
    is_udhaar = random.random() < 0.2
    sale_time = fake.date_time_between(start_date="-120d", end_date="now")
    return {
        "tenant_id": tenant_id,
        "establishment_id": tenant_id + "-main",
        "item_id": item["item_id"],
        "item_name": item["item_name"],
        "quantity": qty,
        "price_per_unit": item["price_per_unit"],
        "payment_method": random.choice(PAYMENT_METHODS),
        "customer_id": "c" + fake.unique.bothify(text="###"),
        "is_udhaar": is_udhaar,
        "user": user["username"],
        "timestamp": sale_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_price": total_price
    }

def create_payment(tenant_id, sale):
    paid = random.random() < 0.85  # Most sales are paid
    method = random.choice([m for m in PAYMENT_METHODS if m != "CREDIT" or sale["is_udhaar"]])
    received_on = datetime.strptime(sale["timestamp"], "%Y-%m-%dT%H:%M:%S") + timedelta(days=random.randint(0, 7))
    return {
        "tenant_id": tenant_id,
        "sale_id": fake.uuid4(),
        "amount_received": sale["total_price"] if paid else 0,
        "payment_method": method,
        "received_on": received_on.strftime("%Y-%m-%dT%H:%M:%S")
    }

def post(url, data):
    resp = requests.post(url, json=data)
    if resp.status_code not in (200, 201):
        print(f"[ERROR {resp.status_code}] POST {url} : {resp.text}")
    return resp.json()

for t in range(NUM_TENANTS):
    tenant = create_tenant(t)
    print(f"\n=== Creating Tenant: {tenant['tenant_id']} ({tenant['business_name']}) ===")
    
    # Users
    num_users = random.randint(*USERS_PER_TENANT)
    users = []
    for i in range(num_users):
        role = ROLES[i % len(ROLES)]
        user = create_user(tenant["tenant_id"], role)
        users.append(user)
        # post(f"{API_BASE}/register", user)  # Uncomment to insert via API

    # Inventory
    num_items = random.randint(*ITEMS_PER_TENANT)
    items = [create_item(tenant["tenant_id"]) for _ in range(num_items)]
    # for item in items:
    #     post(f"{API_BASE}/items", item)  # Adjust as per your inventory endpoint

    # Sales and Payments
    for _ in range(random.randint(*SALES_PER_TENANT)):
        user = random.choice(users)
        item = random.choice(items)
        sale = create_sale(tenant["tenant_id"], user, item)
        # post(f"{API_BASE}/sales", sale)  # Adjust endpoint
        payment = create_payment(tenant["tenant_id"], sale)
        # post(f"{API_BASE}/sales/{sale['sale_id']}/receive_payment", payment)  # Adjust endpoint

    print(f"Inserted: {num_users} users, {num_items} items, sales+payments for tenant {tenant['tenant_id']}")

print("\n[INFO] Dummy data generation done! Uncomment API post() calls as needed for your environment.")
