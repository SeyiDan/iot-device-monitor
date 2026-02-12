"""
System Demonstration Script

Demonstrates all features of the IoT Device Monitor including:
- Device management
- Sensor readings
- Critical temperature alerts
- AI-powered queries (if configured)

Usage:
    python scripts/demo.py
"""

import requests
import time
import sys
from datetime import datetime
from typing import Optional

API_BASE = "http://localhost:8000"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def check_api_health() -> bool:
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def demo_device_management():
    """Demonstrate device management features."""
    print_section("Device Management")
    
    # Create devices
    print_info("Creating demo devices...")
    devices = [
        {"name": "Temperature Sensor A1", "location": "Server Room", "is_active": True},
        {"name": "Temperature Sensor B2", "location": "Data Center", "is_active": True},
        {"name": "Humidity Sensor C3", "location": "Warehouse", "is_active": True},
    ]
    
    created_devices = []
    for device_data in devices:
        response = requests.post(f"{API_BASE}/api/v1/devices", json=device_data)
        if response.status_code == 201:
            device = response.json()
            created_devices.append(device)
            print_success(f"Created: {device['name']} (ID: {device['id']}) at {device['location']}")
        else:
            print_error(f"Failed to create device: {device_data['name']}")
    
    time.sleep(1)
    
    # List all devices
    print_info("\nRetrieving all devices...")
    response = requests.get(f"{API_BASE}/api/v1/devices")
    if response.status_code == 200:
        all_devices = response.json()
        print_success(f"Found {len(all_devices)} total devices in system")
        for device in all_devices[-3:]:  # Show last 3
            status = "Active" if device["is_active"] else "Inactive"
            print(f"  - {device['name']} | {device['location']} | {status}")
    
    return created_devices


def demo_sensor_readings(devices: list):
    """Demonstrate sensor reading submission."""
    print_section("Sensor Readings")
    
    if not devices:
        print_warning("No devices available for readings demo")
        return []
    
    print_info(f"Sending sensor readings from {len(devices)} devices...")
    
    readings_data = [
        # Normal readings
        {"device_id": devices[0]["id"], "temperature": 25.5, "humidity": 55.0, "battery_level": 85.0},
        {"device_id": devices[1]["id"], "temperature": 32.1, "humidity": 48.0, "battery_level": 90.0},
        {"device_id": devices[2]["id"], "temperature": 28.7, "humidity": 62.0, "battery_level": 75.0},
    ]
    
    created_readings = []
    for reading_data in readings_data:
        reading_data["timestamp"] = datetime.utcnow().isoformat()
        response = requests.post(f"{API_BASE}/api/v1/readings", json=reading_data)
        
        if response.status_code == 201:
            reading = response.json()
            created_readings.append(reading)
            device_name = next((d["name"] for d in devices if d["id"] == reading["device_id"]), "Unknown")
            print_success(
                f"{device_name}: "
                f"Temp={reading['temperature']}°C, "
                f"Humidity={reading['humidity']}%, "
                f"Battery={reading['battery_level']}%"
            )
        else:
            print_error(f"Failed to submit reading for device {reading_data['device_id']}")
    
    return created_readings


