from app_controller.models import ModelInfo, SerializerInfo, UrlInfo, ViewsInfo
from app_controller.services.write_model import WriteToModel
from app_controller.services.write_serilizer import WriteToSerializer
from app_controller.services.write_url import WriteToUrls
from app_controller.services.write_view import WriteToView


class AppCreation:
    project = None
    app = None
    
    model_data = None
    serializer_data = None
    view_data = None
    url_data = None
    
    def __init__(self, project, app):
        self.project = project
        self.app = app
        
    def createModel(self):
        model_objs = []
        for key, value in self.model_data.items():
            tem_data = {
                "app_id": self.app.id,
                "name": key,
                "field_properties": value
            }
            model_objs.append(tem_data)
            
        WriteToModel(self.app)
    
    def createSerializer(self):
        serializer_objs = []
        for key, value in self.serializer_data.items():
            model_relation = ModelInfo.objects.filter(app_id=self.app.id, name=key.replace("Serializer", ""))
            if not model_relation:
                continue
            tem_data = {
                "model_relation_id": model_relation[0].id,
                "app_id": self.app.id,
                "name": key,
                "field_properties": value
            }
            serializer_objs.append(tem_data)
            
        SerializerInfo.objects.bulk_create([SerializerInfo(**i) for i in serializer_objs])
        WriteToSerializer(self.app)
    
    def createView(self):
        view_objs = []
        for key, value in self.view_data.items():
            serializer_name = key.replace("View", "Serializer")
            if value.get("serializer", None) is not None:
                serializer_name = value["serializer"]
            serializer_relation = SerializerInfo.objects.filter(app_id=self.app.id, name=serializer_name)
            if not serializer_relation:
                continue
            tem_data = {
                "serializer_relation_id": serializer_relation[0].id,
                "model_id": serializer_relation[0].model_relation.id,
                "app_id": self.app.id,
                "name": key,
                "field_properties": value
            }
            view_objs.append(tem_data)
            
        ViewsInfo.objects.bulk_create([ViewsInfo(**i) for i in view_objs])
        WriteToView(self.app)
    
    def createUrls(self):
        url_objs = []
        for key, value in self.url_data.items():
            view_relation = ViewsInfo.objects.filter(app_id=self.app.id, name=value.get("view", None))
            if not view_relation:
                continue
            tem_data = {
                "view_relation_id": view_relation[0].id,
                "app_id": self.app.id,
                "name": key,
                "field_properties": value
            }
            url_objs.append(tem_data)
            
        UrlInfo.objects.bulk_create([UrlInfo(**i) for i in url_objs])
        WriteToUrls(self.app)
    
    def createFlow(self):
        self.createModel()
        self.createSerializer()
        self.createView()
        self.createUrls()