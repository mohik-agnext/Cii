#!/usr/bin/env python3
"""
Test script to verify server is responding correctly
"""

import requests
import json
import time

def test_server():
    """Test if server is responding to requests"""
    url = "http://localhost:3003/api/search"
    
    test_cases = [
        {"message": "hello", "expected": "greeting"},
        {"message": "hi there", "expected": "greeting"},
        {"message": "what are EV incentives", "expected": "policy"}
    ]
    
    print("🧪 Testing Server Connectivity and Responses")
    print("=" * 50)
    
    # First check health
    try:
        health_response = requests.get("http://localhost:3003/api/health", timeout=5)
        print(f"🏥 Health Check: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"   Status: {health_response.json()}")
        print()
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test search functionality
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['message']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"message": test_case["message"]},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Response received:")
                print(f"   Bot: {data.get('response', 'No response')[:100]}...")
                print(f"   Performance: {data.get('performance', {}).get('total_time', 'N/A')}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print("\n" + "="*50 + "\n")
    
    return True

if __name__ == "__main__":
    print("⏳ Waiting for server to be ready...")
    time.sleep(5)  # Give server time to start
    test_server() 