import os
import asyncio
import pytest
from remote_expose import exposeRemote, exposeRemoteAsync

def test_parallel_expose():
    """Test that multiple files can be exposed in parallel using the synchronous context manager"""
    # Create temporary test files
    files = {
        'test_file1.txt': "Hello from file 1!",
        'test_file2.txt': "Hello from file 2!",
        'test_file3.txt': "Hello from file 3!"
    }
    
    try:
        # Create test files
        for filename, content in files.items():
            with open(filename, 'w') as f:
                f.write(content)
        
        # Expose multiple files in parallel
        with exposeRemote('test_file1.txt') as url1, \
             exposeRemote('test_file2.txt') as url2, \
             exposeRemote('test_file3.txt') as url3:
            
            # Verify all URLs are valid
            assert all(url.startswith('http') for url in [url1, url2, url3])
            assert all('ngrok' in url for url in [url1, url2, url3])
            
            # Verify each URL is unique
            urls = [url1, url2, url3]
            assert len(set(urls)) == len(urls)
            
    finally:
        # Clean up test files
        for filename in files:
            if os.path.exists(filename):
                os.remove(filename)

@pytest.mark.asyncio
async def test_parallel_expose_async():
    """Test that multiple files can be exposed in parallel using the async context manager"""
    # Create temporary test files
    files = {
        'async_file1.txt': "Async hello from file 1!",
        'async_file2.txt': "Async hello from file 2!",
        'async_file3.txt': "Async hello from file 3!"
    }
    
    try:
        # Create test files
        for filename, content in files.items():
            with open(filename, 'w') as f:
                f.write(content)
        
        # Expose multiple files in parallel using async context managers
        async with exposeRemoteAsync('async_file1.txt') as url1, \
                  exposeRemoteAsync('async_file2.txt') as url2, \
                  exposeRemoteAsync('async_file3.txt') as url3:
            
            # Verify all URLs are valid
            assert all(url.startswith('http') for url in [url1, url2, url3])
            assert all('ngrok' in url for url in [url1, url2, url3])
            
            # Verify each URL is unique
            urls = [url1, url2, url3]
            assert len(set(urls)) == len(urls)
            
            # Add a small delay to ensure server stability
            await asyncio.sleep(1)
            
    finally:
        # Clean up test files
        for filename in files:
            if os.path.exists(filename):
                os.remove(filename)
