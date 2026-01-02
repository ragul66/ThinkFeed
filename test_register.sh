#!/bin/bash

echo "Testing Backend Registration Endpoint"
echo "======================================"
echo ""

echo "1. Testing health endpoint..."
curl -s http://localhost:8000/health
echo ""
echo ""

echo "2. Testing registration endpoint..."
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser123",
    "password": "password123",
    "full_name": "Test User"
  }'
echo ""
echo ""

echo "Done!"
