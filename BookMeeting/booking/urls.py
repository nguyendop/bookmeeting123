from django.urls import path
from .views import *

from .api_26_update_booking import Booking_update

urlpatterns = [
    path('', BookingList.as_view(), name="all-booking"),
    path('in_time/', BookingListInTime.as_view(), name="get booking in range time"),
    path('update-booking/<str:pk>', Booking_update.as_view(), name='update specific booking'),
    path('empty_room/', SearchEmptyRoom.as_view(), name="SearchEmptyRoom"),
    path('delete_many_booking/', DeleteManyBooking.as_view(), name="Delete-many-booking"),
    path('delete_booking/', DeleteBooking.as_view(), name="delete-booking"),
]
