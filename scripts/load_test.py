"""
Load testing script to demonstrate high-frequency data ingestion.
Simulates multiple IoT devices sending readings simultaneously.

Requirements:
    pip install aiohttp

Usage:
    python scripts/load_test.py --devices 10 --readings 100
"""

import asyncio
import aiohttp
import time
import argparse
from datetime import datetime
import sys


API_BASE = "http://localhost:8000/api/v1"


async def create_device(session, device_num):
    """Create a test device"""
    payload = {
        "name": f"Load Test Device {device_num}",
        "location": f"Test Zone {device_num % 10}",
        "is_active": True
    }
    
    async with session.post(f"{API_BASE}/devices", json=payload) as response:
        if response.status == 201:
            data = await response.json()
            return data["id"]
        else:
            print(f"Failed to create device: {response.status}")
            return None


async def send_reading(session, device_id, reading_num):
    """Send a single reading"""
    payload = {
        "device_id": device_id,
        "temperature": 20.0 + (reading_num % 30),
        "humidity": 40.0 + (reading_num % 40),
        "battery_level": 100.0 - (reading_num % 50),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    start_time = time.time()
    
    try:
        async with session.post(f"{API_BASE}/readings", json=payload) as response:
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # Convert to ms
            
            return {
                "success": response.status == 201,
                "status": response.status,
                "latency": latency,
                "device_id": device_id
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "latency": 0,
            "device_id": device_id
        }


async def device_simulator(session, device_id, num_readings, results):
    """Simulate a single device sending multiple readings"""
    for i in range(num_readings):
        result = await send_reading(session, device_id, i)
        results.append(result)
        
        # Small delay to simulate realistic sensor behavior
        await asyncio.sleep(0.01)


async def run_load_test(num_devices, readings_per_device):
    """Run the load test with multiple devices"""
    
    print(f"\nIoT Fleet Monitor - Load Test")
    print("=" * 60)
    print(f"Devices: {num_devices}")
    print(f"Readings per device: {readings_per_device}")
    print(f"Total readings: {num_devices * readings_per_device}")
    print("=" * 60)
    print()
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Create devices
        print("Creating test devices...")
        device_tasks = [create_device(session, i) for i in range(num_devices)]
        device_ids = await asyncio.gather(*device_tasks)
        device_ids = [d for d in device_ids if d is not None]
        
        if len(device_ids) != num_devices:
            print(f"Warning: Only created {len(device_ids)}/{num_devices} devices")
        
        print(f"Created {len(device_ids)} devices")
        print()
        
        # Step 2: Send readings concurrently
        print("Sending readings...")
        start_time = time.time()
        
        results = []
        simulator_tasks = [
            device_simulator(session, device_id, readings_per_device, results)
            for device_id in device_ids
        ]
        
        await asyncio.gather(*simulator_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        successful = sum(1 for r in results if r.get("success", False))
        failed = len(results) - successful
        
        latencies = [r["latency"] for r in results if r.get("success", False)]
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        else:
            avg_latency = min_latency = max_latency = p95_latency = 0
        
        # Print results
        print()
        print("=" * 60)
        print("Results")
        print("=" * 60)
        print(f"Total time: {total_time:.2f}s")
        print(f"Throughput: {len(results) / total_time:.2f} readings/sec")
        print()
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {(successful / len(results) * 100):.1f}%")
        print()
        print("Latency (ms):")
        print(f"  Average: {avg_latency:.2f}ms")
        print(f"  Min: {min_latency:.2f}ms")
        print(f"  Max: {max_latency:.2f}ms")
        print(f"  P95: {p95_latency:.2f}ms")
        print("=" * 60)
        
        # Print failed requests if any
        if failed > 0:
            print()
            print("Failed requests:")
            for r in results:
                if not r.get("success", False):
                    print(f"  Device {r['device_id']}: {r.get('error', 'Unknown error')}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Load test the IoT Fleet Monitor API"
    )
    parser.add_argument(
        "--devices",
        type=int,
        default=10,
        help="Number of devices to simulate (default: 10)"
    )
    parser.add_argument(
        "--readings",
        type=int,
        default=100,
        help="Number of readings per device (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Check if API is accessible
    try:
        import requests
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code != 200:
            print("[ERROR] API is not accessible. Make sure the server is running.")
            print("   Run: docker-compose up -d")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Cannot connect to API: {e}")
        print("   Make sure the server is running: docker-compose up -d")
        sys.exit(1)
    
    # Run the load test
    asyncio.run(run_load_test(args.devices, args.readings))
    
    print()
    print("Tips for improving performance:")
    print("  1. Increase Uvicorn workers in Dockerfile")
    print("  2. Increase database connection pool size")
    print("  3. Add Redis caching layer")
    print("  4. Use read replicas for queries")
    print("  5. Deploy with load balancer")


if __name__ == "__main__":
    main()
