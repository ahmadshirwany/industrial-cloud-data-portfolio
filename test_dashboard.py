#!/usr/bin/env python3
"""
TEST 3: Test dashboard pages and features
Run this to verify all dashboard pages load correctly
"""

import requests
import re
import sys

BASE_URL = "http://localhost:8000"

def test_page(path, required_elements=None):
    """Test a dashboard page"""
    url = f"{BASE_URL}{path}"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for required elements
            if required_elements:
                missing = []
                for element in required_elements:
                    if element not in content:
                        missing.append(element)
                
                if missing:
                    print(f"⚠️  Partial load        {path}")
                    return False
            
            print(f"✅ Loaded             {path}")
            return True
        else:
            print(f"❌ Status {response.status_code}     {path}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect      {path}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)[:15]}  {path}")
        return False

def test_dashboard_data():
    """Test if dashboard has actual data"""
    print("\n" + "-" * 70)
    print("Testing data availability...")
    print("-" * 70 + "\n")
    
    # Check if dashboard-api has data
    api_url = "http://localhost:8080/api/servers/current?limit=1"
    
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"✅ Database has data    {len(data) if isinstance(data, list) else 1} server records found")
                return True
            else:
                print(f"⚠️  Database empty       No server data yet (generator may need time)")
                return False
    except Exception as e:
        print(f"❌ Cannot check data    {str(e)[:30]}")
        return False

def main():
    """Run all page tests"""
    print("\n")
    print("=" * 70)
    print("DASHBOARD PAGES TEST".center(70))
    print("=" * 70)
    print()
    
    print("Testing dashboard pages...\n")
    
    pages = [
        ("/", ["dashboard", "server", "container"]),  # Home page
        ("/dashboard", ["server", "container"]),  # Main dashboard
        ("/servers", ["server", "metric"]),  # Servers tab
        ("/containers", ["container"]),  # Containers tab
        ("/profile", ["Ahmad", "skill", "experience"]),  # Profile page
    ]
    
    results = []
    
    for path, elements in pages:
        passed = test_page(path, elements)
        results.append((path, passed))
    
    # Test data availability
    print("\n" + "-" * 70)
    data_test = test_dashboard_data()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nResult: {passed_count}/{total_count} pages loaded")
    
    if passed_count == total_count:
        print("\n✅ All dashboard pages functional!")
        if data_test:
            print("✅ Database has data")
        else:
            print("⚠️  Database empty but pages working")
        return 0
    else:
        failed = [p for p, passed in results if not passed]
        print(f"\n⚠️  Failed pages ({len(failed)}):")
        for p in failed:
            print(f"   - {p}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
