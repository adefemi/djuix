from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from abstractions.defaults import PROJECT_TEMPLATES, SERIALIZER_REQUIREMENT, SETTINGS_INFO, MODEL_REQUIREMENT

class GetProjectTemplate(ModelViewSet):
    http_method_names = ("get",)
    permission_classes = []
    
    def get_queryset(self):
        return None
    
    def list(self, request, *args, **kwargs):
        return Response(PROJECT_TEMPLATES)
    

class GetSettingInfo(ModelViewSet):
    http_method_names = ("get",)
    permission_classes = []
    
    def get_queryset(self):
        return None
    
    def list(self, request, *args, **kwargs):
        return Response(SETTINGS_INFO)
    
    
class GetModelFieldInfo(ModelViewSet):
    http_method_names = ("get",)
    permission_classes = []
    
    def get_queryset(self):
        return None
    
    def list(self, request, *args, **kwargs):
        return Response(MODEL_REQUIREMENT)
    

class GetSerializerFieldInfo(ModelViewSet):
    http_method_names = ("get",)
    permission_classes = []
    
    def get_queryset(self):
        return None
    
    def list(self, request, *args, **kwargs):
        return Response(SERIALIZER_REQUIREMENT)