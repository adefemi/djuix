from rest_framework.routers import DefaultRouter
from .views import ModelInfoView, ModelFieldView, SerializerInfoView, SerializerFieldView
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
router.register("model", ModelInfoView)
router.register("model-field", ModelFieldView)
router.register("serializer", SerializerInfoView)
router.register("serializer-field", SerializerFieldView)


urlpatterns = [
    path("", include(router.urls))
]
