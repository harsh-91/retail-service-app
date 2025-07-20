# Retail Management Platform – Multi-Service Architecture

*Comprehensive Handover \& Progress Report (July 2025)*

The Retail Management Platform now contains six independent, container-ready micro-services. Each service owns its own MongoDB database (Database-per-Service pattern) and communicates through REST or event topics. Extensive unit/integration tests and a basic CI pipeline are in place. This document consolidates design details, current completion status and next-step guidance for every service, followed by global architecture, operations, security and deployment notes required for a seamless hand-off.

## 1  Overall Architecture

### 1.1  High-Level Topology

| Layer | Components | Notes |
| :-- | :-- | :-- |
| Edge | NGINX Ingress (public)  ➜  Kong API Gateway | Central TLS termination, rate-limit, JWT verification [^1][^2] |
| Service Mesh | Istio (mTLS, retry, circuit breaker) | Zero-trust east-west traffic [^3][^4] |
| Core Micro-services | User, Product, Inventory, Order, Payment, Notification | Each containerised, owns separate MongoDB collection set |
| Data \& Messaging | MongoDB 8.0, Kafka (orders, payments, email topics) | Polyglot persistence possible later [^5][^6] |
| CI/CD | GitHub Actions ➜ Docker Hub ➜ GitOps Flux to AKS/EKS | Branch-specific pipelines per repo [^7] |
| Observability | Prometheus, Grafana, Loki central logs, Jaeger tracing | Correlation-ID injected at gateway [^8][^9] |

### 1.2  Progress Snapshot (July 2025)

| Service | Core APIs | Auth | DB Indexes | Unit Tests | Integration Tests | Status |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| User | Register, Login, JWT, Profile, Role Mgmt, List + Pagination | ✔ | username, email unique | 95% | Postman collection ✔ | **PROD-ready** |
| Product | CRUD, Category, Image upload stub | Gatekeeper token | sku unique | 90% | Stubbed | **Beta** |
| Inventory | Stock-in/-out, threshold alert | Gatekeeper token | sku, warehouse | 80% | Pending event tests | **Alpha** |
| Order | Create, Cancel, Query, CQRS write/read split | Gatekeeper token | orderId, userId | 75% | Kafka saga tests 60% | **Alpha** |
| Payment | Stripe webhook, async capture, refund | Gatekeeper token + HMAC | txnId, orderId | 70% | Awaiting sandbox test | **Alpha** |
| Notification | Email, SMS adapters, templating | Internal token | msgId | 60% | Unit email ✓, SMS todo | **PoC** |

## 2  Service-by-Service Low-Level Design

### 2.1  User Service (FastAPI + MongoDB)

*Completed \& running in production*

- **Endpoints**: `/register`, `/login`, `/profile`, `/change-password`, `/users` (admin paginated list).
- **Security**: BCrypt 12-round hash, HS256 JWT (60 min exp), role-array field, admin guard.
- **Data**: `users` collection; indexes on `username` and `email` unique [^10].
- **CI/CD**: Push triggers lint-test-build-publish to `retail/user-service:latest`.
- **Ops Runbook**: Reset-password, lock-account, rotate-secret instructions.
- **Open Items**: none – service frozen except for bug-fixes.


### 2.2  Product Service (Node.js NestJS)

- **Endpoints**: `/products`, `/products/{id}`, `/categories`.
- **Schema**: `products` (sku, name, price, categoryIds, pictures[]).
- **Validation**: class-validator pipe, JSON-Schema published.
- **Current gaps**: image upload path uses local disk; switch to S3 bucket before GA.
- **Next steps**

1. Add public search filter \& pagination.
2. Harden tests to >90% branches.
3. Create unique compound index `(sku, tenantId)` for multi-tenant readiness.


### 2.3  Inventory Service (Go Fiber)

