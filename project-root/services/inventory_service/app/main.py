from fastapi import FastAPI
from app.api import inventory
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(inventory.router)
app.mount("/static", StaticFiles(directory="static"), name="static")