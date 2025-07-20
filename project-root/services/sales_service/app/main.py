from fastapi import FastAPI
from api import sales
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(sales.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
