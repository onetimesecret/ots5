.PHONY: help install dev-install test lint format clean run docker-build docker-up docker-down migrate

help:
	@echo "OneTimeSecret - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install production dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Run development server"
	@echo "  make test          - Run test suite"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code with black and isort"
	@echo "  make type-check    - Run type checking with mypy"
	@echo "  make security      - Run security checks with bandit"
	@echo ""
	@echo "Database:"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migration     - Create new migration"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - View Docker logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove build artifacts"

install:
	pip install -r requirements/base.txt

dev-install:
	pip install -r requirements/dev.txt
	pre-commit install

run:
	uvicorn onetimesecret.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

test-cov:
	pytest --cov=src/onetimesecret --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/onetimesecret

security:
	bandit -r src/ -f json -o bandit-report.json
	@echo "Security report generated: bandit-report.json"

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info
