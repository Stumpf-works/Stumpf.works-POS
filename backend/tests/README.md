# Backend Tests

Comprehensive test suite for the Stumpf.works POS backend.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_auth.py             # Authentication tests
├── test_products.py         # Product management tests
├── test_transactions.py     # Transaction processing tests
├── test_admin.py            # Admin dashboard tests
├── test_exports.py          # Export functionality tests
└── test_tse_service.py      # TSE/Fiskaly integration tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run specific test class
```bash
pytest tests/test_auth.py::TestAuthentication
```

### Run specific test
```bash
pytest tests/test_auth.py::TestAuthentication::test_login_with_password
```

### Run tests with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run tests matching a pattern
```bash
pytest -k "transaction"
```

### Run tests with specific markers
```bash
pytest -m auth          # Only auth tests
pytest -m "not slow"    # Skip slow tests
```

## Test Database

Tests use a separate test database: `pos_test`

Before running tests, ensure PostgreSQL is running and create the test database:

```bash
createdb pos_test
```

The test database is automatically created and torn down for each test.

## Fixtures

Common fixtures available in `conftest.py`:

- `db_session` - Test database session
- `client` - HTTP test client
- `test_tenant` - Test tenant/organization
- `test_admin_user` - Test admin user
- `test_cashier_user` - Test cashier user
- `admin_token` - Admin JWT token
- `cashier_token` - Cashier JWT token
- `auth_headers` - Authorization headers with admin token
- `cashier_auth_headers` - Authorization headers with cashier token
- `test_category` - Test product category
- `test_product` - Test product

## Test Coverage

Current coverage targets:
- Minimum coverage: 70%
- Target coverage: 80%+

View coverage report:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Writing Tests

### Example test structure:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestMyFeature:
    """Test my feature."""

    async def test_something(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test something specific."""
        response = await client.get(
            "/api/v1/endpoint",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert "expected_field" in response.json()
```

### Best practices:

1. **Use descriptive test names** - `test_login_with_valid_credentials` not `test_1`
2. **Test one thing per test** - Each test should verify a single behavior
3. **Use fixtures** - Reuse common setup code
4. **Test both success and failure** - Test happy path and edge cases
5. **Mock external services** - Don't call real APIs in tests
6. **Keep tests fast** - Avoid unnecessary delays
7. **Clean up** - Tests should not affect each other

## Continuous Integration

Tests are automatically run on:
- Every push to any branch
- Every pull request
- Before deployment

See `.github/workflows/ci.yml` for CI configuration.
