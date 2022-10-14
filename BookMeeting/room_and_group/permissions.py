from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from users.models import Group_user


class IsADGroupPermission(IsAuthenticated):
    def has_permission(self, request, view, **kwargs):
        return bool(
            super(IsADGroupPermission, self).has_permission(request=request, view=view)
            and Group_user.objects.filter(
                Q(group_id=view.kwargs.get("group_id")) & Q(isADGroup=True) & Q(email=request.user)).exists()
        )
