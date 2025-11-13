# RPAS Business Management System - AI Coding Assistant Instructions

## Project Architecture - CASA-Compliant Drone Operations Platform 🚁

This is a **three-tier distributed Django application** specifically designed for **RPAS (Remotely Piloted Aircraft Systems) business management** with full **CASA (Civil Aviation Safety Authority) regulatory compliance**:

- **Alpha Server (192.168.0.16)**: Django backend + Aviation APIs (current development environment)
- **Beta Server (192.168.0.17)**: React frontend for operations dashboard
- **Delta Server (192.168.0.18)**: PostgreSQL + PostGIS + Redis for aviation data management

### **Business Context: Australian Aviation Compliance**
This system manages **commercial drone operations** under Australian aviation law, specifically:
- **CASA Advisory Circular 101-01**: RPAS operations requirements
- **ReOC (Remote Operator Certificate)**: Business authorization for commercial operations
- **RPC (Remote Pilot Certificate)**: Individual pilot certification and currency
- **Operations Manual**: Comprehensive safety management system
- **Flight Logging**: Detailed operational record keeping
- **Maintenance Tracking**: Aircraft inspection and maintenance compliance

The project implements a **complete aviation business management platform** with authentication, geographical intelligence, pilot certification tracking, aircraft fleet management, flight operations, and regulatory compliance reporting.

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

## Frontend & UI Framework Standards

### **Mandatory UI Stack**
All pages, forms, and user interfaces **MUST** use this consistent technology stack:

#### **Tailwind CSS v4 Standalone**
- **Utility-first CSS**: Use Tailwind classes for all styling
- **No custom CSS**: Avoid writing custom CSS files - use Tailwind utilities
- **Responsive Design**: Mobile-first approach with `sm:`, `md:`, `lg:`, `xl:` breakpoints
- **Component Pattern**: Consistent spacing, colors, typography across all pages
- **Theme App**: Tailwind compiled via `theme/` Django app (no Node.js required)

#### **HTMX Integration**
- **Dynamic Interactions**: Use HTMX for all AJAX requests and dynamic updates
- **Form Submissions**: Replace traditional form posts with `hx-post`, `hx-get`
- **Page Updates**: Use `hx-target`, `hx-swap` for seamless UX
- **Progressive Enhancement**: Pages work without JavaScript, enhanced with HTMX
- **Integration**: `django-htmx` middleware already configured

#### **Django Crispy Forms**
- **Form Rendering**: All Django forms must use Crispy Forms for consistent styling
- **Bootstrap 5 Layout**: Pre-configured with `CRISPY_TEMPLATE_PACK = "bootstrap5"`
- **Tailwind Integration**: Override Crispy templates to use Tailwind classes when practical
- **Complex Forms**: Use Crispy's `Layout`, `Fieldset`, `Row`, `Column` for advanced layouts

#### **Django Cotton (Template Components)**
- **Reusable Components**: All UI elements must use Django Cotton components for consistency
- **Component Directory**: Components stored in `templates/components/`
- **Available Components**: `card`, `button`, `alert` with DarkLight Meta branding
- **Template Loading**: Always add `{% load cotton %}` to templates using Cotton components
- **Easy Maintenance**: Single source of truth for UI patterns across the entire site
- **Consistent Styling**: All components follow DarkLight Meta brand guidelines

### **UI Development Guidelines**
```python
# Example form class with Crispy integration
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {'hx-post': reverse('profile_update')}
        self.helper.layout = Layout(
            Div('first_name', 'last_name', css_class='grid grid-cols-2 gap-4'),
            Submit('submit', 'Update Profile', css_class='bg-blue-500 hover:bg-blue-600 text-white')
        )
```

```html
<!-- Example template with Tailwind + HTMX + Cotton Components -->
{% load cotton %}

{% cotton 'card' title="Update Profile" variant="default" %}
    {% crispy form %}
    <div id="profile-status" class="mt-4"></div>
    
    {% cotton 'button' variant="primary" type="submit" %}
        Update Profile
    {% endcotton %}
{% endcotton %}
```

### **Django Cotton Component Usage**
```html
{% load cotton %}

<!-- Card Component -->
{% cotton 'card' title="Dashboard Stats" variant="accent" size="lg" %}
    <p>Your stats content here</p>
{% endcotton %}

<!-- Button Component -->
{% cotton 'button' variant="primary" href="{% url 'accounts:register' %}" %}
    Get Started
{% endcotton %}

<!-- Alert Component -->
{% cotton 'alert' variant="success" dismissible=True %}
    Profile updated successfully!
{% endcotton %}
```

### **Template Standards**
- **Base Template**: Extend `base.html` which includes Tailwind CSS and HTMX
- **Component Reuse**: Use Django Cotton for reusable template components
- **HTMX Attributes**: Add `hx-*` attributes for dynamic behavior
- **Tailwind Classes**: Use consistent color scheme, spacing, and typography
- **Responsive**: All layouts must work on mobile devices

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

