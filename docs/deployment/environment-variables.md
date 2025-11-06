# Environment Variables Reference

Complete reference for all environment variables used in Stumpf.works POS.

## Quick Start

Copy the example file and configure:

```bash
cp .env.example .env
nano .env
```

---

## Application Settings

### `APP_NAME`
- **Type:** String
- **Default:** `"Stumpf.works POS"`
- **Description:** Application name shown in logs and UI
- **Example:** `APP_NAME=My Store POS`

### `ENVIRONMENT`
- **Type:** String
- **Default:** `development`
- **Options:** `development`, `staging`, `production`
- **Description:** Current environment
- **Example:** `ENVIRONMENT=production`

### `DEBUG`
- **Type:** Boolean
- **Default:** `true`
- **Description:** Enable debug mode (disable in production!)
- **Example:** `DEBUG=false`

### `LOG_LEVEL`
- **Type:** String
- **Default:** `INFO`
- **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Description:** Logging verbosity level
- **Example:** `LOG_LEVEL=INFO`

---

## API Configuration

### `API_HOST`
- **Type:** String
- **Default:** `0.0.0.0`
- **Description:** API server bind address
- **Example:** `API_HOST=127.0.0.1`

### `API_PORT`
- **Type:** Integer
- **Default:** `8000`
- **Description:** API server port
- **Example:** `API_PORT=8000`

---

## Database

### `DATABASE_URL` ⚠️ **REQUIRED**
- **Type:** PostgreSQL DSN
- **Description:** PostgreSQL connection string
- **Format:** `postgresql+asyncpg://user:password@host:port/database`
- **Example:** `DATABASE_URL=postgresql+asyncpg://posuser:secret@localhost:5432/pos_db`
- **Production:** Use strong password, consider connection pooling

### `DB_POOL_SIZE`
- **Type:** Integer
- **Default:** `10`
- **Description:** SQLAlchemy connection pool size
- **Example:** `DB_POOL_SIZE=20`

### `DB_MAX_OVERFLOW`
- **Type:** Integer
- **Default:** `20`
- **Description:** Maximum overflow connections
- **Example:** `DB_MAX_OVERFLOW=30`

---

## Redis

### `REDIS_URL` ⚠️ **REQUIRED**
- **Type:** Redis DSN
- **Description:** Redis connection string
- **Format:** `redis://[:password]@host:port/db`
- **Example:** `REDIS_URL=redis://:mypassword@localhost:6379/0`
- **Production:** Always use password!

---

## Security

### `SECRET_KEY` ⚠️ **REQUIRED**
- **Type:** String
- **Description:** Secret key for JWT signing and encryption
- **Generation:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Example:** `SECRET_KEY=super-secret-key-minimum-32-chars-long`
- **⚠️ CRITICAL:** Change from default, keep secret!

### `ALGORITHM`
- **Type:** String
- **Default:** `HS256`
- **Description:** JWT signing algorithm
- **Example:** `ALGORITHM=HS256`

### `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Type:** Integer
- **Default:** `30`
- **Description:** JWT access token lifetime in minutes
- **Example:** `ACCESS_TOKEN_EXPIRE_MINUTES=60`

### `REFRESH_TOKEN_EXPIRE_DAYS`
- **Type:** Integer
- **Default:** `7`
- **Description:** JWT refresh token lifetime in days
- **Example:** `REFRESH_TOKEN_EXPIRE_DAYS=30`

---

## CORS (Cross-Origin Resource Sharing)

### `ALLOWED_ORIGINS`
- **Type:** Comma-separated list
- **Description:** Allowed frontend origins for CORS
- **Example:** `ALLOWED_ORIGINS=https://pos.example.com,https://app.example.com`
- **Development:** Set automatically to localhost
- **Production:** ⚠️ **Must be configured!**

---

## Rate Limiting

### `RATE_LIMIT_ENABLED`
- **Type:** Boolean
- **Default:** `true`
- **Description:** Enable rate limiting
- **Example:** `RATE_LIMIT_ENABLED=true`
- **Production:** Always enable!

