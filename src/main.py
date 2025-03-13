from fastapi import FastAPI
from src.configs.db import initDB
from src.api.main import api_router

app = FastAPI()


@app.on_event("startup")
def startup():
    print("Starting up...")
    initDB()


app.include_router(api_router)
