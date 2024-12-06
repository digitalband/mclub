from fastapi import APIRouter

from api.auth import router as auth_router
from api.health_check import router as health_check_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(health_check_router, tags=["healthcheck"])
