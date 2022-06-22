from django.db import models
from django.utils.text import slugify

from abstractions.defaults import DEFAULT_PROJECT_DIR


class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    project_path = models.TextField(default=DEFAULT_PROJECT_DIR, editable=False)
    slug = models.SlugField(max_length=50, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.pk}"

    class Meta:
        ordering = ("-created_at", )
        
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SettingValue(models.Model):
    project = models.ForeignKey(
        Project, related_name="project_setting_value", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    value = models.TextField()

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    class Meta:
        ordering = ("name", )


class SettingHeader(models.Model):
    project = models.ForeignKey(
        Project, related_name="project_setting_header", on_delete=models.CASCADE)
    value = models.TextField()

    def __str__(self):
        return f"{self.project.name} - {self.value}"

    class Meta:
        ordering = ("project__name", )


class App(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    project = models.ForeignKey(
        Project, related_name="project_apps", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.name} - {self.pk}"

    class Meta:
        ordering = ("name", )
        unique_together = ("project_id", "name")