### `RATE_LIMIT_PER_MINUTE`
- **Type:** Integer
- **Default:** `60`
- **Description:** Default requests per minute per IP/user
- **Example:** `RATE_LIMIT_PER_MINUTE=100`

---

## Error Tracking (Sentry)

### `SENTRY_DSN`
- **Type:** String
- **Optional:** Yes
- **Description:** Sentry DSN for error tracking
- **Example:** `SENTRY_DSN=https://xxx@sentry.io/123456`
- **Production:** Highly recommended!

### `SENTRY_ENVIRONMENT`
- **Type:** String
- **Default:** Uses `ENVIRONMENT`
- **Description:** Sentry environment name
- **Example:** `SENTRY_ENVIRONMENT=production`

### `SENTRY_TRACES_SAMPLE_RATE`
- **Type:** Float (0.0 - 1.0)
- **Default:** `0.1`
- **Description:** Percentage of transactions to trace
- **Example:** `SENTRY_TRACES_SAMPLE_RATE=0.2`

---

## TSE / Fiskaly Integration

### `TSE_ENABLED`
- **Type:** Boolean
- **Default:** `true`
- **Description:** Enable TSE (Technische Sicherheitseinrichtung) signing
- **Example:** `TSE_ENABLED=true`
- **Germany:** ⚠️ **Required for compliance!**

### `FISKALY_API_KEY`
- **Type:** String
- **Required if:** `TSE_ENABLED=true`
- **Description:** Fiskaly API key
- **Example:** `FISKALY_API_KEY=test_xxx`
- **Get from:** https://dashboard.fiskaly.com/

### `FISKALY_API_SECRET`
- **Type:** String
- **Required if:** `TSE_ENABLED=true`
- **Description:** Fiskaly API secret
- **Example:** `FISKALY_API_SECRET=secret_xxx`
- **⚠️ Keep secret!**

### `FISKALY_TSS_ID`
- **Type:** String
- **Optional:** Yes
- **Description:** Fiskaly TSS (Technical Security System) ID
- **Example:** `FISKALY_TSS_ID=tss-xxx-xxx`

---

## SumUp Integration

### `SUMUP_ENABLED`
- **Type:** Boolean
- **Default:** `false`
- **Description:** Enable SumUp payment integration
- **Example:** `SUMUP_ENABLED=true`

### `SUMUP_API_KEY`
- **Type:** String
- **Required if:** `SUMUP_ENABLED=true`
- **Description:** SumUp API key
- **Example:** `SUMUP_API_KEY=sup_sk_xxx`
- **Get from:** https://developer.sumup.com/

### `SUMUP_MERCHANT_CODE`
- **Type:** String
- **Required if:** `SUMUP_ENABLED=true`
- **Description:** SumUp merchant code
- **Example:** `SUMUP_MERCHANT_CODE=MXXX`

### `SUMUP_WEBHOOK_SECRET`
- **Type:** String
- **Optional:** Yes
- **Description:** Secret for webhook signature verification
- **Example:** `SUMUP_WEBHOOK_SECRET=whsec_xxx`

---

## Celery (Background Tasks)

### `CELERY_BROKER_URL`
- **Type:** Redis/RabbitMQ URL
- **Default:** Uses `REDIS_URL`
- **Description:** Celery message broker
- **Example:** `CELERY_BROKER_URL=redis://:password@localhost:6379/1`

### `CELERY_RESULT_BACKEND`
- **Type:** Redis/Database URL
- **Default:** Uses `REDIS_URL`
- **Description:** Celery result backend
- **Example:** `CELERY_RESULT_BACKEND=redis://:password@localhost:6379/2`

---

## File Storage

### `UPLOAD_DIR`
- **Type:** Path
- **Default:** `/app/uploads`
- **Description:** Directory for file uploads
- **Example:** `UPLOAD_DIR=/var/pos/uploads`

### `MAX_UPLOAD_SIZE`
- **Type:** Integer (bytes)
- **Default:** `10485760` (10MB)
- **Description:** Maximum file upload size
- **Example:** `MAX_UPLOAD_SIZE=52428800` (50MB)

