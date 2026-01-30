# IoT Fleet Monitor

A high-performance IoT device monitoring system built with FastAPI for managing sensor data ingestion and device state management.

## Overview

This application provides RESTful APIs for ingesting high-frequency sensor data from IoT devices, storing device information, and monitoring critical conditions in real-time using background tasks.

## Features

- High-frequency sensor data ingestion with async/await optimization
- PostgreSQL database with SQLAlchemy 2.0 ORM
- Pydantic v2 data validation
- Background task processing for critical condition monitoring
- Docker containerization for easy deployment
- Comprehensive test suite with pytest
- CI/CD pipeline with GitHub Actions

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-asyncio
- **Deployment**: Docker, Docker Compose

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Python 3.11+ (for local development)
- Git

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd iot-fleet-monitor
```

2. Start the services:
```bash
# Windows
.\start.ps1

# Linux/Mac
docker-compose up -d
```

3. Access the application:
- API Documentation: http://localhost:8000/docs
- API: http://localhost:8000
- PGAdmin: http://localhost:5050 (admin@iot.com / admin123)

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Device Management

- `POST /api/v1/devices` - Create a new device
- `GET /api/v1/devices` - List all devices
- `GET /api/v1/devices/{id}` - Get device by ID
- `PUT /api/v1/devices/{id}` - Update device
- `DELETE /api/v1/devices/{id}` - Delete device

### Sensor Readings

- `POST /api/v1/readings` - Submit sensor reading
- `GET /api/v1/readings/{id}` - Get reading by ID
- `GET /api/v1/devices/{device_id}/readings` - Get all readings for a device

### System

- `GET /` - Root endpoint
- `GET /health` - Health check

## Database Schema

### Devices Table

| Column    | Type    | Description                |
|-----------|---------|----------------------------|
| id        | Integer | Primary key                |
| name      | String  | Device name                |
| location  | String  | Device location            |
| is_active | Boolean | Device activation status   |

### Readings Table

| Column    | Type     | Description                    |
|-----------|----------|--------------------------------|
| id        | Integer  | Primary key                    |
| device_id | Integer  | Foreign key to devices table   |
| values    | JSON     | Sensor values (temp, humidity) |
| timestamp | DateTime | Reading timestamp              |

**Relationship**: One Device has Many Readings (One-to-Many)

## Example Usage

### Create a Device

```bash
curl -X POST "http://localhost:8000/api/v1/devices" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Temperature Sensor 01",
    "location": "Building A",
    "is_active": true
  }'
```

### Submit a Reading

```bash
curl -X POST "http://localhost:8000/api/v1/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "temperature": 25.5,
    "humidity": 60.0,
    "battery_level": 85.0,
    "timestamp": "2024-01-15T10:30:00"
  }'
```

## Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

### Integration Tests

```bash
python scripts/test_api.py
```

### Load Testing

```bash
python scripts/load_test.py --devices 10 --readings 100
```

## Database Management

### Seed Test Data

```bash
python scripts/seed_database.py
```

### Access PGAdmin

1. Navigate to http://localhost:5050
2. Login with admin@iot.com / admin123
3. Add server connection:
   - Host: postgres
   - Port: 5432
   - Database: iot_monitor
   - Username: iot_user
   - Password: iot_pass

## Configuration

Environment variables can be configured in `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://iot_user:iot_pass@postgres:5432/iot_monitor
DATABASE_URL_SYNC=postgresql://iot_user:iot_pass@postgres:5432/iot_monitor
CRITICAL_TEMP_THRESHOLD=80.0
```

## Deployment

For production deployment on Ubuntu/Linux servers, see [DEPLOYMENT.md](DEPLOYMENT.md).

## CI/CD

The project includes a GitHub Actions workflow that:
- Runs pytest on every push
- Builds Docker images
- Runs linting checks

## Project Structure

```
iot-fleet-monitor/
├── app/
│   ├── api/v1/endpoints/    # API route handlers
│   ├── core/                 # Configuration
│   ├── database.py           # Database connection
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   └── main.py               # FastAPI application
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
├── .github/workflows/        # CI/CD configuration
├── Dockerfile                # Container definition
├── docker-compose.yml        # Multi-container setup
└── requirements.txt          # Python dependencies
```

## Performance Considerations

- Async database operations throughout
- Connection pooling (pool_size=10, max_overflow=20)
- Background tasks for non-blocking operations
- Indexed database columns for fast queries
- Multiple Uvicorn workers in production

## Security

- Non-root user in Docker containers
- Environment-based configuration
- SQL injection protection via ORM
- Input validation with Pydantic
- Password protection for database access

## Monitoring

The application includes:
- Health check endpoint at `/health`
- Structured logging
- Critical condition monitoring
- Docker health checks

## Troubleshooting

### Port Already in Use

If port 5432 is occupied, the docker-compose.yml is configured to use port 5433.

### Docker Connection Issues

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f api

# Restart services
docker-compose restart
```

### Database Connection Failed

```bash
# Verify PostgreSQL is running
docker-compose logs postgres

# Check database connection
docker exec -it iot_postgres psql -U iot_user -d iot_monitor
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
