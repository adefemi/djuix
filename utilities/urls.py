from rest_framework.routers import DefaultRouter
from .views import GetTopViewGetOptions, GetSimilarViewKeys, GetSearchableFields, GetLookupFieldOptions
from django.urls import include, path

router = DefaultRouter(trailing_slash=False)
# router.register("top-data-option/<str:serializer_id>", GetTopViewGetOptions, basename="get-top-view-options")


urlpatterns = [
    # path("", include(router.urls)),
    path("top-data-option/<str:serializer_id>", GetTopViewGetOptions.as_view({'get': 'list'}), name="get-top-view-options"),
    path("similar-data-option/<str:serializer_id>", GetSimilarViewKeys.as_view({'get': 'list'}), name="get-similar-view-options"),
    path("searchable-fields/<str:serializer_id>", GetSearchableFields.as_view({'get': 'list'}), name="searchable-fields"),
    path("lookup-fields-options/<str:serializer_id>", GetLookupFieldOptions.as_view({'get': 'list'}), name="lookup-fields-options"),
]
