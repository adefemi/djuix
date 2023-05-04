from rest_framework import serializers
from .models import CustomUser, UserActivities, UserStatus, Faq, Documentation, Issue


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CreateUserSerializer(AuthSerializer):
    username = serializers.CharField()


class VerifyUserSerializer(serializers.Serializer):
    token = serializers.CharField()


class ResentEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_forget = serializers.BooleanField(required=False)


class UpdatePasswordSerializer(VerifyUserSerializer):
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


class FaqSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Faq
        fields = "__all__"
        

class DocumentationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Documentation
        fields = "__all__"
        
class IssueSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Issue
        fields = "__all__"