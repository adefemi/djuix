from rest_framework.viewsets import ModelViewSet
from abstractions.defaults import PACKAGE_LIST
from project_controller.models import ProjectSettings
from .services.write_settings_file import WriteSettings

from project_controller.services.write_utils import WriteUtils

from .services.process_app_creation import process_app_creation
from .serializers import Project, ProjectSerializer, App, AppSerializer, ProjectSettingSerializer, RunMigrationSerializer
from controllers.terminal_controller import TerminalController
from rest_framework.response import Response
from djuix.helper import Helper

from project_templates.blog.process import CreateBlogTemplate


class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = "slug"

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)
        template = data.pop("template", None)
        
        delete_if_project_exist = data.get("delete_if_project_exist", False)
        if delete_if_project_exist:
            Project.objects.filter(name=data["name"]).delete() 
        else:
            proj = Project.objects.filter(name=data["name"])
            if proj:
                raise Exception(f"A project with name '{data['name']}' already exists")   
                
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("delete_if_project_exist", None)
        serializer.save()
        
        project_path = serializer.data["project_path"]
        active_project = self.queryset.get(id=serializer.data["id"])

        terminal_controller = TerminalController(project_path, active_project.formatted_name, delete_if_project_exist)

        try:
            terminal_controller.create_project()
            project_path = terminal_controller.path
            active_project.project_path = project_path
            active_project.save()
            print("project created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)

        try:
            settings_c = WriteSettings(active_project)
            settings_c.update_package_on_setting(PACKAGE_LIST)
            settings_c.create_setting()
            print("settings created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)
        
        # create some basic project artifacts
        WriteUtils(active_project)
        
        if template == "blog":
            print("start creating blog template")
            try:
                CreateBlogTemplate(active_project)
                terminal_controller.run_migration()
            except Exception as e:
                active_project.delete()
                raise Exception(e)

        return Response(self.serializer_class(active_project).data, status=201)


class AppView(ModelViewSet):
    serializer_class = AppSerializer
    queryset = App.objects.select_related("project")
    
    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset
        
        if query.get("get_app_by_project_id", None) is not None:
            id = query["get_app_by_project_id"]
            queryset = queryset.filter(project__slug = id)
            
        return queryset

    def create(self, request, *args, **kwargs):
        app = process_app_creation(request.data)

        return Response(self.get_serializer(app).data, status="201")
    

class RunMigrationView(ModelViewSet):
    http_method_names = ("post",)
    serializer_class = RunMigrationSerializer
    
    def create(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        
        active_project = Project.objects.get(id=data.validated_data["project_id"])
        
        terminal_controller = TerminalController(active_project.project_path, active_project.formatted_name)
        
        terminal_controller.run_migration()
        
        active_project.run_migration = False
        active_project.save()
        
        return Response("Migration created successfully")
    

class SettingsView(ModelViewSet):
    serializer_class = ProjectSettingSerializer
    queryset = ProjectSettings.objects.select_related("project")
    lookup_field = "project__slug"
    
    
