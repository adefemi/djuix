

from abstractions.enums import ModelFieldTypes, SerializerFieldTypes
from app_controller.models import SerializerInfo, ViewsInfo
from app_controller.serializers import SerializerInfoSerializer, UrlInfoSerializer, ViewInfoSerializer
from djuix.helper import Helper


class GenerateModelComponents:
    
    def __init__(self, model):
        self.model = model
        self.generate_model_serializer()
        self.generate_model_view()
        self.get_view_url()
        
    def generate_model_serializer(self):
        serializer_name = self.model.name + "Serializer"
        
        serializer_data = {
            "name": serializer_name,
            "app_id": self.model.app.id,
            "model_relation_id": self.model.id,
        }
        
        field_properties = {
            "fields": [],
            "meta": {
                "model": self.model.name,
                "fields": "'__all__'",
            },
            "type": "ModelSerializer",
        }
        
        model_fields = self.model.field_properties["fields"]
        
        for field in model_fields:
            if field["field_type"] in (ModelFieldTypes.ForeignKey, ModelFieldTypes.OneToOneField):
                a = {
                    "name": field["name"],
                    "field_type": field["field_properties"]["related_model_name"]+"Serializer",
                    "is_custom_type": True,
                    "field_properties": {
                        "read_only": "True",
                    }
                }
                b = {
                    "name": field["name"]+"_id",
                    "field_type": SerializerFieldTypes.IntegerField,
                    "field_properties": {
                        "write_only": "True",
                    }
                }
                field_properties["fields"].append(a)
                field_properties["fields"].append(b)
            
            elif field["field_type"] == ModelFieldTypes.ManyToManyField:
                c = {
                    "name": field["name"],
                    "field_type": field["field_properties"]["related_model_name"]+"Serializer",
                    "is_custom_type": True,
                    "field_properties": {
                        "read_only": "True",
                        "many": "True",
                    }
                }
                field_properties["fields"].append(c)
                
        serializer_data["field_properties"] = field_properties
        serializer_v = SerializerInfoSerializer(data=serializer_data)
        serializer_v.is_valid(raise_exception=True)
        serializer_v.save()
        
        self.serializer = SerializerInfo.objects.get(id=serializer_v.data["id"])
        
    def generate_model_view(self):
        view_name = self.model.name + "View"
        
        view_data = {
            "name": view_name,
            "app_id": self.model.app.id,
            "serializer_relation_id": self.serializer.id,
            "model_id": self.model.id,
        }
        
        field_properties = {
            "model": self.model.name,
            "serializer": self.serializer.name,
        }
        
        view_data["field_properties"] = field_properties
        
        view_v = ViewInfoSerializer(data=view_data)
        view_v.is_valid(raise_exception=True)
        view_v.save()
        
        self.view = ViewsInfo.objects.get(id=view_v.data["id"])
        
    def get_view_url(self):
        url_name = Helper.camelToSnakeDash(self.view.model.name)
        
        url_data = {
            "name": url_name,
            "app_id": self.model.app.id,
            "view_relation_id": self.view.id,
        }
        
        field_properties = {
            "name": url_name,
            "view": self.view.name,
        }
        
        url_data["field_properties"] = field_properties
        url_v = UrlInfoSerializer(data=url_data)
        url_v.is_valid(raise_exception=True)
        url_v.save()
        

        