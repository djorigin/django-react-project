"""
Profile views for user profile management

Handles profile creation, editing, and geographical HTMX endpoints
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from core.models import BaseProfile, City, Country, PostalCode, ProfileType, State

from .profile_forms import ProfileEditForm


@login_required
def profile_edit(request):
    """
    Profile editing view with mandatory completion workflow

    New users are redirected here after registration and cannot access
    dashboard until profile is complete.
    """

    # Get or create profile with default General type
    try:
        profile = request.user.profile
    except BaseProfile.DoesNotExist:
        # Create default General profile
        general_type = ProfileType.objects.get(code="general")
        profile = BaseProfile.objects.create(
            user=request.user, profile_type=general_type
        )

    if request.method == "POST":
        form = ProfileEditForm(
            request.POST, request.FILES, instance=profile, user=request.user
        )
        if form.is_valid():
            with transaction.atomic():
                form.save()
                messages.success(request, "Profile updated successfully!")

                # Check if profile is now complete
                if _is_profile_complete(profile):
                    # HTMX response for successful completion
                    if request.htmx:
                        dashboard_url = reverse("accounts:dashboard")
                        return HttpResponse(
                            f"""
                            <div id="profile-form-container">
                                <div class="text-center space-y-6">
                                    <div class="bg-gradient-to-r from-green-400/10 to-green-600/10 border border-green-400/50 text-green-300 px-6 py-4 rounded-lg">
                                        <div class="flex items-center justify-center mb-2">
                                            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                            </svg>
                                            <span class="font-bold">Profile Completed Successfully!</span>
                                        </div>
                                        <p class="text-sm">Your profile is now complete and you can access all features.</p>
                                        <p class="text-xs mt-2 opacity-75">Taking you to your dashboard...</p>
                                    </div>
                                    <div class="flex justify-center">
                                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-gold"></div>
                                    </div>
                                </div>
                            </div>
                            <script>
                                setTimeout(function() {{
                                    window.location.href = "{dashboard_url}";
                                }}, 2000);
                            </script>
                        """
                        )

                    return redirect("accounts:dashboard")
                else:
                    # Profile not complete yet, show what's missing
                    missing_fields = _get_missing_required_fields(profile)
                    messages.warning(
                        request,
                        f'Please complete the following required fields: {", ".join(missing_fields)}',
                    )
        else:
            # Form has errors
            if request.htmx:
                return render(
                    request,
                    "accounts/partials/profile_edit_form.html",
                    {"form": form, "profile": profile},
                )
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    # Check if this is a new user who needs to complete profile
    is_profile_incomplete = not _is_profile_complete(profile)

    context = {
        "form": form,
        "profile": profile,
        "is_profile_incomplete": is_profile_incomplete,
        "page_title": (
            "Complete Your Profile - DarkLight Meta"
            if is_profile_incomplete
            else "Edit Profile - DarkLight Meta"
        ),
    }
    return render(request, "accounts/profile_edit.html", context)


@login_required
def profile_view(request):
    """View user's completed profile"""
    try:
        profile = request.user.profile
    except BaseProfile.DoesNotExist:
        messages.warning(request, "Please complete your profile first.")
        return redirect("accounts:profile_edit")

    if not _is_profile_complete(profile):
        messages.warning(request, "Please complete your profile first.")
        return redirect("accounts:profile_edit")

    context = {"profile": profile, "page_title": "Your Profile - DarkLight Meta"}
    return render(request, "accounts/profile_view.html", context)


# HTMX endpoints for geographical chained selection
@login_required
@require_http_methods(["GET"])
def load_states(request):
    """HTMX endpoint to load states based on selected country"""
    country_id = request.GET.get("country")

    # Debug logging
    print(f"DEBUG: load_states called with country_id: {country_id}")
    print(f"DEBUG: All GET parameters: {request.GET}")

    if country_id:
        states = State.objects.filter(country_id=country_id, is_active=True).order_by(
            "name"
        )
        print(f"DEBUG: Found {states.count()} states for country_id {country_id}")
    else:
        states = State.objects.none()
        print("DEBUG: No country_id provided")

    # Generate complete select element with HTMX attributes
    html = '<select name="state" id="id_state" '
    html += 'class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent" '
    html += 'hx-get="/load-cities/" hx-target="#id_city_direct" hx-trigger="change" hx-swap="outerHTML" hx-include="[name=state]">'
    html += '<option value="">Select State/Province</option>'
    for state in states:
        html += f'<option value="{state.id}">{state.name}</option>'
    html += "</select>"

    print(f"DEBUG: Generated HTML: {html[:100]}...")
    return HttpResponse(html)


