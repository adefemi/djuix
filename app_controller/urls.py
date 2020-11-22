from rest_framework.routers import DefaultRouter
from .views import ModelInfoView, ModelFieldView
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
router.register("model", ModelInfoView)
router.register("model-field", ModelFieldView)


urlpatterns = [
    path("", include(router.urls))
]
