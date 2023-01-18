from rest_framework import serializers
from .models import CustomUser, UserActivities, UserStatus


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
    

class UserStatusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserStatus
        fields = "__all__"


class CustomUserSerializer(serializers.ModelSerializer):
    user_statuses = UserStatusSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        exclude = ("password", )


class UserActivitiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserActivities
        fields = "__all__"
