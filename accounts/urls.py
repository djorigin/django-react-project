"""
URL configuration for accounts app

ENTERPRISE STANDARDIZATION: Phase 3.2 Complete
Professional authentication and profile management with Cotton + Three-Color compliance
"""

from django.urls import path

from . import auth_views, modern_views

app_name = "accounts"

urlpatterns = [
    # ENTERPRISE AUTHENTICATION SYSTEM
    path("login/", auth_views.login_view, name="login"),
    path("register/", auth_views.register_view, name="register"),
    path("logout/", auth_views.logout_view, name="logout"),
    # ENTERPRISE PROFILE SYSTEM - Cotton + Three-Color Compliance
    path("profile/", modern_views.modern_profile_edit, name="profile_edit"),
    path("profile/edit/", modern_views.modern_profile_edit, name="modern_profile_edit"),
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
        modern_views.profile_compliance_status,
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
    # HTMX Geographical Chaining
    path("ajax/state-options/", modern_views.load_states, name="state_options"),
    path("ajax/city-options/", modern_views.load_cities, name="city_options"),
    path("load-states/", modern_views.load_states, name="load_states"),
    path("load-cities/", modern_views.load_cities, name="load_cities"),
    path(
        "load-postal-codes/", modern_views.load_postal_codes, name="load_postal_codes"
    ),
    # Profile Completion Checking
    path(
        "profile/check-complete/",
        modern_views.check_profile_complete,
        name="check_profile_complete",
    ),
]
