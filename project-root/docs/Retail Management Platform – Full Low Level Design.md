# Retail Management Platform – Full Low Level Design (LLD)

This Low Level Design enables any engineer to understand, maintain, and extend the entire Retail Management Platform. All services are independent Python FastAPI microservices, connected only via APIs, with MongoDB-per-service and strict multi-tenancy throughout. Every class, DB schema, and endpoint is crafted to meet Indian retail needs, including GST, UPI, udhaar, inventory, payments, and digital sharing.

## 1. Core Design Principles

- **Microservices:** Independent, DB-per-service, Python FastAPI.
- **Multi-Tenancy:** Every entity, model, endpoint, and DB call uses `tenant_id` to enforce complete data isolation.
- **Security:** JWT authentication everywhere, with JWT containing `tenant_id`.
- **SaaS Extension:** All business flows (sales, GST, payments, notifications) are tenant-scoped and B2B ready.
- **Compliance:** Explicit support for Indian GST invoicing, udhaar, digital receipts, and WhatsApp/email integration.


## 2. Service-by-Service Class \& Model Design

### A. Tenant Service

#### **Tenant**

```python
class Tenant(BaseModel):
    tenant_id: str
    name: str
    owner: str
    created_at: datetime
    contact_info: Optional[dict]
    settings: Optional[dict]
```

**Role:** Registers new businesses. All other data (users, inventory, sales) is always tied by `tenant_id`.

### B. User Service

#### **UserCreate \& UserOut**

```python
class UserCreate(BaseModel):
    tenant_id: str
    username: str
    mobile: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    business_name: str
    device_model: Optional[str] = None
    device_type: Optional[str] = None

class UserOut(BaseModel):
    tenant_id: str
    username: str
    mobile: str
    business_name: str
    roles: List[str]
    # ...other fields, excluding password
```

**Role:** Allows mobile-first, multi-device user onboarding per business. `tenant_id` binds each user to a business, preventing cross-business login or data leaks.

### C. Inventory Service

#### **ItemCreate \& ItemOut**

```python
class ItemCreate(BaseModel):
    tenant_id: str
    item_id: str
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

**Role:** Tracks all SKUs, quantities, and triggers low-stock business logic, always by tenant, enabling individualized inventory management.

### D. Sales (Order) Service

#### **SaleCreate, SaleOut, GST Models**

```python
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
    gst_invoice: Optional[dict] = None
    invoice_pdf_url: Optional[str] = None
```

**Role:** Logs every sale, links it to a tenant, allows udhaar (credit), and is the anchor for GST invoice generation and sharing.

#### **GSTInvoice, GSTParty, GSTInvoiceItem**

```python
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
```

**Role:** Encapsulates GST compliance, tracks item-wise tax values, and supports digital compliance and audit.

### E. Payment Service

#### **PaymentCreate \& PaymentOut**

```python
class PaymentCreate(BaseModel):
    tenant_id: str
    sale_id: str
    user: str
    amount: condecimal(gt=0)
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

**Role:** Ensures all payments/receipts are mapped to both the tenant and sale, supporting UPI, cash, credit, reconciliation, and reporting.

### F. Notification Service

#### **NotificationCreate**

```python
class NotificationCreate(BaseModel):
    tenant_id: str
    message_type: str
    recipient: str
    data: dict
    sent_at: Optional[datetime] = None
```

**Role:** Coordinates WhatsApp, SMS, and email notifications per tenant for sales, payments, udhaar reminders, and GST invoices.

## 3. Key DB and API Patterns

- **Compound indexes:**
Each collection is indexed by `tenant_id` plus the resource ID (`sale_id`, `item_id`, `payment_id`, etc.) to guarantee uniqueness and query speed within each business, never allowing overlap or leakage.
- **API security:**
All endpoints require JWT auth. Tenant_id is provided via the token or as an explicit query param.
- **Document structure:**
Every document in MongoDB for every service contains the `tenant_id` as a top-level field.


## 4. End-to-End Functional Mapping

| Requirement | Class(es)/Endpoint(s) | How Requirement is Fulfilleed |
| :-- | :-- | :-- |
| Multi-tenant isolation | Every `*Create`, `*Out`, and DB doc | tenant_id always required, validated on every API and DB operation |
| GST invoice compliance | GSTInvoice, SaleOut, PDF generator | Structured data + logic for number/date/parties/tax export/sharing |
| Daily sales \& credits | SaleCreate, SaleOut, mark_udhaar_paid | Model guarantees proper sale/credit/audit info per business |
| Inventory tracking | ItemCreate, ItemOut, alerts | Per-tenant, supports low-stock and accurate SKU accounting |
| Payments/collections | PaymentCreate, PaymentOut, summaries | Each payment always linked to sale and tenant for clear audit trail |
| WhatsApp/PDF sharing | SaleInvoiceShareRequest, NotificationCreate | Logic for sending receipts or GST invoices to customer on demand |
| Analytics/Summaries | SaleOut, get_sales_summary, PaymentSummaryOut | All endpoints are tenant-filtered, supporting trend analysis |

## 5. Modular Service Structure

```
services/
├── user_service/
│   └── app/
├── tenant_service/
│   └── app/
├── inventory_service/
│   └── app/
├── sales_service/
│   └── app/
├── payment_service/
│   └── app/
├── notification_service/
│   └── app/
└── shared/   # (optional: for shared code)
```

Each `app/` subfolder contains: `api/`, `db/`, `models/`, `core/`, `utils/`, `templates/` as needed.

## 6. Design Justification

- **Each domain has clear, validated models, strictly tenant-aware, and mapped 1:1 to MongoDB documents.**
- **APIs are RESTful, stateless, and designed for simple but strict mobile and web app integration.**
- **All compliance needs (GST, audit trail, digital share/download) are core to the data model, not bolted on.**
- **Loose coupling between services ensures each one is independently testable, scalable, and maintainable.**
- **All flows—sale, credit, payment, summary, GST, notification—are extensible, secure, and map tightly to Indian business and regulatory reality.**


## 7. Example Sequence: Sale → GST Invoice → WhatsApp

1. **Sale Entry:**
    - User (with tenant_id) makes POST `/sales`.
    - Item/quantity/cost/udhaar stored per-tenant.
2. **Request GST Invoice:**
    - POST `/sales/{sale_id}/gst_invoice` (with supplier/customer GSTParty info).
    - System generates structured GSTInvoice, creates PDF, updates sale record (attaches PDF URL).
3. **Share on WhatsApp:**
    - POST `/sales/{sale_id}/share_invoice` (with recipient number).
    - System triggers WhatsApp API to deliver PDF or link, logs result in sale DB for audit.

## 8. Helping New Developers

- **Swagger UI** for every service at `/docs`, with sample payloads.
- **Models are type-safe and validated at API layer; you can't put invalid data in.**
- **Security, multi-tenancy, and compliance are not optional—always required by the models and enforced in every code path.**
- **Starter scripts, sample cURL, and PDF templates all included in repo.**

**Any developer, intern or SRE can build, extend, test, or audit the system – just follow the above entity designs, always respect the tenant_id, and use the API contract for every operation.**

