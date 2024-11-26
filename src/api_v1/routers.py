from fastapi import APIRouter

from api_v1.auth.views import router as auth_router
from api_v1.health_check.views import router as health_check_router

router = APIRouter()

router.include_router(auth_router, tags=["auth"])
router.include_router(health_check_router, tags=["healthcheck"])
