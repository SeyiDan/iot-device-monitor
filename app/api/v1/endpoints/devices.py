from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Device
from app.schemas import DeviceCreate, DeviceResponse, DeviceWithReadings

router = APIRouter()


@router.post(
    "/devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new device"
)
async def create_device(
    device: DeviceCreate,
    db: AsyncSession = Depends(get_db)
) -> DeviceResponse:
    """Create a new IoT device in the system"""
    
    db_device = Device(
        name=device.name,
        location=device.location,
        is_active=device.is_active
    )
    
    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)
    
    return db_device


@router.get(
    "/devices",
    response_model=list[DeviceResponse],
    summary="List all devices"
)
async def list_devices(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> list[DeviceResponse]:
    """Retrieve all devices with pagination"""
    
    result = await db.execute(
        select(Device)
        .offset(skip)
        .limit(limit)
    )
    devices = result.scalars().all()
    
    return list(devices)


@router.get(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    summary="Get device by ID"
)
async def get_device(
    device_id: int,
    db: AsyncSession = Depends(get_db)
) -> DeviceResponse:
    """Retrieve a specific device by ID"""
    
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    
    return device


@router.put(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    summary="Update a device"
)
async def update_device(
    device_id: int,
    device_update: DeviceCreate,
    db: AsyncSession = Depends(get_db)
) -> DeviceResponse:
    """Update device information"""
    
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    
    device.name = device_update.name
    device.location = device_update.location
    device.is_active = device_update.is_active
    
    await db.commit()
    await db.refresh(device)
    
    return device


@router.delete(
    "/devices/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a device"
)
async def delete_device(
    device_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a device and all its readings"""
    
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    
    await db.delete(device)
    await db.commit()
