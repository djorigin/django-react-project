from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


def home_view(request):
    """Simple home page view"""
    return HttpResponse(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Django React Project - Alpha Server</title>
        <link rel="stylesheet" href="/static/css/main.css">
    </head>
    <body>
        <div class="header">
            <h1>🚀 Django React Project</h1>
            <p>Alpha Server - Backend API</p>
        </div>
        <div class="container">
            <div class="card">
                <h2>System Status</h2>
                <p>✅ Django Backend: <span class="status-success">Running</span></p>
                <p>✅ PostgreSQL: <span class="status-success">Connected</span></p>
                <p>✅ Redis: <span class="status-success">Connected</span></p>
                <p>✅ Static Files: <span class="status-success">Serving</span></p>
                <p>✅ Installed Apps: <span class="status-success">{} apps loaded</span></p>
            </div>
            <div class="card">
                <h2>Available Endpoints</h2>
                <ul>
                    <li><a href="/admin/">Django Admin</a></li>
                    <li><a href="/__debug__/">Debug Toolbar</a> (Development)</li>
                    <li><a href="/static/css/main.css">Static Files Test</a></li>
                </ul>
            </div>
            <div class="card">
                <h2>Infrastructure</h2>
                <p><strong>Alpha Server (192.168.0.16):</strong> Django Backend + API</p>
                <p><strong>Beta Server (192.168.0.17):</strong> React Frontend</p>
                <p><strong>Delta Server (192.168.0.18):</strong> PostgreSQL + Redis</p>
            </div>
        </div>
        <script src="/static/js/main.js"></script>
    </body>
    </html>
    """.format(
            len(__import__("django.conf").conf.settings.INSTALLED_APPS)
        )
    )


@login_required
def dashboard_view(request):
    """
    Profile-aware dashboard view that provides different content
    based on user's profile type (Pilot, Staff, Client, Customer, General)
    """
    context = {}

    # Get user profile information
    if (
        hasattr(request.user, "profile")
        and request.user.profile
        and request.user.is_authenticated
    ):
        profile = request.user.profile
        profile_type = (
            profile.profile_type.name.lower() if profile.profile_type else "general"
        )

        # Add profile-specific context data
        if profile_type == "pilot":
            context.update(
                {
                    "pilot_stats": {
                        "flight_hours": 28.7,  # Example data
                        "flights_completed": 15,
                        "aircraft_assigned": 2,
                    }
                }
            )
        elif profile_type == "staff":
            context.update(
                {
                    "staff_stats": {
                        "active_flights": 3,
                        "pilots_on_duty": 5,
                        "safety_incidents": 0,
                        "operational_aircraft": 8,
                        "maintenance_aircraft": 2,
                        "grounded_aircraft": 0,
                    }
                }
            )
        elif profile_type == "client":
            context.update(
                {
                    "client_stats": {
                        "active_projects": 3,
                        "completed_projects": 7,
                        "total_hours": 42.5,
                    }
                }
            )
        elif profile_type == "customer":
            context.update(
                {
                    "customer_stats": {
                        "total_services": 1,
                        "last_service": "Roof inspection",
                    }
                }
            )
        else:
            context.update(
                {
                    "general_stats": {
                        "last_updated": "Just now",
                    }
                }
            )
    else:
        # For unauthenticated users or users without profiles, show general content
        context.update(
            {
                "general_stats": {
                    "last_updated": "Just now",
                }
            }
        )

    return render(request, "dashboard/main.html", context)
