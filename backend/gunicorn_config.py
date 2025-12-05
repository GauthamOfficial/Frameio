# Gunicorn configuration file for Frameio Backend
import multiprocessing
import os
from pathlib import Path

# Get the backend directory
BASE_DIR = Path(__file__).resolve().parent

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
# Use 2 * CPU cores + 1 workers for optimal performance
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
# Create logs directory if it doesn't exist
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

accesslog = str(logs_dir / "gunicorn_access.log")
errorlog = str(logs_dir / "gunicorn_error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "frameio_backend"

# Server mechanics
daemon = False
pidfile = str(logs_dir / "frameio_backend.pid")
umask = 0
user = None
group = None
tmp_upload_dir = None

# Graceful timeout for worker restarts
graceful_timeout = 30

# Maximum requests per worker before restart (helps prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload app for better performance
preload_app = True

# SSL (if using HTTPS directly with Gunicorn - not recommended, use Nginx instead)
# keyfile = None
# certfile = None

