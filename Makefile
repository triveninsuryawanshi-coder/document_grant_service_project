.PHONY: help install dev db-up db-down migrate seed run test lint format clean

help:
	@echo "Document Grant Service - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Install dev dependencies"
	@echo "  make db-up         - Start PostgreSQL with Docker"
	@echo "  make db-down       - Stop PostgreSQL"
	@echo ""
	@echo "Database:"
	@echo "  make migrate       - Run Alembic migrations"
	@echo "  make seed          - Seed database with sample data"
	@echo "  make db-reset      - Drop and recreate all tables"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Start FastAPI server"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-int      - Run integration tests only"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code with black and isort"
	@echo "  make clean         - Remove build artifacts"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

db-up:
	docker-compose up -d

db-down:
	docker-compose down

db-down-v:
	docker-compose down -v

migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

seed:
	python -m app.seed

db-reset: db-down db-up
	sleep 5
	alembic upgrade head
	python -m app.seed

run:
	uvicorn app.main:app --reload

test:
	pytest --cov=app --cov-report=term-missing

test-unit:
	pytest tests/test_services.py -v

test-int:
	pytest tests/test_endpoints.py -v

lint:
	python -m flake8 app tests
	python -m black --check app tests

format:
	black app tests
	isort app tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf dist/ build/
