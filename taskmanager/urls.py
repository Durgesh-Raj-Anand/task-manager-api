"""
URL configuration for taskmanager project.

The `urlpatterns` list routes URLs to views.
https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/tasks/', include('tasks.urls')),
    path('api/auth/', include('accounts.urls')),

    # DRF browsable API login (optional, handy during development)
    path('api-auth/', include('rest_framework.urls')),
]
