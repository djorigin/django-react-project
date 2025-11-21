"""
Authentication views for DarkLight Meta project

Uses HTMX for dynamic form submissions and page updates
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, RegisterForm


def landing_page(request):
    """Landing page for the application"""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    context = {"page_title": "Welcome to DarkLight Meta", "show_auth_buttons": True}
    return render(request, "accounts/landing.html", context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Login view with HTMX support"""

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.cleaned_data["user"]
            # Specify the backend since we have multiple authentication backends
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # HTMX response for successful login
            if request.htmx:
                return HttpResponse(
                    '''
                    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                        Login successful! Redirecting...
                    </div>
                    <script>
                        setTimeout(() => {
                            window.location.href = "'''
                    + reverse("accounts:dashboard")
                    + """";
                        }, 1000);
                    </script>
                """
                )

            return redirect("accounts:dashboard")
        else:
            # HTMX response for form errors
            if request.htmx:
                return render(
                    request, "accounts/partials/login_form.html", {"form": form}
                )
    else:
        form = LoginForm()

    context = {"form": form, "page_title": "Sign In - DarkLight Meta"}
    return render(request, "accounts/login.html", context)


@require_http_methods(["GET", "POST"])
def register_view(request):
    """Registration view with HTMX support"""

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Specify the backend since we have multiple authentication backends
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # Always try HTMX response first, redirect to profile completion
            profile_edit_url = reverse("accounts:profile_edit")
            success_html = f"""
            <div id="register-form-container">
                <div class="text-center space-y-6">
                    <div class="bg-gradient-to-r from-green-400/10 to-green-600/10 border border-green-400/50 text-green-300 px-6 py-4 rounded-lg">
                        <div class="flex items-center justify-center mb-2">
                            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            <span class="font-bold">Account Created Successfully!</span>
                        </div>
                        <p class="text-sm">Welcome to DarkLight Meta, {user.first_name}!</p>
                        <p class="text-xs mt-2 opacity-75">Please complete your profile to get started...</p>
                    </div>
                    <div class="flex justify-center">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-gold"></div>
                    </div>
                </div>
            </div>
            <script>
                setTimeout(function() {{
                    window.location.href = "{profile_edit_url}";
                }}, 2000);
            </script>
            """

            # Return HTMX response or fallback to redirect
            return HttpResponse(success_html)
        else:
            # HTMX response for form errors
            if request.headers.get("HX-Request"):
                return render(
                    request, "accounts/partials/register_form.html", {"form": form}
                )
    else:
        form = RegisterForm()

    context = {"form": form, "page_title": "Create Account - DarkLight Meta"}
    return render(request, "accounts/register.html", context)


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("accounts:landing")


@login_required
def dashboard(request):
    """User dashboard after login"""
    # Get user profile if it exists
    profile = None
    try:
        profile = request.user.profile
    except AttributeError:
        # Handle case where user doesn't have a profile
        pass

    context = {
        "user": request.user,
        "profile": profile,
        "page_title": "Dashboard - DarkLight Meta",
    }
    return render(request, "accounts/dashboard.html", context)
