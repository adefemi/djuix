from .serializers import (
    ModelInfo, SerializerInfo, ViewsInfo, UrlInfo, ModelInfoSerializer,
    SerializerInfoSerializer, ViewInfoSerializer, UrlInfoSerializer
)
from rest_framework.viewsets import ModelViewSet


class ModelInfoView(ModelViewSet):
    queryset = ModelInfo.objects.select_related("app")
    serializer_class = ModelInfoSerializer
    
class SerializerInfoView(ModelViewSet):
    queryset = SerializerInfo.objects.select_related("model_relation", "model_relation__app")
    serializer_class = SerializerInfoSerializer
    
class ViewInfoView(ModelViewSet):
    queryset = ViewsInfo.objects.select_related(
        "serializer_relation", "serializer_relation__model_relation", "serializer_relation__model_relation__app")
    serializer_class = ViewInfoSerializer
    
class UrlInfoView(ModelViewSet):
    queryset = UrlInfo.objects.select_related(
        "view_relation", "view_relation__serializer_relation", "view_relation__serializer_relation__model_relation",
        "view_relation__serializer_relation__model_relation__app"
    )
    serializer_class = UrlInfoSerializer
