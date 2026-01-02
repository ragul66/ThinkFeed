# Setup Guide - News App Backend

## What is Alembic? 🔄

**Alembic** is a database migration tool for SQLAlchemy. Think of it as "version control for your database schema."

### Why Use Alembic?

1. **Track Database Changes**: Like Git tracks code changes, Alembic tracks database schema changes
2. **Safe Updates**: Modify database structure without losing data
3. **Team Collaboration**: Everyone gets the same database structure
4. **Rollback Support**: Undo database changes if something goes wrong

### How It Works:

```
Your Models (Python) → Alembic → SQL Commands → Database
```

Example: When you add a new field to a model, Alembic creates a migration file that adds that column to the database.

## Your Current Folder Structure ✅

```
backend/                    ← Your backend folder (CORRECT!)
├── app/                    ← Application code
│   ├── api/               ← API endpoints
│   ├── models/            ← Database models
│   ├── schemas/           ← Request/response schemas
│   ├── services/          ← Business logic
│   ├── utils/             ← Helper functions
│   ├── middleware/        ← Rate limiting
│   ├── config.py          ← Settings
│   ├── database.py        ← DB connection
│   └── main.py            ← FastAPI app
├── alembic/               ← Migration files
│   ├── versions/          ← Migration history (auto-generated)
│   ├── env.py             ← Alembic config
│   └── script.py.mako     ← Migration template
├── docker-compose.yml     ← Docker services
├── Dockerfile             ← API container
├── requirements.txt       ← Python packages
├── .env                   ← Your credentials
└── README.md              ← Documentation
```

**This structure is PERFECT!** ✅ No errors will occur.

## Step-by-Step Setup

### 1. Navigate to Backend Folder

```bash
cd backend
```

### 2. Configure Environment Variables

Edit `.env` file and add your API keys:

```bash
# Required: Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_actual_gemini_key_here

# Optional: For Google OAuth (can skip for now)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# News API key is already set ✅
NEWS_API_KEY=f0e24f9a61104e8d909a2ebf9269c6b8
```

### 3. Test News API (Optional but Recommended)

```bash
# Install httpx first
pip install httpx

# Run test
python test_api.py
```

This shows what data categories are available from News API.

### 4. Start Docker Services

```bash
# Start PostgreSQL, Redis, and API
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f api
```

### 5. Create Database Tables with Alembic

```bash
# Create initial migration (generates migration file)
docker-compose exec api alembic revision --autogenerate -m "Initial tables"

# Apply migration (creates tables in database)
docker-compose exec api alembic upgrade head
```

**What just happened?**
- Alembic looked at your models (User, NewsArticle, etc.)
- Created a migration file in `alembic/versions/`
- Ran SQL commands to create tables in PostgreSQL

### 6. Access Your API

- **API Documentation**: http://localhost:8000/docs
- **API Base**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## Common Alembic Commands

```bash
# Create new migration after changing models
docker-compose exec api alembic revision --autogenerate -m "Add new field"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback last migration
docker-compose exec api alembic downgrade -1

# View migration history
docker-compose exec api alembic history

# Check current version
docker-compose exec api alembic current
```

## Testing the API

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. Get News Headlines

```bash
# Technology news
curl "http://localhost:8000/api/news/headlines?category=technology"

# Sports news
curl "http://localhost:8000/api/news/headlines?category=sports"

# Business news
curl "http://localhost:8000/api/news/headlines?category=business"
```

### 3. Search News

```bash
curl "http://localhost:8000/api/news/search?q=artificial+intelligence"
```

## Troubleshooting

### Issue: "Port already in use"

```bash
# Stop existing containers
docker-compose down

# Or change ports in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Issue: "Cannot connect to database"

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart services
docker-compose restart
```

### Issue: "Alembic command not found"

```bash
# Make sure you're running inside the container
docker-compose exec api alembic upgrade head
```

### Issue: "Module not found"

```bash
# Rebuild the container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Development Without Docker

If you prefer to run locally without Docker:

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Update .env for local database
DATABASE_URL=postgresql://newsuser:newspass@localhost:5432/newsdb
REDIS_URL=redis://localhost:6379/0

# 4. Install PostgreSQL and Redis locally
# (Download from official websites)

# 5. Run migrations
alembic upgrade head

# 6. Start API
uvicorn app.main:app --reload
```

## Next Steps

1. ✅ Start Docker services
2. ✅ Run Alembic migrations
3. ✅ Test API endpoints at http://localhost:8000/docs
4. ✅ Build your frontend app
5. ✅ Connect frontend to backend API

## Folder Structure is Correct! ✅

Your `backend/` folder structure will NOT cause any errors because:
- Docker Compose runs from the `backend/` directory
- All paths are relative to `backend/`
- The Dockerfile copies everything correctly
- Alembic paths are configured properly

You're all set! 🚀