### `EXPORT_DIR`
- **Type:** Path
- **Default:** `/app/exports`
- **Description:** Directory for DSFinV-K and other exports
- **Example:** `EXPORT_DIR=/var/pos/exports`

---

## Multi-Tenancy

### `TENANT_HEADER_NAME`
- **Type:** String
- **Default:** `X-Tenant-ID`
- **Description:** HTTP header for tenant identification
- **Example:** `TENANT_HEADER_NAME=X-Tenant-ID`

### `DEFAULT_TENANT_SCHEMA`
- **Type:** String
- **Default:** `public`
- **Description:** Default PostgreSQL schema
- **Example:** `DEFAULT_TENANT_SCHEMA=public`

---

## Feature Flags

### `OFFLINE_MODE_ENABLED`
- **Type:** Boolean
- **Default:** `true`
- **Description:** Enable offline mode in frontend
- **Example:** `OFFLINE_MODE_ENABLED=true`

---

## Compliance

### `GOBD_RETENTION_YEARS`
- **Type:** Integer
- **Default:** `10`
- **Description:** Data retention period for GoBD compliance
- **Example:** `GOBD_RETENTION_YEARS=10`
- **Germany:** ⚠️ **Legally required: 10 years**

---

## Environment File Template

### Development (`.env.development`)

```bash
# Application
APP_NAME=Stumpf.works POS
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# API
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pos_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Features
TSE_ENABLED=false
SUMUP_ENABLED=false
RATE_LIMIT_ENABLED=false
```

### Production (`.env.production`)

```bash
# Application
APP_NAME=Stumpf.works POS
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://posuser:STRONG_PASSWORD@localhost:5432/pos_production
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://:STRONG_REDIS_PASSWORD@localhost:6379/0

# Security
SECRET_KEY=GENERATED_SECRET_KEY_32_CHARS_MINIMUM
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=https://pos.yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Sentry
SENTRY_DSN=https://xxx@sentry.io/123456
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# TSE (Fiskaly)
TSE_ENABLED=true
FISKALY_API_KEY=your_api_key
FISKALY_API_SECRET=your_api_secret
FISKALY_TSS_ID=your_tss_id

# SumUp
SUMUP_ENABLED=true
SUMUP_API_KEY=your_sumup_key
SUMUP_MERCHANT_CODE=your_merchant_code
SUMUP_WEBHOOK_SECRET=your_webhook_secret

# Celery
CELERY_BROKER_URL=redis://:STRONG_REDIS_PASSWORD@localhost:6379/1
CELERY_RESULT_BACKEND=redis://:STRONG_REDIS_PASSWORD@localhost:6379/2

# Storage
UPLOAD_DIR=/var/pos/uploads
EXPORT_DIR=/var/pos/exports

# Compliance
GOBD_RETENTION_YEARS=10
```

---

## Security Best Practices

### ⚠️ Critical

1. **Never commit `.env` files to version control**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use strong passwords**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

3. **Restrict file permissions**
   ```bash
   chmod 600 .env
   chown posapp:posapp .env
   ```

4. **Use secrets management in production**
   - Consider: Vault, AWS Secrets Manager, etc.

5. **Rotate secrets regularly**
   - SECRET_KEY: Every 90 days
   - Database passwords: Every 180 days
   - API keys: As per provider recommendations

---

## Validation

Check your environment variables:

```bash
# Load .env and validate
cd backend
source venv/bin/activate
python -c "from app.core.config import settings; print(settings)"
```

---

## Troubleshooting

### "SECRET_KEY not set"
```bash
# Generate and add to .env
python -c "import secrets; print(f'SECRET_KEY={secrets.token_urlsafe(32)}')" >> .env
```

### "Database connection failed"
```bash
# Test connection
psql -U posuser -d pos_production -c "SELECT version();"
```

### "Redis connection error"
```bash
# Test Redis
redis-cli -a YOUR_PASSWORD ping
```

---

For deployment help, see [Production Deployment Guide](./production.md)
