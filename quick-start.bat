@echo off
REM Quick start script for Document Grant Service (Windows)

echo 🚀 Starting Document Grant Service setup...

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    exit /b 1
)

echo 📦 Starting PostgreSQL container...
docker-compose up -d

REM Wait for database to be ready
echo ⏳ Waiting for database to be ready...
timeout /t 5 /nobreak

echo 📚 Installing Python dependencies...
pip install -e ".[dev]"

echo 🔄 Running database migrations...
alembic upgrade head

echo 🌱 Seeding database with sample data...
python -m app.seed

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo   1. Start the server: uvicorn app.main:app --reload
echo   2. Open browser: http://localhost:8000/docs
echo   3. Try the API!
echo.
echo 🛑 To stop PostgreSQL: docker-compose down
echo 🗑️  To remove data volume: docker-compose down -v
