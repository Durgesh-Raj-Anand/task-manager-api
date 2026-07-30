"""
URL configuration for the tasks app.

Uses DRF's DefaultRouter to auto-generate URL patterns for
the ModelViewSets.

Endpoints:
    /api/tasks/categories/       – List / Create categories.
    /api/tasks/categories/{id}/  – Retrieve / Update / Delete a category.
    /api/tasks/tasks/            – List / Create tasks.
    /api/tasks/tasks/{id}/       – Retrieve / Update / Delete a task.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'tasks'

# The DefaultRouter creates standard REST endpoints for each viewset.
# It also provides an API root view at /api/tasks/ that lists
# all available endpoints.
router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='category')
router.register('tasks', views.TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
