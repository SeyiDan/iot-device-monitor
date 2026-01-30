import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.database import get_db
from app.models import Device, Reading


# Mock database session fixture
@pytest.fixture
def mock_db_session():
    """Create a mock async database session"""
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


# Test client fixture with overridden dependency
@pytest.fixture
def client(mock_db_session):
    """Create test client with mocked database"""
    
    async def override_get_db():
        yield mock_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestReadingsAPI:
    """Test suite for readings API endpoints"""
    
    def test_create_reading_device_not_found(self, client, mock_db_session):
        """Test that API returns 404 when device doesn't exist"""
        
        # Setup mock to return None (device not found)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Prepare test data
        reading_data = {
            "device_id": 999,  # Non-existent device
            "temperature": 25.5,
            "humidity": 60.0,
            "battery_level": 85.0,
            "timestamp": "2024-01-15T10:30:00"
        }
        
        # Make request
        response = client.post("/api/v1/readings", json=reading_data)
        
        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        assert "999" in response.json()["detail"]
    
    def test_create_reading_device_inactive(self, client, mock_db_session):
        """Test that API returns 400 when device is inactive"""
        
        # Setup mock to return inactive device
        mock_device = Device(
            id=1,
            name="Test Device",
            location="Lab A",
            is_active=False
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_device
        mock_db_session.execute.return_value = mock_result
        
        # Prepare test data
        reading_data = {
            "device_id": 1,
            "temperature": 25.5,
            "humidity": 60.0,
            "battery_level": 85.0,
            "timestamp": "2024-01-15T10:30:00"
        }
        
        # Make request
        response = client.post("/api/v1/readings", json=reading_data)
        
        # Assertions
        assert response.status_code == 400
        assert "not active" in response.json()["detail"].lower()
    
    def test_create_reading_success(self, client, mock_db_session):
        """Test successful reading creation"""
        
        # Setup mocks
        mock_device = Device(
            id=1,
            name="Test Device",
            location="Lab A",
            is_active=True
        )
        
        # Mock device query
        mock_device_result = MagicMock()
        mock_device_result.scalar_one_or_none.return_value = mock_device
        
        # Configure execute to return device result
        mock_db_session.execute.return_value = mock_device_result
        
        # Mock reading creation
        mock_reading = Reading(
            id=1,
            device_id=1,
            values={
                "temperature": 25.5,
                "humidity": 60.0,
                "battery_level": 85.0
            },
            timestamp=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        # Mock refresh to set the reading attributes
        async def mock_refresh(obj):
            obj.id = 1
            obj.device_id = 1
            obj.values = {
                "temperature": 25.5,
                "humidity": 60.0,
                "battery_level": 85.0
            }
            obj.timestamp = datetime(2024, 1, 15, 10, 30, 0)
        
        mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
        mock_db_session.commit = AsyncMock()
        
        # Prepare test data
        reading_data = {
            "device_id": 1,
            "temperature": 25.5,
            "humidity": 60.0,
            "battery_level": 85.0,
            "timestamp": "2024-01-15T10:30:00"
        }
        
        # Make request
        response = client.post("/api/v1/readings", json=reading_data)
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["device_id"] == 1
        assert data["values"]["temperature"] == 25.5
        assert data["values"]["humidity"] == 60.0
        assert data["values"]["battery_level"] == 85.0
    
    def test_create_reading_validation_error(self, client, mock_db_session):
        """Test that API validates input data correctly"""
        
        # Invalid temperature (out of range)
        invalid_data = {
            "device_id": 1,
            "temperature": 200.0,  # Exceeds max of 150
            "humidity": 60.0,
            "battery_level": 85.0
        }
        
        response = client.post("/api/v1/readings", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_reading_missing_fields(self, client, mock_db_session):
        """Test that API requires all mandatory fields"""
        
        # Missing humidity field
        incomplete_data = {
            "device_id": 1,
            "temperature": 25.5,
            "battery_level": 85.0
        }
        
        response = client.post("/api/v1/readings", json=incomplete_data)
        assert response.status_code == 422


# Run tests with: pytest tests/test_readings.py -v
