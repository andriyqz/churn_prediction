import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.predict import router as predict_router
from app.services import model_service
from app.settings import settings

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app_: FastAPI):
    model_service.load_model()
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(predict_router)