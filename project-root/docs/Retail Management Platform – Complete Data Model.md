<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Retail Management Platform – Complete Data Model

## 1. Tenant (Business) Model

```python
class Tenant(BaseModel):
    tenant_id: str         # Unique business identifier
    name: str              # Business name
    owner: str             # User ID of the owner/admin
    created_at: datetime
    contact_info: Optional[dict] = None  # Email/phone/address
    settings: Optional[dict] = None      # Plan, language, preferences
```

- **Purpose:** Registers a business (“tenant”). Every other record is linked to a tenant via `tenant_id`.


## 2. User Model

```python
class UserCreate(BaseModel):
    tenant_id: str
    username: str
    mobile: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    business_name: str                 # Store or shop name
    device_model: Optional[str] = None
    device_type: Optional[str] = None

class UserOut(BaseModel):
    tenant_id: str
    username: str
    mobile: str
    business_name: str
    roles: list[str]
    language_pref: Optional[str] = None
    device_model: Optional[str] = None
    device_type: Optional[str] = None
```

- **Role:** Authenticates users to the platform, enforces per-tenant visibility.


## 3. Inventory Model

```python
class ItemCreate(BaseModel):
    tenant_id: str
    item_id: str                       # SKU or product code
    item_name: str
    quantity: int
    min_quantity: int
    description: Optional[str] = None

class ItemOut(BaseModel):
    tenant_id: str
    item_id: str
    item_name: str
    quantity: int
    min_quantity: int
    description: Optional[str] = None
    last_updated: Optional[str] = None
```

- **Role:** Tracks all items/SKUs for each business, manages stock and low-stock alerts.


## 4. Sales (Order) and GST Invoicing Models

```python
from typing import List, Optional, Literal

class GSTParty(BaseModel):
    name: str
    gstin: str
    address: str

class GSTInvoiceItem(BaseModel):
    item_id: str
    name: str
    qty: int
    rate: float
    value: float
    gst_rate: float
    gst_value: float

class GSTInvoice(BaseModel):
    invoice_number: str
    date: str
    supplier: GSTParty
    customer: GSTParty
    items: List[GSTInvoiceItem]
    total: float
    gst_total: float

class SaleCreate(BaseModel):
    tenant_id: str
    item_id: str
    item_name: str
    quantity: int
    price_per_unit: float
    payment_method: Literal["CASH", "UPI", "CREDIT"]
    customer_id: Optional[str] = None
    is_udhaar: bool = False
    user: str

class SaleOut(BaseModel):
    tenant_id: str
    sale_id: str
    item_id: str
    item_name: str
    quantity: int
    price_per_unit: float
    total_price: float
    payment_method: str
    customer_id: Optional[str] = None
    is_udhaar: bool = False
    udhaar_paid: Optional[bool] = False
    udhaar_paid_on: Optional[datetime] = None
    amount_received: Optional[float] = None
    user: str
    timestamp: datetime
    gst_invoice: Optional[GSTInvoice] = None
    invoice_pdf_url: Optional[str] = None
```

- **Role:** Logs every sale, credit/udhaar, payment type, and customer. GST invoice is attached as an embedded document.


## 5. Payment Model

```python
class PaymentCreate(BaseModel):
    tenant_id: str
    sale_id: str
    user: str
    amount: float
    method: Literal["CASH", "UPI", "CREDIT"]
    upi_vpa: Optional[str] = None
    status: Literal["PENDING", "RECEIVED", "FAILED"] = "PENDING"
    created_at: Optional[datetime] = None

class PaymentOut(BaseModel):
    tenant_id: str
    payment_id: str
    sale_id: str
    user: str
    amount: float
    method: str
    upi_vpa: Optional[str]
    status: Literal["PENDING", "RECEIVED", "FAILED"]
    created_at: datetime
    received_at: Optional[datetime] = None
    note: Optional[str] = None
```

- **Role:** Manages all transaction receipts, payment status, and reconciliation; always mapped to a sale and tenant.


## 6. Notification Model

```python
class NotificationCreate(BaseModel):
    tenant_id: str
    message_type: str                   # "LOW_STOCK", "PAYMENT_REMINDER", etc.
    recipient: str                      # mobile/email/WhatsApp
    data: dict                          # payload for the message
    sent_at: Optional[datetime] = None
```

- **Role:** Records and triggers all business event notifications, reminders, and digital GST/WhatsApp shares.


## 7. Cross-Service Key Patterns

- Every record **has `tenant_id`** (always required): guarantees strict data isolation for each tenant/business.
- All unique indexes in MongoDB are compound: **(tenant_id, resource_id)** (e.g., (tenant_id, item_id) for inventory).
- Data models are designed for **rapid API validation** via Pydantic, making misuse nearly impossible.


## 8. Example MongoDB Document

```json
{
  "tenant_id": "nair_traders_001",
  "sale_id": "SL20250719-001",
  "item_id": "parleg100g",
  "item_name": "Parle-G 100g",
  "quantity": 10,
  "total_price": 200,
  "payment_method": "UPI",
  "customer_id": "c004",
  "is_udhaar": false,
  "user": "priya",
  "timestamp": "2025-07-19T11:21:00Z",
  "gst_invoice": {
    "invoice_number": "INV/2025/021",
    "date": "2025-07-19",
    "supplier": { ... },
    "customer": { ... },
    "items": [ ... ],
    "total": 210.0,
    "gst_total": 10.0
  },
  "invoice_pdf_url": "https://cloud/INV/2025/021.pdf"
}
```


## 9. Data Model Justification Summary

- **Tenant-aware:** All data is isolated per business (`tenant_id`).
- **Regulatory compliance:** GST invoice structure meets Indian e-invoicing \& tax rules.
- **Scalable:** Each service’s models and collections can be extended for analytics, notifications, new payment types or regulatory updates, without breaking other tenants.
- **API- and UI-ready:** Models are directly used in request/response validation, ensuring seamless integration with frontend/mobile/Web APIs.

**This data model will support your core requirements: robust multi-tenant retail, full GST compliance, up-to-date payments and inventory, notification flows, and mobile integration. Any new team member can extend or use the system safely and confidently.**

