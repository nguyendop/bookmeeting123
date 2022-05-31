from django.urls import path
from .views import *
from .update_event import update_event

# from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('Searchevent/', SearchEvent.as_view(), name="list-Searchevent"),
    path('', EventList.as_view(), name="lists_event"),
    path('delete/<uuid:pk>/', DeleteEvent.as_view(), name="delete-event"),
    path('update-event/<uuid:pk>', update_event, name='update-event'),

]

# urlpatterns = format_suffix_patterns(urlpatterns)
