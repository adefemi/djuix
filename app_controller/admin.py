from django.contrib import admin
from .models import ModelField, ModelInfo


admin.site.register((ModelField, ModelInfo))