def demo_critical_alert(devices: list):
    """Demonstrate critical temperature alert."""
    print_section("Critical Temperature Alert")
    
    if not devices:
        print_warning("No devices available for critical alert demo")
        return
    
    print_info("Simulating critical temperature event...")
    print_warning(f"Sending reading with temperature > 80°C")
    
    critical_reading = {
        "device_id": devices[0]["id"],
        "temperature": 95.0,  # Critical!
        "humidity": 45.0,
        "battery_level": 80.0,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    response = requests.post(f"{API_BASE}/api/v1/readings", json=critical_reading)
    
    if response.status_code == 201:
        reading = response.json()
        print_error(
            f"CRITICAL ALERT: {devices[0]['name']} - "
            f"Temperature: {reading['temperature']}°C (Threshold: 80°C)"
        )
        print_info("Check container logs to see the alert:")
        print("  docker logs iot_device_monitor_api --tail 20")
    else:
        print_error("Failed to submit critical reading")


def demo_device_statistics(devices: list):
    """Demonstrate device statistics endpoint."""
    print_section("Device Statistics")
    
    if not devices:
        print_warning("No devices available for statistics demo")
        return
    
    device = devices[0]
    print_info(f"Retrieving statistics for: {device['name']}")
    
    response = requests.get(f"{API_BASE}/api/v1/devices/{device['id']}/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print_success("Statistics retrieved successfully:")
        print(f"  Device: {stats.get('device_name', 'N/A')}")
        print(f"  Total Readings: {stats.get('total_readings', 0)}")
        print(f"  Avg Temperature: {stats.get('avg_temperature', 0):.2f}°C")
        print(f"  Max Temperature: {stats.get('max_temperature', 0):.2f}°C")
        print(f"  Min Temperature: {stats.get('min_temperature', 0):.2f}°C")
        print(f"  Avg Humidity: {stats.get('avg_humidity', 0):.2f}%")
        print(f"  Avg Battery: {stats.get('avg_battery_level', 0):.2f}%")
    else:
        print_warning("Statistics endpoint may not be available")


def demo_ai_queries():
    """Demonstrate AI-powered natural language queries."""
    print_section("AI-Powered Queries (Optional)")
    
    # Check if AI endpoint exists
    try:
        response = requests.get(f"{API_BASE}/api/v1/ai/examples", timeout=5)
        if response.status_code != 200:
            print_warning("AI features not configured or OpenAI API key not set")
            print_info("To enable: Add OPENAI_API_KEY to .env file")
            return
    except Exception:
        print_warning("AI endpoints not available")
        return
    
    print_success("AI features are available!")
    
    # Try a simple query
    queries = [
        "Show all devices",
        "Devices with high temperature",
        "Average temperature per device",
    ]
    
    for query in queries:
        print_info(f"\nQuery: '{query}'")
        
        try:
            response = requests.post(
                f"{API_BASE}/api/v1/ai/query",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Found {result['result_count']} results")
                print(f"SQL: {result['sql'][:100]}...")
                print(f"Explanation: {result['explanation'][:150]}...")
            else:
                print_error(f"Query failed: {response.status_code}")
                
        except Exception as e:
            print_error(f"Query error: {str(e)}")
        
        time.sleep(1)


def demo_api_documentation():
    """Show API documentation links."""
    print_section("API Documentation")
    
    print_info("Interactive API documentation available at:")
    print(f"  {Colors.BOLD}Swagger UI:{Colors.RESET} {API_BASE}/docs")
    print(f"  {Colors.BOLD}ReDoc:{Colors.RESET} {API_BASE}/redoc")
    print()
    print_info("Database management:")
    print(f"  {Colors.BOLD}pgAdmin:{Colors.RESET} http://localhost:5050")
    print(f"    Login: admin@iot.com / admin123")


def main():
    """Main demonstration function."""
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}IoT Device Monitor - System Demonstration{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")
    
    # Check if API is running
    print_info("Checking API status...")
    if not check_api_health():
        print_error("API is not accessible!")
        print_info("Please start the application first:")
        print("  docker-compose up -d")
        sys.exit(1)
    
    print_success("API is running")
    time.sleep(1)
    
    # Run demonstrations
    try:
        # 1. Device Management
        devices = demo_device_management()
        time.sleep(2)
        
        # 2. Sensor Readings
        readings = demo_sensor_readings(devices)
        time.sleep(2)
        
        # 3. Critical Alert
        demo_critical_alert(devices)
        time.sleep(2)
        
        # 4. Statistics
        demo_device_statistics(devices)
        time.sleep(2)
        
        # 5. AI Queries
        demo_ai_queries()
        time.sleep(1)
        
        # 6. Documentation
        demo_api_documentation()
        
        # Summary
        print_section("Demonstration Complete")
        print_success("All features demonstrated successfully!")
        print_info("\nNext steps:")
        print("  1. Explore API at: http://localhost:8000/docs")
        print("  2. View data in pgAdmin: http://localhost:5050")
        print("  3. Run device simulator: python scripts/simulate_devices.py")
        print("  4. Run load tests: python scripts/load_test.py")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demonstration interrupted by user{Colors.RESET}")
    except Exception as e:
        print_error(f"Demonstration error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
