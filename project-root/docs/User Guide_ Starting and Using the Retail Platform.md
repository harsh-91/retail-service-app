# User Guide: Starting and Using the Retail Platform Backend (No Frontend Needed)

This guide will help you start your backend microservices using Docker Compose and interact with all APIs from your terminal or Postman even if you have no frontend UI.

## 1. **Starting the Backend**

### **Step 1: Prerequisites**

- **Docker and Docker Compose** installed and working.
- Project source code is present locally, with your `docker-compose.yml` in the root.


### **Step 2: Start All Services**

From your project root in terminal:

```sh
docker compose up --build
```

- This command builds and runs all backend services: users, inventory, sales, payments, analytics, MongoDBs, Kafka, and Zookeeper.
- Wait until all services display `INFO: ... Application startup complete.` and/or show as "Up" in:

```sh
docker compose ps
```

**Tip:**
Each service will be available on a unique port:


| Service | Port |
| :-- | :-- |
| user | 8001 |
| inventory | 8002 |
| sales | 8003 |
| payment | 8004 |
| analytics | 8008 |

## 2. **Using the Backend Without a Frontend**

You can send requests via:

- **Postman** GUI (recommended)
- **cURL** or any terminal HTTP client
- **HTTPie** (for simple CLI HTTP requests)


### **A. Register a Tenant and User**

#### **1. Register a User**

**Endpoint:** `POST http://localhost:8001/register`
**Example JSON:**

```json
{
  "tenant_id": "tenant1",
  "username": "alice",
  "mobile": "9876543210",
  "business_name": "DemoMart",
  "password": "Secret123!",
  "email": "alice@example.com"
}
```

**Instruction:**

- In Postman, select POST.
- Set URL to the endpoint.
- Choose "raw" JSON body; paste the example payload.
- Send. You should get `{ "msg": "User registered" }` or similar.


#### **2. Log In**

**Endpoint:** `POST http://localhost:8001/login`
**Body:**

```json
{
  "username": "alice",
  "password": "Secret123!"
}
```

**Response:**

- Should return a JWT token. Copy this token for all further API calls.


### **B. Add Data and Operate (API-by-API)**

**Remember:**
For all endpoints (except `/register`, `/login`, `/health`), you must set the `Authorization` header:

```
Authorization: Bearer <the-token-you-got-from-login>
```


#### **Inventory Example**

- **Add Item:**
`POST http://localhost:8002/items`

```json
{
  "tenant_id": "tenant1",
  "item_id": "item123",
  "item_name": "iPhone 14",
  "quantity": 10,
  "min_quantity": 2
}
```

- **List Items:**
`GET http://localhost:8002/items`
(Set the Authorization header.)


#### **Sales Example**

- **Create a Sale:**
`POST http://localhost:8003/sales`

```json
{
  "tenant_id": "tenant1",
  "item_id": "item123",
  "item_name": "iPhone 14",
  "quantity": 1,
  "price_per_unit": 74999,
  "payment_method": "CASH",
  "user": "alice"
}
```

- **See Your Sales:**
`GET http://localhost:8003/sales`


#### **Payments Example**

- **Record Payment:**
`POST http://localhost:8004/payments`

```json
{
  "tenant_id": "tenant1",
  "sale_id": "<sale_id-from-sale-response>",
  "user": "alice",
  "amount": 74999,
  "method": "CASH"
}
```


#### **Analytics Example**

- **Get Report:**
`POST http://localhost:8008/reports`

```json
{
  "tenant_id": "tenant1",
  "report_type": "sales",
  "period_start": "2025-07-01T00:00:00Z",
  "period_end": "2025-07-21T23:59:59Z"
}
```

- **Get Event Counts:**
`GET http://localhost:8008/analytics/tenant1/event_counts`


## 3. **How to Explore and Validate Everything**

- Visit e.g. `http://localhost:8001/docs`, `.../8002/docs`, etc.
You’ll see Swagger/OpenAPI documentation for every endpoint.
- Run healthchecks with:

```
curl http://localhost:8001/health
curl http://localhost:8002/health
...
```

- Use Postman to automate test flows: register, login, create item, create sale, record payment, view analytics.


## 4. **Troubleshooting**

- **Service not starting?**
    - Check logs: `docker compose logs <service>`
- **Unauthorized?**
    - Ensure your JWT is attached as `Bearer <token>` in the header.
- **Mongo/Kafka errors?**
    - Check `docker compose ps` to ensure infra is up (`mongodb-user`, `kafka`, etc.).
    - Restart stuck containers if needed.


## 5. **Quick Summary Table**

| Action | Endpoint | Method | Notes |
| :-- | :-- | :-- | :-- |
| Register user | `/register` (8001) | POST | Needs tenant_id, username, mobile, password |
| Login | `/login` (8001) | POST | Returns JWT |
| Add item | `/items` (8002) | POST | Needs Authorization header with JWT |
| Create sale | `/sales` (8003) | POST | Needs Authorization, references tenant_id/user/item |
| Record payment | `/payments` (8004) | POST | Link to sale_id |
| Fetch analytics report | `/reports` (8008) | POST | Time-bounded; filter by tenant_id |

## 6. **Best Practices for CLI/API Use**

- Always handle tenant_id when POSTing data.
- Use strong, unique passwords during registration.
- Store the JWT token securely for session-based flows.
- Leverage `/health` and `/docs` endpoints for quick checks and API exploration.

**With this guide, you can fully operate, test, and demo your backend microservices using only the API—no frontend UI needed.** If you need advanced use cases (batch imports, custom reports, multi-tenant role scenarios), these APIs support such workflows as well.

