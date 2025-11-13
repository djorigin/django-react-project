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


def tailwind_test(request):
    """Test view to demonstrate Tailwind CSS integration"""
    return render(request, "tailwind_test.html")
