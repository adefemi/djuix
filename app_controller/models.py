from django.db import models
from project_controller.models import App


field_type_choices = (
    ("CharField", "CharField"), 
    ("TextField", "TextField"), 
    ("DateTimeField", "DateTimeField"),
    ("FileField", "FileField"),
    ("ImageField", "ImageField"),
    ("JSONField", "JSONField"),
    ("ForeignKey", "ForeignKey"),
    ("OneToOneField", "OneToOneField"),
    ("ManyToManyField", "ManyToManyField"),
    ("EmailField", "EmailField"),
    ("SlugField", "SlugField"),
    ("UUIDField", "UUIDField"),
    ("BooleanField", "BooleanField"),
    ("FloatField", "FloatField"),
    ("IntegerField", "IntegerField"),
)


class ModelInfo(models.Model):
    app = models.ForeignKey(
        App, related_name="app_models", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    field_properties = models.JSONField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('app_id', 'name')

    def __str__(self):
        return f"{self.app.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        self.name = self.name.capitalize().replace('-', '').replace('_', '')
        return super().save(*args, **kwargs)


class SerializerInfo(models.Model):
    model_relation = models.ForeignKey(
        ModelInfo, related_name="model_serializers", on_delete=models.CASCADE, null=True)
    app = models.ForeignKey(
        App, related_name="app_serializers", on_delete=models.CASCADE, null=True
    )
    
    field_properties = models.JSONField(default=None, null=True)

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('app_id', 'name')

    def __str__(self):
        return f"{self.model_relation.app.name} - {self.name}"
    
    
class ViewsInfo(models.Model):
    serializer_relation = models.ForeignKey(
        SerializerInfo, related_name="serializer_views", on_delete=models.CASCADE, null=True)
    model = models.ForeignKey(
        ModelInfo, related_name="model_views", on_delete=models.CASCADE, null=True
    )
    app = models.ForeignKey(
        App, related_name="app_views", on_delete=models.CASCADE, null=True
    )
    
    field_properties = models.JSONField(default=None, null=True)

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('app_id', 'name')

    def __str__(self):
        return f"{self.serializer_relation.model_relation.app.name} - {self.name}"
    

class UrlInfo(models.Model):
    view_relation = models.ForeignKey(
        ViewsInfo, related_name="view_urls", on_delete=models.CASCADE, null=True
    )
    app = models.ForeignKey(
        App, related_name="app_urls", on_delete=models.CASCADE, null=True
    )
    field_properties = models.JSONField(default=None, null=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('app_id', 'name')

    def __str__(self):
        return f"{self.view_relation.serializer_relation.model_relation.app.name} - {self.name}"