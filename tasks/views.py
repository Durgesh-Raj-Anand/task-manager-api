"""
Views for the tasks app.

Contains:
    CategoryViewSet – Full CRUD for categories (owner-scoped).
    TaskViewSet     – Full CRUD for tasks (owner-scoped).

Custom endpoints:
    POST /api/tasks/tasks/{id}/complete/ – Mark a task as done.
    GET  /api/tasks/tasks/stats/         – Aggregate task counts.

Both viewsets:
    - Require authentication (inherited from settings).
    - Scope querysets to the logged-in user (owner-based access).
    - Auto-set the owner on creation via perform_create().
"""

from django.db.models import Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

    # -- Custom actions -----------------------------------------------

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        POST /api/tasks/tasks/{id}/complete/

        Marks a task as done.  Returns the updated task.
        If the task is already done, it still returns 200
        (idempotent behaviour).
        """
        task = self.get_object()
        task.status = Task.Status.DONE
        task.save(update_fields=['status', 'updated_at'])

        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        GET /api/tasks/tasks/stats/

        Returns aggregate counts for the current user's tasks:
            total, pending (todo), completed (done),
            in_progress, cancelled, overdue.

        Uses conditional aggregation so everything is computed
        in a single database query.
        """
        now = timezone.now()

        counts = (
            Task.objects
            .filter(owner=request.user)
            .aggregate(
                total=Count('id'),
                pending=Count(
                    'id', filter=Q(status=Task.Status.TODO),
                ),
                completed=Count(
                    'id', filter=Q(status=Task.Status.DONE),
                ),
                in_progress=Count(
                    'id', filter=Q(status=Task.Status.IN_PROGRESS),
                ),
                cancelled=Count(
                    'id', filter=Q(status=Task.Status.CANCELLED),
                ),
                overdue=Count(
                    'id',
                    filter=Q(
                        due_date__lt=now,
                        status__in=[
                            Task.Status.TODO,
                            Task.Status.IN_PROGRESS,
                        ],
                    ),
                ),
            )
        )

        return Response(counts, status=status.HTTP_200_OK)
