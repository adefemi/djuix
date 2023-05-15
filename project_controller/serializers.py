from rest_framework import serializers

from abstractions.defaults import AUTH_URLS
from .models import Project, App, ProjectSettings, ProjectAuth
from user_management.serializers import CustomUserSerializer
from djuix.custom_methods import get_minutes_remaining


class ProjectAuthSerializer(serializers.ModelSerializer):
    project = serializers.CharField(read_only=True)
    project_id = serializers.CharField(write_only=True)
    urls = serializers.SerializerMethodField("get_auth_urls", read_only=True)
    
    class Meta:
        model = ProjectAuth
        fields = "__all__"
        
    def get_auth_urls(self, obj):
        return AUTH_URLS


class ProjectSettingSerializer(serializers.ModelSerializer):
    project = serializers.CharField(read_only=True)
    project_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = ProjectSettings
        fields = "__all__"


class AppSerializer(serializers.ModelSerializer):
    project = serializers.CharField(read_only=True)
    project_id = serializers.CharField(write_only=True)

    class Meta:
        model = App
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    delete_if_project_exist = serializers.BooleanField(write_only=True, default=False)
    project_apps = AppSerializer(many=True, read_only=True)
    owner = CustomUserSerializer(read_only=True)
    owner_id = serializers.CharField(write_only=True)
    project_auth = ProjectAuthSerializer(read_only=True)
    test_server = serializers.SerializerMethodField("check_test_server", read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
        
    def check_test_server(self, obj):
        try:
            test_server = obj.project_test_server
        except Exception:
            return None
        
        return {
            "minutes_remaining": get_minutes_remaining(test_server.created_at),
            "ip": test_server.ip
        }


class RunMigrationSerializer(serializers.Serializer):
    project_id = serializers.CharField()