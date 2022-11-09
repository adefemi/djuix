from rest_framework.routers import DefaultRouter
from .views import GetTopViewGetOptions, GetSimilarViewKeys, GetSearchableFields, GetLookupFieldOptions, GetAppAttributes
from django.urls import path

router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    # path("", include(router.urls)),
    path("top-data-option/<str:serializer_id>", GetTopViewGetOptions.as_view({'get': 'list'}), name="get-top-view-options"),
    path("similar-data-option/<str:serializer_id>", GetSimilarViewKeys.as_view({'get': 'list'}), name="get-similar-view-options"),
    path("searchable-fields/<str:serializer_id>", GetSearchableFields.as_view({'get': 'list'}), name="searchable-fields"),
    path("lookup-fields-options/<str:serializer_id>", GetLookupFieldOptions.as_view({'get': 'list'}), name="lookup-fields-options"),
    path("get-app-attributes/<str:app_id>", GetAppAttributes.as_view({'get': 'list'}), name="get-app-attributes"),
]
