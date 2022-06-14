from rest_framework.viewsets import ModelViewSet

from project_controller.sevices import process_app_creation
from .serializers import Project, ProjectSerializer, App, AppSerializer
from controllers.terminal_controller import TerminalController
from rest_framework.response import Response
from djuix import functions
from djuix.helper import Helper

from project_templates.blog.process import CreateBlogTemplate


class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)
        
        delete_if_project_exist = data.get("delete_if_project_exist", False)
        if(delete_if_project_exist):
            Project.objects.filter(name=data["name"]).delete()
                
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("delete_if_project_exist", None)
        template = serializer.validated_data.pop("template", None)
        serializer.save()
        
        project_path = serializer.data["project_path"]
        active_project = None

        terminal_controller = TerminalController(project_path, serializer.data["name"], delete_if_project_exist)

        try:
            terminal_controller.create_project()
            project_path = terminal_controller.path
            active_project = self.queryset.get(id=serializer.data["id"])
            active_project.project_path = project_path
            active_project.save()
            print("project created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)

        try:
            functions.create_settings(
                serializer.data["name"], serializer.data["id"])
            print("settings created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)

        try:
            functions.update_settings(
                terminal_controller.get_settings_path(), serializer.data["id"])
            print("settings updated")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)
        
        if template == "blog":
            print("start creating blog template")
            CreateBlogTemplate(active_project)

        return Response(self.serializer_class(active_project).data, status=201)


class AppView(ModelViewSet):
    serializer_class = AppSerializer
    queryset = App.objects.prefetch_related("project")

    def create(self, request, *args, **kwargs):
        app = process_app_creation(request.data)

        return Response(self.get_serializer(app).data, status="201")
    
