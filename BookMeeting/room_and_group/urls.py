from django.urls import path
from .views import *

urlpatterns = [
    path('groups/listgroup/', GroupView.as_view(), name="list-group"),
    path('groups/<uuid:pk>', GroupDetailView.as_view(), name="group-detail"),
    path('groups/edit_group/<uuid:pk>', EditGroup.as_view(), name="group-edit"),
    path('groups/add_group/', AddGroup.as_view(), name="add-group"),
    path('groups/delete_group/', DeleteGroup.as_view(), name="delete-group"),

    path('room/', RoomView.as_view(), name="list-room"),
    path('room/<int:pk>', RoomDetailView.as_view(), name="room-detail"),
    path('room/search_event_room/', SearchEventRoom.as_view(), name="event-room"),
    path('room/add_room/', AddRoom.as_view(), name="add-room"),
    path('room/delete_room/', DeleteRoom.as_view(), name="delete-room"),
    path('room/edit_room/<uuid:pk>', EditRoom.as_view(), name="edit-room"),

]
