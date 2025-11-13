# Gunicorn configuration file for Django development
# Place this in your project root as gunicorn.conf.py

import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Logging
errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "django_project_gunicorn"

# Server mechanics
daemon = False
pidfile = "/home/djangoadmin/django_project/gunicorn.pid"  # Use project directory
user = None
group = None
tmp_upload_dir = None

# Django settings module
env = {"DJANGO_SETTINGS_MODULE": "backend.settings"}

# Development specific settings
reload = True
reload_extra_files = []
