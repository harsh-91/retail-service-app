from fastapi import FastAPI, Body
from contextlib import asynccontextmanager
from models import ReportRequest
import asyncio
import event_ingestor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch the event consumer
    consumer_task = asyncio.create_task(event_ingestor.consume_events())
    yield
    # Shutdown: cancel the consumer
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="Analytics Service", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"msg": "Analytics Service live!"}

@app.post("/reports")
async def generate_report(request: ReportRequest = Body(...)):
    """
    Generate and fetch an analytics report by tenant, type, and period.
    """
    # Basic: fetch relevant events from db for requested period
    coll = db.domain_events
    query = {
        "tenant_id": request.tenant_id,
        "event_type": {"$regex": f"^{request.report_type.split('_')[0]}"},
        "timestamp": {
            "$gte": request.period_start,
            "$lte": request.period_end
        }
    }
    events = await coll.find(query).to_list(1000)
    if not events:
        raise HTTPException(status_code=404, detail="No events found for this report/period.")

    # Example logic: just return raw events for now, you can summarize as needed
    return {"tenant_id": request.tenant_id, "report_type": request.report_type, "count": len(events), "events": events}

@app.get("/analytics/{tenant_id}/event_counts")
async def event_counts(tenant_id: str, report_type: str = None):
    """
    Get summary event counts for a tenant, optionally filtered by report type/topic.
    """
    coll = db.domain_events
    match = {"tenant_id": tenant_id}
    if report_type:
        match["event_type"] = {"$regex": f"^{report_type}"}
    count = await coll.count_documents(match)
    return {"tenant_id": tenant_id, "report_type": report_type, "event_count": count}
