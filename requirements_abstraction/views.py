from rest_framework.viewsets import ModelViewSet
from app_controller.models import ModelInfo
from rest_framework.response import Response

from abstractions.defaults import PROJECT_TEMPLATES


class GetProjectTemplate(ModelViewSet):
    queryset = ModelInfo.objects.none()
    http_method_names = ("get")
    
    def get_queryset(self):
        return None
    
    def list(self, request, *args, **kwargs):
        return Response(PROJECT_TEMPLATES)