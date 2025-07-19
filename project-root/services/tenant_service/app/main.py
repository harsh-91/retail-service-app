from fastapi import FastAPI
from app.api import tenant  # assumes your router is at app/api/tenant.py

app = FastAPI(
    title="Tenant Service",
    description="APIs for onboarding and managing business tenants in the Retail Management Platform.",
    version="1.0.0"
)

# Mount the tenant router
app.include_router(tenant.router)

# (Optional) Health Check
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

# (Optional) Root welcome
@app.get("/", tags=["welcome"])
def root():
    return {"message": "Tenant Service is up and running."}
