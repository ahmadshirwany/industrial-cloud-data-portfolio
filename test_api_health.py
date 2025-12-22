#!/usr/bin/env python3
"""
TEST 2: Test all essential API endpoints
Run this to verify all API routes are working correctly
"""

import requests
import json
import sys

BASE_API_URL = "http://localhost:8080/api"

def test_endpoint(endpoint, description):
    """Test a single API endpoint"""
    url = f"{BASE_API_URL}{endpoint}"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Count records
            if isinstance(data, list):
                count = len(data)
                status = f"✅ {count} records"
            elif isinstance(data, dict):
                status = "✅ OK"
            else:
                status = "✅ Response received"
            
            print(f"{status:20} {endpoint}")
            return True
        else:
            print(f"❌ Status {response.status_code}     {endpoint}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect      {endpoint}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)[:15]}  {endpoint}")
        return False

def main():
    """Run all endpoint tests"""
    print("\n")
    print("=" * 70)
    print("API ENDPOINTS TEST".center(70))
    print("=" * 70)
    print()
    
    print("Testing API endpoints...\n")
    
    endpoints = [
        # Servers
        ("/servers/current?limit=5", "Get current servers"),
        
        # Containers
        ("/containers/current?limit=5", "Get current containers"),
        ("/containers/health", "Get container health"),
        
        # Analytics
        ("/analytics/cpu-trends?hours=6", "CPU trends"),
        ("/analytics/memory-trends?hours=6", "Memory trends"),
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        passed = test_endpoint(endpoint, description)
        results.append((endpoint, passed))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nResult: {passed_count}/{total_count} endpoints working")
    
    if passed_count == total_count:
        print("\n✅ All API endpoints operational!")
        return 0
    else:
        failed = [ep for ep, p in results if not p]
        print(f"\n⚠️  Failed endpoints ({len(failed)}):")
        for ep in failed:
            print(f"   - {ep}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
