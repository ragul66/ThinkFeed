"""
Quick test script to verify backend is working
Run: python test_backend.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_root():
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_register():
    print("\n3. Testing register endpoint...")
    try:
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User"
        }
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Success! User registered.")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_docs():
    print("\n4. Testing docs endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Backend API Test")
    print("=" * 50)
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Docs", test_docs()))
    results.append(("Register", test_register()))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n✅ All tests passed! Backend is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure Docker is running: docker-compose ps")
        print("2. Check logs: docker-compose logs -f api")
        print("3. Run migrations: docker-compose exec api alembic upgrade head")
