"""
URL configuration for accounts app

STRATEGIC UI REBUILD: Phase 3.2 - Authentication System
Professional authentication interfaces with enterprise styling
"""

from django.urls import path

from . import auth_views, profile_views, views

app_name = "accounts"

urlpatterns = [
    # PHASE 3.2: Professional Authentication System
    path("login/", auth_views.login_view, name="login"),
    path("register/", auth_views.register_view, name="register"),
    path("logout/", auth_views.logout_view, name="logout"),
    # TEMPORARILY DISABLED - Will be rebuilt in Phase 3.2
    # path("", views.landing_page, name="landing"),
    # path("dashboard/", views.dashboard, name="dashboard"),
    # path("profile/edit/", profile_views.profile_edit, name="profile_edit"),
    # path("profile/view/", profile_views.profile_view, name="profile_view"),
    # WORKING ENDPOINTS - No templates required
    path(
        "profile/check-complete/",
        profile_views.check_profile_complete,
        name="check_profile_complete",
    ),
    # HTMX endpoints for geographical chained selection (JSON responses)
    path("load-states/", profile_views.load_states, name="load_states"),
    path("load-cities/", profile_views.load_cities, name="load_cities"),
    path(
        "load-postal-codes/", profile_views.load_postal_codes, name="load_postal_codes"
    ),
]
