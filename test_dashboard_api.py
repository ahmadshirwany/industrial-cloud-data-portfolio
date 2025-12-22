"""
Dashboard API Test Script
Tests all endpoints and displays results in terminal
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any
import time

# Configuration
BASE_URL = "http://localhost:8080"
TIMEOUT = 10


class Colors:
    """Terminal colors for output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}[PASS] {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}[FAIL] {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}[INFO] {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}[WARN] {text}{Colors.ENDC}")


def print_response(data: Any, indent: int = 2):
    """Print formatted JSON response"""
    if isinstance(data, (dict, list)):
        json_str = json.dumps(data, indent=indent, default=str)
        print(f"{Colors.OKBLUE}{json_str}{Colors.ENDC}")
    else:
        print(f"{Colors.OKBLUE}{data}{Colors.ENDC}")


def test_endpoint(
    method: str,
    endpoint: str,
    params: Dict = None,
    description: str = ""
) -> bool:
    """
    Test a single endpoint
    Returns True if successful, False otherwise
    """
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{Colors.BOLD}Testing: {description}{Colors.ENDC}")
    print(f"Endpoint: {method} {endpoint}")
    if params:
        print(f"Parameters: {params}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=params, timeout=TIMEOUT)
        else:
            print_error(f"Unsupported method: {method}")
            return False
        
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed_time:.2f}ms")
        
        if response.status_code == 200:
            data = response.json()
            
            # Print response preview
            if isinstance(data, list):
                print(f"Response: List with {len(data)} items")
                if data:
                    print("First item:")
                    print_response(data[0])
                    if len(data) > 1:
                        print(f"... and {len(data) - 1} more items")
            elif isinstance(data, dict):
                print("Response:")
                print_response(data)
            else:
                print(f"Response: {data}")
            
            print_success(f"PASSED - {description}")
            return True
        else:
            print_error(f"FAILED - Status {response.status_code}")
            try:
                error_data = response.json()
                print_response(error_data)
            except:
                print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"FAILED - Cannot connect to {BASE_URL}")
        print_warning("Make sure the dashboard-api service is running!")
        return False
    except requests.exceptions.Timeout:
        print_error(f"FAILED - Request timeout after {TIMEOUT}s")
        return False
    except Exception as e:
        print_error(f"FAILED - {str(e)}")
        return False


