# Contributing

## Development Setup

1. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Start PostgreSQL:**
   ```bash
   docker-compose up -d
   ```

3. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start dev server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Code Style

- Use Black for code formatting
- Use isort for import sorting
- Use meaningful variable and function names
- Add docstrings to functions and classes

### Format Code
```bash
make format
```

## Testing

Run all tests:
```bash
make test
```

Run specific test file:
```bash
pytest tests/test_services.py -v
```

Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Commits

- Write clear, descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused and atomic

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest`
4. Format code: `make format`
5. Push to your fork
6. Open a pull request with a clear description

## Project Structure

```
app/
├── config.py           - Settings and configuration
├── database.py         - Database connection management
├── logging_config.py   - Structured logging setup
├── main.py            - FastAPI application and routes
├── models.py          - SQLAlchemy ORM models
├── schemas.py         - Pydantic request/response schemas
├── services.py        - Business logic
└── seed.py            - Database seeding

alembic/
├── versions/          - Migration files
├── env.py             - Migration environment config
├── script.mako        - Migration template
└── alembic.ini        - Alembic config

tests/
├── conftest.py        - Pytest configuration
├── test_services.py   - Unit tests
└── test_endpoints.py  - Integration tests
```

## Debugging

- Use print() or logger statements
- Use VS Code debugger with Python extension
- Check application logs for errors

## Database

### Create a migration:
```bash
alembic revision --autogenerate -m "Add new column"
```

### Upgrade:
```bash
alembic upgrade head
```

### Downgrade one migration:
```bash
alembic downgrade -1
```

## Common Issues

### Port already in use
If port 8000 is in use:
```bash
uvicorn app.main:app --port 8001 --reload
```

### Database connection failed
Ensure PostgreSQL is running:
```bash
docker-compose ps
```

### Tests failing
Clear pytest cache:
```bash
pytest --cache-clear
```

## Performance Tips

- Use database indexes for frequently queried columns
- Use pagination on list endpoints
- Use async/await for I/O operations
- Monitor query performance with `database_echo=true`

## Security Notes

- This is a demo service without authentication
- In production, implement OAuth/JWT authentication
- Validate all user inputs
- Use environment variables for secrets
- Never commit `.env` files

## Documentation

Update README.md when adding new endpoints or changing behavior.

Maintain API.md with example requests.

Include docstrings in all new functions:
```python
def my_function(param: str) -> str:
    """Short description.
    
    Longer explanation if needed.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something is invalid
    """
```
