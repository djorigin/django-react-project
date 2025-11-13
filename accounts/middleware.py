"""
Profile completion middleware

Ensures users complete their profile before accessing protected areas
"""

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from core.models import BaseProfile, ProfileType


class ProfileCompletionMiddleware:
    """
    Middleware to enforce profile completion for authenticated users

    Business Rules:
    - Users must complete profile before accessing dashboard
    - Profile completion requirements vary by profile type
    - Staff/Pilot profiles have additional requirements
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # URLs that don't require profile completion
        self.exempt_urls = [
            reverse("accounts:landing"),
            reverse("accounts:login"),
            reverse("accounts:register"),
            reverse("accounts:logout"),
            reverse("accounts:profile_edit"),
            reverse("accounts:load_states"),
            reverse("accounts:load_cities"),
            reverse("accounts:load_postal_codes"),
            reverse("accounts:check_profile_complete"),
            "/admin/",  # Django admin
            "/static/",  # Static files
            "/media/",  # Media files
        ]

    def __call__(self, request):
        # Skip middleware for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip middleware for exempt URLs
        if self._is_exempt_url(request.path):
            return self.get_response(request)

        # Check if user has a complete profile
        try:
            profile = request.user.profile
            if not self._is_profile_complete(profile):
                messages.warning(
                    request, "Please complete your profile to access this area."
                )
                return redirect("accounts:profile_edit")
        except BaseProfile.DoesNotExist:
            # Create default General profile and redirect to edit
            general_type = ProfileType.objects.get(code="general")
            BaseProfile.objects.create(user=request.user, profile_type=general_type)
            messages.info(request, "Please complete your profile to get started.")
            return redirect("accounts:profile_edit")

        return self.get_response(request)

    def _is_exempt_url(self, path):
        """Check if URL is exempt from profile completion requirement"""
        for exempt_url in self.exempt_urls:
            if path.startswith(exempt_url):
                return True
        return False

    def _is_profile_complete(self, profile):
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
