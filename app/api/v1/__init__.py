from fastapi import APIRouter
from app.api.v1.endpoints import readings, devices, ai_query

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

api_router.include_router(
    ai_query.router,
    prefix="/ai",
    tags=["ai"]
)
