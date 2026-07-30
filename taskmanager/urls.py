"""
URL configuration for taskmanager project.

All API endpoints live under /api/:
    /api/tasks/           – Task CRUD + custom actions.
    /api/categories/      – Category CRUD.
    /api/auth/register/   – User registration.
    /api/auth/login/      – User login.

https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints – tasks and categories are registered via
    # DefaultRouter in tasks/urls.py and mounted here at /api/.
    path('api/', include('tasks.urls')),

    # Authentication endpoints
    path('api/auth/', include('accounts.urls')),

    # DRF browsable API login/logout (handy during development).
    # Adds a "Log in" button to the top-right of the browsable API.
    path('api-auth/', include('rest_framework.urls')),
]
