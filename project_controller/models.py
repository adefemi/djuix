from django.db import models
from django.utils.text import slugify

from abstractions.defaults import DEFAULT_PROJECT_DIR


class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    formatted_name = models.CharField(max_length=50, unique=True, editable=False, null=True)
    description = models.TextField(null=True, blank=True)
    project_path = models.TextField(default=DEFAULT_PROJECT_DIR, editable=False)
    slug = models.SlugField(max_length=50, null=True, blank=True, editable=False)
    run_migration = models.BooleanField(default=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.pk}"

    class Meta:
        ordering = ("-created_at", )
        
    def save(self, *args, **kwargs):
        self.formatted_name = self.name.lower().replace(" ", "_")
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        

class ProjectSettings(models.Model):
    project = models.OneToOneField(
        Project, related_name="project_setting", on_delete=models.CASCADE)
    properties = models.JSONField(null=True, blank=True)


class App(models.Model):
    name = models.CharField(max_length=50)
    formatted_name = models.CharField(max_length=50, editable=False, null=True)
    description = models.TextField(null=True, blank=True)
    project = models.ForeignKey(
        Project, related_name="project_apps", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.name} - {self.pk}"

    class Meta:
        ordering = ("name", )
        unique_together = ("project_id", "formatted_name")
        
    def save(self, *args, **kwargs):
        self.formatted_name = self.name.lower().replace(" ", "_")
        super().save(*args, **kwargs)
