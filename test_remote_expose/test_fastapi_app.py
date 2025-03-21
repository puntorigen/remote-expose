#!/usr/bin/env python
import os
import requests
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from remote_expose import exposeRemote, exposeRemoteAsync

app = FastAPI(title="Remote-Expose FastAPI Test")

# Path to our sample file
SAMPLE_FILE_PATH = os.path.join(os.path.dirname(__file__), "files", "sample.txt")

@app.get("/sync-expose")
def sync_expose_endpoint():
    """
    Endpoint that uses the synchronous version of exposeRemote
    """
    try:
        with exposeRemote(SAMPLE_FILE_PATH) as public_url:
            # Verify the file is accessible
            response = requests.get(public_url)
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Failed to access exposed file: {response.status_code}")
            
            return {
                "success": True,
                "message": "File exposed successfully using synchronous API",
                "public_url": public_url,
                "file_content": response.text
            }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/async-expose")
async def async_expose_endpoint():
    """
    Endpoint that uses the asynchronous version of exposeRemoteAsync
    """
    try:
        async with exposeRemoteAsync(SAMPLE_FILE_PATH) as public_url:
            # Verify the file is accessible
            response = requests.get(public_url)
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Failed to access exposed file: {response.status_code}")
            
            return {
                "success": True,
                "message": "File exposed successfully using asynchronous API",
                "public_url": public_url,
                "file_content": response.text
            }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/health")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