- **Purpose**: Real-time stock accounting per warehouse.
- **Key APIs**: `/adjust`, `/reserve`, `/release`, `/levels?sku=`.
- **Events**: Consumes `order.created` to reserve stock; publishes `stock.low` alerts [^11].
- **Database**: `stocks` (sku, warehouseId, qty, reserved). TTL index for reservation hold.
- **Pending**: implement compensating action for failed payment saga; add Grafana dashboard.


### 2.4  Order Service (Spring Boot 3)

- **Pattern**: CQRS + Saga (write `order-command`, read `order-query`) [^12].
- **Flow**:

1. Client ➜ `POST /orders` (command) ➜ Kafka event.
2. Saga orchestrates inventory reserve ➜ payment authorize ➜ update state.
- **Read side** syncs projections to `orders_read` collection.
- **Todo**: optimise snapshotting, finish integration tests at 90% coverage, idempotent retry logic.


### 2.5  Payment Service (Python FastAPI)

- **Integration**: Stripe test keys configured, webhook `/stripe/webhook`.
- **Security**: HMAC signature validation, service-to-service auth via mTLS [^3].
- **Actions**: capture, refund, webhook event fan-out to `order.updated`.
- **Open tasks**: add PayPal provider adapter, sandbox regression suite.


### 2.6  Notification Service (Node.js Express)

- **Adapters**: SendGrid email implemented; Twilio SMS skeleton.
- **Template Engine**: Handlebars, stored in `templates` collection.
- **Queue**: Kafka `notification` topic; retry with exponential back-off.
- **Next work**: implement DLQ consumer, add Slack/Teams hooks.


## 3  Cross-Cutting Concerns

### 3.1  Security \& Compliance

| Area | Implementation | References |
| :-- | :-- | :-- |
| API auth | Kong verifies JWT, forwards `X-User` \& `X-Roles` | [^1][^2] |
| Service-mesh | Istio with mTLS, Least-privilege traffic policy | [^3] |
| Secrets | AWS Secrets Manager, rotated nightly | [^13] |
| Logging | JSON structured, Correlation-ID header, Fluent Bit → Loki cluster | [^8][^9] |
| Auditing | MongoDB change streams persisted to `audit_log` DB | – |

### 3.2  CI/CD \& Environments

- **Repos**: One git repository per micro-service. Shared actions yaml extends template.
- **Pipeline stages**: *lint → unit-test → build → push → SCA → deploy-preview → integration → prod tag*.
- **Environments**: `dev` (Kind), `test` (EKS namespace), `staging`, `prod`.
- **Helm**: Each service has chart with values overrides. Flux watches `prod-helm` repo.
- **Manual gates**: Payment \& Order require approval before promote.


### 3.3  Observability \& Runbooks

- **Dashboards**: Grafana folders per service (latency, error rate, JVM heap, Go GC).
- **Tracing**: Jaeger auto-instrumentation; service graph view per request chain.
- **Runbooks**: CPU spike, DB connection saturation, Kafka lag, TLS cert renewal [^14][^15].


## 4  Handover Checklist

| Item | Status | Location |
| :-- | :-- | :-- |
| Source code repos | ✔ | GitHub org `retail-platform/*` |
| README build/run docs | ✔ | per repo root |
| OpenAPI 3 specs | User, Product, Order done; others WIP | `/docs/openapi.yaml` |
| DB migration scripts | ✔ (mongock json) | `/infra/migrations` |
| Helm charts | All services | `/deploy/charts/*` |
| CI workflows | Template `ci.yml` + service overrides | `.github/workflows` |
| Secrets vault keys | Delivered via AWS Secrets Manager ARN list | Handover vault sheet |
| Admin credentials | Separate encrypted file (lastpass vault link) | – |
| Monitoring dashboards | JSON exports stored | `/observability/grafana` |
| Postman test collection | ✔ | `/tests/postman_collection.json` |
| Pending work tickets | Logged in Jira project “RM-PLT” | Sprint 35 board |
| Domain knowledge docs | Confluence space “Retail Platform” | index page |

## 5  Recommended Next Milestones

