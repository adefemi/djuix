from .models import ModelInfo, ModelField
from rest_framework import serializers


class ModelInfoSerializer(serializers.ModelSerializer):
    app = serializers.CharField(read_only=True)
    app_id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = "__all__"
        model = ModelInfo


class ModelFieldSerializer(serializers.ModelSerializer):
    model_main = serializers.CharField(read_only=True)
    model_main_id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = "__all__"
        model = ModelField
