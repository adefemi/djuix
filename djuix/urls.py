
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("project-controls/", include("project_controller.urls")),
    path("app-controls/", include("app_controller.urls")),
    path("requirements/", include("requirements_abstraction.urls")),
    path("utilities/", include("utilities.urls")),
    path("user-management/", include("user_management.urls")),
]
