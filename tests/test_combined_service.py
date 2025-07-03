#!/usr/bin/env python3
"""
Test Script for Salesforce Combined Service
------------------------------------------
This script tests the Salesforce Combined Service by sending sample requests
to both the prompt service and metadata API endpoints.

Usage:
    python test_combined_service.py --host <host> --port <port>

Example:
    python test_combined_service.py --host localhost --port 5000
"""

import argparse
import requests
import json
import sys

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Test Salesforce Combined Service')
    parser.add_argument('--host', type=str, default='localhost',
                        help='Host where the service is running')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port where the service is running')
    return parser.parse_args()

def test_health_check(base_url):
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200 and response.json().get('status') == 'healthy':
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_generate_query(base_url, prompt):
    """Test the generate-query endpoint"""
    print(f"\n=== Testing Generate Query: '{prompt}' ===")
    try:
        response = requests.post(
            f"{base_url}/api/generate-query",
            json={"prompt": prompt}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200 and 'query' in response.json():
            print("✅ Generate query test passed")
            return True
        else:
            print("❌ Generate query test failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_batch_generate(base_url, prompts):
    """Test the batch-generate endpoint"""
    print(f"\n=== Testing Batch Generate: {len(prompts)} prompts ===")
    try:
        response = requests.post(
            f"{base_url}/api/batch-generate",
            json={"prompts": prompts}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200 and 'results' in response.json():
            print("✅ Batch generate test passed")
            return True
        else:
            print("❌ Batch generate test failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_get_objects(base_url, credentials):
    """Test the objects endpoint"""
    print("\n=== Testing Get Objects ===")
    print("Note: This test requires valid Salesforce credentials")
    print("Skipping actual API call to avoid credential requirements")
    
    # Uncomment the following code to test with actual credentials
    """
    try:
        response = requests.post(
            f"{base_url}/api/objects",
            json=credentials
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200 and 'objects' in response.json():
            print("✅ Get objects test passed")
            return True
        else:
            print("❌ Get objects test failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    """
    
    print("✅ Get objects test skipped")
    return True

def test_get_metadata(base_url, credentials):
    """Test the metadata endpoint"""
    print("\n=== Testing Get Metadata ===")
    print("Note: This test requires valid Salesforce credentials")
    print("Skipping actual API call to avoid credential requirements")
    
    # Uncomment the following code to test with actual credentials
    """
    try:
        response = requests.post(
            f"{base_url}/api/metadata",
            json=credentials
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Get metadata test passed")
            return True
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("❌ Get metadata test failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    """
    
    print("✅ Get metadata test skipped")
    return True

def main():
    """Main function"""
    args = parse_arguments()
    base_url = f"http://{args.host}:{args.port}"
    
    print(f"Testing Salesforce Combined Service at {base_url}")
    
    # Test health check
    if not test_health_check(base_url):
        print("\n❌ Health check failed. Make sure the service is running.")
        sys.exit(1)
    
    # Sample prompts for testing
    sample_prompts = [
        "Get all Accounts with Name and Industry",
        "Find Contacts in California",
        "Get Opportunities where Amount is greater than 10000",
        "List all Cases with their Status",
        "Show me Users who are active"
    ]
    
    # Sample credentials for testing (replace with actual credentials)
    sample_credentials = {
        "username": "your-username",
        "password": "your-password",
        "security_token": "your-security-token",
        "client_id": "your-client-id",
        "client_secret": "your-client-secret"
    }
    
    # Test generate query with a single prompt
    test_generate_query(base_url, sample_prompts[0])
    
    # Test batch generate with multiple prompts
    test_batch_generate(base_url, sample_prompts)
    
    # Test metadata API endpoints
    test_get_objects(base_url, sample_credentials)
    test_get_metadata(base_url, sample_credentials)
    
    print("\n=== Test Summary ===")
    print("All tests completed. Check the results above for any failures.")

if __name__ == "__main__":
    main()