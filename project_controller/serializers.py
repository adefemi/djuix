from asyncore import write
from rest_framework import serializers
from .models import Project, App


class ProjectSerializer(serializers.ModelSerializer):
    delete_if_project_exist = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = Project
        fields = "__all__"


class AppSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    project_id = serializers.CharField(write_only=True)

    class Meta:
        model = App
        fields = "__all__"
