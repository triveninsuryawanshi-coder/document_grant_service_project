#!/bin/bash
# Quick start script for Document Grant Service

set -e

echo "🚀 Starting Document Grant Service setup..."

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Start PostgreSQL
echo "📦 Starting PostgreSQL container..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -e ".[dev]"

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Seed data
echo "🌱 Seeding database with sample data..."
python -m app.seed

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Start the server: uvicorn app.main:app --reload"
echo "  2. Open browser: http://localhost:8000/docs"
echo "  3. Try the API!"
echo ""
echo "🛑 To stop PostgreSQL: docker-compose down"
echo "🗑️  To remove data volume: docker-compose down -v"
