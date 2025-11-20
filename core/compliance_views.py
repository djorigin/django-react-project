"""
Compliance Views - Three-Color CASA Compliance HTMX Endpoints

HTMX-powered views for real-time compliance checking and status updates.
These views provide the backbone for the revolutionary three-color compliance
system's dynamic user interface.

Features:
- Real-time compliance checking via HTMX
- Dynamic form field validation
- Live status updates without page reload
- Compliance dashboard data endpoints
- Object-specific compliance validation

Design Philosophy:
- Lightweight HTMX responses
- Progressive enhancement
- Graceful degradation
- Performance-optimized queries
"""

import json
from typing import Any, Dict, Optional

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from .compliance_engine import compliance_engine
from .models import ComplianceCheck, ComplianceMixin, ComplianceRule, ComplianceStatus


@require_http_methods(["POST"])
@login_required
def check_field_compliance(request: HttpRequest) -> HttpResponse:
    """
    HTMX endpoint for real-time field compliance checking.

    Validates individual form fields and returns compliance status
    with visual feedback for immediate user response.

    Expected POST data:
    - field_name: Name of the field being validated
    - field_value: Current value of the field
    - object_id: ID of the object (if editing existing)
    - content_type: Content type of the object
    - context_data: Additional context for validation
    """
    field_name = request.POST.get("field_name")
    field_value = request.POST.get("field_value")
    object_id = request.POST.get("object_id")
    content_type_id = request.POST.get("content_type")

    # Default response
    response_data = {
        "status": ComplianceStatus.GREEN,
        "message": "Field validation passed",
        "field_name": field_name,
        "errors": [],
    }

    # Perform field-specific validation
    try:
        # If we have an object context, validate against it
        if object_id and content_type_id:
            content_type = get_object_or_404(ContentType, id=content_type_id)
            model_class = content_type.model_class()

            if issubclass(model_class, ComplianceMixin):
                obj = get_object_or_404(model_class, id=object_id)

                # Run compliance checks on the object
                compliance_result = compliance_engine.check_object_compliance(
                    obj, user=request.user
                )

                response_data["status"] = compliance_result["overall_status"]
                response_data["message"] = "Compliance check completed"

                # Add any field-specific issues
                for rule_result in compliance_result.get("rule_results", []):
                    if rule_result["status"] != ComplianceStatus.GREEN:
                        response_data["errors"].append(rule_result["message"])

        # Basic field validation (can be extended)
        if not field_value or field_value.strip() == "":
            response_data["status"] = ComplianceStatus.YELLOW
            response_data["message"] = "Field requires validation"

    except Exception as e:
        response_data = {
            "status": ComplianceStatus.RED,
            "message": f"Validation error: {str(e)}",
            "field_name": field_name,
            "errors": [str(e)],
        }

    # Return HTMX-compatible response
    return render(request, "components/compliance_field_status.html", response_data)


@require_http_methods(["POST"])
@login_required
def check_object_compliance(request: HttpRequest) -> HttpResponse:
    """
    HTMX endpoint for comprehensive object compliance checking.

    Performs full compliance evaluation for an object and returns
    updated compliance card with current status.

    Expected POST data:
    - object_id: ID of the object to check
    - content_type: Content type identifier
    """
    object_id = request.POST.get("object_id")
    content_type_name = request.POST.get("content_type")

    try:
        # Get the object
        if "." in content_type_name:
            app_label, model = content_type_name.split(".", 1)
            content_type = get_object_or_404(
                ContentType, app_label=app_label, model=model
            )
        else:
            content_type = get_object_or_404(ContentType, model=content_type_name)

        model_class = content_type.model_class()
        obj = get_object_or_404(model_class, id=object_id)

        if not isinstance(obj, ComplianceMixin):
            return JsonResponse(
                {"error": "Object does not support compliance checking"}, status=400
            )

        # Run comprehensive compliance check
        compliance_result = compliance_engine.check_object_compliance(
            obj, user=request.user
        )

        # Render updated compliance card
        return render(
            request,
            "components/compliance_card.html",
            {"object": obj, "compliance_result": compliance_result},
        )

    except Exception as e:
        return render(
            request, "components/compliance_error.html", {"error_message": str(e)}
        )


