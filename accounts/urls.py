"""
URL configuration for the accounts app.

Endpoints:
    POST /api/auth/register/  – Create a new user account.
    POST /api/auth/login/     – Log in and get an auth token.
"""

from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
]
