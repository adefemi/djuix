from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from abstractions.enums import ModelFieldTypes

from app_controller.models import ModelInfo, SerializerInfo, UrlInfo, ViewsInfo
from project_controller.models import App

# Create your views here.

class GetTopViewGetOptions(ModelViewSet):
    http_method_names = ("get",)
    
    def get_queryset(self):
        return None
    
    def list(self, request, *args, **kwargs):
        serializer_id = kwargs["serializer_id"]
        
        serializer_obj = SerializerInfo.objects.get(id=serializer_id, app__project__owner_id=request.user.id)
        model_obj = serializer_obj.model_relation
        app_obj = serializer_obj.app
        
        # get all model fields with a foreign relationship with the model
        
        app_models = app_obj.app_models.exclude(id=model_obj.id)
        possible_fields = []
        
        for model in app_models:
            for field in model.field_properties["fields"]:
                if field["field_type"] == "ForeignKey":
                    if field["field_properties"]["related_model_name"] == model_obj.name:
                        possible_fields.append(field["field_properties"]["related_name"])
                        
        return Response(possible_fields)
    
    
class GetSimilarViewKeys(ModelViewSet):
    http_method_names = ("get",)
    
    def get_queryset(self):
        return None
    
    @staticmethod
    def get_related_fields(app, model_name):
        active_model = app.app_models.filter(name=model_name)
        fields = []
        if active_model:
            for field in active_model[0].field_properties["fields"]:
                if field["field_type"] in (ModelFieldTypes.ForeignKey, ModelFieldTypes.ManyToManyField, ModelFieldTypes.OneToOneField, ModelFieldTypes.FileField, ModelFieldTypes.ImageField):
                    continue
                if field.get("field_properties", None):
                    if field["field_properties"].get("unique", None) == "True":
                        continue
                fields.append(field["name"])
                
        fields.append("id")
        return fields
            
    
    def list(self, request, *args, **kwargs):
        serializer_id = kwargs["serializer_id"]
        
        serializer_obj = SerializerInfo.objects.get(id=serializer_id, app__project__owner_id=request.user.id)
        model_obj = serializer_obj.model_relation
        app_obj = serializer_obj.app
        
        fields = []
        
        for field in model_obj.field_properties["fields"]:
            if field["field_type"] in (ModelFieldTypes.FileField, ModelFieldTypes.ImageField):
                continue
            if field.get("field_properties", None):
                if field["field_properties"].get("unique", None) == "True":
                    continue
                
            temp_obj = {
                "name": field["name"],
            }
            if field["field_type"] in (ModelFieldTypes.ForeignKey, ModelFieldTypes.ManyToManyField, ModelFieldTypes.OneToOneField):
                temp_obj["fields"] = self.get_related_fields(app_obj, field["field_properties"]['related_model_name'])
            fields.append(temp_obj)
            
        return Response(fields)
    

class GetSearchableFields(ModelViewSet):
    http_method_names = ("get",)
    
    def get_queryset(self):
        return None
    
    @staticmethod
    def get_related_fields(app, model_name):
        active_model = app.app_models.filter(name=model_name)
        fields = []
        if active_model:
            for field in active_model[0].field_properties["fields"]:
                if field["field_type"] in (ModelFieldTypes.ForeignKey, ModelFieldTypes.ManyToManyField, ModelFieldTypes.OneToOneField, ModelFieldTypes.FileField, ModelFieldTypes.ImageField, ModelFieldTypes.BooleanField, ModelFieldTypes.DateTimeField):
                    continue
                fields.append(field["name"])
        return fields
    
    def list(self, request, *args, **kwargs):
        serializer_id = kwargs["serializer_id"]
        
        serializer_obj = SerializerInfo.objects.get(id=serializer_id, app__project__owner_id=request.user.id)
        model_obj = serializer_obj.model_relation
        app_obj = serializer_obj.app
        
        fields = []
        
        
        for field in model_obj.field_properties["fields"]:
            if field["field_type"] in (ModelFieldTypes.FileField, ModelFieldTypes.ImageField, ModelFieldTypes.BooleanField, ModelFieldTypes.DateTimeField):
                continue
            
            prefix = field["name"]
            
            if field["field_type"] in (ModelFieldTypes.ForeignKey, ModelFieldTypes.ManyToManyField, ModelFieldTypes.OneToOneField):
                t_fields = self.get_related_fields(app_obj, field["field_properties"]['related_model_name'])
                for d in t_fields:
                    fields.append({
                        "name": f"{field['field_properties']['related_model_name']} - {d}",
                        "key": f"{prefix}__{d}"
                    })
            else:
                fields.append({
                    "name": prefix,
                    "key": prefix
                })
                
        return Response(fields)
    
    
class GetLookupFieldOptions(ModelViewSet):
    http_method_names = ("get",)
    
    def get_queryset(self):
        return None
    
    def list(self, request, *args, **kwargs):
        serializer_id = kwargs["serializer_id"]
        
        serializer_obj = SerializerInfo.objects.get(id=serializer_id, app__project__owner_id=request.user.id)
        model_obj = serializer_obj.model_relation
        
        fields = []
        
        for field in model_obj.field_properties["fields"]:
            if field["field_type"] not in (ModelFieldTypes.SlugField, ModelFieldTypes.EmailField, ModelFieldTypes.IntegerField):
                continue
            
            if field.get("field_properties", None):
                if field["field_properties"].get("unique", None) or field["field_properties"].get("unique", None) == "True":
                    fields.append(field["name"])
    
        return Response(fields)
    
    
class GetAppAttributes(ModelViewSet):
    http_method_names = ("get",)
    
    def get_queryset(self):
        return None
    
    def get_attributeInfo(self, model):
        query = model.objects.filter(app_id=self.app_id)
        count = query.count()
        order_with_update = query.order_by("-updated_at")
        last_update = None
        if order_with_update:
            last_update = order_with_update[0].updated_at
            
        return {"count": count, "last_update": last_update}
    
    def list(self, request, app_id):
        try:
            App.objects.get(id=app_id, project__owner_id=request.user.id)
            self.app_id = app_id
        except App.DoesNotExist:
            raise Exception("App with specified id does not exist")
        
        # for models
        data = {
            "model": self.get_attributeInfo(ModelInfo),
            "serializer": self.get_attributeInfo(SerializerInfo),
            "view": self.get_attributeInfo(ViewsInfo),
            "url": self.get_attributeInfo(UrlInfo),
        }
    
        return Response(data)