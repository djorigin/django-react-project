"""
Compliance URLs - Three-Color CASA Compliance System Routes

URL configuration for the revolutionary three-color compliance system.
Provides HTMX endpoints and views for real-time compliance checking.

URL Patterns:
- /compliance/check/field/ - Real-time field validation
- /compliance/check/object/ - Object compliance checking
- /compliance/dashboard/ - Main compliance dashboard
- /compliance/widget/ - Status widget for embedding
- /compliance/api/data/ - Dashboard data API
- /compliance/scheduled/ - Run scheduled checks
- /compliance/rule/<id>/ - Rule information modal
"""

from django.urls import path

from .compliance_views import (
    ComplianceDashboardView,
    check_field_compliance,
    check_object_compliance,
    compliance_dashboard_data,
    compliance_rule_info,
    compliance_status_widget,
    run_scheduled_compliance_checks,
)

app_name = "compliance"

urlpatterns = [
    # Main compliance dashboard
    path("dashboard/", ComplianceDashboardView.as_view(), name="dashboard"),
    # HTMX endpoints for real-time checking
    path("check/field/", check_field_compliance, name="check_field"),
    path("check/object/", check_object_compliance, name="check_object"),
    # Status widgets and data endpoints
    path("widget/", compliance_status_widget, name="status_widget"),
    path("api/dashboard/", compliance_dashboard_data, name="dashboard_data"),
    # Administrative endpoints
    path("scheduled/run/", run_scheduled_compliance_checks, name="run_scheduled"),
    # Rule information
    path("rule/<int:rule_id>/", compliance_rule_info, name="rule_info"),
]
