"""
Script to seed the database with test devices and readings.
Run this after starting the Docker containers to populate initial data.

Usage:
    python scripts/seed_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from app.database import AsyncSessionLocal, engine, Base
from app.models import Device, Reading


async def create_test_devices():
    """Create test devices in the database"""
    
    async with AsyncSessionLocal() as session:
        # Create sample devices
        devices = [
            Device(
                name="Temperature Sensor 01",
                location="Lab A - North Wall",
                is_active=True
            ),
            Device(
                name="Temperature Sensor 02",
                location="Lab B - South Wall",
                is_active=True
            ),
            Device(
                name="Humidity Sensor 01",
                location="Warehouse Zone 1",
                is_active=True
            ),
            Device(
                name="Multi-Sensor 01",
                location="Server Room",
                is_active=True
            ),
            Device(
                name="Outdoor Sensor",
                location="Building Exterior",
                is_active=False
            ),
        ]
        
        session.add_all(devices)
        await session.commit()
        
        print(f"Created {len(devices)} test devices")
        return devices


async def create_test_readings(devices):
    """Create test readings for the devices"""
    
    async with AsyncSessionLocal() as session:
        base_time = datetime.utcnow() - timedelta(hours=24)
        readings = []
        
        # Create 50 readings for each active device
        for device in devices:
            if not device.is_active:
                continue
                
            for i in range(50):
                timestamp = base_time + timedelta(minutes=i * 30)
                
                # Vary temperature to simulate real conditions
                base_temp = 20.0 + (i % 20)
                temp_variation = (i % 5) * 2.0
                
                reading = Reading(
                    device_id=device.id,
                    values={
                        "temperature": base_temp + temp_variation,
                        "humidity": 40.0 + (i % 30),
                        "battery_level": 100.0 - (i * 0.5)
                    },
                    timestamp=timestamp
                )
                readings.append(reading)
        
        session.add_all(readings)
        await session.commit()
        
        print(f"Created {len(readings)} test readings")


async def main():
    """Main function to seed the database"""
    
    print("Starting database seeding...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created")
    
    # Create test data
    devices = await create_test_devices()
    await create_test_readings(devices)
    
    print("\nDatabase seeding completed successfully!")
    print("\nTest devices created:")
    for device in devices:
        status = "Active" if device.is_active else "Inactive"
        print(f"  - {device.name} ({device.location}) - {status}")
    
    print("\nYou can now:")
    print("  1. Access the API at http://localhost:8000/docs")
    print("  2. View data in PGAdmin at http://localhost:5050")
    print("  3. Test the API with the created devices")


if __name__ == "__main__":
    asyncio.run(main())
