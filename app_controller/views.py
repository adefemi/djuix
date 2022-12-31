from app_controller.services.generateModelComponents import GenerateModelComponents
from app_controller.services.write_model import WriteToModel
from app_controller.services.write_serilizer import WriteToSerializer
from app_controller.services.write_url import WriteToUrls
from app_controller.services.write_view import WriteToView
from djuix.helper import Helper
from .serializers import (
    ModelInfo, SerializerInfo, ViewsInfo, UrlInfo, ModelInfoSerializer,
    SerializerInfoSerializer, ViewInfoSerializer, UrlInfoSerializer
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from abstractions.enums import ModelFieldTypes


class ModelInfoView(ModelViewSet):
    queryset = ModelInfo.objects.select_related("app")
    serializer_class = ModelInfoSerializer
    
    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset.filter(app__project__owner_id=self.request.user.id)
        
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
        
        active_model = self.queryset.get(id=serialized_data.data["id"])
        active_app = active_model.app
        WriteToModel(active_app)
        
        GenerateModelComponents(active_model)
        WriteToSerializer(active_app)
        WriteToView(active_app)
        WriteToUrls(active_app)
        
        active_app.project.run_migration = True
        active_app.project.save()
        
        return Response("Model created", status=201)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        normalized_data = Helper.normalizer_request(request.data)
        
        # check field changes
        self.check_field_addition(instance, normalized_data)
        self.check_same_field_names(normalized_data)
        self.check_slugification(normalized_data)
        self.check_field_changes(instance, normalized_data)
        
        serialized_data = self.get_serializer(data=request.data, instance=instance, partial=True)
        serialized_data.is_valid(raise_exception=True)
        serialized_data.save()
        
        active_app = self.queryset.get(id=serialized_data.data["id"]).app

        WriteToModel(active_app)
        
        active_app.project.run_migration = True
        active_app.project.save()
        
        return Response("Model update", status=201)
    
    @staticmethod
    def check_field_changes(model_instance, request_data):
        current_fields = model_instance.field_properties["fields"]
        new_fields = request_data["field_properties"]["fields"]
        
        existing_field_names = {}
        for field in current_fields:
            existing_field_names[field["name"]] = field
        
        modify_fields = {}
        for field in new_fields:
            t_data = existing_field_names.get(field["name"], None)
            if t_data and t_data["field_type"] == field["field_type"]:
                modify_fields[field["name"]] = field
                del existing_field_names[field["name"]]
                
        formatted_model_name = model_instance.name.lower()
                
        # check fields using the old fields
        ModelInfoView.check_string_rep(existing_field_names, model_instance, modify_fields, formatted_model_name)
        ModelInfoView.check_serializer_fields(existing_field_names, model_instance, modify_fields)
        ModelInfoView.check_implement_search_fields(existing_field_names, model_instance, modify_fields, formatted_model_name)
        
    @staticmethod
    def check_implement_search_fields(existing_field_names, model_instance, modify_fields, formatted_model_name):
        for key, value in existing_field_names.items():
            app_views = ViewsInfo.objects.filter(app_id=model_instance.app.id)
            for view in app_views:
                possible_strings = [key, f'{formatted_model_name}.{key}']
                implement_search = view.field_properties.get('implement_search', None)
                if implement_search:
                    fields = implement_search["search_fields"]
                    for possible_string in possible_strings:
                        if possible_string in fields:
                            if not modify_fields.get(key, None):
                                raise Exception(f"A modified field named was used in {view.name} implement search fields")
                            else:
                                if modify_fields["key"]["field_type"] in [ModelFieldTypes.ForeignKey, ModelFieldTypes.ManyToManyField, ModelFieldTypes.OneToOneField]:
                                    raise Exception("Changing field type to a related field will affect {view.name} implement search fields")
        
    @staticmethod
    def check_serializer_fields(existing_field_names, model_instance, modify_fields):
        for key, value in existing_field_names.items():
            model_serializers = model_instance.model_serializers.all()
            for model_serializer in model_serializers:
                meta = model_serializer.field_properties.get("meta", None)
                if meta is not None:
                    fields = meta.get("fields", None)
                    if fields is not None:
                        if "__all__" in fields:
                            continue
                        else:
                            if key in fields:
                                if not modify_fields.get(key, None):
                                    raise Exception(f"A modified field named was used in the {model_serializer.name} serializer.")
        
    @staticmethod
    def check_string_rep(existing_field_names, model_instance, modify_fields, formatted_model_name):
        for key, value in existing_field_names.items():
            model_string_rep = model_instance.field_properties.get("string_representation", [])
            possible_strings = [key, f'{formatted_model_name}.{key}']
            for possible_string in possible_strings:
                if possible_string in model_string_rep:
                    if not modify_fields.get(key, None):
                        raise Exception("A modified field named was used in string representation for model")
                    else:
                        if modify_fields["key"]["field_type"] in [ModelFieldTypes.ForeignKey, ModelFieldTypes.ManyToManyField, ModelFieldTypes.OneToOneField]:
                            raise Exception("Changing field type to a related field will affect string representation for model")
                        
            possible_string = f'{formatted_model_name}.{key}'
            app_models = model_instance.app.app_models.all()
            
            for app_model in app_models:
                model_string_rep = app_model.field_properties.get("string_representation", [])
                
                if possible_string in model_string_rep:
                    if not modify_fields.get(key, None):
                        raise Exception("A modified field named was used in string representation for model")
                    else:
                        if modify_fields["key"]["field_type"] in [ModelFieldTypes.ForeignKey, ModelFieldTypes.ManyToManyField, ModelFieldTypes.OneToOneField]:
                            raise Exception("Changing field type to a related field will affect string representation for model")
    
    @staticmethod
    def check_slugification(new_data):
        new_fields = new_data["field_properties"]["fields"]
        # check if there is a slug field in the fields
        slug_fields = []
        field_names = []
        for field in new_fields:
            if field["field_type"] == ModelFieldTypes.SlugField:
                slug_fields.append(field)
            else:
                field_names.append(field["name"])
                
        for slug_field in slug_fields:
            ref = slug_field["field_properties"]["field_reference"]
            if not ref in field_names:
                raise Exception("One or more slug field reference cannot be found.")
                
    @staticmethod
    def check_same_field_names(new_data):
        new_fields = new_data["field_properties"]["fields"]
        
        existing_field_names = []
        for field in new_fields:
            if field["name"] in existing_field_names:
                raise Exception("Model field names cannot be repeated.")
            
            existing_field_names.append(field["name"])
            
    @staticmethod
    def check_field_addition(model_instance, request_data):
        has_migration = model_instance.has_created_migration
        if not has_migration:
            return
        
        current_fields = model_instance.field_properties["fields"]
        new_fields = request_data["field_properties"]["fields"]
        
        if len(new_fields) > len(current_fields):
            # new field what added, find the new field 
            # store the name of existing fields in an array
            existing_field_names = []
            for field in current_fields:
                existing_field_names.append(field["name"])
            
            # check which of the fields from the new fields in not in the existing fields names
            new_field_content = []
            for field in new_fields:
                if field["name"] not in existing_field_names:
                    new_field_content.append(field)
                
            # check if the new field is null or has a default value, if not then raise an exception that this will affect the migrations
            for e in new_field_content:
                field_props = e["field_properties"]
                if not field_props.get("default", None) and not field_props.get("null", None):
                    raise Exception("Adding a new field to an already migrated model requires you to specify either a default value or mark as nullable.")
            
    
class SerializerInfoView(ModelViewSet):
    queryset = SerializerInfo.objects.select_related("model_relation", "model_relation__app")
    serializer_class = SerializerInfoSerializer
    
    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset.filter(app__project__owner_id=self.request.user.id)
        
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
        
        active_serializer = self.queryset.get(id=serialized_data.data["id"])
        active_app = active_serializer.app
        WriteToSerializer(active_app)
        
        return Response("Model created", status=201)
    
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        
        WriteToSerializer(self.get_object().app)
        
        return Response("Model updated", status=200)

    
class ViewInfoView(ModelViewSet):
    queryset = ViewsInfo.objects.select_related(
        "serializer_relation", "serializer_relation__model_relation", "serializer_relation__model_relation__app")
    serializer_class = ViewInfoSerializer
    
    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset.filter(app__project__owner_id=self.request.user.id)
        
        if query.get("get_by_app_id", None) is not None:
            id = query["get_by_app_id"]
            queryset = queryset.filter(app_id = id)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        data = self.setup_data(request)
        
        save_data = self.get_serializer(data=data)
        save_data.is_valid(raise_exception=True)
        save_data.save()
        
        active_app = self.queryset.get(id=save_data.data["id"]).app
        
        WriteToView(active_app)
        
        return Response("View created successfully")
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.setup_data(request)
        
        save_data = self.get_serializer(data=data, instance=instance, partial=True)
        save_data.is_valid(raise_exception=True)
        save_data.save()
        
        active_app = instance.app
        
        WriteToView(active_app)
        
        return Response("View update successfully")
    
    def setup_data(self, request):
        normalized_data = Helper.normalizer_request(request.data)
        if not normalized_data.get("serializer_id", None):
            raise Exception("You must provide a serializer_id")
        if not normalized_data.get("name", None):
            raise Exception("You must provide a name for the view")
        
        active_serializer = SerializerInfoView.queryset.get(id=normalized_data["serializer_id"])
        active_model = active_serializer.model_relation
        active_app = active_serializer.app
        
        new_data_structure = {
            "name": normalized_data["name"],
            "serializer_relation_id": normalized_data["serializer_id"],
            "app_id": active_app.id,
            "model_id": active_model.id,
        }
        
        field_properties = {
            "model": active_model.name,
            "serializer": active_serializer.name,
        }
        
        has_http_method_names = normalized_data.get("http_method_names", None)
        if has_http_method_names:
            field_properties["http_method_names"] = has_http_method_names
            
        has_lookup_field = normalized_data.get("lookup_field", None)
        if has_lookup_field:
            field_properties["lookup_field"] = has_lookup_field
            
        has_permission = normalized_data.get("permission", None)
        if has_permission:
            field_properties["permission"] = has_permission
            
        can_create = True if not has_http_method_names or "post" in has_http_method_names else False
        can_update = True if not has_http_method_names or "patch" in has_http_method_names else False
        
        self.handle_similar_content(field_properties, normalized_data, active_model)
        self.handle_top_content(field_properties, normalized_data)
        self.handle_implement_search(field_properties, normalized_data)
        if can_create:
            self.override_create(active_serializer, field_properties)
        if can_update:
            self.override_update(active_serializer, field_properties)
        
        new_data_structure["field_properties"] = field_properties
        
        return new_data_structure
        
    @staticmethod
    def handle_implement_search(field_obj, request_obj):
        implement_search = request_obj.get("implement_search", None)
        if implement_search:
            field_obj["implement_search"] = implement_search
    
    @staticmethod
    def override_create(active_serializer, field_obj):
        model = active_serializer.model_relation
        
        # check if model field contains foreign relationsips
        fields = model.field_properties.get("fields", None)
        has_override_create = False
        if fields:
            for field in fields:
                if field["field_type"] in (ModelFieldTypes.ManyToManyField, ):
                    if not has_override_create:
                        field_obj["override_create"] = {}
                        has_override_create = True
                    ViewInfoView.add_many_to_many(field_obj["override_create"], field, active_serializer.app)
                    
    @staticmethod
    def override_update(active_serializer, field_obj):
        model = active_serializer.model_relation
        
        # check if model field contains foreign relationsips
        fields = model.field_properties.get("fields", None)
        has_override_create = False
        if fields:
            for field in fields:
                if field["field_type"] in (ModelFieldTypes.ManyToManyField, ):
                    if not has_override_create:
                        field_obj["override_update"] = {}
                        has_override_create = True
                    ViewInfoView.add_many_to_many(field_obj["override_update"], field, active_serializer.app, "update_many_to_many")
                    
    @staticmethod
    def add_many_to_many(field_obj, my_field, active_app, key="add_many_to_many"):
        active_model = active_app.app_models.filter(name=my_field["field_properties"]['related_model_name'])
        field_to_check = "id"
        
        if not field_obj.get(key, None):
            field_obj[key] = []
        
        if active_model:
            for field in active_model[0].field_properties["fields"]:
                if field["field_type"] in (ModelFieldTypes.ForeignKey, ModelFieldTypes.ManyToManyField, ModelFieldTypes.OneToOneField, ModelFieldTypes.FileField, ModelFieldTypes.ImageField):
                    continue
                if field.get("field_properties", None):
                    if field["field_properties"].get("unique", None) == "True":
                        field_to_check = field["name"]
                        break
        
        field_obj[key].append(
            {
                "field_name": my_field["name"],
                "field_body_key": my_field["name"],
                "field_model": my_field["field_properties"]['related_model_name'],
                "field_check_key": field_to_check
            }
        )
        
    @staticmethod
    def handle_similar_content(field_obj, request_obj, model):
        get_similar_content = request_obj.get("get_similar_content", None)
        if get_similar_content:
            field_obj["get_similar_content"] = get_similar_content
            field_obj["get_similar_content"]["search_id"] = f"{model.name.lower()}_id"
            
    @staticmethod
    def handle_top_content(field_obj, request_obj):
        get_top_content = request_obj.get("get_top_content", None)
        if get_top_content:
            field_obj["get_top_content"] = get_top_content
            field_obj["get_top_content"]["order_key"] = field_obj["get_top_content"]["counter_key"] + "_count"
        
        
class UrlInfoView(ModelViewSet):
    queryset = UrlInfo.objects.select_related(
        "view_relation", "view_relation__serializer_relation", "view_relation__serializer_relation__model_relation",
        "view_relation__serializer_relation__model_relation__app"
    )
    serializer_class = UrlInfoSerializer
    
    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset.filter(app__project__owner_id=self.request.user.id)
        
        if query.get("get_by_app_id", None) is not None:
            id = query["get_by_app_id"]
            queryset = queryset.filter(app_id = id)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        normalized_data = Helper.normalizer_request(request.data)
        if not normalized_data.get("view_relation_id", None):
            raise Exception("You must provide a view_relation_id")
        if not normalized_data.get("name", None):
            raise Exception("You must provide a name for the url")
        
        active_view = ViewInfoView.queryset.get(id=normalized_data["view_relation_id"])
        active_app = active_view.app
        
        obj = {
            "view_relation_id": normalized_data["view_relation_id"],
            "name": Helper.camelToSnakeDash(normalized_data["name"]),
            "app_id": active_app.id
        }
        
        field_properties = {
            "view": active_view.name,
            "name": f"{obj['name']}_list",
        }
        
        self.get_kwargs(field_properties, active_view)
        obj['field_properties'] = field_properties
        
        save_data = self.get_serializer(data=obj)
        save_data.is_valid(raise_exception=True)
        save_data.save()
        
        WriteToUrls(active_app)
        
        return Response("Created url successfully")
    
    def update(self, request, *args, **kwargs):
        normalized_data = Helper.normalizer_request(request.data)
        instance = self.get_object()
        
        if not normalized_data.get("view_relation_id", None):
            raise Exception("You must provide a view_relation_id")
        if not normalized_data.get("name", None):
            raise Exception("You must provide a name for the url")
        
        obj = {
            "view_relation_id": normalized_data["view_relation_id"],
            "name": Helper.camelToSnakeDash(normalized_data["name"]),
        }
        
        active_view = ViewInfoView.queryset.get(id=obj["view_relation_id"])
        active_app = active_view.app
        
        field_properties = {
            "view": active_view.name,
            "name": f"{obj['name']}_list",
        }
        
        self.get_kwargs(field_properties, active_view)
        obj['field_properties'] = field_properties
        
        save_data = self.get_serializer(data=obj, instance=instance, partial=True)
        save_data.is_valid(raise_exception=True)
        save_data.save()
        
        WriteToUrls(active_app)
        
        return Response("Created url successfully")
        
    def get_kwargs(self, field_properties, active_view):
        view_properties = active_view.field_properties
        
        has_get_similar_content = view_properties.get("get_similar_content", None)
        
        if(has_get_similar_content):
            if not field_properties.get("kwargs", None):
                field_properties["kwargs"] = []
                
            t_obj = {
                "key": has_get_similar_content["search_id"],
                "type": "int" if has_get_similar_content["field_to_check"] == "id" else "str",
            }
            
            field_properties["kwargs"].append(t_obj)