from rest_framework.routers import DefaultRouter
from .views import GetProjectTemplate, GetSettingInfo, GetModelFieldInfo, GetSerializerFieldInfo
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
router.register("get-templates", GetProjectTemplate, basename="get-templates")
router.register("get-setting-info", GetSettingInfo, basename="get-setting-info")
router.register("get-model-field-info", GetModelFieldInfo, basename="get-model-field-info")
router.register("get-serializer-field-info", GetSerializerFieldInfo, basename="get-serializer-field-info")


urlpatterns = [
    path("", include(router.urls))
]
