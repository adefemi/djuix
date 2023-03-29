from abstractions.enums import ModelFieldTypes
from app_controller.services.writer_main import WriterMain

class WriteToModel(WriterMain):
    models = []
    has_save_method = False
    has_slug = False
    slug_data = {}

    def __init__(self, app):
        super().__init__(app)
        self.models = app.app_models.all()
        self.write_model()
        self.write_admin()

    def write_model(self):
        # define the base structure
        print("writing model")
        self.content_data = "from django.db import models\n"
        for model in self.models:
            field_properties = model.field_properties
            fields = field_properties["fields"]
            self.check_for_import(fields, self.content_data)

        for model in self.models:
            self.content_data += f"\n\nclass {model.name}(models.Model):\n"
            field_properties = model.field_properties
            fields = field_properties["fields"]
            has_save_method = False

            has_slug, slug_data, data = self.handle_model_fields(fields, self.content_data, self.get_formatted_name)   
            self.content_data = data               
            
            has_created_at = field_properties.get('has_created_at', False)
            if has_created_at:
                self.content_data = self.format_has_created_date(self.content_data)
                
            has_updated_at = field_properties.get('has_updated_at', False)
            if has_updated_at:
                self.content_data = self.format_has_updated_date(self.content_data)
                
            self.content_data += "\n"
            
            print("writing extra data")
            
            meta = field_properties.get("meta", None)
            if meta:
                self.content_data = self.format_meta(self.content_data, meta)
                
            string_rep = field_properties.get("string_representation", None)
            if string_rep:
                self.content_data = self.format_string_representation(self.content_data, string_rep)
                
            if has_slug:
                self.content_data = self.format_slug(has_save_method, self.content_data, slug_data)
                
            if self.has_save_method:
                self.content_data = self.finalize_save(self.content_data)
                

        self.write_to_file('model')
        
    def write_admin(self):
        self.content_data = "from django.contrib import admin\n"
        import_obj = {}
        
        for model in self.models:
            key = ".models"
            
            if not import_obj.get(key, None):
                import_obj[key] = []
                
            if model.name not in import_obj[key]:
                import_obj[key].append(model.name)
                
        self.format_import(import_obj)
        string_attr = ", ".join(x.name for x in self.models)
        if len(self.models) < 2:
            string_attr = string_attr + ", "
        self.content_data += "\n\nadmin.site.register(\n"
        self.content_data += f"\t({string_attr})\n"
        self.content_data += ")\n"
        
        self.write_to_file(None, "admin.py")
    
    @staticmethod
    def format_meta(data, meta_data):
        print("writing meta data")
        data += f"\tclass Meta:\n"
        for k, v in meta_data.items():
            data += f"\t\t{k} = {v}\n"
        return data
    
    @staticmethod        
    def format_has_created_date(data):
        print("writing created_at")
        data += f"\tcreated_at = models.DateTimeField(auto_now_add=True)\n"
        return data
    
    @staticmethod    
    def format_has_updated_date(data):
        print("writing updated_at")
        data += f"\tupdated_at = models.DateTimeField(auto_now=True)\n"
        return data
    
    @staticmethod    
    def format_string_representation(data, string_arr):
        print("writing string representation")
        data += f"\tdef __str__(self):\n"
        string_attr = " - ".join('{self.'+ f'{x}' +'}' for x in string_arr)
        data += '\t\treturn f"'+string_attr+'"\n'
        return data
    
    @staticmethod    
    def format_slug(has_save_method, data, slug_data):
        print("writing slug")
        if not has_save_method:
            has_save_method = True
            data += f"\tdef save(self, *args, **kwargs):\n"
        field_name = slug_data["field_name"]
        field_to_use = slug_data["field_to_use"]
        data += f"\t\tself.{field_name} = slugify(self.{field_to_use}, allow_unicode=True)\n"
        data += f"\t\tsuper().save(args, kwargs)\n"
        return data
    
    @staticmethod    
    def finalize_save(data):
        data += f"\t\tsuper().save(*args, **kwargs)\n"
        return data
      
    def check_for_import(self, fields, data):
        for field_data in fields:    
            if field_data["field_type"] == ModelFieldTypes.SlugField and not self.has_slug:
                data += "from django.utils.text import slugify\n"
                self.has_slug = True
                
        return data
  
    @staticmethod
    def handle_model_fields(fields, data, get_formatted_name_func):
        has_slug = False
        slug_data = None
        for field_data in fields:    
            field_attrs = field_data.get("field_properties", None)
            attrs_string = ""
            
            if field_data["field_type"] == ModelFieldTypes.SlugField:
                has_slug = True
                slug_data = {
                    "field_name": field_data['name'],
                    "field_to_use": field_data["field_properties"].pop('field_reference'),
                }
                field_attrs["unique"] = "True"
            
            if field_attrs:
                related_model_name = field_attrs.pop("related_model_name", None)
                if related_model_name:
                    attrs_string += f"'{related_model_name}', "
                for key,value in field_attrs.items():
                    if key in ("related_name", "default", "help_text", "upload_to"):
                        value = f"'{value}'"
                    attrs_string += f"{key}={value}, "
            if field_attrs:
                attrs_string = attrs_string[:-2]
                    
            data += f"\t{get_formatted_name_func(field_data['name'])} = models.{field_data['field_type']}({attrs_string})\n"
            
        return has_slug, slug_data, data                    