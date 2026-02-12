"""
IoT Device Simulator - Simulates multiple IoT devices sending real-time sensor data.

This script creates virtual IoT devices that continuously send sensor readings
to the API, simulating real-world device behavior with realistic patterns.

Usage:
    python scripts/simulate_devices.py --devices 5 --interval 10
"""

import asyncio
import random
import sys
from pathlib import Path
from datetime import datetime
import argparse
import httpx

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

API_BASE = "http://localhost:8000"


class VirtualDevice:
    """Simulates a single IoT device with realistic sensor behavior."""

    def __init__(self, device_id: int, name: str, location: str):
        self.device_id = device_id
        self.name = name
        self.location = location
        self.temperature = 25.0  # Base temperature
        self.humidity = 50.0  # Base humidity
        self.battery_level = 100.0
        self.is_running = True

    def generate_reading(self) -> dict:
        """Generate realistic sensor reading with natural variations."""
        
        # Temperature variations (slow drift + random noise)
        self.temperature += random.uniform(-1.0, 1.0)
        self.temperature = max(15.0, min(95.0, self.temperature))  # Bounds
        
        # Humidity variations
        self.humidity += random.uniform(-2.0, 2.0)
        self.humidity = max(20.0, min(90.0, self.humidity))
        
        # Battery drain (gradual decrease)
        self.battery_level -= random.uniform(0.01, 0.05)
        self.battery_level = max(0.0, self.battery_level)
        
        # Occasionally simulate critical temperature
        if random.random() < 0.05:  # 5% chance
            self.temperature = random.uniform(80.0, 95.0)
        
        return {
            "device_id": self.device_id,
            "temperature": round(self.temperature, 2),
            "humidity": round(self.humidity, 2),
            "battery_level": round(self.battery_level, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def send_reading(self, client: httpx.AsyncClient) -> bool:
        """Send sensor reading to API."""
        reading = self.generate_reading()
        
        try:
            response = await client.post(
                f"{API_BASE}/api/v1/readings",
                json=reading,
                timeout=10.0
            )
            
            if response.status_code == 201:
                temp_status = "CRITICAL" if reading["temperature"] > 80 else "NORMAL"
                print(
                    f"[{self.name}] Sent reading: "
                    f"Temp={reading['temperature']}°C ({temp_status}), "
                    f"Humidity={reading['humidity']}%, "
                    f"Battery={reading['battery_level']}%"
                )
                return True
            else:
                print(f"[{self.name}] Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[{self.name}] Failed to send: {str(e)}")
            return False


class DeviceSimulator:
    """Manages multiple virtual devices."""

    def __init__(self, num_devices: int = 5, interval: int = 10):
        self.num_devices = num_devices
        self.interval = interval
        self.devices = []
        self.stats = {
            "total_readings": 0,
            "successful": 0,
            "failed": 0,
            "critical_temps": 0,
        }

    async def create_devices(self, client: httpx.AsyncClient):
        """Create virtual devices in the system."""
        print(f"\nCreating {self.num_devices} virtual devices...")
        
        locations = [
            "Server Room A",
            "Data Center B",
            "Warehouse Zone 1",
            "Laboratory North",
            "Office Building C",
            "Production Floor",
            "Storage Area D",
            "Testing Facility",
        ]
        
        for i in range(self.num_devices):
            device_data = {
                "name": f"Sensor-{i+1:03d}",
                "location": locations[i % len(locations)],
                "is_active": True,
            }
            
            try:
                response = await client.post(
                    f"{API_BASE}/api/v1/devices",
                    json=device_data
                )
                
                if response.status_code == 201:
                    device_info = response.json()
                    virtual_device = VirtualDevice(
                        device_info["id"],
                        device_info["name"],
                        device_info["location"],
                    )
                    self.devices.append(virtual_device)
                    print(f"  Created: {device_info['name']} at {device_info['location']}")
                else:
                    print(f"  Failed to create device {i+1}")
                    
            except Exception as e:
                print(f"  Error creating device {i+1}: {str(e)}")
        
        print(f"\n{len(self.devices)} virtual devices ready\n")

    async def run_simulation(self):
        """Run continuous device simulation."""
        print(f"Starting simulation...")
        print(f"  Devices: {len(self.devices)}")
        print(f"  Interval: {self.interval} seconds")
        print(f"  Press Ctrl+C to stop\n")
        
        async with httpx.AsyncClient() as client:
            # Create devices
            await self.create_devices(client)
            
            if not self.devices:
                print("No devices created. Exiting.")
                return
            
            # Main simulation loop
            try:
                iteration = 0
                while True:
                    iteration += 1
                    print(f"\n--- Iteration {iteration} ---")
                    
                    # Send readings from all devices concurrently
                    tasks = [
                        device.send_reading(client)
                        for device in self.devices
                    ]
                    results = await asyncio.gather(*tasks)
                    
                    # Update statistics
                    self.stats["total_readings"] += len(results)
                    self.stats["successful"] += sum(results)
                    self.stats["failed"] += len(results) - sum(results)
                    
                    # Count critical temperatures
                    for device in self.devices:
                        if device.temperature > 80:
                            self.stats["critical_temps"] += 1
                    
                    # Print statistics
                    print(f"\nStatistics:")
                    print(f"  Total readings sent: {self.stats['total_readings']}")
                    print(f"  Successful: {self.stats['successful']}")
                    print(f"  Failed: {self.stats['failed']}")
                    print(f"  Critical temps detected: {self.stats['critical_temps']}")
                    
                    # Wait before next iteration
                    await asyncio.sleep(self.interval)
                    
            except KeyboardInterrupt:
                print("\n\nSimulation stopped by user")
                print("\nFinal Statistics:")
                print(f"  Total readings sent: {self.stats['total_readings']}")
                print(f"  Successful: {self.stats['successful']}")
                print(f"  Failed: {self.stats['failed']}")
                print(f"  Critical temps detected: {self.stats['critical_temps']}")


async def verify_api():
    """Verify API is accessible."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/health", timeout=5.0)
            return response.status_code == 200
    except Exception:
        return False


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Simulate IoT devices sending sensor data"
    )
    parser.add_argument(
        "--devices",
        type=int,
        default=5,
        help="Number of virtual devices to simulate (default: 5)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Seconds between readings (default: 10)",
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("IoT Device Simulator")
    print("=" * 60)
    
    # Verify API is running
    print("\nChecking API availability...")
    if not await verify_api():
        print("\nERROR: API is not accessible at", API_BASE)
        print("Please ensure the application is running:")
        print("  docker-compose up -d")
        print("  OR")
        print("  uvicorn app.main:app")
        sys.exit(1)
    
    print("API is accessible")
    
    # Run simulation
    simulator = DeviceSimulator(
        num_devices=args.devices,
        interval=args.interval
    )
    
    await simulator.run_simulation()


if __name__ == "__main__":
    asyncio.run(main())
