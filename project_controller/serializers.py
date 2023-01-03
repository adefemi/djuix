from rest_framework import serializers

from abstractions.defaults import AUTH_URLS
from .models import Project, App, ProjectSettings, ProjectAuth
from user_management.serializers import CustomUserSerializer


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

    class Meta:
        model = Project
        fields = "__all__"


class RunMigrationSerializer(serializers.Serializer):
    project_id = serializers.CharField()