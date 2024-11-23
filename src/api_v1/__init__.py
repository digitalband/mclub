from fastapi import APIRouter
from api_v1.health_check.views import router as auth_router

router = APIRouter()

router.include_router(auth_router, tags=["healthcheck"])
