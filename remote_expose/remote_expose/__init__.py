import os
import http.server
import socketserver
import threading
import time
import logging
import asyncio
from contextlib import contextmanager, asynccontextmanager
from pyngrok import ngrok
from typing import Optional, Union
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NonBlockingTCPServer(socketserver.TCPServer):
    def __init__(self, *args, **kwargs):
        self.timeout = 1
        super().__init__(*args, **kwargs)
        self.socket.settimeout(1)
        self.allow_reuse_address = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def shutdown(self):
        self.socket.close()

class ServerManager:
    _instance: Optional['ServerManager'] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ServerManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.PORT = 8000
        self._server = None
        self._server_thread = None
        self._ngrok_tunnel = None
        self._public_url = None
        self._ref_count = 0
        self._server_lock = threading.Lock()
        self._running = threading.Event()

    def serve_forever(self, httpd):
        self._running.set()
        while self._running.is_set():
            try:
                httpd.handle_request()
            except (socket.timeout, socket.error):
                continue
            except Exception as e:
                if self._running.is_set():
                    logger.debug(f"Server error: {e}")
        logger.debug("Server stopped")

    def start_server(self, handler_class=None):
        with self._server_lock:
            if self._server is not None:
                return

            try:
                logger.info("Starting server...")
                handler = handler_class if handler_class else SimpleHTTPRequestHandlerNoListing
                self._server = NonBlockingTCPServer(("", self.PORT), handler)
                self._server_thread = threading.Thread(target=self.serve_forever, 
                                                    args=(self._server,))
                self._server_thread.daemon = True
                self._server_thread.start()
            except Exception as e:
                self._server = None
                self._server_thread = None
                self._running.clear()
                raise RuntimeError(f"Failed to start server: {e}")

    def start_ngrok(self):
        with self._server_lock:
            if self._ngrok_tunnel is None:
                logger.info("Starting ngrok tunnel...")
                self._ngrok_tunnel = ngrok.connect(self.PORT)
                self._public_url = self._ngrok_tunnel.public_url
                logger.info(f"Tunnel established at {self._public_url}")

    def cleanup(self):
        """Forcefully cleanup all resources"""
        if self._ngrok_tunnel:
            try:
                ngrok.disconnect(self._public_url)
            except Exception as e:
                logger.debug(f"Error during ngrok disconnect: {e}")
            finally:
                self._ngrok_tunnel = None
                self._public_url = None
        
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
            except Exception as e:
                logger.debug(f"Error during server shutdown: {e}")
            finally:
                self._server = None
        
        self._server_thread = None

    def stop_server(self):
        with self._server_lock:
            if self._server is not None and self._ref_count == 0:
                self.cleanup()

    def stop_ngrok(self):
        with self._server_lock:
            if self._ngrok_tunnel is not None and self._ref_count == 0:
                self.cleanup()

    def get_file_url(self, filename: str) -> str:
        return f"{self._public_url}/{filename}"

    def increment_ref(self):
        with self._server_lock:
            self._ref_count += 1
            logger.debug(f"Active connections: {self._ref_count}")

    def decrement_ref(self):
        with self._server_lock:
            self._ref_count -= 1
            logger.debug(f"Active connections: {self._ref_count}")
            if self._ref_count == 0:
                self.cleanup()

class SimpleHTTPRequestHandlerNoListing(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self._directory = directory
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.send_error(403, "Directory listing forbidden")
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, format, *args):
        if self.path != '/favicon.ico':  # Skip favicon requests
            logger.debug(f"{self.client_address[0]} - {format%args}")

@contextmanager
def exposeRemote(filepath: str) -> str:
    """
    Context manager that exposes a local file through a public ngrok URL.
    Multiple files can be exposed simultaneously using the same server.
    
    Args:
        filepath (str): Path to the local file to expose
    
    Yields:
        str: Public ngrok URL where the file can be accessed
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found")

    directory = os.path.dirname(os.path.abspath(filepath))
    filename = os.path.basename(filepath)
    
    server_manager = ServerManager()
    
    try:
        handler = lambda *args, **kwargs: SimpleHTTPRequestHandlerNoListing(*args, directory=directory, **kwargs)
        server_manager.start_server(handler)
        server_manager.start_ngrok()
        server_manager._ref_count += 1
        
        yield f"{server_manager._public_url}/{filename}"
    finally:
        with server_manager._server_lock:
            server_manager._ref_count -= 1
            if server_manager._ref_count == 0:
                server_manager._running.clear()
                if server_manager._server:
                    server_manager._server.shutdown()
                    server_manager._server = None
                if server_manager._server_thread:
                    server_manager._server_thread.join()
                    server_manager._server_thread = None
                server_manager.cleanup()

@asynccontextmanager
async def exposeRemoteAsync(filepath: str) -> str:
    """
    Async context manager that exposes a local file through a public ngrok URL.
    Multiple files can be exposed simultaneously using the same server.
    
    Args:
        filepath (str): Path to the local file to expose
    
    Yields:
        str: Public ngrok URL where the file can be accessed
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found")

    directory = os.path.dirname(os.path.abspath(filepath))
    filename = os.path.basename(filepath)
    
    server_manager = ServerManager()
    
    try:
        handler = lambda *args, **kwargs: SimpleHTTPRequestHandlerNoListing(*args, directory=directory, **kwargs)
        server_manager.start_server(handler)
        server_manager.start_ngrok()
        server_manager._ref_count += 1
        
        yield f"{server_manager._public_url}/{filename}"
    finally:
        with server_manager._server_lock:
            server_manager._ref_count -= 1
            if server_manager._ref_count == 0:
                server_manager._running.clear()
                if server_manager._server:
                    server_manager._server.shutdown()
                    server_manager._server = None
                if server_manager._server_thread:
                    await asyncio.get_event_loop().run_in_executor(None, server_manager._server_thread.join)
                    server_manager._server_thread = None
                server_manager.cleanup()