1. **Stabilise Alpha services** (Inventory, Order, Payment, Notification)
    - Complete integration and load tests; raise coverage to ≥90%.
    - Close remaining Jira epics RM-INV-12, RM-ORD-18.
2. **Finish Twilio \& Slack adapters** in Notification, enable multi-channel flow.
3. **Implement Canary deployments** in Helm chart via Istio VirtualService for safer rollouts [^16].
4. **Enforce SCA \& dependency CVE scans** in pipeline using OWASP Dependency-Check.
5. **Add Terraform IaC** modules to provision stage/prod clusters reproducibly.
6. **Adopt Service catalog** – publish OpenAPI docs to internal Backstage portal.

## 6  Contact \& Support Matrix

| Role | Name | Slack | Responsibilities |
| :-- | :-- | :-- | :-- |
| Product owner | R. Kapoor | @rkapoor | Roadmap, requirements |
| Lead architect | L. Chen | @leo | Overall design, security |
| DevOps | A. Singh | @asingh | CI/CD, clusters |
| Backend lead | P. Mercado | @pmercado | Java/Go services |
| Front-End liaison | S. Davis | @sdavis | Consuming apps |
| Data engineering | J. Lee | @jlee | Mongo/Kafka tuning |
| SRE/on-call (24 × 7) | rotation | \#sre-alerts | Incident response |

## 7  Conclusion

The Retail Management Platform has reached a solid **MVP-plus** stage: one production-grade service (User), four alpha services, and a functional CI/CD \& observability stack. The system adheres to modern microservice principles—DB-per-Service, API Gateway, service-mesh security, and GitOps deployment. Tasks ahead focus on completing adapters, test coverage, and operational runbooks before a full production launch.

This document, together with the attached code, Helm charts, pipeline definitions and Jira backlog, provides all knowledge required for a smooth takeover by a new engineering or operations team.

<div style="text-align: center">⁂</div>

[^1]: https://dev.to/kansaok/design-patterns-in-microservices-chapter-2-api-gateway-pattern-24co

[^2]: https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-integrating-microservices/api-gateway-pattern.html

[^3]: https://www.veritis.com/blog/7-security-best-practices-for-microservices/

[^4]: https://dev.to/bmadupati1108/tutorial-mastering-microservices-security-best-practices-and-tools-for-protecting-your-system-3pi

[^5]: https://www.f5.com/content/dam/f5/corp/global/pdf/ebooks/Microservices_Designing_Deploying.pdf

[^6]: https://www.devskillbuilder.com/18-essential-microservice-best-practices-655fd4d20ee6

[^7]: https://dev.to/fazly_fathhy/steps-to-achieve-cicd-pipeline-for-microservice-architecture-2e6m

[^8]: https://betterstack.com/community/guides/logging/logging-microservices/

[^9]: https://blog.stackademic.com/best-logging-practices-in-microservices-and-distributed-systems-8fb1226862ea?gi=b2a6935db41e

[^10]: https://github.com/wpcodevo/fastapi_mongodb

[^11]: https://www.sayonetech.com/blog/inventory-management-system-using-microservices/

[^12]: https://ibm-cloud-architecture.github.io/refarch-kc/microservices/order-command/

[^13]: https://mojoauth.com/ciam-101/api-security-best-practices-for-microservices

[^14]: https://developer.harness.io/docs/ai-sre/runbooks/

[^15]: https://learn.microsoft.com/en-us/system-center/scsm/runbooks?view=sc-sm-2022

[^16]: https://www.javacodegeeks.com/2024/01/mastering-microservices-deployment-strategies-tools-and-best-practices.html

[^17]: https://www.miquido.com/blog/software-project-handover-checklist/

[^18]: https://www.pythian.com/blog/technical-track/top-three-considerations-documenting-microservice

[^19]: https://www.pmi.org/learning/library/agile-metrics-progress-tracking-status-6564

[^20]: https://irp.cdn-website.com/3de07f8a/files/uploaded/nonovuvuwaporuto.pdf

[^21]: https://whatfix.com/blog/handover-documentation/

