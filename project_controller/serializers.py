from rest_framework import serializers
from .models import Project, App, ProjectSettings


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

    class Meta:
        model = Project
        fields = "__all__"


class RunMigrationSerializer(serializers.Serializer):
    project_id = serializers.CharField()