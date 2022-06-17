from app_controller.services.writer_main import WriterMain

class WriteToUrls(WriterMain):
    urls = []

    def __init__(self, app, urls):
        super().__init__(app)
        self.urls = urls
        self.write_url()
        
    def write_url(self):
        print("writing url...")
        self.content_data = "from django.urls import path, include\n"
        self.content_data += "from rest_framework.routers import DefaultRouter\n"
        self.check_for_import()
        self.content_data += "\n\n"
        
        self.content_data += "router = DefaultRouter()\n"
        
        for url in self.urls:
            field_properties = url.field_properties
            
            self.content_data += f"router.register('{(url.name)}', {field_properties['view']}, '{field_properties['name']}')\n"
            
        self.content_data += "\n"
        
        self.content_data += "urlpatterns = [\n"
        self.content_data += "\tpath('', include(router.urls)),\n"
        self.content_data += "]\n"
            
        self.write_to_file('url')    
        
        
    def check_for_import(self):
        print("writing url imports")
        import_obj = {}
        
        for url in self.urls:
            key = ".views"
            
            if not import_obj.get(key, None):
                import_obj[key] = []
                
            if url.view_relation.name not in import_obj[key]:
                import_obj[key].append(url.view_relation.name)
                
        self.format_import(import_obj)