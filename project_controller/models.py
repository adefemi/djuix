from django.db import models
from django.utils import timezone


class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    project_path = models.TextField(default="/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-created_at", )


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
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    is_auth = models.BooleanField(default=False)
    project = models.ForeignKey(
        Project, related_name="project_apps", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    class Meta:
        ordering = ("name", )
