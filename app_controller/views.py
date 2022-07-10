from app_controller.services.write_model import WriteToModel
from .serializers import (
    ModelInfo, SerializerInfo, ViewsInfo, UrlInfo, ModelInfoSerializer,
    SerializerInfoSerializer, ViewInfoSerializer, UrlInfoSerializer
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response


class ModelInfoView(ModelViewSet):
    queryset = ModelInfo.objects.select_related("app")
    serializer_class = ModelInfoSerializer
    
    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset
        
        if query.get("get_by_app_id", None) is not None:
            id = query["get_by_app_id"]
            queryset = queryset.filter(app_id = id)
            
        if query.get("get_by_project_id", None) is not None:
            id = query["get_by_project_id"]
            self.pagination_class = None
            queryset = queryset.filter(app__project_id = id)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data.save()
        
        active_app = self.queryset.get(id=serialized_data.data["id"]).app
        WriteToModel(active_app, active_app.app_models.all())
        
        active_app.project.run_migration = False
        active_app.project.save()
        
        return Response("Model created", status=201)
        # return super().create(request, *args, **kwargs)
    
class SerializerInfoView(ModelViewSet):
    queryset = SerializerInfo.objects.select_related("model_relation", "model_relation__app")
    serializer_class = SerializerInfoSerializer
    
    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset
        
        if query.get("get_by_app_id", None) is not None:
            id = query["get_by_app_id"]
            queryset = queryset.filter(app_id = id)
            
        return queryset
    
class ViewInfoView(ModelViewSet):
    queryset = ViewsInfo.objects.select_related(
        "serializer_relation", "serializer_relation__model_relation", "serializer_relation__model_relation__app")
    serializer_class = ViewInfoSerializer
    
    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset
        
        if query.get("get_by_app_id", None) is not None:
            id = query["get_by_app_id"]
            queryset = queryset.filter(app_id = id)
            
        return queryset
    
class UrlInfoView(ModelViewSet):
    queryset = UrlInfo.objects.select_related(
        "view_relation", "view_relation__serializer_relation", "view_relation__serializer_relation__model_relation",
        "view_relation__serializer_relation__model_relation__app"
    )
    serializer_class = UrlInfoSerializer
    
    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset
        
        if query.get("get_by_app_id", None) is not None:
            id = query["get_by_app_id"]
            queryset = queryset.filter(app_id = id)
            
        return queryset
