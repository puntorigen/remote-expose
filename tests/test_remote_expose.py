import os
import pytest
from remote_expose import exposeRemote

def test_expose_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        with exposeRemote('nonexistent_file.txt') as _:
            pass

def test_expose_file():
    # Create a temporary test file
    test_content = "Hello, World!"
    with open('test_file.txt', 'w') as f:
        f.write(test_content)
    
    try:
        with exposeRemote('test_file.txt') as url:
            assert url.startswith('http')
            assert 'ngrok' in url
    finally:
        # Clean up
        os.remove('test_file.txt')