def main():
    """Run all API tests"""
    
    print_header("DASHBOARD API TEST SUITE")
    print_info(f"Testing API at: {BASE_URL}")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Test root and health endpoints
    print_header("BASIC ENDPOINTS")
    
    tests = [
        ("GET", "/", {}, "Root endpoint"),
        ("GET", "/health", {}, "Health check"),
    ]
    
    for method, endpoint, params, desc in tests:
        results["total"] += 1
        if test_endpoint(method, endpoint, params, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
        time.sleep(0.5)
    
    # Test Server Metrics Endpoints
    print_header("SERVER METRICS ENDPOINTS")
    
    tests = [
        ("GET", "/api/servers/health", {"minutes": 5}, "Get server health summary"),
        ("GET", "/api/servers/current", {"limit": 10}, "Get current server states"),
        ("GET", "/api/servers/trends/cpu", {"hours": 1, "interval": "5min"}, "Get CPU trends"),
        ("GET", "/api/servers/by-region", {}, "Get servers by region"),
        ("GET", "/api/servers/top-cpu", {"limit": 5}, "Get top CPU consumers"),
        ("GET", "/api/servers/disk-usage", {}, "Get disk usage"),
    ]
    
    for method, endpoint, params, desc in tests:
        results["total"] += 1
        if test_endpoint(method, endpoint, params, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
        time.sleep(0.5)
    
    # Test Container Metrics Endpoints
    print_header("CONTAINER METRICS ENDPOINTS")
    
    tests = [
        ("GET", "/api/containers/health", {"minutes": 5}, "Get container health"),
        ("GET", "/api/containers/current", {"limit": 10}, "Get current containers"),
        ("GET", "/api/containers/by-service", {}, "Get containers by service"),
        ("GET", "/api/containers/high-memory", {"threshold": 80, "limit": 10}, "Get high memory containers"),
        ("GET", "/api/containers/restarts", {"hours": 24}, "Get container restarts"),
        ("GET", "/api/containers/throughput-trend", {"hours": 1}, "Get throughput trend"),
    ]
    
    for method, endpoint, params, desc in tests:
        results["total"] += 1
        if test_endpoint(method, endpoint, params, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
        time.sleep(0.5)
    
    # Test Service Metrics Endpoints
    print_header("SERVICE METRICS ENDPOINTS")
    
    tests = [
        ("GET", "/api/services/performance", {"hours": 1}, "Get service performance"),
        ("GET", "/api/services/latency-trend", {"hours": 1}, "Get latency trend"),
        ("GET", "/api/services/error-rate-trend", {"hours": 1}, "Get error rate trend"),
        ("GET", "/api/services/success-rate-gauge", {"minutes": 5}, "Get success rate gauge"),
        ("GET", "/api/services/failed-requests", {"hours": 24}, "Get failed requests"),
        ("GET", "/api/services/instances", {}, "Get service instances"),
        ("GET", "/api/services/by-region", {}, "Get services by region"),
        ("GET", "/api/services/slowest", {"limit": 5}, "Get slowest services"),
    ]
    
    for method, endpoint, params, desc in tests:
        results["total"] += 1
        if test_endpoint(method, endpoint, params, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
        time.sleep(0.5)
    
    # Test Analytics Endpoints
    print_header("ANALYTICS ENDPOINTS")
    
    tests = [
        ("GET", "/api/analytics/system-health", {"minutes": 5}, "Get system health score"),
        ("GET", "/api/analytics/top-cpu-resources", {"limit": 5}, "Get top CPU resources"),
        ("GET", "/api/analytics/top-memory-resources", {"limit": 5}, "Get top memory resources"),
        ("GET", "/api/analytics/anomalies", {"hours": 1}, "Detect anomalies"),
        ("GET", "/api/analytics/daily-stats", {}, "Get daily stats"),
        ("GET", "/api/analytics/capacity-forecast", {"days": 7}, "Get capacity forecast"),
        ("GET", "/api/analytics/regional-summary", {}, "Get regional summary"),
    ]
    
    for method, endpoint, params, desc in tests:
        results["total"] += 1
        if test_endpoint(method, endpoint, params, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
        time.sleep(0.5)
    
    # Test WebSocket Endpoints
    print_header("WEBSOCKET ENDPOINTS")
    
    tests = [
        ("GET", "/ws/connections", {}, "Get active WebSocket connections"),
    ]
    
    for method, endpoint, params, desc in tests:
        results["total"] += 1
        if test_endpoint(method, endpoint, params, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
        time.sleep(0.5)
    
    # Print Summary
    print_header("TEST SUMMARY")
    
    print(f"\n{Colors.BOLD}Total Tests: {results['total']}{Colors.ENDC}")
    print_success(f"Passed: {results['passed']}")
    print_error(f"Failed: {results['failed']}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.ENDC}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}ALL TESTS PASSED!{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}SOME TESTS FAILED{Colors.ENDC}")
        print_warning("Check the logs above for details")
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    print_info("Test WebSocket streaming:")
    print(f"{Colors.OKCYAN}ws://localhost:8080/ws/metrics{Colors.ENDC}")
    print_info("Use a WebSocket client like 'websocat' or browser DevTools")
    
    print(f"\n{Colors.BOLD}API Documentation:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Swagger UI: {BASE_URL}/docs{Colors.ENDC}")
    print(f"{Colors.OKCYAN}ReDoc: {BASE_URL}/redoc{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
