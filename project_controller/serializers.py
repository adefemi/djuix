from rest_framework import serializers
from .models import Project, App


class ProjectSerializer(serializers.ModelSerializer):
    delete_if_project_exist = serializers.BooleanField(write_only=True, default=False)
    template = serializers.ChoiceField(required=False, choices=(
        ("blog", "blog"),
        ("custom", "custom"),
    ), default="custom")

    class Meta:
        model = Project
        fields = "__all__"


class AppSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    project_id = serializers.CharField(write_only=True)

    class Meta:
        model = App
        fields = "__all__"
