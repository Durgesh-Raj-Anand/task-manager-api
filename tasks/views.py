"""
Views for the tasks app.

Contains:
    CategoryViewSet – Full CRUD for categories (owner-scoped).
    TaskViewSet     – Full CRUD for tasks (owner-scoped).

Both viewsets:
    - Require authentication (inherited from settings).
    - Scope querysets to the logged-in user (owner-based access).
    - Auto-set the owner on creation via perform_create().
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Category, Task
from .serializers import (
    CategorySerializer,
    TaskListSerializer,
    TaskSerializer,
)


# ------------------------------------------------------------------
# CategoryViewSet
# ------------------------------------------------------------------
# Provides list / create / retrieve / update / partial_update / destroy
# for Category objects, all scoped to the current user.
# ------------------------------------------------------------------

class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for categories.

    Each user only sees and manages their own categories.
    """

    serializer_class = CategorySerializer

    # -- Filtering / Search / Ordering --------------------------------
    # These are also set globally in settings.py, but being explicit
    # here makes it clear what this viewset supports.
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']  # default ordering

    # -- Queryset -----------------------------------------------------

    def get_queryset(self):
        """
        Return only categories owned by the logged-in user.

        This is the owner-based access control — users can never
        see or modify another user's categories.
        """
        return Category.objects.filter(owner=self.request.user)

    # -- Auto-set owner on creation -----------------------------------

    def perform_create(self, serializer):
        """
        Automatically set the category owner to the current user.

        The serializer marks 'owner' as read-only, so the client
        cannot override this.
        """
        serializer.save(owner=self.request.user)


# ------------------------------------------------------------------
# TaskViewSet
# ------------------------------------------------------------------
# Provides list / create / retrieve / update / partial_update / destroy
# for Task objects, all scoped to the current user.
#
# Uses two different serializers:
#   - TaskListSerializer for the list action (lighter payload).
#   - TaskSerializer for everything else (full detail).
# ------------------------------------------------------------------

class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for tasks.

    Each user only sees and manages their own tasks.
    Supports filtering, search, and ordering.
    """

    # -- Filtering / Search / Ordering --------------------------------

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Filter by exact match on these fields.
    # Example: GET /api/tasks/tasks/?status=done&priority=high
    filterset_fields = ['status', 'priority', 'category']

    # Search across these fields with a ?search= query param.
    # Example: GET /api/tasks/tasks/?search=groceries
    search_fields = ['title', 'description']

    # Allow ordering by these fields with ?ordering= query param.
    # Example: GET /api/tasks/tasks/?ordering=due_date
    # Prefix with '-' for descending: ?ordering=-priority
    ordering_fields = ['created_at', 'priority', 'due_date']
    ordering = ['-created_at']  # default ordering

    # -- Queryset -----------------------------------------------------

    def get_queryset(self):
        """
        Return only tasks owned by the logged-in user.

        select_related() joins owner and category in a single query
        to avoid N+1 problems when serializing.
        """
        return (
            Task.objects
            .filter(owner=self.request.user)
            .select_related('owner', 'category')
        )

    # -- Serializer selection -----------------------------------------

    def get_serializer_class(self):
        """
        Use TaskListSerializer for the list endpoint to keep the
        response payload small.  Use the full TaskSerializer for
        everything else (retrieve, create, update, partial_update).
        """
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    # -- Auto-set owner on creation -----------------------------------

    def perform_create(self, serializer):
        """
        Automatically set the task owner to the current user.

        The serializer marks 'owner' as read-only, so the client
        cannot override this.
        """
        serializer.save(owner=self.request.user)
