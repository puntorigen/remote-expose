#!/usr/bin/env python
import os
import asyncio
import requests
from remote_expose import exposeRemote, exposeRemoteAsync

# Path to our sample file
SAMPLE_FILE_PATH = os.path.join(os.path.dirname(__file__), "files", "sample.txt")

def test_sync():
    """Test the synchronous version of exposeRemote"""
    print("Testing synchronous exposeRemote...")
    
    with exposeRemote(SAMPLE_FILE_PATH) as public_url:
        print(f"File exposed at: {public_url}")
        
        # Verify the file is accessible
        response = requests.get(public_url)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        # Check if content matches
        with open(SAMPLE_FILE_PATH, 'r') as f:
            original_content = f.read()
        
        assert response.text == original_content
        print("✅ Synchronous test passed!")

async def test_async():
    """Test the asynchronous version of exposeRemoteAsync"""
    print("Testing asynchronous exposeRemoteAsync...")
    
    async with exposeRemoteAsync(SAMPLE_FILE_PATH) as public_url:
        print(f"File exposed at: {public_url}")
        
        # Verify the file is accessible
        response = requests.get(public_url)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        # Check if content matches
        with open(SAMPLE_FILE_PATH, 'r') as f:
            original_content = f.read()
        
        assert response.text == original_content
        print("✅ Asynchronous test passed!")

if __name__ == "__main__":
    # Run synchronous test
    test_sync()
    
    # Run asynchronous test
    asyncio.run(test_async())
    
    print("All tests completed successfully!")
