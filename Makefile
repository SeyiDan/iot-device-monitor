.PHONY: help install dev test build up down logs clean seed

help:
	@echo "IoT Fleet Monitor - Available Commands"
	@echo "======================================"
	@echo "install     - Install Python dependencies"
	@echo "dev         - Run development server locally"
	@echo "test        - Run pytest test suite"
	@echo "build       - Build Docker image"
	@echo "up          - Start all services with Docker Compose"
	@echo "down        - Stop all services"
	@echo "logs        - Show Docker logs"
	@echo "seed        - Seed database with test data"
	@echo "clean       - Clean up Python cache files"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

build:
	docker build -t iot-fleet-monitor:latest .

up:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "📚 API Docs: http://localhost:8000/docs"
	@echo "🗄️  PGAdmin: http://localhost:5050"

down:
	docker-compose down

logs:
	docker-compose logs -f

seed:
	python scripts/seed_database.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage
