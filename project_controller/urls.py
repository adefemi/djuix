from rest_framework.routers import DefaultRouter
from .views import ProjectView, AppView
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
router.register("project", ProjectView)
router.register("app", AppView)


urlpatterns = [
    path("", include(router.urls))
]
