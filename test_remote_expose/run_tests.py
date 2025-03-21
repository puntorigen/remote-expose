#!/usr/bin/env python
import os
import time
import asyncio
import subprocess
import requests
import signal
import sys
from urllib.parse import urljoin

# Define constants
FASTAPI_PORT = 8080
FASTAPI_BASE_URL = f"http://localhost:{FASTAPI_PORT}"
SAMPLE_FILE_PATH = os.path.join(os.path.dirname(__file__), "files", "sample.txt")
FASTAPI_PROCESS = None

def run_standalone_test():
    """Run the standalone test script"""
    print("\n🔍 Running standalone tests...")
    try:
        result = subprocess.run(
            [sys.executable, "test_standalone.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Standalone test failed with error: {result.stderr}")
            return False
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Standalone test failed with error: {e.stderr}")
        return False

def start_fastapi_server():
    """Start the FastAPI server as a subprocess"""
    global FASTAPI_PROCESS
    print("\n🚀 Starting FastAPI server...")
    
    FASTAPI_PROCESS = subprocess.Popen(
        [sys.executable, "test_fastapi_app.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print("⏳ Waiting for FastAPI server to start...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(urljoin(FASTAPI_BASE_URL, "/health"))
            if response.status_code == 200:
                print(f"✅ FastAPI server started successfully at {FASTAPI_BASE_URL}")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    
    print("❌ Failed to start FastAPI server")
    return False

def stop_fastapi_server():
    """Stop the FastAPI server subprocess"""
    global FASTAPI_PROCESS
    if FASTAPI_PROCESS:
        print("\n🛑 Stopping FastAPI server...")
        FASTAPI_PROCESS.send_signal(signal.SIGTERM)
        FASTAPI_PROCESS.wait(timeout=5)
        print("✅ FastAPI server stopped")

def test_fastapi_endpoints():
    """Test the FastAPI endpoints"""
    print("\n🔍 Testing FastAPI endpoints...")
    
    # Test synchronous endpoint
    print("\nTesting synchronous endpoint...")
    try:
        response = requests.get(urljoin(FASTAPI_BASE_URL, "/sync-expose"))
        response.raise_for_status()
        result = response.json()
        print(f"Response: {result}")
        
        # Verify we got a valid public URL
        if not result.get("public_url") or not result.get("public_url").startswith("http"):
            print("❌ Invalid public URL")
            return False
        
        # Verify the file content
        with open(SAMPLE_FILE_PATH, 'r') as f:
            original_content = f.read()
        
        if result.get("file_content") != original_content:
            print("❌ File content doesn't match")
            return False
        
        print("✅ Synchronous endpoint test passed!")
    except Exception as e:
        print(f"❌ Synchronous endpoint test failed with error: {str(e)}")
        return False
    
    # Test asynchronous endpoint
    print("\nTesting asynchronous endpoint...")
    try:
        response = requests.get(urljoin(FASTAPI_BASE_URL, "/async-expose"))
        response.raise_for_status()
        result = response.json()
        print(f"Response: {result}")
        
        # Verify we got a valid public URL
        if not result.get("public_url") or not result.get("public_url").startswith("http"):
            print("❌ Invalid public URL")
            return False
        
        # Verify the file content
        with open(SAMPLE_FILE_PATH, 'r') as f:
            original_content = f.read()
        
        if result.get("file_content") != original_content:
            print("❌ File content doesn't match")
            return False
        
        print("✅ Asynchronous endpoint test passed!")
    except Exception as e:
        print(f"❌ Asynchronous endpoint test failed with error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        # Run standalone tests
        standalone_success = run_standalone_test()
        
        # Run FastAPI tests
        fastapi_success = False
        if start_fastapi_server():
            fastapi_success = test_fastapi_endpoints()
        
        # Print final results
        print("\n📊 Test Results:")
        print(f"Standalone Tests: {'✅ PASSED' if standalone_success else '❌ FAILED'}")
        print(f"FastAPI Tests: {'✅ PASSED' if fastapi_success else '❌ FAILED'}")
        
        if standalone_success and fastapi_success:
            print("\n🎉 All tests passed! The remote-expose package works in both standalone and FastAPI contexts.")
        else:
            print("\n❌ Some tests failed. Please check the logs above for details.")
        
    finally:
        stop_fastapi_server()
