from fastapi import FastAPI
from app.api import inventory

app = FastAPI()
app.include_router(inventory.router)
