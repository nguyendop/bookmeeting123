import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager

status_user = (
    ("-1", "delete"),
    ("0", "new"),
    ("1", "active"),
    ("2", "lock")
)

role_user = (
    ("1", "BU"),
    ("2", "BOM")
)

vip_or_not = (
    ("1", "yes"),
    ("0", "no")
)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    fullname = models.CharField(max_length=254, unique=False, blank=False)
    email = models.EmailField(_('email address'), max_length=128, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    status_user = models.CharField(max_length=20, choices=status_user, default="0")
    is_vip = models.CharField(max_length=20, choices=vip_or_not, default="0")
    role = models.CharField(max_length=20, choices=role_user, default="1")
    group = models.ForeignKey("room_and_group.Group", on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="created_by_admin", null=True,
                                   blank=True)
    updated_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="updated_by_admin", null=True,
                                   blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    forgotkey = models.UUIDField(max_length=50, primary_key=False, null=True, blank=True, editable=True)
    forgotkey_timeout = models.DateTimeField(primary_key=False, null=True, blank=True, editable=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email}'
