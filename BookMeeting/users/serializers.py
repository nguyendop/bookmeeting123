from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    model = CustomUser

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    fullname = serializers.CharField()
    password = serializers.CharField(max_length=255, default='123456')

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class UserViewSerializer(serializers.Serializer):
    email = serializers.EmailField()
    fullname = serializers.CharField()
    phone = serializers.CharField()
    status_user = serializers.CharField()
    is_superuser = serializers.BooleanField()

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class listevent(serializers.Serializer):
    fullname = serializers.CharField()

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class UserListAll(serializers.Serializer):
    email = serializers.EmailField()
    fullname = serializers.CharField()
    status_user = serializers.CharField()
    is_superuser = serializers.BooleanField()
    group = serializers.CharField()
    created_at = serializers.DateTimeField()
    
