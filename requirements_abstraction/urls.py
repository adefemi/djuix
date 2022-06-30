from rest_framework.routers import DefaultRouter
from .views import GetProjectTemplate, GetSettingInfo
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
router.register("get-templates", GetProjectTemplate)
router.register("get-setting-info", GetSettingInfo)


urlpatterns = [
    path("", include(router.urls))
]
