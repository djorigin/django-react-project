"""
Enterprise Authentication Views for RPAS Management System
Professional authentication flow with SAP/GE Vernova styling
"""

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from core.models import BaseProfile, ProfileType

User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Enterprise login view with HTMX support"""

    if request.method == "GET":
        # Show login form
        return render(request, "accounts/login.html")

    # POST - Handle login submission
    email = request.POST.get("email")
    password = request.POST.get("password")
    remember_me = request.POST.get("remember_me") == "on"

    if not email or not password:
        if request.headers.get("HX-Request"):
            return HttpResponse(
                '<div class="mt-4"><div class="text-red-600 text-sm font-medium bg-red-50 border border-red-200 rounded-md px-3 py-2">Please enter both email and password.</div></div>'
            )
        messages.error(request, "Please enter both email and password.")
        return render(request, "accounts/login.html")

    # Authenticate user
    user = authenticate(request, username=email, password=password)

    if user is not None:
        login(request, user)

        # Set session expiry based on remember me
        if not remember_me:
            request.session.set_expiry(0)  # Browser session only
        else:
            request.session.set_expiry(1209600)  # 2 weeks

        if request.headers.get("HX-Request"):
            # HTMX redirect to dashboard
            response = HttpResponse()
            response["HX-Redirect"] = reverse("dashboard")
            return response

        return redirect("dashboard")

    else:
        error_message = "Invalid email or password. Please try again."
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="mt-4"><div class="text-red-600 text-sm font-medium bg-red-50 border border-red-200 rounded-md px-3 py-2">{error_message}</div></div>'
            )
        messages.error(request, error_message)
        return render(request, "accounts/login.html")


@require_http_methods(["GET", "POST"])
def register_view(request):
    """Enterprise registration view with profile type selection"""

    if request.method == "GET":
        return render(request, "accounts/register.html")

    # POST - Handle registration submission
    email = request.POST.get("email")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    profile_type = request.POST.get("profile_type")
    password1 = request.POST.get("password1")
    password2 = request.POST.get("password2")

    # Basic validation
    if not all([email, first_name, last_name, profile_type, password1, password2]):
        error_msg = "All fields are required."
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="mt-4"><div class="text-red-600 text-sm font-medium bg-red-50 border border-red-200 rounded-md px-3 py-2">{error_msg}</div></div>'
            )
        messages.error(request, error_msg)
        return render(request, "accounts/register.html")

    if password1 != password2:
        error_msg = "Passwords do not match."
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="mt-4"><div class="text-red-600 text-sm font-medium bg-red-50 border border-red-200 rounded-md px-3 py-2">{error_msg}</div></div>'
            )
        messages.error(request, error_msg)
        return render(request, "accounts/register.html")

    # Check if user already exists
    if User.objects.filter(email=email).exists():
        error_msg = "An account with this email already exists."
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="mt-4"><div class="text-red-600 text-sm font-medium bg-red-50 border border-red-200 rounded-md px-3 py-2">{error_msg}</div></div>'
            )
        messages.error(request, error_msg)
        return render(request, "accounts/register.html")

    # Create user
    try:
        user = User.objects.create_user(
            email=email, password=password1, first_name=first_name, last_name=last_name
        )

        # Get or create the profile type
        profile_type_obj, created = ProfileType.objects.get_or_create(
            code=profile_type,
            defaults={
                "name": profile_type.title(),
                "description": f"{profile_type.title()} profile type",
            },
        )

        # Create the user profile
        BaseProfile.objects.create(user=user, profile_type=profile_type_obj)

        # Success message
        messages.success(request, "Account created successfully! Please log in.")

        if request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Redirect"] = reverse("accounts:login")
            return response

        return redirect("accounts:login")

    except Exception as e:
        # Log the actual error for debugging
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Registration error: {str(e)}")

        error_msg = "Error creating account. Please try again."
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="mt-4"><div class="text-red-600 text-sm font-medium bg-red-50 border border-red-200 rounded-md px-3 py-2">{error_msg}</div></div>'
            )
        messages.error(request, error_msg)
        return render(request, "accounts/register.html")


@login_required
def logout_view(request):
    """Professional logout view"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("accounts:login")


def dashboard_view(request):
    """
    Redirect to the main enterprise dashboard
    This view is a bridge to the main dashboard
    """
    return redirect("dashboard")
