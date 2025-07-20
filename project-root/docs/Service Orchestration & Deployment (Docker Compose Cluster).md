<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# update documentation

Certainly! Here’s an updated **Docker/Service Orchestration Documentation** section, tailored for your current production architecture and clearly reflecting your observed deployment.

# **Service Orchestration \& Deployment (Docker Compose Cluster)**

## **Service Overview**

Your project consists of the following microservices and supporting MongoDB storage, orchestrated using Docker Compose:


| **Service Name** | **Purpose** | **Exposed Ports** | **Dependent DB** |
| :-- | :-- | :-- | :-- |
| user_service | User registration, login, profile, RBAC | 8001/tcp | mongodb-user |
| sales_service | Sales entry, billing, order, and udhaar management | 8003/tcp | mongodb-sales |
| inventory_service | Item/SKU CRUD, stock tracking, inventory alerts | 8002/tcp | mongodb-inventory |
| payment_service | Payment capture, UPI/cash/credit, and receipts | 8004/tcp | mongodb-payments |
| mongodb-user | Dedicated DB for user_service | 27017/tcp (internal) | - |
| mongodb-sales | Dedicated DB for sales_service | 27019/tcp (internal) | - |
| mongodb-inventory | Dedicated DB for inventory_service | 27018/tcp (internal) | - |
| mongodb-payments | Dedicated DB for payment_service | 27020/tcp (internal) | - |

## **Service Naming (as seen in Docker Compose \& ps)**

All containers are automatically prefixed with your project directory for uniqueness:

```
project-root-user_service-1
project-root-sales_service-1
project-root-inventory_service-1
project-root-payment_service-1
project-root-mongodb-user-1
project-root-mongodb-sales-1
project-root-mongodb-inventory-1
project-root-mongodb-payments-1
```


## **Port Map (Host → Container)**

- **user_service:**        `8001` → `8000/tcp`
- **inventory_service:**   `8002` → `8000/tcp`
- **sales_service:**       `8003` → `8000/tcp`
- **payment_service:**     `8004` → `8000/tcp`
- **mongodb-user:**        `27017` → `27017/tcp`
- **mongodb-inventory:**   `27018` → `27017/tcp`
- **mongodb-sales:**       `27019` → `27017/tcp`
- **mongodb-payments:**    `27020` → `27017/tcp`


## **How to List and Inspect Services**

**List all defined services:**

```sh
docker compose config --services
```

**List running services with status and ports:**

```sh
docker compose ps
```

**List all containers (if needed):**

```sh
docker ps -a
```


## **How to Access APIs**

- Base URLs (on your host machine by default):
    - **http://localhost:8001**  → user_service
    - **http://localhost:8002**  → inventory_service
    - **http://localhost:8003**  → sales_service
    - **http://localhost:8004**  → payment_service


## **Best Practices**

- **Each business domain service has its own MongoDB instance (DB-per-service).**
- **All data is tenant-isolated, with strict enforcement at API and DB layer.**
- **Admin/services communicate via HTTP APIs, with JWT-based authentication and tenant-aware middleware.**
- **MongoDB ports (`27017` and up) should be firewalled or accessible only internally for security.**


## **Known Warnings**

> Docker Compose v2+ no longer requires the `version` key in the YAML file.
> Remove the `version` attribute to suppress this warning:

```
the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
```


## **Logs, Health Checks, and Maintenance**

- Check logs for a service:

```
docker compose logs user_service
```

- Restart a service:

```
docker compose restart payment_service
```

- Monitor health/restarts with

```
docker compose ps
```


**This documentation section reflects your observed running cluster, clear port mapping, data isolation, and operational best practices for a modern microservices stack.**
You can copy this directly into your README, deployment guide, or team runbook.

