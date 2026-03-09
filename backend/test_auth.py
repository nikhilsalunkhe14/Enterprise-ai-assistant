#!/usr/bin/env python3
"""
Test script to verify authentication endpoints are working
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

async def test_health():
    """Test health endpoint"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/health") as response:
            data = await response.json()
            print("🏥 Health Check:", json.dumps(data, indent=2))
            return response.status == 200

async def test_register():
    """Test registration endpoint"""
    test_user = {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/api/auth/register", 
            json=test_user
        ) as response:
            data = await response.json()
            print("📝 Registration Response:", json.dumps(data, indent=2))
            return response.status == 201

async def test_login():
    """Test login endpoint"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/api/auth/login", 
            json=login_data
        ) as response:
            data = await response.json()
            print("🔑 Login Response:", json.dumps(data, indent=2))
            return response.status == 200

async def main():
    """Run all tests"""
    print("🚀 Testing Authentication Endpoints...")
    print("=" * 50)
    
    # Test health
    health_ok = await test_health()
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print()
    
    # Test registration
    reg_ok = await test_register()
    print(f"Registration: {'✅ PASS' if reg_ok else '❌ FAIL'}")
    print()
    
    # Test login
    login_ok = await test_login()
    print(f"Login: {'✅ PASS' if login_ok else '❌ FAIL'}")
    print()
    
    print("=" * 50)
    if all([health_ok, reg_ok, login_ok]):
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("❌ Some tests failed. Check the backend logs.")

if __name__ == "__main__":
    asyncio.run(main())
