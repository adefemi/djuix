from django.db import models
from project_controller.models import App


field_type_choices = (("CharField", "CharField"), ("TextField",
                                                   "TextField"), ("DateTimeField", "DateTimeField"), )


class ModelInfo(models.Model):
    app = models.ForeignKey(
        App, related_name="app_models", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.app.name} - {self.name}"


class ModelField(models.Model):
    model_main = models.ForeignKey(
        ModelInfo, related_name="model_fields", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    field_type = models.CharField(
        max_length=50, default="CharField", choices=field_type_choices)
    is_null = models.BooleanField(default=False)
    is_blank = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    is_created_at = models.BooleanField(default=False)
    default_value = models.CharField(max_length=255, null=True, blank=True)
    helper_text = models.TextField(blank=True, null=True)
    max_length = models.IntegerField(null=True)
    is_related = models.BooleanField(default=False)
    related_model_name = models.CharField(
        max_length=100, null=True, blank=True)
    related_name_main = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model_main.app.name} - {self.model_main.name} - {self.name}"


class SerializerInfo(models.Model):
    model_relation = models.ForeignKey(
        ModelInfo, related_name="model_serializers", on_delete=models.CASCADE, null=True)
    app = models.ForeignKey(
        App, related_name="app_serializers", on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.app.name} - {self.name}"


class SerializerField(models.Model):
    serializer_main = models.ForeignKey(
        SerializerInfo, related_name="serializer_fields", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    field_type = models.CharField(
        max_length=50, default="CharField", choices=field_type_choices)
    is_required = models.BooleanField(default=True)
    is_write_only = models.BooleanField(default=False)
    is_read_only = models.BooleanField(default=False)
    is_related = models.BooleanField(default=False)
    related_serializer_name = models.CharField(
        max_length=100, null=True, blank=True)
    is_many = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.serializer_main.app.name} - {self.serializer_main.name} - {self.name}"
