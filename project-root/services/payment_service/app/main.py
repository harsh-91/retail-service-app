from fastapi import FastAPI
from api import payments
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(payments.router)
app.mount("/static", StaticFiles(directory="static"), name="static")