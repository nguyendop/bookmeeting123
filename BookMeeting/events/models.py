import uuid
from django.utils import timezone
from django.db import models

status = (
    ("-1", "delete"),
    ("0", "active")
)


class Event(models.Model):
    id = models.UUIDField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(null=False, blank=False)
    group = models.ForeignKey('room_and_group.Group', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=status, default="0")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE,
                                   related_name="created_by_admin_in_event", null=True, blank=True)
    updated_by = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE,
                                   related_name="updated_by_admin_in_event", null=True, blank=True)

    def __str__(self):
        return f"{self.title}"
