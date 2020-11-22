from django.contrib import admin
from .models import Project, SettingValue, SettingHeader, App

# Register your models here.

admin.site.register([
    Project,
    SettingHeader,
    SettingValue,
    App
])
