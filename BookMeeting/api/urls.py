from django.urls import path, include
from .api_add_event import api_add_event

urlpatterns = [
    path('', include('room_and_group.urls')),
    path('user/', include('users.urls')),
    path('events/', include('events.urls')),
    path('booking/', include('booking.urls')),
    path('add-event/', api_add_event, name='add-event'),

]