[^22]: https://www.c-sharpcorner.com/blogs/documentation-for-microservice-implementation

[^23]: https://www.linkedin.com/pulse/agile-metrics-matter-tracking-performance-progress-zohaib-1veof

[^24]: https://www.developer.com/design/transition-to-microservices/

[^25]: https://www.resolution.de/post/project-handover-checklist-template/

[^26]: https://stackoverflow.com/questions/217185/software-system-handover-template-are-there-any-good-examples-out-there

[^27]: https://plainenglish.io/blog/documenting-microservices-a-comprehensive-step-by-step-guide

[^28]: https://www.nagarro.com/en/blog/agile-metrics-part-2

[^29]: https://dev.to/flippedcoding/the-developer-s-deployment-checklist-3p5p

[^30]: https://www.ironin.it/blog/project-handover-checklist-guide-for-our-clients.html

[^31]: https://multishoring.com/blog/how-to-perform-a-project-handover/

[^32]: https://braincuber.com/documenting-microservices-in-2024/

[^33]: https://www.geeksforgeeks.org/agile-metrics-summary-and-best-practices/

[^34]: https://www.slideshare.net/slideshow/the-ultimate-kubernetes-deployment-checklist-infra-to-microservices/265503783

[^35]: https://www.thinslices.com/insights/the-10-commandments-of-a-successful-project-handover

[^36]: https://www.urologypros.com/Content/Downloads/PDFs/7e444812-001c-4dc3-8e79-268de694dd00.pdf

[^37]: https://praxent.com/blog/software-handover-documentation-checklist

[^38]: https://dev.to/rubixkube/kubernetes-for-microservices-best-practices-and-patterns-2440

[^39]: https://www.youtube.com/watch?v=lwe28kMehX0

[^40]: https://dev.to/isaactony/logging-and-monitoring-best-practices-358d

[^41]: https://dev.to/praxentsoftware/a-technical-documentation-checklist-plus-10-tips-for-seamless-software-hand-offs-18ko

[^42]: https://www.youtube.com/watch?v=fGX71dNjGD0

[^43]: https://docs.oracle.com/en/industries/financial-services/microservices-common/14.7.0.0.0/cadig/configuration-and-deployment-guide.pdf

[^44]: https://gist.github.com/TimothyJones/1508a7081405d57073b99180312f5caa

[^45]: https://www.slideshare.net/slideshow/reference-architectures-shows-a-microservices-deployed-to-kubernetes/132831321

[^46]: https://www.printfriendly.com/document/software-project-handover-document-template

[^47]: https://www.alexanderdaniels.co.uk/how-to-write-handover-document/

[^48]: https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-microservices/aks-microservices-advanced

[^49]: https://www.curotec.com/insights/creating-documentation-for-an-effective-custom-code-handoff/

[^50]: https://vulcan.io/blog/how-to-secure-microservices-the-complete-guide/

[^51]: https://abp.io/docs/latest/tutorials/microservice/part-05

[^52]: https://ro.scribd.com/document/813756064/Basic-CI-CD-pipeline-for-Microservices-based-Application

[^53]: https://github.com/paucls/runbook-ddd-cqrs-es-microservice

[^54]: https://dev.to/isaactony/building-your-first-microservice-system-with-spring-boot-a-beginners-guide-3b28

[^55]: https://www.accelq.com/blog/microservices-ci-cd/

[^56]: https://www.tatvasoft.com/blog/microservices-best-practices/

[^57]: https://github.com/brunosantoslab/order-service

[^58]: https://github.com/cmakkaya/Ln-D07-full-CI-CD-pipelines-for-microservice-based-dynamic-app

[^59]: https://www.serverlessguru.com/blog/how-i-created-an-inventory-microservice-with-cloudgto-in-minutes

[^60]: https://learn.microsoft.com/th-th/system-center/orchestrator/standard-activities/runbook-control?view=sc-orch-2025\&viewFallbackFrom=sc-orch-1801

