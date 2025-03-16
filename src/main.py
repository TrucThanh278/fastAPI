from fastapi import FastAPI
from src.configs.db import lifespan
from src.api.main import api_router
from fastapi_pagination import add_pagination

app = FastAPI(lifespan=lifespan)


app.include_router(api_router)

add_pagination(app)
