from app_controller.services.writer_main import WriterMain
from abstractions.defaults import auth_app_name

class WriteToView(WriterMain):
    views = []
    has_ast_for_many_to_many = False
    has_count_q_for_search = False
    implemented_queryset = False
    auth_app_name = auth_app_name
    
    def __init__(self, app):
        super().__init__(app)
        self.views = app.app_views.all()
        self.write_view()
        
    def write_view(self):
        # define the base structure
        print("writing views")
        self.content_data = "from rest_framework.viewsets import ModelViewSet\n"
        self.check_for_import()
        
        for view in self.views:
            field_properties = view.field_properties
            self.content_data += f"\n\nclass {view.name}(ModelViewSet):\n"
            
            self.implemented_queryset = False
            
            self.define_view_attrs(field_properties, view)
            
            if field_properties.get("implement_search", None) is not None:
                self.implement_search(field_properties["implement_search"])
                
            if field_properties.get("allowFilter", None) is not None:
                self.implement_allow_filter(field_properties.get("implement_search", None))
                
            if field_properties.get("get_top_content", None) is not None:
                self.implement_get_top_content(field_properties["get_top_content"])
                
            if field_properties.get("get_similar_content", None) is not None:
                self.implement_get_similar_content(field_properties["get_similar_content"])
            
                
            if self.implemented_queryset:
                self.finalize_queryset()
                
            if field_properties.get("override_create", None) is not None:
                self.override_create(field_properties["override_create"], view)
                
            if field_properties.get("override_update", None) is not None:
                self.override_update(field_properties["override_update"], view)
            
        self.write_to_file('view')
        
    def define_view_attrs(self, props, view):
        print("writing view attributes")
        # define view attributes
        view_attrs = {}
        model = None
        if not props.get("model", None):
            model = view.model.name
        else:
            model = props["model"]
        view_attrs["queryset"] = f"{model}.objects.all()"
            
        serializer = None
        if not props.get("serializer", None):
            serializer = view.serializer_relation.name
        else:
            serializer = props["serializer"]
        view_attrs["serializer_class"] = serializer
        
        if props.get("lookup_field", None) is not None:
            view_attrs["lookup_field"] = f"'{props['lookup_field']}'"
            
        if props.get("permission", None) is not None:
            view_attrs["permission_classes"] = f"{props['permission']}"
            
        if props.get("http_method_names", None) is not None:
            view_attrs["http_method_names"] = props["http_method_names"]
            
        for k,v in view_attrs.items():
            self.content_data += f"\t{k} = {v}\n"
            
    def implement_get_top_content(self, obj):
        print("writing implment get top content")
        amount = obj.get("amount", None)
        order_key = obj["order_key"]
        counter_key = obj["counter_key"]
        
        result_key = "self.queryset"
        
        if not self.implemented_queryset:
            self.content_data += f"\n\tdef get_queryset(self):\n"
        else:
            self.content_data += "\n"
            
        if self.implemented_queryset:
            result_key = "results"
            
        amount_string = ""
        if amount:
            amount_string = f"[:{amount}]"
        self.content_data += f"\t\tresults = {result_key}.annotate({order_key}=Count('{counter_key}')).order_by('-{order_key}'){amount_string}\n"
            
        self.implemented_queryset = True
        
    def implement_get_similar_content(self, obj):
        print("writing implment get similar content")
        amount = obj.get("amount", None)
        search_id = obj["search_id"]
        related_key = obj["related_key"]
        field_to_check = obj.get("field_to_check", None)
        
        result_key = "self.queryset"
        
        if not self.implemented_queryset:
            self.content_data += f"\n\tdef get_queryset(self):\n"
        else:
            self.content_data += "\n"
            
        if self.implemented_queryset:
            result_key = "results"
            
        self.content_data += f"\t\t{search_id} = self.kwargs.get('{search_id}')\n"
        if field_to_check:
            self.content_data += f"\t\ttry:\n"
            self.content_data += f"\t\t\titems = {result_key}.get({field_to_check}={search_id}).{related_key}.all()\n"
            self.content_data += f"\t\texcept Exception as e:\n"
            self.content_data += f"\t\t\t{result_key} = None\n"
            
            self.content_data += f"\t\tif {result_key} is not None:\n"
            amount_string = ""
            if amount:
                amount_string = f"[:{amount}]"
            self.content_data += f"\t\t\t{result_key} = {result_key}.filter({related_key}__{field_to_check}__in=[a.{field_to_check} for a in items]).exclude({field_to_check}={search_id}){amount_string}\n"
        else:
            amount_string = ""
            if amount:
                amount_string = f"[:{amount}]"
            self.content_data += f"\t\ttry:\n"
            self.content_data += f"\t\t\t{related_key} = {result_key}.get(id={search_id}).{related_key}\n"
            self.content_data += f"\t\t\t{result_key} = {result_key}.filter({related_key}={related_key}).exclude(id={search_id}){amount_string}\n"
            self.content_data += f"\t\texcept Exception as e:\n"
            self.content_data += f"\t\t\t{result_key} = None\n"
            
        self.content_data += f"\t\tresults = {result_key}\n"
            
        self.implemented_queryset = True
            
    def override_create(self, obj, view):
        print("writing override_create")
        self.content_data += f"\n\tdef create(self, request, *args, **kwargs):\n"
        self.content_data += f"\t\tdata = Helper.normalize_request(request.data)\n"
 
        if obj.get("update_data_field", None) is not None:
            
            for item in obj["update_data_field"]:
                field_value = item["field_from"]
                field = item["field_name"]
                if field_value == "auth_user":
                    self.content_data += "\t\tdata.update({" + f"'{field}': int(request.user.id)" + "})\n"
                else:
                    self.content_data += "\t\tdata.update({" + f"'{field}': {field_value}" + "})\n"
                
        self.content_data += f"\t\tserializer = self.get_serializer(data=data)\n"
        self.content_data += f"\t\tserializer.is_valid(raise_exception=True)\n"
        self.content_data += f"\t\tserializer.save()\n"
        
        result = 'serializer.data'
        
        if obj.get("add_many_to_many", None) is not None:
            mtm_obj = obj["add_many_to_many"]
            for item in mtm_obj:
                result = self.integrate_many_to_many(item)
            
        self.content_data += f"\n\t\treturn Response({result}, 201)\n"
        
    
    def implement_search(self, obj):
        print("writing implement_search")
        search_key = obj["search_key"]
        search_fields = obj["search_fields"]
        
        if not self.implemented_queryset:
            self.content_data += f"\n\tdef get_queryset(self):\n"
        else:
            self.content_data += "\n"
            
        self.content_data += f"\t\tif self.request.method.lower() != 'get':\n"
        self.content_data += f"\t\t\treturn self.queryset\n"
        
        self.content_data += f"\n\t\tparams = self.request.query_params.dict()\n"
        self.content_data += f"\t\t{search_key} = params.pop('{search_key}', None)\n"
        self.content_data += f"\t\tparams.pop('page', None)\n"
        self.content_data += f"\t\tresults = self.queryset.filter(**params)\n"
        self.content_data += f"\t\tif {search_key}:\n"
        
        search_fields = [str(k) for k in search_fields]
        self.content_data += f"\t\t\tsearch_fields = {search_fields}\n"
        self.content_data += f"\t\t\tquery = get_query({search_key}, search_fields)\n"
        self.content_data += f"\t\t\tresults = results.filter(query)\n"
        
        self.implemented_queryset = True
        
    def implement_allow_filter(self, obj):
        print("writing implement allow filter")
        search_key = None if not obj else obj.get("search_key", None)
        
        if not self.implemented_queryset:
            self.content_data += f"\n\tdef get_queryset(self):\n"
            
        if not search_key:
            self.content_data += "\n"
            self.content_data += f"\t\tif self.request.method.lower() != 'get':\n"
            self.content_data += f"\t\t\treturn self.queryset\n"
        
        self.content_data += f"\n\t\tfilter_params = self.request.query_params.dict()\n"
        if search_key:
            self.content_data += f"\n\t\t# Remove search key from considerable fields\n"
            self.content_data += f"\t\tif '{search_key}' in filter_params:\n"
            self.content_data += f"\t\t\tdel filter_params['{search_key}']\n"
            
        self.content_data += f"\n\t\ttry:\n"    
        self.content_data += f"\t\t\tresults = self.queryset.filter(**filter_params)\n"
        self.content_data += f"\n\t\texcept Exception as e:\n"  
        self.content_data += f"\t\t\traise Exception(e)\n"
        
        self.implemented_queryset = True
        
    def finalize_queryset(self):
        self.content_data += f"\n\t\treturn results\n"
            
            
    def override_update(self, obj, view):
        print("writing override_update")
        self.content_data += f"\n\tdef update(self, request, *args, **kwargs):\n"
        self.content_data += f"\t\tinstance = self.get_object()\n"
        self.content_data += f"\t\tdata = Helper.normalize_request(request.data)\n"
                
        self.content_data += f"\t\tserializer = self.get_serializer(data=data, instance=instance, partial=True)\n"
        self.content_data += f"\t\tserializer.is_valid(raise_exception=True)\n"
        self.content_data += f"\t\tserializer.save()\n"
        
        result = 'serializer.data'
        
        if obj.get("update_many_to_many", None) is not None:
            mtm_obj = obj["update_many_to_many"]
            
            for item in mtm_obj:
                result = self.integrate_many_to_many(item, True)
            
        self.content_data += f"\n\t\treturn Response({result}, 201)\n"
        
    def integrate_many_to_many(self, mtm_obj, is_update=False):
        print("writing integration for many to many")
        field_name = mtm_obj["field_name"]
        field_model = mtm_obj["field_model"]
        field_body_key = mtm_obj["field_body_key"]
        field_check_key = mtm_obj["field_check_key"]
        
        active_obj_key = "active_obj"
        
        self.content_data += f"\n\t\t#implement many to many item \n"
        if not is_update:
            self.content_data += f"\t\tactive_obj = self.queryset.get(id=serializer.data['id']) \n"
        else:
            active_obj_key = "instance"
        self.content_data += f"\t\tmtm_obj = data.get('{field_body_key}', None)\n"
        self.content_data += f"\t\tif mtm_obj:\n"
        self.content_data += f"\t\t\tmtm_obj = ast.literal_eval(mtm_obj)\n"
        if is_update:
            self.content_data += f"\t\t\tinstance.{field_name}.clear()\n"
        self.content_data += f"\t\t\tfor item in mtm_obj:\n"
        self.content_data += f"\t\t\t\tmtm_instance = {field_model}.objects.filter({field_check_key}=item['{field_check_key}'])\n"
        self.content_data += f"\t\t\t\tif mtm_instance:\n"
        self.content_data += f"\t\t\t\t\tmtm_instance = mtm_instance[0]\n"
        self.content_data += f"\t\t\t\t\t{active_obj_key}.{field_name}.add(mtm_instance)\n"
        
        return f'self.get_serializer({active_obj_key}).data'
        
        
    def check_for_import(self):
        print("writing view imports")
        p_name = self.get_formatted_name(self.app.project.name)
        import_obj = {
            f"{p_name}.utils": ["Helper",]
        }
        for view in self.views:
            field_properties = view.field_properties
            app_ref = field_properties.get("app_ref", None)
            key = ".models"
            if app_ref is not None:
                key = f"{app_ref}.models"
            
            if not import_obj.get(key, None):
                import_obj[key] = []
                    
            if view.model.name not in import_obj[key]:
                import_obj[key].append(view.model.name)
            
            key = ".serializers"
            if app_ref is not None:
                key = f"{app_ref}.serializers"
            
            if not import_obj.get(key, None):
                import_obj[key] = []
                    
            if view.serializer_relation.name not in import_obj[key]:
                import_obj[key].append(view.serializer_relation.name)
                
            if field_properties.get("permission", None) is not None:
                if len(field_properties["permission"]) > 4:
                    key = f"{self.auth_app_name}.methods"
                    
                    if not import_obj.get(key, None):
                        import_obj[key] = []
                        
                    import_obj[key].append(field_properties["permission"].replace("[", "").replace("]", ""))
            
            if not self.has_count_q_for_search:
                if field_properties.get("implement_search", None) is not None:
                    import_key = "django.db.models"
                    if import_obj.get(import_key, None) is None:
                        import_obj[import_key] = []
                    
                    import_obj[import_key].append('Count')
                    import_obj[import_key].append('Q')
                    
                    key = f"{p_name}.utils"
                    if not import_obj.get(key, None):
                        import_obj[key] = []
                        
                    import_obj[key].append('get_query')
                    
                    self.has_count_q_for_search = True
                
            if not self.has_ast_for_many_to_many:    
                obj = False
                if field_properties.get("override_create", None) is not None:
                    if field_properties["override_create"].get("add_many_to_many", None) is not None:
                        obj = True
                
                if field_properties.get("override_update", None) is not None and not obj:
                    if field_properties["override_update"].get("add_many_to_many", None) is not None:
                        obj = True
                        
                if obj:
                    self.content_data += "import ast\n"
                    self.has_ast_for_many_to_many = True
                    
            if field_properties.get("override_create", None) is not None or field_properties.get("override_update", None) is not None:
                import_key = "rest_framework.response"
                if not import_obj.get(import_key, None):
                    import_obj[import_key] = []
                    
                if "Response" not in import_obj[import_key]:
                    import_obj[import_key].append("Response")
                  
            if field_properties.get("permission_classes", None) is not None:
                import_key = "rest_framework.permissions"
                if not import_obj.get(import_key, None):
                    import_obj[import_key] = []
                    
                for perm in field_properties["permission_classes"]:
                    if perm not in import_obj[import_key]:
                        import_obj[import_key].append(perm)
            
        self.format_import(import_obj)