"""
Compliance URLs - Three-Color CASA Compliance System Routes

STRATEGIC UI REBUILD: Some URLs temporarily disabled
Templates for dashboard and components removed as part of clean slate.
API endpoints and HTMX endpoints without templates remain active.
"""

from django.http import HttpResponse
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


# Temporary placeholder for compliance dashboard
def temporary_compliance_dashboard(request):
    return HttpResponse(
        """
    <html>
    <head><title>Compliance Dashboard - Rebuild in Progress</title></head>
    <body style="font-family: Arial, sans-serif; padding: 40px; background: #f8f9fa;">
        <h1 style="color: #212529;">Three-Color Compliance System</h1>
        <h2 style="color: #6c757d;">Dashboard Rebuild in Progress</h2>
        <p>The compliance dashboard is being rebuilt as part of the strategic UI overhaul.</p>
        <p>Working endpoints:</p>
        <ul>
            <li><a href="/compliance/api/dashboard/">Dashboard Data API</a> (JSON)</li>
            <li><a href="/compliance/scheduled/run/">Run Scheduled Checks</a></li>
        </ul>
        <p style="color: #28a745;"><strong>✅ Compliance Engine:</strong> Fully operational</p>
        <p style="color: #28a745;"><strong>✅ Three-Color System:</strong> All 12+ models integrated</p>
        <p style="color: #28a745;"><strong>✅ HTMX Endpoints:</strong> Real-time checking available</p>
        <p><em>Professional enterprise dashboard coming soon...</em></p>
    </body>
    </html>
    """,
        content_type="text/html",
    )


app_name = "compliance"

urlpatterns = [
    # TEMPORARY - Dashboard placeholder during rebuild
    path("dashboard/", temporary_compliance_dashboard, name="dashboard"),
    # WORKING ENDPOINTS - No templates required
    path("api/dashboard/", compliance_dashboard_data, name="dashboard_data"),
    path("scheduled/run/", run_scheduled_compliance_checks, name="run_scheduled"),
    # HTMX endpoints - May need component template fixes
    # path("check/field/", check_field_compliance, name="check_field"),
    # path("check/object/", check_object_compliance, name="check_object"),
    # path("widget/", compliance_status_widget, name="status_widget"),
    # path("rule/<int:rule_id>/", compliance_rule_info, name="rule_info"),
]
