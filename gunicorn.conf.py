import multiprocessing
import os

wsgi_app = "api.app:app"

# Bind to a specific IP address and port.
bind = "0.0.0.0:8080"

# Use the 'uvicorn.workers.UvicornWorker' worker class for FastAPI compatibility.
worker_class = "uvicorn.workers.UvicornWorker"

# Set the number of worker processes based on available CPU cores.
namespace = 'dev'
if namespace == "production":
    workers = multiprocessing.cpu_count() * 2 + 1
else:
    workers = 2

# Define the location for Gunicorn to write its access and error logs.
accesslog = "-"
errorlog = "-"

# Enable logging to stdout/stderr in addition to log files.
capture_output = True

# Enable threading to handle concurrent requests more efficiently.
threads = 10

# Optimize memory usage by preloading the application code.
preload_app = True

# Enable reuse of worker processes to reduce startup time.
reuse_port = True

# timeout = 300
# graceful_timeout = 60