### **Aviation Profile Types**
- **Pilot**: CASA-certified remote pilots with ReOC authority (ARN required, image mandatory)
- **Staff**: Operations managers, safety officers, maintenance personnel (image mandatory)
- **Client**: Commercial customers requiring drone services
- **Customer**: End users of drone services and operations
- **General**: Non-operational system users with limited access
- **CASA Compliance**: Profile types determine access to aviation operations and safety-critical functions
- **Conditional Validation**: Aviation Reference Number (ARN) required for Pilot profiles
- **Image Requirements**: Staff and Pilot profiles require images for identification and security

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

# Tailwind CSS workflow
python3 manage.py tailwind build    # Build CSS for production
python3 manage.py tailwind start    # Watch mode for development
python3 manage.py collectstatic     # Collect static files (includes Tailwind)

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

### **Completed Authentication System**
- ✅ **Complete DarkLight Meta branded authentication system** with landing, login, register, logout, dashboard pages
- ✅ **Django Cotton components** configured in `templates/components/` (`card`, `button`, `alert`)
- ✅ **HTMX integration** for dynamic form interactions without page reloads
- ✅ **Responsive design** with mobile-first Tailwind CSS approach

### **Available Application URLs**
```
Current Routes:
├── / (Landing page with authentication)
├── /login/ (Login page)
├── /register/ (Registration page) 
├── /logout/ (Logout functionality)
├── /dashboard/ (User dashboard - requires auth)
├── /system/ (System status page)
└── /admin/ (Django admin)
```

### **Infrastructure Status**
According to `PROJECT_STATUS.md`:
- ✅ Infrastructure, development environment, CI/CD complete
- ✅ **Nginx + Gunicorn production setup complete**
- ✅ **CustomUser with compliance fields**: Email auth + Australian TFN/ARN validation
- ✅ **Geographical chained selection**: Country → State → City → PostalCode models
- ✅ **Tailwind CSS integration**: v4 standalone with HTMX and Crispy Forms
- ✅ **Authentication system**: Complete with DarkLight Meta branding
- 🔄 **Current phase**: Ready for core application development
- ⏳ Upcoming: API endpoints (DRF), background tasks (Celery), React frontend

### **Development Guidelines**
When creating new Django apps:
- **Follow established UI standards**: Tailwind + HTMX + Crispy Forms + Django Cotton
- **Use DarkLight Meta branding**: Consistent color scheme and component styling
- **Maintain code quality standards**: Black, isort, flake8, bandit
- **Leverage existing components**: Use Cotton components for consistent UI patterns

## CRITICAL: Geographical Data Management 🗺️

### **Data Integrity Requirements**
The geographical chained selection system (Country → State → City → PostalCode) depends on **perfect data relationships** for:
- HTMX chained dropdown functionality
- Automatic coordinate detection
- PostGIS geographical queries
- System-wide location intelligence

### **Access Control Policy**
- **SUPERUSER ONLY**: Geographical data (Countries, States, Cities, PostalCodes) must only be managed by superusers
- **Risk**: Manual data entry by regular users will break system functionality
- **Rationale**: Incorrect relationships can break HTMX chaining, coordinate lookups, and data consistency

### **Future Implementation Requirements**
When implementing geographical data management:

#### **Specialized Admin Interface**
```python
# Custom admin views with enhanced validation
class GeographicalDataAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
```

#### **Required Features**
- **Coordinate Validation**: Ensure lat/lng values are within valid ranges
- **Relationship Integrity**: Verify State belongs to Country, City belongs to State, etc.
- **Bulk Import/Export**: CSV import with validation and error reporting
- **Coordinate Geocoding**: Auto-populate coordinates from place names
- **Data Backup**: Regular exports before major updates

#### **Validation Rules**
- **Coordinate Ranges**: Latitude (-90 to 90), Longitude (-180 to 180)
- **Unique Constraints**: No duplicate cities within the same state
- **Required Fields**: Name, coordinates, parent relationships
- **Active Status**: Maintain is_active flags for soft deletion

#### **Admin Section Design**
- **Separate Admin Section**: `/admin/geographical/` with restricted access
- **Batch Operations**: Bulk activate/deactivate, coordinate updates
- **Data Analytics**: Show usage statistics, popular locations
- **Import Wizard**: Step-by-step CSV import with validation

### **Current Data Status**
- ✅ **250 Countries** with center coordinates
- ✅ **76 Australian States/Territories** with precise coordinates  
- ✅ **155 Australian Cities** with accurate coordinates
- ❌ **0 Postal Codes** - future expansion needed
- ✅ **Smart System**: Handles missing postal codes gracefully with manual input

### **Development Priority**
This geographical data management system should be implemented **before** allowing extensive user profile creation to ensure data consistency from the start.