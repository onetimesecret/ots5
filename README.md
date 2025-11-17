# OneTimeSecret Python3 Community Edition

A modern Python3 implementation of OneTimeSecret, providing secure one-time message sharing with automatic link expiration after viewing. Built following Python community standards and conventions for maintainability, security, and extensibility.

## Features

- **One-time viewing**: Secrets automatically expire after first access
- **Time-based expiration**: Optional TTL for unviewed secrets
- **Passphrase protection**: Optional encryption layer for additional security
- **RESTful API**: Compatible with OneTimeSecret v2 specification
- **Redis backend**: Fast and reliable storage with automatic expiration
- **Type safety**: Full type hints throughout the codebase
- **Comprehensive testing**: Unit and integration tests with >80% coverage
- **Docker support**: Easy deployment with Docker and Docker Compose

## Technical Specifications

- **Python**: 3.10+
- **Framework**: FastAPI for REST API
- **Database**: Redis (primary storage for secrets)
- **Encryption**: Fernet symmetric encryption with optional passphrase-based key derivation
- **API**: RESTful JSON API maintaining compatibility with OneTimeSecret v2 specification

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/onetimesecret/onetimesecret-python
cd onetimesecret-python
```

2. Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and set OTS_SECRET_KEY to your generated key
```

4. Start the services:
```bash
docker-compose up -d
```

5. Access the API:
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v2/status

### Manual Installation

#### Prerequisites
- Python 3.10 or higher
- Redis server
- Virtual environment tool (venv/virtualenv)

#### Setup Steps

1. Clone and navigate to the repository:
```bash
git clone https://github.com/onetimesecret/onetimesecret-python
cd onetimesecret-python
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements/base.txt
# For development:
# pip install -r requirements/dev.txt
```

4. Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

5. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration, especially OTS_SECRET_KEY
```

6. Start Redis (if not already running):
```bash
redis-server
```

7. Start the development server:
```bash
uvicorn onetimesecret.main:app --reload
```

The API will be available at http://localhost:8000

## Configuration

Configuration is managed through environment variables with the `OTS_` prefix. See `.env.example` for all available options.

### Key Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `OTS_REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `OTS_SECRET_KEY` | *Required* | Application secret key (generate a secure random key) |
| `OTS_SSL_ENABLED` | `false` | Enable SSL/TLS enforcement |
| `OTS_AUTH_REQUIRED` | `false` | Require authentication for API access |
| `OTS_PASSPHRASE_REQUIRED` | `false` | Require passphrase for all secrets |
| `OTS_MAX_SECRET_SIZE` | `1048576` | Maximum secret size in bytes (1MB) |
| `OTS_DEFAULT_TTL` | `604800` | Default TTL in seconds (7 days) |
| `OTS_MAX_TTL` | `2592000` | Maximum TTL in seconds (30 days) |

## API Usage

### Create a Secret

```bash
curl -X POST http://localhost:8000/api/v2/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "This is my secret message",
    "ttl": 3600
  }'
```

Response:
```json
{
  "secret_key": "abc123def456",
  "metadata_key": "abc123def456:metadata",
  "ttl": 3600,
  "created_at": "2023-01-01T00:00:00"
}
```

### Create a Passphrase-Protected Secret

```bash
curl -X POST http://localhost:8000/api/v2/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "Protected secret",
    "passphrase": "my_secure_password",
    "ttl": 7200
  }'
```

### Retrieve a Secret

Using GET:
```bash
curl http://localhost:8000/api/v2/secrets/abc123def456
```

Using POST with passphrase:
```bash
curl -X POST http://localhost:8000/api/v2/secrets/abc123def456 \
  -H "Content-Type: application/json" \
  -d '{"passphrase": "my_secure_password"}'
```

Response:
```json
{
  "secret": "This is my secret message",
  "created_at": "2023-01-01T00:00:00"
}
```

### Get Secret Metadata

```bash
curl http://localhost:8000/api/v2/secrets/abc123def456/metadata
```

Response:
```json
{
  "secret_key": "abc123def456",
  "created_at": "2023-01-01T00:00:00",
  "ttl": 3600,
  "viewed": false,
  "has_passphrase": true
}
```

### Delete a Secret

```bash
curl -X DELETE http://localhost:8000/api/v2/secrets/abc123def456
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements/dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=onetimesecret --cov-report=html

# Run only unit tests
pytest tests/unit -m unit

# Run only integration tests
pytest tests/integration -m integration
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/
```

### Project Structure

```
onetimesecret/
├── src/
│   └── onetimesecret/
│       ├── __init__.py
│       ├── main.py              # FastAPI application entry point
│       ├── api/
│       │   ├── routes.py        # API endpoints
│       │   └── validators.py    # Input validation
│       ├── core/
│       │   ├── config.py        # Configuration management
│       │   ├── exceptions.py    # Custom exceptions
│       │   └── security.py      # Security utilities
│       ├── models/
│       │   └── secret.py        # Pydantic models
│       ├── services/
│       │   ├── redis_client.py  # Redis storage client
│       │   └── secret_service.py # Business logic
│       └── utils/
│           └── crypto.py        # Cryptographic utilities
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── conftest.py              # Pytest fixtures
├── requirements/
│   ├── base.txt                 # Production dependencies
│   ├── dev.txt                  # Development dependencies
│   └── prod.txt                 # Production + deployment tools
├── pyproject.toml               # Project metadata and tool config
├── setup.cfg                    # Additional tool configuration
├── Dockerfile                   # Container image definition
├── docker-compose.yml           # Local development stack
└── README.md                    # This file
```

## Security Considerations

### Encryption

- All secrets are encrypted using Fernet (symmetric encryption)
- Optional passphrase protection adds an additional encryption layer using PBKDF2
- Secrets are never stored in plaintext
- Cryptographically secure random key generation

### Best Practices

1. **Generate a Strong Secret Key**: Use the provided command to generate a cryptographically secure key
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use Environment Variables**: Never commit secrets to version control

3. **Enable SSL/TLS in Production**: Set `OTS_SSL_ENABLED=true` and use HTTPS

4. **Set Appropriate TTLs**: Configure reasonable default and maximum TTL values

5. **Monitor Access**: Implement logging and monitoring for production deployments

6. **Regular Updates**: Keep dependencies updated for security patches

## Production Deployment

### Docker

Build and run the container:
```bash
docker build -t onetimesecret:latest .
docker run -d \
  -p 8000:8000 \
  -e OTS_REDIS_URL=redis://your-redis:6379/0 \
  -e OTS_SECRET_KEY=your-secure-key \
  -e OTS_SSL_ENABLED=true \
  onetimesecret:latest
```

### Using Gunicorn

For production deployments with multiple workers:
```bash
pip install -r requirements/prod.txt
gunicorn onetimesecret.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## API Documentation

Once the server is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code follows PEP 8 style guidelines
- Type hints are included
- Documentation is updated
- Test coverage remains >80%

## Support

For issues and questions:
- GitHub Issues: https://github.com/onetimesecret/onetimesecret-python/issues
- Documentation: https://github.com/onetimesecret/onetimesecret-python

## Acknowledgments

Based on the original OneTimeSecret project: https://github.com/onetimesecret/onetimesecret
