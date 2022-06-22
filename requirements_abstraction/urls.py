from rest_framework.routers import DefaultRouter
from .views import GetProjectTemplate
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
router.register("get-templates", GetProjectTemplate)


urlpatterns = [
    path("", include(router.urls))
]
