from abstractions.enums import ModelFieldTypes
from app_controller.services.writer_main import WriterMain

class WriteToModel(WriterMain):
    models = []
    has_save_method = False
    has_slug = False
    slug_data = {}

    def __init__(self, app, models):
        super().__init__(app)
        self.models = models
        self.write_model()
        self.write_admin()

    def write_model(self):
        # define the base structure
        print("writing model")
        self.content_data = "from django.db import models\n"
        self.check_for_import()

        for model in self.models:
            self.content_data += f"\n\nclass {model.name}(models.Model):\n"
            field_properties = model.field_properties
            fields = field_properties["fields"]
            self.has_slug = False
            self.has_save_method = False

            for field_data in fields:    
                field_attrs = field_data.get("field_properties", None)
                attrs_string = ""
                
                if field_data["field_type"] == ModelFieldTypes.SlugField:
                    self.has_slug = True
                    self.slug_data = {
                        "field_name": field_data['name'],
                        "field_to_use": field_data["field_properties"].pop('field_reference'),
                    }
                
                if field_attrs:
                    related_model_name = field_attrs.pop("related_model_name", None)
                    if related_model_name:
                        attrs_string += f"'{related_model_name}', "
                    for key,value in field_attrs.items():
                        if key in ("related_name", "default", "help_text"):
                            value = f"'{value}'"
                        attrs_string += f"{key}={value}, "
                if field_attrs:
                    attrs_string = attrs_string[:-2]
                        
                self.content_data += f"\t{self.get_formatted_name(field_data['name'])} = models.{field_data['field_type']}({attrs_string})\n"                    
            
            has_created_at = field_properties.get('has_created_at', False)
            if has_created_at:
                self.format_has_created_date()
                
            has_updated_at = field_properties.get('has_updated_at', False)
            if has_updated_at:
                self.format_has_updated_date()
                
            self.content_data += "\n"
            
            print("writing extra data")
                
            
            meta = field_properties.get("meta", None)
            if meta:
                self.format_meta(meta)
                
            string_rep = field_properties.get("string_representation", None)
            if string_rep:
                self.format_string_representation(string_rep)
                
            if self.has_slug:
                self.format_slug()
                
            if self.has_save_method:
                self.finalize_save()
                

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
    
    def format_meta(self, meta_data):
        print("writing meta data")
        self.content_data += f"\tclass Meta:\n"
        for k, v in meta_data.items():
            self.content_data += f"\t\t{k} = {v}\n"
            
    def format_has_created_date(self):
        print("writing created_at")
        self.content_data += f"\tcreated_at = models.DateTimeField(auto_now_add=True)\n"
        
    def format_has_updated_date(self):
        print("writing updated_at")
        self.content_data += f"\tupdated_at = models.DateTimeField(auto_now=True)\n"
        
    def format_string_representation(self, string_arr):
        print("writing string representation")
        self.content_data += f"\tdef __str__(self):\n"
        string_attr = " - ".join('{self.'+ f'{x}' +'}' for x in string_arr)
        self.content_data += '\t\treturn f"'+string_attr+'"\n'
        
    def format_slug(self):
        print("writing slug")
        if not self.has_save_method:
            self.has_save_method = True
            self.content_data += f"\tdef save(self, *args, **kwargs):\n"
        field_name = self.slug_data["field_name"]
        field_to_use = self.slug_data["field_to_use"]
        self.content_data += f"\t\tself.{field_name} = slugify(self.{field_to_use}, allow_unicode=True)\n"
        
    def finalize_save(self):
        self.content_data += f"\t\tsuper().save(*args, **kwargs)\n"
        
    def check_for_import(self):
        for model in self.models:
            field_properties = model.field_properties
            fields = field_properties["fields"]
            for field_data in fields:    
                if field_data["field_type"] == ModelFieldTypes.SlugField:
                    self.content_data += "from django.utils.text import slugify\n"
  