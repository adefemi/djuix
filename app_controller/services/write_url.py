from app_controller.services.writer_main import WriterMain
from project_controller.services.write_url import WriteProjectUrl

class WriteToUrls(WriterMain):
    urls = []

    def __init__(self, app):
        super().__init__(app)
        self.urls = app.app_urls.all()
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
            
            self.content_data += f"router.register('{(url.name)}', {url.view_relation.name}, basename='{field_properties['name']}')\n"
            
        self.content_data += "\n"
        
        self.content_data += "urlpatterns = [\n"
        self.content_data += "\tpath('', include(router.urls)),\n"
        self.content_data += "]\n"
            
        self.write_to_file('url')    
        WriteProjectUrl(self.app.project)
        
        
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