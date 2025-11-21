"""
URL configuration for accounts app

ENTERPRISE STANDARDIZATION: Phase 3.2 Complete
Professional authentication and profile management with Cotton + Three-Color compliance
"""

from django.urls import path

from . import auth_views, modern_views, profile_views, views

app_name = "accounts"

urlpatterns = [
    # PHASE 3.2: Professional Authentication System
    path("login/", auth_views.login_view, name="login"),
    path("register/", auth_views.register_view, name="register"),
    path("logout/", auth_views.logout_view, name="logout"),
    # ENTERPRISE PROFILE SYSTEM - Cotton + Three-Color Compliance
    path(
        "profile/modern/", modern_views.modern_profile_edit, name="modern_profile_edit"
    ),
    path(
        "profile/compliance-status/",
        modern_views.profile_compliance_status,
        name="profile_compliance_status",
    ),
    path(
        "profile/field-compliance/",
        modern_views.field_compliance_check,
        name="field_compliance_check",
    ),
    path(
        "profile/overall-compliance/",
        modern_views.overall_compliance_status,
        name="overall_compliance_status",
    ),
    # HTMX Section Loading
    path(
        "profile/tax-info-section/",
        modern_views.tax_info_section,
        name="tax_info_section",
    ),
    path(
        "profile/aviation-info-section/",
        modern_views.aviation_info_section,
        name="aviation_info_section",
    ),
    # HTMX Geographical Chaining (Enterprise Style)
    path("ajax/state-options/", modern_views.state_options, name="state_options"),
    path("ajax/city-options/", modern_views.city_options, name="city_options"),
    # TEMPORARILY DISABLED - Will be rebuilt in Phase 3.3
    # path("", views.landing_page, name="landing"),
    # path("dashboard/", views.dashboard, name="dashboard"),
    # path("profile/edit/", profile_views.profile_edit, name="profile_edit"),
    # path("profile/view/", profile_views.profile_view, name="profile_view"),
    # LEGACY ENDPOINTS - Still functional for compatibility
    path(
        "profile/check-complete/",
        profile_views.check_profile_complete,
        name="check_profile_complete",
    ),
    path("load-states/", profile_views.load_states, name="load_states"),
    path("load-cities/", profile_views.load_cities, name="load_cities"),
    path(
        "load-postal-codes/", profile_views.load_postal_codes, name="load_postal_codes"
    ),
]
