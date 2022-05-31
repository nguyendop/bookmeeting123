import uuid
from django.db import models
from django.utils import timezone

status = (
    ("-1", "delete"),
    ("0", "active "),
    ("1", "completed"),
)


class Booking(models.Model):
    id = models.UUIDField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    time_from = models.DateTimeField()
    time_to = models.DateTimeField()
    room = models.ForeignKey('room_and_group.Room', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=status, default="0")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE,
                                   related_name="created_by_admin_in_booking", null=True, blank=True)
    updated_by = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE,
                                   related_name="updated_by_admin_in_booking", null=True, blank=True)

    def __str__(self):
        return f'{self.event}'

    class Meta:
        ordering = ['time_from']
