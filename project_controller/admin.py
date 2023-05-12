from django.contrib import admin
from .models import Project, ProjectSettings, App, ProjectAuth, TestServer

# Register your models here.

admin.site.register([
    Project,
    ProjectSettings,
    App,
    ProjectAuth, 
    TestServer
])
