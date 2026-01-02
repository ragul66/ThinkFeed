# Quick Fix for 404 Error

## The Problem
Getting 404 error when trying to register means the backend endpoint doesn't exist or database isn't set up.

## Solution - Run These Commands

### 1. Check if Docker is running
```bash
cd backend
docker-compose ps
```

You should see 3 services running:
- news_postgres
- news_redis  
- news_api

### 2. If not running, start Docker
```bash
docker-compose up -d
```

### 3. Check API logs
```bash
docker-compose logs -f api
```

Look for errors. Press Ctrl+C to exit.

### 4. Create Database Tables (IMPORTANT!)
```bash
docker-compose exec api alembic revision --autogenerate -m "Initial tables"
docker-compose exec api alembic upgrade head
```

This creates the database tables. Without this, registration will fail!

### 5. Test Backend
Open browser: **http://localhost:8000/docs**

You should see the FastAPI documentation page with all endpoints.

### 6. Test Registration Manually
In the FastAPI docs page:
1. Click on `POST /api/auth/register`
2. Click "Try it out"
3. Enter test data:
```json
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "password123"
}
```
4. Click "Execute"

If it works here, it should work in the app!

### 7. Restart Everything
```bash
# Stop
docker-compose down

# Start fresh
docker-compose up -d

# Check logs
docker-compose logs -f api
```

## Test Script

I created a test script. Run it to verify backend:

```bash
cd backend
pip install requests
python test_backend.py
```

This will test all endpoints and show you exactly what's wrong.

## Common Issues

### Issue: "No module named 'app'"
**Solution:** You're running outside Docker. Use Docker:
```bash
docker-compose up -d
```

### Issue: "Connection refused"
**Solution:** Backend isn't running. Start it:
```bash
docker-compose up -d
```

### Issue: "404 Not Found"
**Solution:** Database tables don't exist. Run migrations:
```bash
docker-compose exec api alembic upgrade head
```

### Issue: "500 Internal Server Error"
**Solution:** Check logs for the actual error:
```bash
docker-compose logs -f api
```

## Verify Everything

After running the fixes above:

1. ✅ Backend running: http://localhost:8000/health
2. ✅ API docs: http://localhost:8000/docs
3. ✅ Database tables created (check logs)
4. ✅ Can register via docs page

Then try the app again!

## For Physical Device

If using physical device, also check:

1. **Firewall:** Allow port 8000
2. **Same Network:** Phone and PC on same WiFi
3. **Correct IP:** Use `ipconfig` to find your PC's IP
4. **Test from phone browser:** http://YOUR_IP:8000/health

---

**Most likely issue: Database tables not created. Run the alembic commands!**
