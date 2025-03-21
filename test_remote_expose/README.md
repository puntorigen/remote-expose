# Remote-Expose Test Suite

This test suite verifies that the `remote-expose` package works correctly in both standalone Python scripts and FastAPI applications.

## Structure

- `files/sample.txt` - Sample file used for testing
- `test_standalone.py` - Tests the package in a standalone Python script
- `test_fastapi_app.py` - A FastAPI application with endpoints using both sync and async versions
- `run_tests.py` - Main script that runs all tests and reports results
- `requirements.txt` - Required dependencies

## Running the Tests

Make sure you have installed the required dependencies:

```bash
pip install -r requirements.txt
pip install -e /path/to/remote-expose
```

Then run the test suite:

```bash
python run_tests.py
```

## Test Scenarios

The test suite verifies the following scenarios:

1. **Standalone Tests**:
   - Tests the synchronous `exposeRemote` context manager
   - Tests the asynchronous `exposeRemoteAsync` context manager

2. **FastAPI Integration Tests**:
   - Tests a synchronous endpoint using `exposeRemote`
   - Tests an asynchronous endpoint using `exposeRemoteAsync`

## Expected Behavior

Both the standalone script and FastAPI application should successfully:
- Create a temporary web server
- Establish an ngrok tunnel
- Expose the sample file via the tunnel
- Return a valid public URL
- Allow the file to be accessed via the public URL

If all tests pass, the `remote-expose` package works correctly in both contexts.
