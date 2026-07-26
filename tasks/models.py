from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """
    A category to group tasks.
    Each category belongs to one user (owner).
    """
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        help_text='Hex color code, e.g. #ff5733',
    )

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
        # Prevent the same user from creating duplicate category names.
        unique_together = ['name', 'owner']

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    A task that belongs to a user.
    Can optionally be assigned to a category.
    """

    # -- Priority choices --
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    # -- Status choices --
    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE = 'done', 'Done'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.TODO,
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """
        Returns True if the task has a due date in the past
        and the task is not marked as done.
        """
        if self.due_date and self.status != self.Status.DONE:
            return timezone.now() > self.due_date
        return False
