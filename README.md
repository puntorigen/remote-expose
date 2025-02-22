# remote-expose

A Python package that allows you to easily expose local files through a public URL using ngrok.

## Installation

```bash
pip install remote-expose
```

## Usage

```python
from remote_expose import exposeRemote, exposeRemoteAsync

# Synchronous usage with context manager
with exposeRemote('path/to/your/file.txt') as url:
    print(f"Your file is available at: {url}")
    # The file will be accessible at the URL while in this context
    # Once the context is exited, the tunnel will be closed if no other files are being exposed

# Multiple files can be exposed simultaneously
with exposeRemote('file1.txt') as url1, exposeRemote('file2.txt') as url2:
    print(f"File 1 is at: {url1}")
    print(f"File 2 is at: {url2}")

# Async usage with async context manager
import asyncio

async def expose_files():
    async with exposeRemoteAsync('file1.txt') as url1, \
              exposeRemoteAsync('file2.txt') as url2:
        print(f"File 1 is at: {url1}")
        print(f"File 2 is at: {url2}")
        await asyncio.sleep(60)  # Keep files exposed for 60 seconds

# Run the async function
asyncio.run(expose_files())
```

## Features

- Easy-to-use context manager interface
- Async support with async context manager
- Automatic resource cleanup
- Support for exposing multiple files simultaneously
- Secure file serving (no directory listing)
- Thread-safe implementation
- Automatic port management
- Efficient resource sharing (single server for multiple files)

## Requirements

- Python 3.7+
- ngrok account (free tier works fine)
- pyngrok

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
