# OneTimeSecret - Modern Python3 Implementation

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modern, secure, and community-driven Python3 rebuild of [OneTimeSecret](https://github.com/onetimesecret/onetimesecret) - the trusted service for sharing sensitive information that self-destructs after being read.

## Features

- **Secure by Design**: Fernet symmetric encryption (AES-128-CBC with HMAC)
- **Self-Destructing**: Secrets automatically deleted after first view
- **Passphrase Protection**: Optional additional layer of security
- **Time-Limited**: Configurable TTL from 5 minutes to 3 days
- **Modern Stack**: FastAPI, PostgreSQL, Redis, async-first architecture
- **RESTful API**: Full REST API with OpenAPI/Swagger documentation
- **Type-Safe**: 100% type-hinted Python code
- **Well-Tested**: Comprehensive test suite with >90% coverage
- **Production-Ready**: Docker deployment, rate limiting, CORS, security headers

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/onetimesecret/ots5.git
cd ots5

# Copy environment file and configure
cp .env.example .env
# Edit .env and set a secure SECRET_KEY (generate with: openssl rand -hex 32)

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

### Manual Installation

**Requirements:**
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn onetimesecret.main:app --reload
```

## Usage

### Creating a Secret

```bash
curl -X POST http://localhost:8000/api/v3/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "This is my secret message!",
    "ttl": 3600,
    "burn_after_reading": true
  }'
```

Response:
```json
{
  "secret_id": "abc123xyz",
  "metadata_key": "meta_def456uvw",
  "expires_at": "2024-01-01T12:00:00Z",
  "ttl": 3600,
  "burn_after_reading": true,
  "created_at": "2024-01-01T11:00:00Z"
}
```

### Retrieving a Secret

```bash
curl -X POST http://localhost:8000/api/v3/secrets/abc123xyz
```

Response:
```json
{
  "secret_id": "abc123xyz",
  "secret": "This is my secret message!",
  "burn_after_reading": true
}
```

### Creating a Passphrase-Protected Secret

```bash
curl -X POST http://localhost:8000/api/v3/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "Highly sensitive data",
    "passphrase": "my-secure-passphrase",
    "ttl": 86400
  }'
```

Retrieve with passphrase:
```bash
curl -X POST http://localhost:8000/api/v3/secrets/abc123xyz \
  -H "Content-Type: application/json" \
  -d '{"passphrase": "my-secure-passphrase"}'
```

## API Documentation

Full API documentation is available at `/docs` when running in development mode.

### Endpoints

- `POST /api/v3/secrets` - Create a new secret
- `POST /api/v3/secrets/{secret_id}` - Retrieve a secret
- `GET /api/v3/secrets/{secret_id}/metadata` - Get secret metadata (doesn't burn)
- `DELETE /api/v3/secrets/{secret_id}` - Delete a secret
- `GET /api/v3/health` - Health check

## Development

### Setup Development Environment

```bash
# Install development dependencies
make dev-install

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Run linters
make lint

# Type checking
make type-check

# Security scanning
make security
```

### Project Structure

```
onetimesecret/
├── src/onetimesecret/
│   ├── api/           # API endpoints and routing
│   ├── core/          # Business logic and schemas
│   ├── crypto/        # Cryptographic operations
│   ├── db/            # Database models and connection
│   ├── services/      # External service integrations
│   └── utils/         # Shared utilities
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## Security

### Security Features

- **Encryption**: Fernet (AES-128-CBC + HMAC) with PBKDF2 key derivation
- **Secure Tokens**: Cryptographically secure random token generation
- **Rate Limiting**: Configurable rate limits per IP
- **Input Validation**: Pydantic schema validation
- **Security Headers**: HSTS, X-Frame-Options, CSP, etc.
- **No Logging**: Secrets never logged or exposed in logs
- **Constant-Time Comparison**: Prevents timing attacks

### Reporting Security Issues

Please report security vulnerabilities to security@onetimesecret.com

DO NOT create public GitHub issues for security problems.

## Configuration

All configuration is done via environment variables. See `.env.example` for all available options.

### Critical Settings

```bash
# REQUIRED: Generate with: openssl rand -hex 32
SECRET_KEY=your-secure-random-key-here

# REQUIRED in production
SSL_ENABLED=true

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0
```

## Deployment

### Docker Production Deployment

```bash
# Build production image
docker build -t onetimesecret:latest .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY=your-key \
  -e DATABASE_URL=your-db-url \
  -e REDIS_URL=your-redis-url \
  -e ENVIRONMENT=production \
  -e SSL_ENABLED=true \
  onetimesecret:latest
```

### Production Checklist

- [ ] Set a strong `SECRET_KEY` (minimum 32 characters)
- [ ] Enable SSL/TLS (`SSL_ENABLED=true`)
- [ ] Use production database (PostgreSQL)
- [ ] Configure Redis for caching
- [ ] Set up rate limiting
- [ ] Configure CORS origins
- [ ] Disable debug mode (`DEBUG=false`)
- [ ] Set up monitoring and logging
- [ ] Configure backups for database
- [ ] Review security headers
- [ ] Set appropriate TTL limits

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/onetimesecret --cov-report=html

# Run specific test file
pytest tests/unit/test_crypto.py

# Run with verbose output
pytest -v
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters (`make test lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original [OneTimeSecret](https://github.com/onetimesecret/onetimesecret) by Delano Mandelbaum
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Encryption by [cryptography](https://cryptography.io/)

## Support

- **Issues**: [GitHub Issues](https://github.com/onetimesecret/ots5/issues)
- **Discussions**: [GitHub Discussions](https://github.com/onetimesecret/ots5/discussions)
- **Email**: support@onetimesecret.com

## Roadmap

- [x] Core secret encryption and storage
- [x] RESTful API with FastAPI
- [x] Passphrase protection
- [x] Docker deployment
- [x] Comprehensive test suite
- [ ] User accounts and API keys
- [ ] Email notifications
- [ ] Rate limiting per user
- [ ] Web UI (separate project)
- [ ] Client libraries (Python, JavaScript, Go)
- [ ] Kubernetes deployment manifests
- [ ] Metrics and monitoring integration

---

**Made with ❤️ by the OneTimeSecret community**