@login_required
@require_http_methods(["GET"])
def load_cities(request):
    """HTMX endpoint to load cities based on selected state"""
    state_id = request.GET.get("state")

    # Debug logging
    print(f"DEBUG: load_cities called with state_id: {state_id}")
    print(f"DEBUG: All GET parameters: {request.GET}")

    if state_id:
        cities = City.objects.filter(state_id=state_id, is_active=True).order_by("name")
        print(f"DEBUG: Found {cities.count()} cities for state_id {state_id}")
    else:
        cities = City.objects.none()
        print("DEBUG: No state_id provided")

    # Generate complete select element with HTMX attributes
    html = '<select name="city_direct" id="id_city_direct" '
    html += 'class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent" '
    html += 'hx-get="/load-postal-codes/" hx-target="#id_postal_code_select" hx-trigger="change" hx-swap="outerHTML" hx-include="[name=city_direct]">'
    html += '<option value="">Select City/Town</option>'
    for city in cities:
        html += f'<option value="{city.id}">{city.name}</option>'
    html += "</select>"

    print(f"DEBUG: Generated cities HTML: {html[:100]}...")
    return HttpResponse(html)


@login_required
@require_http_methods(["GET"])
def load_postal_codes(request):
    """HTMX endpoint to handle postal codes based on selected city"""
    city_id = request.GET.get("city_direct")

    if city_id:
        postal_codes = PostalCode.objects.filter(
            city_id=city_id, is_active=True
        ).order_by("code")
        city = City.objects.get(id=city_id)
    else:
        postal_codes = PostalCode.objects.none()
        city = None

    # Smart postal code handling
    if postal_codes.count() == 0:
        # No postal codes available - show text input with helpful placeholder
        city_name = city.name if city else "this city"
        html = f"""
        <div class="space-y-2">
            <input type="text" name="postal_code_manual" id="id_postal_code_manual"
                   placeholder="Enter postal code for {city_name}"
                   class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent">
            <p class="text-sm text-gray-400">Enter your postal code manually</p>
        </div>"""
    elif postal_codes.count() == 1:
        # Exactly one postal code - auto-select it
        postal_code = postal_codes.first()
        html = f"""
        <div class="space-y-2">
            <input type="hidden" name="postal_code_select" value="{postal_code.id}">
            <div class="block w-full px-4 py-3 border border-gray-300 rounded-lg bg-green-50 text-green-800">
                {postal_code.code} (auto-selected)
            </div>
            <p class="text-sm text-green-600">Postal code automatically selected</p>
        </div>"""
    else:
        # Multiple postal codes - show dropdown
        html = '<select name="postal_code_select" id="id_postal_code_select" class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent">'
        html += '<option value="">Select Postal Code</option>'
        for postal_code in postal_codes:
            html += f'<option value="{postal_code.id}">{postal_code.code}</option>'
        html += "</select>"

    return HttpResponse(html)


def _is_profile_complete(profile):
    """
    Check if profile meets completion requirements based on profile type

    Business Rules:
    - General: Basic contact info sufficient
    - Staff/Pilot: Must have image, DOB, TFN, and for pilots: ARN
    - Client/Customer: Basic contact info sufficient
    """
    if not profile or not profile.profile_type:
        return False

    # Basic requirements for all profiles
    if not profile.phone:
        return False

    # Enhanced requirements for staff and pilots
    if profile.profile_type.code in ["staff", "pilot"]:
        required_fields = [
            profile.date_of_birth,
            profile.tax_file_number,
            profile.image,
        ]

        if not all(required_fields):
            return False

        # Additional requirement for pilots
        if profile.profile_type.code == "pilot" and not profile.arn_number:
            return False

    return True


def _get_missing_required_fields(profile):
    """Get list of missing required fields for the profile type"""
    missing_fields = []

    if not profile.phone:
        missing_fields.append("Phone Number")

    if profile.profile_type.code in ["staff", "pilot"]:
        if not profile.date_of_birth:
            missing_fields.append("Date of Birth")
        if not profile.tax_file_number:
            missing_fields.append("Tax File Number")
        if not profile.image:
            missing_fields.append("Profile Image")

        if profile.profile_type.code == "pilot" and not profile.arn_number:
            missing_fields.append("Aviation Reference Number (ARN)")

    return missing_fields


@login_required
def check_profile_complete(request):
    """
    HTMX endpoint to check if user can access dashboard
    Used by middleware to enforce profile completion
    """
    try:
        profile = request.user.profile
        is_complete = _is_profile_complete(profile)

        return JsonResponse(
            {
                "complete": is_complete,
                "missing_fields": (
                    _get_missing_required_fields(profile) if not is_complete else []
                ),
            }
        )
    except BaseProfile.DoesNotExist:
        return JsonResponse(
            {"complete": False, "missing_fields": ["Profile not created"]}
        )
