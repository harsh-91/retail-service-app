from fastapi import FastAPI
from app.api import payments

app = FastAPI()

app.include_router(payments.router)
