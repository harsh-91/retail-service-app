<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# ok just update my documentation first

Here’s a precise, updated summary of your Retail Management Platform documentation, integrating your current design and feature set:

# Retail Management Platform — Documentation (July 2025)

## 1. Architecture Overview

- **Microservice-based SaaS**—Independent services for User, Inventory, Sales (incl. GST/Udhaar), Payment, Notification, and Tenant management.
- **Strict multi-tenancy**—Every entity, API, and DB call is scoped by `tenant_id` for privacy and security.
- **DB-per-service pattern**—MongoDB instance per microservice, with unique compound indexes (e.g., `(tenant_id, sale_id)`).


## 2. Data Model

Full Pydantic data models for every business entity, including premium/freemium logic, inventory-per-user, per-tenant credit limits, and GST compliance. Examples:

```python
class Tenant(BaseModel):
    tenant_id: str
    name: str
    owner: str
    created_at: datetime
    contact_info: Optional[dict]
    settings: Optional[dict]  # Includes subscription_status, subscription_end_date, and allowed establishments
```

```python
class SaleCreate(BaseModel):
    tenant_id: str
    establishment_id: str
    item_id: str
    item_name: str
    quantity: int
    price_per_unit: float
    payment_method: Literal["CASH", "UPI", "CREDIT"]
    customer_id: Optional[str] = None
    is_udhaar: bool = False
    user: str
```

- **See full, updated data models in [Retail-Management-Platform-Complete-Data-Model.md][^1].**
- Every document includes a `tenant_id`, and relations such as `establishment_id` and `customer_id` are supported for advanced flows.


## 3. High Level \& Low Level Design

- **[High Level Design][^4]**:
    - All business and data flows—onboarding, inventory, sales, credit, payment, notification—are mapped in Mermaid diagrams and in a table of responsibilities.
    - Microservices interact via HTTP/REST and event/webhook flows as seen in `sequenceDiagram` and `flowchart`.
- **[Low Level Design][^3]: Service-by-service class, model, and schema definition; per-service directory layout; and example code for all data entities and workflows.**


## 4. Data Flow

```mermaid
sequenceDiagram
    participant Client as Mobile/Web App
    participant Gateway as API Gateway
    participant TenantSvc as Tenant Service
    participant UserSvc as User Service
    participant InvSvc as Inventory Service
    participant SalesSvc as Sales Service
    participant PaymentSvc as Payment Service
    participant NotifSvc as Notification Service
    participant Storage as PDF Storage

    Client->>Gateway: POST /tenants (onboarding)
    Gateway->>TenantSvc: Register
    Client->>Gateway: POST /register (user, tenant_id)
    Gateway->>UserSvc: Register
    Client->>Gateway: Add/adjust inventory
    Gateway->>InvSvc: CRUD
    Client->>Gateway: POST /sales?tenant_id=...
    Gateway->>SalesSvc: Log sale/credit
    SalesSvc->>InvSvc: Deduct stock/update
    SalesSvc->>PaymentSvc: Payment initiation/log
    SalesSvc->>NotifSvc: Notifications/WhatsApp
    ...
```

- **See full diagram and flow details in [Retail-Management-Platform-Data-Flow-Mermaid-Di.md][^2].**


## 5. Key Flows and Features

- **Premium/Freemium:**
    - Each tenant has a flag and `subscription_end_date` controlling access to features such as GST billing, analytics, cloud backup, and multi-device sync.
- **Udhaar/Credit:**
    - Multiple open udhaar sales per customer, enforced credit limit (configurable per business/customer).
- **Inventory Management:**
    - Item stock is managed at the user level; sales can be recorded even if inventory is not entered (pending deduction triggers warning).
- **UPI/Webhook Payments:**
    - UPI and credit payments use third-party providers with webhook/callback handling; manual override is supported.
- **Localization:**
    - All backend messages and errors are localized via a standard system; each user/tenant profile may set its own language.
- **Exports and Sharing:**
    - Sales and analytics exports as CSV/PDF via backend endpoints; WhatsApp/email file/link sharing supported (premium only).


## 6. Testing Guide

- **Test all business modules end-to-end** using Docker Compose/local test environments.
- **Layered test approach:** Unit tests (for models/rules), service/component tests (each microservice API), contract tests (API schemas), integration (multi-service flows), E2E (full business simulation: register→inventory→sale→pay→GST→share).
- **See full step-by-step instructions and sample test cases in [Test_Guide.md][^6].**


## 7. CI/CD, Security, and Handover

- **CI/CD pipelines** (per-service) trigger: lint, test, build, SCA, deploy.
- **Security:** JWT everywhere, tenant isolation via code \& data, secrets via vault.
- **Observability:** All API and DB logs tagged by tenant, correlation IDs, Grafana dashboards/Kibana suggested.
- **Handover docs**: All design and ops knowledge checked in; see [Multi-Service Architecture doc][^5] for ops handoff.

**For detailed business rules, model schemas, flow diagrams, and cross-service glue, always consult the latest design docs and test suite in `/docs` and `/tests`.**

- All design, data model, HLD/LLD, and testing references have been updated as of July 20, 2025.

[^1]: Retail-Management-Platform-Complete-Data-Model.md

[^2]: Retail-Management-Platform-Data-Flow-Mermaid-Di.md

[^3]: Retail-Management-Platform-Full-Low-Level-Design.md

[^4]: Retail-Management-Platform-High-Level-Design-HL.md

[^5]: Retail-Management-Platform-Multi-Service-Archite.md

[^6]: Test_Guide.md

<div style="text-align: center">⁂</div>

[^1]: Retail-Management-Platform-Complete-Data-Model.md

[^2]: Retail-Management-Platform-Data-Flow-Mermaid-Di.md

[^3]: Retail-Management-Platform-Full-Low-Level-Design.md

[^4]: Retail-Management-Platform-High-Level-Design-HL.md

[^5]: Retail-Management-Platform-Multi-Service-Archite.md

[^6]: Test_Guide.md

