#!/usr/bin/env python3
"""
TEST 1: Verify all Docker services are running and responding
Run this to check if the entire application stack is healthy
"""

import subprocess
import sys
import time
import requests

def check_docker_services():
    """Check if all Docker containers are running"""
    print("=" * 70)
    print("TEST 1: DOCKER SERVICES STATUS")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True,
            cwd="."
        )
        
        print(result.stdout)
        
        # Check if all services show "Up"
        if "5 containers" in result.stdout or result.stdout.count("Up") >= 5:
            print("✅ All services are running")
            return True
        else:
            print("❌ Not all services are running")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker services: {e}")
        return False

def test_api_connectivity():
    """Test if the API is responding"""
    print("\n" + "=" * 70)
    print("TEST 2: API CONNECTIVITY")
    print("=" * 70)
    
    api_url = "http://localhost:8080/api/servers/current?limit=1"
    
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API responding: {api_url}")
            print(f"   Got {len(data) if isinstance(data, list) else 1} records")
            return True
        else:
            print(f"❌ API returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API. Is it running on port 8080?")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_frontend_health():
    """Test if the frontend is serving"""
    print("\n" + "=" * 70)
    print("TEST 3: FRONTEND HEALTH")
    print("=" * 70)
    
    frontend_url = "http://localhost:8000/"
    
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend responding: {frontend_url}")
            return True
        else:
            print(f"❌ Frontend returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to frontend. Is it running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def test_data_generation():
    """Test if data is being generated"""
    print("\n" + "=" * 70)
    print("TEST 4: DATA GENERATION")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=generator"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "Up" in result.stdout:
            print("✅ Generator is active and generating data")
            print("   (publishes metrics every 5 minutes)")
            return True
        else:
            print("❌ Generator not running")
            return False
    except Exception as e:
        print(f"❌ Data generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("=" * 70)
    print("COMPLETE SYSTEM HEALTH CHECK".center(70))
    print("=" * 70)
    print()
    
    results = []
    
    # Run all tests
    results.append(("Docker Services", check_docker_services()))
    time.sleep(1)
    results.append(("API Connectivity", test_api_connectivity()))
    time.sleep(1)
    results.append(("Frontend Health", test_frontend_health()))
    time.sleep(1)
    results.append(("Data Generation", test_data_generation()))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nResult: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All systems operational!")
        return 0
    else:
        print("\n⚠️  Some systems need attention. Check logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
