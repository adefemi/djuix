from app_controller.models import ModelInfo, SerializerInfo
from app_controller.services.write_model import WriteToModel
from app_controller.services.write_serilizer import WriteToSerializer


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
            
        models = ModelInfo.objects.bulk_create([ModelInfo(**i) for i in model_objs])
        WriteToModel(self.app, models)
    
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
            
        serializers = SerializerInfo.objects.bulk_create([SerializerInfo(**i) for i in serializer_objs])
        WriteToSerializer(self.app, serializers)
    
    def createView(self):
        pass
    
    def createUrls(self):
        pass
    
    def createFlow(self):
        self.createModel()
        self.createSerializer()
        self.createView()
        self.createUrls()