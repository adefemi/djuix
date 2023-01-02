from rest_framework import serializers
from .models import CustomUser, UserActivities


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CreateUserSerializer(AuthSerializer):
    username = serializers.CharField()


class VerifyUserSerializer(serializers.Serializer):
    token = serializers.CharField()
    is_forget = serializers.BooleanField(required=False)


class ResentEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_forget = serializers.BooleanField(required=False)


class UpdatePasswordSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    password = serializers.CharField()


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ("password", )


class UserActivitiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserActivities
        fields = ("__all__")
