from rest_framework.routers import DefaultRouter
from .views import GetProjectTemplate, GetSettingInfo, GetModelFieldInfo
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
router.register("get-templates", GetProjectTemplate, basename="get-templates")
router.register("get-setting-info", GetSettingInfo, basename="get-setting-info")
router.register("get-model-field-info", GetModelFieldInfo, basename="get-model-field-info")


urlpatterns = [
    path("", include(router.urls))
]
