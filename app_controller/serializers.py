from project_controller.serializers import AppSerializer
from .models import ModelInfo, SerializerInfo, ViewsInfo, UrlInfo
from rest_framework import serializers


class ModelInfoSerializer(serializers.ModelSerializer):
    app = AppSerializer(read_only=True)
    app_id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = "__all__"
        model = ModelInfo


class SerializerInfoSerializer(serializers.ModelSerializer):
    model_relation = serializers.CharField(read_only=True)
    model_relation_id = serializers.CharField(write_only=True, required=False)
    app = AppSerializer(read_only=True)
    app_id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = "__all__"
        model = SerializerInfo


class ViewInfoSerializer(serializers.ModelSerializer):
    serializer_relation = serializers.CharField(read_only=True)
    serializer_relation_id = serializers.CharField(write_only=True, required=False)
    app = AppSerializer(read_only=True)
    app_id = serializers.IntegerField(write_only=True)
    model = serializers.CharField(read_only=True)
    model_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        fields = "__all__"
        model = ViewsInfo


class UrlInfoSerializer(serializers.ModelSerializer):
    view_relation = serializers.CharField(read_only=True)
    view_relation_id = serializers.CharField(write_only=True, required=False)
    app = AppSerializer(read_only=True)
    app_id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = "__all__"
        model = UrlInfo
