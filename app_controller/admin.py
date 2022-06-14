from django.contrib import admin
from .models import ModelInfo, SerializerInfo, ViewsInfo, UrlInfo


admin.site.register((ModelInfo, SerializerInfo, ViewsInfo, UrlInfo))