from django.contrib import admin

from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin config for the Category model."""
    list_display = ['name', 'owner', 'color']
    search_fields = ['name']
    list_filter = ['owner']
    ordering = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin config for the Task model."""
    list_display = [
        'title',
        'owner',
        'category',
        'priority',
        'status',
        'due_date',
        'is_overdue',
        'created_at',
    ]
    search_fields = ['title', 'description']
    list_filter = ['status', 'priority', 'category']
    ordering = ['-created_at']

    @admin.display(boolean=True, description='Overdue?')
    def is_overdue(self, obj):
        """Show a green/red icon in the admin list."""
        return obj.is_overdue
