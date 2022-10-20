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


class BookingInviteUserSerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    participant = serializers.ListField(child=serializers.EmailField())

    class Meta:
        model = Booking
        fields = [
            "id",
            "event",
            "time_from",
            "time_to",
            "room",
            "participant",
            "status"
        ]

    def update(self, instance, validated_data):
        participant = list()
        if not validated_data.get("group") is None:
            member_group = Group_user.objects.filter(group_id=validated_data["group"])
            for _email in member_group:
                participant.append(_email.email)
        else:
            pass
        participant.extend(validated_data["participant"])
        data = list(set(participant))
        instance.participant = data
        instance.save()
        return instance

    def get_event(self, obj):
        return obj.event.title

    def get_room(self, obj):
        return obj.room.name

    # def get_participant(self, obj):
    #     print(obj)
    #     return obj.participant


class BookingViewSerializer(BookingInviteUserSerializer):
    participant = serializers.SerializerMethodField()

    def get_participant(self, obj):
        if obj.participant is "" or obj.participant is None:
            obj.participant = "[]"
        return eval(obj.participant)
