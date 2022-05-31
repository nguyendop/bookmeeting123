from rest_framework import serializers
from .models import Event
from users.serializers import listevent


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

    def create(self, validated_data):
        return Event.objects.create(**validated_data)


class EventSearchSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    group = serializers.CharField()
    created_at = serializers.DateTimeField()

    def create(self, validated_data):
        return Event.objects.create(**validated_data)


class EventlistchSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    created_by = listevent()

    def create(self, validated_data):
        return Event.objects.create(**validated_data)
