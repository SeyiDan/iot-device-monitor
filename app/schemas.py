from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ReadingCreate(BaseModel):
    """Schema for creating a new reading - strict validation with Pydantic v2"""
    device_id: int = Field(..., gt=0, description="Device ID must be positive")
    temperature: float = Field(..., ge=-50, le=150, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    battery_level: float = Field(..., ge=0, le=100, description="Battery level percentage")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Reading timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "device_id": 1,
                "temperature": 25.5,
                "humidity": 60.0,
                "battery_level": 85.0,
                "timestamp": "2024-01-15T10:30:00"
            }
        }
    )


class ReadingResponse(BaseModel):
    """Schema for reading response"""
    id: int
    device_id: int
    values: dict
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DeviceBase(BaseModel):
    """Base device schema"""
    name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


class DeviceCreate(DeviceBase):
    """Schema for creating a device"""
    pass


class DeviceResponse(DeviceBase):
    """Schema for device response"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class DeviceWithReadings(DeviceResponse):
    """Schema for device with its readings"""
    readings: list[ReadingResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
