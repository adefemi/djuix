from controllers.command_template import CommandTemplate
from djuix.functions import write_to_file


class WriteUrl(CommandTemplate):
    project = None
    
    def __init__(self, project):
        self.project = project
        self.write_url()
        
    def write_url(self):
        print("writing project urls...")
        content_data = "from django.urls import path, include\n"
        content_data += "from django.contrib import admin\n"
        content_data += "\n\n"
        
        content_data += "urlpatterns = [\n"
        content_data += "\tpath('admin/', admin.site.urls),\n"
        
        apps = self.project.project_apps.all()
        for app in apps:
            content_data += f"\tpath('{app.name}-path/', include('{app.name}.urls')),\n"
        
        content_data += "]\n"
        
        p_name = self.get_formatted_name(self.project.name)
        
        path_data = f"{self.project.project_path}/{p_name}/{p_name}/"
        
        write_to_file(path_data, 'urls.py', content_data)
        