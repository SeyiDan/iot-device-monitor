import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Reading, Device
from app.schemas import ReadingCreate, ReadingResponse
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


async def check_critical_reading(
    device_id: int,
    temperature: float,
    reading_id: int
) -> None:
    """
    Background task to check if reading is critical.
    This runs asynchronously and doesn't block the API response.
    """
    if temperature > settings.CRITICAL_TEMP_THRESHOLD:
        logger.warning(
            f"CRITICAL ALERT: Device {device_id} temperature is {temperature}°C "
            f"(threshold: {settings.CRITICAL_TEMP_THRESHOLD}°C) - Reading ID: {reading_id}"
        )
        # In production, this would trigger alerts (email, SMS, webhook, etc.)


@router.post(
    "/readings",
    response_model=ReadingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest sensor readings at high frequency",
    description="Optimized endpoint for high-frequency sensor data ingestion with background processing"
)
async def create_reading(
    reading: ReadingCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> ReadingResponse:
    """
    High-performance endpoint for ingesting IoT sensor readings.
    
    - **device_id**: ID of the device sending the reading
    - **temperature**: Temperature in Celsius (-50 to 150)
    - **humidity**: Humidity percentage (0 to 100)
    - **battery_level**: Battery level percentage (0 to 100)
    - **timestamp**: UTC timestamp of the reading
    
    Background processing checks for critical conditions without blocking the response.
    """
    
    # Verify device exists (optimized query)
    result = await db.execute(
        select(Device).where(Device.id == reading.device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {reading.device_id} not found"
        )
    
    if not device.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device {reading.device_id} is not active"
        )
    
    # Store sensor values as JSON for flexibility
    values = {
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "battery_level": reading.battery_level
    }
    
    # Create reading record (async for high performance)
    db_reading = Reading(
        device_id=reading.device_id,
        values=values,
        timestamp=reading.timestamp
    )
    
    db.add(db_reading)
    await db.commit()
    await db.refresh(db_reading)
    
    # Add background task for critical condition checking
    # This doesn't block the API response
    background_tasks.add_task(
        check_critical_reading,
        device_id=reading.device_id,
        temperature=reading.temperature,
        reading_id=db_reading.id
    )
    
    return db_reading


@router.get(
    "/readings/{reading_id}",
    response_model=ReadingResponse,
    summary="Get a specific reading by ID"
)
async def get_reading(
    reading_id: int,
    db: AsyncSession = Depends(get_db)
) -> ReadingResponse:
    """Retrieve a specific reading by its ID"""
    
    result = await db.execute(
        select(Reading).where(Reading.id == reading_id)
    )
    reading = result.scalar_one_or_none()
    
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reading with id {reading_id} not found"
        )
    
    return reading


@router.get(
    "/devices/{device_id}/readings",
    response_model=list[ReadingResponse],
    summary="Get all readings for a device"
)
async def get_device_readings(
    device_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> list[ReadingResponse]:
    """Retrieve recent readings for a specific device"""
    
    # Verify device exists
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    
    # Get readings ordered by timestamp (most recent first)
    result = await db.execute(
        select(Reading)
        .where(Reading.device_id == device_id)
        .order_by(Reading.timestamp.desc())
        .limit(limit)
    )
    readings = result.scalars().all()
    
    return list(readings)
