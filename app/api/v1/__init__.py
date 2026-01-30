from fastapi import APIRouter
from app.api.v1.endpoints import readings, devices

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    devices.router,
    prefix="",
    tags=["devices"]
)

api_router.include_router(
    readings.router,
    prefix="",
    tags=["readings"]
)
