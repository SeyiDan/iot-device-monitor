# PowerShell script to start the IoT Device Monitor system
# Usage: .\start.ps1

Write-Host "IoT Device Monitor - Starting System" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Docker is running" -ForegroundColor Green

# Start services
Write-Host "Starting Docker Compose services..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] All services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access Points:" -ForegroundColor Cyan
    Write-Host "  - API Docs:  http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  - API:       http://localhost:8000" -ForegroundColor White
    Write-Host "  - PGAdmin:   http://localhost:5050" -ForegroundColor White
    Write-Host "    (Login: admin@iot.com / admin123)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Useful Commands:" -ForegroundColor Cyan
    Write-Host "  - View logs:    docker-compose logs -f" -ForegroundColor White
    Write-Host "  - Stop system:  docker-compose down" -ForegroundColor White
    Write-Host "  - Seed data:    python scripts/seed_database.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Failed to start services. Check the error messages above." -ForegroundColor Red
    exit 1
}
