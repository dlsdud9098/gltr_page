#!/bin/bash

echo "==================================="
echo "GLTR Webtoon Platform Setup Script"
echo "(No Authentication Version)"
echo "==================================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL first."
    exit 1
fi

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first:"
    echo "   pip install uv"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

echo "✅ All required tools are installed."
echo ""

# Database setup
echo "📊 Setting up PostgreSQL database..."
read -p "Enter PostgreSQL username (default: postgres): " PG_USER
PG_USER=${PG_USER:-postgres}

read -sp "Enter PostgreSQL password: " PG_PASSWORD
echo ""

# Create database
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -c "CREATE DATABASE gltr_webtoon;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Database created successfully."
else
    echo "⚠️  Database might already exist or creation failed."
fi

# Apply schema
if [ -f database/schema.sql ]; then
    PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d gltr_webtoon -f database/schema.sql
    echo "✅ Database schema applied."
else
    echo "❌ Schema file not found at database/schema.sql"
fi

# Backend setup
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment
uv venv
echo "✅ Virtual environment created."

# Install dependencies
source .venv/bin/activate
uv pip install -r requirements.txt
echo "✅ Backend dependencies installed."

# Create .env file
if [ ! -f .env ]; then
    cat > .env << EOF
DATABASE_URL=postgresql://$PG_USER:$PG_PASSWORD@localhost:5432/gltr_webtoon
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
EOF
    echo "✅ Backend .env file created."
else
    echo "⚠️  Backend .env file already exists."
fi

cd ..

# Frontend setup
echo ""
echo "🎨 Setting up Frontend..."
cd frontend

# Install dependencies
npm install
echo "✅ Frontend dependencies installed."

cd ..

# Clean up old auth-related files
echo ""
echo "🧹 Cleaning up old authentication files..."
rm -f backend/auth.py 2>/dev/null
rm -f backend/routers/auth_router.py 2>/dev/null
rm -f backend/routers/users_router.py 2>/dev/null
rm -f frontend/src/contexts/AuthContext.js 2>/dev/null
rm -f frontend/src/components/PrivateRoute.js 2>/dev/null
rm -f frontend/src/pages/LoginPage.js 2>/dev/null
rm -f frontend/src/pages/LoginPage.css 2>/dev/null
rm -f frontend/src/pages/RegisterPage.js 2>/dev/null
rm -f frontend/src/pages/RegisterPage.css 2>/dev/null
rm -f frontend/src/pages/ProfilePage.js 2>/dev/null
rm -f frontend/src/pages/ProfilePage.css 2>/dev/null
echo "✅ Old authentication files removed."

echo ""
echo "==================================="
echo "✅ Setup completed successfully!"
echo "==================================="
echo ""
echo "This version works without login/signup!"
echo "Sessions are managed automatically via browser cookies."
echo ""
echo "To start the application:"
echo ""
echo "1. Start Backend:"
echo "   cd backend"
echo "   source .venv/bin/activate"
echo "   python main.py"
echo ""
echo "2. Start Frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "The application will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Features:"
echo "   - No login required"
echo "   - Session-based ownership (30 days)"
echo "   - Create and manage webtoons anonymously"
echo "   - All data tied to browser session"