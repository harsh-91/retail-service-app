# Retail Management Platform

**A Modern, Multi-Tenant, GST-Ready SaaS to Power Retail in India**

## ✨ Features

- B2B multi-tenant: Each business (tenant) has totally private users, inventory, sales, payments, and notifications.
- Mobile-first, Indian-context business flows: Daily sales, udhaar/credit, UPI, GST, sharing on WhatsApp.
- Automated GST-compliant PDF invoices and cloud sharing.
- Modular Python microservices with MongoDB-per-service, enforced at the code/database level.
- Role-based auth (JWT), audit-ready, analytics and summary APIs.
- Simple, developer-friendly API, clean docs, and ready-to-use Swagger UI for every service.


## 📦 Structure

```
project-root/
  services/
    user_service/
    tenant_service/
    inventory_service/
    sales_service/
    payment_service/
    notification_service/
  shared/ (optional: for auth/utilities)
  README.md
  .env.example
```


## 🚦 Quickstart for Devs (Microservice Example)

```bash
# Enter the desired service folder
cd services/payment_service

# Install dependencies
pip install -r requirements.txt

# Set environment for service (example .env)
export SALES_MONGO_URI="mongodb://localhost:27017"
export SALES_DB_NAME="sales_service_db"
export SECRET_KEY="...."  # Same as used for JWT signing

# Launch service (ensure you're in correct folder!)
uvicorn app.main:app --reload

# Visit docs at:
http://localhost:8000/docs
```


## 🏗️ **System Diagram**

```mermaid
flowchart TD
  AppUser1 -- "API w/ JWT & tenant_id" --> Gateway
  Gateway -- to --> UserService
  Gateway -- to --> TenantService
  Gateway -- to --> InventoryService
  Gateway -- to --> SalesService
  Gateway -- to --> PaymentService
  Gateway -- to --> NotificationService
  SalesService-->|integrates|PaymentService
  SalesService-->|updates|InventoryService
  InventoryService -- |webhooks| NotificationService
  subgraph Each Service DB
    direction LR
    DB1[(MongoDB per service)]
  end
```


## 🎯 Business Flows Covered

| Flow | Done? | API/Service | Multi-Tenant | GST Ready | PDF or WhatsApp |
| :-- | :-- | :-- | :--: | :--: | :--: |
| Business registration | ✔️ | tenant_service | ✔️ | n/a | n/a |
| User registration/login | ✔️ | user_service | ✔️ | n/a | n/a |
| Inventory tracking | ✔️ | inventory_service | ✔️ | n/a | n/a |
| Daily sale \& udhaar | ✔️ | sales_service | ✔️ | ✔️ | via PDF |
| Payment (UPI, Cash) | ✔️ | payment_service | ✔️ | n/a | n/a |
| GST invoice/pdf | ✔️ | sales_service (GST APIs) | ✔️ | ✔️ | ✔️ |
| WhatsApp invoice share | ✔️ | notification_service/sales | ✔️ | ✔️ | ✔️ |
| Analytics \& summary | ✔️ | sales_service (summary API) | ✔️ | ✔️ | via API |

## 🚩 How Does Multi-Tenancy Work?

**Every API call and every DB record contains a `tenant_id`.**

- No cross-business data leakage is possible.
- All unique constraints are `(tenant_id, resource_id)` for every major entity.
- User JWTs encode the tenant context.


## 🚀 Key Endpoints (Per-Service, Example)

### User

| Endpoint | Verb | Purpose |
| :-- | :-- | :-- |
| `/register` | POST | Register user for a business |
| `/login` | POST | JWT login (with tenant_id) |
| `/profile` | GET | Get/update profile |

### Sales/Order

| Endpoint | Verb | Purpose |
| :-- | :-- | :-- |
| `/sales` | POST | Log sale, payment, udhaar |
| `/sales` | GET | List sales |
| `/sales/summary/daily` | GET | Get daily summary |
| `/sales/{sale_id}/gst_invoice` | POST | Generate invoice, create PDF |
| `/sales/{sale_id}/share_invoice` | POST | Send invoice on WhatsApp |

### Payment

| `/payments`                         | POST/GET    | Record/list payments           |
| `/payments/{id}`                    | GET         | Get payment status             |
| `/payments/{id}/status`             | PATCH       | Mark payment as received       |
| `/payments/summary`                 | GET         | Collection/analytics summary   |

### Inventory

| `/items`                            | POST/GET    | Create/list item, per tenant   |
| `/items/{item_id}`                  | GET/PUT     | View/update item               |
| `/items/alerts/low-stock`           | GET         | Get low-stock alerts           |

> For full details, see `/docs` on each microservice.

## 📄 GST Invoice Sample

- PDF auto-generated for each B2B sale with GST fields (number/date/parties/items/HSN/taxes/total).
- Shareable as a public/private URL or attached to a WhatsApp message with a single call.


## 🛡️ Security

- JWT authentication, every request validated.
- Every user/session scoped to a business (`tenant_id`)
- MongoDB compound indexes: (`tenant_id`, `resource_id`) everywhere.


## 🧪 Testing

- All services expose Swagger/OpenAPI at `/docs`
- Unauthenticated or wrong-tenant data returns 401/403/404
- Easily test API flows in Swagger or with curl (samples above)


## 🧑‍💻 Contributing

1. Clone the repo
2. Pick a service and `cd` into its folder
3. Make your changes and test them locally
4. Ensure all endpoints still require `tenant_id`
5. Open a PR describing the business flow enabled or fixed

## 🚨 Common Issues \& Solutions

- **404 Not Found:** Service/router not loaded, or calling wrong URL/method. Double-check `/docs`!
- **Not authenticated:** Missing or invalid Bearer token; login or create new user and paste JWT.
- **Database not shown in Compass:** No data yet—insert a record, it will appear.
- **GST PDF not generated:** Check `app/templates/gst_invoice.html` exists and WeasyPrint is installed.


## 📝 FAQ

**How do I add a new business (tenant)?**
POST to `/tenants` → save `tenant_id` → use it in all subsequent API calls

**How do I ensure sales and payments are not visible outside a business?**
Each API and DB call filters data by the supplied or JWT-embedded `tenant_id`.

**How do I test GST invoices?**
POST a sale, then POST to `/sales/{sale_id}/gst_invoice`; download PDF or share on WhatsApp.

## 🤝 Contact / Support

- [Product Owner] R. Kapoor (`@rkapoor`)
- [Lead Backend] P. Mercado (`@pmercado`)
- [DevOps/Deployment] A. Singh (`@asingh`)


## 💡 More Docs

- See each service’s `/docs` endpoint for live OpenAPI
- For full architecture and onboarding: `Retail-Management-Platform-Multi-Service-Archite.md`
- For GST, see [GST India Government Portal](https://www.gst.gov.in/)

**Happy hacking, team 🚀 — you’re building something retailers will love.**

