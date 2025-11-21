"""
Modern Profile Views using Enterprise Standards

This demonstrates the new standard for all views in the application:
- Cotton template integration
- Three-color compliance system
- Professional error handling
- HTMX real-time interactions
- Enterprise styling throughout

This establishes patterns for use across rpas/, sms/, aviation/ apps.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from core.models import BaseProfile, City, Country, PostalCode, ProfileType, State

from .modern_forms import ModernProfileForm


@login_required
@require_http_methods(["GET", "POST"])
def modern_profile_edit(request):
    """
    Modern profile editing view demonstrating enterprise standards

    Features:
    - Cotton template integration
    - Three-color compliance feedback
    - Professional error handling
    - HTMX real-time updates
    - Enterprise styling
    """

    # Get or create profile with default General type
    try:
        profile = request.user.profile
    except BaseProfile.DoesNotExist:
        general_type = ProfileType.objects.get(code="general")
        profile = BaseProfile.objects.create(
            user=request.user, profile_type=general_type
        )

    if request.method == "POST":
        form = ModernProfileForm(
            request.POST, request.FILES, instance=profile, user=request.user
        )

        if form.is_valid():
            with transaction.atomic():
                updated_profile = form.save()

                # Success message with three-color system
                success_msg = "Profile updated successfully!"

                # Check compliance status for contextual messaging
                if hasattr(updated_profile, "get_compliance_summary"):
                    compliance = updated_profile.get_compliance_summary()
                    if compliance["overall_status"] == "green":
                        success_msg += " ✅ All compliance requirements met."
                    elif compliance["overall_status"] == "yellow":
                        success_msg += (
                            " ⚠️ Some recommended fields still need attention."
                        )
                    elif compliance["overall_status"] == "red":
                        success_msg += (
                            " 🔴 Critical compliance requirements still missing."
                        )

                # Handle HTMX vs regular request
                if request.headers.get("HX-Request"):
                    # HTMX response with updated form
                    context = {
                        "form": ModernProfileForm(
                            instance=updated_profile, user=request.user
                        ),
                        "profile": updated_profile,
                        "success_message": success_msg,
                    }
                    html = render_to_string(
                        "accounts/modern_profile_form.html", context, request=request
                    )
                    return HttpResponse(html)
                else:
                    # Regular form submission
                    messages.success(request, success_msg)
                    return redirect("accounts:profile_edit")
        else:
            # Handle form errors with three-color system
            if request.headers.get("HX-Request"):
                # HTMX error response
                context = {
                    "form": form,
                    "profile": profile,
                    "error_message": "Please correct the errors below.",
                }
                html = render_to_string(
                    "accounts/modern_profile_form.html", context, request=request
                )
                return HttpResponse(html)
            else:
                # Regular form error handling
                messages.error(request, "Please correct the errors below.")
    else:
        # GET request - show form
        form = ModernProfileForm(instance=profile, user=request.user)

    context = {
        "form": form,
        "profile": profile,
        "page_title": "Profile Settings",
        "page_subtitle": "Manage your professional profile and CASA compliance information",
    }

    # Use Cotton-based template for modern UI
    return render(request, "accounts/modern_profile_edit.html", context)


@login_required
@require_http_methods(["GET"])
def profile_compliance_status(request):
    """
    HTMX endpoint for real-time compliance status display

    Returns colored compliance indicators for profile
    """
    try:
        profile = request.user.profile

        if hasattr(profile, "get_compliance_summary"):
            compliance = profile.get_compliance_summary()
            status = compliance["overall_status"]

            # Generate compliance indicator HTML
            indicators = {
                "green": {
                    "class": "bg-green-100 text-green-800 border-green-200",
                    "icon": "✅",
                    "text": "Fully Compliant",
                },
                "yellow": {
                    "class": "bg-yellow-100 text-yellow-800 border-yellow-200",
                    "icon": "⚠️",
                    "text": "Attention Required",
                },
                "red": {
                    "class": "bg-red-100 text-red-800 border-red-200",
                    "icon": "🔴",
                    "text": "Critical Issues",
                },
            }

            indicator = indicators.get(status, indicators["yellow"])

            html = f"""
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {indicator['class']}">
                    {indicator['icon']} {indicator['text']}
                </span>
            """

            return HttpResponse(html)
        else:
            return HttpResponse(
                '<span class="text-sm text-gray-500">No compliance data</span>'
            )

    except BaseProfile.DoesNotExist:
        return HttpResponse(
            '<span class="text-sm text-red-500">Profile not found</span>'
        )


# Geographical HTMX endpoints for chained selection
@login_required
@require_http_methods(["GET"])
def load_states(request):
    """
    HTMX endpoint for loading states based on country selection
    """
    country_id = request.GET.get("country")
    states = State.objects.filter(country_id=country_id, is_active=True).order_by(
        "name"
    )

    html = """<select name="state" id="id_state"
                      class="block w-full px-3 py-2 text-sm rounded-md transition-colors duration-200 border-enterprise-gray-300 focus:border-professional-blue focus:ring-professional-blue-light"
                      hx-get="/accounts/load-cities/"
                      hx-target="#id_city_direct"
                      hx-trigger="change"
                      hx-swap="outerHTML"
                      hx-include='[name="state"]'
                      hx-indicator="#geo-loading">
                <option value="">Select State/Province</option>"""

    for state in states:
        html += f'<option value="{state.id}">{state.name}</option>'

    html += "</select>"

    return HttpResponse(html)


@login_required
@require_http_methods(["GET"])
def load_cities(request):
    """
    HTMX endpoint for loading cities based on state selection
    """
    state_id = request.GET.get("state")
    cities = City.objects.filter(state_id=state_id, is_active=True).order_by("name")

    html = """<select name="city_direct" id="id_city_direct"
                      class="block w-full px-3 py-2 text-sm rounded-md transition-colors duration-200 border-enterprise-gray-300 focus:border-professional-blue focus:ring-professional-blue-light"
                      hx-get="/accounts/load-postal-codes/"
                      hx-target="#id_postal_code_select"
                      hx-trigger="change"
                      hx-swap="outerHTML"
                      hx-include='[name="city_direct"]'
                      hx-indicator="#geo-loading">
                <option value="">Select City/Town</option>"""

    for city in cities:
        html += f'<option value="{city.id}">{city.name}</option>'

    html += "</select>"

    return HttpResponse(html)


@login_required
@require_http_methods(["GET"])
def load_postal_codes(request):
    """
    HTMX endpoint for loading postal codes based on city selection
    """
    city_id = request.GET.get("city_direct")
    postal_codes = PostalCode.objects.filter(city_id=city_id, is_active=True).order_by(
        "code"
    )

    html = """<select name="postal_code_select" id="id_postal_code_select"
                      class="block w-full px-3 py-2 text-sm rounded-md transition-colors duration-200 border-enterprise-gray-300 focus:border-professional-blue focus:ring-professional-blue-light">
                <option value="">Select Postal Code (Optional)</option>"""

    for postal_code in postal_codes:
        html += f'<option value="{postal_code.id}">{postal_code.code}</option>'

    html += "</select>"

    return HttpResponse(html)


@login_required
@require_http_methods(["GET"])
def field_compliance_check(request):
    """
    HTMX endpoint for real-time field compliance checking

    This demonstrates the pattern for compliance checking across all apps
    """
    field_name = request.GET.get("field")
    field_value = request.GET.get(field_name)

    try:
        profile = request.user.profile
        profile_type = profile.profile_type.code if profile.profile_type else "general"

        # Field-specific compliance logic
        compliance_status = "default"
        message = ""

        if field_name == "arn_number":
            if profile_type == "pilot":
                if not field_value:
                    compliance_status = "red"
                    message = "🔴 Aviation Reference Number required for Pilot profiles"
                else:
                    compliance_status = "green"
                    message = "✅ ARN provided for CASA compliance"
            else:
                compliance_status = "yellow" if not field_value else "green"
                message = "⚠️ ARN not required for this profile type"

        elif field_name == "tax_file_number":
            if profile_type in ["staff", "pilot"]:
                if not field_value:
                    compliance_status = "yellow"
                    message = "⚠️ Tax File Number recommended for Staff/Pilot profiles"
                else:
                    compliance_status = "green"
                    message = "✅ Tax File Number provided"

        elif field_name == "date_of_birth":
            if profile_type in ["staff", "pilot"]:
                if not field_value:
                    compliance_status = "yellow"
                    message = "⚠️ Date of birth recommended for identity verification"
                else:
                    compliance_status = "green"
                    message = "✅ Date of birth provided"

        # Generate compliance indicator
        if compliance_status != "default":
            colors = {
                "green": "text-green-600 bg-green-50 border-green-200",
                "yellow": "text-yellow-600 bg-yellow-50 border-yellow-200",
                "red": "text-red-600 bg-red-50 border-red-200",
            }

            color_class = colors.get(
                compliance_status, "text-gray-600 bg-gray-50 border-gray-200"
            )

            html = f"""
                <div class="mt-1 px-3 py-1 rounded-md border text-xs {color_class}">
                    {message}
                </div>
            """

            return HttpResponse(html)

    except BaseProfile.DoesNotExist:
        pass

    # Return empty for no compliance checking needed
    return HttpResponse("")


# TEMPLATE CREATION FUNCTIONS FOR CONSISTENCY
def create_enterprise_success_message(message, compliance_status=None):
    """
    Create standardized success message with optional compliance info
    """
    base_msg = f'<div class="bg-green-50 border border-green-200 rounded-md p-4 text-green-700">{message}</div>'

    if compliance_status:
        if compliance_status == "green":
            base_msg += '<div class="mt-2 text-sm text-green-600">✅ All compliance requirements satisfied</div>'
        elif compliance_status == "yellow":
            base_msg += '<div class="mt-2 text-sm text-yellow-600">⚠️ Some optional fields could be completed</div>'
        elif compliance_status == "red":
            base_msg += '<div class="mt-2 text-sm text-red-600">🔴 Critical compliance requirements still needed</div>'

    return base_msg


def create_enterprise_error_message(message, field_errors=None):
    """
    Create standardized error message with field-specific details
    """
    html = f'<div class="bg-red-50 border border-red-200 rounded-md p-4 text-red-700">{message}</div>'

    if field_errors:
        html += '<div class="mt-2 space-y-1">'
        for field, error in field_errors.items():
            html += f'<div class="text-sm text-red-600">• {field}: {error}</div>'
        html += "</div>"

    return html


# USAGE DOCUMENTATION FOR OTHER APPS:
"""
STANDARD PATTERN FOR ALL APPS (rpas/, sms/, aviation/):

1. Create {app}_enterprise_forms.py:
   - Inherit from EnterpriseMixin
   - Use create_enterprise_layout()
   - Apply three-color compliance

2. Create {app}_modern_views.py:
   - Professional error handling
   - HTMX integration
   - Cotton template rendering
   - Compliance status integration

3. Create templates/{app}/modern_*.html:
   - Cotton component integration
   - Three-color compliance indicators
   - Professional styling throughout
   - HTMX real-time updates

Example for rpas app:
# rpas/f2_forms.py
class F2MaintenanceForm(EnterpriseMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_enterprise_styling()
        self.helper = self.get_enterprise_helper('/rpas/f2/maintenance/')
        self.helper.layout = create_enterprise_layout(
            'aircraft', 'work_performed', 'next_inspection_hours',
            card_title="F2 Maintenance Entry - CASA Compliant"
        )

# rpas/f2_views.py
@login_required
def f2_maintenance_create(request):
    # Same pattern as modern_profile_edit
    # Cotton templates, HTMX, compliance integration
    pass
"""
