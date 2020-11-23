from .models import ModelInfo, ModelField, SerializerField, SerializerInfo
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


class SerializerInfoSerializer(serializers.ModelSerializer):
    app = serializers.CharField(read_only=True)
    app_id = serializers.IntegerField(write_only=True)
    model_relation = serializers.CharField(read_only=True)
    model_relation_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        fields = "__all__"
        model = SerializerInfo


class SerializerFieldSerializer(serializers.ModelSerializer):
    serializer_main = serializers.CharField(read_only=True)
    serializer_main_id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = "__all__"
        model = SerializerField
