from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from .models import Booking


class IsADBookingPermission(IsAuthenticated):
    def has_permission(self, request, view, **kwargs):
        return bool(
            super(IsADBookingPermission, self).has_permission(request=request, view=view)
            and Booking.objects.filter(
                Q(pk=view.kwargs.get("pk")) & Q(created_by=request.user)).exists() or request.user.is_superuser
        )