@require_http_methods(["GET"])
@login_required
def compliance_dashboard_data(request: HttpRequest) -> JsonResponse:
    """
    HTMX/JSON endpoint for compliance dashboard statistics.

    Provides real-time compliance data for dashboard widgets
    and monitoring interfaces.
    """
    try:
        dashboard_data = compliance_engine.get_compliance_dashboard_data()
        return JsonResponse(dashboard_data)

    except Exception as e:
        return JsonResponse({"error": f"Dashboard data error: {str(e)}"}, status=500)


@require_http_methods(["POST"])
@login_required
def run_scheduled_compliance_checks(request: HttpRequest) -> HttpResponse:
    """
    HTMX endpoint to trigger scheduled compliance checks.

    Runs all overdue compliance checks and returns summary
    of results for admin monitoring.
    """
    try:
        results = compliance_engine.run_scheduled_compliance_checks(user=request.user)

        return render(
            request, "compliance/scheduled_check_results.html", {"results": results}
        )

    except Exception as e:
        return render(request, "compliance/check_error.html", {"error_message": str(e)})


@require_http_methods(["GET"])
@login_required
def compliance_status_widget(request: HttpRequest) -> HttpResponse:
    """
    HTMX endpoint for compliance status widget updates.

    Returns a lightweight compliance status widget that can be
    embedded in any page for real-time compliance monitoring.

    Query parameters:
    - object_id: ID of specific object to monitor
    - content_type: Content type of the object
    - widget_size: 'small'|'medium'|'large' (default: 'medium')
    """
    object_id = request.GET.get("object_id")
    content_type_name = request.GET.get("content_type")
    widget_size = request.GET.get("widget_size", "medium")

    context = {"widget_size": widget_size, "timestamp": timezone.now()}

    if object_id and content_type_name:
        try:
            # Get specific object status
            content_type = get_object_or_404(ContentType, model=content_type_name)
            model_class = content_type.model_class()
            obj = get_object_or_404(model_class, id=object_id)

            if isinstance(obj, ComplianceMixin):
                context.update(
                    {
                        "object": obj,
                        "status": obj.compliance_status,
                        "summary": obj.get_compliance_summary(),
                    }
                )

        except Exception:
            # Fallback to system-wide status
            pass

    if "object" not in context:
        # Get system-wide compliance status
        dashboard_data = compliance_engine.get_compliance_dashboard_data()
        total_checks = dashboard_data["total_checks"]
        failed_checks = dashboard_data["red_checks"] + dashboard_data["yellow_checks"]

        if failed_checks == 0:
            status = ComplianceStatus.GREEN
        elif dashboard_data["red_checks"] > 0:
            status = ComplianceStatus.RED
        else:
            status = ComplianceStatus.YELLOW

        context.update(
            {
                "status": status,
                "total_checks": total_checks,
                "failed_checks": failed_checks,
                "system_wide": True,
            }
        )

    return render(request, "components/compliance_status_widget.html", context)


@method_decorator(login_required, name="dispatch")
class ComplianceDashboardView(TemplateView):
    """
    Main compliance dashboard view with HTMX-powered live updates.

    Provides comprehensive compliance monitoring interface with:
    - Real-time status updates
    - Compliance statistics and trends
    - Failed compliance details
    - Scheduled check management
    - Rule management interface
    """

    template_name = "compliance/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Get comprehensive compliance data
        dashboard_data = compliance_engine.get_compliance_dashboard_data()

        context.update(
            {
                "dashboard_data": dashboard_data,
                "failed_checks": ComplianceCheck.objects.filter(
                    status__in=[ComplianceStatus.YELLOW, ComplianceStatus.RED],
                    rule__is_active=True,
                ).select_related("rule", "content_type")[:10],
                "overdue_checks": compliance_engine.get_overdue_checks()[:10],
                "compliance_rules": ComplianceRule.objects.filter(
                    is_active=True
                ).order_by("rule_code"),
                "page_title": "CASA Compliance Dashboard",
            }
        )

        return context


@require_http_methods(["GET"])
def compliance_rule_info(request: HttpRequest, rule_id: int) -> HttpResponse:
    """
    HTMX endpoint for compliance rule details modal/popup.

    Returns detailed information about a specific compliance rule
    for user education and transparency.
    """
    rule = get_object_or_404(ComplianceRule, id=rule_id)

    # Get recent checks for this rule
    recent_checks = (
        ComplianceCheck.objects.filter(rule=rule)
        .select_related("content_type")
        .order_by("-last_checked")[:5]
    )

    return render(
        request,
        "compliance/rule_detail_modal.html",
        {"rule": rule, "recent_checks": recent_checks},
    )
