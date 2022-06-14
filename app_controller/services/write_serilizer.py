from controllers.directory_controller import DirectoryManager

class WriteToSerializer:
    serializers = []
    content_data = ""
    app = None
    
    def __init__(self, app, serializers):
        self.app = app
        self.serializers = serializers
        self.write_serializer()
        
    def write_serializer(self):
        # define the base structure
        print("writing serializer")
        self.content_data = "from rest_framework import serializers\n"
        self.check_for_import()
        self.content_data += "\n\n"
        
        for serializer in self.serializers:
            field_properties = serializer.field_properties
            serializer_type = field_properties["type"]
            self.content_data += f"class {serializer.name}(serializers.{serializer_type}):\n"
            fields = field_properties.get("fields", [])
            
            for field_data in fields:    
                field_attrs = field_data.get("field_properties", None)
                attrs_string = ""
                
                if field_attrs:
                    for key,value in field_attrs.items():
                        attrs_string += f"{key}={value}, "
                if field_attrs:
                    attrs_string = attrs_string[:-2]
                    
                field_type = field_data["field_type"]
                is_custom_type = field_data.get("is_custom_type", False)
                if not is_custom_type:
                    field_type = f"serializers.{field_type}"
                    
                self.content_data += f"\t{field_data['name']} = {field_type}({attrs_string})\n"
                
            should_double_next_line = False
                
            print("writing extra data")
            meta = field_properties.get("meta", None)
            if meta:
                should_double_next_line = True
                self.format_meta(meta)
                
            if should_double_next_line:
                self.content_data += "\n\n"
        
        try:
            print("writing to serializer file")
            serializer_path = f"{self.app.project.project_path}/{self.app.project.name}/{self.app.name}/"
            directory_manager = DirectoryManager(serializer_path)
            file_data = directory_manager.create_file("serializers.py")
            directory_manager.write_file(file_data, self.content_data)
            return True
        except Exception as e:
            print(e)
            return False
        
    def format_meta(self, meta_data):
        print("writing meta data")
        self.content_data += f"\tclass Meta:\n"
        for k, v in meta_data.items():
            self.content_data += f"\t\t{k} = {v}\n"
        print("finish writing meta data")
        
    def check_for_import(self):
        import_obj = {}
        for serializer in self.serializers:
            field_properties = serializer.field_properties
            app_ref = field_properties.get("app_ref", None)
            key = ".models"
            if app_ref is not None:
                key = f"{app_ref}.models"
            
            if not import_obj.get(key, None):
                import_obj[key] = []
                    
            import_obj[key].append(serializer.model_relation.name)
            
            
        for key, value in import_obj.items():
            import_string = ", ".join(i for i in value)
            self.content_data += f"from {key} import ({import_string})\n"