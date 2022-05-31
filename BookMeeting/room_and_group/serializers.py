from rest_framework import serializers
from events.serializers import EventSerializer
from room_and_group.models import Group, Room


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

    def create(self, validated_data):
        return Group.objects.create(**validated_data)


class AddGroupSerializer(serializers.Serializer):
    name = serializers.CharField()

    def create(self, validated_data):
        return Group.objects.create(**validated_data)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def create(self, validated_data):
        return Room.objects.create(**validated_data)


class Roomempty(serializers.Serializer):
    id = serializers.UUIDField()

    def create(self, validated_data):
        return Room.objects.create(**validated_data)


class AddRoomSerializer(serializers.Serializer):
    name = serializers.CharField()
    size = serializers.IntegerField()
    color = serializers.CharField()
    is_peripheral = serializers.BooleanField(required=False, default=False)
    is_vip = serializers.BooleanField(required=False, default=False)

    def create(self, validated_data):
        return Room.objects.create(**validated_data)


class DeleteRoomSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    status_room = serializers.CharField()

    def create(self, validated_data):
        return Room.objects.create(**validated_data)


class Room_Search_event_Serializer(serializers.Serializer):
    name = serializers.CharField()

    def create(self, validated_data):
        return Room.objects.create(**validated_data)
