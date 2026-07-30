"""
URL configuration for the tasks app.

Uses DRF's DefaultRouter to auto-generate URL patterns for
the ModelViewSets.

Endpoints (mounted at /api/ by the project urls.py):
    /api/tasks/            – List / Create tasks.
    /api/tasks/{id}/       – Retrieve / Update / Delete a task.
    /api/tasks/{id}/complete/ – Mark a task as done.
    /api/tasks/stats/      – Aggregate task counts.
    /api/categories/       – List / Create categories.
    /api/categories/{id}/  – Retrieve / Update / Delete a category.
"""

from rest_framework.routers import DefaultRouter

from . import views

app_name = 'tasks'

# The DefaultRouter creates standard REST endpoints for each viewset.
# It also provides an API root view that lists all available endpoints.
router = DefaultRouter()
router.register('tasks', views.TaskViewSet, basename='task')
router.register('categories', views.CategoryViewSet, basename='category')

# Let the project urls.py include router.urls directly.
# We export urlpatterns for backwards compatibility, but the
# project urls.py can also import router from this module.
urlpatterns = router.urls
