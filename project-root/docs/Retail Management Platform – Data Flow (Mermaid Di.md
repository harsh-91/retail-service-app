<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Retail Management Platform – Data Flow (Mermaid Diagram)

Below is a comprehensive data flow for your multi-tenant retail platform, showing how requests and data traverse the system, how microservices interact, and where persistence and notifications occur. This diagram assumes a modern flow—covering onboarding, inventory, sales, GST invoicing, payments, and notifications.

## 1. End-to-End Data Flow Overview

```mermaid
sequenceDiagram
    participant Client as Mobile/Web App (User/Owner)
    participant Gateway as API Gateway
    participant TenantSvc as Tenant Service
    participant UserSvc as User Service
    participant InvSvc as Inventory Service
    participant SalesSvc as Sales Service
    participant PaymentSvc as Payment Service
    participant NotifSvc as Notification Service
    participant Storage as Object/PDF Storage

    %% 1. Business Onboarding/Registration
    Client->>Gateway: POST /tenants (new business)
    Gateway->>TenantSvc: Register tenant (creates tenant_id)
    TenantSvc-->>Gateway: tenant_id issued
    Gateway-->>Client: tenant_id sent

    %% 2. User Registration & Login
    Client->>Gateway: POST /register (user, tenant_id)
    Gateway->>UserSvc: Register user (with tenant_id)
    UserSvc-->>Gateway: JWT (with tenant_id)
    Gateway-->>Client: JWT sent

    %% 3. Inventory Operations (Add/Adjust Stock)
    Client->>Gateway: GET/POST /items?tenant_id=...
    Gateway->>InvSvc: Inventory CRUD by tenant_id
    InvSvc-->>Gateway: Inventory data/ack
    Gateway-->>Client: Inventory update/alert

    %% 4. Sales Entry (Sale/Udhaar)
    Client->>Gateway: POST /sales?tenant_id=...
    Gateway->>SalesSvc: Log sale/credit with tenant_id
    SalesSvc->>InvSvc: PATCH /items/{item_id}/stock (deduct stock)
    InvSvc-->>SalesSvc: Stock updated
    SalesSvc-->>Gateway: Sale confirmation (sale_id)
    Gateway-->>Client: sale_id

    %% 5. GST Invoice Generation
    Client->>Gateway: POST /sales/{sale_id}/gst_invoice?tenant_id=...
    Gateway->>SalesSvc: Generate GST invoice
    SalesSvc->>Storage: Render & save PDF
    Storage-->>SalesSvc: PDF URL
    SalesSvc->>SalesSvc: Attach GST invoice, PDF url to sale
    SalesSvc-->>Gateway: Invoice info, PDF link
    Gateway-->>Client: Invoice metadata/PDF url

    %% 6. Payment
    Client->>Gateway: POST /payments?tenant_id=...
    Gateway->>PaymentSvc: Log payment (for sale_id, tenant_id)
    PaymentSvc-->>Gateway: Payment confirmation
    Gateway-->>Client: Payment status

    %% 7. WhatsApp/Notification
    Client->>Gateway: POST /sales/{sale_id}/share_invoice
    Gateway->>NotifSvc: Share invoice (WhatsApp/SMS)
    NotifSvc->>Storage: Fetch PDF url
    NotifSvc->>External: Send WhatsApp/message
    NotifSvc-->>Gateway: Share confirmation
    Gateway-->>Client: Share status/update
```


## 2. Key Flow Summary

- **All API calls** must include `tenant_id` (from body, query, or JWT).
- **Each microservice** only sees and acts on its own tenant-scoped MongoDB database.
- **Integration points** occur for sale-to-inventory, sale-to-payment, and notification triggers.
- **PDF \& WhatsApp flows** are handled via sales service (PDF generation) and notification service (sending), with files stored in object storage or a static files server.
- **Audit and analytics** derive from these flows for summaries, compliance, and dashboarding.

This data flow ensures strict multi-tenancy, robust compliance, easy extensibility, and a clear developer/onboarding experience for your entire retail management SaaS.

