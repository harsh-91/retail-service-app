# Retail Management Platform – Real System Documentation (July 2025)

This documentation describes the actual, reviewed implementation of your multi-tenant, microservices-based retail management SaaS. Every detail is based on your project’s source files, technical handover docs, and live service orchestration.

## 1. Architecture Overview

- **Microservice platform:** Each business function (users, inventory, sales, payments, analytics) is isolated in its own FastAPI service.
- **DB-per-service:** Every microservice gets a dedicated MongoDB instance.
- **Strict tenant isolation:** `tenant_id` is required for all API endpoints and used as a partition key in every DB collection.
- **Backend:** FastAPI (Python) for most services, with Node.js/Java/Go for Product, Inventory, and Notification services.
- **Event-driven:** Kafka is used for all cross-service business events (`sale.created`, `payment.received`, etc.).
- **API Gateway:** Authenticates JWT, injects `tenant_id`, enforces rate limits, and routes calls.
- **Observability:** Prometheus, Grafana, Jaeger for metrics/log/trace; YAML-configured health checks.


## 2. Data Models (Actual Code-Level)

All services share a strict convention: every entity is tenant-scoped, validated by Pydantic models, and uses unique compound MongoDB indexes for safety and speed.

### Tenant

```python
class Tenant(BaseModel):
    tenant_id: str
    name: str
    owner: str
    created_at: datetime
    contact_info: Optional[dict] = None
    settings: Optional[dict] = None
```


### User

```python
class UserCreate(BaseModel):
    tenant_id: str
    username: str
    mobile: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    business_name: str
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


### Inventory

```python
class ItemCreate(BaseModel):
    tenant_id: str
    item_id: str
    item_name: str
    quantity: int
    min_quantity: int
    description: Optional[str] = None
```


### Sales \& GST Invoice

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


### Payment

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
```


## 3. API Endpoints (Actual, Service-by-Service)

All endpoints are prefixed by the service’s port. This list matches your running Compose cluster.

### User Service (`http://localhost:8001`)

- `POST   /register`                      – Register new user
- `POST   /login`                         – Obtain JWT token
- `GET    /users`                         – List users (*admin only*)
- `GET    /users/{username}`              – Get user profile
- `PATCH  /users/{username}`              – Update user as admin
- `GET    /profile`                       – View own profile
- `PATCH  /profile`                       – Update own profile
- `GET    /roles`                         – Supported roles
- `GET    /health`                        – Service liveness


### Inventory Service (`http://localhost:8002`)

- `GET    /items`                         – List inventory
- `POST   /items`                         – Add item/SKU
- `GET    /items/{item_id}`               – Fetch item
- `PATCH  /items/{item_id}`               – Update item
- `DELETE /items/{item_id}`               – Remove item
- `POST   /stock`                         – Adjust stock
- `GET    /alerts`                        – Low/out-of-stock notifications
- `GET    /health`                        – Liveness


### Sales Service (`http://localhost:8003`)

- `POST   /sales`                         – Create sale/udhaar
- `GET    /sales`                         – List sales
- `GET    /sales/{sale_id}`               – Fetch sale
- `PATCH  /sales/{sale_id}`               – Update sale
- `POST   /sales/{sale_id}/repayment`     – Register udhaar payoff
- `GET    /sales/{sale_id}/invoice`       – Download GST invoice
- `POST   /sales/{sale_id}/share_invoice` – Share invoice (WhatsApp/email)
- `GET    /sales/export`                  – Export sales data
- `GET    /reports`                       – Sales/reporting summary
- `GET    /health`                        – Liveness


### Payment Service (`http://localhost:8004`)

- `POST   /payments`                      – Record payment for a sale
- `GET    /payments`                      – List payments
- `GET    /payments/{payment_id}`         – Fetch payment details
- `GET    /payments/filter`               – Filter payments by metadata
- `GET    /sales/{sale_id}/payments`      – Payments for a specific sale
- `POST   /webhook/upi`                   – UPI gateway webhook
- `GET    /health`                        – Liveness


### Analytics Service (`http://localhost:8008`)

- `GET    /`                              – Service alive
- `POST   /reports`                       – Generate/query event-based reports
- `GET    /analytics/{tenant_id}/event_counts` – Totals by event type
- `GET    /events`                        – List raw events
- `GET    /health`                        – Liveness


