from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict

class DomainEvent(BaseModel):
    event_type: str
    tenant_id: str
    payload: Dict
    timestamp: datetime

class ReportRequest(BaseModel):
    tenant_id: str
    report_type: str
    period_start: datetime
    period_end: datetime
