from fastapi import FastAPI
from app.api import sales

app = FastAPI()
app.include_router(sales.router)
