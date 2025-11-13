"""
URL configuration for accounts app
"""

from django.urls import path

from . import profile_views, views

app_name = "accounts"

urlpatterns = [
    # Authentication URLs
    path("", views.landing_page, name="landing"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    # Profile URLs
    path("profile/edit/", profile_views.profile_edit, name="profile_edit"),
    path("profile/view/", profile_views.profile_view, name="profile_view"),
    path(
        "profile/check-complete/",
        profile_views.check_profile_complete,
        name="check_profile_complete",
    ),
    # HTMX endpoints for geographical chained selection
    path("load-states/", profile_views.load_states, name="load_states"),
    path("load-cities/", profile_views.load_cities, name="load_cities"),
    path(
        "load-postal-codes/", profile_views.load_postal_codes, name="load_postal_codes"
    ),
]
