"""
Script to test the API endpoints after deployment.
Runs a series of tests to verify the system is working correctly.

Usage:
    python scripts/test_api.py
"""

import requests
import sys
from datetime import datetime

API_BASE = "http://localhost:8000"


def print_status(test_name, success, message=""):
    """Print test status with color"""
    status = "[OK]" if success else "[FAIL]"
    color = "\033[92m" if success else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {test_name}", end="")
    if message:
        print(f": {message}")
    else:
        print()


def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{API_BASE}/health")
        success = response.status_code == 200
        print_status("Health Check", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_status("Health Check", False, str(e))
        return False


def test_create_device():
    """Test device creation"""
    try:
        payload = {
            "name": "Test Sensor",
            "location": "Test Lab",
            "is_active": True
        }
        response = requests.post(f"{API_BASE}/api/v1/devices", json=payload)
        success = response.status_code == 201
        
        if success:
            device_id = response.json()["id"]
            print_status("Create Device", success, f"Device ID: {device_id}")
            return device_id
        else:
            print_status("Create Device", success, f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_status("Create Device", False, str(e))
        return None


def test_create_reading(device_id):
    """Test reading creation"""
    try:
        payload = {
            "device_id": device_id,
            "temperature": 25.5,
            "humidity": 60.0,
            "battery_level": 85.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = requests.post(f"{API_BASE}/api/v1/readings", json=payload)
        success = response.status_code == 201
        
        if success:
            reading_id = response.json()["id"]
            print_status("Create Reading", success, f"Reading ID: {reading_id}")
            return reading_id
        else:
            print_status("Create Reading", success, f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_status("Create Reading", False, str(e))
        return None


def test_create_critical_reading(device_id):
    """Test critical temperature alert"""
    try:
        payload = {
            "device_id": device_id,
            "temperature": 95.0,  # Critical temperature
            "humidity": 45.0,
            "battery_level": 80.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = requests.post(f"{API_BASE}/api/v1/readings", json=payload)
        success = response.status_code == 201
        print_status("Critical Alert Test", success, "Check logs for alert")
        return success
    except Exception as e:
        print_status("Critical Alert Test", False, str(e))
        return False


def test_device_not_found():
    """Test 404 error handling"""
    try:
        payload = {
            "device_id": 99999,
            "temperature": 25.0,
            "humidity": 60.0,
            "battery_level": 85.0
        }
        response = requests.post(f"{API_BASE}/api/v1/readings", json=payload)
        success = response.status_code == 404
        print_status("404 Error Handling", success, "Device not found")
        return success
    except Exception as e:
        print_status("404 Error Handling", False, str(e))
        return False


def test_validation_error():
    """Test input validation"""
    try:
        payload = {
            "device_id": 1,
            "temperature": 200.0,  # Invalid: exceeds max
            "humidity": 60.0,
            "battery_level": 85.0
        }
        response = requests.post(f"{API_BASE}/api/v1/readings", json=payload)
        success = response.status_code == 422
        print_status("Input Validation", success, "Validation error")
        return success
    except Exception as e:
        print_status("Input Validation", False, str(e))
        return False


def test_get_device_readings(device_id):
    """Test getting device readings"""
    try:
        response = requests.get(f"{API_BASE}/api/v1/devices/{device_id}/readings")
        success = response.status_code == 200
        
        if success:
            count = len(response.json())
            print_status("Get Device Readings", success, f"Found {count} readings")
        else:
            print_status("Get Device Readings", success, f"Status: {response.status_code}")
        
        return success
    except Exception as e:
        print_status("Get Device Readings", False, str(e))
        return False


def main():
    """Run all tests"""
    print("\nIoT Device Monitor - API Tests")
    print("=" * 50)
    print()
    
    # Check if API is accessible
    if not test_health_check():
        print("\n[ERROR] API is not accessible. Make sure the server is running.")
        print("   Run: docker-compose up -d")
        sys.exit(1)
    
    print()
    
    # Run test sequence
    device_id = test_create_device()
    if device_id:
        test_create_reading(device_id)
        test_create_critical_reading(device_id)
        test_get_device_readings(device_id)
    
    print()
    
    # Test error handling
    test_device_not_found()
    test_validation_error()
    
    print()
    print("=" * 50)
    print("Test suite completed!")
    print()
    print("View full API docs at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
