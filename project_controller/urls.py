from rest_framework.routers import DefaultRouter
from .views import ProjectView, AppView, SettingsView, RunMigrationView, GetProjectUrls
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
router.register("project", ProjectView)
router.register("app", AppView)
router.register("settings", SettingsView)
router.register("run-migration", RunMigrationView, basename="run-migration")
router.register("project-urls", GetProjectUrls, basename="project-urls")


urlpatterns = [
    path("", include(router.urls))
]
