#!/usr/bin/env python
"""
Test script to verify Phase 1 setup
Run this after starting the Django server with: python manage.py runserver
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
SCAN_ENDPOINT = f"{BASE_URL}/api/v1/scan/"

def test_api_health():
    """Test if the server is running"""
    print("🔍 Testing API connectivity...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code in [200, 404]:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned unexpected status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start with: python manage.py runserver")
        return False

def test_scan_endpoint():
    """Test the /scan/ endpoint with mock data"""
    print("\n🔍 Testing /api/v1/scan/ endpoint...")
    
    # Create a valid 1x1 pixel PNG image
    from io import BytesIO
    try:
        from PIL import Image
        
        # Create a simple 1x1 red pixel image
        img = Image.new('RGB', (1, 1), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        test_image_data = img_bytes.getvalue()
    except ImportError:
        # Fallback: Use a properly formatted minimal PNG
        test_image_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
            b'\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT'
            b'\x08\x99c\xf8\x0f\x00\x00\x01\x01\x00\x01\x18\xdd\x8d\xb4'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )
    
    files = {
        'image': ('test_label.png', test_image_data, 'image/png')
    }
    
    data = {
        'user_profile': json.dumps({
            "age_months": 8,
            "region": "PK-Punjab",
            "dietary_restrictions": ["halal"]
        })
    }
    
    try:
        response = requests.post(SCAN_ENDPOINT, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API endpoint working correctly")
            
            # Validate response structure
            result = response.json()
            required_fields = [
                'scan_id', 'timestamp', 'status', 'parsed_ingredients',
                'health_impact_summary', 'allergen_alerts'
            ]
            
            missing_fields = [field for field in required_fields if field not in result]
            
            if not missing_fields:
                print("✅ Response structure is valid")
                print(f"\n📊 Sample Response:")
                print(f"  Scan ID: {result.get('scan_id')}")
                print(f"  Status: {result.get('status')}")
                print(f"  Verdict: {result.get('health_impact_summary', {}).get('verdict')}")
                print(f"  Summary: {result.get('health_impact_summary', {}).get('short_summary')}")
                return True
            else:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during request: {e}")
        return False

def main():
    print("="*60)
    print("NutriScan Phase 1 - Backend Setup Verification")
    print("="*60)
    
    tests_passed = 0
    total_tests = 2
    
    if test_api_health():
        tests_passed += 1
    
    if test_scan_endpoint():
        tests_passed += 1
    
    print("\n" + "="*60)
    print(f"Results: {tests_passed}/{total_tests} tests passed")
    print("="*60)
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! Phase 1 setup is complete.")
        print("✅ Ready for mobile app integration")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
