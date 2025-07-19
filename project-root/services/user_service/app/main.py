from fastapi import FastAPI
from app.api import auth
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.include_router(auth.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def root():
    return {"message": "User Service is running"}
