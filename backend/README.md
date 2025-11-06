# Stumpf.works POS - Backend

FastAPI-based backend for the Stumpf.works POS system with multi-tenant support.

## Architecture

### Core Components

- **FastAPI**: Modern async web framework
- **SQLAlchemy 2.0**: ORM with async support
- **PostgreSQL**: Database with schema-per-tenant isolation
- **Redis**: Caching and message broker
- **Celery**: Background task processing
- **Pydantic**: Data validation and settings management

### Directory Structure

```
app/
├── core/           # Core configuration, database, security
├── api/            # API endpoints (routers)
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── middleware/     # Custom middleware
├── plugins/        # Plugin system
└── utils/          # Helper functions
```

## Multi-Tenant Architecture

The system uses PostgreSQL schemas for tenant isolation:

- Each tenant gets its own database schema
- Tenant identified via `X-Tenant-ID` header or subdomain
- TenantMiddleware sets the search_path for each request
- Migrations are run per tenant schema

### Tenant Identification

**Method 1: HTTP Header**
```bash
curl -H "X-Tenant-ID: acme-corp" http://localhost:8000/api/v1/products
```

**Method 2: Subdomain (if enabled)**
```bash
curl http://acme-corp.stumpf.works/api/v1/products
```

## Setup & Development

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example ../.env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Running with Docker

```bash
# From project root
docker-compose up backend
```

## Database Migrations

Using Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current
```

### Multi-Tenant Migrations

When a new tenant is onboarded:

1. Create schema: `CREATE SCHEMA tenant_name`
2. Run migrations in that schema
3. Set up tenant configuration

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
pylint app/
```

## Background Tasks (Celery)

### Start Celery Worker

```bash
celery -A app.core.celery_app worker --loglevel=info
```

### Start Celery Beat (Scheduled Tasks)

```bash
celery -A app.core.celery_app beat --loglevel=info
```

### Monitor with Flower

```bash
celery -A app.core.celery_app flower
# Visit http://localhost:5555
```

## Plugin System

The backend supports a plugin architecture for easy extensibility:

```python
# Example plugin structure
plugins/
├── my_plugin/
│   ├── __init__.py
│   ├── models.py      # Database models
│   ├── schemas.py     # API schemas
│   ├── routes.py      # API endpoints
│   ├── services.py    # Business logic
│   └── migrations/    # Database migrations
```

Plugins are automatically discovered and loaded at startup.

## Security

### Authentication

- OAuth2 with JWT tokens
- Access tokens (30 min expiry)
- Refresh tokens (7 day expiry)
- Password hashing with bcrypt

### Authorization

- Role-based access control (RBAC)
- Tenant-scoped permissions
- User permissions per tenant

## Integrations

### SumUp Payment

```python
from app.services.payment import SumUpService

sumup = SumUpService(tenant_id="acme-corp")
payment = await sumup.create_checkout(amount=10.00, currency="EUR")
```

### Cloud-TSE (Fiskaly)

```python
from app.services.tse import TSEService

tse = TSEService(tenant_id="acme-corp")
signature = await tse.sign_transaction(transaction_data)
```

## Environment Variables

See `.env.example` for all configuration options.

Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key (min 32 chars)
- `SUMUP_CLIENT_ID`: SumUp API credentials
- `FISKALY_API_KEY`: Fiskaly TSE credentials

## Logging

Structured JSON logging with `structlog`:

```python
import structlog

logger = structlog.get_logger()
logger.info("user_created", user_id=123, tenant_id="acme")
```

Logs include:
- Request ID for tracing
- Tenant ID
- Timestamp
- Log level
- Contextual data

## Troubleshooting

### Database connection errors

Check PostgreSQL is running and credentials are correct:
```bash
psql $DATABASE_URL
```

### Redis connection errors

Check Redis is running:
```bash
redis-cli ping
```

### Import errors

Ensure virtual environment is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to functions
3. Write tests for new features
4. Update documentation
5. Run code quality checks before committing

## License

MIT License - see LICENSE file
