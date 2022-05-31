from rest_framework import serializers
from .models import Booking
from room_and_group.serializers import *
from events.serializers import *


class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer()
    event = EventSerializer()

    class Meta:
        model = Booking
        fields = '__all__'

    def create(self, validated_data):
        return Booking.objects.create(**validated_data)

class BookingemptySerializer(serializers.Serializer):
    room = Roomempty()

    def create(self, validated_data):
        return Booking.objects.create(**validated_data)

class BookingsearchroomSerializer(serializers.ModelSerializer):
    event = EventSerializer()

    class Meta:
        model = Booking
        fields = '__all__'

    def create(self, validated_data):
        return Booking.objects.create(**validated_data)

class Booking_Search_event_Serializer(serializers.Serializer):
    room = Room_Search_event_Serializer()
    event = EventlistchSerializer()
    
    time_from = serializers.DateTimeField()
    time_to = serializers.DateTimeField()

    def create(self, validated_data):
        return Booking.objects.create(**validated_data)