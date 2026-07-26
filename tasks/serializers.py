"""
Serializers for the tasks app.

Contains:
    UserSerializer     – Read-only nested representation of a user.
    CategorySerializer – Full CRUD serializer for categories.
    TaskSerializer     – Full detail serializer for tasks (create/update).
    TaskListSerializer – Lightweight serializer for task list endpoints.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Category, Task

User = get_user_model()


# ------------------------------------------------------------------
# UserSerializer
# ------------------------------------------------------------------
# Purpose: Provide a read-only snapshot of the user.
# Used as a nested serializer inside Task and Category responses
# so the API returns {"id": 1, "username": "alice"} instead of
# just the raw user id.
# ------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    """Read-only serializer for the User model."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        # All fields are read-only because we never create or
        # update users through the tasks API.
        read_only_fields = ['id', 'username', 'email']


# ------------------------------------------------------------------
# CategorySerializer
# ------------------------------------------------------------------
# Purpose: Handle full CRUD for categories.
# - Shows the nested owner on read (via UserSerializer).
# - owner is set automatically in the view (perform_create),
#   so we mark it read-only here.
# - Validates that the category name is not blank whitespace.
# ------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""

    # Nested owner so GET responses show user details, not just an id.
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'owner', 'color']
        read_only_fields = ['id', 'owner']

    # -- Custom validation ------------------------------------------

    def validate_name(self, value):
        """
        Reject category names that are empty or only whitespace.
        strip() removes leading/trailing spaces, so '   ' becomes ''.
        """
        if not value.strip():
            raise serializers.ValidationError(
                'Category name cannot be blank.'
            )
        return value.strip()


# ------------------------------------------------------------------
# TaskSerializer
# ------------------------------------------------------------------
# Purpose: Full detail serializer used for retrieve / create / update.
#
# Key design decisions:
#   1. owner is nested and read-only (set by the view).
#   2. category is nested and read-only (used on GET responses).
#   3. category_id is write-only – the client sends just the id
#      when creating or updating a task.
#   4. is_overdue is a computed field pulled from the model property.
#   5. Custom validation prevents blank titles and past due dates
#      on creation.
# ------------------------------------------------------------------

class TaskSerializer(serializers.ModelSerializer):
    """Full detail serializer for the Task model."""

    # --- Read-only nested fields ---
    owner = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    # --- Write-only field for setting the category ---
    # The client sends {"category_id": 3} to assign a category.
    # We use PrimaryKeyRelatedField so DRF validates the id exists.
    # allow_null=True because category is optional on the model.
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True,
    )

    # --- Computed field ---
    # Reads the @property on the Task model.
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'owner',
            'category',
            'category_id',
            'priority',
            'status',
            'due_date',
            'is_overdue',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'owner',
            'category',
            'is_overdue',
            'created_at',
            'updated_at',
        ]

    # -- Custom validation ------------------------------------------

    def validate_title(self, value):
        """
        Reject titles that are empty or only whitespace.
        Also strip surrounding whitespace so ' Buy milk ' becomes
        'Buy milk'.
        """
        if not value.strip():
            raise serializers.ValidationError(
                'Task title cannot be blank.'
            )
        return value.strip()

    def validate_due_date(self, value):
        """
        When creating a new task, the due date must be in the future.
        On updates we skip this check so the user can keep an
        existing (now-past) due date without being forced to change it.
        """
        if value is None:
            # due_date is optional, so None is fine.
            return value

        # self.instance is None during creation, set during updates.
        is_creation = self.instance is None

        if is_creation and value <= timezone.now():
            raise serializers.ValidationError(
                'Due date must be in the future.'
            )
        return value

    def validate_category_id(self, value):
        """
        Make sure the category belongs to the same user who owns
        the task.  The current user is passed from the view via
        serializer context.
        """
        if value is None:
            return value

        request = self.context.get('request')
        if request and value.owner != request.user:
            raise serializers.ValidationError(
                'You can only assign your own categories.'
            )
        return value


# ------------------------------------------------------------------
# TaskListSerializer
# ------------------------------------------------------------------
# Purpose: A slimmed-down serializer for list endpoints.
# - Drops the full description to keep payloads small.
# - Shows the category name instead of the full nested object.
# - Still includes is_overdue for quick scanning.
#
# Using a separate list serializer is a common pattern to reduce
# the amount of data transferred when fetching many records.
# ------------------------------------------------------------------

class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task list responses."""

    owner = UserSerializer(read_only=True)

    # Show just the category name, not the full nested object.
    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
        default=None,
    )

    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'owner',
            'category_name',
            'priority',
            'status',
            'due_date',
            'is_overdue',
            'created_at',
        ]
        read_only_fields = fields
