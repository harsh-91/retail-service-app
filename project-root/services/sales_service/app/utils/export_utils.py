# utils/export_utils.py

from fastapi.responses import StreamingResponse, FileResponse
import io

def export_sales_csv(tenant_id, sale_id=None):
    # Stub: create in-memory CSV with dummy content
    content = "sale_id,amount,date\n0001,100.0,2025-01-01\n"
    return StreamingResponse(io.StringIO(content), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sales.csv"})

def export_sales_pdf(tenant_id, sale_id=None):
    # Stub: send a dummy PDF file (could be generated)
    # Here we just use a blank bytesio for demo
    return StreamingResponse(io.BytesIO(b"%PDF-1.4\n%EOF\n"), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=sales.pdf"})