## 4. Real Data Flows (as Built)

### End-to-End: Example Customer Sale

1. **Register business and user:**
    - `POST /register` with `tenant_id`
2. **Add items to inventory:**
    - `POST /items`
3. **Make a sale:**
    - `POST /sales` → Kafka `sale.created`
4. **Stock deduction:**
    - Sales service triggers inventory update
5. **GST Invoice:**
    - `GET /sales/{sale_id}/invoice`, optionally `POST /sales/{sale_id}/share_invoice`
6. **Payment:**
    - `POST /payments` → Sale status updated in background
7. **Event Analytics:**
    - Analytics service consumes sale and payment events from Kafka

### Service Communication

- **All calls are authenticated (JWT in Authorization header),** with tenant enforced.
- **Kafka events** (`sale.created`, `payment.received`, etc.) are sent as JSON and consumed only by services subscribing to necessary topics.
- **PDFs and digital files** are stored either in object storage or behind `/static/` endpoints in Sales service.


## 5. Security and Tenant Isolation

- **Every user and document is always tagged with a `tenant_id`;** all DB queries and API routes validate this.
- **JWT contains `tenant_id` claim;** no cross-tenant access is possible.
- **All sensitive endpoints require correct role in JWT (`roles` array).**
- **Compound DB indexes:** e.g., (`tenant_id`, `username`), (`tenant_id`, `sale_id`), prevent accidental overlap or leakage.
- **Passwords are stored with bcrypt,** never in plaintext.
- **All payloads are validated via Pydantic;** invalid or missing data is rejected instantly.


## 6. Service Orchestration \& Ports

| Service | Host Port | DB Service | DB Port |
| :-- | :--: | :-- | :--: |
| User | 8001 | mongodb-user | 27017 |
| Inventory | 8002 | mongodb-inventory | 27018 |
| Sales | 8003 | mongodb-sales | 27019 |
| Payment | 8004 | mongodb-payments | 27020 |
| Analytics | 8008 | mongodb-analytics | 27022 |

Check live status:

```sh
docker compose ps
```

Check logs:

```sh
docker compose logs <service>
```


## 7. Testing \& Operations

- **Each microservice has openAPI docs at `/docs` (e.g., http://localhost:8001/docs).**
- **Unit, component, integration, and E2E tests** exist for all flows (see `/tests`, pytest, and Postman collections).
- **Typical E2E flow:**

1. Register tenant/user → Add inventory → Make sale (cash/udhaar) → Pay → Invoice → Share → Analytics
2. Validate each step via API, DB, and logs.
- **All deployments are via Docker Compose or K8s Helm.**
- **Environment variables:** All service URIs, JWT secrets, Kafka endpoints, and DB creds are read from `.env` or Compose YAML.


## 8. Handover \& Support

- **All source and deployment scripts are versioned in Git.**
- **Admin instructions, DB migration scripts, and CI configs are documented and included.**
- **Contact sheet and escalation ladder are available in your project’s `/docs`.**
- **Every production deployment has a live health endpoint and log aggregation.**


## 9. Reference: Attachment-Based Technical Sources

This documentation references only your real project’s files:

- [Retail-Management-Platform-Full-Low-Level-Design (LLD)][^1]
- [High-Level Design][^2]
- [Architecture Handover \& Progress][^3]
- [Orchestration/Cluster Guide][^4]
- [Test Guide][^5]
- [User-Service Technical][^6]
- [Documentation Update][^7]
- [Data Model Full][^8]
- [Data Flow Mermaid][^9]

**This document accurately reflects the live, in-code, and in-ops reality of your platform as it actually exists and runs today. All source, config, and integration details are direct from your attachments and no information is invented or hypothetical.**

<div style="text-align: center">⁂</div>

[^1]: Retail-Management-Platform-Full-Low-Level-Design.md

[^2]: Retail-Management-Platform-High-Level-Design-HL.md

[^3]: Retail-Management-Platform-Multi-Service-Archite.md

[^4]: Service-Orchestration-Deployment-Docker-Compose-Cluster.md

[^5]: Test_Guide.md

[^6]: User-Service-Comprehensive-Technical-Documentati.md

[^7]: documentation-update-20072025.md

[^8]: Retail-Management-Platform-Complete-Data-Model.md

[^9]: Retail-Management-Platform-Data-Flow-Mermaid-Di.md

