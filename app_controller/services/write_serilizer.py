from app_controller.services.writer_main import WriterMain

class WriteToSerializer(WriterMain):
    serializers = []
    
    def __init__(self, app):
        super().__init__(app)
        self.serializers = app.app_serializers.all().order_by('created_at')
        self.write_serializer()
        
    def write_serializer(self):
        # define the base structure
        print("writing serializer")
        self.content_data = "from rest_framework import serializers\n"
        self.check_for_import()
        
        for serializer in self.serializers:
            field_properties = serializer.field_properties
            serializer_type = field_properties["type"]
            self.content_data += f"\n\nclass {serializer.name}(serializers.{serializer_type}):\n"
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
                
            print("writing extra data")
            meta = field_properties.get("meta", None)
            if meta:
                self.format_meta(meta)
        
        self.write_to_file('serializer')
        
    def format_meta(self, meta_data):
        print("writing meta data")
        self.content_data += f"\tclass Meta:\n"
        for k, v in meta_data.items():
            self.content_data += f"\t\t{k} = {v}\n"
        
    def check_for_import(self):
        import_obj = {}
        for serializer in self.serializers:
            field_properties = serializer.field_properties
            
            key = ".models"
            if not import_obj.get(key, None):
                import_obj[key] = []
                    
            if serializer.model_relation.name not in import_obj[key]:
                import_obj[key].append(serializer.model_relation.name)
                
            fields = field_properties.get("fields", [])
            for field in fields:
                app_ref = field.get("app_ref", None)
                if app_ref is not None:
                    key = f"{app_ref}.serializers"
                    if not import_obj.get(key, None):
                        import_obj[key] = []
                    import_obj[key].append(field["field_type"])
            
            
        self.format_import(import_obj)