from datetime import datetime
import uuid
from django.utils import timezone
from django.db import models

status = (
    ("-1", "delete"),
    ("0", "active"),
    ("1", "lock")
)


class Group(models.Model):
    id = models.UUIDField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=254, unique=False, blank=False)
    status_group = models.CharField(max_length=20, choices=status, default="0")
    created_at = models.DateTimeField(default=datetime.now())
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE,
                                   related_name="created_by_admin_in_group", null=True, blank=True)
    updated_by = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE,
                                   related_name="updated_by_admin_in_group", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_at']


class Room(models.Model):
    id = models.UUIDField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=254, blank=False, null=False)
    size = models.IntegerField(null=False, blank=False)
    color = models.CharField(max_length=30)
    is_peripheral = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)
    status_room = models.CharField(max_length=20, choices=status, default="0")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE,
                                   related_name="created_by_admin_in_room", null=True, blank=True)
    updated_by = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE,
                                   related_name="updated_by_admin_in_room", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_at']
