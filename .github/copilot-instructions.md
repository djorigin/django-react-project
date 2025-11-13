# Django React Project - AI Coding Assistant Instructions

## Project Architecture

This is a **three-tier distributed Django application** with a specific infrastructure setup:
- **Alpha Server (192.168.0.16)**: Django backend + API (current development environment)
- **Beta Server (192.168.0.17)**: React frontend 
- **Delta Server (192.168.0.18)**: PostgreSQL + PostGIS + Redis

The project is currently in **early development phase** - Django backend structure exists but no apps are created yet.

## Key Development Patterns

### Code Quality & Standards
- **Black** formatting (line-length: 88, target Python 3.12)
- **isort** with Django-aware imports: `DJANGO`, `THIRDPARTY`, `FIRSTPARTY`, `LOCALFOLDER`
- **Flake8** linting with migrations excluded
- **Bandit** security scanning (skips B101, B601)
- All tools exclude `migrations/` directories

### Database Strategy  
- **Production**: PostgreSQL 16 + PostGIS on Delta server via `DATABASE_URL`
- **Development**: SQLite3 (current settings.py default)
- **Testing**: PostgreSQL with PostGIS in CI/CD
- **Key**: Always use environment variables for database connections

### Django Project Structure
- Main Django project in `backend/` directory
- `manage.py` commands use `python3` (not `python`)
- Standard Django structure but **no apps created yet**
- Virtual environment in `venv/` (must be activated for development)

## Critical Dependencies

This project uses **advanced Django ecosystem packages**:
```python
# Core stack
Django==5.2.8 + djangorestframework==3.16.1
psycopg2-binary==2.9.11  # PostgreSQL adapter
celery==5.5.3 + django-celery-beat==2.8.1  # Background tasks
redis==7.0.1  # Caching and Celery broker

# Enhanced Django features  
django-extensions==4.1  # Management command extensions
django-debug-toolbar==6.1.0  # Development debugging
django-axes==8.0.0  # Security/login attempt tracking
django-cotton==2.3.1  # Template components
django-htmx==1.26.0  # HTMX integration
django-cors-headers==4.9.0  # API CORS handling
```

## Core Models Architecture

### **Central Hub Pattern**
- **Core App**: Contains foundational models that other apps depend on
- **One-Way Dependencies**: Other apps reference core models, never the reverse
- **Data Normalization**: Each piece of data stored only once

### **Custom User System**
- **Email-based Authentication**: No username, email + password only
- **UUID Primary Keys**: Better for distributed systems and APIs
- **Profile Hierarchy**: BaseProfile with ProfileType for extensibility

### **Geographical Models (Chained Selection)**
```python
# Normalized geographical hierarchy
Country → State → City → PostalCode
```
- **Chained Selection**: Country filters states, state filters cities, etc.
- **PostGIS Integration**: Latitude/longitude fields for mapping (Leaflet)
- **Reusable**: Used across all apps needing location data
- **Data Normalization**: Cities, states, countries stored once, referenced many times

### **Profile Types**
- General User, Staff, Pilot, Client, Customer
- **Image Requirements**: Staff and Pilot profiles require images  
- **Conditional Validation**: Enforced at model level
- **Extensible**: Easy to add new profile types without code changes

## Essential Commands

### Development Workflow
```bash
# Always activate venv first
source venv/bin/activate

# Django commands (use python3, not python)
python3 manage.py check           # System validation
python3 manage.py migrate         # Apply migrations
python3 manage.py runserver       # Development server
python3 manage.py shell           # Django shell

# Production-like serving (Nginx + Gunicorn)
sudo systemctl start django-gunicorn    # Start gunicorn service
sudo systemctl status django-gunicorn   # Check service status
sudo systemctl reload nginx             # Reload Nginx config
curl http://192.168.0.16                # Test external access

# Code quality (run before commits)
black .                          # Format code
isort .                         # Sort imports
flake8 .                        # Lint code
bandit -r .                     # Security scan
```

### CI/CD Integration
- **GitHub Actions** workflow in `.github/workflows/django.yml`
- **Two-stage pipeline**: lint-and-format → test
- **Services**: PostgreSQL + PostGIS + Redis containers
- **System deps**: `gdal-bin libgdal-dev` for PostGIS support

## Project-Specific Conventions

### Settings Architecture
- `backend/settings.py` currently uses SQLite3 default
- **Production settings** should use `DATABASE_URL` and `REDIS_URL` environment variables  
- Security: `SECRET_KEY` needs environment variable for production

### Testing Strategy
- CI runs full PostgreSQL + PostGIS + Redis stack
- Tests should be environment-agnostic via environment variables
- Command: `python3 manage.py test --verbosity=2`

### Import Organization (isort)
```python
# Standard library
import os
from pathlib import Path

# Third-party packages  
import celery
import redis

# Django packages
from django.db import models
from django.contrib.auth.models import User

# First-party (your project)
from backend.settings import BASE_DIR

# Local imports
from .models import YourModel
```

## Infrastructure Context

When creating database models or Celery tasks, remember:
- **PostGIS capabilities** available (geospatial data support)
- **Redis** available for caching and async task queues
- **Multi-server deployment** - design for distributed architecture
- **Environment-based configuration** - avoid hardcoded connections

## Production Infrastructure

### Nginx + Gunicorn Setup
- **Nginx**: Reverse proxy on port 80, serves static files
- **Gunicorn**: WSGI server on 127.0.0.1:8000 with 9 workers
- **Systemd service**: `django-gunicorn.service` for auto-restart
- **Configuration files**: `nginx.conf` and `gunicorn.conf.py` in project root
- **ALLOWED_HOSTS**: Configured for `192.168.0.16`, `localhost`, `alpha`

## Current Development State

According to `PROJECT_STATUS.md`:
- ✅ Infrastructure, development environment, CI/CD complete
- ✅ **Nginx + Gunicorn production setup complete**
- 🔄 **Next phase**: Create Django CustomUsers
- ⏳ Upcoming: Configure database connections to Delta, set up DRF + Celery

When creating new Django apps, follow the established code quality standards and remember the distributed architecture context.