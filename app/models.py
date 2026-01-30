from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.database import Base


class Device(Base):
    """Device model - represents IoT devices in the fleet"""
    __tablename__ = "devices"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # One-to-Many relationship: One Device -> Many Readings
    readings: Mapped[List["Reading"]] = relationship(
        "Reading",
        back_populates="device",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Device(id={self.id}, name={self.name}, location={self.location})>"


class Reading(Base):
    """Reading model - stores sensor data from devices"""
    __tablename__ = "readings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Store all sensor values as JSON for flexibility
    values: Mapped[dict] = mapped_column(JSON, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # Many-to-One relationship: Many Readings -> One Device
    device: Mapped["Device"] = relationship("Device", back_populates="readings")
    
    def __repr__(self) -> str:
        return f"<Reading(id={self.id}, device_id={self.device_id}, timestamp={self.timestamp})>"
