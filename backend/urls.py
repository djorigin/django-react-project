"""
URL configuration for backend project.

PHASE 3 ENTERPRISE UI: Production-ready URL configuration
Professional authentication and dashboard system operational
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from .views import dashboard_view


# Root URL redirect - Smart routing based on authentication
def root_redirect(request):
    """Smart redirect: authenticated users to dashboard, guests to login"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("accounts:login")


urlpatterns = [
    # Root URL - Smart redirect based on authentication
    path("", root_redirect, name="home"),
    # PHASE 3: Enterprise Authentication System (Operational)
    path("accounts/", include("accounts.urls")),
    # PHASE 3: Profile-Aware Dashboard System (Operational)
    path("dashboard/", dashboard_view, name="dashboard"),
    # Three-Color Compliance System (Universal ComplianceMixin operational)
    path("compliance/", include("core.compliance_urls")),
    # System Administration
    path("admin/", admin.site.urls),
    # Development/Status Pages
    path("system/", dashboard_view, name="system_home"),  # Redirect to main dashboard
    # Future Implementation - Prepared for next phase
    # path("api/", include("api.urls")),           # REST API endpoints
    # path("operations/", include("ops.urls")),    # Flight operations
    # path("maintenance/", include("f2.urls")),    # F2 technical log
    # path("safety/", include("sms.urls")),        # Safety management
]

# Add debug toolbar URLs in development
if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        # path("__reload__/", include("django_browser_reload.urls")),  # Disabled for form testing
    ]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
