from rest_framework.routers import DefaultRouter
from .views import ModelInfoView, SerializerInfoView, ViewInfoView, UrlInfoView
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
router.register("models", ModelInfoView)
router.register("serializers", SerializerInfoView)
router.register("views", ViewInfoView)
router.register("urls", UrlInfoView)


urlpatterns = [
    path("", include(router.urls))
]
